import ast
import base64
import dataclasses
import importlib
import pathlib
import subprocess
import unittest
from types import SimpleNamespace
from unittest.mock import patch, mock_open

import app
import collectors
import hardware
from config import Settings


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.create_app({'TESTING': True, 'ACCESS_TOKEN': ''}).test_client()

    def test_write_endpoints_never_execute_or_write(self):
        with patch('subprocess.run') as run, patch('subprocess.Popen') as popen, patch('builtins.open') as opened:
            for endpoint in ('backup', 'led', 'fans', 'oled'):
                for body in ({}, {'profile': 'PERFORMANCE'}, ['bad'], 'bad'):
                    response = self.client.post('/api/' + endpoint, json=body)
                    self.assertEqual(response.status_code, 403)
                    self.assertFalse(response.json['ok'])
            run.assert_not_called()
            popen.assert_not_called()
            opened.assert_not_called()

    def test_direct_control_functions_are_disabled(self):
        with patch('subprocess.run') as run, patch('builtins.open') as opened:
            for method in (collectors.apply_fan_profile, collectors.apply_led_settings, collectors.apply_oled_mode):
                self.assertFalse(method({'profile': 'AUTO'})['ok'])
            run.assert_not_called()
            opened.assert_not_called()

    def test_read_routes_with_mock_collectors(self):
        for name in ('overview', 'cooling', 'storage', 'services', 'network'):
            with patch.object(collectors, 'get_' + name, return_value={'mock': name}):
                response = self.client.get('/api/' + name)
                self.assertEqual(response.json, {'mock': name})
                self.assertEqual(response.headers['Cache-Control'], 'no-store')
        with patch.object(collectors, 'get_overview', return_value={'mock': True}), patch('subprocess.run') as run:
            self.assertEqual(self.client.get('/api/system').json, {'mock': True})
            run.assert_not_called()

    def test_alert_get_does_not_persist_history(self):
        with patch.object(collectors, 'get_alerts', return_value={'alerts': []}), patch('builtins.open') as opened:
            self.assertEqual(self.client.get('/api/alerts').json['history'], [])
            opened.assert_not_called()

    def test_host_remote_and_authentication_guards(self):
        self.assertEqual(self.client.get('/api/capabilities', headers={'Host': 'attacker.invalid'}).status_code, 400)
        self.assertEqual(self.client.get('/api/capabilities', environ_overrides={'REMOTE_ADDR': '192.0.2.1'}, headers={'X-Forwarded-For': '127.0.0.1'}).status_code, 403)
        client = app.create_app({'TESTING': True, 'ACCESS_TOKEN': 'test-only'}).test_client()
        self.assertEqual(client.get('/api/capabilities').status_code, 401)
        for supplied, expected in [('wrong', 401), ('test-only', 200)]:
            header = 'Basic ' + base64.b64encode(('vaultpanel:' + supplied).encode()).decode()
            self.assertEqual(client.get('/api/capabilities', headers={'Authorization': header}).status_code, expected)

    def test_templates_render_disabled_controls_and_local_assets(self):
        for route in ('/', '/retro'):
            response = self.client.get(route)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'READ-ONLY REVIEW BUILD', response.data)
            self.assertIn(b'<button disabled', response.data)
            self.assertIn(b'safe-html.js', response.data)
            self.assertIn("script-src 'self'", response.headers['Content-Security-Policy'])

    def test_imports_have_no_hardware_side_effects(self):
        with patch('subprocess.run') as run, patch('subprocess.Popen') as popen, patch('builtins.open') as opened:
            importlib.reload(collectors)
            importlib.reload(app)
            run.assert_not_called()
            popen.assert_not_called()
            opened.assert_not_called()


class CollectorTests(unittest.TestCase):
    def test_default_commands_and_probes_are_disabled(self):
        with patch.object(collectors, 'settings', Settings()), patch('subprocess.run') as run:
            self.assertEqual(collectors.run(['vcgencmd', 'measure_temp']), '')
            self.assertIsNone(collectors.check_internet())
            self.assertIsNone(collectors.check_dns())
            self.assertIsNone(collectors.btrfs_status()['healthy'])
            run.assert_not_called()

    def test_smart_parsing_and_device_allowlist(self):
        config = dataclasses.replace(Settings(), smart_devices=('/dev/testdisk',))
        with patch.object(collectors, 'settings', config):
            for text, expected in [('Temperature: 42 Celsius', 42.0), ('Temperature Sensor 1: 39 Celsius', 39.0), ('194 Temperature_Celsius 0x0022 100 100 000 Old_age Always - 36 (Min/Max 20/50)', 36.0), ('', None)]:
                with patch.object(collectors, 'run', return_value=text):
                    self.assertEqual(collectors.smart_temperature('/dev/testdisk'), expected)
            for text, expected in [('Critical Warning: 0x00', 'OK'), ('Critical Warning: 0x04', 'CHECK'), ('SMART overall-health self-assessment test result: PASSED', 'PASSED'), ('unrelated OK token', 'unknown'), ('', 'unknown')]:
                with patch.object(collectors, 'run', return_value=text):
                    self.assertEqual(collectors.smart_health('/dev/testdisk'), expected)
            with patch.object(collectors, 'run') as run:
                self.assertIsNone(collectors.smart_temperature('/dev/unlisted'))
                run.assert_not_called()

    def test_portable_storage_and_missing_snapshots(self):
        with patch.object(collectors, 'settings', Settings(storage_mount='/example')), patch.object(collectors, 'disk_usage', return_value={}) as usage, patch.object(collectors, 'btrfs_status', return_value={}), patch.object(collectors, 'list_block_devices', return_value=[]):
            result = collectors.get_storage()
            usage.assert_called_once_with('/example')
            self.assertEqual(result['mountpoint'], '/example')
            self.assertIsNone(result['snapshot_count'])

    def test_memory_uses_psutil_available_memory(self):
        with patch.object(collectors.psutil, 'virtual_memory', return_value=SimpleNamespace(total=104857600, available=26214400, percent=75.0)):
            self.assertEqual(collectors.get_mem_usage()['used_mb'], 75)

    def test_service_names_are_exact(self):
        config = Settings(services=({'name': 'Example', 'docker': 'example', 'port': None, 'panel': None},))
        with patch.object(collectors, 'settings', config), patch.object(collectors, 'SERVICES', config.services), patch.object(collectors, 'run', return_value='example-other'):
            self.assertFalse(collectors.get_services()['services'][0]['active'])

    def test_only_one_fan_function_survives(self):
        tree = ast.parse(pathlib.Path('collectors.py').read_text())
        self.assertEqual(sum(isinstance(n, ast.FunctionDef) and n.name == 'apply_fan_profile' for n in tree.body), 1)


class BoundaryTests(unittest.TestCase):
    def test_shell_sudo_and_mutations_are_refused(self):
        with patch('subprocess.run') as run:
            for cmd in ('echo unsafe', ['sudo', 'smartctl', '-a', '/dev/test'], ['systemctl', 'restart', 'example'], ['btrfs', 'scrub', 'start', '/'], ['sh', '-c', 'true'], ['systemctl', 'is-active', '--help']):
                self.assertEqual(hardware.read_command(cmd, enabled=True), '')
            run.assert_not_called()

    def test_reads_have_timeout_no_shell_and_no_stderr_data(self):
        with patch('hardware.capture', return_value=(0, '42\n')) as run:
            self.assertEqual(hardware.read_command(['vcgencmd', 'measure_temp'], enabled=True), '42')
            run.assert_called_once_with(['vcgencmd', 'measure_temp'], 3)
        with patch('hardware.capture', side_effect=subprocess.TimeoutExpired('test', 3)):
            self.assertEqual(hardware.read_command(['vcgencmd', 'measure_temp'], enabled=True), '')

    def test_smart_health_bits_preserve_valid_output(self):
        for code, expected in [(0, 'data'), (8, 'data'), (1, ''), (2, '')]:
            with patch('hardware.capture', return_value=(code, 'data')):
                self.assertEqual(hardware.read_command(['smartctl', '-a', '/dev/test'], enabled=True), expected)

    def test_config_validation_and_safe_defaults(self):
        self.assertEqual(Settings.from_env({}), Settings())
        for env in ({'VAULTPANEL_COMMAND_READS': 'yes'}, {'VAULTPANEL_SMART_DEVICES': '/etc/passwd'}, {'VAULTPANEL_SERVICES': '{}'}, {'VAULTPANEL_SERVICES': '[{"name":"x","systemd":"--bad"}]'}, {'VAULTPANEL_PING_TARGET': '-x'}):
            with self.assertRaises(ValueError):
                Settings.from_env(env)


if __name__ == '__main__':
    unittest.main()
