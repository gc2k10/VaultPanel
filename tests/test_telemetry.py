import dataclasses
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import collectors
import hardware
from config import Settings
from hardware import capture, MAX_OUTPUT_BYTES
from telemetry import read_state, read_text, MAX_STATE_BYTES


class TelemetryTests(unittest.TestCase):
    def test_service_unavailable_is_not_offline(self):
        with patch.object(collectors, 'run', return_value=''):
            self.assertIsNone(collectors.systemd_status('example')['active'])
            with patch.object(collectors, 'SERVICES', [{'name': 'Example', 'docker': 'example', 'port': None, 'panel': None}]):
                result = collectors.get_services()['services'][0]
                self.assertIsNone(result['active'])
                self.assertEqual(result['active_text'], 'unknown')
        for code, value in [(3, 'inactive'), (3, 'failed'), (4, 'unknown')]:
            with patch.object(hardware, 'capture', return_value=(code, value)):
                self.assertEqual(hardware.read_command(['systemctl', 'is-active', 'example'], enabled=True), value)

    def test_regular_bounded_state_and_schema(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            state = root / 'state.json'
            state.write_text(json.dumps({'profile': 'AUTO', 'brightness': 500, 'speed': True,
                                         'color': 'red;anything', 'mode': [], 'scene': 'x' * 65,
                                         'private': 'never returned'}))
            self.assertEqual(read_state(state), {'profile': 'AUTO'})
            state.write_text(json.dumps({'mode': 'STATIC', 'brightness': 50, 'speed': 10, 'color': '#aabbcc'}))
            self.assertEqual(read_state(state)['brightness'], 50)
            state.write_text('x' * (MAX_STATE_BYTES + 1))
            self.assertEqual(read_text(state), '')
            state.write_text('[]')
            self.assertEqual(read_state(state), {})
            link = root / 'link'
            link.symlink_to(state)
            self.assertEqual(read_text(link), '')
            fifo = root / 'fifo'
            os.mkfifo(fifo)
            self.assertEqual(read_text(fifo), '')
            self.assertEqual(read_text(root / 'missing'), '')

    def test_unknown_hardware_is_not_synthetic(self):
        with patch.object(collectors, 'get_cpu_temp', return_value=None), patch.object(collectors, 'get_fans', return_value=[]), patch.object(collectors, 'read_state', return_value={}), patch.object(collectors, 'get_rear_fans_state', return_value='UNKNOWN'), patch.object(collectors, 'get_oled_mode', return_value='UNKNOWN'):
            data = collectors.get_cooling()
            self.assertIsNone(data['led']['brightness'])
            self.assertIsNone(data['led']['mode'])
            self.assertEqual(data['fan_profile'], 'UNKNOWN')
            self.assertEqual(data['fans'], [])

    def test_snapshots_do_not_prove_backup(self):
        with patch.object(collectors, 'settings', Settings(snapshot_dir='/example')):
            self.assertIsNone(collectors.get_last_backup())
            self.assertIsNone(collectors.get_last_vaultpanel_backup())
            with patch('os.path.exists', return_value=False):
                self.assertIsNone(collectors.get_snapshot_info()['snapshot_count'])
            with patch('os.path.exists', return_value=True), patch('os.listdir', return_value=[]):
                self.assertEqual(collectors.get_snapshot_info()['snapshot_count'], 0)

    def test_btrfs_requires_completed_error_free_evidence(self):
        fs = 'Label: none uuid: example\nTotal devices 2'
        for output, expected in [('', None), ('no errors found', None),
                                  ('Status: running\nError summary: no errors found', None),
                                  ('Status: finished\nError summary: no errors found', True),
                                  ('Status: finished\nError summary: csum=2', False),
                                  ('Status: finished\nError summary: no errors found\nuncorrectable_errors: 1', False)]:
            with patch.object(collectors, 'run', side_effect=[fs, output]):
                self.assertIs(collectors.btrfs_status()['healthy'], expected)
        with patch.object(collectors, 'run', side_effect=['uuid: example device missing', '']):
            self.assertFalse(collectors.btrfs_status()['healthy'])

    def test_invalid_paths_and_service_types_are_rejected(self):
        for env in ({'VAULTPANEL_STORAGE_MOUNT': ''}, {'VAULTPANEL_STORAGE_MOUNT': 'relative'},
                    {'VAULTPANEL_SNAPSHOT_DIR': 'relative'},
                    {'VAULTPANEL_SERVICES': '[{"name":"x","systemd":null}]'},
                    {'VAULTPANEL_SERVICES': '[{"name":"x","systemd":"example","port":true}]'}):
            with self.assertRaises(ValueError):
                Settings.from_env(env)


class CaptureTests(unittest.TestCase):
    # Only these newly authored Python snippets are executed; no hardware utilities.
    def test_stdout_and_stderr_are_separate(self):
        code, text = capture([sys.executable, '-c', 'import sys; print("ok"); print("private", file=sys.stderr)'], 2)
        self.assertEqual((code, text), (0, 'ok\n'))

    def test_output_limit_reaps_process(self):
        with self.assertRaises(ValueError):
            capture([sys.executable, '-c', f'print("x" * {MAX_OUTPUT_BYTES + 1})'], 2)

    def test_timeout_reaps_process(self):
        with self.assertRaises(subprocess.TimeoutExpired):
            capture([sys.executable, '-c', 'import time; time.sleep(5)'], 0.05)
