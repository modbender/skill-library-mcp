"""OpenClaw messaging client for PrivateApp apps.

Apps import this module to send messages to OpenClaw chat rooms
(Matrix, Discord, Telegram, etc.) through the OpenClaw gateway API.

Usage in an app's routes.py:

    from commons.openclaw_client import send_message
    await send_message("Alert: stock NVDA dropped 5%!", room="cronjob")

The module reads the gateway URL from:
  1. OPENCLAW_GATEWAY_URL env var
  2. Default: http://localhost:18789

This is a lightweight HTTP client — no OpenClaw SDK required.
"""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
import logging

log = logging.getLogger("privateapp.openclaw_client")


def get_gateway_url() -> str:
    """Get the OpenClaw gateway URL from env var or default."""
    url = os.environ.get("OPENCLAW_GATEWAY_URL", "http://localhost:18789")
    return url.rstrip("/")


async def send_message(
    message: str,
    room: str | None = None,
    channel: str | None = None,
) -> bool:
    """Send a message to an OpenClaw chat room.

    Args:
        message: Text to send
        room:    Room name or ID (optional — uses default if not specified)
        channel: Channel type (matrix, discord, telegram, etc.)

    Returns:
        True if sent successfully.
    """
    try:
        gateway = get_gateway_url()
        url = f"{gateway}/api/v1/message"

        payload: dict = {"message": message}
        if room:
            payload["room"] = room
        if channel:
            payload["channel"] = channel

        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200

    except Exception as e:
        log.warning(f"OpenClaw message failed: {e}")
        return False


def send_message_sync(
    message: str,
    room: str | None = None,
    channel: str | None = None,
) -> bool:
    """Synchronous version."""
    try:
        gateway = get_gateway_url()
        url = f"{gateway}/api/v1/message"

        payload: dict = {"message": message}
        if room:
            payload["room"] = room
        if channel:
            payload["channel"] = channel

        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200

    except Exception as e:
        log.warning(f"OpenClaw message failed: {e}")
        return False
