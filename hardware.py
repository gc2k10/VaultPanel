"""Explicit read boundary. No sudo, shell, control driver, or backup execution."""
import subprocess


def disabled_operation(operation):
    return {'ok': False, 'error': 'Hardware writes and backups are disabled in this review build',
            'operation': operation}


def permitted_read(cmd):
    if not isinstance(cmd, list) or not cmd or not all(isinstance(v, str) for v in cmd):
        return False
    exact = [
        ['vcgencmd', 'measure_temp'], ['hostname', '-I'], ['tailscale', 'ip', '-4'],
        ['ip', 'route'], ['lsblk', '-J', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT,MODEL'],
        ['docker', 'ps', '--format', '{{.Names}}'],
    ]
    if cmd in exact:
        return True
    if len(cmd) == 3 and cmd[0] == 'systemctl' and cmd[1] in {'is-active', 'is-enabled'}:
        return not cmd[2].startswith('-')
    if len(cmd) == 6 and cmd[:2] == ['systemctl', 'show'] and cmd[3:] == ['-p', 'ActiveEnterTimestamp', '--value']:
        return not cmd[2].startswith('-')
    if len(cmd) == 3 and cmd[:2] == ['smartctl', '-a']:
        return cmd[2].startswith('/dev/')
    if len(cmd) == 4 and cmd[:3] in [['btrfs', 'scrub', 'status'], ['btrfs', 'filesystem', 'show']]:
        return cmd[3].startswith('/')
    if len(cmd) == 5 and cmd[:4] == ['docker', 'inspect', '-f', '{{.State.StartedAt}}']:
        return not cmd[4].startswith('-')
    if len(cmd) == 6 and cmd[:5] == ['ping', '-c', '1', '-W', '1']:
        return bool(cmd[-1]) and not cmd[-1].startswith('-')
    if len(cmd) == 3 and cmd[:2] == ['getent', 'hosts']:
        return bool(cmd[-1]) and not cmd[-1].startswith('-')
    return False


def read_command(cmd, timeout=3, *, enabled=False):
    if not enabled or not permitted_read(cmd):
        return ''
    try:
        result = subprocess.run(cmd, shell=False, capture_output=True, text=True,
                                timeout=timeout, check=False)
        # smartctl's health bits can be nonzero while stdout contains valid findings.
        if result.returncode and (cmd[0] != 'smartctl' or result.returncode & 3):
            return ''
        return (result.stdout or '').strip()
    except (OSError, subprocess.TimeoutExpired):
        return ''
