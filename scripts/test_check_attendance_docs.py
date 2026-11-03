#!/usr/bin/env python3
"""Exercise GitHub link portability and integrity failures on tiny fixtures."""

from pathlib import Path
import json
import re
import tempfile
import unittest
from unittest.mock import patch

import check_attendance_docs as checker


class DocumentationChecks(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return Path(name)

    def test_encoded_image_and_duplicate_heading_links(self):
        page = self.write('guide/start.md', '# Start\n[Read](../topic.md#repeat-1)\n![Model](../assets/model%20view.png)\n')
        target = self.write('topic.md', '# Topic\n## Repeat\n## Repeat\n')
        image = self.write('assets/model view.png', 'synthetic image bytes')
        files = {page, target, image}
        manifest = checker.integrity_snapshot(self.root, files)
        self.assertEqual(checker.check_repository(self.root, files, manifest)[0], [])

    def test_wrong_case_missing_anchor_and_ignored_attachment_fail(self):
        page = self.write('README.md', '# Guide\n[Case](Topic.md)\n[Anchor](topic.md#absent)\n[Local](assets/example.csv)\n')
        target = self.write('topic.md', '# Topic\n')
        self.write('assets/example.csv', 'local,private\n')
        files = {page, target}
        errors = checker.check_repository(self.root, files, checker.integrity_snapshot(self.root, files))[0]
        self.assertEqual(len(errors), 3)
        self.assertTrue(any('wrong-case' in error and 'Topic.md' in error for error in errors))
        self.assertTrue(any('missing heading anchor' in error for error in errors))
        self.assertTrue(any('example.csv' in error for error in errors))

    def test_fenced_examples_do_not_create_navigation(self):
        page = self.write('README.md', '# Guide\n```powerquery\n// [[example]] [example](absent.md)\n1\n```\n')
        files = {page}
        self.assertEqual(checker.check_repository(self.root, files, checker.integrity_snapshot(self.root, files))[0], [])

    def test_code_changes_and_new_blocks_need_reviewed_manifest(self):
        page = self.write('README.md', '# Guide\n```dax\nMetric = 1\n```\n')
        files = {page}
        manifest = checker.integrity_snapshot(self.root, files)
        self.write('README.md', '# Guide\n```dax\nMetric = 2\n```\n```powerquery\n1\n```\n')
        errors = checker.check_repository(self.root, files, manifest)[0]
        self.assertEqual(len(errors), 1)
        self.assertIn('Integrity mismatch', errors[0])

    def test_image_change_needs_reviewed_manifest(self):
        page = self.write('README.md', '# Guide\n![Model](model.png)\n')
        image = self.write('model.png', 'first image')
        files = {page, image}
        manifest = checker.integrity_snapshot(self.root, files)
        self.write('model.png', 'different image')
        self.assertTrue(any('images' in error for error in checker.check_repository(self.root, files, manifest)[0]))

    def test_zip_inventory_exposes_stray_source_files_instead_of_hiding_them(self):
        self.write('README.md', '# Guide\n')
        self.write('.github/workflows/docs.yml', 'name: Documentation\n')
        self.write('assets/private.csv', 'local,private\n')
        self.write('.obsidian/settings.json', '{}\n')
        self.write('AGENTS.md', '# Local instructions\n')
        files = checker.distribution_files(self.root)
        self.assertEqual(files, {Path('README.md'), Path('.github/workflows/docs.yml'), Path('assets/private.csv')})
        errors = checker.public_content_errors(self.root, files)
        self.assertTrue(any('assets/private.csv' in error for error in errors))

    def test_accidentally_tracked_source_files_are_rejected(self):
        (self.root / '.git').mkdir()
        self.write('README.md', '# Guide\n')
        self.write('private.xlsx', 'not publication data')
        with patch.object(checker.subprocess, 'check_output', return_value=b'README.md\0private.xlsx\0'):
            files = checker.distribution_files(self.root)
        self.assertIn(Path('private.xlsx'), files)
        self.assertTrue(any('private.xlsx' in error for error in checker.public_content_errors(self.root, files)))

    def test_nested_parentheses_and_reference_destinations(self):
        links = checker.markdown_links('[Read](folder/topic_(one).md#section)\n![Diagram][model]\n[model]: <assets/model view.png>\n')
        self.assertIn('folder/topic_(one).md#section', links)
        self.assertIn('assets/model view.png', links)

    def test_absolute_and_outside_links_fail(self):
        page = self.write('README.md', '# Guide\n')
        errors = checker.link_errors(self.root, page, ['/Users/example.md', '../outside.md', 'file:///private/example.md'], {page}, {})
        self.assertEqual(len(errors), 3)

    def test_real_wiki_syntax_and_unclosed_fence_fail(self):
        page = self.write('README.md', '# Guide\n[[topic]]\n```dax\nMetric = 1\n')
        files = {page}
        errors = checker.check_repository(self.root, files, checker.integrity_snapshot(self.root, files))[0]
        self.assertTrue(any('wiki syntax' in error for error in errors))
        self.assertTrue(any('unclosed code fence' in error for error in errors))

    def test_heading_punctuation_and_slug_collisions(self):
        ids = checker.heading_ids('# Guide\n## What is a **measure**?\n## A\n## A-1\n## A\n')
        self.assertTrue({'guide', 'what-is-a-measure', 'a', 'a-1', 'a-2'} <= ids)

    def test_front_matter_is_not_published(self):
        page = self.write('README.md', '---\ntitle: Example\n---\n\n# Guide\n')
        self.assertTrue(any('front matter' in error for error in checker.public_content_errors(self.root, {page})))

    def test_deployment_url_email_and_home_path_are_checked_inside_code(self):
        site = 'https://' + 'tenant' + '.sharepoint.com/sites/project'
        email = 'reader' + '@' + 'sample-business.example'
        home = '/Users/' + 'private-user' + '/project/file.md'
        page = self.write('README.md', '# Guide\n```powerquery\n"' + site + '"\n"' + email + '"\n"' + home + '"\n```\n')
        errors = checker.public_content_errors(self.root, {page})
        self.assertEqual(len(errors), 3)
        self.assertTrue(any('SharePoint URL' in error for error in errors))
        self.assertTrue(any('email addresses' in error for error in errors))
        self.assertTrue(any('home path' in error for error in errors))

    def test_documented_placeholder_and_reference_domains_are_allowed(self):
        page = self.write('README.md', '# Guide\nhttps://YOUR-TENANT.sharepoint.com/sites/YOUR-SITE\nhttps://learn.microsoft.com/en-us/power-query/\nhttps://docs.github.com/en/\nhttps://www.pewresearch.org/\nhttps://aapor.org/\nreader@example.test reader@example.com reader@example.org reader@sample.invalid\n')
        self.assertEqual(checker.public_content_errors(self.root, {page}), [])

    def test_unreviewed_external_domain_is_not_accepted_as_reference(self):
        page = self.write('README.md', '# Guide\n' + 'https://' + 'unlisted.example' + '/reference\n')
        self.assertTrue(any('external URL' in error for error in checker.public_content_errors(self.root, {page})))

    def test_private_policy_is_case_insensitive_and_reports_no_matched_text(self):
        page = self.write('README.md', '# Guide\nSAMPLE HOLDINGS\n')
        policy = self.write('.local-only/review.json', json.dumps([r'\bsample holdings\b']))
        rules = checker.load_private_terms(self.root / policy)
        errors = checker.public_content_errors(self.root, {page}, rules)
        self.assertEqual(len(errors), 1)
        self.assertIn('rule 1', errors[0])
        self.assertNotIn('SAMPLE HOLDINGS', errors[0])
        self.write('README.md', '# Guide\nA simple returning visitor.\n')
        self.assertEqual(checker.public_content_errors(self.root, {page}, rules), [])

    def test_private_policy_rejects_bad_shape_and_invalid_regex(self):
        for value in [{'rules': []}, [''], ['[']]:
            policy = self.write('.local-only/review.json', json.dumps(value))
            with self.assertRaises(ValueError):
                checker.load_private_terms(self.root / policy)

    def test_private_policy_checks_filenames(self):
        page = self.write('sample-company.md', '# Guide\n')
        errors = checker.public_content_errors(self.root, {page}, [re.compile('sample-company', re.I)])
        self.assertTrue(any('filename' in error for error in errors))

    def test_symlink_is_not_a_publication_input(self):
        target = self.write('source.txt', 'synthetic\n')
        link = self.root / 'README.md'
        link.symlink_to(self.root / target)
        errors = checker.public_content_errors(self.root, {Path('README.md')})
        self.assertTrue(any('symbolic links' in error for error in errors))

    def test_non_utf8_markdown_reports_failure_without_crashing(self):
        page = self.write('README.md', '# Guide\n')
        (self.root / page).write_bytes(b'\xff\xfe\x00')
        errors = checker.check_repository(self.root, {page}, checker.integrity_snapshot(self.root, {page}))[0]
        self.assertTrue(any('UTF-8' in error for error in errors))


if __name__ == '__main__':
    unittest.main()
