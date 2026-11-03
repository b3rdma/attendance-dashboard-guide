#!/usr/bin/env python3
"""Check the public guide, links and reviewed code without private data.

Run the normal read-only check:
    python3 scripts/check_attendance_docs.py

After reviewing an intentional M/DAX or image change, refresh its recorded hashes:
    python3 scripts/check_attendance_docs.py --update-integrity

Use --terms-file with a private JSON list of case-insensitive regular expressions
for an additional release review. That policy file is not a publication input.
Neither command executes Power Query/DAX, commits files or publishes them.
"""

import argparse
from collections import defaultdict
from hashlib import sha256
import html
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path('scripts/documentation_integrity.json')
IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'}
EXCLUDED_PARTS = {'.git', '.obsidian', '.local-only', 'guide_theme', 'handover', '__pycache__'}
RESTRICTED_SUFFIXES = {'.csv', '.xlsx', '.xlsm', '.xlsb', '.xls', '.pbix', '.pbip', '.pbit', '.docx', '.zip', '.pdf', '.pyc', '.log'}
TEXT_SUFFIXES = {'.md', '.py', '.json', '.yml', '.yaml', '.txt', '.svg'}
TEXT_NAMES = {'LICENSE', '.gitignore', '.gitattributes'}
EXAMPLE_HOSTS = {'example.com', 'example.org', 'example.test'}
REFERENCE_HOSTS = {'microsoft.com', 'github.com', 'github.blog', 'githubusercontent.com', 'powerbi.com', 'pewresearch.org', 'aapor.org', 'python.org'}
URL_PATTERN = re.compile(r'https?://[A-Za-z0-9][A-Za-z0-9_.-]*(?::\d+)?(?:/[^\s<>"\'`\\]*)?', re.I)
EMAIL_PATTERN = re.compile(r'(?<![\w@])[A-Za-z0-9.!#$%&\'*+/=?^_`{|}~-]+@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)')
HOME_PATTERN = re.compile(r'/(?:Users|home)/([A-Za-z0-9_.-]+)/[^\s<>"\'`]+')
WINDOWS_HOME_PATTERN = re.compile(r'[A-Za-z]:\\(?:Users|Documents and Settings)\\([^\\\s]+)\\', re.I)


def distribution_files(root):
    """Include tracked and new non-ignored files; also support a source ZIP.

    No historical object is read. A local working copy can therefore validate
    files prepared for its next commit, while ignored source attachments cannot
    make a broken GitHub link appear valid merely because they exist locally.
    """
    if (root / '.git').exists():
        try:
            result = subprocess.check_output(
                ['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                cwd=root, stderr=subprocess.DEVNULL,
            )
            return {Path(name) for name in result.decode().split('\0') if name and (root / name).is_file()}
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    # A GitHub source ZIP contains distributed files only. The exclusions also
    # keep copied local references out of the fallback inventory.
    return {
        path.relative_to(root) for path in root.rglob('*')
        if path.is_file()
        and not any(part in EXCLUDED_PARTS for part in path.relative_to(root).parts)
        and path.name not in {'AGENTS.md', '.DS_Store'}
    }


def load_private_terms(path):
    """Read private release rules without copying their text into public output."""
    if path is None:
        return []
    rules = json.loads(Path(path).read_text())
    if not isinstance(rules, list) or any(not isinstance(rule, str) or not rule.strip() for rule in rules):
        raise ValueError('The private terms file must contain a JSON array of nonempty regular-expression strings')
    try:
        return [re.compile(rule, re.I) for rule in rules]
    except re.error as error:
        raise ValueError('The private terms file contains an invalid regular expression') from error


def private_policy_errors(root, files, path):
    if path is None:
        return []
    try:
        relative = Path(path).resolve().relative_to(root.resolve())
    except ValueError:
        return []
    if relative in files:
        return ['The private release policy is a distributed file; move it outside the publication inventory']
    return []


def example_host(host):
    return host in EXAMPLE_HOSTS or host.endswith('.invalid')


def reference_host(host):
    return any(host == base or host.endswith('.' + base) for base in REFERENCE_HOSTS)


def public_content_errors(root, files, private_terms=()):
    """Check all distributed text, including code and machine-readable fixtures.

    This is a mechanical check, not proof that text or image pixels contain no
    identifying context. Keep private review terms outside the distributed tree.
    """
    errors = []
    for path in sorted(files):
        full = root / path
        if full.is_symlink():
            errors.append(f'{path}: symbolic links are not release inputs')
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts) or path.name in {'AGENTS.md', '.DS_Store'}:
            errors.append(f'{path}: local settings, backups or history must not be distributed')
            continue
        if path.name.startswith('.env') or path.suffix.lower() in RESTRICTED_SUFFIXES:
            errors.append(f'{path}: source, report, credential or generated archive files must not be distributed')
            continue
        is_text = path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_NAMES
        if not is_text and path.suffix.lower() not in IMAGE_SUFFIXES:
            errors.append(f'{path}: unrecognised release file type; review it before distribution')
            continue
        for number, rule in enumerate(private_terms, 1):
            if rule.search(path.as_posix()):
                errors.append(f'{path}: private release policy matched filename, rule {number}')
        if not is_text:
            continue
        try:
            text = full.read_text(encoding='utf-8')
        except (OSError, UnicodeError):
            errors.append(f'{path}: distributed text must be readable UTF-8')
            continue
        if path.suffix.lower() == '.md' and text.lstrip('\ufeff').startswith(('---\n', '---\r\n')):
            errors.append(f'{path}: remove YAML front matter from the public guide')
        for line_number, line in enumerate(text.splitlines(), 1):
            label = f'{path}:{line_number}'
            for number, rule in enumerate(private_terms, 1):
                if rule.search(line):
                    errors.append(f'{label}: private release policy matched, rule {number}')
            for match in URL_PATTERN.finditer(line):
                parts = urlsplit(match.group())
                host = (parts.hostname or '').casefold()
                if host.endswith('.sharepoint.com'):
                    if host != 'your-tenant.sharepoint.com' or parts.path.rstrip(').,;') != '/sites/YOUR-SITE':
                        errors.append(f'{label}: replace the deployment-specific SharePoint URL with the documented placeholder')
                elif not example_host(host) and not reference_host(host):
                    errors.append(f'{label}: external URL is outside the public reference/example domains; review it')
            for match in EMAIL_PATTERN.finditer(line):
                if not example_host(match[1].casefold()):
                    errors.append(f'{label}: replace personal or organisational email addresses with an example domain')
            for match in HOME_PATTERN.finditer(line):
                if match[1].casefold() not in {'example', 'username', 'your-user'}:
                    errors.append(f'{label}: remove the machine-specific home path')
            for match in WINDOWS_HOME_PATTERN.finditer(line):
                if match[1].casefold() not in {'example', 'username', 'your-user'}:
                    errors.append(f'{label}: remove the machine-specific home path')
    return errors


def scan_fences(text):
    """Return non-code text, M/DAX bodies and any unclosed fenced block."""
    visible, code = [], []
    fence = None
    body = []
    for line in text.replace('\r\n', '\n').splitlines(keepends=True):
        if fence:
            if re.match(r'^ {0,3}' + re.escape(fence[0]) + r'{' + str(fence[1]) + r',}\s*$', line):
                if fence[2] in {'powerquery', 'dax'}:
                    code.append({'language': fence[2], 'body': ''.join(body)})
                fence = None
                body = []
            else:
                body.append(line)
            visible.append('\n' if line.endswith('\n') else '')
            continue
        match = re.match(r'^ {0,3}(`{3,}|~{3,})([^\n]*)\n?$', line)
        if match:
            marker, info = match.groups()
            fence = (marker[0], len(marker), info.strip().split(' ', 1)[0].lower())
            visible.append('\n' if line.endswith('\n') else '')
        else:
            visible.append(line)
    return ''.join(visible), code, fence is not None


def slug(text):
    """GitHub-style anchors for the headings used by this guide."""
    text = re.sub(r'!?\[([^\]]+)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text).lower().strip()
    text = text.replace('`', '')
    return ''.join(char for char in text if char.isalnum() or char in '-_ ').replace(' ', '-')


def heading_ids(visible):
    counts = defaultdict(int)
    result = set()
    for heading in re.findall(r'^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$', visible, re.M):
        base = slug(heading)
        suffix = counts[base]
        candidate = base if suffix == 0 else f'{base}-{suffix}'
        while candidate in result:
            suffix += 1
            candidate = f'{base}-{suffix}'
        counts[base] = suffix + 1
        result.add(candidate)
    # Explicit HTML anchors are supported as well as ordinary Markdown headings.
    result.update(re.findall(r'<a\s+(?:[^>]*?\s)?(?:id|name)=["\']([^"\']+)["\']', visible, re.I))
    return result


def markdown_links(visible):
    """Read inline links/images and reference definitions, including () paths.

    This deliberately checks destinations, rather than attempting to render all
    Markdown. Balanced parentheses allow legal relative filenames and external
    documentation URLs. Inline code is removed before examining link syntax.
    """
    text = re.sub(r'(`+)(.*?)\1', '', visible, flags=re.S)
    references = {}
    for match in re.finditer(r'^ {0,3}\[([^\]]+)\]:\s*(<[^>]+>|\S+)', text, re.M):
        references[match[1].strip().casefold()] = match[2].strip('<>')
    result = list(references.values())
    cursor = 0
    while cursor < len(text):
        start = text.find('](', cursor)
        if start < 0:
            break
        index = start + 2
        while index < len(text) and text[index].isspace():
            index += 1
        if index < len(text) and text[index] == '<':
            end = text.find('>', index + 1)
            if end < 0:
                cursor = index + 1
                continue
            result.append(text[index + 1:end])
            cursor = end + 1
            continue
        beginning, depth = index, 0
        while index < len(text):
            char = text[index]
            if char == '\\':
                index += 2
                continue
            if char == '(':
                depth += 1
            elif char == ')':
                if depth == 0:
                    break
                depth -= 1
            elif char.isspace() and depth == 0:
                break
            index += 1
        if index > beginning:
            result.append(text[beginning:index])
        cursor = max(index + 1, start + 2)
    for match in re.finditer(r'!?\[([^\]\n]+)\]\[([^\]\n]*)\]', text):
        reference = (match[2] or match[1]).strip().casefold()
        if reference in references:
            result.append(references[reference])
    return result


def link_errors(root, source, destinations, files, anchors):
    errors = []
    for destination in destinations:
        try:
            parts = urlsplit(html.unescape(destination))
        except ValueError:
            errors.append(f'{source}: malformed link destination: {destination}')
            continue
        if parts.scheme in {'http', 'https', 'mailto', 'tel'} or destination.startswith('//'):
            continue
        if parts.scheme:
            errors.append(f'{source}: non-portable link scheme: {destination}')
            continue
        if '\\' in parts.path or parts.path.startswith('/'):
            errors.append(f'{source}: use a relative Markdown path: {destination}')
            continue
        candidate = ((root / source).parent / unquote(parts.path)).resolve() if parts.path else (root / source).resolve()
        try:
            target = candidate.relative_to(root.resolve())
        except ValueError:
            errors.append(f'{source}: link leaves the repository: {destination}')
            continue
        if target not in files:
            errors.append(f'{source}: missing, ignored or wrong-case link target: {destination}')
            continue
        if parts.fragment and target.suffix.lower() == '.md':
            fragment = unquote(parts.fragment)
            if fragment not in anchors.get(target, set()):
                errors.append(f'{source}: missing heading anchor: {destination}')
    return errors


def integrity_snapshot(root, files):
    code_blocks, images = {}, {}
    for path in sorted(files):
        if (root / path).is_symlink():
            continue
        if path.suffix.lower() == '.md':
            try:
                text = (root / path).read_text(encoding='utf-8')
            except (OSError, UnicodeError):
                continue
            _, blocks, _ = scan_fences(text)
            if blocks:
                code_blocks[path.as_posix()] = [
                    {'language': block['language'], 'sha256': sha256(block['body'].encode()).hexdigest()}
                    for block in blocks
                ]
        elif path.suffix.lower() in IMAGE_SUFFIXES:
            images[path.as_posix()] = sha256((root / path).read_bytes()).hexdigest()
    return {
        'schema_version': 1,
        'purpose': 'Reviewed M/DAX code blocks and distributed images; no historical Git objects or private files are required.',
        'refresh_command': 'python3 scripts/check_attendance_docs.py --update-integrity',
        'code_blocks': code_blocks,
        'images': images,
    }


def check_repository(root, files, manifest, private_terms=()):
    errors, anchors, visible_notes = public_content_errors(root, files, private_terms), {}, {}
    notes = sorted(path for path in files if path.suffix.lower() == '.md' and path.name != 'AGENTS.md' and not (root / path).is_symlink())
    for path in notes:
        try:
            text = (root / path).read_text(encoding='utf-8')
        except (OSError, UnicodeError):
            continue
        visible, _, unclosed = scan_fences(text)
        visible_notes[path] = visible
        anchors[path] = heading_ids(visible)
        if unclosed:
            errors.append(f'{path}: unclosed code fence')
        if len(re.findall(r'^# ', visible, re.M)) != 1:
            errors.append(f'{path}: expected one H1 heading')
        if re.search(r'!?\[\[', re.sub(r'(`+)(.*?)\1', '', visible, flags=re.S)):
            errors.append(f'{path}: Obsidian wiki syntax must be converted to Markdown')
        if '\u2014' in text:
            errors.append(f'{path}: em dash')
        for number, line in enumerate(text.splitlines(), 1):
            if line.rstrip() != line:
                errors.append(f'{path}:{number}: trailing whitespace')
    for path, visible in visible_notes.items():
        errors.extend(link_errors(root, path, markdown_links(visible), files, anchors))
    current = integrity_snapshot(root, files)
    if manifest.get('schema_version') != 1:
        errors.append('Integrity manifest is missing or has an unsupported schema version')
    else:
        for section in ('code_blocks', 'images'):
            before, after = manifest.get(section, {}), current[section]
            for path in sorted(before.keys() | after.keys()):
                if before.get(path) != after.get(path):
                    errors.append(f'Integrity mismatch in {section}: {path}. Review the change before refreshing the manifest.')
    return errors, len(notes), sum(len(blocks) for blocks in current['code_blocks'].values()), len(current['images'])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--update-integrity', action='store_true', help='Explicitly record reviewed current M/DAX and image hashes, then exit')
    parser.add_argument('--terms-file', type=Path, help='Private JSON list of regular-expression review terms; never included in a release')
    args = parser.parse_args(argv)
    try:
        private_terms = load_private_terms(args.terms_file)
    except (OSError, ValueError) as error:
        print(f'Cannot load private release policy: {error}')
        return 1
    files = distribution_files(ROOT)
    policy_errors = private_policy_errors(ROOT, files, args.terms_file)
    if policy_errors:
        print('\n'.join(policy_errors))
        return 1
    manifest_path = ROOT / MANIFEST
    if args.update_integrity:
        errors = public_content_errors(ROOT, files, private_terms)
        if errors:
            print('\n'.join(errors))
            return 1
        manifest_path.write_text(json.dumps(integrity_snapshot(ROOT, files), indent=2) + '\n')
        print(f'Updated {MANIFEST}. Review this manifest diff together with every intentional code or image change.')
        return 0
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, ValueError) as error:
        print(f'Cannot read {MANIFEST}: {error}')
        return 1
    errors, notes, blocks, images = check_repository(ROOT, files, manifest, private_terms)
    if errors:
        print('\n'.join(errors))
        return 1
    print(f'Passed: {notes} Markdown pages, relative links, heading anchors and formatting.')
    print(f'Passed: {blocks} reviewed M/DAX blocks and {images} distributed images match the integrity manifest.')
    print('Passed: public text rules and any supplied private release policy. Image pixels and Git history require separate review.')
    print('External URL availability, M/DAX execution and Power BI outputs are not tested.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
