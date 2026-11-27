from flask import Flask, jsonify, render_template, request
import json
import os
import subprocess
from pathlib import Path
from security import protect_app
from datetime import datetime
from collectors import (
    get_overview,
    get_cooling,
    get_storage,
    get_services,
    get_network,
    get_alerts,
    apply_led_settings,
    apply_fan_profile,
    apply_oled_mode,
)

BASE_DIR = Path(__file__).resolve().parent
ALERT_HISTORY_FILE = str(Path(os.environ.get("VAULTPANEL_STATE_DIR", str(BASE_DIR / "state"))) / "alert_history.json")
app = Flask(__name__)
protect_app(app)

@app.route('/api/backup', methods=['POST'])
def api_backup():
    try:
        subprocess.Popen(
            ['sudo', '/opt/vaultpanel/backup.sh'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return jsonify({'ok': True, 'message': 'Backup started'})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

def ensure_dir_for_file(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def read_alert_history():
    try:
        if not os.path.exists(ALERT_HISTORY_FILE):
            return []
        with open(ALERT_HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def write_alert_history(history):
    try:
        ensure_dir_for_file(ALERT_HISTORY_FILE)
        with open(ALERT_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[vaultpanel] failed to write alert history: {e}")


def normalize_alert_for_history(alert, generated_at):
    return {
        "timestamp": generated_at,
        "source": str(alert.get("source", "SYSTEM")),
        "level": str(alert.get("level", "INFO")).upper(),
        "message": str(alert.get("message", "NO DETAILS"))
    }


def append_alerts_to_history(current_alerts, generated_at):
    history = read_alert_history()

    normalized = [
        normalize_alert_for_history(alert, generated_at)
        for alert in (current_alerts or [])
    ]

    for alert in normalized:
        last = history[-1] if history else None

        if (
            last
            and last.get("source") == alert["source"]
            and last.get("level") == alert["level"]
            and last.get("message") == alert["message"]
        ):
            continue

        history.append(alert)

    history = history[-200:]
    # Read-only intake build: do not persist history during a GET request.
    return history

@app.route('/')
def index():
    return render_template('index.html', title='VaultPanel')

@app.route('/retro')
def index_retro():
    return render_template('index_retro.html', title='VaultPanel Retro')

@app.route('/api/overview')
def api_overview():
    return jsonify(get_overview())

@app.route('/api/cooling')
def api_cooling():
    return jsonify(get_cooling())

@app.route('/api/storage')
def api_storage():
    return jsonify(get_storage())

@app.route('/api/services')
def api_services():
    return jsonify(get_services())

@app.route('/api/network')
def api_network():
    return jsonify(get_network())

@app.route('/api/alerts')
def api_alerts():
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    payload = get_alerts()

    if isinstance(payload, dict):
        alerts = payload.get("alerts", [])
    elif isinstance(payload, list):
        alerts = payload
    else:
        alerts = []

    if not alerts:
        alerts = [{"level": "INFO", "message": "No active alerts", "source": "SYSTEM"}]

    history = append_alerts_to_history(alerts, generated_at)

    return jsonify({
        "alerts": alerts,
        "history": list(reversed(history[-10:])),
        "generated_at": generated_at
    })

@app.route('/api/led', methods=['POST'])
def api_led():
    payload = request.get_json(force=True, silent=True) or {}
    return jsonify(apply_led_settings(payload))

@app.route('/api/fans', methods=['POST'])
def api_fans():
    payload = request.get_json(force=True, silent=True) or {}
    return jsonify(apply_fan_profile(payload))

@app.post('/api/oled')
def api_oled():
    data = request.json or {}
    return jsonify(apply_oled_mode(data))

@app.route('/api/system')
def api_system():
    try:
        output = subprocess.check_output(
            ["bash", str(BASE_DIR / "api" / "system.sh")],
            text=True, timeout=5
        )
        return output, 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        return f"ERROR: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8090, debug=False)
