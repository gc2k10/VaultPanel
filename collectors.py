from __future__ import annotations
import glob
import json
import os
import platform
import shutil
import socket
import psutil
import re
from config import settings
from hardware import read_command, disabled_operation
from telemetry import read_state, read_text
from datetime import datetime
from typing import Any

SERVICES = settings.services

ALERT_THRESHOLDS = {
    'cpu_warn': 65.0,
    'cpu_crit': 75.0,
    'disk_warn': 48.0,
    'disk_crit': 55.0,
    'storage_warn_pct': 85.0,
    'storage_crit_pct': 95.0,
}


def run(cmd: list[str], timeout: int = 3) -> str:
    return read_command(cmd, timeout, enabled=settings.command_reads)


def parse_float(s: str) -> float | None:
    try:
        return float(s)
    except Exception:
        return None


def get_cpu_temp() -> float | None:
    text = run(['vcgencmd', 'measure_temp'])
    if 'temp=' in text:
        try:
            return float(text.split('=')[1].replace("'C", ''))
        except Exception:
            pass
    path = '/sys/class/thermal/thermal_zone0/temp'
    if os.path.exists(path):
        try:
            with open(path) as f:
                return round(int(f.read().strip()) / 1000.0, 1)
        except Exception:
            pass
    return None

def get_last_backup():
    # A snapshot name is not evidence of a completed or restorable backup.
    return None


def get_last_scrub():
    try:
        out = run(["btrfs", "scrub", "status", settings.storage_mount], timeout=5)

        for raw in out.splitlines():
            line = raw.strip()

            if "finished on" in line:
                return line.split("finished on", 1)[1].strip()

            if line.startswith("Scrub started:"):
                return line.split("Scrub started:", 1)[1].strip()

            if line.startswith("scrub started at"):
                return line.split("scrub started at", 1)[1].strip()

        return None

    except Exception:
        return None

def get_last_smart_test():
    devices = settings.smart_devices

    seen_ok = False
    seen_check = False

    for dev in devices:
        health = smart_health(dev).upper()

        if health in ("OK", "PASSED"):
            seen_ok = True
        elif health in ("CHECK", "UNKNOWN"):
            seen_check = True

    if seen_ok and not seen_check:
        return "OK"
    if seen_check:
        return "CHECK"
    return "NO DATA"

def get_loadavg() -> dict[str, float | None]:
    try:
        one, five, fifteen = os.getloadavg()
        return {'1m': round(one, 2), '5m': round(five, 2), '15m': round(fifteen, 2)}
    except Exception:
        return {'1m': None, '5m': None, '15m': None}


def get_cpu_usage() -> float | None:
    try:
        return round(psutil.cpu_percent(interval=0.2), 1)
    except Exception:
        return None

def get_mem_usage() -> dict[str, Any]:
    try:
        memory = psutil.virtual_memory()
        return {'total_mb': round(memory.total / 1024**2),
                'used_mb': round((memory.total - memory.available) / 1024**2),
                'free_mb': round(memory.available / 1024**2), 'used_pct': memory.percent}
    except Exception:
        return {'total_mb': None, 'used_mb': None, 'free_mb': None, 'used_pct': None}


def get_uptime() -> str:
    try:
        with open('/proc/uptime') as f:
            seconds = int(float(f.read().split()[0]))
        days, rem = divmod(seconds, 86400)
        hours, rem = divmod(rem, 3600)
        mins, _ = divmod(rem, 60)
        return f'{days}d {hours}h {mins}m'
    except Exception:
        return 'unknown'


def disk_usage(path: str = '/') -> dict[str, Any]:
    try:
        usage = shutil.disk_usage(path)
        used_pct = round((usage.used / usage.total) * 100, 1) if usage.total else None
        return {
            'path': path,
            'total_gb': round(usage.total / 1024**3, 1),
            'used_gb': round(usage.used / 1024**3, 1),
            'free_gb': round(usage.free / 1024**3, 1),
            'used_pct': used_pct,
        }
    except Exception:
        return {'path': path, 'total_gb': None, 'used_gb': None, 'free_gb': None, 'used_pct': None}


def get_hostname() -> str:
    return socket.gethostname()


def get_ip_addresses() -> dict[str, str | None]:
    lan_ip = None
    tailscale_ip = None
    text = run(['hostname', '-I'])
    if text:
        ips = text.split()
        if ips:
            lan_ip = ips[0]
    ts = run(['tailscale', 'ip', '-4'])
    if ts:
        tailscale_ip = ts.splitlines()[0].strip()
    return {'lan_ip': lan_ip, 'tailscale_ip': tailscale_ip}


def check_internet() -> bool | None:
    if not settings.command_reads or not settings.ping_target:
        return None
    output = run(['ping', '-c', '1', '-W', '1', settings.ping_target])
    return '1 received' in output or '1 packets received' in output


def check_dns() -> bool | None:
    if not settings.command_reads or not settings.dns_target:
        return None
    return bool(run(['getent', 'hosts', settings.dns_target]))


def systemd_status(name: str) -> dict[str, Any]:
    active = run(['systemctl', 'is-active', name])
    enabled = run(['systemctl', 'is-enabled', name])
    since = run(["systemctl", "show", name, "-p", "ActiveEnterTimestamp", "--value"])
    return {
        'active': (active == 'active') if active in {'active', 'inactive', 'failed'} else None,
        'active_text': active or 'unknown',
        'enabled': enabled,
        'since': since,
    }


def get_fans() -> list[dict[str, Any]]:
    fans = []
    seen = set()
    for path in sorted(glob.glob('/sys/class/hwmon/hwmon*/fan*_input')):
        try:
            label = os.path.basename(path).replace('_input', '').upper()
            if path in seen:
                continue
            seen.add(path)
            with open(path) as f:
                rpm = int(f.read().strip())
            fans.append({'label': label, 'rpm': rpm})
        except Exception:
            continue
    return fans


def detect_led_state() -> dict[str, Any]:
    state = read_state(settings.state_dir / 'led.json')
    return {
        'scene': state.get('scene'), 'mode': state.get('mode'),
        'color': state.get('color'), 'brightness': state.get('brightness'),
        'speed': state.get('speed'), 'fan_led': state.get('fan_led'),
        'note': 'Read-only; unavailable state is not inferred.',
    }


def list_block_devices() -> list[dict[str, Any]]:
    out = run(['lsblk', '-J', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT,MODEL'])
    devices = []

    try:
        data = json.loads(out)

        for dev in data.get('blockdevices', []):
            if dev.get('type') == 'disk':

                name = dev.get('name')

                # pomijamy pseudo urządzenia
                if not name or name.startswith("zram") or name.startswith("loop"):
                    continue

                devices.append({
                    'name': name,
                    'size': dev.get('size'),
                    'model': dev.get('model'),
                    'mountpoint': dev.get('mountpoint'),
                    'temperature_c': smart_temperature(f'/dev/{name}') if name else None,
                    'smart_health': smart_health(f'/dev/{name}') if name else 'unknown'
                })

    except Exception:
        pass

    return devices

def smart_temperature(device: str) -> float | None:
    if device not in settings.smart_devices:
        return None
    out = run(['smartctl', '-a', device], timeout=5)
    for line in out.splitlines():
        match = re.match(r'\s*Temperature(?: Sensor \d+)?:\s*(-?\d+(?:\.\d+)?)', line)
        if match:
            return float(match.group(1))
        fields = line.split()
        if len(fields) >= 10 and fields[1] in {'Temperature_Celsius', 'Airflow_Temperature_Cel'}:
            return parse_float(fields[9])
    return None


def smart_health(device: str) -> str:
    if device not in settings.smart_devices:
        return 'unknown'
    out = run(['smartctl', '-a', device], timeout=5)
    warning = re.search(r'^Critical Warning:\s*(0x[0-9a-fA-F]+|\d+)\s*$', out, re.M)
    if warning:
        value = warning.group(1)
        return 'OK' if int(value, 16 if value.startswith('0x') else 10) == 0 else 'CHECK'
    assessment = re.search(r'^SMART overall-health self-assessment test result:\s*(\S+)', out, re.M)
    if assessment:
        return 'PASSED' if assessment.group(1) == 'PASSED' else 'CHECK'
    return 'unknown'


def btrfs_status(path: str = '/') -> dict[str, Any]:
    fs_show = run(['btrfs', 'filesystem', 'show', path], timeout=5)
    scrub = run(['btrfs', 'scrub', 'status', path], timeout=5)
    degraded = bool(re.search(r'degraded|missing|unrecoverable|uncorrectable', fs_show, re.I))
    # Only explicit completed scrub evidence can report healthy. A zero-error
    # substring alone, an unstarted scrub or unrelated output cannot establish it.
    completed = bool(re.search(r'^\s*(?:Status:\s*finished|scrub .*finished|finished on)', scrub, re.M | re.I))
    clean = bool(re.search(r'^\s*(?:Error summary:\s*no errors found|total errors:\s*0)\s*$', scrub, re.M | re.I))
    counters = re.findall(r'\b(?:read|csum|verify|super|malloc|uncorrectable|uncorrected|corrected|unverified)(?:_errors| errors)?\s*[:=]\s*(\d+)', scrub, re.I)
    errors = any(int(value) > 0 for value in counters)
    summary = re.search(r'^\s*Error summary:\s*(.*)$', scrub, re.M | re.I)
    if summary and summary.group(1).strip().lower() != 'no errors found':
        errors = True
    known_fs = bool(re.search(r'\buuid:', fs_show, re.I))
    healthy = False if degraded or errors else (True if known_fs and completed and clean else None)
    return {'filesystem_show': fs_show, 'scrub_status': scrub,
            'degraded': degraded, 'healthy': healthy}


def classify_status(value: float | None, warn: float, crit: float) -> str:
    if value is None:
        return 'UNKNOWN'
    if value >= crit:
        return 'CRITICAL'
    if value >= warn:
        return 'WARNING'
    return 'NOMINAL'


def get_overview() -> dict[str, Any]:
    temp = get_cpu_temp()
    storage = disk_usage(settings.storage_mount)
    mem = get_mem_usage()
    internet = check_internet()
    services = get_services()['services']
    online = sum(1 for s in services if s['active'])
    total = len(services)
    return {
        'hostname': get_hostname(),
        'platform': platform.platform(),
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'uptime': get_uptime(),
        'cpu_temp_c': temp,
        'cpu_temp_status': classify_status(temp, ALERT_THRESHOLDS['cpu_warn'], ALERT_THRESHOLDS['cpu_crit']),
        'cpu_usage_pct': get_cpu_usage(),
        'last_backup': get_last_backup(),
        'last_scrub': get_last_scrub(),
        'last_smart_test': get_last_smart_test(),
        'vaultpanel_backup': get_last_vaultpanel_backup(),
        'loadavg': get_loadavg(),
        'memory': mem,
        'storage': storage,
        'internet_ok': internet,
        'services_online': online,
        'services_total': total,
        'ips': get_ip_addresses(),
        'global_status': 'CRITICAL' if internet is False else ('UNKNOWN' if internet is None or temp is None else classify_status(temp, ALERT_THRESHOLDS['cpu_warn'], ALERT_THRESHOLDS['cpu_crit'])),
    }

def get_rear_fans_state() -> str:
    text = read_text(settings.state_dir / 'fan-control.state')
    for line in text.splitlines():
        if line == 'LAST_REAR=on':
            return 'ON'
        if line == 'LAST_REAR=off':
            return 'OFF'
    return 'UNKNOWN'


def get_cooling() -> dict[str, Any]:
    cpu_temp = get_cpu_temp()
    led = detect_led_state()
    led['oled_mode'] = get_oled_mode()
    fan_state = read_state(settings.state_dir / 'fans.json')
    return {
        'cpu_temp_c': cpu_temp, 'fans': get_fans(),
        'thermal_status': classify_status(cpu_temp, ALERT_THRESHOLDS['cpu_warn'], ALERT_THRESHOLDS['cpu_crit']),
        'fan_profile': fan_state.get('profile', 'UNKNOWN'), 'led': led,
        'rear_fans': get_rear_fans_state(),
    }


def get_snapshot_info():
    path = settings.snapshot_dir
    if not path:
        return {"snapshot_count": None, "newest_snapshot": None}
    try:
        if not os.path.exists(path):
            return {"snapshot_count": None, "newest_snapshot": None}

        snapshots = [
            d for d in os.listdir(path)
            if os.path.isdir(os.path.join(path, d))
        ]

        if not snapshots:
            return {"snapshot_count": 0, "newest_snapshot": None}

        latest = sorted(snapshots)[-1]

        m = re.search(r'(\d{4})-(\d{2})-(\d{2})', latest)
        if m:
            yyyy, mm, dd = m.groups()
            newest = f"{yyyy}-{mm}-{dd} 00:00:00"
        else:
            newest = latest

        return {
            "snapshot_count": len(snapshots),
            "newest_snapshot": newest,
        }

    except Exception:
        return {"snapshot_count": None, "newest_snapshot": None}

def get_storage() -> dict[str, Any]:
    storage_mount = settings.storage_mount
    root = disk_usage(storage_mount)
    btrfs = btrfs_status(storage_mount)
    devices = list_block_devices()
    snapshot_info = get_snapshot_info()
    nvme_temps = {}
    for device in settings.smart_devices:
        dev = os.path.basename(device)
        out = run(['smartctl', '-a', device])
        for line in out.splitlines():
            if line.strip().startswith("Temperature:"):
                parts = line.split()
                for token in parts:
                    if token.isdigit():
                        nvme_temps[dev] = f"{token} C"
                        break
                break
    return {
        'root': root,
        'devices': devices,
        'btrfs': btrfs,
        'nvme_temps': nvme_temps,
        'mountpoint': storage_mount,
        'snapshot_count': snapshot_info['snapshot_count'],
        'newest_snapshot': snapshot_info['newest_snapshot'],
    }

def format_since_short(value: str | None) -> str:
    if not value:
        return '--'

    s = str(value).strip()
    if s in {'--', 'NO DATA', 'n/a', 'N/A'}:
        return '--'

    # Tue 2026-03-17 15:25:45 CET
    m = re.match(r'^[A-Z][a-z]{2}\s+(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})', s)
    if m:
        _, mm, dd, hh, mi = m.groups()
        return f'{dd}.{mm} {hh}:{mi}'

    # 2026-03-17 15:25:45
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})', s)
    if m:
        _, mm, dd, hh, mi = m.groups()
        return f'{dd}.{mm} {hh}:{mi}'

    # 2026-03-17.15:25:45 CET
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})[._-](\d{2}):(\d{2})', s)
    if m:
        _, mm, dd, hh, mi = m.groups()
        return f'{dd}.{mm} {hh}:{mi}'

    # Tue 17 Mar 14:06:34 CET 2026
    m = re.match(r'^[A-Z][a-z]{2}\s+(\d{1,2})\s+([A-Z][a-z]{2})\s+(\d{2}):(\d{2})', s)
    if m:
        dd, mon, hh, mi = m.groups()
        months = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12',
        }
        mm = months.get(mon, mon)
        return f'{dd.zfill(2)}.{mm} {hh}:{mi}'

    return s

def docker_started_at(container: str) -> str:
    out = run(["docker", "inspect", "-f", "{{.State.StartedAt}}", container]).strip()
    if not out or out == '{{.State.StartedAt}}':
        return ''
    return out

def get_services() -> dict[str, Any]:
    items = []
    docker_output = run(["docker", "ps", "--format", "{{.Names}}"] )
    docker_names = docker_output.splitlines()

    for service in SERVICES:
        if 'docker' in service:
            container = service['docker']
            is_active = (container in docker_names) if docker_output else None
            started = docker_started_at(container) if is_active else ''
            status = {
                'active': is_active,
                'active_text': 'unknown' if is_active is None else ('active' if is_active else 'inactive'),
                'enabled': 'docker',
                'since': started,
            }
            backend_name = f"docker:{container}"
        else:
            status = systemd_status(service['systemd'])
            backend_name = service['systemd']

        items.append({
            'name': service['name'],
            'systemd': backend_name,
            'port': service['port'],
            'panel': service['panel'],
            **status,
            'since_short': format_since_short(status.get('since')),
        })

    return {'services': items}

def get_network() -> dict[str, Any]:
    route = run(['ip', 'route'])
    gw = None
    for line in route.splitlines():
        if line.startswith('default via '):
            gw = line.split()[2]
            break
    return {
        'ips': get_ip_addresses(),
        'gateway': gw,
        'internet_ok': check_internet(),
        'dns_ok': check_dns(),
        'tailscale_status': 'Detailed peer information is not exposed.',
        'resolv_conf': 'Resolver configuration is not exposed.',
    }


def get_alerts() -> dict[str, Any]:
    alerts = []
    overview = get_overview()
    storage = get_storage()
    if overview['cpu_temp_c'] is not None:
        status = classify_status(overview['cpu_temp_c'], ALERT_THRESHOLDS['cpu_warn'], ALERT_THRESHOLDS['cpu_crit'])
        if status != 'NOMINAL':
            alerts.append({'level': status, 'source': 'COOLING', 'message': f"CPU temperature is {overview['cpu_temp_c']}°C"})
    if overview['internet_ok'] is False:
        alerts.append({'level': 'CRITICAL', 'source': 'NETWORK', 'message': 'Internet connectivity test failed'})
    if (storage['root']['used_pct'] or 0) >= ALERT_THRESHOLDS['storage_warn_pct']:
        level = 'CRITICAL' if (storage['root']['used_pct'] or 0) >= ALERT_THRESHOLDS['storage_crit_pct'] else 'WARNING'
        alerts.append({'level': level, 'source': 'STORAGE', 'message': f"Root filesystem usage at {storage['root']['used_pct']}%"})
    for dev in storage['devices']:
        temp = dev.get('temperature_c')
        if temp is not None and temp >= ALERT_THRESHOLDS['disk_warn']:
            level = 'CRITICAL' if temp >= ALERT_THRESHOLDS['disk_crit'] else 'WARNING'
            alerts.append({'level': level, 'source': dev['name'], 'message': f"Disk temperature is {temp}°C"})
        smart = str(dev.get('smart_health', 'unknown')).upper()

        if smart == 'CHECK':
            alerts.append({
                'level': 'WARNING',
                'source': dev['name'].upper(),
                'message': f"SMART health requires review: {smart}"
            })
        elif smart == 'UNKNOWN':
            alerts.append({
                'level': 'WARNING',
                'source': dev['name'].upper(),
                'message': "SMART data unavailable"
            })
    if storage['btrfs']['healthy'] is False:
        alerts.append({'level': 'CRITICAL', 'source': 'BTRFS', 'message': 'Filesystem health requires review'})
    if not alerts:
        alerts.append({'level': 'INFO', 'source': 'SYSTEM', 'message': 'No alerts from available telemetry; unavailable checks are not verified'})
    return {'alerts': alerts, 'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

def apply_led_settings(payload: dict[str, Any]) -> dict[str, Any]:
    return disabled_operation('led')


def get_oled_mode() -> str:
    try:
        out = run(['systemctl', 'is-active', 'vaultpanel-oled-custom.service'], timeout=5).strip()
        return 'CUSTOM' if out == 'active' else 'UNKNOWN'
    except Exception:
        return 'UNKNOWN'

def get_last_vaultpanel_backup():
    # Legacy markers did not prove success; the backup adapter is disabled.
    return None


def apply_oled_mode(payload: dict[str, Any]) -> dict[str, Any]:
    return disabled_operation('oled')


def apply_fan_profile(payload: dict[str, Any]) -> dict[str, Any]:
    return disabled_operation('fans')
