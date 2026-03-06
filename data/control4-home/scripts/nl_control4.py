#!/usr/bin/env python3
"""Natural-language wrapper for Control4 commands.

Supports lights, relays, room media source switching, mute/unmute, and room volume.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

ROOT = Path(__file__).resolve().parent
CLI = ROOT / "control4_cli.py"
MAP_FILE = ROOT / "device_map.json"


def load_map() -> Dict:
    if not MAP_FILE.exists():
        raise RuntimeError(f"Missing {MAP_FILE}. Copy device_map.example.json to device_map.json and set IDs.")
    with MAP_FILE.open() as f:
        return json.load(f)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def find_alias(text: str, aliases: Dict[str, int]) -> Optional[Tuple[str, int]]:
    for alias, item_id in aliases.items():
        if alias.lower() in text:
            return alias, int(item_id)
    return None


def run_cli(args: list[str]) -> int:
    cmd = [sys.executable, str(CLI), *args]
    return subprocess.run(cmd).returncode


def parse_light_level(text: str) -> Optional[int]:
    m = re.search(r"(\d{1,3})\s*%", text)
    if m:
        return max(0, min(100, int(m.group(1))))
    m = re.search(r"\bto\s+(\d{1,3})\b", text)
    if m:
        return max(0, min(100, int(m.group(1))))
    if re.search(r"\b(off|switch off|lights off|turn off)\b", text):
        return 0
    if re.search(r"\b(on|switch on|lights on|turn on)\b", text):
        return 100
    return None


def parse_volume(text: str) -> Optional[int]:
    m = re.search(r"(?:volume|vol)\s*(?:to)?\s*(\d{1,3})", text)
    if m:
        return max(0, min(100, int(m.group(1))))
    return None


def handle(text: str, mapping: Dict) -> int:
    text = norm(text)
    lights = mapping.get("lights", {})
    relays = mapping.get("relays", {})
    rooms = mapping.get("rooms", {})
    media = mapping.get("media_sources", {})

    if re.search(r"\b(list|show)\b", text):
        if "relay" in text:
            print(json.dumps(relays, indent=2))
            return 0
        if "light" in text:
            print(json.dumps(lights, indent=2))
            return 0
        if "room" in text:
            print(json.dumps(rooms, indent=2))
            return 0
        if "source" in text or "apple tv" in text:
            print(json.dumps(media, indent=2))
            return 0
        print(json.dumps(mapping, indent=2))
        return 0

    # Media / room controls
    if any(k in text for k in ["watch", "source", "apple tv", "mute", "unmute", "volume", "room off"]):
        room_match = find_alias(text, rooms)
        if room_match:
            _, room_id = room_match

            if re.search(r"\bunmute\b", text):
                return run_cli(["room-mute", "--room-id", str(room_id), "--state", "off"])
            if re.search(r"\bmute\b", text):
                return run_cli(["room-mute", "--room-id", str(room_id), "--state", "on"])
            if re.search(r"\broom off\b|\bturn off.*room\b", text):
                return run_cli([
                    "call", "--entity", "room", "--id", str(room_id), "--method", "setRoomOff"
                ])

            v = parse_volume(text)
            if v is not None:
                return run_cli(["room-volume", "--room-id", str(room_id), "--level", str(v)])
            if re.search(r"\bvolume up\b", text):
                return run_cli(["room-volume", "--room-id", str(room_id), "--delta", "up"])
            if re.search(r"\bvolume down\b", text):
                return run_cli(["room-volume", "--room-id", str(room_id), "--delta", "down"])

            source_match = find_alias(text, media)
            if source_match:
                _, source_id = source_match
                return run_cli(["room-set-source", "--room-id", str(room_id), "--source-id", str(source_id)])

    if "relay" in text:
        match = find_alias(text, relays)
        if not match:
            raise RuntimeError("No relay alias matched. Update device_map.json relays.")
        _, item_id = match
        if "toggle" in text:
            return run_cli(["relay-toggle", "--id", str(item_id)])
        if re.search(r"\b(open|on)\b", text):
            return run_cli(["relay-set", "--id", str(item_id), "--state", "open"])
        if re.search(r"\b(close|off)\b", text):
            return run_cli(["relay-set", "--id", str(item_id), "--state", "close"])
        raise RuntimeError("Relay command unclear. Use toggle/on/off.")

    if "light" in text or "lights" in text:
        match = find_alias(text, lights)
        if not match:
            raise RuntimeError("No light alias matched. Update device_map.json lights.")
        _, item_id = match
        level = parse_light_level(text)
        if level is None:
            raise RuntimeError("Could not infer light level. Include percent, on, or off.")
        return run_cli(["light-set", "--id", str(item_id), "--level", str(level)])

    raise RuntimeError("Unsupported request. Try lights/relays/media/room commands.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Natural language Control4 wrapper")
    parser.add_argument("text", nargs="+", help="Natural language command")
    args = parser.parse_args()

    try:
        return handle(" ".join(args.text), load_map())
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
