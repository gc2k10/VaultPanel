#!/usr/bin/env bash

# Unverified hardware adapter: no automatic installation or execution.
if [ "${VAULTPANEL_ENABLE_HARDWARE:-0}" != "1" ]; then
  echo "Hardware adapter disabled pending device-specific review" >&2
  exit 78
fi
set -e

STATE_FILE="/tmp/vaultpanel_fan_state.json"

if [ -f "$STATE_FILE" ] && grep -q '"profile": "AUTO"' "$STATE_FILE"; then
  /opt/vaultpanel/scripts/pironman_fans.sh AUTO >/dev/null 2>&1 || true
fi
