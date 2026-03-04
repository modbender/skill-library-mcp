#!/usr/bin/env python3
"""Manage discord-digest configuration: token, servers, channels."""

import json
import os
import sys

CONFIG_DIR = os.environ.get("DISCORD_DIGEST_CONFIG_DIR", os.path.expanduser("~/.openclaw/workspace/config"))
CONFIG_FILE = os.path.join(CONFIG_DIR, "discord-digest.json")


def load_config() -> dict:
    """Load existing config or return empty template."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"discord_token": "", "servers": [], "digest_period_hours": 24}


def save_config(config: dict):
    """Save config to file."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"✅ Config saved to {CONFIG_FILE}")


def set_token(token: str):
    """Set Discord user token."""
    config = load_config()
    config["discord_token"] = token
    save_config(config)


def get_token() -> str:
    """Get Discord user token from config."""
    config = load_config()
    return config.get("discord_token", "")


def add_server(server_id: str, server_name: str, channels: list):
    """Add or update a server in config."""
    config = load_config()
    # Remove existing entry for this server
    config["servers"] = [s for s in config["servers"] if s["id"] != server_id]
    config["servers"].append({
        "id": server_id,
        "name": server_name,
        "channels": channels
    })
    save_config(config)


def remove_server(server_id: str):
    """Remove a server from config."""
    config = load_config()
    config["servers"] = [s for s in config["servers"] if s["id"] != server_id]
    save_config(config)


def list_servers() -> list:
    """List configured servers."""
    config = load_config()
    return config.get("servers", [])


def get_config() -> dict:
    """Get full config."""
    return load_config()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: config_manager.py <action> [args...]")
        print("Actions: get, set-token <token>, add-server <json>, remove-server <id>, list-servers")
        sys.exit(1)

    action = sys.argv[1]

    if action == "get":
        config = get_config()
        # Mask token for display
        if config.get("discord_token"):
            config["discord_token"] = config["discord_token"][:20] + "..."
        print(json.dumps(config, indent=2, ensure_ascii=False))
    elif action == "set-token" and len(sys.argv) > 2:
        set_token(sys.argv[2])
    elif action == "add-server" and len(sys.argv) > 2:
        data = json.loads(sys.argv[2])
        add_server(data["id"], data["name"], data.get("channels", []))
    elif action == "remove-server" and len(sys.argv) > 2:
        remove_server(sys.argv[2])
    elif action == "list-servers":
        servers = list_servers()
        for s in servers:
            ch_count = len(s.get("channels", []))
            print(f"  {s['name']} (ID: {s['id']}) — {ch_count} channels")
    else:
        print("Unknown action")
        sys.exit(1)
