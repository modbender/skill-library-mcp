"""Minimal secret redaction for relay output.

Keep it simple: default redaction is intentionally conservative (high-confidence
patterns only) to avoid wrecking readability. Callers can pass strict=True for a
slightly broader pass (e.g., redact --token=... flags).
"""

from __future__ import annotations

import re

REDACT_MARK = "[REDACTED]"

_RE_DISCORD_WEBHOOK = re.compile(
    r"(https?://(?:ptb\.)?discord(?:app)?\.com/api/webhooks/\d+/)([A-Za-z0-9_-]+)",
    re.IGNORECASE,
)
_RE_TELEGRAM_BOT_URL = re.compile(
    r"(https?://api\.telegram\.org/bot)(\d{5,}:[A-Za-z0-9_-]{20,})(/)",
    re.IGNORECASE,
)
_RE_AUTHZ_HEADER = re.compile(
    r"(\bauthorization\s*:\s*(?:bearer|bot|token)\s+)([^\s'\"`]+)",
    re.IGNORECASE,
)
_RE_BEARER_TOKEN = re.compile(r"\bbearer\s+([A-Za-z0-9._-]{20,})", re.IGNORECASE)
_RE_OPENAI_KEY = re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")
_RE_OPENAI_PROJ_KEY = re.compile(r"\bsk-proj-[A-Za-z0-9]{10,}\b")
_RE_GITHUB_TOKEN = re.compile(r"\b(?:ghp|gho|ghs|ghu)_[A-Za-z0-9]{20,}\b")
_RE_GITHUB_PAT = re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")
_RE_SLACK_TOKEN = re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")
_RE_AWS_ACCESS_KEY = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
_RE_PRIVATE_KEY_BLOCK = re.compile(
    r"-----BEGIN (?:[A-Z0-9 ]+)?PRIVATE KEY-----.*?-----END (?:[A-Z0-9 ]+)?PRIVATE KEY-----",
    re.DOTALL,
)
_RE_ENV_ASSIGN_UPPER = re.compile(
    r"\b([A-Z][A-Z0-9_]*?(?:TOKEN|API[_-]?KEY|SECRET|PASSWORD|PASSWD)[A-Z0-9_]*)=([^\s]+)"
)

_RE_FLAG_SECRET = re.compile(
    r"(--(?:token|api[-_]?key|secret|password|passwd)\b)(\s+|=)([^\s]+)",
    re.IGNORECASE,
)


def redact_text(text: str, *, strict: bool = False) -> str:
    if not text:
        return text

    out = text
    out = _RE_PRIVATE_KEY_BLOCK.sub(
        "-----BEGIN PRIVATE KEY-----\n[REDACTED]\n-----END PRIVATE KEY-----", out
    )
    out = _RE_DISCORD_WEBHOOK.sub(r"\1" + REDACT_MARK, out)
    out = _RE_TELEGRAM_BOT_URL.sub(r"\1" + REDACT_MARK + r"\3", out)
    out = _RE_AUTHZ_HEADER.sub(r"\1" + REDACT_MARK, out)
    out = _RE_BEARER_TOKEN.sub("Bearer " + REDACT_MARK, out)
    out = _RE_ENV_ASSIGN_UPPER.sub(r"\1=" + REDACT_MARK, out)
    out = _RE_OPENAI_PROJ_KEY.sub(REDACT_MARK, out)
    out = _RE_OPENAI_KEY.sub(REDACT_MARK, out)
    out = _RE_GITHUB_PAT.sub(REDACT_MARK, out)
    out = _RE_GITHUB_TOKEN.sub(REDACT_MARK, out)
    out = _RE_SLACK_TOKEN.sub(REDACT_MARK, out)
    out = _RE_AWS_ACCESS_KEY.sub(REDACT_MARK, out)

    if strict:
        out = _RE_FLAG_SECRET.sub(r"\1\2" + REDACT_MARK, out)

    return out

