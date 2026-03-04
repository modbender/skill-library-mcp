#!/usr/bin/env python3
"""Decide whether to route an LLM request to a local provider or the cloud.

Usage:
  python3 route_request.py --prompt "..." [--tokens N]
    [--local-available] [--local-provider NAME] [--sensitive]

Output (JSON):
  { "decision": "local"|"cloud", "reason": str, "complexity_score": int,
    "sensitive": bool, "estimated_tokens": int, "local_provider": str|null }
"""
import argparse
import json

# Keywords that raise/lower complexity score
COMPLEX_KEYWORDS = [
    "analyze", "synthesize", "compare", "reason", "architecture",
    "code review", "multi-step", "evaluate", "critique", "refactor",
    "design", "implement", "debug", "strategy",
]
SIMPLE_KEYWORDS = [
    "summarize", "translate", "list", "what is", "define",
    "explain briefly", "convert", "format", "reformat", "spell check",
]
# Any of these in the prompt forces local routing for privacy
SENSITIVE_KEYWORDS = [
    "password", "secret", "private", "confidential", "internal",
    "ssn", "api key", "token", "credential", "salary", "medical",
]


def score_complexity(prompt: str, tokens: int) -> int:
    lower = prompt.lower()
    score = 0
    for kw in COMPLEX_KEYWORDS:
        if kw in lower:
            score += 2
    for kw in SIMPLE_KEYWORDS:
        if kw in lower:
            score -= 1
    if tokens > 4000:
        score += 2
    elif tokens < 500:
        score -= 1
    return score


def contains_sensitive(prompt: str) -> bool:
    lower = prompt.lower()
    return any(kw in lower for kw in SENSITIVE_KEYWORDS)


parser = argparse.ArgumentParser()
parser.add_argument("--prompt", required=True, help="The user prompt text")
parser.add_argument("--tokens", type=int, default=200, help="Estimated token count")
parser.add_argument("--local-available", action="store_true", help="A local provider is running")
parser.add_argument("--local-provider", default="ollama", help="Name of the local provider")
parser.add_argument("--sensitive", action="store_true", help="Force sensitive flag")
args = parser.parse_args()

sensitive = args.sensitive or contains_sensitive(args.prompt)
complexity = score_complexity(args.prompt, args.tokens)

if not args.local_available:
    decision = "cloud"
    reason = "No local LLM provider is running"
elif sensitive:
    decision = "local"
    reason = "Prompt contains sensitive data — routing locally for privacy"
elif complexity >= 3:
    decision = "cloud"
    reason = f"High complexity score ({complexity}) — routing to cloud for best results"
else:
    decision = "local"
    reason = f"Simple/moderate request (complexity={complexity}) — local model sufficient"

print(json.dumps({
    "decision": decision,
    "reason": reason,
    "complexity_score": complexity,
    "sensitive": sensitive,
    "estimated_tokens": args.tokens,
    "local_provider": args.local_provider if decision == "local" else None,
}))
