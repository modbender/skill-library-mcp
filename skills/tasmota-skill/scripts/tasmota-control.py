#!/usr/bin/env python3
"""
Tasmota Device Controller
Control Tasmota devices via HTTP JSON API
"""

import sys
import json
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

def tasmota_command(ip, command, timeout=5):
    """Send command to Tasmota device"""
    try:
        # Tasmota JSON API format: /cm?cmnd=COMMAND
        cmd = command.replace(' ', '%20')
        url = f"http://{ip}/cm?cmnd={cmd}"

        req = Request(url, headers={'User-Agent': 'Tasmota-Controller'})
        with urlopen(req, timeout=timeout) as response:
            data = response.read()
            return json.loads(data.decode('utf-8'))
    except Exception as e:
        return {"ERROR": str(e)}

def toggle_power(ip):
    """Toggle power on/off"""
    return tasmota_command(ip, "Power")

def set_power(ip, state):
    """Set power state (ON/OFF/TOGGLE)"""
    return tasmota_command(ip, f"Power {state.upper()}")

def get_status(ip, status_type="0"):
    """Get device status
    status_type codes:
    0 = Status
    1 = StatusPRM (Parameters)
    2 = StatusFWR (Firmware)
    3 = StatusLOG (Log)
    4 = StatusNET (Network)
    5 = StatusMQT (MQTT)
    9 = StatusTIM (Time)
    """
    return tasmota_command(ip, f"Status {status_type}")

def set_brightness(ip, level):
    """Set brightness (0-100)"""
    return tasmota_command(ip, f"Dimmer {level}")

def set_color(ip, color):
    """Set RGB color (hex or r,g,b)"""
    return tasmota_command(ip, f"Color {color}")

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python3 tasmota-control.py <IP> power [on|off|toggle]")
        print("  python3 tasmota-control.py <IP> status [0-9|all]")
        print("  python3 tasmota-control.py <IP> brightness <0-100>")
        print("  python3 tasmota-control.py <IP> color <hex>")
        sys.exit(1)

    ip = sys.argv[1]
    cmd = sys.argv[2].lower()

    if cmd == "power":
        if len(sys.argv) > 3:
            result = set_power(ip, sys.argv[3])
        else:
            result = toggle_power(ip)
    elif cmd == "status":
        if len(sys.argv) > 3:
            status_type = sys.argv[3]
            if status_type == "all":
                # Get all statuses
                result = {"statuses": {}}
                for st in ["0", "1", "2", "3", "4", "5", "9"]:
                    result["statuses"][st] = get_status(ip, st)
            else:
                result = get_status(ip, status_type)
        else:
            result = get_status(ip, "0")
    elif cmd == "brightness":
        if len(sys.argv) < 4:
            print("Error: brightness requires level (0-100)")
            sys.exit(1)
        result = set_brightness(ip, sys.argv[3])
    elif cmd == "color":
        if len(sys.argv) < 4:
            print("Error: color requires hex value (e.g., FF0000)")
            sys.exit(1)
        result = set_color(ip, sys.argv[3])
    else:
        # Raw command
        result = tasmota_command(ip, ' '.join(sys.argv[2:]))

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()