"""Bounded, regular-file-only reads for optional local state."""
import json
import os
import re
import stat

MAX_STATE_BYTES = 4096


def read_text(path):
    descriptor = None
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > MAX_STATE_BYTES:
            return ''
        with os.fdopen(descriptor, 'rb') as stream:
            descriptor = None
            data = stream.read(MAX_STATE_BYTES + 1)
        return data.decode('utf-8') if len(data) <= MAX_STATE_BYTES else ''
    except (OSError, UnicodeError):
        return ''
    finally:
        if descriptor is not None:
            os.close(descriptor)


def read_state(path):
    try:
        data = json.loads(read_text(path))
    except (ValueError, TypeError):
        return {}
    if not isinstance(data, dict):
        return {}
    clean = {}
    choices = {
        'mode': {'STATIC', 'RAINBOW', 'BREATHING', 'PULSE', 'THERMAL', 'NIGHT', 'CUSTOM'},
        'profile': {'AUTO', 'SILENT', 'BALANCED', 'PERFORMANCE', 'MANUAL'},
        'fan_led': {'ON', 'OFF', 'FOLLOW'},
    }
    for key, values in choices.items():
        if isinstance(data.get(key), str) and data[key] in values:
            clean[key] = data[key]
    for key in ('brightness', 'speed'):
        if type(data.get(key)) is int and 0 <= data[key] <= 100:
            clean[key] = data[key]
    if isinstance(data.get('color'), str) and re.fullmatch(r'#[0-9a-fA-F]{6}', data['color']):
        clean['color'] = data['color']
    if isinstance(data.get('scene'), str) and len(data['scene']) <= 64:
        clean['scene'] = data['scene']
    return clean
