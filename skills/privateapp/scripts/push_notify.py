"""PWA Web Push notification support for privateapp.

Manages push subscriptions and sends VAPID notifications.
"""
from __future__ import annotations

import json
import logging
import os
import sqlite3
from pathlib import Path

log = logging.getLogger("privateapp.push")

# Paths are resolved at runtime via config; these are defaults overridable by set_config()
_DATA_DIR: Path | None = None
_VAPID_EMAIL: str = "admin@localhost"
_VAPID_PRIVATE_KEY_PATH: Path | None = None
_SUBSCRIPTIONS_DB_PATH: Path | None = None


def set_config(data_dir: str, vapid_email: str) -> None:
    global _DATA_DIR, _VAPID_EMAIL, _VAPID_PRIVATE_KEY_PATH, _SUBSCRIPTIONS_DB_PATH
    _DATA_DIR = Path(data_dir).expanduser()
    _VAPID_EMAIL = vapid_email
    _VAPID_PRIVATE_KEY_PATH = _DATA_DIR / "vapid_private.pem"
    _SUBSCRIPTIONS_DB_PATH = _DATA_DIR / "privateapp.db"


def get_vapid_private_key_path() -> Path | None:
    return _VAPID_PRIVATE_KEY_PATH


def get_subscriptions_db_path() -> Path | None:
    return _SUBSCRIPTIONS_DB_PATH


def _db() -> sqlite3.Connection:
    if _SUBSCRIPTIONS_DB_PATH is None:
        raise RuntimeError("push_notify not configured — call set_config() first")
    conn = sqlite3.connect(str(_SUBSCRIPTIONS_DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        endpoint TEXT UNIQUE NOT NULL,
        keys_json TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        last_used_at TEXT
    )""")
    conn.commit()
    return conn


def save_subscription(subscription: dict) -> bool:
    """Save or update a push subscription."""
    try:
        conn = _db()
        conn.execute(
            """INSERT INTO subscriptions (endpoint, keys_json)
               VALUES (?, ?)
               ON CONFLICT(endpoint) DO UPDATE SET keys_json=excluded.keys_json,
               last_used_at=datetime('now')""",
            (subscription["endpoint"], json.dumps(subscription.get("keys", {})))
        )
        conn.commit()
        conn.close()
        log.info(f"Push subscription saved: {subscription['endpoint'][:60]}...")
        return True
    except Exception as e:
        log.error(f"Failed to save subscription: {e}")
        return False


def remove_subscription(endpoint: str) -> bool:
    """Remove a push subscription by endpoint."""
    try:
        conn = _db()
        conn.execute("DELETE FROM subscriptions WHERE endpoint=?", (endpoint,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        log.error(f"Failed to remove subscription: {e}")
        return False


def get_all_subscriptions() -> list[dict]:
    """Return all active push subscriptions."""
    try:
        conn = _db()
        rows = conn.execute("SELECT endpoint, keys_json FROM subscriptions").fetchall()
        conn.close()
        return [
            {"endpoint": r["endpoint"], "keys": json.loads(r["keys_json"])}
            for r in rows
        ]
    except Exception as e:
        log.error(f"Failed to get subscriptions: {e}")
        return []


def send_push_notification(
    title: str,
    body: str,
    url: str = "/",
    tag: str | None = None,
    icon: str = "/static/icon-192.png",
) -> int:
    """Send push notification to all subscribers. Returns count of successful sends."""
    if _VAPID_PRIVATE_KEY_PATH is None or not _VAPID_PRIVATE_KEY_PATH.exists():
        log.warning("VAPID private key not found — skipping push")
        return 0

    try:
        from pywebpush import webpush, WebPushException
    except ImportError:
        log.error("pywebpush not installed — run install.py")
        return 0

    payload = json.dumps({
        "title": title,
        "body": body,
        "url": url,
        "tag": tag or "privateapp",
        "icon": icon,
    })

    claims = {"sub": f"mailto:{_VAPID_EMAIL}"}
    log.info(f"VAPID email: {_VAPID_EMAIL}, key: {_VAPID_PRIVATE_KEY_PATH}")
    subscriptions = get_all_subscriptions()
    if not subscriptions:
        log.info("No push subscriptions — skipping")
        return 0

    sent = 0
    stale = []
    for sub in subscriptions:
        try:
            webpush(
                subscription_info=sub,
                data=payload,
                vapid_private_key=str(_VAPID_PRIVATE_KEY_PATH),
                vapid_claims=claims,
            )
            sent += 1
        except WebPushException as e:
            if e.response and e.response.status_code in (404, 410):
                stale.append(sub["endpoint"])
                log.info(f"Removing stale subscription: {sub['endpoint'][:60]}")
            else:
                log.error(f"Push failed: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    log.error(f"  Response: {e.response.status_code} {e.response.text[:200]}")
        except Exception as e:
            log.error(f"Push error: {e}")

    for endpoint in stale:
        remove_subscription(endpoint)

    log.info(f"Push sent to {sent}/{len(subscriptions)} subscribers")
    return sent
