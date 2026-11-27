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
