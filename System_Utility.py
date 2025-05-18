import os
import time
import json
import platform
import requests
import subprocess
from datetime import datetime

API_URL = "https://your-backend-server.com/report"
MACHINE_ID_FILE = os.path.expanduser("~/.machine_id")
CHECK_INTERVAL = 1800  # 30 minutes

# Function to get a unique machine ID
def get_machine_id():
    if os.path.exists(MACHINE_ID_FILE):
        with open(MACHINE_ID_FILE, 'r') as f:
            return f.read().strip()
    else:
        machine_id = os.popen("uuidgen").read().strip()
        with open(MACHINE_ID_FILE, 'w') as f:
            f.write(machine_id)
        return machine_id

# Functions for system checks (platform-specific logic would be added per OS)
def check_disk_encryption():
    os_name = platform.system()
    try:
        if os_name == "Windows":
            output = subprocess.check_output("manage-bde -status", shell=True).decode()
            return "On" if "Percentage Encrypted: 100%" in output else "Off"
        elif os_name == "Linux":
            return "Encrypted" if os.path.exists("/dev/mapper") else "Unencrypted"
        else:
            return "Unknown"
    except Exception as e:
        return e

def check_os_update_status():
    os_name = platform.system()
    try:
        if os_name == "Windows":
            return "Check manually"  # Windows update status requires PowerShell
        elif os_name == "Linux":
            output = subprocess.check_output(["apt", "list", "--upgradable"]).decode()
            return "Up-to-date" if "Listing... Done" in output and len(output.strip().splitlines()) == 1 else "Outdated"
        else:
            return "Unknown"
    except Exception as e:
        return e


def check_antivirus_status():
    os_name = platform.system()
    try:
        if os_name == "Windows":
            output = subprocess.check_output('"C:\\Program Files\\Windows Defender\\MpCmdRun.exe" -GetAVStatus', shell=True).decode()
            return "Active" if "Enabled" in output else "Inactive"
        elif os_name == "Linux":
            output = subprocess.getoutput("systemctl is-active clamav-daemon")
            return "Active" if "active" in output else "Inactive"
        else:
            return "Unknown"
    except Exception as e:
        return e

def check_inactivity_sleep():
    os_name = platform.system()
    try:
        if os_name == "Windows":
            output = subprocess.check_output("powercfg -query", shell=True).decode()
            return "10" in output or "600" in output
        elif os_name == "Linux":
            output = subprocess.getoutput("gsettings get org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout")
            sleep_time = int(output.strip())
            return sleep_time <= 600
        else:
            return "Unknown"
    except Exception as e:
        return e

def collect_status():
    return {
        "machine_id": get_machine_id(),
        "timestamp": datetime.utcnow().isoformat(),
        "os": platform.system(),
        "disk_encryption": check_disk_encryption(),
        "os_update_status": check_os_update_status(),
        "antivirus": check_antivirus_status(),
        "sleep_setting": check_inactivity_sleep()
    }

# Daemon-like behavior
def run_daemon():
    last_payload = None
    while True:
        status = collect_status()
        if status != last_payload:
            try:
                requests.post(API_URL, json=status)
                last_payload = status
            except Exception as e:
                print("[Error] Failed to report: ", e)
        time.sleep(CHECK_INTERVAL)
