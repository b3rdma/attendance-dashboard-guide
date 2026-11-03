#!/usr/bin/env python3
"""Check that release exports contain checked files and no repository history."""

from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

import build_public_release as release
import check_attendance_docs as checker


class PublicReleaseTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.base = Path(self.directory.name)
        self.root = self.base / 'source'
        self.root.mkdir()
        (self.root / 'README.md').write_text('# Guide\nA generic public example.\n')
        (self.root / 'scripts').mkdir()
        self.refresh_manifest()

    def refresh_manifest(self):
        files = checker.distribution_files(self.root)
        (self.root / checker.MANIFEST).write_text(json.dumps(checker.integrity_snapshot(self.root, files)))

    def test_export_has_checksums_but_no_history_settings_or_private_policy(self):
        (self.root / '.git').mkdir()
        (self.root / '.git/config').write_text('not a real Git checkout\n')
        (self.root / '.local-only').mkdir()
        (self.root / '.local-only/review.json').write_text(json.dumps(['private phrase']))
        (self.root / '.obsidian').mkdir()
        (self.root / '.obsidian/settings.json').write_text('{}')
        destination = self.base / 'public-guide'
        output, inventory = release.build_release(self.root, destination, self.root / '.local-only/review.json')
        self.assertEqual(output, destination.resolve())
        self.assertFalse((output / '.git').exists())
        self.assertFalse((output / '.local-only').exists())
        self.assertFalse((output / '.obsidian').exists())
        self.assertFalse((output / inventory.name).exists())
        data = json.loads(inventory.read_text())
        self.assertFalse(data['history_included'])
        self.assertTrue(data['private_review_policy_used'])
        files = checker.distribution_files(output)
        self.assertEqual(data['file_count'], len(files))
        for record in data['files']:
            self.assertEqual(record['sha256'], sha256((output / record['path']).read_bytes()).hexdigest())

    def test_unsafe_content_prevents_output_creation(self):
        (self.root / 'source.xlsx').write_text('not publication data')
        destination = self.base / 'public-guide'
        with self.assertRaises(ValueError) as error:
            release.build_release(self.root, destination)
        self.assertIn('public release checks failed', str(error.exception))
        self.assertFalse(destination.exists())

    def test_private_term_match_prevents_output_creation(self):
        (self.root / 'README.md').write_text('# Guide\nPrivate phrase.\n')
        (self.root / '.local-only').mkdir()
        policy = self.root / '.local-only/review.json'
        policy.write_text(json.dumps(['private phrase']))
        destination = self.base / 'public-guide'
        with self.assertRaises(ValueError) as error:
            release.build_release(self.root, destination, policy)
        self.assertIn('private release policy', str(error.exception))
        self.assertFalse(destination.exists())

    def test_private_policy_cannot_be_exported_as_a_normal_file(self):
        policy = self.root / 'review-policy.json'
        policy.write_text(json.dumps(['unmatched term']))
        destination = self.base / 'public-guide'
        with self.assertRaises(ValueError) as error:
            release.build_release(self.root, destination, policy)
        self.assertIn('policy is a distributed file', str(error.exception))
        self.assertFalse(destination.exists())

    def test_changed_formula_prevents_export_until_reviewed(self):
        (self.root / 'README.md').write_text('# Guide\n```dax\nCount = 1\n```\n')
        self.refresh_manifest()
        (self.root / 'README.md').write_text('# Guide\n```dax\nCount = 2\n```\n')
        destination = self.base / 'public-guide'
        with self.assertRaises(ValueError) as error:
            release.build_release(self.root, destination)
        self.assertIn('Integrity mismatch', str(error.exception))

    def test_existing_destination_is_preserved(self):
        destination = self.base / 'public-guide'
        destination.mkdir()
        sentinel = destination / 'keep.txt'
        sentinel.write_text('keep')
        with self.assertRaises(ValueError):
            release.build_release(self.root, destination)
        self.assertEqual(sentinel.read_text(), 'keep')

    def test_source_and_nonignored_nested_destinations_are_rejected(self):
        for destination in [self.root, self.base, self.root / 'release']:
            with self.subTest(destination=destination), self.assertRaises(ValueError):
                release.build_release(self.root, destination)

    def test_default_style_local_only_destination_is_allowed(self):
        destination = self.root / '.local-only/public-release'
        output, _ = release.build_release(self.root, destination)
        self.assertTrue((output / 'README.md').exists())


if __name__ == '__main__':
    unittest.main()
