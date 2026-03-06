#!/usr/bin/env python3
"""
Main entry point: generate Discord digest for all configured servers.
Usage: run_digest.py [hours] [--server SERVER_ID]
"""

import json
import os
import sys
import time

# Add scripts dir to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from discord_api import validate_token, get_messages_since
from digest_formatter import format_digest
from config_manager import load_config


def run(hours: int = 24, server_filter: str = None) -> dict:
    """
    Run digest generation.
    Returns: {"ok": bool, "digests": [{"server": str, "text": str}], "error": str}
    """
    config = load_config()
    token = config.get("discord_token", "")

    if not token:
        return {"ok": False, "error": "no_token", "message": "Discord token not configured. Use config_manager.py set-token <token>"}

    # Validate token
    validation = validate_token(token)
    if not validation["valid"]:
        return {"ok": False, "error": "invalid_token", "message": f"Discord token is invalid or expired: {validation.get('error')}"}

    servers = config.get("servers", [])
    if not servers:
        return {"ok": False, "error": "no_servers", "message": "No servers configured. Use the setup flow to add servers."}

    if server_filter:
        servers = [s for s in servers if s["id"] == server_filter]
        if not servers:
            return {"ok": False, "error": "server_not_found", "message": f"Server {server_filter} not in config"}

    digests = []

    for server in servers:
        server_name = server["name"]
        server_id = server["id"]
        channels = server.get("channels", [])

        if not channels:
            continue

        channels_data = []
        for ch in channels:
            ch_id = ch["id"]
            ch_name = ch["name"]

            try:
                messages = get_messages_since(token, ch_id, hours)
                if messages:
                    channels_data.append({
                        "channel_name": ch_name,
                        "channel_id": ch_id,
                        "messages": messages
                    })
            except Exception as e:
                print(f"Error reading {ch_name}: {e}", file=sys.stderr)
                continue

        if channels_data:
            digest_text = format_digest(server_name, server_id, channels_data)
            digests.append({
                "server": server_name,
                "server_id": server_id,
                "text": digest_text,
                "channels_read": len(channels_data),
                "total_messages": sum(len(cd["messages"]) for cd in channels_data)
            })

    return {"ok": True, "digests": digests, "username": validation.get("username")}


if __name__ == "__main__":
    hours = 24
    server_filter = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--server" and i + 1 < len(args):
            server_filter = args[i + 1]
            i += 2
        elif args[i] == "--hours" and i + 1 < len(args):
            hours = int(args[i + 1])
            i += 2
        else:
            try:
                hours = int(args[i])
            except ValueError:
                pass
            i += 1

    result = run(hours, server_filter)

    if not result["ok"]:
        print(f"❌ Error: {result['message']}", file=sys.stderr)
        sys.exit(1)

    for d in result["digests"]:
        print(d["text"])
        print(f"\n📊 {d['server']}: {d['total_messages']} messages from {d['channels_read']} channels")
        print("---")
