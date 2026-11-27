#!/usr/bin/env bash

# Unverified hardware adapter: no automatic installation or execution.
if [ "${VAULTPANEL_ENABLE_HARDWARE:-0}" != "1" ]; then
  echo "Hardware adapter disabled pending device-specific review" >&2
  exit 78
fi
set -euo pipefail

LED_SCRIPT="/opt/vaultpanel/scripts/pironman_led.sh"
ALERTS_URL="http://127.0.0.1:8090/api/alerts"

# kolory
VAULT_GREEN="#7cfc00"
DANGER="#ff0000"

# minuty od północy
HOUR="$(date +%H)"
MINUTE="$(date +%M)"
NOW=$((10#$HOUR * 60 + 10#$MINUTE))

# sprawdzenie czy VaultPanel zgłasza jakikolwiek warning / alert / critical / error / degraded itp.
HAS_ALERT=0
ALERTS_JSON="$(curl -fsS --max-time 2 "$ALERTS_URL" 2>/dev/null || true)"

if echo "$ALERTS_JSON" | grep -Eiq '"(severity|status|level|state|badge)":"?(warning|warn|alert|critical|crit|error|failed|fail|offline|degraded)'; then
    HAS_ALERT=1
fi

if echo "$ALERTS_JSON" | grep -Eiq '\b(WARNING|WARN|ALERT|CRITICAL|CRIT|ERROR|FAILED|FAIL|OFFLINE|DEGRADED)\b'; then
    HAS_ALERT=1
fi

# 1) priorytet: jakikolwiek alert => danger 80%
if [ "$HAS_ALERT" -eq 1 ]; then
    "$LED_SCRIPT" STATIC "$DANGER" 80
    exit 0
fi

# 2) harmonogram normalny
# 08:00-17:59 => vault green 30%
if [ "$NOW" -ge 480 ] && [ "$NOW" -lt 1080 ]; then
    "$LED_SCRIPT" STATIC "$VAULT_GREEN" 30
    exit 0
fi

# 18:00-21:59 => vault green 70%
if [ "$NOW" -ge 1080 ] && [ "$NOW" -lt 1320 ]; then
    "$LED_SCRIPT" STATIC "$VAULT_GREEN" 70
    exit 0
fi

# 22:00-07:59 => LED OFF
/usr/local/bin/pironman5 -re false >/dev/null 2>&1 || true
exit 0
