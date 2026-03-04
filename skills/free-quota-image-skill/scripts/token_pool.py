#!/usr/bin/env python3
"""Token pool management with provider-aware daily reset rules."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

PROVIDER_RESET_RULE = {
    "huggingface": "utc",
    "a4f": "utc",
    "gitee": "beijing",
    "modelscope": "beijing",
}

QUOTA_SIGNATURES = (
    "429",
    "quota",
    "credit",
    "insufficient_quota",
    "you have exceeded your free gpu quota",
    "arrearage",
)

AUTH_SIGNATURES = (
    "401",
    "403",
    "unauthorized",
    "forbidden",
    "invalid token",
    "authentication",
)


@dataclass
class TokenAttempt:
    token: Optional[str]
    label: str


class TokenPool:
    def __init__(self, state_file: Path, providers_config: Dict[str, Dict[str, object]]) -> None:
        self.state_file = state_file.expanduser()
        self.providers_config = providers_config
        self._state = self._load_state()

    def tokens_for(self, provider: str) -> List[str]:
        cfg = self.providers_config.get(provider, {})
        raw = cfg.get("tokens", [])
        tokens = _normalize_tokens(raw)
        return _dedupe(tokens)

    def available_attempts(self, provider: str, allow_public: bool = False) -> List[TokenAttempt]:
        self._reset_if_new_day(provider)
        exhausted = self._state.setdefault(provider, {}).setdefault("exhausted", {})

        attempts: List[TokenAttempt] = []
        tokens = self.tokens_for(provider)
        for index, token in enumerate(tokens, start=1):
            if exhausted.get(token):
                continue
            attempts.append(TokenAttempt(token=token, label=f"token{index}"))

        if not attempts and allow_public:
            attempts.append(TokenAttempt(token=None, label="public"))

        return attempts

    def mark_exhausted(self, provider: str, token: Optional[str]) -> None:
        if not token:
            return
        self._reset_if_new_day(provider)
        provider_state = self._state.setdefault(provider, {})
        exhausted = provider_state.setdefault("exhausted", {})
        exhausted[token] = True
        self._save_state()

    def _date_for_provider(self, provider: str) -> str:
        rule = PROVIDER_RESET_RULE.get(provider, "utc")
        now_utc = datetime.now(timezone.utc)
        if rule == "beijing":
            beijing = now_utc + timedelta(hours=8)
            return beijing.strftime("%Y-%m-%d")
        return now_utc.strftime("%Y-%m-%d")

    def _reset_if_new_day(self, provider: str) -> None:
        today = self._date_for_provider(provider)
        provider_state = self._state.setdefault(provider, {})
        if provider_state.get("date") == today:
            return
        provider_state["date"] = today
        provider_state["exhausted"] = {}
        self._save_state()

    def _load_state(self) -> Dict[str, Dict[str, object]]:
        if not self.state_file.exists():
            return {}
        try:
            data = json.loads(self.state_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        if not isinstance(data, dict):
            return {}
        return data

    def _save_state(self) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(self._state, indent=2, ensure_ascii=True), encoding="utf-8")


def _normalize_tokens(raw: object) -> List[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        return [token.strip() for token in raw.split(",") if token.strip()]
    if isinstance(raw, list):
        normalized: List[str] = []
        for item in raw:
            if not isinstance(item, str):
                continue
            parts = [part.strip() for part in item.split(",")]
            normalized.extend([part for part in parts if part])
        return normalized
    return []


def _dedupe(values: Iterable[str]) -> List[str]:
    seen = set()
    output: List[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        output.append(value)
    return output


def classify_error(message: str, status_code: Optional[int] = None) -> str:
    msg = (message or "").lower()
    if status_code in (401, 403):
        return "auth"
    if status_code == 429:
        return "quota"

    if any(signature in msg for signature in QUOTA_SIGNATURES):
        return "quota"
    if any(signature in msg for signature in AUTH_SIGNATURES):
        return "auth"
    if "timeout" in msg or "connection" in msg or "network" in msg:
        return "network"
    return "provider"
