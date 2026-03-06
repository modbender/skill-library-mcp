from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class TaskComplexity:
    simple: bool
    creative: bool
    long_form: bool
    technical: bool


def analyze_task(text: str) -> TaskComplexity:
    t = (text or "").lower()
    simple = bool(re.search(r"\b(summarize|list|check|search|status|heartbeat)\b", t))
    creative = bool(re.search(r"\b(write|create|generate|design|draft|publish)\b", t))
    long_form = "article" in t or "2000+" in t or "long form" in t
    technical = bool(re.search(r"\b(code|debug|analyze|parse|script|automation|json)\b", t))
    return TaskComplexity(simple=simple, creative=creative, long_form=long_form, technical=technical)


def select_optimal_model(task_text: str, context_tokens: int, prefs: dict[str, str]) -> str:
    c = analyze_task(task_text)
    if c.simple and context_tokens < 50_000:
        return prefs.get("simple", "anthropic/claude-3-5-sonnet-latest")
    if c.creative or c.long_form:
        return prefs.get("complex", "anthropic/claude-opus-4-6")
    return prefs.get("balanced", "anthropic/claude-sonnet-4-20250514")
