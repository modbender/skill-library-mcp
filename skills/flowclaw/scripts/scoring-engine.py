#!/usr/bin/env python3
"""FlowClaw Scoring Engine — EDF-based urgency scoring for LLM account routing.

Reads usage JSON from stdin (produced by usage collector), computes urgency
scores for each account, and outputs a ranked list with recommended routing.

Providers: Anthropic, Google Gemini CLI, Google Antigravity, OpenAI Codex,
           GitHub Copilot, Ollama

Scoring based on Earliest Deadline First + perishable inventory management:
  score = urgency * 0.30 + availability * 0.25 + proximity * 0.15
        + weekly_headroom * 0.20 + tier_bonus * 0.10

The weekly_headroom factor ensures accounts near their weekly limit are
deprioritized — prefer the account with more long-term capacity even if
both have available session capacity.
"""

import json
import sys
from dataclasses import dataclass, field

# ── Provider tier bonuses (cost optimization) ─────────────────────────
TIER_BONUS = {
    "google": 0.8,             # Free tier (Gemini CLI / Antigravity), prefer strongly
    "google-gemini-cli": 0.5,  # Paid Gemini CLI, still preferred
    "google-antigravity": 0.8, # Free Antigravity tier
    "anthropic": 0.0,          # Subscription baseline
    "openai": 0.0,             # Codex subscription baseline
    "github-copilot": 0.0,     # Copilot subscription baseline
    "ollama": -0.3,            # Quality penalty, but always available
}

TIER_EXTRA_PENALTY = -1.0  # Heavy penalty when burning extra usage $$$

# ── Scoring weights ───────────────────────────────────────────────────
W_URGENCY = 0.30       # Credits wasting per hour (session-level)
W_AVAILABILITY = 0.25  # Remaining capacity (dampened)
W_PROXIMITY = 0.15     # How close to reset deadline
W_WEEKLY = 0.20        # Long-term headroom (7d usage)
W_TIER = 0.10          # Provider cost preference

@dataclass
class ScoredAccount:
    provider: str
    account: str
    email: str
    profile_id: str       # OpenClaw profile ID
    model: str            # OpenClaw model string
    score: float
    available: bool
    reason: str
    utilization: float
    resets_in: str
    family: str = field(default="other")

def parse_reset_hours(resets_in: str) -> float:
    """Parse human-readable reset string to hours. Returns 999 if unknown."""
    if not resets_in or resets_in in ("—", "unknown", ""):
        return 999.0
    hours = 0.0
    parts = resets_in.split()
    for part in parts:
        if part.endswith("d"):
            hours += float(part[:-1]) * 24
        elif part.endswith("h"):
            hours += float(part[:-1])
        elif part.endswith("m"):
            hours += float(part[:-1]) / 60
    return max(hours, 0.01)

def model_family(model: str) -> str:
    """Classify a model into a capability family for fair comparison."""
    m = model.lower()
    if "opus" in m:
        return "opus"
    elif "sonnet" in m:
        return "sonnet"
    elif "gpt-5.2" in m or "gpt-5" in m and "mini" not in m:
        return "gpt5"
    elif "gpt-5-mini" in m or "gpt-4o" in m:
        return "gpt5-mini"
    elif "gemini-3-pro" in m or "gemini-pro" in m:
        return "gemini-pro"
    elif "gemini-3-flash" in m or "gemini-flash" in m:
        return "gemini-flash"
    elif "ollama" in m:
        return "local"
    return "other"


def score_anthropic(account: dict) -> list[ScoredAccount]:
    """Score an Anthropic Max account."""
    email = account.get("email", "?")
    name = account.get("account", "?")
    profile_id = f"anthropic:{name}"
    model = "anthropic/claude-opus-4-6"

    session = account.get("session", {})
    weekly = account.get("weekly", {})
    extra = account.get("extra", {})

    s_util = session.get("utilization", 0)
    w_util = weekly.get("utilization", 0)
    s_reset_h = parse_reset_hours(session.get("resets_in", ""))
    w_reset_h = parse_reset_hours(weekly.get("resets_in", ""))

    if s_util >= 100:
        return [ScoredAccount(
            provider="anthropic", account=name, email=email,
            profile_id=profile_id, model=model,
            score=0.0, available=False,
            reason=f"5h session limit (resets in {session.get('resets_in', '?')})",
            utilization=s_util, resets_in=session.get("resets_in", "?")
        )]
    if w_util >= 100:
        return [ScoredAccount(
            provider="anthropic", account=name, email=email,
            profile_id=profile_id, model=model,
            score=0.0, available=False,
            reason=f"7d weekly limit (resets in {weekly.get('resets_in', '?')})",
            utilization=w_util, resets_in=weekly.get("resets_in", "?")
        )]

    s_remaining = (100 - s_util) / 100
    w_remaining = (100 - w_util) / 100
    s_pressure = s_util / max(s_reset_h, 0.01)
    w_pressure = w_util / max(w_reset_h, 0.01)

    # Session urgency (5h window) — how fast are session credits expiring?
    if s_pressure > w_pressure:
        remaining, reset_h = s_remaining, s_reset_h
        window_h = 5.0
        resets_in = session.get("resets_in", "?")
    else:
        remaining, reset_h = w_remaining, w_reset_h
        window_h = 168.0
        resets_in = weekly.get("resets_in", "?")

    urgency = remaining / reset_h if reset_h > 0 else 0
    availability = remaining ** 0.5
    proximity = max(0, 1 - reset_h / window_h)

    # Weekly headroom — how much 7-day capacity remains?
    # An account at 96% weekly should be heavily deprioritized vs 51%...
    # UNLESS the weekly window is about to reset (≤12h) — then burn it!
    weekly_headroom = w_remaining  # 1.0 = fresh, 0.0 = exhausted
    if w_reset_h <= 6:
        # About to reset — ignore weekly headroom entirely, burn away
        weekly_headroom = 1.0
    elif w_reset_h <= 12:
        # Transitional zone: linearly reduce the penalty from 12h→6h
        # At 12h: use actual headroom; at 6h: treat as fully fresh
        blend = (w_reset_h - 6) / 6  # 1.0 at 12h, 0.0 at 6h
        weekly_headroom = w_remaining * blend + 1.0 * (1 - blend)

    tier = TIER_BONUS.get("anthropic", 0)
    if extra.get("enabled") and extra.get("utilization", 0) >= 100:
        tier += TIER_EXTRA_PENALTY * 0.3

    score = (
        urgency * W_URGENCY +
        availability * W_AVAILABILITY +
        proximity * W_PROXIMITY +
        weekly_headroom * W_WEEKLY +
        tier * W_TIER
    )

    return [ScoredAccount(
        provider="anthropic", account=name, email=email,
        profile_id=profile_id, model=model,
        score=round(score, 4), available=True,
        reason=f"5h:{s_util}% 7d:{w_util}%",
        utilization=max(s_util, w_util), resets_in=resets_in
    )]


def score_google(account: dict) -> list[ScoredAccount]:
    """Score a Google account (via Gemini CLI).
    
    Google provides access to both Claude and Gemini models through a single account.
    OpenClaw provider: google-gemini-cli/*
    """
    email = account.get("email", "?")
    provider_prefix = "google-gemini-cli"
    
    results = []
    models = [
        ("claude", f"{provider_prefix}/claude-opus-4-6-thinking", "🤖"),
        ("gemini_pro", f"{provider_prefix}/gemini-3-pro-high", "♊"),
        ("gemini_flash", f"{provider_prefix}/gemini-3-flash", "⚡"),
    ]

    for key, model, emoji in models:
        data = account.get(key, {})
        util = data.get("used_pct", 0)
        resets_in = data.get("resets_in", "?")
        reset_h = parse_reset_hours(resets_in)

        if util >= 100:
            results.append(ScoredAccount(
                provider="google", account=f"google-{key}", email=email,
                profile_id=f"{provider_prefix}:{email}", model=model,
                score=0.0, available=False,
                reason=f"Limit reached (resets in {resets_in})",
                utilization=util, resets_in=resets_in
            ))
            continue

        remaining = (100 - util) / 100
        urgency = remaining / reset_h if reset_h > 0 else 0
        availability = remaining ** 0.5
        proximity = max(0, 1 - reset_h / 12.0)
        weekly_headroom = remaining  # single-window provider
        tier = TIER_BONUS.get("google", TIER_BONUS.get(provider_prefix, 0))

        score = (
            urgency * W_URGENCY +
            availability * W_AVAILABILITY +
            proximity * W_PROXIMITY +
            weekly_headroom * W_WEEKLY +
            tier * W_TIER
        )

        results.append(ScoredAccount(
            provider="google", account=f"google-{key}", email=email,
            profile_id=f"{provider_prefix}:{email}", model=model,
            score=round(score, 4), available=True,
            reason=f"{util}% used",
            utilization=util, resets_in=resets_in
        ))

    return results


def score_openai(account: dict) -> list[ScoredAccount]:
    """Score an OpenAI account. API-based billing (no hard rate windows like Anthropic)."""
    source = account.get("source", "api")
    today_tokens = account.get("today_tokens", 0)
    available = account.get("available", True)
    error = account.get("error", "")
    
    if error:
        return [ScoredAccount(
            provider="openai", account="openai-api", email="api",
            profile_id="openai:default", model="openai/gpt-5.2",
            score=0.0, available=False,
            reason=f"Error: {error}",
            utilization=0, resets_in="—"
        )]
    
    # OpenAI is pay-per-token — always available if key works
    # Lower tier bonus than free Google, but no rate limits
    tier = TIER_BONUS.get("openai", 0)
    score = (0.5 * W_URGENCY) + (1.0 * W_AVAILABILITY) + (0.0 * W_PROXIMITY) + (1.0 * W_WEEKLY) + (tier * W_TIER)
    
    return [ScoredAccount(
        provider="openai", account="openai-api", email="api",
        profile_id="openai:default", model="openai/gpt-5.2",
        score=round(score, 4), available=available,
        reason=f"API ({today_tokens // 1000}K tokens today)",
        utilization=0, resets_in="never"
    )]


def score_ollama(account: dict) -> list[ScoredAccount]:
    """Score Ollama local model. Always available, quality penalty."""
    model = account.get("model", "unknown")
    size = account.get("size", "?")
    tier = TIER_BONUS.get("ollama", -0.3)
    score = (0.0 * W_URGENCY) + (1.0 * W_AVAILABILITY) + (0.0 * W_PROXIMITY) + (1.0 * W_WEEKLY) + (tier * W_TIER)
    return [ScoredAccount(
        provider="ollama", account=f"local-{model}", email="localhost",
        profile_id=f"ollama:{model}", model=f"ollama/{model}",
        score=round(score, 4), available=True,
        reason=f"Local ({size})",
        utilization=0, resets_in="never"
    )]


def score_all(data: dict) -> list[ScoredAccount]:
    """Score all accounts from usage JSON."""
    scored = []
    for entry in data.get("providers", []):
        provider = entry.get("provider", "")
        if provider == "anthropic":
            scored.extend(score_anthropic(entry))
        elif provider == "google":
            scored.extend(score_google(entry))
        elif provider == "openai":
            scored.extend(score_openai(entry))
        elif provider == "ollama":
            scored.extend(score_ollama(entry))
    for s in scored:
        s.family = model_family(s.model)
    return sorted(scored, key=lambda s: s.score, reverse=True)


def best_per_family(scored: list[ScoredAccount]) -> dict[str, ScoredAccount]:
    """Return the best available account for each model family."""
    best = {}
    for s in scored:
        fam = model_family(s.model)
        if fam not in best and s.available:
            best[fam] = s
    return best


def run_tests():
    """Built-in unit tests."""
    print("Running scoring engine tests...\n")

    # Test 1: Anthropic 100% session → blocked
    result = score_anthropic({"account": "test", "email": "t@t.com",
        "session": {"utilization": 100, "resets_in": "2h 30m"},
        "weekly": {"utilization": 41, "resets_in": "6d 12h"},
        "extra": {"enabled": True, "utilization": 100}})
    assert not result[0].available
    assert result[0].score == 0.0
    print("  ✅ Test 1: Anthropic 100% session → blocked")

    # Test 2: High urgency (resets soon)
    result = score_anthropic({"account": "soon", "email": "t@t.com",
        "session": {"utilization": 50, "resets_in": "10m"},
        "weekly": {"utilization": 20, "resets_in": "5d"},
        "extra": {"enabled": False}})
    soon_score = result[0].score
    print(f"  ✅ Test 2: 50% used, resets in 10m → score={soon_score:.4f}")

    # Test 3: Low urgency (resets far)
    result = score_anthropic({"account": "late", "email": "t@t.com",
        "session": {"utilization": 50, "resets_in": "4h 50m"},
        "weekly": {"utilization": 50, "resets_in": "6d"},
        "extra": {"enabled": False}})
    late_score = result[0].score
    assert soon_score > late_score
    print(f"  ✅ Test 3: 50% used, resets in 6d → score={late_score:.4f}")

    # Test 4: Google 0% → high score (free tier bonus)
    result = score_google({"email": "t@t.com",
        "claude": {"used_pct": 0, "resets_in": "12h"},
        "gemini_pro": {"used_pct": 0, "resets_in": "12h"},
        "gemini_flash": {"used_pct": 0, "resets_in": "12h"}})
    assert all(r.available for r in result)
    assert all(r.score > 0 for r in result), "Google free tier should score positive"
    print(f"  ✅ Test 4: Google 0% → scores={[r.score for r in result]}")

    # Test 5: Google mixed usage
    result = score_google({"email": "t@t.com",
        "claude": {"used_pct": 100, "resets_in": "3h"},
        "gemini_pro": {"used_pct": 50, "resets_in": "6h"},
        "gemini_flash": {"used_pct": 0, "resets_in": "12h"}})
    assert not result[0].available
    assert result[1].available
    assert "google-gemini-cli" in result[0].profile_id
    print(f"  ✅ Test 5: Google mixed → Claude blocked, Gemini available")

    # Test 6: OpenAI always available
    result = score_openai({"source": "api", "today_tokens": 50000, "available": True})
    assert result[0].available
    assert result[0].score > 0
    print(f"  ✅ Test 6: OpenAI API → score={result[0].score:.4f}")

    # Test 7: Family classification
    assert model_family("anthropic/claude-opus-4-6") == "opus"
    assert model_family("google-gemini-cli/claude-opus-4-6-thinking") == "opus"
    assert model_family("google-gemini-cli/gemini-3-pro-high") == "gemini-pro"
    assert model_family("openai/gpt-5.2") == "gpt5"
    assert model_family("openai/gpt-5-mini") == "gpt5-mini"
    print(f"  ✅ Test 7: Model family classification correct")

    # Test 8: Cross-provider family routing
    data = {"providers": [
        {"provider": "anthropic", "account": "work", "email": "w@t.com",
         "session": {"utilization": 80, "resets_in": "1h"},
         "weekly": {"utilization": 60, "resets_in": "3d"},
         "extra": {"enabled": False}},
        {"provider": "google", "email": "g@t.com",
         "claude": {"used_pct": 10, "resets_in": "12h"},
         "gemini_pro": {"used_pct": 5, "resets_in": "12h"},
         "gemini_flash": {"used_pct": 0, "resets_in": "12h"}},
    ]}
    scored = score_all(data)
    families = best_per_family(scored)
    assert "opus" in families, "Should have opus family"
    assert "gemini-pro" in families, "Should have gemini-pro family"
    print(f"  ✅ Test 8: Cross-provider family routing → {list(families.keys())}")

    print("\n✅ All tests passed!")


def main():
    if "--test" in sys.argv:
        run_tests()
        return

    if "--file" in sys.argv:
        idx = sys.argv.index("--file") + 1
        data = json.load(open(sys.argv[idx]))
    else:
        data = json.load(sys.stdin)

    scored = score_all(data)
    output_format = "json" if "--json" in sys.argv else "text"

    if output_format == "json":
        family_best = best_per_family(scored)
        result = {
            "ranked": [{
                "rank": i + 1,
                "provider": s.provider,
                "account": s.account,
                "email": s.email,
                "profile_id": s.profile_id,
                "model": s.model,
                "family": s.family,
                "score": s.score,
                "available": s.available,
                "reason": s.reason,
                "utilization": s.utilization,
                "resets_in": s.resets_in,
            } for i, s in enumerate(scored)],
            "recommended_primary": next((s.model for s in scored if s.available), None),
            "recommended_per_family": {fam: s.model for fam, s in family_best.items()},
            "recommended_anthropic_order": [s.profile_id for s in scored if s.provider == "anthropic"],
        }
        print(json.dumps(result, indent=2))
    else:
        print("🧠 FlowClaw Scoring\n")
        for i, s in enumerate(scored):
            status = "✅" if s.available else "🚫"
            print(f"  #{i+1}  {status} {s.account:15s}  [{s.family:12s}]  score={s.score:.4f}  {s.reason}")
            print(f"       model: {s.model}")
            print(f"       profile: {s.profile_id}  resets: {s.resets_in}")
            print()

        best = next((s for s in scored if s.available), None)
        if best:
            print(f"  🎯 Recommended: {best.account} ({best.model})")
        else:
            print("  ⚠️  All accounts exhausted!")


if __name__ == "__main__":
    main()
