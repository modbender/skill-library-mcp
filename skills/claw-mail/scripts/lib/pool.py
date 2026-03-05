"""Connection pool for IMAP and SMTP clients.

Caches and reuses connections across multiple operations within a single
session (e.g. a heartbeat cycle), reducing the overhead of repeated
connect/disconnect calls.

Usage::

    pool = ConnectionPool(account_manager)
    client = pool.get_imap("work")   # connects on first call
    client = pool.get_imap("work")   # returns cached connection
    pool.close_all()                 # disconnect everything
"""

from __future__ import annotations

import logging
import time
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .account_manager import AccountManager
    from .imap_client import IMAPClient
    from .smtp_client import SMTPClient

logger = logging.getLogger("clawMail.pool")

_DEFAULT_MAX_AGE = 300  # seconds before forcing a reconnect


class ConnectionPool:
    """Pool of IMAP/SMTP connections keyed by account name."""

    def __init__(
        self,
        account_manager: AccountManager,
        max_age: int = _DEFAULT_MAX_AGE,
    ) -> None:
        self._mgr = account_manager
        self._max_age = max_age
        self._imap: dict[str, tuple[IMAPClient, float]] = {}
        self._smtp: dict[str, tuple[SMTPClient, float]] = {}

    def get_imap(self, account: str = "") -> IMAPClient:
        """Return a connected IMAPClient, reusing if possible."""
        account = account or self._mgr.default_account

        if account in self._imap:
            client, created = self._imap[account]
            age = time.monotonic() - created
            if age < self._max_age and self._imap_alive(client):
                return client
            # Stale or dead — close and recreate
            self._close_imap(account)

        client = self._mgr.get_imap_client(account)
        client.connect()
        self._imap[account] = (client, time.monotonic())
        return client

    def get_smtp(self, account: str = "") -> SMTPClient:
        """Return an SMTPClient (created fresh, SMTP is stateless per send)."""
        account = account or self._mgr.default_account
        return self._mgr.get_smtp_client(account)

    def release_imap(self, account: str = "") -> None:
        """Release (disconnect) a specific IMAP connection."""
        account = account or self._mgr.default_account
        self._close_imap(account)

    def close_all(self) -> None:
        """Disconnect all pooled connections."""
        for acct in list(self._imap):
            self._close_imap(acct)
        self._imap.clear()
        self._smtp.clear()

    def _close_imap(self, account: str) -> None:
        entry = self._imap.pop(account, None)
        if entry:
            client, _ = entry
            try:
                client.disconnect()
            except Exception as exc:
                logger.debug("Pool disconnect %s: %s", account, exc)

    @staticmethod
    def _imap_alive(client: IMAPClient) -> bool:
        """Quick liveness check via NOOP."""
        try:
            status, _ = client.conn.noop()
            return status == "OK"
        except Exception:
            return False

    def __enter__(self) -> ConnectionPool:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close_all()
