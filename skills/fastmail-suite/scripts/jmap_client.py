#!/usr/bin/env python3
"""Minimal, safe-by-default JMAP client for Fastmail.

- No external deps (stdlib only)
- Redaction ON by default (FASTMAIL_REDACT=1)
- Write operations require FASTMAIL_ENABLE_WRITES=1 and (optionally) separate token

Env:
  FASTMAIL_TOKEN            (required for read ops)
  FASTMAIL_TOKEN_SEND       (optional; used for send if set)
  FASTMAIL_ENABLE_WRITES    (set to 1 to allow write ops)
  FASTMAIL_REDACT           (default: 1)
  FASTMAIL_MAX_BODY_BYTES   (default: 5000)
  FASTMAIL_BASE_URL         (default: https://api.fastmail.com)
  FASTMAIL_ACCOUNT_ID       (optional; else first account from session)

Identity env (for sending):
  FASTMAIL_IDENTITY_ID      (preferred)
  FASTMAIL_IDENTITY_EMAIL   (pick identity matching email)

This module is intended to be imported by other scripts in this skill.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_BASE_URL = "https://api.fastmail.com"
JMAP_API_PATH = "/jmap/api/"
JMAP_SESSION_PATH = "/jmap/session"

USING_CORE_MAIL = ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"]
USING_CORE_MAIL_SEND = [
    "urn:ietf:params:jmap:core",
    "urn:ietf:params:jmap:mail",
    "urn:ietf:params:jmap:submission",
]


class FastmailError(RuntimeError):
    pass


def _env_flag(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


def redact_text(text: str) -> str:
    """Best-effort redaction for display/logging (emails, phone-ish numbers)."""
    if not text:
        return text

    # emails: keep domain, mask local part
    def _mask_email(m: re.Match) -> str:
        local = m.group(1)
        domain = m.group(2)
        if len(local) <= 2:
            masked = "*" * len(local)
        else:
            masked = local[0] + "*" * (len(local) - 2) + local[-1]
        return f"{masked}@{domain}"

    text = re.sub(r"\b([A-Za-z0-9._%+-]{1,64})@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b", _mask_email, text)

    # phone-ish: sequences of 8+ digits possibly separated by spaces/dashes
    text = re.sub(r"\b(?:\+?\d[\d\s\-()]{7,}\d)\b", "[REDACTED_PHONE]", text)

    return text


def safe_print(obj: Any, *, raw: bool = False) -> None:
    s = obj if isinstance(obj, str) else json.dumps(obj, indent=2, ensure_ascii=False)
    if not raw and _env_flag("FASTMAIL_REDACT", True):
        s = redact_text(s)
    print(s)


@dataclass
class JmapSession:
    api_url: str
    account_id: str


class FastmailJMAP:
    def __init__(self, token: str, *, base_url: Optional[str] = None, account_id: Optional[str] = None):
        self.token = token
        self.base_url = (base_url or os.environ.get("FASTMAIL_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self._account_id_override = account_id or os.environ.get("FASTMAIL_ACCOUNT_ID")
        self._session: Optional[JmapSession] = None

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def session(self) -> JmapSession:
        if self._session:
            return self._session

        url = self.base_url + JMAP_SESSION_PATH
        req = urllib.request.Request(url, headers=self._headers())
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read())
        except Exception as e:
            raise FastmailError(f"Failed to fetch JMAP session: {e}")

        api_url = data.get("apiUrl")
        if not api_url:
            raise FastmailError("JMAP session response missing apiUrl")

        if self._account_id_override:
            account_id = self._account_id_override
        else:
            accounts = data.get("accounts") or {}
            if not accounts:
                raise FastmailError("JMAP session response has no accounts")
            account_id = list(accounts.keys())[0]

        self._session = JmapSession(api_url=api_url, account_id=account_id)
        return self._session

    def call(self, method_calls: List[list], *, using: Optional[List[str]] = None) -> Dict[str, Any]:
        sess = self.session()
        for mc in method_calls:
            if isinstance(mc, list) and len(mc) >= 2 and isinstance(mc[1], dict):
                if mc[1].get("accountId") is None:
                    mc[1]["accountId"] = sess.account_id

        body = json.dumps({"using": using or USING_CORE_MAIL, "methodCalls": method_calls}).encode()
        req = urllib.request.Request(sess.api_url, data=body, headers=self._headers(), method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                resp = json.loads(r.read())
        except Exception as e:
            raise FastmailError(f"JMAP call failed: {e}")

        # Raise on JMAP-level error responses
        for mr in resp.get("methodResponses", []) or []:
            if mr and mr[0] == "error":
                err = mr[1] or {}
                t = err.get("type", "unknown")
                desc = err.get("description", "")
                raise FastmailError(f"JMAP error: {t} {desc}".strip())

        return resp

    def mailbox_map(self) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str]]:
        resp = self.call([
            ["Mailbox/get", {"accountId": None, "properties": ["name", "role", "parentId"]}, "mb"],
        ])
        by_name: Dict[str, str] = {}
        by_role: Dict[str, str] = {}
        by_id: Dict[str, str] = {}
        lst = resp["methodResponses"][0][1].get("list") or []
        for mb in lst:
            name = (mb.get("name") or "").lower()
            if name:
                by_name[name] = mb["id"]
            if mb.get("role"):
                by_role[mb["role"]] = mb["id"]
            by_id[mb["id"]] = mb.get("name") or mb["id"]
        return by_name, by_role, by_id

    def require_writes_enabled(self) -> None:
        if not _env_flag("FASTMAIL_ENABLE_WRITES", False):
            raise FastmailError("Write operation blocked. Set FASTMAIL_ENABLE_WRITES=1 to enable.")


def get_required_env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        raise FastmailError(
            f"Missing env var {name}.\n"
            "For Fastmail tokens: https://app.fastmail.com/settings/security/tokens"
        )
    return v


def exit_with_error(e: Exception) -> None:
    msg = str(e)
    if _env_flag("FASTMAIL_REDACT", True):
        msg = redact_text(msg)
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)
