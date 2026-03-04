#!/usr/bin/env python3
"""Decide whether to route an LLM request to a local provider or the cloud.

Usage:
  python3 route_request.py --prompt "..." [--tokens N]
    [--local-available] [--local-provider NAME]
    [--sensitive] [--config PATH]

Output (JSON):
  { "decision": "local"|"cloud", "reason": str, "complexity_score": int,
    "sensitive": bool, "estimated_tokens": int, "local_provider": str|null }

Config file (~/.openclaw/adaptive-routing/config.json) supports:
  { "complexity_threshold": 3, "token_high_watermark": 4000,
    "token_low_watermark": 500, "redact_output": true }
"""
import argparse
import json
import os
import re

# ── Secret redaction (ported from adaptive-routing.ts PR #30185) ─────────────

_SECRET_PATTERNS = [
    (re.compile(r'sk-[A-Za-z0-9_\-]{8,}'), '[REDACTED:sk-key]'),
    (re.compile(r'Bearer\s+[A-Za-z0-9._\-/+]{8,}', re.IGNORECASE), 'Bearer [REDACTED]'),
    (re.compile(
        r'(?:api[_-]?key|apikey|access[_-]?token|secret)[=:]\s*["\']?[A-Za-z0-9._\-/+]{8,}["\']?',
        re.IGNORECASE,
    ), '[REDACTED:api-key]'),
    (re.compile(
        r'eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}'
    ), '[REDACTED:jwt]'),
]


def redact_secrets(text: str) -> str:
    for pattern, replacement in _SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


# ── Config ────────────────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "complexity_threshold": 3,
    "token_high_watermark": 4000,
    "token_low_watermark": 500,
    "redact_output": True,
}

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.openclaw/adaptive-routing/config.json")


def load_config(path: str) -> dict:
    try:
        with open(path) as f:
            user = json.load(f)
        return {**DEFAULT_CONFIG, **user}
    except Exception:
        return DEFAULT_CONFIG


# ── Keyword lists ─────────────────────────────────────────────────────────────

COMPLEX_KEYWORDS = [
    "analyze", "synthesize", "compare", "reason", "architecture",
    "code review", "multi-step", "evaluate", "critique", "refactor",
    "design", "implement", "debug", "strategy",
]
SIMPLE_KEYWORDS = [
    "summarize", "translate", "list", "what is", "define",
    "explain briefly", "convert", "format", "reformat", "spell check",
]
# Any match forces local routing for privacy
SENSITIVE_KEYWORDS = [
    "password", "secret", "private", "confidential", "internal",
    "ssn", "api key", "token", "credential", "salary", "medical",
]


def score_complexity(prompt: str, tokens: int, cfg: dict) -> int:
    lower = prompt.lower()
    score = 0
    for kw in COMPLEX_KEYWORDS:
        if kw in lower:
            score += 2
    for kw in SIMPLE_KEYWORDS:
        if kw in lower:
            score -= 1
    if tokens > cfg["token_high_watermark"]:
        score += 2
    elif tokens < cfg["token_low_watermark"]:
        score -= 1
    return score


def contains_sensitive(prompt: str) -> bool:
    lower = prompt.lower()
    return any(kw in lower for kw in SENSITIVE_KEYWORDS)


# ── CLI ───────────────────────────────────────────────────────────────────────

parser = argparse.ArgumentParser()
parser.add_argument("--prompt", required=True, help="The user prompt text")
parser.add_argument("--tokens", type=int, default=200, help="Estimated token count")
parser.add_argument("--local-available", action="store_true", help="A local provider is running")
parser.add_argument("--local-provider", default="ollama", help="Name of the local provider")
parser.add_argument("--sensitive", action="store_true", help="Force sensitive flag")
parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Path to config JSON")
args = parser.parse_args()

cfg = load_config(args.config)
sensitive = args.sensitive or contains_sensitive(args.prompt)
complexity = score_complexity(args.prompt, args.tokens, cfg)
threshold = cfg["complexity_threshold"]

if not args.local_available:
    decision = "cloud"
    reason = "No local LLM provider is running"
elif sensitive:
    decision = "local"
    reason = "Prompt contains sensitive data — routing locally for privacy"
elif complexity >= threshold:
    decision = "cloud"
    reason = f"High complexity score ({complexity}) — routing to cloud for best results"
else:
    decision = "local"
    reason = f"Simple/moderate request (complexity={complexity}) — local model sufficient"

# Redact the prompt echo in output when sensitive (never log raw credentials)
if cfg.get("redact_output") and sensitive:
    reason = redact_secrets(reason)

print(json.dumps({
    "decision": decision,
    "reason": reason,
    "complexity_score": complexity,
    "complexity_threshold": threshold,
    "sensitive": sensitive,
    "estimated_tokens": args.tokens,
    "local_provider": args.local_provider if decision == "local" else None,
}))
