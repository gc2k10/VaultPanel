import base64
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'vaultpanel'))
import app as application
import collectors


class ApplicationBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {'VAULTPANEL_PASSWORD': 'test-only-' * 5})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.client = application.app.test_client()
        value = base64.b64encode(('vaultpanel:' + 'test-only-' * 5).encode()).decode()
        self.headers = {'Authorization': 'Basic ' + value}

    def test_unconfigured_and_unauthenticated_fail_before_collection(self):
        with patch.object(application, 'get_overview') as collect:
            self.assertEqual(self.client.get('/api/overview').status_code, 401)
            with patch.dict(os.environ, {'VAULTPANEL_PASSWORD': ''}):
                self.assertEqual(self.client.get('/api/overview', headers=self.headers).status_code, 503)
            collect.assert_not_called()

    def test_authenticated_read_and_security_headers(self):
        with patch.object(application, 'get_overview', return_value={'hostname': 'test-host'}):
            response = self.client.get('/api/overview', headers=self.headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['hostname'], 'test-host')
            self.assertEqual(response.headers['Cache-Control'], 'no-store')
            self.assertIn("script-src 'self'", response.headers['Content-Security-Policy'])

    def test_every_privileged_route_is_blocked_without_invocation(self):
        with patch.object(application.subprocess, 'Popen') as process, \
                patch.object(application, 'apply_led_settings') as led, \
                patch.object(application, 'apply_fan_profile') as fans, \
                patch.object(application, 'apply_oled_mode') as oled:
            for route in ('backup', 'led', 'fans', 'oled'):
                response = self.client.post('/api/' + route, headers=self.headers, json={})
                self.assertEqual(response.status_code, 403)
            for mock in (process, led, fans, oled):
                mock.assert_not_called()

    def test_rebinding_host_and_wrong_password_are_rejected(self):
        response = self.client.get('/', headers=self.headers, base_url='http://untrusted.example.invalid')
        self.assertEqual(response.status_code, 400)
        response = self.client.get('/', headers={'Authorization': 'Basic ' + base64.b64encode(b'vaultpanel:wrong').decode()})
        self.assertEqual(response.status_code, 401)

    def test_both_templates_and_local_assets_render(self):
        import re
        for route in ('/', '/retro'):
            response = self.client.get(route, headers=self.headers)
            self.assertEqual(response.status_code, 200)
            text = response.get_data(as_text=True)
            self.assertIn('read-only', text)
            for url in re.findall(r'(?:src|href)="(/static/[^" ]+)"', text):
                with self.client.get(url, headers=self.headers) as asset:
                    self.assertEqual(asset.status_code, 200, url)

    def test_alert_reads_do_not_write_history(self):
        with patch.object(application, 'get_alerts', return_value={'alerts': []}), \
                patch.object(application, 'read_alert_history', return_value=[]), \
                patch.object(application, 'write_alert_history') as write:
            self.assertEqual(self.client.get('/api/alerts', headers=self.headers).status_code, 200)
            write.assert_not_called()

    def test_manifest_icons_resolve_under_static(self):
        from urllib.parse import urljoin
        with self.client.get('/static/site.webmanifest', headers=self.headers) as response:
            import json
            manifest = json.loads(response.get_data(as_text=True))
        self.assertEqual(manifest['name'], 'VaultPanel')
        for icon in manifest['icons']:
            url = urljoin('/static/site.webmanifest', icon['src'])
            self.assertTrue(url.startswith('/static/'))
            with self.client.get(url, headers=self.headers) as image:
                self.assertEqual(image.status_code, 200)
                self.assertTrue(image.get_data().startswith(b'\x89PNG\r\n\x1a\n'))


class CollectorTests(unittest.TestCase):
    def test_failed_sudo_is_noninteractive_and_not_successful_data(self):
        import subprocess
        with patch.object(collectors.subprocess, 'run', return_value=subprocess.CompletedProcess([], 1, '', 'permission denied')) as run:
            self.assertEqual(collectors.run(['sudo', 'smartctl', '-a', '/dev/test']), '')
            self.assertEqual(run.call_args.args[0][:2], ['sudo', '-n'])

    def test_no_btrfs_output_never_means_healthy(self):
        with patch.object(collectors, 'run', return_value=''):
            self.assertIsNone(collectors.btrfs_status()['healthy'])

    def test_smart_does_not_accept_incidental_ok_text(self):
        with patch.object(collectors, 'run', return_value='device lookup failed; previous status OK'):
            self.assertEqual(collectors.smart_health('/dev/test'), 'CHECK')

    def test_backup_and_all_hardware_adapters_refuse_without_opt_in(self):
        import subprocess
        root = Path(__file__).resolve().parents[1] / 'vaultpanel'
        environment = dict(os.environ)
        environment.pop('VAULTPANEL_ENABLE_HARDWARE', None)
        for script in [root / 'backup.sh', *sorted((root / 'scripts').glob('*'))]:
            if script.suffix not in {'.sh', '.py'}:
                continue
            command = ['bash' if script.suffix == '.sh' else sys.executable, str(script)]
            result = subprocess.run(command, env=environment, capture_output=True, text=True, timeout=3)
            self.assertNotEqual(result.returncode, 0, script.name)
            self.assertIn('disabled', (result.stdout + result.stderr).lower(), script.name)


if __name__ == '__main__':
    unittest.main()
