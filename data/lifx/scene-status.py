#!/storage/venv/bin/python3
"""LIFX Scene Status Detector — checks if scenes are currently active."""

import json
import os
import sys
from typing import Any

import requests

LIFX_API = "https://api.lifx.com/v1"

# Tolerances
BRIGHTNESS_TOL = 0.05
SATURATION_TOL = 0.10
HUE_TOL = 10.0
KELVIN_TOL = 200
MATCH_THRESHOLD = 0.70


def api(token: str, path: str) -> Any:
    r = requests.get(f"{LIFX_API}{path}", headers={"Authorization": f"Bearer {token}"}, timeout=15)
    r.raise_for_status()
    return r.json()


def hue_match(a: float, b: float) -> bool:
    diff = abs(a - b) % 360
    return min(diff, 360 - diff) <= HUE_TOL


def color_match(light_color: dict, scene_color: dict, light_power: str, scene_power: str | None) -> bool:
    # Power check: if scene specifies power off, light must be off
    if scene_power is not None:
        if scene_power == "off" and light_power != "off":
            return False
        if scene_power == "on" and light_power != "on":
            return False

    # If light is off and scene wants it off, that's a match
    if scene_power == "off" and light_power == "off":
        return True

    if not hue_match(light_color.get("hue", 0), scene_color.get("hue", 0)):
        return False
    if abs(light_color.get("saturation", 0) - scene_color.get("saturation", 0)) > SATURATION_TOL:
        return False
    if abs(light_color.get("brightness", 0) - scene_color.get("brightness", 0)) > BRIGHTNESS_TOL:
        return False
    if abs(light_color.get("kelvin", 3500) - scene_color.get("kelvin", 3500)) > KELVIN_TOL:
        return False
    return True


def check_scene(token: str, scene: dict, lights_by_id: dict) -> dict:
    states = scene.get("states", [])
    if not states:
        return {"uuid": scene["uuid"], "name": scene.get("name", ""), "active": False, "matched": 0, "total": 0}

    matched = 0
    total = 0
    details = []

    for state in states:
        selector = state.get("selector", "")
        # Extract light id from selector (format: "id:d073d5xxxxxx")
        light_id = selector.replace("id:", "") if selector.startswith("id:") else selector

        light = lights_by_id.get(light_id)
        if light is None:
            # Try matching by label
            for l in lights_by_id.values():
                if l.get("label", "").lower() == light_id.lower():
                    light = l
                    break

        if light is None:
            continue

        total += 1
        scene_color = {
            "hue": state.get("hue", state.get("color", {}).get("hue", 0) if isinstance(state.get("color"), dict) else 0),
            "saturation": state.get("saturation", state.get("color", {}).get("saturation", 0) if isinstance(state.get("color"), dict) else 0),
            "brightness": state.get("brightness", state.get("color", {}).get("brightness", 0) if isinstance(state.get("color"), dict) else 0),
            "kelvin": state.get("kelvin", state.get("color", {}).get("kelvin", 3500) if isinstance(state.get("color"), dict) else 3500),
        }
        # Parse color string if present (e.g. "hue:120 saturation:1.0 brightness:1.0 kelvin:3500")
        color_str = state.get("color")
        if isinstance(color_str, str):
            for part in color_str.split():
                if ":" in part:
                    k, v = part.split(":", 1)
                    try:
                        scene_color[k] = float(v)
                    except ValueError:
                        pass

        light_color = light.get("color", {})
        scene_power = state.get("power")
        light_power = light.get("power", "on")

        is_match = color_match(light_color, scene_color, light_power, scene_power)
        if is_match:
            matched += 1
        details.append({
            "selector": selector,
            "label": light.get("label", ""),
            "match": is_match,
        })

    active = total > 0 and (matched / total) >= MATCH_THRESHOLD

    return {
        "uuid": scene["uuid"],
        "name": scene.get("name", ""),
        "active": active,
        "matched": matched,
        "total": total,
        "ratio": round(matched / total, 2) if total > 0 else 0,
        "details": details,
    }


def get_lights_by_id(token: str) -> dict:
    lights = api(token, "/lights/all")
    by_id = {}
    for l in lights:
        lid = l.get("id", "")
        by_id[lid] = l
    return by_id


def cmd_check(token: str, scene_uuid: str):
    scenes = api(token, "/scenes")
    lights_by_id = get_lights_by_id(token)

    target = None
    for s in scenes:
        if s["uuid"] == scene_uuid:
            target = s
            break

    if target is None:
        print(json.dumps({"error": f"Scene {scene_uuid} not found"}))
        sys.exit(1)

    result = check_scene(token, target, lights_by_id)
    print(json.dumps(result, indent=2))


def cmd_all(token: str):
    scenes = api(token, "/scenes")
    lights_by_id = get_lights_by_id(token)

    results = []
    for s in scenes:
        r = check_scene(token, s, lights_by_id)
        results.append(r)

    active = [r for r in results if r["active"]]
    output = {
        "total_scenes": len(results),
        "active_count": len(active),
        "active": active,
        "all": results,
    }
    print(json.dumps(output, indent=2))


def main():
    token = os.environ.get("LIFX_TOKEN")
    if not token:
        # Try loading from .lifx-token in script directory
        token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lifx-token")
        if os.path.exists(token_file):
            with open(token_file) as f:
                token = f.read().strip()
    if not token:
        print(json.dumps({"error": "LIFX_TOKEN env var required"}))
        sys.exit(1)

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <check <scene_uuid> | all>", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "check":
        if len(sys.argv) < 3:
            print(f"Usage: {sys.argv[0]} check <scene_uuid>", file=sys.stderr)
            sys.exit(1)
        cmd_check(token, sys.argv[2])
    elif cmd == "all":
        cmd_all(token)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
