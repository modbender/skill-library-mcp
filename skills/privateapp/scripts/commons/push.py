"""VAPID Web Push notification helpers for privateapp.

A clean class-based wrapper around push_notify.py functionality.

Usage:
    from scripts.commons.push import PushManager

    push = PushManager(data_dir="~/.local/share/privateapp", vapid_email="admin@localhost")
    await push.subscribe(subscription_dict)
    await push.send("Alert", "Something happened", url="/app/system-monitor")
"""
from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path

log = logging.getLogger("privateapp.push")


class PushManager:
    """Manages VAPID push subscriptions and sends Web Push notifications."""

    def __init__(self, data_dir: str, vapid_email: str) -> None:
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vapid_email = vapid_email
        self.private_key_path = self.data_dir / "vapid_private.pem"
        self.public_key_path = self.data_dir / "vapid_public.txt"
        self._db_path = self.data_dir / "privateapp.db"

    # ── Public key ─────────────────────────────────────────────────────

    def get_public_key(self) -> str | None:
        """Return the VAPID public key (base64url), or None if not generated."""
        if self.public_key_path.exists():
            return self.public_key_path.read_text().strip()
        return None

    # ── Subscriptions ───────────────────────────────────────────────────

    def _db(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path))
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

    def subscribe(self, subscription: dict) -> bool:
        """Save or update a push subscription. Returns True on success."""
        try:
            conn = self._db()
            conn.execute(
                """INSERT INTO subscriptions (endpoint, keys_json)
                   VALUES (?, ?)
                   ON CONFLICT(endpoint) DO UPDATE SET
                   keys_json=excluded.keys_json,
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

    def unsubscribe(self, endpoint: str) -> bool:
        """Remove a push subscription by endpoint."""
        try:
            conn = self._db()
            conn.execute("DELETE FROM subscriptions WHERE endpoint=?", (endpoint,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            log.error(f"Failed to remove subscription: {e}")
            return False

    def get_all_subscriptions(self) -> list[dict]:
        """Return all active push subscriptions."""
        try:
            conn = self._db()
            rows = conn.execute("SELECT endpoint, keys_json FROM subscriptions").fetchall()
            conn.close()
            return [
                {"endpoint": r["endpoint"], "keys": json.loads(r["keys_json"])}
                for r in rows
            ]
        except Exception as e:
            log.error(f"Failed to get subscriptions: {e}")
            return []

    # ── Send ────────────────────────────────────────────────────────────

    def send(self, title: str, body: str, url: str = "/", tag: str | None = None) -> int:
        """Send push notification to all subscribers. Returns count of successful sends."""
        if not self.private_key_path.exists():
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
            "icon": "/icon-192.png",
        })

        claims = {"sub": f"mailto:{self.vapid_email}"}
        subscriptions = self.get_all_subscriptions()
        if not subscriptions:
            log.info("No push subscriptions — nothing to send")
            return 0

        sent = 0
        stale = []
        for sub in subscriptions:
            try:
                webpush(
                    subscription_info=sub,
                    data=payload,
                    vapid_private_key=str(self.private_key_path),
                    vapid_claims=claims,
                )
                sent += 1
            except WebPushException as e:
                if e.response and e.response.status_code in (404, 410):
                    stale.append(sub["endpoint"])
                    log.info(f"Removing stale subscription: {sub['endpoint'][:60]}")
                else:
                    log.error(f"Push failed: {e}")
            except Exception as e:
                log.error(f"Push error: {e}")

        for endpoint in stale:
            self.unsubscribe(endpoint)

        log.info(f"Push sent to {sent}/{len(subscriptions)} subscribers")
        return sent
