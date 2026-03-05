"""Data models for email messages, addresses, and attachments."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any


@dataclass(frozen=True)
class EmailAddress:
    """An email address with optional display name."""

    address: str
    display_name: str = ""

    def __str__(self) -> str:
        if self.display_name:
            return f"{self.display_name} <{self.address}>"
        return self.address

    @classmethod
    def parse(cls, raw: str) -> EmailAddress:
        raw = raw.strip()
        if "<" in raw and raw.endswith(">"):
            name_part, addr_part = raw.rsplit("<", 1)
            return cls(
                address=addr_part.rstrip(">").strip(),
                display_name=name_part.strip().strip('"'),
            )
        return cls(address=raw)

    def to_dict(self) -> dict[str, str]:
        return {"address": self.address, "display_name": self.display_name}

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> EmailAddress:
        return cls(address=d["address"], display_name=d.get("display_name", ""))


class EmailPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


@dataclass
class EmailAttachment:
    """An email attachment."""

    filename: str
    content_type: str
    data: bytes
    size: int = 0
    content_id: str | None = None

    def __post_init__(self) -> None:
        if not self.size:
            self.size = len(self.data)

    def to_dict(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "content_type": self.content_type,
            "data_b64": base64.b64encode(self.data).decode("ascii"),
            "size": self.size,
            "content_id": self.content_id,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> EmailAttachment:
        return cls(
            filename=d["filename"],
            content_type=d["content_type"],
            data=base64.b64decode(d.get("data_b64", "")),
            size=d.get("size", 0),
            content_id=d.get("content_id"),
        )


@dataclass
class EmailMessage:
    """Represents an email message for both inbound and outbound use."""

    subject: str = ""
    sender: EmailAddress | None = None
    recipients: list[EmailAddress] = field(default_factory=list)
    cc: list[EmailAddress] = field(default_factory=list)
    bcc: list[EmailAddress] = field(default_factory=list)
    body_plain: str = ""
    body_html: str = ""
    attachments: list[EmailAttachment] = field(default_factory=list)
    headers: dict[str, str] = field(default_factory=dict)
    message_id: str = ""
    in_reply_to: str = ""
    references: list[str] = field(default_factory=list)
    date: datetime | None = None
    priority: EmailPriority = EmailPriority.NORMAL
    is_read: bool = False
    mailbox: str = "INBOX"
    account: str = ""
    flags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def has_attachments(self) -> bool:
        return len(self.attachments) > 0

    @property
    def body(self) -> str:
        return self.body_html if self.body_html else self.body_plain

    @property
    def recipient_addresses(self) -> list[str]:
        return [r.address for r in self.recipients]

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "sender": self.sender.to_dict() if self.sender else None,
            "recipients": [r.to_dict() for r in self.recipients],
            "cc": [r.to_dict() for r in self.cc],
            "bcc": [r.to_dict() for r in self.bcc],
            "body_plain": self.body_plain,
            "body_html": self.body_html,
            "attachments": [a.to_dict() for a in self.attachments],
            "headers": self.headers,
            "message_id": self.message_id,
            "in_reply_to": self.in_reply_to,
            "references": self.references,
            "date": self.date.isoformat() if self.date else None,
            "priority": self.priority.value,
            "is_read": self.is_read,
            "mailbox": self.mailbox,
            "account": self.account,
            "flags": self.flags,
            "has_attachments": self.has_attachments,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> EmailMessage:
        sender = EmailAddress.from_dict(d["sender"]) if d.get("sender") else None
        recipients = [EmailAddress.from_dict(r) for r in d.get("recipients", [])]
        cc = [EmailAddress.from_dict(r) for r in d.get("cc", [])]
        bcc = [EmailAddress.from_dict(r) for r in d.get("bcc", [])]
        attachments = [EmailAttachment.from_dict(a) for a in d.get("attachments", [])]
        date = None
        if d.get("date"):
            try:
                date = datetime.fromisoformat(d["date"])
            except (ValueError, TypeError):
                pass
        priority = EmailPriority(d.get("priority", "normal"))
        return cls(
            subject=d.get("subject", ""),
            sender=sender,
            recipients=recipients,
            cc=cc,
            bcc=bcc,
            body_plain=d.get("body_plain", ""),
            body_html=d.get("body_html", ""),
            attachments=attachments,
            headers=d.get("headers", {}),
            message_id=d.get("message_id", ""),
            in_reply_to=d.get("in_reply_to", ""),
            references=d.get("references", []),
            date=date,
            priority=priority,
            is_read=d.get("is_read", False),
            mailbox=d.get("mailbox", "INBOX"),
            account=d.get("account", ""),
            flags=d.get("flags", []),
            metadata=d.get("metadata", {}),
        )
