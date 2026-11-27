#!/usr/bin/env python3
import os
if os.environ.get("VAULTPANEL_ENABLE_HARDWARE") != "1":
    raise SystemExit("Hardware adapter disabled pending device-specific review")
import os
import time
import subprocess
from PIL import Image, ImageDraw, ImageFont
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106

LOGO_PATH = "/opt/vaultpanel/assets/logo.png"

serial = i2c(port=1, address=0x3C)
device = sh1106(serial)
font = ImageFont.load_default()


def run(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except Exception:
        return "--"


def get_cpu_usage() -> str:
    try:
        line = run("grep 'cpu ' /proc/stat")
        parts1 = [int(x) for x in line.split()[1:8]]
        total1 = sum(parts1)
        idle1 = parts1[3] + parts1[4]
        time.sleep(0.2)
        line = run("grep 'cpu ' /proc/stat")
        parts2 = [int(x) for x in line.split()[1:8]]
        total2 = sum(parts2)
        idle2 = parts2[3] + parts2[4]
        total_delta = total2 - total1
        idle_delta = idle2 - idle1
        if total_delta <= 0:
            return "--%"
        usage = 100.0 * (1.0 - idle_delta / total_delta)
        return f"{usage:.0f}%"
    except Exception:
        return "--%"


def get_cpu_temp() -> str:
    out = run("vcgencmd measure_temp")
    if "temp=" in out:
        return out.replace("temp=", "").replace("'C", "°C")
    return "--°C"


def get_disk_usage() -> str:
    out = run("df -h /data | awk 'NR==2 {print $5}'")
    return out if out else "--%"


def get_ip() -> str:
    out = run("hostname -I | awk '{print $1}'")
    return out if out else "--"


def draw_text(lines):
    img = Image.new("1", (128, 64), 0)
    draw = ImageDraw.Draw(img)

    y = 0
    for line in lines[:4]:
        draw.text((2, y), line, font=font, fill=255)
        y += 16

    device.display(img)


def draw_logo():
    try:
        if not os.path.exists(LOGO_PATH):
            draw_text(["LOGO", "NOT FOUND"])
            return

        img = Image.open(LOGO_PATH).convert("1")
        if img.size != (128, 64):
            img = img.resize((128, 64))
        device.display(img)
    except Exception:
        draw_text(["LOGO", "ERROR"])


def draw_stats():
    lines = [
        f"CPU  {get_cpu_usage()}",
        f"TEMP {get_cpu_temp()}",
        f"DISK {get_disk_usage()}",
        f"IP   {get_ip()}",
    ]
    draw_text(lines)


def main():
    while True:
        draw_stats()
        time.sleep(30)

        draw_logo()
        time.sleep(30)

if __name__ == "__main__":
    main()
