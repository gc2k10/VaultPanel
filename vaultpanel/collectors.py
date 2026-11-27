from __future__ import annotations
import glob
import json
import os
import platform
import shutil
import socket
import subprocess
import time
import psutil
from datetime import datetime
from typing import Any

SERVICES = [
    {'name': 'SAMBA', 'systemd': 'smbd', 'port': 445, 'panel': None},
#   {'name': 'Nextcloud Web', 'systemd': 'apache2', 'port': 80, 'panel': '/nextcloud'},
#   {'name': 'PHP-FPM', 'systemd': 'php8.2-fpm', 'port': None, 'panel': None},
    {'name': 'TAILSCALE', 'systemd': 'tailscaled', 'port': None, 'panel': None},
    {'name': 'PI-HOLE', 'systemd': 'pihole-FTL', 'port': 80, 'panel': '/admin'},
    {'name': 'NETDATA', 'systemd': 'netdata', 'port': 19999, 'panel': ':19999'},
    {'name': 'NGINX', 'systemd': 'nginx', 'port': 80, 'panel': None},
    {'name': 'SSH', 'systemd': 'ssh', 'port': 22, 'panel': None},
#   { 'name': 'Nextcloud', 'systemd': 'docker', 'port': 443, 'panel': '/nextcloud' },
    { 'name': 'NEXTCLOUD', 'docker': 'nextcloud', 'port': 443, 'panel': '/nextcloud' },
]

ALERT_THRESHOLDS = {
    'cpu_warn': 65.0,
    'cpu_crit': 75.0,
    'disk_warn': 48.0,
    'disk_crit': 55.0,
    'storage_warn_pct': 85.0,
    'storage_crit_pct': 95.0,
}


def run(cmd: list[str] | str, timeout: int = 3) -> str:
    try:
        if isinstance(cmd, list) and cmd and cmd[0] == 'sudo':
            cmd = ['sudo', '-n', *cmd[1:]]
        result = subprocess.run(
            cmd,
            shell=isinstance(cmd, str),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return (result.stdout or '').strip() if result.returncode == 0 else ''
    except Exception:
        return ''


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
    path = "/data/.snapshots"
    try:
        if not os.path.exists(path):
            return None

        snapshots = [
            d for d in os.listdir(path)
            if os.path.isdir(os.path.join(path, d))
        ]

        if not snapshots:
            return None

        latest = sorted(snapshots)[-1]

        m = re.search(r'(\d{4})-(\d{2})-(\d{2})', latest)
        if m:
            yyyy, mm, dd = m.groups()
            return f"{yyyy}-{mm}-{dd} 00:00:00"

        return latest

    except Exception:
        return None

def get_last_scrub():
    try:
        out = run(["sudo", "btrfs", "scrub", "status", "/data"], timeout=5)

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
    devices = ["/dev/nvme0n1", "/dev/nvme1n1"]

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
    text = run(['free', '-m'])
    lines = [x for x in text.splitlines() if x.strip()]
    for line in lines:
        if line.startswith('Mem:'):
            parts = line.split()
            total = int(parts[1]); used = int(parts[2]); free = int(parts[3])
            pct = round((used / total) * 100, 1) if total else None
            return {'total_mb': total, 'used_mb': used, 'free_mb': free, 'used_pct': pct}
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


def check_internet() -> bool:
    return '1 received' in run(['ping', '-c', '1', '-W', '1', '1.1.1.1']) or '1 packets received' in run(['ping', '-c', '1', '-W', '1', '1.1.1.1'])


def check_dns() -> bool:
    return bool(run(['getent', 'hosts', 'openai.com']))


def systemd_status(name: str) -> dict[str, Any]:
    active = run(['systemctl', 'is-active', name])
    enabled = run(['systemctl', 'is-enabled', name])
    since = run(["systemctl", "show", name, "-p", "ActiveEnterTimestamp", "--value"])
    return {
        'active': active == 'active',
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
    while len(fans) < 3:
        fans.append({'label': f'FAN{len(fans)+1}', 'rpm': None})
    return fans[:3]


def detect_led_state() -> dict[str, Any]:
    state_path = os.environ.get('VAULTPANEL_LED_STATE', '/tmp/vaultpanel_led_state.json')
    if os.path.exists(state_path):
        try:
            with open(state_path) as f:
                return json.load(f)
        except Exception:
            pass
    return {
        'scene': 'VAULT GREEN',
        'mode': 'STATIC',
        'color': '#7CFC00',
        'brightness': 62,
        'speed': 50,
        'note': 'Placeholder state. scripts/pironman_led.sh.',
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
                if name.startswith("zram") or name.startswith("loop"):
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
    out = run(['sudo', 'smartctl', '-a', device], timeout=5)

    for line in out.splitlines():
        s = line.strip()

        if s.startswith('Temperature:'):
            parts = s.split()
            for token in parts:
                if token.isdigit():
                    return float(token)

        if s.startswith('Temperature Sensor 1:'):
            parts = s.split()
            for token in parts:
                if token.isdigit():
                    return float(token)

        if s.startswith('Temperature_Celsius'):
            nums = [token for token in s.replace(':', ' ').split() if token.isdigit()]
            if nums:
                return float(nums[-1])

    return None

def smart_health(device: str) -> str:
    out = run(['sudo', 'smartctl', '-a', device], timeout=5)

    for line in out.splitlines():
        s = line.strip()

        if s.startswith('Critical Warning:'):
            parts = s.split()
            for token in parts:
                if token in ('0', '0x00'):
                    return 'OK'
            return 'CHECK'

    if 'PASSED' in out:
        return 'PASSED'
    if out:
        return 'CHECK'
    return 'unknown'

def btrfs_status(path: str = '/') -> dict[str, Any]:
    fs_show = run(['sudo', 'btrfs', 'filesystem', 'show', path], timeout=5)
    scrub = run(['sudo', 'btrfs', 'scrub', 'status', path], timeout=5)
    degraded = 'degraded' in fs_show.lower() or 'degraded' in scrub.lower()

    return {
        'filesystem_show': fs_show,
        'scrub_status': scrub,
        'degraded': degraded,
        'healthy': None,  # Raw command text alone cannot certify filesystem health.
    }

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
    storage = disk_usage('/')
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
        'global_status': 'CRITICAL' if not internet else ('WARNING' if (temp and temp >= ALERT_THRESHOLDS['cpu_warn']) else 'NOMINAL'),
    }

def get_rear_fans_state() -> str:
    state_file = '/var/lib/vaultpanel/fan-control.state'
    try:
        if os.path.exists(state_file):
            with open(state_file) as f:
                for line in f:
                    if line.startswith('LAST_REAR='):
                        val = line.strip().split('=', 1)[1].strip().lower()
                        if val == 'on':
                            return 'ON'
                        if val == 'off':
                            return 'OFF'
        return 'UNKNOWN'
    except Exception:
        return 'UNKNOWN'

def get_cooling() -> dict[str, Any]:
    fans = []
    idx = 1
    for path in sorted(glob.glob('/sys/class/hwmon/hwmon*/fan*_input')):
        try:
            with open(path) as f:
                rpm = int(f.read().strip())
            fans.append({
                'label': f'FAN {idx}',
                'rpm': rpm,
            })
            idx += 1
        except Exception:
            pass

    cpu_temp = None
    temp_raw = run("vcgencmd measure_temp")
    if temp_raw:
        try:
            cpu_temp = float(temp_raw.replace("temp=", "").replace("'C", ""))
        except Exception:
            cpu_temp = None

    if cpu_temp is None:
        thermal_status = 'UNKNOWN'
    elif cpu_temp >= ALERT_THRESHOLDS['cpu_crit']:
        thermal_status = 'CRITICAL'
    elif cpu_temp >= ALERT_THRESHOLDS['cpu_warn']:
        thermal_status = 'WARNING'
    else:
        thermal_status = 'NOMINAL'

    state_path = os.environ.get('VAULTPANEL_LED_STATE', '/tmp/vaultpanel_led_state.json')
    led = {
        'scene': '--',
        'mode': 'STATIC',
        'color': '#7cfc00',
        'fan_led':'FOLLOW',
        'brightness': 62,
        'speed': 50,
        'note': '',
        'oled_mode': get_oled_mode(),
    }

    try:
        if os.path.exists(state_path):
            with open(state_path) as f:
                led.update(json.load(f))
    except Exception:
        pass

    fan_profile = 'AUTO'
    fan_state_path = os.environ.get('VAULTPANEL_FAN_STATE', '/tmp/vaultpanel_fan_state.json')
    try:
        if os.path.exists(fan_state_path):
            with open(fan_state_path) as f:
                fan_state = json.load(f)
                fan_profile = fan_state.get('profile', 'AUTO')
    except Exception:
        pass

    return {
        'cpu_temp_c': cpu_temp,
        'fans': fans,
        'thermal_status': thermal_status,
        'fan_profile': fan_profile,
        'led': led,
        'rear_fans': get_rear_fans_state(),
    }

def get_snapshot_info():
    path = "/data/.snapshots"
    try:
        if not os.path.exists(path):
            return {"snapshot_count": 0, "newest_snapshot": None}

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
        return {"snapshot_count": 0, "newest_snapshot": None}

def get_storage() -> dict[str, Any]:
    storage_mount = '/data'
    root = disk_usage(storage_mount)
    btrfs = btrfs_status(storage_mount)
    devices = list_block_devices()
    snapshot_info = get_snapshot_info()
    nvme_temps = {}
    for dev in ["nvme0n1", "nvme1n1"]:
        out = run(['sudo', 'smartctl', '-a', f'/dev/{dev}'])
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

import re

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
    docker_names = run("docker ps --format '{{.Names}}'").splitlines()

    for service in SERVICES:
        if 'docker' in service:
            container = service['docker']
            is_active = container in docker_names
            started = docker_started_at(container) if is_active else ''
            status = {
                'active': is_active,
                'active_text': 'active' if is_active else 'inactive',
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
        'tailscale_status': run(['tailscale', 'status'])[:800],
        'resolv_conf': run(['cat', '/etc/resolv.conf'])[:500],
    }


def get_alerts() -> dict[str, Any]:
    alerts = []
    overview = get_overview()
    storage = get_storage()
    if overview['cpu_temp_c'] is not None:
        status = classify_status(overview['cpu_temp_c'], ALERT_THRESHOLDS['cpu_warn'], ALERT_THRESHOLDS['cpu_crit'])
        if status != 'NOMINAL':
            alerts.append({'level': status, 'source': 'COOLING', 'message': f"CPU temperature is {overview['cpu_temp_c']}°C"})
    if not overview['internet_ok']:
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
    if storage['btrfs']['healthy'] is None and not storage['btrfs']['degraded']:
        alerts.append({'level': 'WARNING', 'source': 'BTRFS', 'message': 'Filesystem health is unverified; inspect raw diagnostics'})
    if storage['btrfs']['degraded']:
        alerts.append({'level': 'CRITICAL', 'source': 'BTRFS', 'message': 'Filesystem appears degraded'})
    if not alerts:
        alerts.append({'level': 'INFO', 'source': 'SYSTEM', 'message': 'No active alerts'})
    return {'alerts': alerts, 'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

def apply_led_settings(payload: dict[str, Any]) -> dict[str, Any]:
    allowed_modes = {'STATIC', 'RAINBOW', 'BREATHING', 'PULSE', 'THERMAL', 'NIGHT', 'CUSTOM'}
    allowed_fan_led = {'ON', 'OFF', 'FOLLOW'}

    mode = str(payload.get('mode', 'STATIC')).upper()
    if mode not in allowed_modes:
        return {'ok': False, 'error': 'Unsupported LED mode'}

    fan_led = str(payload.get('fan_led', 'FOLLOW')).upper()
    if fan_led not in allowed_fan_led:
        fan_led = 'FOLLOW'

    color = str(payload.get('color', '#7CFC00'))[:16]
    brightness = max(0, min(100, int(payload.get('brightness', 60))))
    speed = max(0, min(100, int(payload.get('speed', 50))))

    state = {
        'scene': payload.get('scene', 'CUSTOM'),
        'mode': mode,
        'color': color,
        'brightness': brightness,
        'speed': speed,
        'fan_led': fan_led,
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'note': 'IO LEDs: IO color. Fan LED: ON/OFF/FOLLOW.',
    }

    state_path = os.environ.get('VAULTPANEL_LED_STATE', '/tmp/vaultpanel_led_state.json')
    with open(state_path, 'w') as f:
        json.dump(state, f)

    script = os.path.join(os.path.dirname(__file__), 'scripts', 'pironman_led.sh')
    if os.path.exists(script):
        run([script, mode, color, str(brightness), str(speed), fan_led], timeout=8)

    return {'ok': True, 'state': state}

def get_oled_mode() -> str:
    try:
        out = run(['systemctl', 'is-active', 'vaultpanel-oled-custom.service'], timeout=5).strip()
        return 'CUSTOM' if out == 'active' else 'AUTO'
    except Exception:
        return 'AUTO'

def get_last_vaultpanel_backup():
    try:
        with open("/opt/vaultpanel/.last_vaultpanel_backup") as f:
            return f.read().strip()
    except:
        return None

def apply_oled_mode(payload: dict[str, Any]) -> dict[str, Any]:
    mode = str(payload.get('mode', 'AUTO')).upper()
    if mode not in {'AUTO', 'CUSTOM'}:
        return {'ok': False, 'error': 'Unsupported OLED mode'}

    script = os.path.join(os.path.dirname(__file__), 'scripts', 'oled_mode.sh')
    if not os.path.exists(script):
        return {'ok': False, 'error': 'oled_mode.sh not found'}

    result = run([script, mode], timeout=10)
    return {'ok': True, 'mode': mode, 'result': result}

def apply_fan_profile(payload: dict[str, Any]) -> dict[str, Any]:
    allowed = {'AUTO', 'SILENT', 'BALANCED', 'PERFORMANCE', 'MANUAL'}
    profile = str(payload.get('profile', 'AUTO')).upper()

    if profile not in allowed:
        return {'ok': False, 'error': 'Unsupported fan profile'}

    state = {
        'profile': profile,
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }

    state_path = os.environ.get('VAULTPANEL_FAN_STATE', '/tmp/vaultpanel_fan_state.json')
    try:
        with open(state_path, 'w') as f:
            json.dump(state, f)
    except Exception as e:
        return {'ok': False, 'error': f'Cannot save fan state: {e}'}

    script = os.path.join(os.path.dirname(__file__), 'scripts', 'pironman_fans.sh')
    result = ''
    if os.path.exists(script):
        result = run([script, profile], timeout=5)

    return {
        'ok': True,
        'profile': profile,
        'result': result,
        'updated_at': state['updated_at'],
    }
