#!/usr/bin/env python3
"""
Capability-Based Tier Classifier v2.0
Assigns model tiers using multiple quality signals from provider metadata.
NO hard-coded name-based tier heuristics.

## Why v1 Was Wrong

v1 used cost as the primary capability signal:
  cost < $0.60/M → SIMPLE

This breaks in 2026 where cheap SOTA models (DeepSeek V3.2 at $0.40/M, Llama-4-Maverick at
$0.40/M) are equal or better than expensive models from 2024. Cost ≠ capability.

## v2 Approach

Four signals, combined into a single capability_score [0–1]:

  1. effective_params   — extracted from model ID (7b, 70b, 405b, MoE-adjusted)
                          Largest single signal. Bigger = more capable.
  2. context_window     — larger window = more capable (long doc, multi-file)
  3. reasoning_flag     — model is a dedicated reasoning/thinking specialist
  4. cost_input         — expensive = likely quality (weak signal, last resort fallback)

SIMPLE tier is ONLY for:
  - Local/Ollama models (zero API cost, free to use)
  - Tiny cloud models (< 10B effective params AND cost < $0.30/M)

Everything else is MEDIUM or above based on capability_score.

"Pick the top ones": within each tier, models are ranked by score. Primary = best.
Routing prefers CHEAPER model within same tier for cost efficiency.
"""

from __future__ import annotations
import json
import re
from pathlib import Path
from collections import defaultdict

# ── Tier Capability Score Thresholds ──────────────────────────────────────────
# Scores are normalised [0, 1]. Boundaries tuned to real-world model landscape.
TIER_THRESHOLDS = {
    # SIMPLE: local/free OR tiny (< 10B, cheap). Score 0.0–0.24
    # MEDIUM: capable mid-range (13B–70B cloud). Score 0.25–0.49
    # COMPLEX: high quality (70B+ cloud, Sonnet-class). Score 0.50–0.79
    # REASONING: specialist thinking models. Always REASONING regardless of score
    # CRITICAL: flagship (Opus-class, >$8/M). Score 0.80+
}

SIMPLE_PARAMS_MAX   = 10        # < 10B effective params → candidate for SIMPLE
SIMPLE_COST_MAX     = 0.30      # also must be cheap
CRITICAL_COST_MIN   = 8.0       # ≥ $8/M input → CRITICAL
COMPLEX_SCORE_MIN   = 0.50      # score ≥ 0.50 → COMPLEX
MEDIUM_SCORE_MIN    = 0.25      # score ≥ 0.25 → MEDIUM

# Context window large enough to imply high capability
CONTEXT_LARGE       = 200_000   # e.g. 200K+ → adds to score
CONTEXT_HUGE        = 500_000   # 500K+ → strong COMPLEX signal

# ── Reasoning-Specialist Detection ────────────────────────────────────────────
# Identifies models BUILT for reasoning (not just ones that support thinking mode).
# Kept minimal and specific — only patterns that are unambiguous reasoning-only models.
REASONING_SPECIALIST_PATTERNS = [
    r"\br1\b",           # DeepSeek R1 family (r1, r1-distill)
    r"\bqwq\b",          # Qwen QwQ (thinking-only model)
    r"-thinking\b",      # "kimi-k2-thinking", "qwen3-next-...-thinking"
    r"\breasoning\b",    # "phi-4-mini-flash-reasoning"
    r"^r\d",             # starts with r + digit (r1, r2)
]

LOCAL_PROVIDERS = {"ollama", "ollama-gpu-server"}

# Path to known-model param lookup (model ID regex → effective param count in B)
_KNOWN_PARAMS_FILE = Path(__file__).parent.parent / "known-model-params.json"


def _load_known_params() -> dict:
    """Load known model parameter counts from companion JSON file."""
    if _KNOWN_PARAMS_FILE.exists():
        with open(_KNOWN_PARAMS_FILE) as f:
            return json.load(f)
    return {}


def extract_effective_params(model_id: str, cost_input: float = 0.0) -> float:
    """
    Extract effective parameter count (billions) from model ID.
    Handles:
      - Dense: 7b, 13b, 70b, 405b
      - MoE: 8x7b → 56B dense-equiv (MoE actual active ~12.5B — we use 0.25x multiplier for density)
      - Sub-billion: 0.5b, 3.8b
      - Shorthand: 32b, 253b
    When param count cannot be extracted from ID (closed models like Claude, GLM),
    estimates from cost bracket as a fallback. This only fires for truly unknown sizes.
    """
    mid = model_id.lower()

    # MoE pattern: NxMb (e.g. 8x7b, 8x22b)
    moe = re.search(r"(\d+)x(\d+\.?\d*)b", mid)
    if moe:
        experts = int(moe.group(1))
        per_expert = float(moe.group(2))
        # MoE effective quality ≈ total params at 0.4x (active params ratio is higher than 1/N)
        return experts * per_expert * 0.4

    # Dense: extract largest param count in ID
    matches = re.findall(r"(\d+\.?\d*)b(?!\w)", mid)
    if matches:
        return max(float(m) for m in matches)

    # Check known-model param table (ground truth for models where ID has no param count).
    # This is a curated list of real published sizes — NOT tier heuristics.
    # Add entries here when you know the real param count for a closed-source model.
    KNOWN_PARAMS = _load_known_params()
    for pattern, params in KNOWN_PARAMS.items():
        if re.search(pattern, mid):
            return params

    # Unknown ID with no known params — estimate from cost bracket.
    # Cost is the only remaining proxy for closed models (Claude, GLM, etc.).
    #   $8+/M   → flagship (Opus-class, ~400B+)     → 400B
    #   $3+/M   → advanced (Sonnet-class, ~200B+)   → 200B
    #   $1+/M   → capable  (mid-range, ~50B+)        →  50B
    #   $0.3+/M → efficient (GLM-class, ~15B)        →  15B
    #   <$0.3/M → micro or free                      →   7B
    if cost_input >= 8.0:
        return 400.0
    elif cost_input >= 3.0:
        return 200.0
    elif cost_input >= 1.0:
        return 50.0
    elif cost_input >= 0.3:
        return 15.0
    else:
        return 7.0


def is_reasoning_specialist(model_id: str, reasoning_flag: bool) -> bool:
    """True only for models DESIGNED for reasoning, not general models with thinking mode."""
    if not reasoning_flag:
        return False
    mid = model_id.lower()
    return any(re.search(p, mid) for p in REASONING_SPECIALIST_PATTERNS)


def capability_score(
    model_id: str,
    context_window: int,
    cost_input: float,
    reasoning: bool,
    is_local: bool,
    effective_params: float,
) -> float:
    """
    Compute a normalised capability score [0, 1].

    Weights (sum = 1.0):
      effective_params: 0.50  — single strongest signal
      context_window:   0.20  — long context = more capable
      cost_input:       0.20  — expensive = likely quality (weak but universal)
      reasoning:        0.10  — dedicated reasoning specialist bonus
    """
    # Params score: log-scale normalised to [0, 1] anchored at 405B = 1.0
    if effective_params > 0:
        import math
        # log2(1) = 0, log2(405) ≈ 8.66
        params_score = min(math.log2(max(effective_params, 1)) / math.log2(405), 1.0)
    else:
        params_score = 0.3  # unknown size — assume mid-range

    # Context score
    ctx_score = min(context_window / 1_000_000, 1.0)  # 1M ctx = 1.0

    # Cost score: proxy for quality, log-scale, $100/M = 1.0
    if is_local:
        cost_score = 0.0  # local = free; use as SIMPLE signal, not quality
    else:
        import math
        cost_score = min(math.log1p(cost_input) / math.log1p(100), 1.0)

    # Reasoning bonus
    reasoning_score = 0.5 if is_reasoning_specialist(model_id, reasoning) else 0.0

    score = (
        0.50 * params_score +
        0.20 * ctx_score +
        0.20 * cost_score +
        0.10 * reasoning_score
    )
    return round(score, 4)


def assign_tier(
    model_id: str,
    context_window: int,
    cost_input: float,
    reasoning: bool,
    is_local: bool,
    effective_params: float,
    cap_score: float,
) -> str:
    """
    Assign tier based on capability score + hard rules.
    Evaluated in order (first match wins).
    """
    # CRITICAL: flagship cost (≥ $8/M) — regardless of score
    if cost_input >= CRITICAL_COST_MIN:
        return "CRITICAL"

    # CRITICAL: huge context flagship (e.g. Opus with 1M ctx)
    if context_window >= CONTEXT_HUGE and cost_input >= 3.0:
        return "CRITICAL"

    # REASONING: dedicated thinking/specialist models
    if is_reasoning_specialist(model_id, reasoning):
        return "REASONING"

    # SIMPLE: local (always free) — regardless of quality
    if is_local:
        return "SIMPLE"

    # SIMPLE: tiny cloud models (< 10B AND cheap)
    if effective_params > 0 and effective_params < SIMPLE_PARAMS_MAX and cost_input < SIMPLE_COST_MAX:
        return "SIMPLE"

    # Score-based classification for everything else
    if cap_score >= 0.70:
        return "COMPLEX"
    if cap_score >= COMPLEX_SCORE_MIN:
        return "COMPLEX"
    if cap_score >= MEDIUM_SCORE_MIN:
        return "MEDIUM"

    # Fallthrough: very cheap cloud models with unknown size → MEDIUM
    # (we never put unknowns in SIMPLE — too risky for quality)
    return "MEDIUM"


def score_model(
    provider: str,
    model_id: str,
    context_window: int,
    cost_input: float,
    cost_output: float,
    reasoning: bool,
    is_local: bool,
) -> dict:
    """
    Full scoring pipeline for one model.
    Returns {"tier": str, "score": float, "signals": dict}
    """
    effective_params = extract_effective_params(model_id, cost_input)
    cap = capability_score(
        model_id, context_window, cost_input, reasoning, is_local, effective_params
    )
    tier = assign_tier(
        model_id, context_window, cost_input, reasoning, is_local, effective_params, cap
    )

    signals = {
        "provider": provider,
        "model_id": model_id,
        "effective_params_b": effective_params,
        "cost_input": cost_input,
        "context_window": context_window,
        "reasoning_flag": reasoning,
        "is_local": is_local,
        "is_reasoning_specialist": is_reasoning_specialist(model_id, reasoning),
        "capability_score": cap,
    }
    return {"tier": tier, "score": cap, "signals": signals}


def classify_from_openclaw_config(config_path: str = None) -> list[dict]:
    """
    Read all model metadata from OpenClaw config and classify every model.
    Returns list of model dicts with tier assigned from real capability signals.
    """
    if config_path is None:
        config_path = Path.home() / ".openclaw" / "openclaw.json"

    with open(config_path) as f:
        oc_config = json.load(f)

    providers = oc_config.get("models", {}).get("providers", {})
    classified = []

    for provider_name, provider_cfg in providers.items():
        is_local = provider_name in LOCAL_PROVIDERS
        base_url = provider_cfg.get("baseUrl", "")

        for model in provider_cfg.get("models", []):
            model_id = model.get("id", "")
            context_window = model.get("contextWindow", 8192)
            cost = model.get("cost", {})
            cost_input = cost.get("input", 0.0)
            cost_output = cost.get("output", 0.0)
            reasoning = model.get("reasoning", False)

            result = score_model(
                provider=provider_name,
                model_id=model_id,
                context_window=context_window,
                cost_input=cost_input,
                cost_output=cost_output,
                reasoning=reasoning,
                is_local=is_local,
            )

            classified.append({
                "id": model_id,
                "alias": model.get("name", model_id),
                "provider": provider_name,
                "base_url": base_url,
                "tier": result["tier"],
                "score": result["score"],
                "context_window": context_window,
                "input_cost_per_m": cost_input,
                "output_cost_per_m": cost_output,
                "reasoning": reasoning,
                "is_local": is_local,
                "modalities": model.get("input", ["text"]),
                "capabilities": ["agentic"] if model.get("agentic") else [],
                "effective_params_b": result["signals"]["effective_params_b"],
                "signals": result["signals"],
            })

    return classified


# ── Provider preference for primary selection ──────────────────────────────────
# Lower = more preferred. Used as tiebreaker within same score+tier.
PROVIDER_PREFERENCE = {
    "ollama-gpu-server": 0,   # dedicated local GPU — most preferred for SIMPLE
    "anthropic": 1,            # OAuth — most reliable for COMPLEX/CRITICAL
    "anthropic-proxy-1": 2,
    "anthropic-proxy-4": 3,    # z.ai cheap proxy (good for SIMPLE cloud fallback)
    "anthropic-proxy-6": 4,
    "nvidia-nim": 5,           # NIM — good coverage across tiers
    "anthropic-proxy-2": 6,
    "anthropic-proxy-5": 7,
    "ollama": 8,               # local CPU — slow, lowest priority
}


def build_tier_config(classified: list[dict]) -> dict:
    """
    Build per-tier routing config from classified models.

    For each tier:
    - Primary = highest capability score model (with provider preference as tiebreaker)
    - Fallbacks = remaining models sorted score desc, with cost preference as secondary sort

    "Top model" selection: score is the primary sort. Within same score bracket (±0.05),
    prefer the cheaper model (cost efficiency). This surfaces the best quality at lowest cost.
    """
    by_tier = defaultdict(list)
    for m in classified:
        by_tier[m["tier"]].append(m)

    def full_id(m: dict) -> str:
        p = m.get("provider", "")
        i = m.get("id", "")
        return f"{p}/{i}" if p else i

    def is_vision_only(m: dict) -> bool:
        mid = m.get("id", "").lower()
        modalities = m.get("modalities", ["text"])
        return "vision" in mid and "text" not in modalities

    def sort_key_for_tier(tier: str, m: dict):
        """
        Sorting key per tier to pick the best primary + fallback ordering.

        SIMPLE:
          - Local GPU first (free, fast)
          - Then cheap cloud text models (no vision-only)
          - Sort: (is_local_desc, is_vision_asc, cost_asc, score_desc)

        MEDIUM/COMPLEX:
          - Best score first
          - Within ±0.05 score bracket, prefer cheaper (cost efficiency)
          - Provider reliability as final tiebreaker

        REASONING:
          - Best score (bigger reasoning models = better)

        CRITICAL:
          - OAuth first (most reliable for prod)
          - Then by score
        """
        score = m.get("score", 0.0)
        cost = m.get("input_cost_per_m", 0.0)
        pref = PROVIDER_PREFERENCE.get(m.get("provider", ""), 99)

        if tier == "SIMPLE":
            # Prefer ≥7B models over tiny ones — sub-7B can't reliably do
            # agent work (tool calls, Telegram, monitoring scripts).
            params = m.get("effective_params_b", 0) or 0
            is_tiny = 1 if params < 7 else 0
            vision_penalty = 1 if is_vision_only(m) else 0
            local_bonus = 0 if m.get("is_local") else 1
            return (is_tiny, local_bonus, vision_penalty, cost, pref, -score)

        if tier == "CRITICAL":
            # OAuth providers first, then by score desc
            return (pref, -score)

        # MEDIUM: score bracket 0.10 — within same quality band, pick cheapest
        if tier == "MEDIUM":
            score_bracket = round(score / 0.10) * 0.10
            return (-score_bracket, cost, pref)

        # COMPLEX: wider 0.15 bracket so provider reliability beats marginal score gaps.
        # Within bracket: reliability (provider pref) FIRST, then newer version, then cost.
        if tier == "COMPLEX":
            score_bracket = round(score / 0.15) * 0.15
            # Extract version for tiebreaking (prefer newer: 4.6 > 4.5)
            ver_match = re.search(r"(\d+)[._-](\d+)", m.get("id", ""))
            ver = float(f"{ver_match.group(1)}.{ver_match.group(2)}") if ver_match else 0.0
            return (-score_bracket, pref, -ver, cost)

        # REASONING: wider 0.15 bracket, prefer by score then cost
        score_bracket = round(score / 0.15) * 0.15
        return (-score_bracket, cost, pref)

    tier_descriptions = {
        "SIMPLE":    "Monitoring, heartbeat, summaries — free/tiny/cheap models",
        "MEDIUM":    "Code fixes, research, data analysis — capable mid-range",
        "COMPLEX":   "Features, architecture, debugging — high quality models",
        "REASONING": "Formal logic, deep analysis, math — dedicated thinking models",
        "CRITICAL":  "Security, production, high-stakes — flagship models only",
    }

    use_for = {
        "SIMPLE":    ["monitoring", "status checks", "summaries", "alerts",
                      "heartbeat", "tweet monitoring", "price alerts", "memory consolidation"],
        "MEDIUM":    ["code fixes", "research", "API integration", "docs",
                      "general QA", "data analysis", "moderate tasks"],
        "COMPLEX":   ["feature development", "architecture", "debugging",
                      "code review", "multi-file changes", "trading strategy"],
        "REASONING": ["formal proofs", "deep analysis", "math", "algorithmic design",
                      "long-horizon planning", "complex logical chains"],
        "CRITICAL":  ["security review", "production decisions", "financial ops",
                      "high-stakes analysis", "strategic planning"],
    }

    configs = {}
    for tier in ["SIMPLE", "MEDIUM", "COMPLEX", "REASONING", "CRITICAL"]:
        models = sorted(by_tier.get(tier, []), key=lambda m: sort_key_for_tier(tier, m))
        if not models:
            configs[tier] = {
                "description": tier_descriptions[tier],
                "primary": "",
                "fallbacks": [],
                "use_for": use_for.get(tier, []),
            }
            continue

        configs[tier] = {
            "description": tier_descriptions[tier],
            "primary": full_id(models[0]),
            "fallbacks": [full_id(m) for m in models[1:]],
            "use_for": use_for.get(tier, []),
        }

    return configs


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Capability-based tier classifier v2.0")
    parser.add_argument("--config", default=None, help="OpenClaw config path")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--tier", choices=["SIMPLE", "MEDIUM", "COMPLEX", "REASONING", "CRITICAL"],
                        help="Show only this tier")
    args = parser.parse_args()

    classified = classify_from_openclaw_config(args.config)

    if args.json:
        print(json.dumps(classified, indent=2))
        return

    from collections import defaultdict
    by_tier = defaultdict(list)
    for m in classified:
        by_tier[m["tier"]].append(m)

    tiers_to_show = [args.tier] if args.tier else ["SIMPLE", "MEDIUM", "COMPLEX", "REASONING", "CRITICAL"]

    print("\n=== Capability-Based Tier Classification v2.0 ===\n")
    for tier in tiers_to_show:
        models = sorted(by_tier.get(tier, []), key=lambda m: -m["score"])
        print(f"{tier} ({len(models)} models):")
        for m in models:
            params = f"  params={m['effective_params_b']:.0f}B" if m['effective_params_b'] > 0 else "  params=?"
            local_tag = " [local]" if m.get("is_local") else ""
            reasoning_tag = " [reasoning-specialist]" if m["signals"].get("is_reasoning_specialist") else ""
            print(f"  {m['provider']}/{m['id']}"
                  f"{params}"
                  f"  ctx={m['context_window']//1000}K"
                  f"  cost=${m['input_cost_per_m']}/M"
                  f"  cap={m['score']:.3f}"
                  f"{local_tag}{reasoning_tag}")
        print()

    tier_cfg = build_tier_config(classified)
    print("Primary models per tier (ranked by capability + cost efficiency):")
    for tier, cfg in tier_cfg.items():
        primary = cfg.get("primary", "(none)")
        fb_count = len(cfg.get("fallbacks", []))
        print(f"  {tier}: {primary} (+{fb_count} fallbacks)")


if __name__ == "__main__":
    main()
