"""Shared push notification client for privateapp apps.

Apps import this module to send push notifications through privateapp's
central push API. Works in both plugged-in and standalone modes.

Usage in an app's routes.py:

    from privateapp_push import send_push
    await send_push("New alert!", "Something happened", url="/app/my-app/")

The module auto-discovers the push endpoint:
  1. Same-origin /api/push/send (when plugged into privateapp)
  2. PWA_HUB_URL env var (for standalone mode pointing to privateapp)
  3. Falls back to localhost:8800
"""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
import logging

log = logging.getLogger("privateapp.push_client")


def _get_push_url() -> str:
    """Resolve the push API endpoint."""
    base = os.environ.get("PWA_HUB_URL", "http://localhost:8800")
    return f"{base.rstrip('/')}/api/push/send"


async def send_push(
    title: str,
    body: str,
    url: str | None = None,
    tag: str | None = None,
) -> bool:
    """Send a push notification through privateapp.

    Args:
        title: Notification title
        body:  Notification body text
        url:   URL to open when tapped (e.g., /app/system-monitor/)
        tag:   Optional tag for notification grouping/replacement

    Returns:
        True if sent successfully, False otherwise.
    """
    try:
        push_url = _get_push_url()
        payload = {"title": title, "body": body}
        if url:
            payload["url"] = url
        if tag:
            payload["tag"] = tag

        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            push_url,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200

    except Exception as e:
        log.warning(f"Push notification failed: {e}")
        return False


def send_push_sync(
    title: str,
    body: str,
    url: str | None = None,
    tag: str | None = None,
) -> bool:
    """Synchronous version of send_push (for non-async contexts)."""
    try:
        push_url = _get_push_url()
        payload = {"title": title, "body": body}
        if url:
            payload["url"] = url
        if tag:
            payload["tag"] = tag

        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            push_url,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200

    except Exception as e:
        log.warning(f"Push notification failed: {e}")
        return False
