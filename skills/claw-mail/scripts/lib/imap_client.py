"""IMAP client for server-side email retrieval and folder management."""

from __future__ import annotations

import base64
import email
import email.header
import email.utils
import imaplib
import logging
import re
import ssl
import time
from datetime import datetime
from typing import Any

from .models import EmailAddress, EmailAttachment, EmailMessage, EmailPriority

logger = logging.getLogger("clawMail.imap")

# Charsets that Python doesn't recognise but appear in real-world headers.
_CHARSET_FALLBACKS = {
    "unknown-8bit": "latin-1",
    "x-unknown": "latin-1",
    "default": "latin-1",
    "iso-8859-8-i": "iso-8859-8",
}

_MAX_SELECT_RETRIES = 3
_SELECT_RETRY_DELAY = 1.0  # seconds


# ── Mailbox name helpers ────────────────────────────────────────────


def _quote_mailbox(name: str) -> str:
    """IMAP-quote a mailbox name for use with imaplib.

    Python's ``imaplib`` does **not** quote mailbox arguments, so a name
    like ``Needs Review`` is sent as two separate tokens.  This helper
    wraps the name in double-quotes and escapes embedded backslashes and
    double-quote characters per RFC 3501 §9 (quoted-string grammar).
    """
    escaped = name.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _decode_mutf7(data: str) -> str:
    """Decode an IMAP modified-UTF-7 mailbox name (RFC 3501 §5.1.3).

    Rules:
    * Printable US-ASCII (0x20-0x7e) except ``&`` pass through literally.
    * ``&-`` decodes to a literal ``&``.
    * ``&<base64>-`` decodes the base64 segment (using ``,`` instead of
      ``/``) as UTF-16BE code-points.
    """
    result: list[str] = []
    i = 0
    while i < len(data):
        if data[i] == "&":
            end = data.find("-", i + 1)
            if end == -1:
                # Malformed — treat the rest as literal
                result.append(data[i:])
                break
            if end == i + 1:
                # &- is literal &
                result.append("&")
            else:
                b64_segment = data[i + 1:end].replace(",", "/")
                # Pad to a multiple of 4
                b64_segment += "=" * ((4 - len(b64_segment) % 4) % 4)
                try:
                    raw = base64.b64decode(b64_segment)
                    result.append(raw.decode("utf-16-be"))
                except Exception:
                    # Malformed — keep the original text
                    result.append(data[i:end + 1])
            i = end + 1
        else:
            result.append(data[i])
            i += 1
    return "".join(result)


def _encode_mutf7(text: str) -> str:
    """Encode a Unicode string to IMAP modified-UTF-7.

    The inverse of ``_decode_mutf7``.
    """
    result: list[str] = []
    non_ascii: list[str] = []

    def _flush_non_ascii() -> None:
        if not non_ascii:
            return
        raw = "".join(non_ascii).encode("utf-16-be")
        b64 = base64.b64encode(raw).decode("ascii").rstrip("=")
        result.append("&" + b64.replace("/", ",") + "-")
        non_ascii.clear()

    for ch in text:
        if ch == "&":
            _flush_non_ascii()
            result.append("&-")
        elif 0x20 <= ord(ch) <= 0x7E:
            _flush_non_ascii()
            result.append(ch)
        else:
            non_ascii.append(ch)
    _flush_non_ascii()
    return "".join(result)


class IMAPClient:
    """IMAP client for fetching emails and managing folders."""

    def __init__(
        self,
        host: str,
        port: int = 993,
        username: str = "",
        password: str = "",
        use_ssl: bool = True,
        timeout: int = 30,
        oauth2_manager: Any | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.timeout = timeout
        self._oauth2 = oauth2_manager
        self._connection: imaplib.IMAP4 | imaplib.IMAP4_SSL | None = None
        self._account: str = ""  # set by AccountManager
        self._last_append_error: str = ""
        self._chunk_size = 16 * 1024

    @staticmethod
    def _create_secure_context() -> ssl.SSLContext:
        """Create a hardened SSL context with secure ciphers only.

        Enforces TLS 1.2+, disables weak ciphers, and enables
        certificate verification and hostname checking.
        """
        ctx = ssl.create_default_context()
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.set_ciphers(
            "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20"
            ":!aNULL:!MD5:!DSS:!RC4:!3DES"
        )
        # Enforce certificate verification (default, but be explicit)
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_REQUIRED
        return ctx

    def connect(self) -> None:
        if self.use_ssl:
            ctx = self._create_secure_context()
            self._connection = imaplib.IMAP4_SSL(
                self.host, self.port, ssl_context=ctx, timeout=self.timeout,
            )
        else:
            self._connection = imaplib.IMAP4(self.host, self.port)
            self._connection.socket().settimeout(self.timeout)

        if self._oauth2:
            from .oauth2 import build_xoauth2_string
            auth_string = build_xoauth2_string(
                self.username, self._oauth2.access_token,
            )
            self._connection.authenticate(
                "XOAUTH2",
                lambda _x: auth_string.encode("ascii"),
            )
        else:
            self._connection.login(self.username, self.password)

    def disconnect(self) -> None:
        conn = self._connection
        self._connection = None
        if conn is None:
            return
        try:
            conn.logout()
        except Exception:
            # logout failed (SSL corruption, connection drop, etc.)
            # Force-close the underlying socket directly.
            try:
                conn.shutdown()
            except Exception:
                pass
            try:
                sock = conn.socket()
                if sock:
                    sock.close()
            except Exception:
                pass

    @property
    def conn(self) -> imaplib.IMAP4 | imaplib.IMAP4_SSL:
        if self._connection is None:
            raise RuntimeError("Not connected. Call connect() first.")
        return self._connection

    # ── Folder management ────────────────────────────────────────────

    def list_folders(self) -> list[dict[str, str]]:
        """List all folders with attributes.

        Returns list of dicts: {"name": ..., "delimiter": ..., "flags": ...}.
        Folder names are decoded from IMAP modified-UTF-7.
        """
        try:
            status, data = self.conn.list()
        except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as exc:
            logger.warning("LIST failed: %s", exc)
            return []
        if status != "OK":
            return []
        folders = []
        # Regex handles both quoted and unquoted folder names:
        #   (\Flags) "delim" "Folder With Spaces"
        #   (\Flags) "delim" PlainFolder
        # The quoted-name branch uses a non-greedy match inside quotes
        # that allows escaped characters (\\ and \").
        _LIST_RE = re.compile(
            r'\(([^)]*)\)\s+'           # flags
            r'(?:"([^"]+)"|NIL)\s+'     # delimiter (quoted or NIL)
            r'(?:"((?:[^"\\]|\\.)*)"|'  # quoted folder name (with escapes)
            r'(\S+))'                   # OR unquoted atom folder name
        )
        for item in data:
            if isinstance(item, bytes):
                decoded = item.decode("utf-8", errors="replace")
                m = _LIST_RE.match(decoded)
                if m:
                    flags = m.group(1)
                    delimiter = m.group(2) or ""
                    # Group 3 = quoted name, Group 4 = unquoted name
                    raw_name = m.group(3) if m.group(3) is not None else (m.group(4) or "")
                    # Un-escape any backslash-escaped characters in quoted names
                    raw_name = raw_name.replace('\\"', '"').replace("\\\\", "\\")
                    # Decode IMAP modified-UTF-7
                    name = _decode_mutf7(raw_name)
                    folders.append({
                        "name": name,
                        "delimiter": delimiter,
                        "flags": flags,
                    })
        return folders

    def folder_status(self, folder: str) -> dict[str, int]:
        """Get message counts for a folder.

        Returns: {"messages": N, "unseen": N, "recent": N}.
        """
        try:
            status, data = self.conn.status(_quote_mailbox(folder), "(MESSAGES UNSEEN RECENT)")
        except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as exc:
            logger.warning("STATUS %s failed: %s", folder, exc)
            return {"messages": 0, "unseen": 0, "recent": 0}
        if status != "OK":
            return {"messages": 0, "unseen": 0, "recent": 0}
        raw = data[0].decode("utf-8", errors="replace") if isinstance(data[0], bytes) else data[0]
        result: dict[str, int] = {"messages": 0, "unseen": 0, "recent": 0}
        for key in ("MESSAGES", "UNSEEN", "RECENT"):
            m = re.search(rf"{key}\s+(\d+)", raw)
            if m:
                result[key.lower()] = int(m.group(1))
        return result

    def create_folder(self, folder: str) -> bool:
        """Create a new folder/mailbox."""
        quoted = _quote_mailbox(folder)
        try:
            status, _ = self.conn.create(quoted)
            if status == "OK":
                self.conn.subscribe(quoted)
                return True
        except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as exc:
            logger.warning("CREATE %s failed: %s", folder, exc)
        return False

    def delete_folder(self, folder: str) -> bool:
        """Delete a folder/mailbox."""
        quoted = _quote_mailbox(folder)
        try:
            self.conn.unsubscribe(quoted)
            status, _ = self.conn.delete(quoted)
            return status == "OK"
        except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as exc:
            logger.warning("DELETE %s failed: %s", folder, exc)
            return False

    def rename_folder(self, old_name: str, new_name: str) -> bool:
        """Rename a folder."""
        try:
            status, _ = self.conn.rename(_quote_mailbox(old_name), _quote_mailbox(new_name))
            return status == "OK"
        except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as exc:
            logger.warning("RENAME %s -> %s failed: %s", old_name, new_name, exc)
            return False

    def move_folder(self, folder: str, new_parent: str) -> bool:
        """Move a folder under a new parent using the folder's delimiter.

        Example: move_folder("Projects", "Archive") renames
        "Projects" to "Archive/Projects" (delimiter-aware).
        """
        folders = self.list_folders()
        delimiter = "/"
        for f in folders:
            if f["name"] == folder:
                delimiter = f.get("delimiter", "/")
                break
        base_name = folder.rsplit(delimiter, 1)[-1]
        new_name = f"{new_parent}{delimiter}{base_name}"
        return self.rename_folder(folder, new_name)

    # ── Message retrieval ────────────────────────────────────────────

    def _select_robust(self, mailbox: str, readonly: bool = True) -> None:
        """Select a mailbox with retry logic for transient errors."""
        last_exc: Exception | None = None
        for attempt in range(_MAX_SELECT_RETRIES):
            try:
                status, data = self.conn.select(_quote_mailbox(mailbox), readonly=readonly)
                if status == "OK":
                    return
                raise imaplib.IMAP4.error(
                    f"SELECT failed: {data}"
                )
            except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as exc:
                last_exc = exc
                logger.warning(
                    "SELECT %s attempt %d/%d failed: %s",
                    mailbox, attempt + 1, _MAX_SELECT_RETRIES, exc,
                )
                if attempt < _MAX_SELECT_RETRIES - 1:
                    time.sleep(_SELECT_RETRY_DELAY * (attempt + 1))
                    # Reconnect if the connection was dropped
                    try:
                        self.conn.noop()
                    except Exception:
                        self.disconnect()
                        self.connect()
        raise RuntimeError(
            f"Failed to SELECT '{mailbox}' after {_MAX_SELECT_RETRIES} attempts: {last_exc}"
        )

    def fetch_unread(
        self, mailbox: str = "INBOX", limit: int = 50, mark_seen: bool = False,
    ) -> list[EmailMessage]:
        self._select_robust(mailbox, readonly=not mark_seen)
        try:
            status, msg_ids = self.conn.search(None, "UNSEEN")
        except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as exc:
            logger.warning("SEARCH UNSEEN in %s failed: %s", mailbox, exc)
            return []
        if status != "OK" or not msg_ids[0]:
            return []
        id_list = msg_ids[0].split()[:limit] if limit else msg_ids[0].split()
        return self._fetch_ids(id_list, mailbox, mark_seen)

    def fetch_all(
        self, mailbox: str = "INBOX", limit: int = 50,
    ) -> list[EmailMessage]:
        """Fetch all messages from a mailbox (most recent first)."""
        self._select_robust(mailbox, readonly=True)
        try:
            status, msg_ids = self.conn.search(None, "ALL")
        except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as exc:
            logger.warning("SEARCH ALL in %s failed: %s", mailbox, exc)
            return []
        if status != "OK" or not msg_ids[0]:
            return []
        id_list = msg_ids[0].split()
        if limit:
            id_list = id_list[-limit:]
        return self._fetch_ids(id_list, mailbox, mark_seen=False)

    def fetch_since(
        self, since: datetime, mailbox: str = "INBOX", limit: int = 100,
    ) -> list[EmailMessage]:
        self._select_robust(mailbox, readonly=True)
        date_str = since.strftime("%d-%b-%Y")
        try:
            status, msg_ids = self.conn.search(None, f"(SINCE {date_str})")
        except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as exc:
            logger.warning("SEARCH SINCE in %s failed: %s", mailbox, exc)
            return []
        if status != "OK" or not msg_ids[0]:
            return []
        id_list = msg_ids[0].split()[:limit] if limit else msg_ids[0].split()
        return self._fetch_ids(id_list, mailbox, mark_seen=False)

    def fetch_by_id(self, message_id: str, mailbox: str = "INBOX") -> EmailMessage | None:
        """Fetch a single message by its Message-ID header value."""
        self._select_robust(mailbox, readonly=True)
        search_id = message_id if message_id.startswith("<") else f"<{message_id}>"
        try:
            status, data = self.conn.search(None, f'(HEADER Message-ID "{search_id}")')
            if status != "OK" or not data[0]:
                return None
            seq_num = data[0].split()[0]
            status, msg_data = self.conn.fetch(seq_num, "(BODY.PEEK[])")
        except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as exc:
            logger.warning("FETCH by Message-ID %s failed: %s", message_id, exc)
            return None
        if status != "OK" or not msg_data[0]:
            return None
        raw = msg_data[0][1] if isinstance(msg_data[0], tuple) else msg_data[0]
        if isinstance(raw, bytes):
            return self._parse_email(raw, mailbox)
        return None

    def search(
        self,
        mailbox: str = "INBOX",
        criteria: str = "ALL",
        limit: int = 50,
    ) -> list[EmailMessage]:
        """Search messages using an IMAP SEARCH criteria string.

        The *criteria* argument is passed directly to the IMAP SEARCH command.
        Examples:
            "UNSEEN"
            '(FROM "alice@example.com")'
            '(SUBJECT "invoice" SINCE 01-Jan-2025)'
            '(OR (FROM "a@b.com") (FROM "c@d.com"))'
        """
        self._select_robust(mailbox, readonly=True)
        try:
            status, msg_ids = self.conn.search(None, criteria)
        except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as exc:
            logger.warning("SEARCH %s in %s failed: %s", criteria, mailbox, exc)
            return []
        if status != "OK" or not msg_ids[0]:
            return []
        id_list = msg_ids[0].split()
        if limit:
            id_list = id_list[-limit:]
        return self._fetch_ids(id_list, mailbox, mark_seen=False)

    # ── Message actions ──────────────────────────────────────────────

    def mark_read(self, message_id: str, mailbox: str = "INBOX") -> bool:
        return self._set_flag(message_id, mailbox, "+FLAGS", "\\Seen")

    def mark_unread(self, message_id: str, mailbox: str = "INBOX") -> bool:
        return self._set_flag(message_id, mailbox, "-FLAGS", "\\Seen")

    def flag_message(self, message_id: str, mailbox: str = "INBOX") -> bool:
        return self._set_flag(message_id, mailbox, "+FLAGS", "\\Flagged")

    def unflag_message(self, message_id: str, mailbox: str = "INBOX") -> bool:
        return self._set_flag(message_id, mailbox, "-FLAGS", "\\Flagged")

    def set_custom_flag(self, message_id: str, flag: str, mailbox: str = "INBOX") -> bool:
        """Set a custom keyword flag (e.g. '$Important', '$Processed')."""
        return self._set_flag(message_id, mailbox, "+FLAGS", flag)

    def remove_custom_flag(self, message_id: str, flag: str, mailbox: str = "INBOX") -> bool:
        """Remove a custom keyword flag."""
        return self._set_flag(message_id, mailbox, "-FLAGS", flag)

    def set_flags_batch(
        self, message_ids: list[str], flag: str, mailbox: str = "INBOX",
    ) -> dict[str, bool]:
        """Set a flag on multiple messages in one mailbox selection.

        Returns dict of {message_id: success}.
        """
        self._select_robust(mailbox, readonly=False)
        results: dict[str, bool] = {}
        for mid in message_ids:
            seq_num = self._resolve_seq(mid)
            if seq_num is None:
                results[mid] = False
                continue
            try:
                status, _ = self.conn.store(seq_num, "+FLAGS", flag)
                results[mid] = status == "OK"
            except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as exc:
                logger.warning("STORE +FLAGS %s on %s failed: %s", flag, mid, exc)
                results[mid] = False
        return results

    def move_message(
        self, msg_uid: str, from_mailbox: str, to_mailbox: str,
    ) -> bool:
        """Move a message between mailboxes via IMAP COPY + DELETE."""
        self._select_robust(from_mailbox, readonly=False)
        seq_num = self._resolve_seq(msg_uid)
        if seq_num is None:
            return False
        try:
            status, _ = self.conn.copy(seq_num, _quote_mailbox(to_mailbox))
            if status != "OK":
                return False
            self.conn.store(seq_num, "+FLAGS", "\\Deleted")
            self.conn.expunge()
            return True
        except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as exc:
            logger.warning("MOVE %s -> %s failed: %s", from_mailbox, to_mailbox, exc)
            return False

    def move_messages_batch(
        self, message_ids: list[str], from_mailbox: str, to_mailbox: str,
    ) -> dict[str, bool]:
        """Move multiple messages, minimising SELECT calls.

        Returns dict of {message_id: success}.
        """
        self._select_robust(from_mailbox, readonly=False)
        results: dict[str, bool] = {}
        moved_seqs = []
        for mid in message_ids:
            seq_num = self._resolve_seq(mid)
            if seq_num is None:
                results[mid] = False
                continue
            try:
                status, _ = self.conn.copy(seq_num, _quote_mailbox(to_mailbox))
                if status == "OK":
                    self.conn.store(seq_num, "+FLAGS", "\\Deleted")
                    results[mid] = True
                    moved_seqs.append(seq_num)
                else:
                    results[mid] = False
            except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as exc:
                logger.warning("MOVE batch %s -> %s failed: %s", mid, to_mailbox, exc)
                results[mid] = False
        if moved_seqs:
            try:
                self.conn.expunge()
            except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as exc:
                logger.warning("EXPUNGE after batch move failed: %s", exc)
        return results

    # ── IMAP IDLE ──────────────────────────────────────────────────

    def idle_start(self, mailbox: str = "INBOX", timeout: int = 29 * 60) -> None:
        """Enter IMAP IDLE mode on *mailbox*.

        The server will push EXISTS/EXPUNGE notifications while idle.
        Call :meth:`idle_check` to poll for responses, and
        :meth:`idle_done` to leave IDLE mode.

        *timeout* is a safety upper-bound in seconds (RFC 2177 recommends
        re-issuing IDLE every 29 minutes).
        """
        self._select_robust(mailbox, readonly=True)
        tag = self.conn._new_tag()
        self._idle_tag = tag
        self.conn.send(tag + b" IDLE\r\n")
        # Wait for the continuation response '+ ...'
        resp = self.conn.readline()
        if not resp.startswith(b"+"):
            raise RuntimeError(f"IDLE rejected: {resp!r}")
        self.conn.sock.settimeout(timeout)

    def idle_check(self, timeout: float = 30.0) -> list[tuple[bytes, bytes]]:
        """Poll for untagged responses while in IDLE mode.

        Returns a list of ``(seq_num, response)`` tuples, e.g.
        ``[(b'3', b'EXISTS')]``.  Returns an empty list on timeout.
        """
        old_timeout = self.conn.sock.gettimeout()
        self.conn.sock.settimeout(timeout)
        responses: list[tuple[bytes, bytes]] = []
        try:
            while True:
                line = self.conn.readline()
                if not line:
                    break
                if line.startswith(b"* "):
                    parts = line[2:].strip().split(None, 1)
                    if len(parts) == 2:
                        responses.append((parts[0], parts[1]))
                    else:
                        responses.append((b"", parts[0] if parts else b""))
                    # Don't block indefinitely — check if more data is ready
                    self.conn.sock.settimeout(0.5)
                else:
                    break
        except (TimeoutError, OSError):
            pass
        finally:
            self.conn.sock.settimeout(old_timeout)
        return responses

    def idle_done(self) -> None:
        """Leave IDLE mode by sending ``DONE``."""
        self.conn.send(b"DONE\r\n")
        # Read the tagged response to complete the IDLE command
        while True:
            line = self.conn.readline()
            if not line:
                break
            tag = getattr(self, "_idle_tag", None)
            if tag and line.startswith(tag):
                break

    def append_message(
        self, raw_message: bytes, mailbox: str = "Drafts", flags: str = "\\Draft",
    ) -> bool:
        """Append a raw RFC822 message to a mailbox (e.g. Drafts).

        Returns True on success.
        """
        logger.debug(
            "IMAP APPEND raw_message length=%d mailbox=%r flags=%r",
            len(raw_message), mailbox, flags,
        )
        orig_send = self.conn.send
        def _chunked_send(data):
            if isinstance(data, str):
                data = data.encode("utf-8")
            if len(data) <= self._chunk_size:
                return orig_send(data)
            for i in range(0, len(data), self._chunk_size):
                orig_send(data[i:i + self._chunk_size])
        try:
            self.conn.send = _chunked_send
            status, _ = self.conn.append(
                _quote_mailbox(mailbox), flags, None, raw_message,
            )
            if status != "OK":
                self._last_append_error = f"APPEND status {status}"
                logger.debug("APPEND response status=%s", status)
            else:
                self._last_append_error = ""
            return status == "OK"
        except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as exc:
            self._last_append_error = str(exc)
            logger.warning("APPEND to %s failed: %s", mailbox, exc)
            return False
        finally:
            self.conn.send = orig_send

    @property
    def last_append_error(self) -> str:
        return self._last_append_error

    def delete_message(self, message_id: str, mailbox: str = "INBOX") -> bool:
        self._select_robust(mailbox, readonly=False)
        seq_num = self._resolve_seq(message_id)
        if seq_num is None:
            return False
        try:
            self.conn.store(seq_num, "+FLAGS", "\\Deleted")
            self.conn.expunge()
            return True
        except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as exc:
            logger.warning("DELETE message %s failed: %s", message_id, exc)
            return False

    # ── Internal helpers ─────────────────────────────────────────────

    def _resolve_seq(self, msg_uid: str) -> bytes | None:
        """Resolve a Message-ID or sequence number to an IMAP sequence number."""
        if msg_uid.startswith("<"):
            try:
                status, data = self.conn.search(None, f'(HEADER Message-ID "{msg_uid}")')
            except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as exc:
                logger.warning("SEARCH for Message-ID %s failed: %s", msg_uid, exc)
                return None
            if status != "OK" or not data[0]:
                return None
            return data[0].split()[0]
        return msg_uid.encode() if isinstance(msg_uid, str) else msg_uid

    def _set_flag(self, message_id: str, mailbox: str, op: str, flag: str) -> bool:
        self._select_robust(mailbox, readonly=False)
        seq_num = self._resolve_seq(message_id)
        if seq_num is None:
            return False
        try:
            status, _ = self.conn.store(seq_num, op, flag)
            return status == "OK"
        except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as exc:
            logger.warning("STORE %s %s failed: %s", op, flag, exc)
            return False

    def _fetch_ids(
        self, id_list: list[bytes], mailbox: str, mark_seen: bool,
    ) -> list[EmailMessage]:
        messages = []
        for msg_id in id_list:
            fetch_flag = "(RFC822)" if mark_seen else "(BODY.PEEK[])"
            try:
                status, msg_data = self.conn.fetch(msg_id, fetch_flag)
            except (imaplib.IMAP4.error, imaplib.IMAP4.abort, OSError) as exc:
                logger.warning("Failed to fetch message %s: %s", msg_id, exc)
                continue
            if status != "OK" or not msg_data[0]:
                continue
            raw = msg_data[0][1] if isinstance(msg_data[0], tuple) else msg_data[0]
            if isinstance(raw, bytes):
                parsed = self._parse_email(raw, mailbox)
                if parsed:
                    messages.append(parsed)
        return messages

    def _parse_email(self, raw: bytes, mailbox: str) -> EmailMessage | None:
        try:
            msg = email.message_from_bytes(raw)
        except Exception:
            return None

        subject = self._decode_header(msg.get("Subject", ""))
        sender = EmailAddress.parse(self._decode_header(msg.get("From", "")))
        recipients = self._parse_address_list(msg.get("To", ""))
        cc = self._parse_address_list(msg.get("Cc", ""))

        date = None
        date_str = msg.get("Date", "")
        if date_str:
            try:
                date = email.utils.parsedate_to_datetime(date_str)
            except Exception:
                pass

        body_plain = ""
        body_html = ""
        attachments: list[EmailAttachment] = []

        if msg.is_multipart():
            for part in msg.walk():
                ct = part.get_content_type()
                disp = str(part.get("Content-Disposition", ""))
                if "attachment" in disp:
                    payload = part.get_payload(decode=True)
                    if payload:
                        attachments.append(EmailAttachment(
                            filename=part.get_filename() or "attachment",
                            content_type=ct, data=payload,
                            content_id=part.get("Content-ID"),
                        ))
                elif ct == "text/plain" and not body_plain:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_plain = payload.decode("utf-8", errors="replace")
                elif ct == "text/html" and not body_html:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_html = payload.decode("utf-8", errors="replace")
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                content = payload.decode("utf-8", errors="replace")
                if msg.get_content_type() == "text/html":
                    body_html = content
                else:
                    body_plain = content

        priority = EmailPriority.NORMAL
        xp = msg.get("X-Priority", "3")
        if xp.startswith(("1", "2")):
            priority = EmailPriority.HIGH
        elif xp.startswith(("4", "5")):
            priority = EmailPriority.LOW

        return EmailMessage(
            message_id=msg.get("Message-ID", ""), subject=subject,
            sender=sender, recipients=recipients, cc=cc,
            body_plain=body_plain, body_html=body_html,
            attachments=attachments, date=date,
            in_reply_to=msg.get("In-Reply-To", ""),
            references=msg.get("References", "").split(),
            priority=priority, mailbox=mailbox,
            account=self._account,
            headers=dict(msg.items()),
        )

    def _decode_header(self, raw: str) -> str:
        """Decode an RFC 2047 encoded header, with safe fallbacks."""
        try:
            parts = email.header.decode_header(raw)
        except Exception:
            return raw
        decoded = []
        for data, charset in parts:
            if isinstance(data, bytes):
                enc = "utf-8"
                if charset:
                    try:
                        enc = _CHARSET_FALLBACKS.get(charset.lower(), charset)
                    except Exception:
                        enc = "latin-1"
                try:
                    decoded.append(data.decode(enc, errors="replace"))
                except (LookupError, UnicodeDecodeError, TypeError):
                    # Unknown / invalid charset — latin-1 never raises
                    decoded.append(data.decode("latin-1", errors="replace"))
            else:
                decoded.append(str(data) if not isinstance(data, str) else data)
        return " ".join(decoded)

    def _parse_address_list(self, raw: str) -> list[EmailAddress]:
        if not raw:
            return []
        decoded = self._decode_header(raw)
        return [
            EmailAddress.parse(a.strip())
            for a in decoded.split(",") if a.strip()
        ]
