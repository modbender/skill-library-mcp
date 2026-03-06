"""IMAP Outbox — temporary folder for outgoing messages.

Implements the Apple Mail-style Outbox pattern:

1. Before sending, the composed MIME message is saved to an IMAP
   ``Outbox`` folder (created on demand).
2. The message is sent via SMTP.
3. On success the message is deleted from Outbox.  If the Outbox is
   now empty the folder itself is removed (it is temporary).
4. On failure the message remains in Outbox and the error is reported.
5. The heartbeat (or ``retry_send.py``) periodically checks for an
   Outbox folder and attempts to deliver anything sitting there.

From the Apple documentation:

    Outbox: This folder temporarily holds messages while they are in the
    process of being sent.  The Outbox generally only appears in the
    sidebar if you have an email that is currently sending or has failed
    to send.
"""

from __future__ import annotations

import logging
from typing import Any

from .imap_client import IMAPClient
from .models import EmailMessage
from .smtp_client import SMTPClient, build_mime

logger = logging.getLogger("clawMail.outbox")

OUTBOX_FOLDER = "Outbox"


class OutboxStageError(Exception):
    """Raised when staging a message in Outbox repeatedly fails."""


class Outbox:
    """Manage an IMAP Outbox folder for outgoing messages."""

    def __init__(self, imap_client: IMAPClient) -> None:
        self._imap = imap_client

    # ── Core operations ───────────────────────────────────────────

    def stage(self, message: EmailMessage) -> bool:
        """Save a message to the Outbox folder prior to sending.

        Creates the Outbox folder if it does not already exist.
        Returns True on success.
        """
        self._ensure_folder()
        mime_msg = build_mime(message)
        raw_bytes = mime_msg.as_bytes()
        logger.debug(
            "Stage Outbox message subject=%r size=%d recipients=%s",
            message.subject, len(raw_bytes),
            ", ".join(str(r) for r in message.recipients),
        )
        ok = False
        attempts = 0
        while attempts < 3 and not ok:
            attempts += 1
            ok = self._imap.append_message(
                raw_bytes, mailbox=OUTBOX_FOLDER, flags="",
            )
            if not ok:
                logger.warning("Outbox stage attempt %d failed", attempts)
        if not ok:
            error_detail = self._imap.last_append_error or "unknown APPEND failure"
            logger.error(
                "Failed to stage message in Outbox after %d attempts: %r (%s)",
                attempts, message.subject, error_detail,
            )
            raise OutboxStageError(error_detail)
        if ok:
            logger.info(
                "Staged message in Outbox: subject=%r, to=%s",
                message.subject,
                ", ".join(str(r) for r in message.recipients),
            )
        else:
            logger.error("Failed to stage message in Outbox: %r", message.subject)
        return ok

    def drain(
        self,
        send_fn: _SendFn,
        limit: int = 50,
    ) -> DrainResult:
        """Attempt to send every message currently in the Outbox.

        *send_fn* is called with each :class:`EmailMessage` and must
        return a dict with at least ``{"success": bool}``.  On success
        the message is removed from Outbox.

        After all messages are processed, if the Outbox is empty the
        folder is deleted.

        Returns a :class:`DrainResult` summarising what happened.
        """
        if not self._folder_exists():
            return DrainResult(attempted=0, sent=0, failed=0, errors=[])

        messages = self._imap.fetch_all(mailbox=OUTBOX_FOLDER, limit=limit)
        if not messages:
            # Folder exists but is empty — clean up
            self._remove_folder()
            return DrainResult(attempted=0, sent=0, failed=0, errors=[])

        sent = 0
        failed = 0
        errors: list[dict[str, Any]] = []

        for msg in messages:
            try:
                result = send_fn(msg)
                if result.get("success"):
                    # Remove from Outbox on successful send
                    if msg.message_id:
                        self._imap.delete_message(msg.message_id, mailbox=OUTBOX_FOLDER)
                    sent += 1
                    logger.info(
                        "Sent from Outbox: subject=%r", msg.subject,
                    )
                else:
                    error_msg = result.get("error", "SMTP send failed")
                    errors.append({
                        "message_id": msg.message_id,
                        "subject": msg.subject,
                        "error": error_msg,
                    })
                    failed += 1
                    logger.warning(
                        "Failed to send from Outbox: subject=%r error=%s",
                        msg.subject, error_msg,
                    )
            except Exception as exc:
                errors.append({
                    "message_id": msg.message_id,
                    "subject": msg.subject,
                    "error": str(exc),
                })
                failed += 1
                logger.error(
                    "Exception sending from Outbox: subject=%r error=%s",
                    msg.subject, exc,
                )

        # If Outbox is now empty, remove the temporary folder
        if sent > 0:
            self._cleanup_if_empty()

        return DrainResult(
            attempted=len(messages), sent=sent, failed=failed, errors=errors,
        )

    def list_pending(self, limit: int = 50) -> list[EmailMessage]:
        """List messages currently sitting in the Outbox."""
        if not self._folder_exists():
            return []
        return self._imap.fetch_all(mailbox=OUTBOX_FOLDER, limit=limit)

    def exists(self) -> bool:
        """Check whether the Outbox folder currently exists."""
        return self._folder_exists()

    # ── Folder management ─────────────────────────────────────────

    def _ensure_folder(self) -> None:
        """Create the Outbox folder if it does not exist."""
        if not self._folder_exists():
            ok = self._imap.create_folder(OUTBOX_FOLDER)
            if ok:
                logger.info("Created Outbox folder")
            else:
                logger.warning("Failed to create Outbox folder")

    def _folder_exists(self) -> bool:
        """Check if the Outbox folder exists on the IMAP server."""
        folders = self._imap.list_folders()
        return any(f["name"] == OUTBOX_FOLDER for f in folders)

    def _remove_folder(self) -> None:
        """Delete the Outbox folder (it is temporary)."""
        ok = self._imap.delete_folder(OUTBOX_FOLDER)
        if ok:
            logger.info("Removed empty Outbox folder")
        else:
            logger.debug("Could not remove Outbox folder")

    def _cleanup_if_empty(self) -> None:
        """Remove the Outbox folder if it has no remaining messages."""
        status = self._imap.folder_status(OUTBOX_FOLDER)
        if status.get("messages", 1) == 0:
            self._remove_folder()


# ── Type alias for the send callback ─────────────────────────────

from typing import Callable, Protocol

_SendFn = Callable[[EmailMessage], dict[str, Any]]


# ── Result dataclass ─────────────────────────────────────────────

class DrainResult:
    """Summary of an Outbox drain operation."""

    __slots__ = ("attempted", "sent", "failed", "errors")

    def __init__(
        self,
        attempted: int,
        sent: int,
        failed: int,
        errors: list[dict[str, Any]],
    ) -> None:
        self.attempted = attempted
        self.sent = sent
        self.failed = failed
        self.errors = errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "attempted": self.attempted,
            "sent": self.sent,
            "failed": self.failed,
            "errors": self.errors,
        }

    def __repr__(self) -> str:
        return (
            f"DrainResult(attempted={self.attempted}, sent={self.sent}, "
            f"failed={self.failed})"
        )
