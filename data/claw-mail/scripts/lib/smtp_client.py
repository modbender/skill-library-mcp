"""SMTP client for sending emails."""

from __future__ import annotations

import logging
import re
import smtplib
import socket
import ssl
import uuid
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from .models import EmailMessage, EmailPriority

logger = logging.getLogger("clawMail.smtp")


def build_mime(message: EmailMessage) -> MIMEMultipart:
    """Build a MIME message from an EmailMessage (without sending).

    Useful for constructing RFC822 bytes to save as a draft.
    """
    return SMTPClient._build_mime_static(message)


class SMTPClient:
    """SMTP client for sending emails via a mail server."""

    def __init__(
        self,
        host: str,
        port: int = 587,
        username: str = "",
        password: str = "",
        use_tls: bool = True,
        oauth2_manager: object | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self._oauth2 = oauth2_manager

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

    def send(self, message: EmailMessage) -> bool:
        mime_msg = self._build_mime_static(message)
        try:
            if self.use_tls:
                server = smtplib.SMTP(self.host, self.port)
                server.ehlo()
                ctx = self._create_secure_context()
                server.starttls(context=ctx)
                server.ehlo()
            else:
                server = smtplib.SMTP(self.host, self.port)

            if self._oauth2:
                from .oauth2 import build_xoauth2_string
                auth_string = build_xoauth2_string(
                    self.username, self._oauth2.access_token,
                )
                server.docmd("AUTH", "XOAUTH2 " + auth_string)
            elif self.username:
                server.login(self.username, self.password)

            all_recips = (
                [r.address for r in message.recipients]
                + [r.address for r in message.cc]
                + [r.address for r in message.bcc]
            )
            sender_addr = message.sender.address if message.sender else self.username
            original_send = server.send
            chunk_size = 16 * 1024
            def _chunked_send(data):
                if isinstance(data, str):
                    data = data.encode("ascii")
                if len(data) <= chunk_size:
                    return original_send(data)
                for i in range(0, len(data), chunk_size):
                    original_send(data[i:i + chunk_size])
            server.send = _chunked_send
            server.sendmail(sender_addr, all_recips, mime_msg.as_string())
            server.send = original_send
            server.quit()
            return True
        except (smtplib.SMTPException, OSError) as exc:
            logger.error("SMTP send failed: %s", exc)
            return False

    @staticmethod
    def _build_mime_static(message: EmailMessage) -> MIMEMultipart:
        if message.attachments:
            mime_msg = MIMEMultipart("mixed")
            alt_part = MIMEMultipart("alternative")
            mime_msg.attach(alt_part)
        else:
            mime_msg = MIMEMultipart("alternative")
            alt_part = mime_msg

        if message.sender:
            mime_msg["From"] = str(message.sender)
        if message.recipients:
            mime_msg["To"] = ", ".join(str(r) for r in message.recipients)
        if message.cc:
            mime_msg["Cc"] = ", ".join(str(r) for r in message.cc)
        mime_msg["Subject"] = message.subject

        # RFC 5322: Date header is REQUIRED
        if message.date:
            mime_msg["Date"] = formatdate(timeval=message.date.timestamp(), localtime=True)
        else:
            mime_msg["Date"] = formatdate(localtime=True)

        # RFC 5322: Message-ID header is REQUIRED (unique identifier for this message)
        if message.message_id:
            mime_msg["Message-ID"] = message.message_id
        else:
            # Generate a unique Message-ID if not provided
            # Format: <timestamp-uuid@hostname> per RFC 5322
            try:
                hostname = socket.getfqdn()
            except Exception:
                # Fallback to sender domain if FQDN is unavailable
                hostname = (
                    message.sender.address.split("@")[1]
                    if message.sender and "@" in str(message.sender)
                    else "localhost"
                )
            msg_id = f"{int(datetime.utcnow().timestamp() * 1000)}.{uuid.uuid4().hex}@{hostname}"
            message.message_id = f"<{msg_id}>"
            mime_msg["Message-ID"] = message.message_id

        if message.in_reply_to:
            mime_msg["In-Reply-To"] = message.in_reply_to
            mime_msg["References"] = " ".join(message.references)
        if message.priority == EmailPriority.HIGH:
            mime_msg["X-Priority"] = "1"
            mime_msg["Importance"] = "high"
        elif message.priority == EmailPriority.LOW:
            mime_msg["X-Priority"] = "5"
            mime_msg["Importance"] = "low"

        # RFC 5322 compliance: Add MIME-Version header
        mime_msg["MIME-Version"] = "1.0"

        # Helpful for deliverability
        mime_msg["User-Agent"] = "clawMail/0.6.0"

        plain_text = message.body_plain
        if not plain_text and message.body_html:
            plain_text = re.sub(r"<[^>]+>", "", message.body_html)
            plain_text = re.sub(r"\n\s*\n", "\n\n", plain_text).strip()

        if plain_text:
            alt_part.attach(MIMEText(plain_text, "plain", "utf-8"))
        if message.body_html:
            alt_part.attach(MIMEText(message.body_html, "html", "utf-8"))

        for att in message.attachments:
            maintype, subtype = att.content_type.split("/", 1)
            part = MIMEBase(maintype, subtype)
            part.set_payload(att.data)
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", "attachment", filename=att.filename)
            if att.content_id:
                part.add_header("Content-ID", f"<{att.content_id}>")
            mime_msg.attach(part)

        return mime_msg
