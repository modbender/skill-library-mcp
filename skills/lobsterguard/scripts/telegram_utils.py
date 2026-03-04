#!/usr/bin/env python3
"""
Shared Telegram utilities for LobsterGuard.
Auto-detects bot token and chat_id from OpenClaw configuration.
"""

import json
import os
import urllib.request
import urllib.parse
from pathlib import Path


def get_telegram_config():
    """Read Telegram bot token and chat_id from OpenClaw config files."""
    oc_home = Path(os.environ.get("OPENCLAW_HOME", os.path.expanduser("~/.openclaw")))

    bot_token = None
    chat_id = ""

    # Bot token: from openclaw.json -> telegram.botToken
    try:
        with open(oc_home / "openclaw.json") as f:
            config = json.load(f)

        def find_key(d, key):
            if isinstance(d, dict):
                if key in d:
                    return d[key]
                for v in d.values():
                    r = find_key(v, key)
                    if r:
                        return r
            return None

        bot_token = find_key(config, "botToken") or ""
    except Exception:
        pass

    # Chat ID: from credentials/telegram-default-allowFrom.json
    try:
        with open(oc_home / "credentials" / "telegram-default-allowFrom.json") as f:
            data = json.load(f)
        allow = data.get("allowFrom", [])
        if allow:
            chat_id = str(allow[0])
    except Exception:
        pass

    return bot_token, chat_id


def send_telegram(text, bot_token=None, chat_id=None):
    """Send a message via Telegram Bot API."""
    if not bot_token or not chat_id:
        bot_token, chat_id = get_telegram_config()
    if not bot_token or not chat_id:
        return False
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = urllib.parse.urlencode({
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }).encode()
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception:
        return False
