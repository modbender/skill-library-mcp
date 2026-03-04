"""Internal shared utilities for parsing lightweight LLM and string helpers."""

from __future__ import annotations

import json
import re


_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.S)
_WORD_RE = re.compile(r"[A-Za-z0-9']+")


def _extract_json(raw: str) -> dict | list | str | None:
    """Extract JSON from raw model output."""
    text = (raw or "").strip()
    if not text:
        return None

    if text.startswith("```") and text.endswith("```"):
        text = "\n".join(text.splitlines()[1:-1]).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = _JSON_OBJECT_RE.search(text)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _first_line(text: str) -> str:
    """Return the first non-empty line."""
    return (text.splitlines() or [""])[0]


def _tokenize(text: str) -> set[str]:
    """Extract normalized tokens from text."""
    return {match.group(0).lower() for match in _WORD_RE.finditer(text or "")}
