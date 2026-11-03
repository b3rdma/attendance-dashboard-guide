#!/usr/bin/env python3
"""Prepare a checked, history-free copy of the public guide.

The source repository and its history are not changed. The destination must be
new. A checksum inventory is written beside it, rather than inside the guide.
Use --terms-file for an optional private JSON list of review expressions.
"""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tempfile

import check_attendance_docs as checker


ROOT = Path(__file__).resolve().parents[1]


def build_release(root, output, terms_file=None):
    """Export only checked distribution files, without Git or local archives."""
    root = Path(root).resolve()
    output = Path(output).resolve()
    if output == root or output in root.parents:
        raise ValueError('Choose a new release directory, not the source repository or its parent')
    if root in output.parents and output.relative_to(root).parts[0] != '.local-only':
        raise ValueError('A release inside the repository must be under .local-only')
    inventory_path = output.with_name(output.name + '.inventory.json')
    if output.exists() or inventory_path.exists():
        raise ValueError('The release directory and adjacent inventory must not already exist')
    private_terms = checker.load_private_terms(terms_file)
    files = checker.distribution_files(root)
    if not files:
        raise ValueError('No distribution files were found')
    policy_errors = checker.private_policy_errors(root, files, terms_file)
    if policy_errors:
        raise ValueError('\n'.join(policy_errors))
    try:
        manifest = json.loads((root / checker.MANIFEST).read_text())
    except (OSError, ValueError) as error:
        raise ValueError('The reviewed documentation integrity manifest is unavailable') from error
    errors, _, _, _ = checker.check_repository(root, files, manifest, private_terms)
    if errors:
        raise ValueError('The public release checks failed:\n' + '\n'.join(errors))

    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.public-release-', dir=output.parent))
    try:
        inventory = []
        for relative in sorted(files):
            if relative.is_absolute() or '..' in relative.parts or '.git' in relative.parts:
                raise ValueError('The distribution inventory contains an unsafe path')
            source = root / relative
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            inventory.append({'path': relative.as_posix(), 'sha256': sha256(target.read_bytes()).hexdigest()})
        copied_files = checker.distribution_files(stage)
        if copied_files != files or (stage / '.git').exists():
            raise ValueError('The copied release inventory does not match the checked source files')
        if json.loads((stage / checker.MANIFEST).read_text()) != manifest:
            raise ValueError('The source integrity manifest changed during export; repeat the review')
        errors, _, _, _ = checker.check_repository(stage, copied_files, manifest, private_terms)
        if errors:
            raise ValueError('The copied public release failed verification:\n' + '\n'.join(errors))
        stage.rename(output)
        inventory_path.write_text(json.dumps({
            'schema_version': 1,
            'file_count': len(inventory),
            'history_included': False,
            'private_review_policy_used': bool(private_terms),
            'files': inventory,
        }, indent=2) + '\n')
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise
    return output, inventory_path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '.local-only/public-release', help='New release directory; defaults to .local-only/public-release')
    parser.add_argument('--terms-file', type=Path, help='Private JSON list of case-insensitive regular expressions; not copied')
    args = parser.parse_args(argv)
    try:
        release, inventory = build_release(ROOT, args.output, args.terms_file)
    except (OSError, ValueError) as error:
        parser.exit(1, str(error) + '\n')
    print('Prepared checked files:', release)
    print('Checksum inventory:', inventory)
    print('Git history and local-only files are excluded. No repository was created, changed or published.')
    return 0


if __name__ == '__main__':
    main()
