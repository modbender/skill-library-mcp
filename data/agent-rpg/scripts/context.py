# RPG Context Manager

import json
import os
import argparse
from pathlib import Path

MEMORY_ROOT = Path("memory/rpg")

def get_campaign_path(campaign):
    return MEMORY_ROOT / campaign

def load_json(path):
    if not path.exists():
        return {}
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_state(campaign):
    path = get_campaign_path(campaign)
    world = load_json(path / "world.json")
    print(json.dumps(world, indent=2, ensure_ascii=False))

def set_flag(campaign, key, value):
    path = get_campaign_path(campaign) / "world.json"
    world = load_json(path)
    
    # Handle boolean strings
    if value.lower() == 'true': value = True
    elif value.lower() == 'false': value = False
    
    world.setdefault("flags", {})[key] = value
    save_json(path, world)
    print(f"Set flag '{key}' to {value}")

def main():
    parser = argparse.ArgumentParser(description="RPG Context Manager")
    subparsers = parser.add_subparsers(dest="command")

    get_parser = subparsers.add_parser("get_state")
    get_parser.add_argument("--campaign", required=True)

    flag_parser = subparsers.add_parser("set_flag")
    flag_parser.add_argument("--campaign", required=True)
    flag_parser.add_argument("--key", required=True)
    flag_parser.add_argument("--value", required=True)

    args = parser.parse_args()

    if args.command == "get_state":
        get_state(args.campaign)
    elif args.command == "set_flag":
        set_flag(args.campaign, args.key, args.value)

if __name__ == "__main__":
    main()
