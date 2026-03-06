"""Rule-based email processing pipeline."""

from __future__ import annotations

import json
import logging
import re
import urllib.request
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from .models import EmailMessage

logger = logging.getLogger("clawMail.processor")


class RuleAction(Enum):
    FLAG = "flag"
    TAG = "tag"
    MARK_READ = "mark_read"
    MOVE = "move"
    ARCHIVE = "archive"
    FORWARD = "forward"
    AUTO_REPLY = "auto_reply"
    CALLBACK = "callback"
    WEBHOOK = "webhook"
    SKIP = "skip"


@dataclass
class ProcessingRule:
    name: str
    actions: list[RuleAction]

    sender_pattern: str = ""
    subject_pattern: str = ""
    body_pattern: str = ""
    mailbox: str = ""
    account: str = ""
    has_attachments: bool | None = None

    flag_index: int = 0
    tag: str = ""
    move_to: str = ""
    forward_to: str = ""
    reply_template: str = ""
    webhook_url: str = ""
    callback: Callable[[EmailMessage], Any] | None = None

    priority: int = 0
    stop_after_match: bool = False

    def matches(self, message: EmailMessage) -> bool:
        if self.sender_pattern:
            sender_str = str(message.sender) if message.sender else ""
            if not re.search(self.sender_pattern, sender_str, re.IGNORECASE):
                return False
        if self.subject_pattern:
            if not re.search(self.subject_pattern, message.subject, re.IGNORECASE):
                return False
        if self.body_pattern:
            body = message.body_plain or message.body_html or ""
            if not re.search(self.body_pattern, body, re.IGNORECASE):
                return False
        if self.mailbox and message.mailbox != self.mailbox:
            return False
        if self.account and message.account != self.account:
            return False
        if self.has_attachments is not None:
            if message.has_attachments != self.has_attachments:
                return False
        return True


@dataclass
class ProcessingResult:
    message: EmailMessage
    matched_rules: list[str] = field(default_factory=list)
    actions_taken: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    should_flag: bool = False
    flag_index: int = 0
    should_mark_read: bool = False
    move_to: str = ""
    should_archive: bool = False
    forward_to: list[str] = field(default_factory=list)
    reply_body: str = ""
    webhook_results: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "message_id": self.message.message_id,
            "subject": self.message.subject,
            "account": self.message.account,
            "matched_rules": self.matched_rules,
            "actions_taken": self.actions_taken,
            "tags": self.tags,
            "should_flag": self.should_flag,
            "flag_index": self.flag_index,
            "should_mark_read": self.should_mark_read,
            "move_to": self.move_to,
            "should_archive": self.should_archive,
            "forward_to": self.forward_to,
            "reply_body": self.reply_body,
            "webhook_results": self.webhook_results,
            "errors": self.errors,
        }


class EmailProcessor:
    def __init__(self) -> None:
        self._rules: list[ProcessingRule] = []

    def add_rule(self, rule: ProcessingRule) -> None:
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority, reverse=True)

    def remove_rule(self, name: str) -> bool:
        before = len(self._rules)
        self._rules = [r for r in self._rules if r.name != name]
        return len(self._rules) < before

    @property
    def rules(self) -> list[ProcessingRule]:
        return list(self._rules)

    def process(self, message: EmailMessage) -> ProcessingResult:
        result = ProcessingResult(message=message)
        for rule in self._rules:
            if not rule.matches(message):
                continue
            result.matched_rules.append(rule.name)
            for action in rule.actions:
                try:
                    self._apply(action, rule, result)
                    result.actions_taken.append(f"{rule.name}:{action.value}")
                except Exception as exc:
                    result.errors.append(f"{rule.name}:{action.value}: {exc}")
            if rule.stop_after_match:
                break
        return result

    def process_batch(self, messages: list[EmailMessage]) -> list[ProcessingResult]:
        return [self.process(msg) for msg in messages]

    def _apply(
        self, action: RuleAction, rule: ProcessingRule, result: ProcessingResult,
    ) -> None:
        if action == RuleAction.FLAG:
            result.should_flag = True
            result.flag_index = rule.flag_index
        elif action == RuleAction.TAG:
            if rule.tag:
                result.tags.append(rule.tag)
        elif action == RuleAction.MARK_READ:
            result.should_mark_read = True
        elif action == RuleAction.MOVE:
            if rule.move_to:
                result.move_to = rule.move_to
        elif action == RuleAction.ARCHIVE:
            result.should_archive = True
        elif action == RuleAction.FORWARD:
            if rule.forward_to:
                result.forward_to.append(rule.forward_to)
        elif action == RuleAction.AUTO_REPLY:
            if rule.reply_template:
                result.reply_body = rule.reply_template
        elif action == RuleAction.WEBHOOK:
            if rule.webhook_url:
                self._fire_webhook(rule.webhook_url, result)
        elif action == RuleAction.CALLBACK:
            if rule.callback:
                rule.callback(result.message)

    @staticmethod
    def _fire_webhook(url: str, result: ProcessingResult) -> None:
        """POST a JSON payload to the webhook URL."""
        msg = result.message
        payload = json.dumps({
            "event": "email_rule_match",
            "message_id": msg.message_id,
            "subject": msg.subject,
            "sender": str(msg.sender) if msg.sender else "",
            "recipients": [str(r) for r in msg.recipients],
            "date": msg.date.isoformat() if msg.date else "",
            "account": msg.account,
            "mailbox": msg.mailbox,
            "matched_rules": result.matched_rules,
            "tags": result.tags,
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                result.webhook_results.append({
                    "url": url,
                    "status": resp.status,
                    "ok": 200 <= resp.status < 300,
                })
        except Exception as exc:
            logger.warning("Webhook POST to %s failed: %s", url, exc)
            result.webhook_results.append({
                "url": url,
                "status": 0,
                "ok": False,
                "error": str(exc),
            })

    @classmethod
    def from_config(cls, rules_config: list[dict[str, Any]]) -> EmailProcessor:
        processor = cls()
        for rd in rules_config:
            actions = [RuleAction(a) for a in rd.get("actions", [])]
            rule = ProcessingRule(
                name=rd["name"], actions=actions,
                sender_pattern=rd.get("sender_pattern", ""),
                subject_pattern=rd.get("subject_pattern", ""),
                body_pattern=rd.get("body_pattern", ""),
                mailbox=rd.get("mailbox", ""),
                account=rd.get("account", ""),
                has_attachments=rd.get("has_attachments"),
                flag_index=rd.get("flag_index", 0),
                tag=rd.get("tag", ""),
                move_to=rd.get("move_to", ""),
                forward_to=rd.get("forward_to", ""),
                reply_template=rd.get("reply_template", ""),
                webhook_url=rd.get("webhook_url", ""),
                priority=rd.get("priority", 0),
                stop_after_match=rd.get("stop_after_match", False),
            )
            processor.add_rule(rule)
        return processor
