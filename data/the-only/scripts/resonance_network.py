#!/usr/bin/env python3
"""
The ONLY — Resonance Network P2P Router

For a decentralized Clawhub skill without a central backend, OpenClaw
uses its Channel Routing (WhatsApp, Telegram, Feishu, iMsg) to DM other
agents directly. This script prepares Echo packets for delivery via
OpenClaw's native messaging capabilities.
"""
import json
import os
import argparse

LOCAL_SOCIAL_CACHE = os.path.expanduser("~/memory/the_only_social_cache.json")

def load_cache():
    if os.path.exists(LOCAL_SOCIAL_CACHE):
        with open(LOCAL_SOCIAL_CACHE, 'r') as f:
            return json.load(f)
    return {"my_handle": "", "sent_echoes": []}

def save_cache(data):
    os.makedirs(os.path.dirname(LOCAL_SOCIAL_CACHE), exist_ok=True)
    with open(LOCAL_SOCIAL_CACHE, 'w') as f:
        json.dump(data, f, indent=2)

def publish_echo(user_name, content, tags, my_handle):
    """
    Prepares an Echo packet for P2P delivery.
    The Agent is responsible for using OpenClaw channel actions
    (imsg, telegram, whatsapp) to actually send the packet.
    """
    cache = load_cache()
    if my_handle:
        cache["my_handle"] = my_handle
    
    packet = {
        "type": "only_echo",
        "author": user_name,
        "content": content,
        "tags": [t.strip() for t in tags.split(",")] if tags else [],
        "reply_to": cache.get("my_handle", "")
    }
    
    # Log it locally
    cache["sent_echoes"].append(packet)
    save_cache(cache)
    
    # Output the packet as JSON for the Agent to consume
    print(json.dumps(packet, ensure_ascii=False, indent=2))

def main():
    parser = argparse.ArgumentParser(description="The ONLY — Resonance Network P2P Router")
    parser.add_argument("--action", choices=["publish_echo"], required=True)
    parser.add_argument("--user_name", type=str, default="Anonymous")
    parser.add_argument("--content", type=str, help="Echo content to publish")
    parser.add_argument("--tags", type=str, help="Comma-separated tags")
    parser.add_argument("--my_handle", type=str, help="Telegram/WhatsApp handle for replies")
    
    args = parser.parse_args()
    
    if args.action == "publish_echo":
        publish_echo(args.user_name, args.content, args.tags, args.my_handle)

if __name__ == "__main__":
    main()
