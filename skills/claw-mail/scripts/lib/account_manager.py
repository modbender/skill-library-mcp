"""Multi-account manager for IMAP/SMTP clients.

Loads a multi-account config, creates clients on demand, and handles
SMTP fallback when an account's own SMTP server is unreachable.

Config layout (YAML)::

    default_account: work

    smtp_fallback:
      host: smtp-relay.example.com
      port: 587
      username: relay-user
      password: relay-pass
      tls: true

    accounts:
      work:
        label: Work
        sender_address: alice@company.com
        sender_name: Alice Smith
        imap:
          host: imap.company.com
          ...
        smtp:
          host: smtp.company.com
          ...
        mailboxes: [INBOX, Projects]
        fetch_limit: 50
        rules: [...]

    # Global rules applied after per-account rules
    rules: [...]
"""

from __future__ import annotations

import copy
import logging
from typing import Any

from . import credential_store
from .imap_client import IMAPClient
from .smtp_client import SMTPClient
from .models import EmailAddress

logger = logging.getLogger("clawMail.accounts")
_ARCHIVE_FREQUENCIES = {"daily", "weekly", "monthly", "yearly"}


class AccountManager:
    """Registry of email accounts with client factory methods."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._raw = config
        self._accounts: dict[str, dict[str, Any]] = config.get("accounts", {})
        self._default_name: str = config.get("default_account", "")
        self._smtp_fallback: dict[str, Any] = config.get("smtp_fallback", {})
        self._global_rules: list[dict[str, Any]] = config.get("rules", [])
        self._defaults: dict[str, Any] = config.get("defaults", {})

        # If no accounts block, treat legacy single-account config as "default"
        if not self._accounts and (config.get("imap") or config.get("smtp")):
            self._accounts["default"] = {
                "label": "Default",
                "imap": config.get("imap", {}),
                "smtp": config.get("smtp", {}),
                "sender_address": config.get("sender_address", ""),
                "mailboxes": config.get("mailboxes", ["INBOX"]),
                "fetch_limit": config.get("fetch_limit", 50),
                "rules": config.get("rules", []),
            }
            if not self._default_name:
                self._default_name = "default"

        # Auto-select default if not set
        if not self._default_name and self._accounts:
            # Use first account as default
            self._default_name = next(iter(self._accounts))

    # ── Queries ──────────────────────────────────────────────────────

    @property
    def default_account(self) -> str:
        return self._default_name

    def list_accounts(self) -> list[str]:
        return list(self._accounts.keys())

    def get_account(self, name: str = "") -> dict[str, Any]:
        """Return the config dict for a named account (or the default)."""
        name = name or self._default_name
        if name not in self._accounts:
            raise KeyError(f"Unknown account: {name!r}. "
                           f"Available: {', '.join(self._accounts)}")
        return self._accounts[name]

    def get_label(self, name: str = "") -> str:
        acct = self.get_account(name)
        return acct.get("label", name)

    def get_sender(self, name: str = "") -> EmailAddress | None:
        acct = self.get_account(name)
        addr = acct.get("sender_address", "")
        if not addr:
            addr = acct.get("imap", {}).get("username", "")
        if not addr:
            return None
        display = acct.get("sender_name", "")
        return EmailAddress(address=addr, display_name=display)

    def get_mailboxes(self, name: str = "") -> list[str]:
        acct = self.get_account(name)
        default_limit = self._defaults.get("mailboxes", ["INBOX"])
        return acct.get("mailboxes", default_limit)

    def get_fetch_limit(self, name: str = "") -> int:
        acct = self.get_account(name)
        default_limit = self._defaults.get("fetch_limit", 50)
        return acct.get("fetch_limit", default_limit)

    def get_archive_root(self, name: str = "") -> str:
        """Return the desired archive folder prefix for an account."""
        acct = self.get_account(name)
        return acct.get("archive_root", self._defaults.get("archive_root", "Archive"))

    def get_archive_frequency(self, name: str = "") -> str:
        """Return the archive frequency (daily/weekly/monthly/yearly)."""
        acct = self.get_account(name)
        freq = acct.get("archive_frequency", self._defaults.get("archive_frequency", "monthly"))
        if freq not in _ARCHIVE_FREQUENCIES:
            return "monthly"
        return freq

    def get_rules(self, name: str = "") -> list[dict[str, Any]]:
        """Per-account rules + global rules, combined."""
        acct = self.get_account(name)
        per_account = acct.get("rules", [])
        return per_account + self._global_rules

    # ── Client factories ─────────────────────────────────────────────

    def _get_oauth2_manager(self, cfg: dict[str, Any]) -> Any:
        """Create an OAuth2Manager if the config uses oauth2 auth."""
        if cfg.get("auth") != "oauth2":
            return None
        oauth2_cfg = cfg.get("oauth2", {})
        if not oauth2_cfg:
            return None
        from .oauth2 import OAuth2Manager
        return OAuth2Manager(oauth2_cfg)

    def get_imap_client(self, name: str = "") -> IMAPClient:
        """Create and return an IMAPClient for the named account.

        Passwords are resolved through the credential store, supporting
        ``op://``, ``keychain://``, ``env://``, and plain-text values.
        """
        acct = self.get_account(name)
        imap_cfg = acct.get("imap", {})
        if not imap_cfg.get("host"):
            raise ValueError(f"No IMAP host configured for account {name!r}")
        oauth2_mgr = self._get_oauth2_manager(imap_cfg)
        client = IMAPClient(
            host=imap_cfg["host"],
            port=imap_cfg.get("port", 993),
            username=imap_cfg.get("username", ""),
            password=credential_store.resolve(imap_cfg.get("password", "")),
            use_ssl=imap_cfg.get("ssl", True),
            timeout=imap_cfg.get("timeout", 30),
            oauth2_manager=oauth2_mgr,
        )
        client._account = name or self._default_name
        return client

    def get_smtp_client(self, name: str = "") -> SMTPClient:
        """Create an SMTPClient for the named account.

        Passwords are resolved through the credential store, supporting
        ``op://``, ``keychain://``, ``env://``, and plain-text values.

        Does NOT attempt to connect or fall back here — that is handled
        by :meth:`send_with_fallback`.
        """
        acct = self.get_account(name)
        smtp_cfg = acct.get("smtp", {})
        if not smtp_cfg.get("host"):
            raise ValueError(f"No SMTP host configured for account {name!r}")
        oauth2_mgr = self._get_oauth2_manager(smtp_cfg)
        return SMTPClient(
            host=smtp_cfg["host"],
            port=smtp_cfg.get("port", 587),
            username=smtp_cfg.get("username", ""),
            password=credential_store.resolve(smtp_cfg.get("password", "")),
            use_tls=smtp_cfg.get("tls", True),
            oauth2_manager=oauth2_mgr,
        )

    def send_with_fallback(self, message, name: str = "") -> dict[str, Any]:
        """Send a message via the account's SMTP, falling back to smtp_fallback.

        Returns: {"success": bool, "transport": str, "account": str,
                  "fallback_used": bool, "error": str}.
        """
        acct_name = name or self._default_name
        result: dict[str, Any] = {
            "success": False,
            "transport": "smtp",
            "account": acct_name,
            "fallback_used": False,
            "error": "",
        }

        # Try account's own SMTP
        acct = self.get_account(acct_name)
        smtp_cfg = acct.get("smtp", {})
        if smtp_cfg.get("host"):
            oauth2_mgr = self._get_oauth2_manager(smtp_cfg)
            client = SMTPClient(
                host=smtp_cfg["host"],
                port=smtp_cfg.get("port", 587),
                username=smtp_cfg.get("username", ""),
                password=credential_store.resolve(smtp_cfg.get("password", "")),
                use_tls=smtp_cfg.get("tls", True),
                oauth2_manager=oauth2_mgr,
            )
            ok = client.send(message)
            if ok:
                result["success"] = True
                return result
            logger.warning(
                "Account %s SMTP (%s) failed, trying fallback",
                acct_name, smtp_cfg["host"],
            )

        # Try fallback SMTP
        fb = self._smtp_fallback
        if fb.get("host"):
            client = SMTPClient(
                host=fb["host"],
                port=fb.get("port", 587),
                username=fb.get("username", ""),
                password=credential_store.resolve(fb.get("password", "")),
                use_tls=fb.get("tls", True),
            )
            ok = client.send(message)
            if ok:
                result["success"] = True
                result["fallback_used"] = True
                return result
            result["error"] = "Both account SMTP and fallback SMTP failed"
        else:
            result["error"] = "Account SMTP failed and no fallback configured"

        return result

    def send_via_outbox(self, message, name: str = "") -> dict[str, Any]:
        """Send a message using the IMAP Outbox pattern.

        1. Stage the message in the account's IMAP Outbox folder.
        2. Attempt SMTP delivery (with fallback).
        3. On success, remove from Outbox.  If Outbox is now empty,
           delete the temporary folder.
        4. On failure, the message remains in Outbox for later retry.

        Returns: {"success": bool, "transport": str, "account": str,
                  "fallback_used": bool, "staged": bool, "error": str}.
        """
        from .outbox import Outbox, OutboxStageError

        acct_name = name or self._default_name
        result: dict[str, Any] = {
            "success": False,
            "transport": "smtp",
            "account": acct_name,
            "fallback_used": False,
            "staged": False,
            "error": "",
            "stage_error": "",
        }

        # Step 1: Stage in Outbox
        import imaplib
        imap_client = self.get_imap_client(acct_name)
        connected = False
        try:
            imap_client.connect()
            connected = True
            outbox = Outbox(imap_client)
            try:
                staged = outbox.stage(message)
                result["staged"] = staged
            except OutboxStageError as exc:
                reason = str(exc) or "unknown reason"
                logger.warning(
                    "Outbox staging failing repeatedly for %s: %s",
                    message.subject, reason,
                )
                result["error"] = f"Outbox staging failed: {reason}"
                result["staged"] = False
                result["stage_error"] = reason
                send_result = self.send_with_fallback(message, acct_name)
                result["success"] = send_result["success"]
                result["fallback_used"] = send_result.get("fallback_used", False)
                if send_result.get("success"):
                    result["note"] = "Message sent directly via SMTP (Outbox unavailable)"
                else:
                    result["error"] = send_result.get("error", result["error"])
                return result

            # Step 2: Send via SMTP (with fallback)
            send_result = self.send_with_fallback(message, acct_name)

            if send_result["success"]:
                # Step 3a: Success — remove from Outbox
                result["success"] = True
                result["fallback_used"] = send_result["fallback_used"]
                if message.message_id:
                    imap_client.delete_message(
                        message.message_id, mailbox="Outbox",
                    )
                # Clean up Outbox folder if empty
                outbox._cleanup_if_empty()
            else:
                # Step 3b: Failure — leave in Outbox for retry
                result["error"] = send_result.get("error", "SMTP send failed")
                logger.warning(
                    "Message staged in Outbox but SMTP failed: %s",
                    result["error"],
                )
        except (imaplib.IMAP4.error, OSError) as exc:
            reason = str(exc)
            logger.warning(
                "IMAP connection for Outbox failed (%s), sending straight via SMTP", reason
            )
            send_result = self.send_with_fallback(message, acct_name)
            result["success"] = send_result["success"]
            result["fallback_used"] = send_result.get("fallback_used", False)
            result["note"] = "Sent via SMTP because IMAP Outbox was unavailable"
            result["stage_error"] = reason
            if not send_result["success"]:
                result["error"] = send_result.get("error", reason)
            else:
                result["error"] = reason
            return result
        finally:
            if connected:
                imap_client.disconnect()

        return result

    def drain_outbox(self, name: str = "") -> dict[str, Any]:
        """Drain the Outbox for an account, sending all pending messages.

        Returns a dict with drain results.
        """
        from .outbox import Outbox

        acct_name = name or self._default_name
        imap_client = self.get_imap_client(acct_name)
        try:
            imap_client.connect()
            outbox = Outbox(imap_client)

            if not outbox.exists():
                return {"account": acct_name, "attempted": 0, "sent": 0,
                        "failed": 0, "errors": []}

            def _send(msg):
                return self.send_with_fallback(msg, acct_name)

            drain_result = outbox.drain(_send)
            out = drain_result.to_dict()
            out["account"] = acct_name
            return out
        finally:
            imap_client.disconnect()

    # ── Convenience ──────────────────────────────────────────────────

    def resolve_account_for_message(self, message) -> str:
        """Determine which account a message belongs to.

        Checks message.account first, then tries to match by sender address.
        Falls back to default.
        """
        if message.account and message.account in self._accounts:
            return message.account
        if message.sender:
            for name, acct in self._accounts.items():
                addr = acct.get("sender_address", "")
                imap_user = acct.get("imap", {}).get("username", "")
                if message.sender.address in (addr, imap_user):
                    return name
        return self._default_name

    @classmethod
    def from_yaml(cls, path: str) -> AccountManager:
        """Load from a YAML config file."""
        import yaml
        with open(path) as f:
            config = yaml.safe_load(f) or {}
        return cls(config)
