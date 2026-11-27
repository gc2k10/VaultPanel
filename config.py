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
            if len(backends) != 1 or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.@-]*', service[backends[0]]):
                raise ValueError('Service requires exactly one valid backend identifier')
            service.setdefault('port', None)
            service['panel'] = None
        targets = [env.get('VAULTPANEL_PING_TARGET', ''), env.get('VAULTPANEL_DNS_TARGET', '')]
        if any(t and not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9.:-]*', t) for t in targets):
            raise ValueError('Invalid probe target')
        return cls(storage_mount=env.get('VAULTPANEL_STORAGE_MOUNT', '/'),
                   snapshot_dir=env.get('VAULTPANEL_SNAPSHOT_DIR', ''),
                   state_dir=Path(env.get('VAULTPANEL_STATE_DIR', 'state')),
                   smart_devices=devices, services=tuple(services), command_reads=flag == 'true',
                   ping_target=targets[0], dns_target=targets[1],
                   access_token=env.get('VAULTPANEL_ACCESS_TOKEN', ''))


settings = Settings.from_env()
