"""Smoke-test a source ZIP outside its checkout; never print host telemetry."""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]

SMOKE = r'''
import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, sys.argv[1])
with patch('subprocess.Popen', side_effect=AssertionError('Unexpected command')) as command, \
     patch('socket.socket.connect', side_effect=AssertionError('Unexpected connection')) as connection:
    import app
    from config import settings
    assert not settings.command_reads
    assert not settings.services and not settings.smart_devices
    client = app.app.test_client()
    for route in ['/', '/retro', '/static/css/style.css', '/static/css/style_retro.css',
                  '/static/js/app.js', '/static/js/app_retro.js', '/static/js/safe-html.js']:
        response = client.get(route)
        assert response.status_code == 200, route
    for name in ['overview', 'cooling', 'storage', 'services', 'network', 'alerts', 'system', 'capabilities']:
        response = client.get('/api/' + name)
        assert response.status_code == 200 and isinstance(response.json, dict), name
    capabilities = client.get('/api/capabilities').json
    assert capabilities == dict(read_only=True, hardware_writes=False, backups=False, command_reads=False)
    for name in ['backup', 'fans', 'led', 'oled']:
        response = client.post('/api/' + name, json={})
        assert response.status_code == 403 and response.json['ok'] is False, name
    command.assert_not_called()
    connection.assert_not_called()
print('Source ZIP smoke passed: pages/assets, 8 APIs, 4 denied writes; no commands or connections')
'''


def fingerprint(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


class DistributionTests(unittest.TestCase):
    def test_export_runs_without_checkout_or_runtime_writes(self):
        names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')[:-1]
        self.assertIn('LICENSE', names)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            archive = root / 'candidate.zip'
            extracted = root / 'source'
            cwd = root / 'empty'
            cwd.mkdir()
            with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as output:
                for name in names:
                    path = ROOT / name
                    self.assertFalse(path.is_symlink(), name)
                    self.assertTrue(path.is_file(), name)
                    self.assertNotIn('..', Path(name).parts)
                    self.assertFalse(Path(name).is_absolute())
                    output.write(path, name)
            with zipfile.ZipFile(archive) as source:
                self.assertIsNone(source.testzip())
                source.extractall(extracted)  # Entries were constructed/validated above.
            before = fingerprint(extracted)
            env = {key: value for key, value in os.environ.items()
                   if not key.startswith(('VAULTPANEL_', 'PYTHON'))}
            result = subprocess.run([sys.executable, '-I', '-B', '-c', SMOKE, str(extracted)],
                                    cwd=cwd, env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Source ZIP smoke passed', result.stdout)
            self.assertEqual(before, fingerprint(extracted), 'Export changed during requests')
            self.assertEqual(list(cwd.iterdir()), [], 'Application wrote into working directory')
