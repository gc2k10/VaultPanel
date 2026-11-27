"""Explicit read boundary. No sudo, shell, control driver, or backup execution."""
import subprocess
import os
import selectors
import time

MAX_OUTPUT_BYTES = 65536


def capture(cmd, timeout):
    """Drain a bounded stdout pipe; discard stderr and reap on every exit."""
    with subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL) as process:
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                deadline = time.monotonic() + timeout
                chunks = []
                size = 0
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0 or not selector.select(remaining):
                        raise subprocess.TimeoutExpired(cmd, timeout)
                    chunk = os.read(process.stdout.fileno(), min(8192, MAX_OUTPUT_BYTES + 1 - size))
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > MAX_OUTPUT_BYTES:
                        raise ValueError('Diagnostic output exceeded limit')
                    chunks.append(chunk)
                code = process.wait(timeout=max(0.001, deadline - time.monotonic()))
                return code, b''.join(chunks).decode('utf-8')
        finally:
            if process.poll() is None:
                process.kill()
            process.wait()


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
        code, output = capture(cmd, timeout)
        if cmd[:2] == ['systemctl', 'is-active'] and code in {3, 4} and output.strip() in {'inactive', 'failed', 'unknown'}:
            return output.strip()
        if cmd[:2] == ['systemctl', 'is-enabled'] and code == 1 and output.strip() in {'disabled', 'masked'}:
            return output.strip()
        # smartctl's health bits can be nonzero while stdout contains valid findings.
        if code and (cmd[0] != 'smartctl' or code & 3):
            return ''
        return output.strip()
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return ''
