#!/usr/bin/env python3
"""Model Audit — LLM stack pricing audit via OpenRouter."""

import argparse
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

# Category keywords for classification
CATEGORIES = {
    "reasoning": ["o1", "o3", "deepseek-r1", "qwq", "reasoning"],
    "code": ["code", "deepseek-coder", "codestral", "starcoder"],
    "fast": ["flash", "mini", "haiku", "nano", "instant", "8b", "small"],
    "cheap": ["flash", "mini", "haiku", "nano", "free"],
    "vision": ["vision", "4o", "gemini", "claude-3", "claude-sonnet", "claude-opus", "gpt-4o"],
    "long_context": ["long", "128k", "200k", "1m", "gemini"],
}


def get_api_key():
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        print("ERROR: OPENROUTER_API_KEY not set.", file=sys.stderr)
        sys.exit(1)
    return key


def fetch_models(api_key):
    """Fetch all models from OpenRouter."""
    req = Request(
        OPENROUTER_MODELS_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data.get("data", [])
    except (HTTPError, URLError) as e:
        print(f"ERROR: Failed to fetch models: {e}", file=sys.stderr)
        sys.exit(1)


def get_pricing(model_data):
    """Extract pricing from model data."""
    pricing = model_data.get("pricing", {})
    prompt = float(pricing.get("prompt", "0") or "0")
    completion = float(pricing.get("completion", "0") or "0")
    # OpenRouter returns per-token, convert to per-1M
    return {
        "input_per_1m": prompt * 1_000_000,
        "output_per_1m": completion * 1_000_000,
    }


def classify_model(model_id, model_name):
    """Classify a model into categories."""
    cats = []
    combined = f"{model_id} {model_name}".lower()
    for cat, keywords in CATEGORIES.items():
        if any(kw in combined for kw in keywords):
            cats.append(cat)
    return cats if cats else ["general"]


def find_config_models():
    """Try to find configured models from openclaw.json."""
    for path in [
        "/root/.openclaw/openclaw.json",
        "/home/node/.openclaw/openclaw.json",
        os.path.expanduser("~/.openclaw/openclaw.json"),
    ]:
        if os.path.isfile(path):
            try:
                with open(path) as f:
                    config = json.load(f)
                models = set()
                # Check defaultModel
                if config.get("defaultModel"):
                    models.add(config["defaultModel"])
                # Check channel configs
                for ch in config.get("channels", []):
                    if ch.get("model"):
                        models.add(ch["model"])
                # Check agents
                for ag in config.get("agents", []):
                    if ag.get("model"):
                        models.add(ag["model"])
                return list(models)
            except (json.JSONDecodeError, IOError):
                continue
    return []


def format_price(price):
    """Format price nicely."""
    if price == 0:
        return "FREE"
    if price < 0.01:
        return f"${price:.4f}"
    return f"${price:.2f}"


def main():
    parser = argparse.ArgumentParser(description="LLM Stack Audit")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--models", help="Comma-separated models to audit")
    parser.add_argument("--top", action="store_true", help="Show top models by category")
    parser.add_argument("--compare", nargs=2, help="Compare two models", metavar="MODEL")
    args = parser.parse_args()

    api_key = get_api_key()
    all_models = fetch_models(api_key)

    # Build lookup
    model_map = {}
    for m in all_models:
        model_map[m["id"]] = m

    # Determine which models to audit
    if args.models:
        user_models = [m.strip() for m in args.models.split(",")]
    else:
        user_models = find_config_models()

    # Compare mode
    if args.compare:
        m1_id, m2_id = args.compare
        m1 = model_map.get(m1_id)
        m2 = model_map.get(m2_id)
        if not m1:
            print(f"Model not found: {m1_id}", file=sys.stderr)
            sys.exit(1)
        if not m2:
            print(f"Model not found: {m2_id}", file=sys.stderr)
            sys.exit(1)
        p1 = get_pricing(m1)
        p2 = get_pricing(m2)
        if args.json_output:
            print(json.dumps({"models": [
                {"id": m1_id, "name": m1.get("name", ""), **p1},
                {"id": m2_id, "name": m2.get("name", ""), **p2},
            ]}, indent=2))
        else:
            print(f"\n{'Model':<40} {'Input/1M':>10} {'Output/1M':>10}")
            print("-" * 62)
            print(f"{m1_id:<40} {format_price(p1['input_per_1m']):>10} {format_price(p1['output_per_1m']):>10}")
            print(f"{m2_id:<40} {format_price(p2['input_per_1m']):>10} {format_price(p2['output_per_1m']):>10}")
            ratio = (p1['input_per_1m'] / p2['input_per_1m']) if p2['input_per_1m'] > 0 else 0
            if ratio > 1:
                print(f"\n{m1_id} is {ratio:.1f}x more expensive (input)")
            elif ratio > 0:
                print(f"\n{m1_id} is {1/ratio:.1f}x cheaper (input)")
        return

    # Top models by category
    if args.top:
        # Find best in each category
        cat_models = {cat: [] for cat in CATEGORIES}
        for m in all_models:
            pricing = get_pricing(m)
            cats = classify_model(m["id"], m.get("name", ""))
            for cat in cats:
                if cat in cat_models:
                    cat_models[cat].append({
                        "id": m["id"],
                        "name": m.get("name", ""),
                        **pricing,
                    })

        if args.json_output:
            # Sort each category by input price
            for cat in cat_models:
                cat_models[cat].sort(key=lambda x: x["input_per_1m"])
                cat_models[cat] = cat_models[cat][:5]
            print(json.dumps(cat_models, indent=2))
        else:
            for cat, models in cat_models.items():
                models.sort(key=lambda x: x["input_per_1m"])
                print(f"\n── Top {cat.upper()} Models ──")
                print(f"{'Model':<45} {'Input/1M':>10} {'Output/1M':>10}")
                print("-" * 67)
                for m in models[:5]:
                    print(f"{m['id']:<45} {format_price(m['input_per_1m']):>10} {format_price(m['output_per_1m']):>10}")
        return

    # Main audit
    if not user_models:
        user_models = [
            "anthropic/claude-opus-4-6",
            "anthropic/claude-sonnet-4",
            "openai/gpt-4o",
        ]
        if not args.json_output:
            print("ℹ️  No configured models found, auditing common defaults.")

    # Analyze user models
    audit_results = []
    for mid in user_models:
        m = model_map.get(mid)
        if m:
            pricing = get_pricing(m)
            cats = classify_model(mid, m.get("name", ""))
            audit_results.append({
                "id": mid,
                "name": m.get("name", mid),
                "categories": cats,
                **pricing,
            })
        else:
            audit_results.append({
                "id": mid,
                "name": mid,
                "categories": ["unknown"],
                "input_per_1m": 0,
                "output_per_1m": 0,
                "warning": "Model not found on OpenRouter",
            })

    # Find alternatives
    recommendations = []
    user_cats = set()
    for r in audit_results:
        user_cats.update(r["categories"])

    # For each category, find cheaper alternatives
    for cat in ["reasoning", "code", "fast"]:
        user_in_cat = [r for r in audit_results if cat in r["categories"]]
        if not user_in_cat:
            recommendations.append(f"💡 No {cat} model configured — consider adding one")
            continue

        cheapest_user = min(user_in_cat, key=lambda x: x["input_per_1m"])
        # Find cheaper alternatives
        for m in all_models:
            m_cats = classify_model(m["id"], m.get("name", ""))
            if cat in m_cats:
                p = get_pricing(m)
                if 0 < p["input_per_1m"] < cheapest_user["input_per_1m"] * 0.5:
                    if m["id"] not in user_models:
                        ratio = cheapest_user["input_per_1m"] / p["input_per_1m"] if p["input_per_1m"] > 0 else 0
                        recommendations.append(
                            f"💡 [{cat}] {m['id']} is {ratio:.0f}x cheaper than {cheapest_user['id']} "
                            f"({format_price(p['input_per_1m'])}/{format_price(p['output_per_1m'])} per 1M)"
                        )
                        break

    if args.json_output:
        print(json.dumps({
            "models": audit_results,
            "recommendations": recommendations,
            "total_models_available": len(all_models),
        }, indent=2))
    else:
        print("\n═══ LLM Stack Audit ═══")
        print(f"Available models on OpenRouter: {len(all_models)}\n")
        print("Your Models:")
        print(f"  {'Model':<45} {'Input/1M':>10} {'Output/1M':>10} {'Categories'}")
        print("  " + "-" * 85)
        for r in audit_results:
            cats = ", ".join(r["categories"])
            warn = f" ⚠️ {r['warning']}" if r.get("warning") else ""
            print(f"  {r['id']:<45} {format_price(r['input_per_1m']):>10} {format_price(r['output_per_1m']):>10} {cats}{warn}")

        if recommendations:
            print("\nRecommendations:")
            for rec in recommendations[:10]:
                print(f"  {rec}")

        print("\n═══════════════════════")


if __name__ == "__main__":
    main()
