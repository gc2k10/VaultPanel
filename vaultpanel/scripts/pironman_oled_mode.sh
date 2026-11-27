#!/usr/bin/env bash

# Unverified hardware adapter: no automatic installation or execution.
if [ "${VAULTPANEL_ENABLE_HARDWARE:-0}" != "1" ]; then
  echo "Hardware adapter disabled pending device-specific review" >&2
  exit 78
fi
set -euo pipefail

MODE="$(echo "${1:-CUSTOM}" | tr '[:lower:]' '[:upper:]')"

case "$MODE" in
  AUTO)
    sudo systemctl stop vaultpanel-oled.service 2>/dev/null || true
    sudo systemctl stop vaultpanel-oled-custom.service 2>/dev/null || true
    echo "OLED mode=AUTO"
    ;;
  CUSTOM)
    sudo systemctl start vaultpanel-oled.service 2>/dev/null || true
    sudo systemctl start vaultpanel-oled-custom.service 2>/dev/null || true
    echo "OLED mode=CUSTOM"
    ;;
  *)
    echo "Usage: $0 AUTO|CUSTOM"
    exit 1
    ;;
esac
