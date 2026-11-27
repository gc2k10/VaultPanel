"""Conservative /proc/mdstat parsing only; no file, device or command access."""
import re

MAX_MDSTAT_BYTES = 64 * 1024
ARRAY = re.compile(r'^(md[\w-]+)\s*:\s*(.*)$')
SUMMARY = re.compile(r'\[(\d{1,5})/(\d{1,5})\]\s+\[([U_]+)\]')
OPERATION = re.compile(r'\b(resync|recovery|reshape|check|repair)\s*=\s*(?:(\d+(?:\.\d+)?)%)?')


def parse_mdstat(text):
    """Return membership evidence, never filesystem integrity or backup status.

    An empty/unrecognized/oversized input is unavailable. Only a consistent
    active RAID1 membership summary can be OK. Maintenance, inactive arrays,
    unsupported levels and conflicting counts remain unverified.
    """
    if not isinstance(text, str):
        return {'available': False, 'arrays': []}
    try:
        if len(text.encode('utf-8')) > MAX_MDSTAT_BYTES:
            return {'available': False, 'arrays': []}
    except UnicodeEncodeError:
        return {'available': False, 'arrays': []}
    blocks = []
    for line in text.splitlines():
        match = ARRAY.match(line)
        if match:
            blocks.append([match.group(1), match.group(2), []])
        elif blocks and line[:1].isspace():
            blocks[-1][2].append(line.strip())
    arrays = []
    for name, header, lines in blocks:
        level = re.search(r'\b(raid\d+|linear|multipath)\b', header)
        level = level.group(1) if level else None
        result = dict(name=name, level=level, status='unknown', healthy=None,
                      expected_members=None, active_members=None,
                      member_states=None, operation=None, progress_pct=None)
        detail = ' '.join(lines)
        summaries = SUMMARY.findall(detail)
        operation = OPERATION.search(detail)
        if operation:
            result['operation'] = operation.group(1)
            if operation.group(2) is not None:
                progress = float(operation.group(2))
                if 0 <= progress <= 100:
                    result['progress_pct'] = progress
        active = header.split()[:1] == ['active']
        if len(summaries) == 1:
            expected, online, states = summaries[0]
            expected, online = int(expected), int(online)
            result.update(expected_members=expected, active_members=online, member_states=states)
            consistent = expected > 0 and len(states) == expected and states.count('U') == online
            if active and level == 'raid1' and consistent:
                if online < expected:
                    result.update(status='degraded', healthy=False)
                elif '(F)' not in header and operation is None:
                    result.update(status='ok', healthy=True)
                elif operation is not None:
                    result['status'] = 'busy'
        arrays.append(result)
    names = [array['name'] for array in arrays]
    if len(names) != len(set(names)):
        return {'available': False, 'arrays': []}
    recognized = bool(arrays) or any(line.startswith('Personalities :') for line in text.splitlines())
    return {'available': recognized, 'arrays': arrays}
