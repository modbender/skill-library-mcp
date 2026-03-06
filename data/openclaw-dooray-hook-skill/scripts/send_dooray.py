#!/usr/bin/env python3
"""
Send a message to a Dooray chat room via incoming webhook.
Uses only Python standard library (no external dependencies).

Usage:
    python send_dooray.py "RoomName" "Message text"
    python send_dooray.py --list

Examples:
    python send_dooray.py "Dev Team" "Deployment complete ✅"
    python send_dooray.py --list  # List configured rooms
"""

import json
import os
import sys
import ssl
import urllib.request
import urllib.error
from pathlib import Path


def load_config():
    """Load OpenClaw config from ~/.openclaw/openclaw.json"""
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    
    if not config_path.exists():
        print(f"Error: OpenClaw config not found at {config_path}", file=sys.stderr)
        print("Ensure OpenClaw is configured and the gateway has written the config.", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse OpenClaw config: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to read OpenClaw config: {e}", file=sys.stderr)
        sys.exit(1)


def get_dooray_config(config):
    """Extract Dooray skill config from OpenClaw config"""
    try:
        # Strict matching: Only look for 'dooray-hook' as defined in SKILL.md
        entries = config.get("skills", {}).get("entries", {})
        dooray_config = entries.get("dooray-hook", {}).get("config", {})
        
        # Return empty dict if not found, to be handled by caller
        return dooray_config
    except (KeyError, AttributeError):
        print("Error: Dooray skill config structure is invalid", file=sys.stderr)
        sys.exit(1)


def list_rooms(dooray_config):
    """List all configured Dooray rooms"""
    rooms = dooray_config.get("rooms", {})
    
    if not rooms:
        print("No Dooray rooms configured or 'dooray-hook' entry is missing.")
        print("\nPlease add the configuration to ~/.openclaw/openclaw.json:")
        print('  "skills": {')
        print('    "entries": {')
        print('      "dooray-hook": {')
        print('        "config": {')
        print('          "verify_ssl": true,')
        print('          "rooms": { "RoomName": "https://hook.dooray.com/..." }')
        print('        }')
        print('      }')
        print('    }')
        print('  }')
        return
    
    print("Configured Dooray rooms:")
    for room_name in sorted(rooms.keys()):
        webhook_url = rooms[room_name]
        # Mask webhook token for security
        masked_url = webhook_url[:40] + "..." if len(webhook_url) > 40 else webhook_url
        print(f"  - {room_name}: {masked_url}")


def send_message(room_name, message_text, dooray_config):
    """Send a message to a Dooray chat room"""
    rooms = dooray_config.get("rooms", {})
    
    if not rooms:
         print(f"Error: No rooms configured under 'dooray-hook'.", file=sys.stderr)
         sys.exit(1)

    if room_name not in rooms:
        print(f"Error: Room '{room_name}' not found in 'dooray-hook' config", file=sys.stderr)
        print(f"\nAvailable rooms: {', '.join(sorted(rooms.keys()))}", file=sys.stderr)
        sys.exit(1)
    
    webhook_url = rooms[room_name]
    bot_name = dooray_config.get("botName", "OpenClaw")
    bot_icon = dooray_config.get("botIconImage", "https://static.dooray.com/static_images/dooray-bot.png")
    
    # Check for SSL verification override (Default: True)
    verify_ssl = dooray_config.get("verify_ssl", True)

    # Prepare payload
    payload = {
        "botName": bot_name,
        "botIconImage": bot_icon,
        "text": message_text
    }
    
    payload_json = json.dumps(payload).encode('utf-8')
    
    # Send POST request
    try:
        req = urllib.request.Request(
            webhook_url,
            data=payload_json,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'OpenClaw-Dooray-Skill/1.0'
            },
            method='POST'
        )
        
        # [SECURITY] Conditional SSL Context
        if verify_ssl:
            # Secure default: Validates SSL certificates
            ssl_context = ssl.create_default_context()
        else:
            # Insecure opt-in: Ignores certificate errors (for proxies/self-signed certs)
            # This handles the [SSL: CERTIFICATE_VERIFY_FAILED] error if config allows it.
            ssl_context = ssl._create_unverified_context()

        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
            status_code = response.getcode()
            response_body = response.read().decode('utf-8')
            
            if status_code == 200:
                print(f"✅ Message sent to Dooray room '{room_name}'")
                return True
            else:
                print(f"⚠️  Unexpected response: {status_code}", file=sys.stderr)
                print(f"Response: {response_body}", file=sys.stderr)
                return False
    
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        try:
            error_body = e.read().decode('utf-8')
            print(f"Response: {error_body}", file=sys.stderr)
        except:
            pass
        return False
    
    except urllib.error.URLError as e:
        print(f"❌ Network error: {e.reason}", file=sys.stderr)
        if "CERTIFICATE_VERIFY_FAILED" in str(e.reason):
             print("\n💡 Hint: Try setting 'verify_ssl': false in your config if using a proxy or self-signed cert.", file=sys.stderr)
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    
    # Load OpenClaw config
    config = load_config()
    dooray_config = get_dooray_config(config)
    
    # Handle --list flag
    if sys.argv[1] == "--list":
        list_rooms(dooray_config)
        sys.exit(0)
    
    # Send message
    if len(sys.argv) < 3:
        print("Error: Missing arguments", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    
    room_name = sys.argv[1]
    message_text = sys.argv[2]
    
    success = send_message(room_name, message_text, dooray_config)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()