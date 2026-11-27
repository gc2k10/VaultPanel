#!/usr/bin/env bash

# Unverified hardware adapter: no automatic installation or execution.
if [ "${VAULTPANEL_ENABLE_HARDWARE:-0}" != "1" ]; then
  echo "Hardware adapter disabled pending device-specific review" >&2
  exit 78
fi
set -euo pipefail

LED_SCRIPT="/opt/vaultpanel/scripts/pironman_led.sh"
ALERTS_URL="http://127.0.0.1:8090/api/alerts"
DANGER="#ff0000"

ALERTS_JSON="$(curl -fsS --max-time 2 "$ALERTS_URL" 2>/dev/null || true)"

if printf '%s' "$ALERTS_JSON" | grep -Eiq '"(severity|status|level|state|badge)"[[:space:]]*:[[:space:]]*"?(warning|warn|alert|critical|crit|error|failed|fail|offline|degraded)'; then
  "$LED_SCRIPT" STATIC "$DANGER" 80
  exit 0
fi

if printf '%s' "$ALERTS_JSON" | grep -Eiq '\b(WARNING|WARN|ALERT|CRITICAL|CRIT|ERROR|FAILED|FAIL|OFFLINE|DEGRADED)\b'; then
  "$LED_SCRIPT" STATIC "$DANGER" 80
  exit 0
fi

exit 0
