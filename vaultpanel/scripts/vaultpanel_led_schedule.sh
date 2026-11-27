#!/usr/bin/env bash

# Unverified hardware adapter: no automatic installation or execution.
if [ "${VAULTPANEL_ENABLE_HARDWARE:-0}" != "1" ]; then
  echo "Hardware adapter disabled pending device-specific review" >&2
  exit 78
fi
set -euo pipefail

LED_SCRIPT="/opt/vaultpanel/scripts/pironman_led.sh"
VAULT_GREEN="#7cfc00"

case "$(date +%H:%M)" in
  08:00)
    "$LED_SCRIPT" STATIC "$VAULT_GREEN" 30 50 OFF
    ;;
  18:00)
    "$LED_SCRIPT" STATIC "#012F7B" 30 50 OFF
    ;;
  22:00)
    "$LED_SCRIPT" NIGHT "" 0 50 OFF
    ;;
esac
