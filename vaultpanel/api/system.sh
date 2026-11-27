#!/bin/bash

SNAP_DIR="/data/.snapshots"

smart_overall="FAIL"
if grep -q PASSED /data/system-backup/smart_status 2>/dev/null; then
  smart_overall="OK"
fi

raid_status="DEGRADED"
if grep -q '\[UU\]' /proc/mdstat 2>/dev/null; then
  raid_status="OK"
fi

backup_value="$(cat /data/system-backup/last_backup 2>/dev/null || echo 'NO DATA')"
scrub_value="$(cat /data/system-backup/last_scrub 2>/dev/null || echo 'NO DATA')"

usage_line="$(df -h /data 2>/dev/null | awk 'NR==2')"
fs_type="$(df -T /data 2>/dev/null | awk 'NR==2 {print $2}')"
mountpoint="$(df -h /data 2>/dev/null | awk 'NR==2 {print $6}')"
total_size="$(echo "$usage_line" | awk '{print $2}')"
used_space="$(echo "$usage_line" | awk '{print $3}')"
free_space="$(echo "$usage_line" | awk '{print $4}')"
usage_pct="$(echo "$usage_line" | awk '{print $5}')"

temp_raw="$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null)"
if [ -n "$temp_raw" ]; then
  temp_value="$(awk "BEGIN {printf \"%.1f°C\", $temp_raw/1000}")"
else
  temp_value="NO DATA"
fi

load_value="$(uptime | awk -F'load average:' '{print $2}' | sed 's/^ *//')"

snapshot_count="0"
newest_snapshot="NO DATA"
if [ -d "$SNAP_DIR" ]; then
  snapshot_count="$(find "$SNAP_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')"
  newest_snapshot="$(find "$SNAP_DIR" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %f\n' 2>/dev/null | sort -nr | head -n1 | cut -d' ' -f2-)"
  [ -n "$newest_snapshot" ] || newest_snapshot="NO DATA"
fi

nvme0_smart="$(awk '
  /^NVME0:/ { in_block=1; next }
  /^NVME1:/ { in_block=0 }
  in_block && /SMART overall-health self-assessment test result:/ {
    sub(/.*result: /, "", $0); print; exit
  }
' /data/system-backup/smart_status 2>/dev/null)"

nvme1_smart="$(awk '
  /^NVME1:/ { in_block=1; next }
  in_block && /SMART overall-health self-assessment test result:/ {
    sub(/.*result: /, "", $0); print; exit
  }
' /data/system-backup/smart_status 2>/dev/null)"

[ -n "$nvme0_smart" ] || nvme0_smart="NO DATA"
[ -n "$nvme1_smart" ] || nvme1_smart="NO DATA"

echo "SMART:"
echo "$smart_overall"

echo "RAID:"
echo "$raid_status"

echo "BACKUP:"
echo "$backup_value"

echo "SCRUB:"
echo "$scrub_value"

echo "USAGE:"
echo "${usage_pct:-NO DATA}"

echo "TEMP:"
echo "$temp_value"

echo "LOAD:"
echo "${load_value:-NO DATA}"

echo "FILESYSTEM:"
echo "${fs_type:-NO DATA}"

echo "MOUNTPOINT:"
echo "${mountpoint:-NO DATA}"

echo "TOTAL_SIZE:"
echo "${total_size:-NO DATA}"

echo "USED_SPACE:"
echo "${used_space:-NO DATA}"

echo "FREE_SPACE:"
echo "${free_space:-NO DATA}"

echo "SNAPSHOT_COUNT:"
echo "$snapshot_count"

echo "NEWEST_SNAPSHOT:"
echo "$newest_snapshot"

echo "NVME0_SMART:"
echo "$nvme0_smart"

echo "NVME1_SMART:"
echo "$nvme1_smart"
