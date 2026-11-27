import os
if os.environ.get("VAULTPANEL_ENABLE_HARDWARE") != "1":
    raise SystemExit("Hardware adapter disabled pending device-specific review")
import time
import json
import subprocess
from PIL import Image, ImageDraw, ImageFont

from luma.core.interface.serial import i2c
from luma.oled.device import sh1106

STATE_FILE = "/opt/vaultpanel/state/oled_state.json"
LOGO_PATH = "/opt/vaultpanel/assets/logo.png"

serial = i2c(port=1, address=0x3C)
device = sh1106(serial)

font = ImageFont.load_default()


def run(cmd):
    return subprocess.getoutput(cmd)


def get_system():
    cpu = run("vcgencmd measure_temp").replace("temp=", "")
    fan = run("cat /sys/class/hwmon/hwmon4/fan1_input")
    return f"CPU {cpu} FAN {fan} RPM"


def get_storage():
    return run("df -h /data | awk 'NR==2 {print \"DATA \" $3 \"/\" $2 \" \" $5}'")


def get_network():
    return run("hostname -I | awk '{print \"IP \" $1}'")


def get_services():
    return "Nextcloud UNVERIFIED"


def draw_text(text):
    img = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(img)
    draw.text((2, 20), text, font=font, fill=255)
    device.display(img)


def draw_logo():
    img = Image.open(LOGO_PATH).convert("1")
    device.display(img)


def main():

    with open(STATE_FILE) as f:
        cfg = json.load(f)

    rotate = cfg.get("rotate_every_s", 5)
    logo_every = cfg.get("show_logo_every_s", 60)
    logo_time = cfg.get("show_logo_duration_s", 10)

    screens = {
        "system": get_system,
        "storage": get_storage,
        "network": get_network,
        "services": get_services,
    }

    last_logo = time.time()

    while True:

        now = time.time()

        if now - last_logo >= logo_every:
            draw_logo()
            time.sleep(logo_time)
            last_logo = time.time()

        for name in cfg["screens"]:

            if name == "logo":
                continue

            text = screens[name]()
            draw_text(text)
            time.sleep(rotate)


if __name__ == "__main__":
    main()
