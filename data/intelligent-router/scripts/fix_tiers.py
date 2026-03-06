#!/usr/bin/env python3
"""
Fix intelligent-router config: assign tiers to all models and rebuild fallback chains.
Run: uv run python skills/intelligent-router/scripts/fix_tiers.py
"""
import json
from pathlib import Path

CONFIG = Path(__file__).parent.parent / "config.json"

# ── Tier definitions ───────────────────────────────────────────────────────────
# SIMPLE:    free/cheap/fast — monitoring, summaries, simple tasks
# MEDIUM:    mid-range — code fixes, research, analysis
# COMPLEX:   high quality — features, architecture, debugging
# REASONING: thinking models — proofs, complex logic
# CRITICAL:  best available — security, production decisions

def assign_tier(model: dict) -> str:
    provider = model.get("provider", "")
    mid = model.get("id", "").lower()
    alias = model.get("alias", "").lower()

    # CRITICAL — Opus models
    if "opus" in mid or "opus" in alias:
        return "CRITICAL"
    if "nemotron-ultra-253b" in mid or "253b" in mid:
        return "CRITICAL"

    # REASONING — thinking/reasoning models
    if any(x in mid for x in ["r1", "qwq", "thinking", "reasoning", "kimi-k2-thinking", "phi-4-mini-flash-reasoning"]):
        return "REASONING"
    if "kimi-k2" in mid and "thinking" in mid:
        return "REASONING"

    # COMPLEX — Sonnet, large capable models
    if "sonnet" in mid:
        return "COMPLEX"
    if "glm-4.7" in mid and provider in ("anthropic-proxy-4", "anthropic-proxy-6", "anthropic-proxy-2", "anthropic-proxy-1"):
        return "COMPLEX"
    if any(x in mid for x in ["llama-4-maverick", "nemotron-super-49b", "nemotron-51b", "mistral-large"]):
        return "COMPLEX"
    if "kimi-k2" in mid:
        return "COMPLEX"

    # SIMPLE — GLM-4.7 via cheap proxies (proxy-4/6 are z.ai, very cheap)
    if "glm-4.7" in mid and provider in ("anthropic-proxy-4", "anthropic-proxy-6",
                                          "nvidia-nim", "ollama-gpu-server"):
        return "SIMPLE"

    # MEDIUM — 70B class, DeepSeek V3, capable mid-range
    if any(x in mid for x in ["deepseek-v3", "deepseek-chat", "llama-3.3-70b", "llama-3.1-70b",
                               "llama-4-scout", "qwen2.5:32b", "llama3.3", "llama-3.3"]):
        return "MEDIUM"
    if "glm-4.7" in mid and provider in ("anthropic-proxy-5",):
        return "MEDIUM"

    # SIMPLE — small/free/fast models
    if any(x in mid for x in ["glm-4.7-flash", "llama3.2:3b", "qwen2.5:1.5b",
                               "llama3.2:3b", "llama-3.2-3b", "phi-3.5"]):
        return "SIMPLE"
    if provider == "ollama" and any(x in mid for x in ["3b", "7b", "1.5b"]):
        return "SIMPLE"

    # MEDIUM fallback for larger ollama models
    if provider == "ollama":
        return "MEDIUM"
    if provider == "nvidia-nim":
        return "MEDIUM"

    return "SIMPLE"


def full_id(model: dict) -> str:
    """Return provider/id format for use in tier fallback chains."""
    p = model.get("provider", "")
    m = model.get("id", "")
    if p:
        return f"{p}/{m}"
    return m


def build_tiers(models: list) -> dict:
    """Build tier configs with primary + fallback chains."""
    by_tier: dict[str, list] = {t: [] for t in ["SIMPLE", "MEDIUM", "COMPLEX", "REASONING", "CRITICAL"]}

    for m in models:
        tier = m["tier"]
        if tier in by_tier:
            by_tier[tier].append(m)

    def tier_cfg(primary_ids: list, fallback_ids: list, description: str) -> dict:
        return {
            "description": description,
            "primary": primary_ids[0] if primary_ids else "",
            "fallbacks": primary_ids[1:] + fallback_ids,
        }

    # Build ordered lists per tier
    def ids(tier):
        return [full_id(m) for m in by_tier[tier]]

    # SIMPLE tier: GPU-server GLM flash first (free local), then proxy-4/6, then others
    def simple_sort(m):
        pid = full_id(m)
        if pid == "ollama-gpu-server/glm-4.7-flash":     return 0  # free local
        if pid == "anthropic-proxy-4/glm-4.7":           return 1  # z.ai key 2
        if pid == "anthropic-proxy-6/glm-4.7":           return 2  # z.ai key 1
        if "glm" in m["id"].lower():                     return 3
        if "flash" in m["id"].lower():                   return 4
        return 5
    simple_order = sorted(by_tier["SIMPLE"], key=simple_sort)

    # MEDIUM tier: DeepSeek V3 first, then 70B models
    medium_priority = ["deepseek-v3", "deepseek-chat", "llama-3.3-70b", "llama3.3", "qwen2.5:32b"]
    def medium_sort(m):
        for i, pat in enumerate(medium_priority):
            if pat in m["id"].lower():
                return i
        return 99
    medium_order = sorted(by_tier["MEDIUM"], key=medium_sort)

    # COMPLEX tier: OAuth Sonnet first, then other Sonnet, then others
    def complex_sort(m):
        pid = full_id(m)
        if pid == "anthropic/claude-sonnet-4-6":   return 0  # OAuth primary
        if pid == "anthropic/claude-sonnet-4-5":   return 1
        if "sonnet-4-6" in m["id"].lower():        return 2
        if "sonnet-4-5" in m["id"].lower():        return 3
        if "glm-4.7" in m["id"].lower():           return 4
        return 5
    complex_order = sorted(by_tier["COMPLEX"], key=complex_sort)

    # REASONING tier: QwQ/R1-32B first
    def reasoning_sort(m):
        if "qwq" in m["id"].lower():
            return 0
        if "r1-distill-qwen-32b" in m["id"].lower():
            return 1
        if "r1-distill-qwen-14b" in m["id"].lower():
            return 2
        if "kimi" in m["id"].lower():
            return 3
        return 4
    reasoning_order = sorted(by_tier["REASONING"], key=reasoning_sort)

    # CRITICAL tier: Opus 4.6 first
    def critical_sort(m):
        pid = full_id(m)
        if pid == "anthropic/claude-opus-4-6":   return 0  # OAuth primary
        if pid == "anthropic/claude-opus-4-5":   return 1
        if "opus-4-6" in m["id"].lower():        return 2
        if "opus-4-5" in m["id"].lower():        return 3
        if "253b" in m["id"].lower():            return 4
        return 5
    critical_order = sorted(by_tier["CRITICAL"], key=critical_sort)

    return {
        "SIMPLE": {
            "description": "Monitoring, summaries, checks — free/cheap/fast models",
            "primary": full_id(simple_order[0]) if simple_order else "",
            "fallbacks": [full_id(m) for m in simple_order[1:]] + [full_id(m) for m in medium_order[:2]],
        },
        "MEDIUM": {
            "description": "Code fixes, research, analysis — mid-range models",
            "primary": full_id(medium_order[0]) if medium_order else "",
            "fallbacks": [full_id(m) for m in medium_order[1:]] + [full_id(m) for m in complex_order[:1]],
        },
        "COMPLEX": {
            "description": "Features, architecture, debugging — high quality models",
            "primary": full_id(complex_order[0]) if complex_order else "",
            "fallbacks": [full_id(m) for m in complex_order[1:]] + [full_id(m) for m in critical_order[:1]],
        },
        "REASONING": {
            "description": "Proofs, formal logic, deep analysis — thinking models",
            "primary": full_id(reasoning_order[0]) if reasoning_order else "",
            "fallbacks": [full_id(m) for m in reasoning_order[1:]] + [full_id(m) for m in complex_order[:1]],
        },
        "CRITICAL": {
            "description": "Security, production, high-stakes — best available models",
            "primary": full_id(critical_order[0]) if critical_order else "",
            "fallbacks": [full_id(m) for m in critical_order[1:]] + [full_id(m) for m in complex_order[:1]],
        },
    }


def main():
    with open(CONFIG) as f:
        config = json.load(f)

    models = config.get("models", [])
    print(f"Fixing tiers for {len(models)} models...\n")

    # Assign tiers
    tier_counts = {}
    for m in models:
        m["tier"] = assign_tier(m)
        tier_counts[m["tier"]] = tier_counts.get(m["tier"], 0) + 1

    # Print assignments
    for tier in ["SIMPLE", "MEDIUM", "COMPLEX", "REASONING", "CRITICAL"]:
        print(f"  {tier}: {tier_counts.get(tier, 0)} models")
        for m in models:
            if m["tier"] == tier:
                print(f"    - {full_id(m)}")

    # Build tier configs
    config["tiers"] = build_tiers(models)
    config["models"] = models

    print("\nTier primary models:")
    for tier, cfg in config["tiers"].items():
        print(f"  {tier}: {cfg['primary']}")
        if cfg["fallbacks"]:
            print(f"    fallbacks: {cfg['fallbacks'][:3]}")

    with open(CONFIG, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ Saved to {CONFIG}")


if __name__ == "__main__":
    main()
