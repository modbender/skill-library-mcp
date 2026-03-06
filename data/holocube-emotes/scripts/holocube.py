#!/usr/bin/env python3
"""
Holocube emote controller.
Push expressions to a GeekMagic holocube based on agent state.

Usage:
    python3 holocube.py <emote|state> [--static] [--ip IP]
    python3 holocube.py --list
    python3 holocube.py --status
    python3 holocube.py --auto
"""

import sys
import argparse
import urllib.request
import urllib.error
import json
from datetime import datetime

DEFAULT_IP = "192.168.0.245"

EMOTES = ["neutral", "happy", "thinking", "surprised", "laughing", "sleeping", "custom"]


def discover_holocube():
    """Scan local subnet for GeekMagic devices via /v.json."""
    import socket
    import concurrent.futures

    def check_host(ip):
        try:
            with urllib.request.urlopen(f"http://{ip}/v.json", timeout=1) as r:
                data = json.loads(r.read())
                if "m" in data and "v" in data:
                    return ip, data
        except:
            pass
        return None, None

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    subnet = ".".join(local_ip.split(".")[:3])

    print(f"Scanning {subnet}.0/24 for GeekMagic devices...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(check_host, f"{subnet}.{i}"): i for i in range(1, 255)}
        found = []
        for future in concurrent.futures.as_completed(futures):
            ip, data = future.result()
            if ip:
                found.append((ip, data))
                print(f"  FOUND: {ip} — {data.get('m', '?')} {data.get('v', '?')}")

    if not found:
        print("No GeekMagic devices found.")
    return found

# Session/agent state → emote mapping
STATE_MAP = {
    "idle":        "neutral",
    "working":     "thinking",
    "complete":    "happy",
    "error":       "surprised",
    "concerned":   "thinking",
    "funny":       "laughing",
    "unexpected":  "surprised",
    "night":       "sleeping",
    "opus":        "thinking",
    "haiku":       "neutral",
    "spawning":    "thinking",
}


def set_emote(emote, static=False, ip=None):
    """Push an emote to the holocube."""
    ip = ip or DEFAULT_IP
    if emote in STATE_MAP:
        emote = STATE_MAP[emote]
    if emote not in EMOTES:
        print(f"ERROR: Unknown emote '{emote}'. Available: {', '.join(EMOTES)}")
        return 1

    ext = "jpg" if static else "gif"
    filename = f"adam-{emote}.{ext}"
    url = f"http://{ip}/set?img=%2Fimage%2F{filename}"

    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            body = resp.read().decode()
            if "OK" in body or resp.status == 200:
                print(f"EMOTE: {emote} ({ext})")
                return 0
            print(f"ERROR: Unexpected response: {body}")
            return 1
    except (urllib.error.URLError, Exception) as e:
        print(f"ERROR: Can't reach holocube at {ip}: {e}")
        return 1


def get_status(ip=None):
    """Check holocube connectivity and storage."""
    ip = ip or DEFAULT_IP
    try:
        with urllib.request.urlopen(f"http://{ip}/v.json", timeout=3) as r:
            info = json.loads(r.read())
        with urllib.request.urlopen(f"http://{ip}/space.json", timeout=3) as r:
            space = json.loads(r.read())
        print(f"Model: {info.get('m', 'unknown')}")
        print(f"Version: {info.get('v', 'unknown')}")
        print(f"Storage: {space.get('free', 0) // 1024}KB free / {space.get('total', 0) // 1024}KB total")
        print("Status: online")
        return 0
    except Exception as e:
        print(f"Status: offline ({e})")
        return 1


def auto_emote(ip=None):
    """Pick emote based on time of day."""
    hour = datetime.now().hour
    if hour >= 23 or hour < 7:
        return set_emote("sleeping", ip=ip)
    elif 7 <= hour < 9:
        return set_emote("happy", ip=ip)
    else:
        return set_emote("neutral", ip=ip)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Holocube emote controller")
    parser.add_argument("emote", nargs="?", help="Emote or state name")
    parser.add_argument("--static", action="store_true", help="Use static JPG instead of GIF")
    parser.add_argument("--ip", default=DEFAULT_IP, help="Holocube IP address")
    parser.add_argument("--list", action="store_true", help="List available emotes and states")
    parser.add_argument("--status", action="store_true", help="Check holocube status")
    parser.add_argument("--auto", action="store_true", help="Auto-select emote based on time")
    parser.add_argument("--discover", action="store_true", help="Scan network for holocube devices")
    args = parser.parse_args()

    if args.discover:
        found = discover_holocube()
        sys.exit(0 if found else 1)
    elif args.list:
        print("Emotes:", ", ".join(EMOTES))
        print("\nState mappings:")
        for state, emote in STATE_MAP.items():
            print(f"  {state:15s} → {emote}")
        sys.exit(0)
    elif args.status:
        sys.exit(get_status(args.ip))
    elif args.auto:
        sys.exit(auto_emote(args.ip))
    elif args.emote:
        sys.exit(set_emote(args.emote, args.static, args.ip))
    else:
        parser.print_help()
        sys.exit(1)
