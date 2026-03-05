#!/usr/bin/env python3
"""Intros CLI - OpenClaw Skill for Social Networking"""

import argparse
import json
import os
import sys
import requests
from pathlib import Path

# Configuration
API_URL = "https://api.openbreeze.ai"
# Cron notifications disabled — using @Intros_verify_bot push notifications instead
CRON_NOTIFICATIONS_ENABLED = False

# Use OPENCLAW_STATE_DIR to support multiple OpenClaw instances
# Each instance gets its own config file
STATE_DIR = os.environ.get('OPENCLAW_STATE_DIR', str(Path.home() / ".openclaw"))
# Store config outside skill folder so reinstalls don't wipe it
DATA_DIR = Path(STATE_DIR) / "data" / "intros"
CONFIG_PATH = DATA_DIR / "config.json"
# Legacy path (inside skill folder) — migrate if found
_LEGACY_CONFIG = Path(STATE_DIR) / "skills" / "intros" / "config.json"

def load_config():
    """Load saved configuration"""
    # Migrate from legacy path (inside skill folder) to data dir
    if not CONFIG_PATH.exists() and _LEGACY_CONFIG.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.move(str(_LEGACY_CONFIG), str(CONFIG_PATH))
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}

def save_config(config):
    """Save configuration with restrictive file permissions (owner-only)"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    os.chmod(CONFIG_PATH, 0o600)

def get_headers():
    """Get auth headers"""
    config = load_config()
    api_key = config.get('api_key')
    if not api_key:
        print(json.dumps({"error": "Not registered. Run 'intros.py register' first."}))
        sys.exit(1)
    return {"Authorization": f"Bearer {api_key}"}

def api_call(method, endpoint, data=None, params=None):
    """Make API call"""
    url = f"{API_URL}{endpoint}"
    headers = get_headers() if endpoint not in ['/register', '/health'] else {}
    
    try:
        if method == 'GET':
            resp = requests.get(url, headers=headers, params=params, timeout=30)
        elif method == 'POST':
            resp = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == 'DELETE':
            resp = requests.delete(url, headers=headers, timeout=30)
        
        if resp.status_code == 200:
            return resp.json()
        else:
            return {"error": resp.json().get('detail', resp.text)}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to Intros server"}
    except Exception as e:
        return {"error": str(e)}

# === Input Validation ===

def validate_bot_id(bot_id):
    """Validate bot_id is safe (alphanumeric + underscores only). Exits on invalid input."""
    clean = bot_id.lower().strip()
    if not clean or not clean.replace('_', '').isalnum() or len(clean) > 64:
        print(json.dumps({"error": "Invalid username. Use only letters, numbers, and underscores (max 64 chars)."}))
        sys.exit(1)
    return clean

# === Commands ===

def _save_identity(bot_id, telegram_id):
    """Save minimal identity to DATA_DIR for auto-recovery after reinstall."""
    identity_file = DATA_DIR / "identity.json"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(identity_file, 'w') as f:
        json.dump({"bot_id": bot_id, "telegram_id": telegram_id}, f)
    os.chmod(identity_file, 0o600)

def _load_identity():
    """Load saved identity for auto-recovery."""
    identity_file = DATA_DIR / "identity.json"
    if identity_file.exists():
        with open(identity_file) as f:
            return json.load(f)
    return {}

def _try_auto_recover():
    """Try to recover config from identity file by re-registering (idempotent).
    Returns True if recovered successfully."""
    identity = _load_identity()
    bot_id = identity.get('bot_id')
    telegram_id = identity.get('telegram_id')
    if not bot_id or not telegram_id:
        return False
    try:
        body = {"bot_id": bot_id, "telegram_id": telegram_id}
        resp = requests.post(f"{API_URL}/register", json=body, timeout=30)
        result = resp.json()
        if resp.status_code == 200 and result.get('success'):
            config = {"api_key": result['api_key'], "bot_id": bot_id, "verify_code": result['verify_code']}
            save_config(config)
            return True
    except Exception:
        pass
    return False

def cmd_register(args):
    """Register a new bot"""
    config = load_config()

    # IMPORTANT: Never re-register if config exists - prevents duplicate accounts
    if config.get('api_key') and config.get('bot_id'):
        print(json.dumps({
            "message": "Already registered",
            "bot_id": config.get('bot_id'),
            "hint": "If you need to re-register, first delete the config file manually"
        }))
        return

    # Require bot_id (username) to be provided
    if not args.bot_id:
        print(json.dumps({
            "error": "Username required. Use: register --bot-id your_username",
            "hint": "Choose a unique username (lowercase, no spaces)"
        }))
        return

    # Validate username format
    bot_id = args.bot_id.lower().strip()
    if not bot_id.replace('_', '').isalnum():
        print(json.dumps({
            "error": "Invalid username. Use only letters, numbers, and underscores.",
            "hint": "Example: sam_dev, alice123"
        }))
        return

    telegram_id = args.telegram_id or os.environ.get('TELEGRAM_USER_ID', '')

    url = f"{API_URL}/register"
    try:
        body = {"bot_id": bot_id, "telegram_id": telegram_id}
        if args.bot_username:
            body["openclaw_bot_username"] = args.bot_username.lstrip('@')
        resp = requests.post(url, json=body, timeout=30)
        result = resp.json()

        if resp.status_code == 200 and result.get('success'):
            config['api_key'] = result['api_key']
            config['bot_id'] = bot_id
            config['verify_code'] = result['verify_code']
            save_config(config)
            # Save identity for auto-recovery after future reinstalls
            _save_identity(bot_id, telegram_id)

            msg = f"Registered! Send '{result['verify_code']}' to @Intros_verify_bot on Telegram to verify."
            if result.get('recovered'):
                msg = "Credentials recovered! You're already registered and verified."
            print(json.dumps({
                "success": True,
                "message": msg,
                "verify_code": result['verify_code'],
                "bot_id": bot_id
            }))
            # Note: Cron is created after profile setup, not here
        else:
            print(json.dumps({"error": result.get('detail', 'Registration failed')}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

def cmd_verify_status(args):
    """Check verification status"""
    result = api_call('GET', '/verify-status')
    print(json.dumps(result))

def cmd_profile_create(args):
    """Create or update profile"""
    data = {
        "name": args.name,
        "interests": args.interests,
        "looking_for": args.looking_for,
        "location": args.location,
        "bio": args.bio,
        "telegram_handle": args.telegram,
        "telegram_public": args.telegram_public
    }
    # Remove None values
    data = {k: v for k, v in data.items() if v is not None}
    
    result = api_call('POST', '/profile', data)
    if result.get('success'):
        print(json.dumps({"success": True, "message": "Profile updated!"}))
    else:
        print(json.dumps(result))

def cmd_profile_me(args):
    """View my profile"""
    result = api_call('GET', '/profile')
    print(json.dumps(result))

def cmd_profile_view(args):
    """View someone's profile"""
    args.bot_id = validate_bot_id(args.bot_id)
    result = api_call('GET', f'/profile/{args.bot_id}')
    print(json.dumps(result))

def cmd_search(args):
    """Search profiles"""
    data = {}

    # Free-text query (positional args)
    if args.query:
        data['query'] = ' '.join(args.query)

    # Legacy filters (backward compat)
    if args.interests:
        data['interests'] = args.interests
    if args.looking_for:
        data['looking_for'] = args.looking_for
    if args.location:
        data['location'] = args.location

    # Pagination (3 per page for chat-based UI)
    page = max(1, args.page)
    data['limit'] = 3
    data['offset'] = (page - 1) * 3

    result = api_call('POST', '/search', data)

    if result.get('has_more'):
        result['hint'] = f"More results available. Use --page {page + 1} to see next page."

    print(json.dumps(result))

def cmd_recommend(args):
    """Get profile recommendations based on your profile"""
    page = max(1, args.page)
    limit = 3
    offset = (page - 1) * limit

    result = api_call('GET', '/recommend', params={'limit': limit, 'offset': offset})

    if result.get('has_more'):
        result['hint'] = f"More results available. Use --page {page + 1} to see next page."
    if result.get('results'):
        result['action_hint'] = "Say 'connect <bot_id>' to send a connection request."

    print(json.dumps(result))

def cmd_visitors(args):
    """View visitors"""
    result = api_call('GET', '/visitors')
    print(json.dumps(result))

def cmd_connect(args):
    """Send connection request"""
    args.bot_id = validate_bot_id(args.bot_id)
    result = api_call('POST', '/connect', {"to_bot_id": args.bot_id})
    if result.get('success'):
        print(json.dumps({"success": True, "message": f"Connection request sent to {args.bot_id}!"}))
    else:
        print(json.dumps(result))

def cmd_requests(args):
    """View pending requests"""
    result = api_call('GET', '/requests')
    print(json.dumps(result))

def cmd_accept(args):
    """Accept connection request"""
    args.bot_id = validate_bot_id(args.bot_id)
    result = api_call('POST', '/respond', {"from_bot_id": args.bot_id, "accept": True})
    if result.get('success'):
        their_profile = result.get('their_profile', {})
        telegram = their_profile.get('telegram_handle', 'Not shared')
        print(json.dumps({
            "success": True,
            "message": f"Connected with {args.bot_id}!",
            "their_telegram": telegram,
            "their_profile": their_profile
        }))
    else:
        print(json.dumps(result))

def cmd_decline(args):
    """Decline connection request"""
    args.bot_id = validate_bot_id(args.bot_id)
    result = api_call('POST', '/respond', {"from_bot_id": args.bot_id, "accept": False})
    print(json.dumps({"success": True, "message": "Request declined."}))

def cmd_connections(args):
    """View all connections"""
    result = api_call('GET', '/connections')
    print(json.dumps(result))

def cmd_limits(args):
    """Check daily limits"""
    result = api_call('GET', '/limits')
    print(json.dumps(result))

def cmd_web(args):
    """Get web profile link"""
    config = load_config()
    bot_id = config.get('bot_id')
    if bot_id:
        token = f"{bot_id}_{config.get('api_key', '')[:8]}"
        print(json.dumps({
            "public_url": f"{API_URL}/u/{bot_id}",
            "private_url": f"{API_URL}/u/{bot_id}?token={token}"
        }))
    else:
        print(json.dumps({"error": "Not registered"}))

def cmd_setup(args):
    """Setup intros skill - notifications are now automatic via @Intros_verify_bot"""
    print(json.dumps({
        "message": "Notifications are automatic! After verifying with @Intros_verify_bot, you'll receive notifications for new messages and connection requests directly on Telegram.",
        "hint": "If you're not getting notifications, send /start to @Intros_verify_bot to re-link your account."
    }))

# === Messaging Commands ===

def cmd_message_send(args):
    """Send a message to a connected user"""
    args.bot_id = validate_bot_id(args.bot_id)
    message = ' '.join(args.message) if isinstance(args.message, list) else args.message

    if len(message) > 500:
        print(json.dumps({"error": "Message too long (max 500 characters)"}))
        return

    result = api_call('POST', '/message', {"to_bot_id": args.bot_id, "content": message})
    if result.get('success'):
        print(json.dumps({"success": True, "message": f"Message sent to {args.bot_id}!"}))
    else:
        print(json.dumps(result))

def cmd_message_read(args):
    """Read messages from a specific user"""
    args.bot_id = validate_bot_id(args.bot_id)
    result = api_call('GET', f'/messages/{args.bot_id}')
    if 'error' not in result:
        messages = result.get('messages', [])
        if not messages:
            print(json.dumps({"message": f"No messages with {args.bot_id} yet."}))
            return

        # Pretty print conversation
        output = f"Conversation with {args.bot_id}:\n\n"
        for msg in messages:
            direction = "→" if msg.get('direction') == 'sent' else "←"
            time = msg.get('created_at', '')[:16]  # Truncate to date+time
            content = msg.get('content', '')
            output += f"{direction} [{time}] {content}\n"
        print(output.strip())
    else:
        print(json.dumps(result))

def cmd_message_list(args):
    """List all conversations"""
    result = api_call('GET', '/conversations')
    if 'error' not in result:
        conversations = result.get('conversations', [])
        if not conversations:
            print(json.dumps({"message": "No conversations yet."}))
            return
        print(json.dumps(result))
    else:
        print(json.dumps(result))

def cmd_check_notifications(args):
    """Check for new connection requests, accepted connections, and messages (legacy/manual fallback)"""
    if not CRON_NOTIFICATIONS_ENABLED:
        return  # Disabled — using @Intros_verify_bot push notifications instead
    config = load_config()
    if not config.get('api_key'):
        # Try auto-recovery from identity file (config lost during reinstall)
        if _try_auto_recover():
            config = load_config()
        else:
            return  # Not registered, skip silently

    # === Check for new messages ===
    msg_result = api_call('GET', '/unread-messages')
    if 'error' not in msg_result:
        messages = msg_result.get('messages', [])

        # Load previously seen message IDs
        seen_msg_file = DATA_DIR / "seen_messages.json"
        seen_msg_ids = set()
        if seen_msg_file.exists():
            with open(seen_msg_file) as f:
                seen_msg_ids = set(json.load(f))

        # Find new messages
        new_messages = []
        current_msg_ids = set()
        for msg in messages:
            msg_id = str(msg.get('id'))
            current_msg_ids.add(msg_id)
            if msg_id not in seen_msg_ids:
                new_messages.append(msg)

        # Save current IDs as seen (only current, old ones cleared when read)
        if current_msg_ids:
            with open(seen_msg_file, 'w') as f:
                json.dump(list(current_msg_ids), f)

        # Notify about new messages
        for msg in new_messages:
            name = msg.get('name', msg.get('from_bot_id', 'Someone'))
            content = msg.get('content', '')
            from_id = msg.get('from_bot_id', '')

            notification = f"📬 New message from {name}!\n\n"
            notification += f"\"{content}\"\n\n"
            notification += f"Reply with: message send {from_id} \"your reply\""
            print(notification)

    # === Check for new incoming requests ===
    result = api_call('GET', '/requests')
    if 'error' not in result:
        requests_list = result.get('requests', [])

        # Load previously seen request IDs
        seen_file = DATA_DIR / "seen_requests.json"
        seen_ids = set()
        if seen_file.exists():
            with open(seen_file) as f:
                seen_ids = set(json.load(f))

        # Find new requests
        new_requests = []
        current_ids = set()
        for req in requests_list:
            req_id = str(req.get('id'))
            current_ids.add(req_id)
            if req_id not in seen_ids:
                new_requests.append(req)

        # Save current IDs as seen
        if current_ids or seen_ids:
            with open(seen_file, 'w') as f:
                json.dump(list(current_ids), f)

        # Notify about new requests
        for req in new_requests:
            name = req.get('name', req.get('from_bot_id', 'Someone'))
            interests = req.get('interests', '')
            location = req.get('location', '')

            notification = f"🔔 New Intros connection request!\n\n"
            notification += f"From: {name}\n"
            if interests:
                notification += f"Interests: {interests}\n"
            if location:
                notification += f"Location: {location}\n"
            notification += f"\nSay 'accept {req.get('from_bot_id')}' or 'decline {req.get('from_bot_id')}'"
            print(notification)

    # === Check for accepted connections ===
    accepted_result = api_call('GET', '/accepted-connections')
    if 'error' not in accepted_result:
        accepted_list = accepted_result.get('connections', [])

        # Load previously seen accepted IDs
        seen_accepted_file = DATA_DIR / "seen_accepted.json"
        seen_accepted_ids = set()
        if seen_accepted_file.exists():
            with open(seen_accepted_file) as f:
                seen_accepted_ids = set(json.load(f))

        # Find newly accepted
        new_accepted = []
        current_accepted_ids = set()
        for conn in accepted_list:
            conn_id = str(conn.get('id'))
            current_accepted_ids.add(conn_id)
            if conn_id not in seen_accepted_ids:
                new_accepted.append(conn)

        # Save current IDs as seen
        if current_accepted_ids or seen_accepted_ids:
            with open(seen_accepted_file, 'w') as f:
                json.dump(list(current_accepted_ids), f)

        # Notify about accepted connections
        for conn in new_accepted:
            name = conn.get('name', conn.get('bot_id', 'Someone'))
            telegram = conn.get('telegram_handle', '')

            notification = f"✅ Connection accepted!\n\n"
            notification += f"{name} accepted your connection request.\n"
            if telegram:
                notification += f"Telegram: @{telegram}\n"
            notification += f"\nYou can now message each other!"
            print(notification)

    # === Daily matches nudge (once per day) ===
    from datetime import date
    nudge_file = DATA_DIR / "last_nudge.txt"
    today = date.today().isoformat()
    last_nudge = ""
    if nudge_file.exists():
        last_nudge = nudge_file.read_text().strip()

    if last_nudge != today:
        # Check remaining views
        limits_result = api_call('GET', '/limits')
        if 'error' not in limits_result:
            remaining = limits_result.get('profile_views_limit', 10) - limits_result.get('profile_views', 0)
            if remaining > 0:
                print(f"🌟 Your daily matches are ready! You have {remaining} profile views today.\n\nSay 'recommend' to discover new people.")
                nudge_file.write_text(today)

def main():
    parser = argparse.ArgumentParser(description='Intros CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Register
    reg_parser = subparsers.add_parser('register', help='Register your bot')
    reg_parser.add_argument('--bot-id', help='Bot ID')
    reg_parser.add_argument('--telegram-id', help='Telegram user ID')
    reg_parser.add_argument('--bot-username', help='Telegram bot username (for notification deep links)')
    
    # Verify status
    subparsers.add_parser('verify-status', help='Check verification status')
    
    # Profile
    profile_parser = subparsers.add_parser('profile', help='Profile commands')
    profile_sub = profile_parser.add_subparsers(dest='profile_cmd')
    
    create_parser = profile_sub.add_parser('create', help='Create/update profile')
    create_parser.add_argument('--name', required=True, help='Your name')
    create_parser.add_argument('--interests', help='Interests (comma separated)')
    create_parser.add_argument('--looking-for', help='What you are looking for')
    create_parser.add_argument('--location', help='Your location')
    create_parser.add_argument('--bio', help='Short bio')
    create_parser.add_argument('--telegram', help='Telegram handle')
    create_parser.add_argument('--telegram-public', action='store_true', help='Make Telegram public')
    
    profile_sub.add_parser('me', help='View my profile')
    
    view_parser = profile_sub.add_parser('view', help='View a profile')
    view_parser.add_argument('bot_id', help='Bot ID to view')
    
    # Search
    search_parser = subparsers.add_parser('search', help='Search profiles')
    search_parser.add_argument('query', nargs='*', help='Free-text search (e.g., "AI engineer Mumbai")')
    search_parser.add_argument('--interests', help='Filter by interests (legacy)')
    search_parser.add_argument('--looking-for', help='Filter by looking for (legacy)')
    search_parser.add_argument('--location', help='Filter by location (legacy)')
    search_parser.add_argument('--page', type=int, default=1, help='Page number (default: 1)')

    # Recommend
    recommend_parser = subparsers.add_parser('recommend', help='Get recommended profiles based on yours')
    recommend_parser.add_argument('--page', type=int, default=1, help='Page number (default: 1)')
    
    # Visitors
    subparsers.add_parser('visitors', help='See who viewed your profile')
    
    # Connect
    connect_parser = subparsers.add_parser('connect', help='Send connection request')
    connect_parser.add_argument('bot_id', help='Bot ID to connect with')
    
    # Requests
    subparsers.add_parser('requests', help='View pending requests')
    
    # Accept
    accept_parser = subparsers.add_parser('accept', help='Accept connection request')
    accept_parser.add_argument('bot_id', help='Bot ID to accept')
    
    # Decline
    decline_parser = subparsers.add_parser('decline', help='Decline connection request')
    decline_parser.add_argument('bot_id', help='Bot ID to decline')
    
    # Connections
    subparsers.add_parser('connections', help='View all connections')
    
    # Limits
    subparsers.add_parser('limits', help='Check daily limits')
    
    # Web
    subparsers.add_parser('web', help='Get web profile link')

    # Message
    msg_parser = subparsers.add_parser('message', help='Messaging commands')
    msg_sub = msg_parser.add_subparsers(dest='msg_cmd')

    msg_send_parser = msg_sub.add_parser('send', help='Send a message')
    msg_send_parser.add_argument('bot_id', help='Bot ID to message')
    msg_send_parser.add_argument('message', nargs='+', help='Message content')

    msg_read_parser = msg_sub.add_parser('read', help='Read messages from a user')
    msg_read_parser.add_argument('bot_id', help='Bot ID to read messages from')

    msg_sub.add_parser('list', help='List all conversations')

    # Check notifications (for cron job)
    subparsers.add_parser('check-notifications', help='Check for new requests (cron)')

    # Setup (register cron job)
    subparsers.add_parser('setup', help='Setup notifications (run once after install)')

    args = parser.parse_args()
    
    if args.command == 'register':
        cmd_register(args)
    elif args.command == 'verify-status':
        cmd_verify_status(args)
    elif args.command == 'profile':
        if args.profile_cmd == 'create':
            cmd_profile_create(args)
        elif args.profile_cmd == 'me':
            cmd_profile_me(args)
        elif args.profile_cmd == 'view':
            cmd_profile_view(args)
        else:
            parser.print_help()
    elif args.command == 'search':
        cmd_search(args)
    elif args.command == 'visitors':
        cmd_visitors(args)
    elif args.command == 'connect':
        cmd_connect(args)
    elif args.command == 'requests':
        cmd_requests(args)
    elif args.command == 'accept':
        cmd_accept(args)
    elif args.command == 'decline':
        cmd_decline(args)
    elif args.command == 'connections':
        cmd_connections(args)
    elif args.command == 'limits':
        cmd_limits(args)
    elif args.command == 'web':
        cmd_web(args)
    elif args.command == 'message':
        if args.msg_cmd == 'send':
            cmd_message_send(args)
        elif args.msg_cmd == 'read':
            cmd_message_read(args)
        elif args.msg_cmd == 'list':
            cmd_message_list(args)
        else:
            msg_parser.print_help()
    elif args.command == 'recommend':
        cmd_recommend(args)
    elif args.command == 'check-notifications':
        cmd_check_notifications(args)
    elif args.command == 'setup':
        cmd_setup(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
