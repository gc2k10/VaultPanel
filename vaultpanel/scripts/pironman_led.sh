#!/usr/bin/env bash

# Unverified hardware adapter: no automatic installation or execution.
if [ "${VAULTPANEL_ENABLE_HARDWARE:-0}" != "1" ]; then
  echo "Hardware adapter disabled pending device-specific review" >&2
  exit 78
fi
set -e

MODE="$(echo "${1:-STATIC}" | tr '[:lower:]' '[:upper:]')"
COLOR="${2:-#7cfc00}"
BRIGHT="${3:-80}"
SPEED="${4:-50}"
FAN_LED="$(echo "${5:-FOLLOW}" | tr '[:lower:]' '[:upper:]')"

COLOR="${COLOR#\#}"

case "$MODE" in
  STATIC)
    STYLE="solid"
    ENABLE="true"
    ;;
  RAINBOW)
    STYLE="rainbow"
    ENABLE="true"
    ;;
  BREATHING)
    STYLE="breathing"
    ENABLE="true"
    ;;
  PULSE)
    STYLE="flow"
    ENABLE="true"
    ;;
  THERMAL)
    STYLE="solid"
    COLOR="ffb000"
    ENABLE="true"
    ;;
  NIGHT)
    STYLE="solid"
    COLOR="000000"
    ENABLE="false"
    ;;
  CUSTOM)
    STYLE="solid"
    ENABLE="true"
    ;;
  *)
    STYLE="solid"
    ENABLE="true"
    ;;
esac

case "$FAN_LED" in
  ON) FAN_LED_ARG="on" ;;
  OFF) FAN_LED_ARG="off" ;;
  FOLLOW) FAN_LED_ARG="follow" ;;
  *) FAN_LED_ARG="follow" ;;
esac

sudo /usr/local/bin/pironman5 \
  -re "$ENABLE" \
  -rc "$COLOR" \
  -rb "$BRIGHT" \
  -rs "$STYLE" \
  -rp "$SPEED" \
  -rl 4 \
  -fl "$FAN_LED_ARG"

sudo systemctl restart pironman5.service >/dev/null 2>&1
sleep 2

echo "Applied MODE=$MODE COLOR=$COLOR BRIGHT=$BRIGHT SPEED=$SPEED FAN_LED=$FAN_LED_ARG"
