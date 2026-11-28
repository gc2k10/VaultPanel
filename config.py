"""Portable, environment-only configuration. No files are written on import."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    storage_mount: str = '/'
    snapshot_dir: str = ''
    state_dir: Path = Path('state')
    smart_devices: tuple = ()
    services: tuple = ()
    mdraid_reads: bool = False
    command_reads: bool = False
    ping_target: str = ''
    dns_target: str = ''
    access_token: str = field(default='', repr=False)

    @classmethod
    def from_env(cls, env=None):
        env = os.environ if env is None else env
        flag = env.get('VAULTPANEL_COMMAND_READS', 'false').lower()
        if flag not in {'true', 'false'}:
            raise ValueError('VAULTPANEL_COMMAND_READS must be true or false')
        mdraid_flag = env.get('VAULTPANEL_MDRAID_READS', 'false').lower()
        if mdraid_flag not in {'true', 'false'}:
            raise ValueError('VAULTPANEL_MDRAID_READS must be true or false')
        devices = tuple(filter(None, env.get('VAULTPANEL_SMART_DEVICES', '').split(',')))
        if any(not re.fullmatch(r'/dev/[a-zA-Z0-9_-]+', d) for d in devices):
            raise ValueError('Invalid SMART device path')
        services = json.loads(env.get('VAULTPANEL_SERVICES', '[]'))
        if not isinstance(services, list):
            raise ValueError('Services must be a JSON list')
        for service in services:
            if not isinstance(service, dict) or not isinstance(service.get('name'), str):
                raise ValueError('Service requires a name')
            backends = [k for k in ('systemd', 'docker') if k in service]
            if len(backends) != 1 or not isinstance(service[backends[0]], str) or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.@-]*', service[backends[0]]):
                raise ValueError('Service requires exactly one valid backend identifier')
            if service.get('port') is not None and (type(service['port']) is not int or not 1 <= service['port'] <= 65535):
                raise ValueError('Service port must be an integer between 1 and 65535')
            service.setdefault('port', None)
            service['panel'] = None
        targets = [env.get('VAULTPANEL_PING_TARGET', ''), env.get('VAULTPANEL_DNS_TARGET', '')]
        if any(t and not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9.:-]*', t) for t in targets):
            raise ValueError('Invalid probe target')
        for key, default in [('VAULTPANEL_STORAGE_MOUNT', '/'), ('VAULTPANEL_SNAPSHOT_DIR', '')]:
            value = env.get(key, default)
            if (key == 'VAULTPANEL_STORAGE_MOUNT' or value) and (not value.startswith('/') or '\x00' in value):
                raise ValueError('Storage and snapshot paths must be absolute')
        return cls(storage_mount=env.get('VAULTPANEL_STORAGE_MOUNT', '/'),
                   snapshot_dir=env.get('VAULTPANEL_SNAPSHOT_DIR', ''),
                   state_dir=Path(env.get('VAULTPANEL_STATE_DIR', 'state')),
                   mdraid_reads=mdraid_flag == 'true',
                   smart_devices=devices, services=tuple(services), command_reads=flag == 'true',
                   ping_target=targets[0], dns_target=targets[1],
                   access_token=env.get('VAULTPANEL_ACCESS_TOKEN', ''))


settings = Settings.from_env()
