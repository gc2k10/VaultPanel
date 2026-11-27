"""Local synthetic fixture server: no collectors, hardware calls or host data."""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from app import create_app
import collectors

fixture = json.loads((pathlib.Path(__file__).parent / 'browser' / 'telemetry.json').read_text())
for name in ('overview', 'cooling', 'storage', 'services', 'network', 'alerts'):
    setattr(collectors, 'get_' + name, lambda name=name: fixture[name])

if __name__ == '__main__':
    create_app({'ACCESS_TOKEN': ''}).run(host='127.0.0.1', port=8091, debug=False)
