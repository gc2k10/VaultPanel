#!/usr/bin/env bash

# Unverified hardware adapter: no automatic installation or execution.
if [ "${VAULTPANEL_ENABLE_HARDWARE:-0}" != "1" ]; then
  echo "Hardware adapter disabled pending device-specific review" >&2
  exit 78
fi
set -euo pipefail

LED_SCRIPT="/opt/vaultpanel/scripts/pironman_led.sh"
ALERTS_URL="http://127.0.0.1:8090/api/alerts"
STATE_FILE="/tmp/vp_led_alert_active"
DANGER="#ff0000"

JSON="$(curl -fsS --max-time 2 "$ALERTS_URL" 2>/dev/null || true)"

HAS_CRITICAL=0

# analizujemy tylko bieżące alerts[], nie history
ACTIVE_LEVELS="$(printf '%s' "$JSON" | python3 - <<'PY'
import sys, json
try:
    data = json.load(sys.stdin)
    alerts = data.get("alerts", [])
    for a in alerts:
        print(str(a.get("level", "")).upper())
except Exception:
    pass
PY
)"

if echo "$ACTIVE_LEVELS" | grep -Eq '^(CRITICAL|CRIT|ERROR|FAILED|FAIL|OFFLINE|DEGRADED)$'; then
    HAS_CRITICAL=1
fi

if [ "$HAS_CRITICAL" -eq 1 ]; then
    echo "1" > "$STATE_FILE"
    "$LED_SCRIPT" STATIC "$DANGER" 80 50 OFF
    exit 0
fi

# jeśli wcześniej był alert, a teraz już go nie ma -> wróć do harmonogramu
if [ -f "$STATE_FILE" ]; then
    rm -f "$STATE_FILE"
    /opt/vaultpanel/scripts/vaultpanel_led_schedule.sh
fi
