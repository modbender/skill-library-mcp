#!/usr/bin/env python3
"""
Zulip API client wrapper for common operations.
Requires: pip install zulip
Config: ~/.config/zulip/zuliprc
"""

import os
import sys
import json
import argparse
from pathlib import Path

try:
    import zulip
except ImportError:
    print("Error: zulip module not found. Install with: pip install zulip", file=sys.stderr)
    sys.exit(1)


def get_client(config_file=None):
    """Initialize Zulip client from config file."""
    if config_file is None:
        config_file = os.path.expanduser("~/.config/zulip/zuliprc")
    
    if not os.path.exists(config_file):
        print(f"Error: Config file not found: {config_file}", file=sys.stderr)
        print("Create it with:", file=sys.stderr)
        print(f"  [api]", file=sys.stderr)
        print(f"  email=bot@example.zulipchat.com", file=sys.stderr)
        print(f"  key=YOUR_API_KEY", file=sys.stderr)
        print(f"  site=https://example.zulipchat.com", file=sys.stderr)
        sys.exit(1)
    
    return zulip.Client(config_file=config_file)


def list_streams(client, include_archived=False):
    """List all streams."""
    result = client.get_streams(include_public=True, include_subscribed=True)
    
    if result["result"] != "success":
        print(f"Error: {result.get('msg', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)
    
    streams = result["streams"]
    if not include_archived:
        streams = [s for s in streams if not s.get("is_archived", False)]
    
    return streams


def get_messages(client, stream=None, topic=None, num=20, narrow_type="stream", stream_id=None):
    """Get recent messages with optional filtering."""
    narrow = []
    
    if narrow_type == "private":
        narrow.append({"operator": "is", "operand": "private"})
    elif narrow_type == "mentioned":
        narrow.append({"operator": "is", "operand": "mentioned"})
    elif stream_id:
        # Use stream ID (more reliable)
        narrow.append({"operator": "stream", "operand": int(stream_id)})
        if topic:
            narrow.append({"operator": "topic", "operand": topic})
    elif stream:
        narrow.append({"operator": "stream", "operand": stream})
        if topic:
            narrow.append({"operator": "topic", "operand": topic})
    
    request = {
        "anchor": "newest",
        "num_before": num,
        "num_after": 0,
        "narrow": narrow
    }
    
    result = client.get_messages(request)
    
    if result["result"] != "success":
        print(f"Error: {result.get('msg', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)
    
    return result["messages"]


def send_message(client, msg_type, to, content, topic=None):
    """Send a message to stream or private."""
    message = {
        "type": msg_type,
        "content": content
    }
    
    if msg_type == "stream":
        message["to"] = to
        message["topic"] = topic or "General"
    else:  # private
        # Convert to list if single user_id
        if isinstance(to, int):
            to = [to]
        elif isinstance(to, str):
            try:
                to = [int(to)]
            except ValueError:
                pass
        message["to"] = to
    
    result = client.send_message(message)
    
    if result["result"] != "success":
        print(f"Error: {result.get('msg', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)
    
    return result


def list_users(client):
    """Get all users in the organization."""
    result = client.get_members()
    
    if result["result"] != "success":
        print(f"Error: {result.get('msg', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)
    
    return result["members"]


def main():
    parser = argparse.ArgumentParser(description="Zulip CLI client")
    parser.add_argument("--config", help="Path to zuliprc config file")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List streams
    stream_parser = subparsers.add_parser("streams", help="List all streams")
    stream_parser.add_argument("--archived", action="store_true", help="Include archived streams")
    stream_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Get messages
    msg_parser = subparsers.add_parser("messages", help="Get recent messages")
    msg_parser.add_argument("--stream", help="Filter by stream name")
    msg_parser.add_argument("--stream-id", type=int, help="Filter by stream ID (more reliable than name)")
    msg_parser.add_argument("--topic", help="Filter by topic")
    msg_parser.add_argument("--num", type=int, default=20, help="Number of messages")
    msg_parser.add_argument("--type", choices=["stream", "private", "mentioned"], 
                           default="stream", help="Message type filter")
    msg_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Send message
    send_parser = subparsers.add_parser("send", help="Send a message")
    send_parser.add_argument("--type", choices=["stream", "private"], required=True)
    send_parser.add_argument("--to", required=True, help="Stream name or user ID(s)")
    send_parser.add_argument("--topic", help="Topic (for stream messages)")
    send_parser.add_argument("--content", required=True, help="Message content")
    
    # List users
    user_parser = subparsers.add_parser("users", help="List all users")
    user_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    client = get_client(args.config)
    
    if args.command == "streams":
        streams = list_streams(client, args.archived)
        if args.json:
            print(json.dumps(streams, indent=2))
        else:
            for s in streams:
                desc = f"\n    Description: {s['description']}" if s.get('description') else ""
                print(f"[{s['stream_id']}] {s['name']}{desc}")
    
    elif args.command == "messages":
        stream_id = getattr(args, 'stream_id', None)
        messages = get_messages(client, args.stream, args.topic, args.num, args.type, stream_id)
        if args.json:
            print(json.dumps(messages, indent=2))
        else:
            for m in messages:
                sender = m.get("sender_full_name", "Unknown")
                content = m.get("content", "").replace("<p>", "").replace("</p>", "")
                print(f"{sender}: {content}")
    
    elif args.command == "send":
        result = send_message(client, args.type, args.to, args.content, args.topic)
        print(f"Message sent successfully. ID: {result['id']}")
    
    elif args.command == "users":
        users = list_users(client)
        if args.json:
            print(json.dumps(users, indent=2))
        else:
            for u in users:
                print(f"[{u['user_id']}] {u['full_name']} ({u['email']})")


if __name__ == "__main__":
    main()
