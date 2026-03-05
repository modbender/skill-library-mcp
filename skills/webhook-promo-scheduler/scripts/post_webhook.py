#!/usr/bin/env python3
"""Discord webhook posting helper (stdlib only).

Safety: this module never prints the webhook URL; callers should also redact it.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Optional, Tuple


def redact_webhook_url(text: str) -> str:
    if not text:
        return text
    lowered = text.lower()
    if "discord.com/api/webhooks" in lowered or "discordapp.com/api/webhooks" in lowered:
        return "<redacted>"
    return text


def post_discord_webhook(
    webhook_url: str,
    message: str,
    *,
    username: Optional[str] = None,
    timeout_seconds: int = 15,
) -> Tuple[bool, str]:
    """Return (ok, info). `info` never contains the webhook URL."""

    payload = {"content": message}
    if username:
        payload["username"] = username

    data = json.dumps(payload, ensure_ascii=True).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "openclaw-webhook-promo-scheduler/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            code = getattr(resp, "status", None) or resp.getcode()
            if 200 <= int(code) < 300:
                return True, f"HTTP {int(code)}"
            return False, f"HTTP {int(code)}"
    except urllib.error.HTTPError as e:
        code = getattr(e, "code", None)
        return False, f"HTTPError {int(code) if code is not None else 'unknown'}"
    except urllib.error.URLError:
        return False, "URLError"
    except Exception as e:
        return False, f"Error {type(e).__name__}"
