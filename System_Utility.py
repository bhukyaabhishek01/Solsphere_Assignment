import os
import time
import json
import platform
import requests
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
    return "Unknown"  # Placeholder

def check_os_update_status():
    return "Unknown"  # Placeholder

def check_antivirus_status():
    return "Unknown"  # Placeholder

def check_inactivity_sleep():
    return "Unknown"  # Placeholder

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
