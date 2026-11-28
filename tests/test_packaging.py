"""Candidate integrity and refusal cases use an isolated synthetic Git repo."""
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('packager', Path(__file__).resolve().parents[1] / 'scripts/package-alpha.py')
packager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)


class CandidatePackagingTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.base = Path(self.folder.name)
        self.repo = self.base / 'repo'
        self.repo.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Synthetic Test')
        self.git('config', 'user.email', 'test@example.invalid')
        (self.repo / 'README.md').write_text('Synthetic source\n')
        self.git('add', 'README.md')
        self.git('commit', '-qm', 'fixture')

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.repo, stderr=subprocess.DEVNULL)

    def build(self, name='candidate'):
        return packager.build('v0.2.0-alpha', self.repo, self.base / name)

    def test_deterministic_archive_hashes_and_untracked_exclusion(self):
        (self.repo / '.env').write_text('synthetic private fixture')
        a, b = self.build('one'), self.build('two')
        self.assertEqual(Path(a['archive']).read_bytes(), Path(b['archive']).read_bytes())
        with zipfile.ZipFile(a['archive']) as bundle:
            self.assertEqual(bundle.namelist(), ['VaultPanel/README.md'])
            self.assertEqual(bundle.read('VaultPanel/README.md'), b'Synthetic source\n')
        output = Path(a['archive']).parent
        self.assertEqual((output / 'SOURCE_COMMIT.txt').read_text().strip(), self.git('rev-parse', 'HEAD').decode().strip())
        for line in (output / 'SHA256SUMS.txt').read_text().splitlines():
            digest, name = line.split('  ')
            self.assertEqual(digest, hashlib.sha256((output / name).read_bytes()).hexdigest())
        with self.assertRaises(FileExistsError):
            self.build('one')

    def test_rejects_dirty_and_staged_source(self):
        (self.repo / 'README.md').write_text('changed')
        for stage in (False, True):
            if stage:
                self.git('add', 'README.md')
            with self.assertRaisesRegex(ValueError, 'worktree'):
                self.build()
        self.assertFalse((self.base / 'candidate').exists())

    def test_rejects_sensitive_names_and_symlinks(self):
        for index, name in enumerate(['.env', 'private-source/raw.py', 'server.pem', 'export.sql', 'state/fans.json', 'linked']):
            p = self.repo / name
            p.parent.mkdir(exist_ok=True)
            if name == 'linked':
                p.symlink_to('README.md')
            else:
                p.write_text('synthetic only')
            self.git('add', name)
            self.git('commit', '-qm', 'add unsafe fixture')
            with self.assertRaises(ValueError):
                self.build(str(index))
            self.git('rm', name)
            self.git('commit', '-qm', 'remove fixture')

    def test_version_requires_safe_explicit_prerelease(self):
        for version in ['', 'v0.2.0', '../v0.2.0-alpha', 'v0.2.0-alpha/secret', 'v00.2.0-alpha']:
            with self.assertRaises(ValueError):
                packager.build(version, self.repo, self.base / 'invalid')

    def test_executable_mode_is_preserved_without_execution(self):
        path = self.repo / 'example.sh'
        path.write_text('#!/bin/sh\nexit 42\n')
        path.chmod(0o755)
        self.git('add', 'example.sh')
        self.git('commit', '-qm', 'executable fixture')
        with zipfile.ZipFile(self.build()['archive']) as bundle:
            self.assertEqual(bundle.getinfo('VaultPanel/example.sh').external_attr >> 16, 0o100755)
