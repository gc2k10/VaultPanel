#!/usr/bin/env bash

# Unverified hardware adapter: no automatic installation or execution.
if [ "${VAULTPANEL_ENABLE_HARDWARE:-0}" != "1" ]; then
  echo "Hardware adapter disabled pending device-specific review" >&2
  exit 78
fi
set -e

PROFILE="$(echo "$1" | tr '[:lower:]' '[:upper:]')"
PWM_PATH="/sys/class/hwmon/hwmon4/pwm1"
ENABLE_PATH="/sys/class/hwmon/hwmon4/pwm1_enable"

get_nvme_temp() {
  local dev="$1"
  local t
  t="$(sudo smartctl -a "/dev/$dev" 2>/dev/null | awk '
    /^Temperature:/ {
      for (i=1; i<=NF; i++) if ($i ~ /^[0-9]+$/) { print $i; exit }
    }
    /^Temperature Sensor 1:/ {
      for (i=1; i<=NF; i++) if ($i ~ /^[0-9]+$/) { print $i; exit }
    }
  ')"
  echo "${t:-unknown}"
}

case "$PROFILE" in
  SILENT)
    PWM=90
    ;;
  BALANCED)
    PWM=140
    ;;
  PERFORMANCE)
    PWM=220
    ;;
  AUTO)
    T0="$(get_nvme_temp nvme0n1)"
    T1="$(get_nvme_temp nvme1n1)"
    if ! [[ "$T0" =~ ^[0-9]+$ && "$T1" =~ ^[0-9]+$ ]]; then
      echo "Temperature unavailable; refusing manual fan control" >&2
      exit 1
    fi
    MAXT="$T0"
    if [ "$T1" -gt "$MAXT" ]; then MAXT="$T1"; fi

    if [ "$MAXT" -lt 35 ]; then
      PWM=90
      PROFILE="AUTO:SILENT"
    elif [ "$MAXT" -le 45 ]; then
      PWM=140
      PROFILE="AUTO:BALANCED"
    else
      PWM=220
      PROFILE="AUTO:PERFORMANCE"
    fi
    ;;
  MANUAL)
    PWM="${2:-140}"
    ;;
  *)
    PWM=140
    PROFILE="BALANCED"
    ;;
esac

if ! [[ "$PWM" =~ ^[0-9]{1,3}$ ]] || (( 10#$PWM > 255 )); then
  echo "PWM must be an integer between 0 and 255" >&2
  exit 1
fi

sudo sh -c "echo 1 > '$ENABLE_PATH'"
sudo sh -c "echo $PWM > '$PWM_PATH'"

logger -t vaultpanel "Fan profile=$PROFILE pwm=$PWM"
echo "Applied profile=$PROFILE pwm=$PWM"
