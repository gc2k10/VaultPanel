import unittest
from mdraid import parse_mdstat, MAX_MDSTAT_BYTES


def sample(summary='[2/2] [UU]', header='active raid1 example_b[1] example_a[0]', extra=''):
    return f'Personalities : [raid1]\nmd0 : {header}\n      123456 blocks super 1.2 {summary}\n      {extra}\nunused devices: <none>\n'


class MdraidParserTests(unittest.TestCase):
    def test_consistent_active_raid1_membership(self):
        array = parse_mdstat(sample())['arrays'][0]
        self.assertEqual((array['status'], array['healthy']), ('ok', True))
        self.assertEqual((array['expected_members'], array['active_members']), (2, 2))
        self.assertNotIn('example_a', str(array))
        self.assertNotIn('backup', array)

    def test_missing_member_is_degraded(self):
        for state in ['U_', '_U']:
            array = parse_mdstat(sample('[2/1] [' + state + ']'))['arrays'][0]
            self.assertEqual((array['status'], array['healthy']), ('degraded', False))

    def test_maintenance_is_not_a_health_claim(self):
        for operation in ['resync', 'recovery', 'reshape', 'check', 'repair']:
            array = parse_mdstat(sample(extra=operation + ' = 42.5% (1/2)'))['arrays'][0]
            self.assertEqual(array['status'], 'busy')
            self.assertIsNone(array['healthy'])
            self.assertEqual(array['operation'], operation)
            self.assertEqual(array['progress_pct'], 42.5)
        array = parse_mdstat(sample('[2/1] [U_]', extra='recovery = 3.0%'))['arrays'][0]
        self.assertEqual(array['status'], 'degraded')

    def test_unavailable_empty_and_oversized(self):
        for value in [None, '', 'permission denied', '\ud800', 'x' * (MAX_MDSTAT_BYTES + 1)]:
            self.assertEqual(parse_mdstat(value), {'available': False, 'arrays': []})
        self.assertEqual(parse_mdstat('Personalities : [raid1]\nunused devices: <none>'), {'available': True, 'arrays': []})

    def test_inactive_unsupported_and_conflicting_data_stay_unknown(self):
        for value in [sample(header='inactive example_a[0]'), sample(header='active raid5 example_a[0]'),
                      sample('[2/2] [U_]'), sample('[2/3] [UU]'), sample('[2/2] [UUU]'),
                      sample(''), sample('[' + '9' * 5000 + '/2] [UU]'), sample('[2/2] [UU] [2/1] [U_]'),
                      sample(header='active raid1 example_a[0](F)')]:
            array = parse_mdstat(value)['arrays'][0]
            self.assertEqual(array['status'], 'unknown')
            self.assertIsNone(array['healthy'])

    def test_multiple_arrays_and_duplicate_names(self):
        result = parse_mdstat(sample() + sample('[2/1] [U_]').replace('md0 :', 'md1 :'))
        self.assertEqual([a['status'] for a in result['arrays']], ['ok', 'degraded'])
        self.assertFalse(parse_mdstat(sample() + sample())['available'])

    def test_pending_and_invalid_progress_do_not_claim_success(self):
        for progress in ['PENDING', 'DELAYED', '101%', '-2%']:
            array = parse_mdstat(sample(extra='recovery = ' + progress))['arrays'][0]
            self.assertIsNone(array['progress_pct'])
            self.assertIsNone(array['healthy'])

class MdraidReadTests(unittest.TestCase):
    def test_single_member_array_is_not_redundancy(self):
        array = parse_mdstat(sample('[1/1] [U]'))['arrays'][0]
        self.assertEqual(array['status'], 'unknown')
        self.assertIsNone(array['healthy'])

    def test_reads_require_separate_explicit_opt_in(self):
        from config import Settings
        from hardware import read_mdstat
        from unittest.mock import patch
        self.assertFalse(Settings.from_env({}).mdraid_reads)
        self.assertFalse(Settings.from_env({'VAULTPANEL_COMMAND_READS': 'true'}).mdraid_reads)
        self.assertTrue(Settings.from_env({'VAULTPANEL_MDRAID_READS': 'true'}).mdraid_reads)
        with self.assertRaises(ValueError):
            Settings.from_env({'VAULTPANEL_MDRAID_READS': 'yes'})
        with patch('builtins.open') as opened, patch('subprocess.Popen') as process:
            self.assertEqual(read_mdstat(), '')
            opened.assert_not_called()
            process.assert_not_called()

    def test_fixed_bounded_read_and_failures(self):
        from hardware import read_mdstat
        from unittest.mock import patch, mock_open
        for content, expected in [(sample().encode(), sample()), (b'x' * (MAX_MDSTAT_BYTES + 1), ''), (b'\xff', '')]:
            opened = mock_open(read_data=content)
            with patch('builtins.open', opened), patch('subprocess.Popen') as process:
                self.assertEqual(read_mdstat(enabled=True), expected)
                opened.assert_called_once_with('/proc/mdstat', 'rb')
                opened().read.assert_called_once_with(MAX_MDSTAT_BYTES + 1)
                process.assert_not_called()
        for error in [PermissionError, FileNotFoundError, OSError]:
            with patch('builtins.open', side_effect=error):
                self.assertEqual(read_mdstat(enabled=True), '')

    def test_storage_api_keeps_membership_separate_from_btrfs(self):
        import app
        import collectors
        from config import Settings
        from unittest.mock import patch
        from contextlib import ExitStack
        client = app.create_app({'TESTING': True, 'ACCESS_TOKEN': ''}).test_client()
        for text, btrfs, status in [(sample('[2/1] [U_]'), {'healthy': True}, 'degraded'),
                                     (sample(), {'healthy': False}, 'ok'),
                                     ('', {'healthy': True}, None)]:
            with ExitStack() as stack:
                stack.enter_context(patch.object(collectors, 'settings', Settings(mdraid_reads=True)))
                stack.enter_context(patch.object(collectors, 'disk_usage', return_value={}))
                stack.enter_context(patch.object(collectors, 'btrfs_status', return_value=btrfs))
                stack.enter_context(patch.object(collectors, 'list_block_devices', return_value=[]))
                stack.enter_context(patch.object(collectors, 'get_snapshot_info', return_value={'snapshot_count': None, 'newest_snapshot': None}))
                read = stack.enter_context(patch.object(collectors, 'read_mdstat', return_value=text))
                response = client.get('/api/storage')
                self.assertEqual(response.status_code, 200)
                read.assert_called_once_with(enabled=True)
                self.assertEqual(response.json['btrfs'], btrfs)
                arrays = response.json['mdraid']['arrays']
                self.assertEqual(arrays[0]['status'] if arrays else None, status)
