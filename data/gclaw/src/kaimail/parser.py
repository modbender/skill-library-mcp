"""Email parser for extracting and cleaning email content."""

import re
from datetime import datetime
from typing import Optional

from kaimail.models import Email, EmailCategory, ParsedEmail, Thread, ThreadMessage


class EmailParser:
    """Parse and clean email content."""

    # Common newsletter/promotional footer patterns to strip
    FOOTER_PATTERNS = [
        r"(?i)unsubscribe.*$",
        r"(?i)click here to unsubscribe.*$",
        r"(?i)you('re| are) receiving this (email|newsletter).*$",
        r"(?i)view (this )?(post|email|newsletter) (on the web|in (your )?browser).*$",
        r"(?i)not interested anymore\?.*$",
        r"(?i)manage (your )?preferences.*$",
        r"(?i)update your preferences.*$",
        r"(?i)if you run into problems.*$",
        r"(?i)turn off renewal receipt.*$",
        r"(?i)get help with.*$",
    ]

    # Forwarded message markers
    FORWARD_PATTERNS = [
        r"---------- Forwarded message ---------",
        r"----- Forwarded Message -----",
        r"Begin forwarded message:",
        r"Fwd:",
    ]

    # Reply markers
    REPLY_PATTERNS = [
        r"^Re:",
        r"^RE:",
        r"^re:",
    ]

    def parse_email(self, email: Email, thread: Optional[Thread] = None) -> ParsedEmail:
        """Parse a raw email into structured format."""
        sender_name, sender_email = self._parse_from_address(email.from_address)
        sender_domain = self._extract_domain(sender_email)

        body_text = ""
        if thread and thread.primary_message:
            body_text = self._clean_body(thread.primary_message.body)

        subject_clean = self._clean_subject(email.subject)
        is_forwarded = self._is_forwarded(email.subject)
        is_reply = self._is_reply(email.subject)
        has_attachments = bool(
            thread and thread.primary_message and thread.primary_message.attachments
        )

        parsed_date = self._parse_date(email.date)

        return ParsedEmail(
            id=email.id,
            thread_id=email.thread_id,
            date=parsed_date,
            sender_email=sender_email,
            sender_name=sender_name,
            sender_domain=sender_domain,
            subject=email.subject,
            subject_clean=subject_clean,
            body_text=body_text,
            body_preview=body_text[:200] if body_text else "",
            labels=email.labels,
            category=EmailCategory.UNKNOWN,  # Set by classifier
            is_forwarded=is_forwarded,
            is_reply=is_reply,
            has_attachments=has_attachments,
        )

    def parse_thread_message(self, msg: ThreadMessage) -> ParsedEmail:
        """Parse a thread message directly."""
        sender_name, sender_email = self._parse_from_address(msg.from_address)
        sender_domain = self._extract_domain(sender_email)
        body_text = self._clean_body(msg.body)
        subject_clean = self._clean_subject(msg.subject)
        parsed_date = self._parse_date(msg.date)

        return ParsedEmail(
            id=msg.id,
            thread_id=msg.id,  # Use message id as thread id for single messages
            date=parsed_date,
            sender_email=sender_email,
            sender_name=sender_name,
            sender_domain=sender_domain,
            subject=msg.subject,
            subject_clean=subject_clean,
            body_text=body_text,
            body_preview=body_text[:200] if body_text else "",
            labels=[],
            category=EmailCategory.UNKNOWN,
            is_forwarded=self._is_forwarded(msg.subject),
            is_reply=self._is_reply(msg.subject),
            has_attachments=bool(msg.attachments),
        )

    def _parse_from_address(self, from_addr: str) -> tuple[str, str]:
        """Extract sender name and email from From header."""
        # Pattern: "Name" <email@domain.com> or Name <email@domain.com>
        match = re.match(r'^"?([^"<]+)"?\s*<([^>]+)>', from_addr)
        if match:
            return match.group(1).strip(), match.group(2).strip().lower()

        # Pattern: email@domain.com
        match = re.match(r"^([^\s<]+@[^\s>]+)", from_addr)
        if match:
            email = match.group(1).strip().lower()
            return email.split("@")[0], email

        return from_addr, from_addr

    def _extract_domain(self, email: str) -> str:
        """Extract domain from email address."""
        if "@" in email:
            return email.split("@")[1].lower()
        return ""

    def _clean_subject(self, subject: str) -> str:
        """Remove Re:, Fwd:, etc. from subject."""
        cleaned = subject
        for pattern in self.REPLY_PATTERNS + [r"^Fwd:\s*", r"^FW:\s*", r"^fw:\s*"]:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()
        return cleaned

    def _is_forwarded(self, subject: str) -> bool:
        """Check if email is a forward."""
        return bool(re.search(r"^Fwd:|^FW:", subject, re.IGNORECASE))

    def _is_reply(self, subject: str) -> bool:
        """Check if email is a reply."""
        return bool(re.search(r"^Re:", subject, re.IGNORECASE))

    def _clean_body(self, body: str) -> str:
        """Clean body text by removing footers, HTML, etc."""
        if not body:
            return ""

        text = body

        # Strip common HTML entities that might be in plain text
        text = re.sub(r"&nbsp;", " ", text)
        text = re.sub(r"&amp;", "&", text)
        text = re.sub(r"&lt;", "<", text)
        text = re.sub(r"&gt;", ">", text)

        # Remove URLs that are just tracking links (long query strings)
        text = re.sub(r"https?://[^\s]+[?&][^\s]{50,}", "[link]", text)

        # Strip footer patterns
        for pattern in self.FOOTER_PATTERNS:
            text = re.sub(pattern, "", text, flags=re.MULTILINE)

        # Remove forwarded message headers (keep the quoted content)
        for pattern in self.FORWARD_PATTERNS:
            text = re.sub(re.escape(pattern) + r".*?\n", "", text)

        # Collapse multiple newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string into datetime."""
        # Try common formats
        formats = [
            "%Y-%m-%d %H:%M",  # 2026-02-26 14:05
            "%a, %d %b %Y %H:%M:%S %z",  # Wed, 25 Feb 2026 19:07:28 +0000
            "%a, %d %b %Y %H:%M:%S %Z",  # With timezone name
            "%d %b %Y %H:%M:%S %z",  # 28 Feb 2026 06:03:38 -0000
            "%a, %d %b %Y %H:%M:%S %z (%Z)",  # With extra tz
        ]

        # Clean up date string
        date_str = re.sub(r"\s*\([^)]+\)\s*$", "", date_str)  # Remove trailing (GMT) etc.

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        # Fallback: return current time
        return datetime.now()
