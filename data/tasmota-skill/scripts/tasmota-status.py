#!/usr/bin/env python3
"""
Get summary of all Tasmota devices from inventory
"""

import subprocess
import json
import time
from pathlib import Path

CSV_FILE = Path.home() / ".openclaw/workspace/memory/tasmota-inventory.csv"

def get_device_status(ip):
    """Get power status from device"""
    try:
        result = subprocess.run(
            ["python3", Path.home() / ".openclaw/workspace/scripts/tasmota-control.py", ip, "status", "0"],
            capture_output=True,
            timeout=3
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if "StatusSTS" in data:
                return data["StatusSTS"].get("POWER", "UNKNOWN")
            if "Status" in data:
                return data["Status"].get("Power", "ON" if data["Status"].get("Power") == 1 else "OFF")
        return "UNKNOWN"
    except:
        return "TIMEOUT"

print("🔍 Tasmota Device Summary")
print("="*80)

devices = []
with open(CSV_FILE) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(',')
        if len(parts) >= 3 and parts[0].strip().startswith('192'):
            ip = parts[0].strip()
            name = parts[1].strip().replace(' - Main Menu', '')
            version = parts[2].strip()
            devices.append((ip, name, version))

# Quick check of first few devices
print(f"Found {len(devices)} devices\n")
print(f"{'IP Address':<18} {'Device Name':<30} {'Version':<12} {'Power'}")
print("-"*80)

for ip, name, version in devices:
    power = get_device_status(ip)
    print(f"{ip:<18} {name[:28]:<30} {version:<12} {power}")
    time.sleep(0.1)  # Don't overwhelm the network

print("="*80)