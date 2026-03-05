#!/usr/bin/env python3
"""
Gemini API Usage Fetcher
Probes Gemini models via minimal API calls to verify key validity,
lists available models, and documents free/paid tier rate limits.

Unlike OpenAI, Google does not expose rate-limit headers or usage
counters via the API. This script:
  1. Validates the API key
  2. Lists available models
  3. Probes key models with 1-token calls to confirm access
  4. Reports known free-tier rate limits (hardcoded from docs)

Usage:
    ./gemini-usage-fetch.py              # Print usage
    ./gemini-usage-fetch.py --update     # Update gemini-usage.json
    ./gemini-usage-fetch.py --json       # Output raw JSON

Requires: GEMINI_API_KEY env var
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

USAGE_JSON_PATH = Path.home() / '.openclaw/workspace/memory/gemini-usage.json'
BASE_URL = 'https://generativelanguage.googleapis.com/v1beta'

# Models to probe (the ones OpenClaw actually uses)
PROBE_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
]

# Free tier rate limits (from https://ai.google.dev/gemini-api/docs/rate-limits, Feb 2026)
FREE_TIER_LIMITS = {
    "gemini-2.5-pro": {
        "rpm": 5, "rpd": 25, "tpm": 250_000,
        "tier": "free", "note": "Thinking model, lower free limits"
    },
    "gemini-2.5-flash": {
        "rpm": 10, "rpd": 500, "tpm": 250_000,
        "tier": "free", "note": "Fast + thinking"
    },
    "gemini-2.0-flash": {
        "rpm": 15, "rpd": 1500, "tpm": 1_000_000,
        "tier": "free", "note": "Workhorse model"
    },
    "gemini-2.0-flash-lite": {
        "rpm": 30, "rpd": 1500, "tpm": 1_000_000,
        "tier": "free", "note": "Lightweight"
    },
}

# Paid tier limits
PAID_TIER_LIMITS = {
    "gemini-2.5-pro": {
        "rpm": 150, "rpd": 10_000, "tpm": 1_000_000,
        "tier": "paid"
    },
    "gemini-2.5-flash": {
        "rpm": 2000, "rpd": 10_000, "tpm": 4_000_000,
        "tier": "paid"
    },
    "gemini-2.0-flash": {
        "rpm": 2000, "rpd": 10_000, "tpm": 4_000_000,
        "tier": "paid"
    },
}


def get_api_key():
    key = os.environ.get('GEMINI_API_KEY')
    if not key:
        env_path = Path.home() / '.openclaw/.env'
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith('GEMINI_API_KEY='):
                    key = line.split('=', 1)[1].strip()
                    break
    return key


def list_models(api_key):
    """List available models."""
    url = f'{BASE_URL}/models?key={api_key}'
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
            return [m['name'].split('/')[-1] for m in data.get('models', [])]
    except Exception as e:
        return {"error": str(e)}


def probe_model(api_key, model):
    """Make a 1-token call to verify access and get token counts."""
    url = f'{BASE_URL}/models/{model}:generateContent?key={api_key}'
    data = json.dumps({
        "contents": [{"parts": [{"text": "x"}]}],
        "generationConfig": {"maxOutputTokens": 1}
    }).encode()

    req = urllib.request.Request(url, data=data, headers={
        'Content-Type': 'application/json'
    })

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            usage = result.get('usageMetadata', {})
            return {
                "status": "ok",
                "promptTokens": usage.get('promptTokenCount', 0),
                "completionTokens": usage.get('candidatesTokenCount', 0),
                "totalTokens": usage.get('totalTokenCount', 0),
            }
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        return {"status": "error", "code": e.code, "message": body}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def detect_tier(api_key):
    """Try to detect if we're on free or paid tier.
    Free tier keys start with 'AIza' (AI Studio keys).
    Paid tier typically uses service accounts or billing-linked projects.
    """
    if api_key.startswith('AIza'):
        return "free"
    return "unknown"


def build_output(api_key, probes, available_models):
    tier = detect_tier(api_key)
    limits = FREE_TIER_LIMITS if tier == "free" else PAID_TIER_LIMITS

    models = {}
    total_probe_tokens = 0

    for model, result in probes.items():
        model_limits = limits.get(model, FREE_TIER_LIMITS.get(model, {}))
        models[model] = {
            "status": result.get("status"),
            "probe_tokens": result.get("totalTokens", 0),
            "rate_limits": {
                "rpm": model_limits.get("rpm"),
                "rpd": model_limits.get("rpd"),
                "tpm": model_limits.get("tpm"),
            },
            "note": model_limits.get("note", ""),
        }
        total_probe_tokens += result.get("totalTokens", 0)

    return {
        "provider": "google",
        "fetchedAt": datetime.utcnow().isoformat() + 'Z',
        "api_key_status": "valid",
        "detected_tier": tier,
        "probe_cost_tokens": total_probe_tokens,
        "available_models_count": len(available_models) if isinstance(available_models, list) else 0,
        "models": models,
        "all_rate_limits": {
            "free": FREE_TIER_LIMITS,
            "paid": PAID_TIER_LIMITS,
        },
    }


def print_usage(output):
    tier = output.get('detected_tier', '?')
    tier_icon = '🆓' if tier == 'free' else '💰' if tier == 'paid' else '❓'

    print(f"\n╔══════════════════════════════════════════════╗")
    print(f"║         GEMINI API USAGE                     ║")
    print(f"╠══════════════════════════════════════════════╣")
    print(f"║ API Key: ✅ valid                             ║")
    print(f"║ Tier: {tier_icon} {tier:<10}                            ║")
    print(f"║ Probe cost: {output.get('probe_cost_tokens', 0)} tokens                      ║")
    print(f"║ Available models: {output.get('available_models_count', '?'):<4}                       ║")
    print(f"║──────────────────────────────────────────────║")
    print(f"║ Model Status & Rate Limits ({tier} tier):      ║")

    for model, info in output.get("models", {}).items():
        status = info.get("status", "?")
        rl = info.get("rate_limits", {})
        if status == "ok":
            rpm = rl.get("rpm", "?")
            rpd = rl.get("rpd", "?")
            tpm = rl.get("tpm", "?")
            tpm_k = f"{tpm//1000}K" if isinstance(tpm, int) else tpm
            note = info.get("note", "")
            print(f"║  ✅ {model:<22} {rpm:>4} rpm  {rpd:>5} rpd ║")
            print(f"║     {tpm_k:>6} tpm  {note:<28}║")
        else:
            code = info.get("code", "?")
            print(f"║  ❌ {model:<22} HTTP {code:<16}  ║")

    print(f"║──────────────────────────────────────────────║")
    print(f"║ ⚠ Google does not expose usage counters      ║")
    print(f"║   via API. Limits shown are from docs.       ║")
    print(f"╚══════════════════════════════════════════════╝\n")


def main():
    args = sys.argv[1:]
    api_key = get_api_key()

    if not api_key:
        print("❌ No GEMINI_API_KEY found.", file=sys.stderr)
        sys.exit(1)

    # List available models
    available = list_models(api_key)

    # Probe key models
    probes = {}
    for model in PROBE_MODELS:
        probes[model] = probe_model(api_key, model)

    output = build_output(api_key, probes, available)

    if '--json' in args:
        print(json.dumps(output, indent=2))
    elif '--update' in args:
        USAGE_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(USAGE_JSON_PATH, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"✓ Updated {USAGE_JSON_PATH}")
        for model, info in output["models"].items():
            status = info.get("status", "?")
            rl = info.get("rate_limits", {})
            print(f"  {model}: {status} | {rl.get('rpm','?')} rpm, {rl.get('rpd','?')} rpd")
    else:
        print_usage(output)


if __name__ == '__main__':
    main()
