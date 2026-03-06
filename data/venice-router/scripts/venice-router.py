#!/usr/bin/env python3
"""
Venice.ai Supreme Router — cost-optimized model routing for OpenClaw.

Classifies prompt complexity and routes to the cheapest Venice.ai model
that can handle the task adequately. Supports streaming, tier overrides,
direct model selection, web search, uncensored/private-only modes,
conversation-aware routing, cost budgets, and function calling.

Venice.ai is the AI platform for privacy and freedom — zero data retention
on private models, no content filters, no refusals. OpenAI-compatible API.

Usage:
    python3 venice-router.py --prompt "your question here"
    python3 venice-router.py --tier mid --prompt "explain recursion"
    python3 venice-router.py --stream --prompt "write a story"
    python3 venice-router.py --web-search --prompt "latest news on X"
    python3 venice-router.py --uncensored --prompt "creative fiction prompt"
    python3 venice-router.py --private-only --prompt "sensitive data query"
    python3 venice-router.py --conversation history.json --prompt "follow up"
    python3 venice-router.py --tools tools.json --prompt "get weather in NYC"
    python3 venice-router.py --budget-status
    python3 venice-router.py --classify "your question"
    python3 venice-router.py --list-models
"""

import argparse
import json
import os
import re
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ── Venice.ai API ────────────────────────────────────────────────────────────

VENICE_API_BASE = "https://api.venice.ai/api/v1"

# ── Model Tiers (sorted cheapest → most expensive) ──────────────────────────
# Prices per 1M tokens [input_usd, output_usd]

MODEL_TIERS = {
    "cheap": {
        "description": "Simple Q&A, greetings, math, lookups",
        "models": [
            {"id": "qwen3-4b",            "name": "Venice Small",        "input": 0.05,  "output": 0.15,  "ctx": 32000,   "private": True,  "uncensored": False},
            {"id": "openai-gpt-oss-120b",  "name": "GPT OSS 120B",       "input": 0.07,  "output": 0.30,  "ctx": 128000,  "private": True,  "uncensored": False},
            {"id": "zai-org-glm-4.7-flash","name": "GLM 4.7 Flash",      "input": 0.13,  "output": 0.50,  "ctx": 128000,  "private": True,  "uncensored": False},
            {"id": "llama-3.2-3b",         "name": "Llama 3.2 3B",        "input": 0.15,  "output": 0.60,  "ctx": 128000,  "private": True,  "uncensored": False},
        ],
        "default": "qwen3-4b",
    },
    "budget": {
        "description": "Moderate questions, summaries, translations",
        "models": [
            {"id": "olafangensan-glm-4.7-flash-heretic", "name": "GLM 4.7 Flash Heretic", "input": 0.14, "output": 0.80, "ctx": 128000, "private": True, "uncensored": True},
            {"id": "qwen3-235b-a22b-instruct-2507", "name": "Qwen 3 235B",  "input": 0.15,  "output": 0.75,  "ctx": 128000,  "private": True,  "uncensored": False},
            {"id": "venice-uncensored",    "name": "Venice Uncensored",   "input": 0.20,  "output": 0.90,  "ctx": 32000,   "private": True,  "uncensored": True},
            {"id": "qwen3-vl-235b-a22b",   "name": "Qwen3 VL 235B",      "input": 0.25,  "output": 1.50,  "ctx": 256000,  "private": True,  "uncensored": False},
        ],
        "default": "qwen3-235b-a22b-instruct-2507",
    },
    "budget-medium": {
        "description": "Moderate-to-complex tasks, code snippets, structured output",
        "models": [
            {"id": "grok-code-fast-1",     "name": "Grok Code Fast",     "input": 0.25,  "output": 1.87,  "ctx": 256000,  "private": False, "uncensored": False},
            {"id": "deepseek-v3.2",        "name": "DeepSeek V3.2",      "input": 0.40,  "output": 1.00,  "ctx": 160000,  "private": True,  "uncensored": False},
            {"id": "minimax-m21",          "name": "MiniMax M2.1",       "input": 0.40,  "output": 1.60,  "ctx": 198000,  "private": True,  "uncensored": False},
        ],
        "default": "deepseek-v3.2",
    },
    "mid": {
        "description": "Code generation, analysis, longer writing, chain-of-thought reasoning",
        "models": [
            {"id": "grok-code-fast-1",                    "name": "Grok Code Fast",         "input": 0.25,  "output": 1.87,  "ctx": 256000,  "private": False, "uncensored": False, "thinking": False},
            {"id": "deepseek-v3.2",                       "name": "DeepSeek V3.2",          "input": 0.40,  "output": 1.00,  "ctx": 160000,  "private": True,  "uncensored": False, "thinking": False},
            {"id": "minimax-m21",                         "name": "MiniMax M2.1",           "input": 0.40,  "output": 1.60,  "ctx": 198000,  "private": True,  "uncensored": False, "thinking": False},
            {"id": "minimax-m25",                         "name": "MiniMax M2.5",           "input": 0.40,  "output": 1.60,  "ctx": 198000,  "private": True,  "uncensored": False, "thinking": False},
            {"id": "qwen3-next-80b",                      "name": "Qwen 3 Next 80B",       "input": 0.35,  "output": 1.90,  "ctx": 256000,  "private": True,  "uncensored": False, "thinking": False},
            {"id": "qwen3-235b-a22b-thinking-2507",       "name": "Qwen3 235B Thinking",   "input": 0.45,  "output": 3.50,  "ctx": 128000,  "private": True,  "uncensored": False, "thinking": True},
            {"id": "mistral-31-24b",                      "name": "Venice Medium",          "input": 0.50,  "output": 2.00,  "ctx": 128000,  "private": True,  "uncensored": False, "thinking": False},
            {"id": "llama-3.3-70b",                       "name": "Llama 3.3 70B",          "input": 0.70,  "output": 2.80,  "ctx": 128000,  "private": True,  "uncensored": False, "thinking": False},
        ],
        "default": "deepseek-v3.2",
    },
    "high": {
        "description": "Complex reasoning, multi-step tasks, code review, function-calling specialists",
        "models": [
            {"id": "grok-41-fast",                         "name": "Grok 4.1 Fast",          "input": 0.50,  "output": 1.25,  "ctx": 256000,  "private": False, "uncensored": False, "thinking": False},
            {"id": "zai-org-glm-4.7",                      "name": "GLM 4.7",                "input": 0.55,  "output": 2.65,  "ctx": 198000,  "private": True,  "uncensored": False, "thinking": False},
            {"id": "gemini-3-flash-preview",               "name": "Gemini 3 Flash",         "input": 0.70,  "output": 3.75,  "ctx": 256000,  "private": False, "uncensored": False, "thinking": False},
            {"id": "kimi-k2-thinking",                    "name": "Kimi K2 Thinking",       "input": 0.75,  "output": 3.20,  "ctx": 256000,  "private": True,  "uncensored": False, "thinking": True},
            {"id": "kimi-k2-5",                           "name": "Kimi K2.5",              "input": 0.75,  "output": 3.75,  "ctx": 256000,  "private": True,  "uncensored": False, "thinking": True},
            {"id": "qwen3-coder-480b-a35b-instruct",      "name": "Qwen 3 Coder 480B",     "input": 0.75,  "output": 3.00,  "ctx": 256000,  "private": True,  "uncensored": False, "thinking": False},
            {"id": "hermes-3-llama-3.1-405b",             "name": "Hermes 3 405B",          "input": 1.10,  "output": 3.00,  "ctx": 128000,  "private": True,  "uncensored": False, "thinking": False},
            {"id": "zai-org-glm-5",                       "name": "GLM 5",                  "input": 1.00,  "output": 3.20,  "ctx": 198000,  "private": True,  "uncensored": False, "thinking": False},
        ],
        "default": "kimi-k2-thinking",
    },
    "premium": {
        "description": "Expert-level analysis, architecture, research, 1M-context tasks",
        "models": [
            {"id": "openai-gpt-52",         "name": "GPT-5.2",            "input": 2.19,  "output": 17.50, "ctx": 256000,  "private": False, "uncensored": False, "thinking": False},
            {"id": "openai-gpt-52-codex",   "name": "GPT-5.2 Codex",     "input": 2.19,  "output": 17.50, "ctx": 256000,  "private": False, "uncensored": False, "thinking": False},
            {"id": "gemini-3-pro-preview",  "name": "Gemini 3 Pro",      "input": 2.50,  "output": 15.00, "ctx": 198000,  "private": False, "uncensored": False, "thinking": False},
            {"id": "gemini-3-1-pro-preview","name": "Gemini 3.1 Pro",    "input": 2.50,  "output": 15.00, "ctx": 1000000, "private": False, "uncensored": False, "thinking": False},
            {"id": "claude-sonnet-4-6",     "name": "Claude Sonnet 4.6", "input": 3.75,  "output": 18.75, "ctx": 1000000, "private": False, "uncensored": False, "thinking": False},
            {"id": "claude-sonnet-45",      "name": "Claude Sonnet 4.5", "input": 3.75,  "output": 18.75, "ctx": 198000,  "private": False, "uncensored": False, "thinking": False},
            {"id": "claude-opus-45",        "name": "Claude Opus 4.5",   "input": 6.00,  "output": 30.00, "ctx": 198000,  "private": False, "uncensored": False, "thinking": False},
            {"id": "claude-opus-4-6",       "name": "Claude Opus 4.6",   "input": 6.00,  "output": 30.00, "ctx": 1000000, "private": False, "uncensored": False, "thinking": False},
        ],
        "default": "gemini-3-pro-preview",
    },
}

TIER_ORDER = ["cheap", "budget", "budget-medium", "mid", "high", "premium"]

# ── Complexity Classifier ────────────────────────────────────────────────────

# Patterns that indicate higher complexity
PREMIUM_PATTERNS = [
    r"\b(architect(ure)?s?|design\s+pattern|system\s+design|distributed\s+system)\b",
    r"\b(research\s+paper|academic|peer.review|hypothesis|theorem)\b",
    r"\b(security\s+audit|penetration\s+test|vulnerability\s+assess)\b",
    r"\b(optimize|refactor)\s+(the\s+)?(entire|whole|complete|full)\b",
    r"\b(compare\s+and\s+contrast|comprehensive\s+analysis)\b",
    r"\b(write|design|create|build|implement)\s+(a\s+)?(complete|full|production|entire|comprehensive)\b",
    r"\bprove\s+(that|why|mathematically)\b",
    r"\b(formal\s+verification|type\s+theory|category\s+theory)\b",
    r"\b(machine\s+learning|deep\s+learning|neural\s+network|transformer)\b",
    r"\b(business\s+plan|go.to.market|competitive\s+analysis)\b",
    r"\b(event\s+sourc|cqrs|saga\s+pattern|domain.driven|hexagonal)\b",
    r"\b(microservices?|distributed)\b.*\b(architect|design|scal|pattern)\b",
    r"\b(horizontal|vertical)\s+scal\b",
    r"\b(real.time).*(platform|system|architect|infra)\b",
]

HIGH_PATTERNS = [
    r"\b(explain|describe)\s+(in\s+detail|thoroughly|step.by.step)\b",
    r"\b(debug|fix|troubleshoot|diagnose)\b",
    r"\b(review|analyze|evaluate|assess|critique)\b",
    r"\b(code\s+review|pull\s+request|merge\s+request)\b",
    r"\b(algorithm|data\s+structure|complexity|big.?o)\b",
    r"\b(api|endpoint|microservices?|database\s+schema)\b",
    r"\b(deploy|ci.?cd|docker|kubernetes|infrastructure)\b",
    r"\b(test|unit\s+test|integration\s+test|e2e)\b",
    r"\b(regex|regular\s+expression)\b",
    r"\b(concurren(t|cy)|parallel|async(hronous)?|thread)\b",
    r"\bwrite\s+(a\s+)?(function|class|module|script|program)\b",
    r"\b(typescript|python|rust|golang|javascript|java|c\+\+|swift)\b.*\b(implement|write|create|build)\b",
    r"\b(implement|build|create)\s+(a|an)\s+\w+\s+(in|using|with)\b",
    r"\b(pros?\s+and\s+cons?|trade.?offs?|advantages?\s+and\s+disadvantages?)\b",
]

MID_PATTERNS = [
    r"\b(explain|describe|summarize|outline)\b",
    r"\b(how\s+(do|does|to|can|would))\b",
    r"\b(what\s+(is|are|does|do)\s+the\s+difference)\b",
    r"\b(convert|transform|translate|format)\b",
    r"\b(list|enumerate|give\s+me|provide)\s+\d+\b",
    r"\b(write|draft|compose)\s+(a|an)\s+(email|letter|message|blog|article)\b",
    r"\b(code|script|function|snippet)\b",
    r"\bexample(s)?\s+(of|for)\b",
    r"\b(compare|versus|vs\.?)\b",
    r"\b(why|how\s+come|what\s+causes)\b",
]

CHEAP_PATTERNS = [
    r"^(hi|hello|hey|yo|sup|greetings|good\s+(morning|afternoon|evening))[\s!?.]*$",
    r"^(thanks?|thank\s+you|thx|ty|cheers)[\s!?.]*$",
    r"^(yes|no|ok(ay)?|sure|nope|yep|yup|nah)[\s!?.]*$",
    r"^(what\s+time|what\s+day|what\s+date)\b",
    r"^\d+\s*[\+\-\*\/\%\^]\s*\d+\s*[=?]?\s*$",
    r"^(who\s+(is|was|are))\s+\w+[\s\w]*\??\s*$",
    r"^(define|meaning\s+of|what\s+does\s+\w+\s+mean)\b",
    r"^(translate|say)\s+.{1,50}\s+(in|to)\s+\w+\s*\??\s*$",
    r"^.{1,30}$",  # Very short queries
]


def classify_complexity(prompt: str) -> str:
    """Classify prompt complexity into a tier name."""
    prompt_lower = prompt.strip().lower()
    prompt_len = len(prompt)

    # ── Check for trivial / cheap patterns first ─────────────────────────
    # But skip the short-text catch-all if the prompt has complex keywords
    has_complex_signal = any(
        re.search(p, prompt_lower, re.IGNORECASE)
        for p in PREMIUM_PATTERNS + HIGH_PATTERNS
    )
    if not has_complex_signal:
        for pattern in CHEAP_PATTERNS:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                return "cheap"

    # ── Score-based classification ───────────────────────────────────────
    score = 0

    # Length heuristic
    if prompt_len > 1000:
        score += 3
    elif prompt_len > 500:
        score += 2
    elif prompt_len > 200:
        score += 1
    elif prompt_len < 50:
        score -= 1

    # Code block detection
    if "```" in prompt:
        score += 2
    if re.search(r"(def |class |function |const |let |var |import |from )", prompt):
        score += 1

    # Multi-step instructions
    bullet_count = len(re.findall(r"^\s*[-*\d+\.]\s", prompt, re.MULTILINE))
    if bullet_count >= 5:
        score += 2
    elif bullet_count >= 3:
        score += 1

    # Question complexity (multiple questions = higher complexity)
    question_marks = prompt.count("?")
    if question_marks >= 3:
        score += 2
    elif question_marks >= 2:
        score += 1

    # Premium pattern matching (accumulate — multiple premium signals = stronger)
    premium_matches = 0
    for pattern in PREMIUM_PATTERNS:
        if re.search(pattern, prompt_lower, re.IGNORECASE):
            premium_matches += 1
    if premium_matches >= 2:
        score += 5
    elif premium_matches == 1:
        score += 3

    # High pattern matching
    high_matches = 0
    for pattern in HIGH_PATTERNS:
        if re.search(pattern, prompt_lower, re.IGNORECASE):
            high_matches += 1
    score += min(high_matches, 3)

    # Mid pattern matching
    mid_matches = 0
    for pattern in MID_PATTERNS:
        if re.search(pattern, prompt_lower, re.IGNORECASE):
            mid_matches += 1
    if mid_matches > 0 and score < 2:
        score += 1

    # ── Map score to tier ────────────────────────────────────────────────
    if score >= 6:
        return "premium"
    elif score >= 4:
        return "high"
    elif score >= 3:
        return "mid"
    elif score >= 2:
        return "budget-medium"
    elif score >= 1:
        return "budget"
    else:
        return "cheap"


def get_effective_tier(classified_tier: str, max_tier: str | None = None) -> str:
    """Apply max_tier cap if configured."""
    if max_tier and max_tier in TIER_ORDER:
        max_idx = TIER_ORDER.index(max_tier)
        classified_idx = TIER_ORDER.index(classified_tier)
        if classified_idx > max_idx:
            return max_tier
    return classified_tier


def _tier_has_matching_model(tier: str, prefer_uncensored: bool, private_only: bool) -> bool:
    """Check if a tier has models matching the given constraints."""
    models = MODEL_TIERS[tier]["models"]
    candidates = models
    if private_only:
        candidates = [m for m in candidates if m.get("private", False)]
    if prefer_uncensored:
        candidates = [m for m in candidates if m.get("uncensored", False)]
    return len(candidates) > 0


def find_tier_with_uncensored(starting_tier: str, max_tier: str | None = None, private_only: bool = False) -> str:
    """Find the lowest tier at or above starting_tier that has uncensored models."""
    start_idx = TIER_ORDER.index(starting_tier)
    max_idx = TIER_ORDER.index(max_tier) if max_tier and max_tier in TIER_ORDER else len(TIER_ORDER) - 1
    # Search upward from the classified tier
    for i in range(start_idx, max_idx + 1):
        if _tier_has_matching_model(TIER_ORDER[i], prefer_uncensored=True, private_only=private_only):
            return TIER_ORDER[i]
    # If nothing found, search downward
    for i in range(start_idx - 1, -1, -1):
        if _tier_has_matching_model(TIER_ORDER[i], prefer_uncensored=True, private_only=private_only):
            return TIER_ORDER[i]
    # No uncensored models anywhere, return original tier
    return starting_tier


def find_tier_with_thinking(starting_tier: str, max_tier: str | None = None) -> str:
    """Find the lowest tier at or above starting_tier that has thinking/reasoning models."""
    start_idx = TIER_ORDER.index(starting_tier)
    max_idx = TIER_ORDER.index(max_tier) if max_tier and max_tier in TIER_ORDER else len(TIER_ORDER) - 1
    for i in range(start_idx, max_idx + 1):
        models = MODEL_TIERS[TIER_ORDER[i]]["models"]
        if any(m.get("thinking", False) for m in models):
            return TIER_ORDER[i]
    # Thinking models start at "mid" — if starting_tier is below mid, default to mid
    mid_idx = TIER_ORDER.index("mid")
    if start_idx < mid_idx:
        return "mid"
    return starting_tier


def select_model(tier: str, prefer_private: bool = True, prefer_uncensored: bool = False, private_only: bool = False, prefer_thinking: bool = False) -> dict:
    """Select the best model from a tier with privacy/uncensored/thinking preferences.

    Priority when prefer_thinking=True:
      1. thinking + private models
      2. thinking models (any)
      3. fall back to normal selection

    Priority when prefer_uncensored=True:
      1. uncensored + private models
      2. uncensored models (any)
      3. fall back to normal selection

    When private_only=True, only private (zero data retention) models are considered.
    """
    tier_data = MODEL_TIERS[tier]
    models = tier_data["models"]

    # Apply private_only filter
    if private_only:
        candidates = [m for m in models if m.get("private", False)]
        if not candidates:
            # Fall back to all models if no private ones in this tier
            candidates = models
    else:
        candidates = models

    # Prefer thinking/reasoning models
    if prefer_thinking:
        thinking_private = [m for m in candidates if m.get("thinking", False) and m.get("private", False)]
        if thinking_private:
            return thinking_private[0]
        thinking_any = [m for m in candidates if m.get("thinking", False)]
        if thinking_any:
            return thinking_any[0]

    # Prefer uncensored models
    if prefer_uncensored:
        uncensored_private = [m for m in candidates if m.get("uncensored", False) and m.get("private", False)]
        if uncensored_private:
            return uncensored_private[0]
        uncensored_any = [m for m in candidates if m.get("uncensored", False)]
        if uncensored_any:
            return uncensored_any[0]

    # Prefer private models
    if prefer_private:
        private_models = [m for m in candidates if m.get("private", False)]
        if private_models:
            return private_models[0]

    return candidates[0]


# ── Conversation-Aware Routing ───────────────────────────────────────────────

def classify_with_conversation(messages: list[dict]) -> str:
    """Classify complexity considering full conversation history.

    Analyzes the latest user message in context of the conversation:
    - Short follow-ups after complex exchanges stay at the conversation's tier
    - Trivial messages (thanks, ok, yes) downgrade to cheap
    - New complex topics in a simple conversation escalate appropriately
    - Code blocks or tool results in history boost the tier
    """
    if not messages:
        return "budget"

    # Get the latest user message
    user_messages = [m for m in messages if m.get("role") == "user"]
    if not user_messages:
        return "budget"

    latest = user_messages[-1].get("content", "")
    latest_tier = classify_complexity(latest)

    # If only one message, just use single-prompt classification
    if len(user_messages) <= 1:
        return latest_tier

    # ── Conversation context signals ─────────────────────────────────
    conv_score = 0

    # Check if the conversation has had complex exchanges
    all_content = " ".join(m.get("content", "") for m in messages if m.get("content"))

    # Code in conversation history
    if "```" in all_content:
        conv_score += 1

    # Tool/function calls in history indicate complex workflow
    has_tool_calls = any(
        m.get("role") == "assistant" and m.get("tool_calls")
        for m in messages
    )
    has_tool_results = any(m.get("role") == "tool" for m in messages)
    if has_tool_calls or has_tool_results:
        conv_score += 2

    # Long conversation = likely complex topic
    if len(messages) >= 10:
        conv_score += 1
    elif len(messages) >= 6:
        conv_score += 0  # neutral

    # Previous assistant responses were long (complex discussion)
    assistant_msgs = [m for m in messages if m.get("role") == "assistant"]
    if assistant_msgs:
        avg_len = sum(len(m.get("content", "")) for m in assistant_msgs) / len(assistant_msgs)
        if avg_len > 1000:
            conv_score += 1

    # ── Latest message analysis ──────────────────────────────────────
    latest_lower = latest.strip().lower()

    # Trivial follow-ups → downgrade regardless of history
    trivial_patterns = [
        r"^(thanks?|thank\s+you|thx|ty|cheers|great|perfect|awesome|got\s+it)[\s!?.]*$",
        r"^(yes|no|ok(ay)?|sure|nope|yep|yup|nah|k|kk)[\s!?.]*$",
        r"^(bye|goodbye|see\s+you|later|done|quit|exit)[\s!?.]*$",
    ]
    for pattern in trivial_patterns:
        if re.search(pattern, latest_lower, re.IGNORECASE):
            return "cheap"

    # Short follow-up in a complex conversation → maintain conversation tier
    # "can you also add error handling?" after a coding discussion
    if len(latest) < 100 and conv_score >= 1:
        # Keep at least the conversation's complexity level
        conv_tier_idx = min(conv_score, len(TIER_ORDER) - 1)
        conv_tier = TIER_ORDER[conv_tier_idx]
        latest_tier_idx = TIER_ORDER.index(latest_tier)
        # Use the higher of conversation context or latest classification
        return TIER_ORDER[max(conv_tier_idx, latest_tier_idx)]

    # Default: classify latest message, but bump up if conversation is complex
    latest_tier_idx = TIER_ORDER.index(latest_tier)
    if conv_score >= 2 and latest_tier_idx < 2:  # bump at least to mid
        return TIER_ORDER[max(latest_tier_idx, 2)]
    elif conv_score >= 1 and latest_tier_idx < 1:  # bump at least to budget
        return TIER_ORDER[max(latest_tier_idx, 1)]

    return latest_tier


# ── Cost Budget Tracker ──────────────────────────────────────────────────────

COST_TRACKING_DIR = Path(os.environ.get(
    "VENICE_COST_DIR",
    os.path.join(os.environ.get("HOME", "/tmp"), ".venice-router", "costs")
))


def _ensure_cost_dir():
    """Create cost tracking directory if needed."""
    COST_TRACKING_DIR.mkdir(parents=True, exist_ok=True)


def _cost_file_path(scope: str = "daily", session_id: str | None = None) -> Path:
    """Get the cost tracking file path for the given scope."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if scope == "daily":
        return COST_TRACKING_DIR / f"cost-{today}.json"
    elif scope == "session":
        sid = session_id or os.environ.get("VENICE_SESSION_ID", str(os.getppid()))
        session_hash = hashlib.md5(f"{today}-{sid}".encode()).hexdigest()[:8]
        return COST_TRACKING_DIR / f"session-{session_hash}.json"
    return COST_TRACKING_DIR / f"cost-{today}.json"


def _load_cost_data(scope: str = "daily", session_id: str | None = None) -> dict:
    """Load cost data from file."""
    path = _cost_file_path(scope, session_id=session_id)
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "total_cost_usd": 0.0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "calls": 0,
        "by_tier": {},
        "by_model": {},
    }


def _save_cost_data(data: dict, scope: str = "daily", session_id: str | None = None):
    """Save cost data to file."""
    _ensure_cost_dir()
    path = _cost_file_path(scope, session_id=session_id)
    path.write_text(json.dumps(data, indent=2))


def record_cost(model_info: dict, input_tokens: int, output_tokens: int, tier: str = "unknown", session_id: str | None = None):
    """Record a completed API call's cost."""
    input_cost = (input_tokens / 1_000_000) * model_info["input"]
    output_cost = (output_tokens / 1_000_000) * model_info["output"]
    total_cost = input_cost + output_cost

    for scope in ["daily", "session"]:
        data = _load_cost_data(scope, session_id=session_id if scope == "session" else None)
        data["total_cost_usd"] += total_cost
        data["total_input_tokens"] += input_tokens
        data["total_output_tokens"] += output_tokens
        data["calls"] += 1

        # Track by tier
        tier_name = tier if tier in TIER_ORDER else "unknown"
        if tier_name == "unknown":
            for t_name in TIER_ORDER:
                for m in MODEL_TIERS[t_name]["models"]:
                    if m["id"] == model_info["id"]:
                        tier_name = t_name
                        break
        tier_data = data.setdefault("by_tier", {}).setdefault(tier_name, {"cost": 0.0, "calls": 0})
        tier_data["cost"] += total_cost
        tier_data["calls"] += 1

        # Track by model
        model_data = data.setdefault("by_model", {}).setdefault(model_info["id"], {"cost": 0.0, "calls": 0, "name": model_info["name"]})
        model_data["cost"] += total_cost
        model_data["calls"] += 1

        _save_cost_data(data, scope, session_id=session_id if scope == "session" else None)

    return total_cost


def check_budget(model_info: dict, estimated_tokens: int = 4096) -> tuple[bool, float, float]:
    """Check if a call would exceed the daily/session budget.

    Returns (allowed, remaining_daily, remaining_session).
    """
    daily_budget = float(os.environ.get("VENICE_DAILY_BUDGET", "0"))
    session_budget = float(os.environ.get("VENICE_SESSION_BUDGET", "0"))

    # Estimate cost for this call
    estimated_cost = (estimated_tokens / 1_000_000) * (model_info["input"] + model_info["output"])

    remaining_daily = float("inf")
    remaining_session = float("inf")

    if daily_budget > 0:
        daily_data = _load_cost_data("daily")
        remaining_daily = daily_budget - daily_data["total_cost_usd"]
        if remaining_daily < estimated_cost:
            return False, remaining_daily, remaining_session

    if session_budget > 0:
        session_data = _load_cost_data("session")
        remaining_session = session_budget - session_data["total_cost_usd"]
        if remaining_session < estimated_cost:
            return False, remaining_daily, remaining_session

    return True, remaining_daily, remaining_session


def get_budget_constrained_tier(tier: str, session_id: str | None = None) -> str:
    """Downgrade tier if budget is running low."""
    daily_budget = float(os.environ.get("VENICE_DAILY_BUDGET", "0") or "0")
    session_budget = float(os.environ.get("VENICE_SESSION_BUDGET", "0") or "0")

    if daily_budget <= 0 and session_budget <= 0:
        return tier  # No budget configured

    daily_data = _load_cost_data("daily")
    daily_spent = daily_data["total_cost_usd"]

    budget = daily_budget if daily_budget > 0 else session_budget
    spent = daily_spent

    if budget <= 0:
        return tier

    usage_pct = spent / budget

    tier_idx = TIER_ORDER.index(tier)

    # Progressive downgrade as budget is consumed
    if usage_pct >= 0.95:
        # Almost exhausted → force cheap
        return "cheap"
    elif usage_pct >= 0.80:
        # 80%+ used → cap at budget tier
        return TIER_ORDER[min(tier_idx, 1)]
    elif usage_pct >= 0.60:
        # 60%+ used → cap at mid
        return TIER_ORDER[min(tier_idx, 2)]
    elif usage_pct >= 0.40:
        # 40%+ used → cap at high
        return TIER_ORDER[min(tier_idx, 3)]

    return tier


def show_budget_status(session_id: str | None = None):
    """Print current budget usage."""
    daily_budget = float(os.environ.get("VENICE_DAILY_BUDGET", "0") or "0")
    session_budget = float(os.environ.get("VENICE_SESSION_BUDGET", "0") or "0")

    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║            Venice.ai Router — Cost & Budget Status             ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

    for scope, budget_val in [("daily", daily_budget), ("session", session_budget)]:
        data = _load_cost_data(scope, session_id=session_id if scope == "session" else None)
        label = "📅 Daily" if scope == "daily" else "🔄 Session"

        print(f"  {label} ({data.get('date', 'unknown')})")
        print(f"  {'─' * 50}")
        print(f"    Total cost:    ${data['total_cost_usd']:.6f}")
        print(f"    API calls:     {data['calls']}")
        print(f"    Input tokens:  {data['total_input_tokens']:,}")
        print(f"    Output tokens: {data['total_output_tokens']:,}")

        if budget_val > 0:
            remaining = budget_val - data["total_cost_usd"]
            pct = (data["total_cost_usd"] / budget_val) * 100 if budget_val > 0 else 0
            bar_len = 30
            filled = int(bar_len * min(pct, 100) / 100)
            bar = "█" * filled + "░" * (bar_len - filled)
            print(f"    Budget:        ${budget_val:.4f}")
            print(f"    Remaining:     ${remaining:.6f}")
            print(f"    Usage:         [{bar}] {pct:.1f}%")
        else:
            print(f"    Budget:        not configured")

        # Per-tier breakdown
        by_tier = data.get("by_tier", {})
        if by_tier:
            print(f"    ┌{'─' * 46}┐")
            print(f"    │ {'Tier':<12} {'Calls':>6} {'Cost':>12} {'%':>8}    │")
            print(f"    ├{'─' * 46}┤")
            total_cost = max(data["total_cost_usd"], 0.000001)
            for t in TIER_ORDER:
                if t in by_tier:
                    td = by_tier[t]
                    pct_t = (td["cost"] / total_cost) * 100
                    print(f"    │ {t:<12} {td['calls']:>6} ${td['cost']:>10.6f} {pct_t:>7.1f}%   │")
            print(f"    └{'─' * 46}┘")
        print()

# ── Venice.ai API Client ─────────────────────────────────────────────────────

def venice_chat(
    api_key: str,
    model_id: str,
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 4096,
    stream: bool = False,
    web_search: bool = False,
    character_slug: str | None = None,
    tools: list[dict] | None = None,
    tool_choice: str | dict | None = None,
) -> dict:
    """Send a chat completion request to Venice.ai.

    Returns a dict with:
      - content: str — the text response (may be empty if tool_calls present)
      - tool_calls: list[dict] | None — function calls the model wants to make
      - usage: dict — token usage {prompt_tokens, completion_tokens, total_tokens}
      - finish_reason: str — "stop", "tool_calls", "length", etc.
    """
    url = f"{VENICE_API_BASE}/chat/completions"

    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream,
    }

    # Function calling / tools
    if tools:
        payload["tools"] = tools
        if tool_choice:
            payload["tool_choice"] = tool_choice

    # Venice-specific parameters
    venice_params = {}
    if web_search:
        venice_params["enable_web_search"] = "on"
    if character_slug:
        venice_params["character_slug"] = character_slug
    if venice_params:
        payload["venice_parameters"] = venice_params

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "OpenClaw-VeniceRouter/1.5.0",
    }

    if stream:
        headers["Accept"] = "text/event-stream"

    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers=headers, method="POST")

    try:
        with urlopen(req) as resp:
            if stream:
                return _handle_stream(resp)
            else:
                body = json.loads(resp.read().decode("utf-8"))
                return _extract_response(body)
    except HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"\n❌ Venice API error ({e.code}): {error_body}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"\n❌ Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def _handle_stream(resp) -> dict:
    """Handle SSE streaming response, including tool call deltas."""
    full_content = []
    tool_calls_by_idx = {}  # index -> {id, type, function: {name, arguments}}
    finish_reason = "stop"

    for line in resp:
        line = line.decode("utf-8").strip()
        if not line or not line.startswith("data: "):
            continue
        data_str = line[6:]
        if data_str == "[DONE]":
            break
        try:
            chunk = json.loads(data_str)
            choices = chunk.get("choices", [])
            if not choices:
                continue
            choice = choices[0]
            delta = choice.get("delta", {})
            fr = choice.get("finish_reason")
            if fr:
                finish_reason = fr

            # Content streaming
            content = delta.get("content", "")
            if content:
                print(content, end="", flush=True)
                full_content.append(content)

            # Tool call streaming — accumulate deltas by index
            tc_deltas = delta.get("tool_calls", [])
            for tc in tc_deltas:
                idx = tc.get("index", 0)
                if idx not in tool_calls_by_idx:
                    tool_calls_by_idx[idx] = {
                        "id": tc.get("id", ""),
                        "type": "function",
                        "function": {"name": "", "arguments": ""},
                    }
                entry = tool_calls_by_idx[idx]
                if tc.get("id"):
                    entry["id"] = tc["id"]
                fn = tc.get("function", {})
                if fn.get("name"):
                    entry["function"]["name"] += fn["name"]
                if fn.get("arguments"):
                    entry["function"]["arguments"] += fn["arguments"]
        except json.JSONDecodeError:
            continue

    if full_content:
        print()  # Final newline after streamed content

    tool_calls = None
    if tool_calls_by_idx:
        tool_calls = [tool_calls_by_idx[i] for i in sorted(tool_calls_by_idx)]
        # Print tool calls for visibility
        for tc in tool_calls:
            fn = tc["function"]
            print(f"🔧 Tool call: {fn['name']}({fn['arguments']})", file=sys.stderr)

    return {
        "content": "".join(full_content),
        "tool_calls": tool_calls,
        "usage": {},
        "finish_reason": finish_reason,
    }


def _extract_response(body: dict) -> dict:
    """Extract content and tool calls from a non-streaming response."""
    choices = body.get("choices", [])
    if not choices:
        return {"content": "(no response)", "tool_calls": None, "usage": {}, "finish_reason": "stop"}

    message = choices[0].get("message", {})
    content = message.get("content") or ""
    tool_calls = message.get("tool_calls")
    finish_reason = choices[0].get("finish_reason", "stop")

    # Show usage if available
    usage = body.get("usage", {})
    if usage:
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        print(
            f"\n📊 Tokens: {prompt_tokens} in → {completion_tokens} out ({total_tokens} total)",
            file=sys.stderr,
        )

    # Print tool calls for visibility
    if tool_calls:
        for tc in tool_calls:
            fn = tc.get("function", {})
            print(f"🔧 Tool call: {fn.get('name', '?')}({fn.get('arguments', '')})", file=sys.stderr)

    return {
        "content": content,
        "tool_calls": tool_calls,
        "usage": usage,
        "finish_reason": finish_reason,
    }


# ── List Models ──────────────────────────────────────────────────────────────

def list_models():
    """Print all model tiers and their models."""
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║              Venice.ai Supreme Router — Model Tiers            ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

    for tier_name in TIER_ORDER:
        tier = MODEL_TIERS[tier_name]
        emoji = {"cheap": "💚", "budget": "💙", "budget-medium": "🩵", "mid": "💛", "high": "🧡", "premium": "💎"}
        print(f"  {emoji.get(tier_name, '⚪')} {tier_name.upper()} — {tier['description']}")
        print(f"  {'─' * 60}")

        for m in tier["models"]:
            privacy = "🔒 private" if m["private"] else "🔀 anon"
            uncensored = " 🔓" if m.get("uncensored", False) else ""
            thinking_flag = " 🧠" if m.get("thinking", False) else ""
            default_marker = " ⭐" if m["id"] == tier["default"] else ""
            ctx_k = m["ctx"] // 1000
            print(
                f"    {m['name']:.<30s} {m['id']:<40s}"
            )
            print(
                f"      ${m['input']:<6.2f} in / ${m['output']:<6.2f} out  "
                f"| {ctx_k}K ctx | {privacy}{uncensored}{thinking_flag}{default_marker}"
            )
        print()


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Venice.ai Supreme Router — cost-optimized model routing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --prompt "What is 2+2?"
  %(prog)s --tier mid --prompt "Explain recursion"
  %(prog)s --stream --prompt "Write a haiku"
  %(prog)s --web-search --prompt "Latest news on AI regulation"
  %(prog)s --uncensored --prompt "Write edgy creative fiction"
  %(prog)s --private-only --prompt "Analyze this confidential data"
  %(prog)s --thinking --prompt "Prove the halting problem is undecidable"
  %(prog)s --conversation history.json --prompt "continue"
  %(prog)s --tools tools.json --prompt "Get weather in NYC"
  %(prog)s --budget-status
  %(prog)s --classify "Design a microservices architecture"
  %(prog)s --list-models
  %(prog)s --model deepseek-v3.2 --prompt "Hello"
        """,
    )

    parser.add_argument("--prompt", "-p", type=str, help="Prompt to send")
    parser.add_argument("--tier", "-t", type=str, choices=TIER_ORDER, help="Force a specific tier")
    parser.add_argument("--model", "-m", type=str, help="Force a specific model ID")
    parser.add_argument("--classify", "-c", type=str, help="Classify prompt complexity (no API call)")
    parser.add_argument("--list-models", "-l", action="store_true", help="List all model tiers")
    parser.add_argument("--stream", "-s", action="store_true", help="Enable streaming output")
    parser.add_argument("--temperature", type=float, default=None, help="Temperature (0.0–2.0)")
    parser.add_argument("--max-tokens", type=int, default=None, help="Max tokens")
    parser.add_argument("--system", type=str, default=None, help="System prompt")
    parser.add_argument("--prefer-anon", action="store_true", help="Prefer anonymized models over private")
    parser.add_argument("--uncensored", "-u", action="store_true", help="Prefer uncensored models (no content filters, no refusals)")
    parser.add_argument("--private-only", action="store_true", help="Only use private models (zero data retention, no Big Tech proxying)")
    parser.add_argument("--web-search", "-w", action="store_true", help="Enable Venice web search ($10/1K calls) — LLM can search & cite sources")
    parser.add_argument("--character", type=str, default=None, help="Venice character slug for persona-based responses")
    parser.add_argument("--json", "-j", action="store_true", help="Output routing info as JSON")
    parser.add_argument("--thinking", action="store_true", help="Prefer thinking/reasoning models (Qwen3 Thinking, Kimi K2) — auto-bumps to mid tier minimum; ideal for math proofs, logic puzzles, multi-step deduction")

    # New: conversation-aware routing
    parser.add_argument("--conversation", type=str, default=None,
                        help="Path to JSON file with conversation history (array of {role, content} messages)")

    # New: function calling
    parser.add_argument("--tools", type=str, default=None,
                        help="Path to JSON file with tool/function definitions (OpenAI tools format)")
    parser.add_argument("--tool-choice", type=str, default=None,
                        help='Tool choice: "auto", "none", "required", or {"type":"function","function":{"name":"..."}}'
                        )

    # New: cost budget
    parser.add_argument("--budget-status", action="store_true",
                        help="Show current cost budget usage and exit")
    parser.add_argument("--session-id", type=str, default=None,
                        help="Session ID for per-session cost tracking (default: auto-generated)")

    args = parser.parse_args()

    # ── List models ──────────────────────────────────────────────────────
    if args.list_models:
        list_models()
        return

    # ── Budget status ────────────────────────────────────────────────────
    if args.budget_status:
        show_budget_status(session_id=args.session_id)
        return

    # ── Classify only ────────────────────────────────────────────────────
    if args.classify:
        tier = classify_complexity(args.classify)
        prefer_private = not args.prefer_anon
        prefer_uncensored = args.uncensored or os.environ.get("VENICE_UNCENSORED", "false").lower() == "true"
        private_only = args.private_only or os.environ.get("VENICE_PRIVATE_ONLY", "false").lower() == "true"
        prefer_thinking = args.thinking or os.environ.get("VENICE_THINKING", "false").lower() == "true"
        # Apply VENICE_DEFAULT_TIER as a minimum floor tier
        default_tier = os.environ.get("VENICE_DEFAULT_TIER")
        if default_tier and default_tier in TIER_ORDER:
            if TIER_ORDER.index(tier) < TIER_ORDER.index(default_tier):
                tier = default_tier
        model = select_model(tier, prefer_private=prefer_private, prefer_uncensored=prefer_uncensored, private_only=private_only, prefer_thinking=prefer_thinking)
        max_tier = os.environ.get("VENICE_MAX_TIER")
        effective_tier = get_effective_tier(tier, max_tier)
        if prefer_uncensored:
            effective_tier = find_tier_with_uncensored(effective_tier, max_tier, private_only)
        if prefer_thinking:
            effective_tier = find_tier_with_thinking(effective_tier, max_tier)
        effective_model = select_model(effective_tier, prefer_private=prefer_private, prefer_uncensored=prefer_uncensored, private_only=private_only, prefer_thinking=prefer_thinking)

        if args.json:
            result = {
                "classified_tier": tier,
                "effective_tier": effective_tier,
                "model_id": effective_model["id"],
                "model_name": effective_model["name"],
                "input_cost_per_1m": effective_model["input"],
                "output_cost_per_1m": effective_model["output"],
                "context_window": effective_model["ctx"],
                "private": effective_model["private"],
                "uncensored": effective_model.get("uncensored", False),
                "prompt_length": len(args.classify),
            }
            if max_tier and tier != effective_tier:
                result["capped_by_max_tier"] = max_tier
            if args.web_search:
                result["web_search"] = True
            if prefer_thinking:
                result["thinking"] = True
            print(json.dumps(result, indent=2))
        else:
            emoji = {"cheap": "💚", "budget": "💙", "budget-medium": "🩵", "mid": "💛", "high": "🧡", "premium": "💎"}
            print(f"  Complexity:  {emoji.get(effective_tier, '⚪')} {effective_tier.upper()}")
            if max_tier and tier != effective_tier:
                print(f"  (classified as {tier}, capped to {effective_tier} by VENICE_MAX_TIER)")
            print(f"  Model:       {effective_model['name']} ({effective_model['id']})")
            print(f"  Cost:        ${effective_model['input']}/M in, ${effective_model['output']}/M out")
            print(f"  Context:     {effective_model['ctx'] // 1000}K tokens")
            print(f"  Privacy:     {'🔒 private (zero retention)' if effective_model['private'] else '🔀 anonymized (proxied)'}")
            print(f"  Uncensored:  {'🔓 yes' if effective_model.get('uncensored', False) else '🛡️ no'}")
            print(f"  Thinking:    {'🧠 yes (chain-of-thought reasoning)' if effective_model.get('thinking', False) else '💬 standard'}")
            if args.web_search:
                print(f"  Web Search:  🌐 enabled ($10/1K calls)")
        return

    # ── Send prompt ──────────────────────────────────────────────────────
    if not args.prompt:
        # Read from stdin if no prompt flag
        if not sys.stdin.isatty():
            args.prompt = sys.stdin.read().strip()
        if not args.prompt:
            parser.print_help()
            sys.exit(1)

    api_key = os.environ.get("VENICE_API_KEY")
    if not api_key:
        print("❌ VENICE_API_KEY environment variable not set.", file=sys.stderr)
        print("   Get one at: https://venice.ai/settings/api", file=sys.stderr)
        sys.exit(1)

    # Model selection preferences
    prefer_private = not args.prefer_anon
    prefer_uncensored = args.uncensored or os.environ.get("VENICE_UNCENSORED", "false").lower() == "true"
    private_only = args.private_only or os.environ.get("VENICE_PRIVATE_ONLY", "false").lower() == "true"
    web_search = args.web_search or os.environ.get("VENICE_WEB_SEARCH", "false").lower() == "true"
    prefer_thinking = args.thinking or os.environ.get("VENICE_THINKING", "false").lower() == "true"

    # ── Load conversation history ────────────────────────────────────
    conversation_messages = []
    if args.conversation:
        try:
            with open(args.conversation, "r") as f:
                conversation_messages = json.load(f)
            if not isinstance(conversation_messages, list):
                print(f"❌ Conversation file must contain a JSON array of messages", file=sys.stderr)
                sys.exit(1)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"❌ Error reading conversation file: {e}", file=sys.stderr)
            sys.exit(1)

    # ── Load tool definitions ────────────────────────────────────────
    tools = None
    tool_choice = None
    if args.tools:
        try:
            with open(args.tools, "r") as f:
                tools = json.load(f)
            if not isinstance(tools, list):
                print(f"❌ Tools file must contain a JSON array of tool definitions", file=sys.stderr)
                sys.exit(1)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"❌ Error reading tools file: {e}", file=sys.stderr)
            sys.exit(1)
    if args.tool_choice:
        # Parse tool_choice — could be a string or JSON object
        tc = args.tool_choice.strip()
        if tc.startswith("{"):
            try:
                tool_choice = json.loads(tc)
            except json.JSONDecodeError:
                print(f"❌ Invalid --tool-choice JSON: {tc}", file=sys.stderr)
                sys.exit(1)
        else:
            tool_choice = tc  # "auto", "none", "required"

    # ── Determine model ──────────────────────────────────────────────
    model_info = None
    if args.model:
        model_id = args.model
        model_name = args.model
        tier_name = "custom"
    elif args.tier:
        tier_name = args.tier
        if prefer_uncensored:
            tier_name = find_tier_with_uncensored(tier_name, os.environ.get("VENICE_MAX_TIER"), private_only)
        if prefer_thinking:
            tier_name = find_tier_with_thinking(tier_name, os.environ.get("VENICE_MAX_TIER"))
        model_info = select_model(tier_name, prefer_private=prefer_private, prefer_uncensored=prefer_uncensored, private_only=private_only, prefer_thinking=prefer_thinking)
        model_id = model_info["id"]
        model_name = model_info["name"]
    else:
        # Smart classification — use conversation if available
        if conversation_messages:
            # Build full message history including the new prompt
            classify_msgs = conversation_messages + [{"role": "user", "content": args.prompt}]
            tier_name = classify_with_conversation(classify_msgs)
        else:
            tier_name = classify_complexity(args.prompt)

        # Apply VENICE_DEFAULT_TIER as a minimum floor tier
        default_tier = os.environ.get("VENICE_DEFAULT_TIER")
        if default_tier and default_tier in TIER_ORDER:
            classified_idx = TIER_ORDER.index(tier_name)
            default_idx = TIER_ORDER.index(default_tier)
            if classified_idx < default_idx:
                tier_name = default_tier

        # Bump for function calling (tool use needs capable models)
        if tools:
            tier_idx = TIER_ORDER.index(tier_name)
            if tier_idx < 2:  # At least mid for function calling
                tier_name = "mid"
                print("  📎 Tier bumped to mid (function calling requires capable models)", file=sys.stderr)

        # Bump for thinking mode (thinking models start at mid)
        if prefer_thinking:
            max_tier = os.environ.get("VENICE_MAX_TIER")
            tier_name = find_tier_with_thinking(tier_name, max_tier)
            print(f"  🧠 Thinking mode — routing to {tier_name.upper()} for reasoning models", file=sys.stderr)

        max_tier = os.environ.get("VENICE_MAX_TIER")
        tier_name = get_effective_tier(tier_name, max_tier)
        if prefer_uncensored:
            tier_name = find_tier_with_uncensored(tier_name, max_tier, private_only)

        # Apply budget constraints
        daily_budget = float(os.environ.get("VENICE_DAILY_BUDGET", "0") or "0")
        session_budget = float(os.environ.get("VENICE_SESSION_BUDGET", "0") or "0")
        if daily_budget > 0 or session_budget > 0:
            budget_tier = get_budget_constrained_tier(tier_name, session_id=args.session_id)
            if budget_tier != tier_name:
                print(f"  💰 Tier downgraded {tier_name} → {budget_tier} (budget constraint)", file=sys.stderr)
                tier_name = budget_tier

        model_info = select_model(tier_name, prefer_private=prefer_private, prefer_uncensored=prefer_uncensored, private_only=private_only, prefer_thinking=prefer_thinking)
        model_id = model_info["id"]
        model_name = model_info["name"]

    # Env defaults
    temperature = args.temperature or float(os.environ.get("VENICE_TEMPERATURE", "0.7"))
    max_tokens = args.max_tokens or int(os.environ.get("VENICE_MAX_TOKENS", "4096"))
    stream = args.stream or os.environ.get("VENICE_STREAM", "false").lower() == "true"

    # Build messages
    messages = []
    if args.system:
        messages.append({"role": "system", "content": args.system})
    # Include conversation history
    if conversation_messages:
        messages.extend(conversation_messages)
    messages.append({"role": "user", "content": args.prompt})

    # Route info
    emoji = {"cheap": "💚", "budget": "💙", "budget-medium": "🩵", "mid": "💛", "high": "🧡", "premium": "💎", "custom": "⚙️"}
    flags = []
    if web_search:
        flags.append("🌐 web")
    if prefer_uncensored:
        flags.append("🔓 uncensored")
    if private_only:
        flags.append("🔒 private-only")
    if prefer_thinking:
        flags.append("🧠 thinking")
    if tools:
        flags.append(f"🔧 {len(tools)} tools")
    if conversation_messages:
        flags.append(f"💬 {len(conversation_messages)} msgs")
    flag_str = f" [{', '.join(flags)}]" if flags else ""
    print(f"🧡 Venice Router → {emoji.get(tier_name, '⚪')} {tier_name.upper()} → {model_name} ({model_id}){flag_str}", file=sys.stderr)

    # Call Venice API
    result = venice_chat(
        api_key=api_key,
        model_id=model_id,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=stream,
        web_search=web_search,
        character_slug=args.character,
        tools=tools,
        tool_choice=tool_choice,
    )

    # ── Record cost ──────────────────────────────────────────────────
    if model_info and result.get("usage"):
        record_cost(
            model_info=model_info,
            input_tokens=result["usage"].get("prompt_tokens", 0),
            output_tokens=result["usage"].get("completion_tokens", 0),
            tier=tier_name,
            session_id=args.session_id,
        )

    # ── Output ───────────────────────────────────────────────────────
    if result.get("tool_calls"):
        # Output tool calls as JSON for programmatic consumption
        if args.json:
            print(json.dumps({
                "content": result["content"],
                "tool_calls": result["tool_calls"],
                "finish_reason": result["finish_reason"],
                "usage": result.get("usage", {}),
            }, indent=2))
        else:
            # Tool calls already printed to stderr by _extract_response / _handle_stream
            if result["content"]:
                print(result["content"])
    elif result.get("content") and not stream:
        print(result["content"])


if __name__ == "__main__":
    main()
