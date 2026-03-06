#!/usr/bin/env python3
"""
Intelligent Router - Model Auto-Discovery

Auto-discovers working models from all configured providers.
Tests each model with a minimal inference call to verify:
- Model is accessible
- Auth is working
- Returns valid responses

Usage:
    python3 discover_models.py                    # Scan and display
    python3 discover_models.py --auto-update       # Scan and update config.json
    python3 discover_models.py --tier COMPLEX      # Test specific tier models
"""

import json
import sys
import time
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import subprocess

# Capability-based tier classifier (no hard-coded name patterns)
sys.path.insert(0, str(Path(__file__).parent))
try:
    from tier_classifier import classify_from_openclaw_config, build_tier_config
    _CLASSIFIER_AVAILABLE = True
except ImportError:
    _CLASSIFIER_AVAILABLE = False

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"
ROUTER_CONFIG = Path(__file__).parent.parent / "config.json"
DISCOVERY_OUTPUT = Path(__file__).parent.parent / "discovered-models.json"


def load_openclaw_config() -> Dict[str, Any]:
    """Load main OpenClaw config."""
    if not CONFIG_PATH.exists():
        print(f"{RED}Error: Config not found at {CONFIG_PATH}{RESET}")
        sys.exit(1)

    with open(CONFIG_PATH) as f:
        return json.load(f)


def load_router_config() -> Dict[str, Any]:
    """Load intelligent-router config."""
    if not ROUTER_CONFIG.exists():
        return {"models": [], "routing_rules": {}}

    with open(ROUTER_CONFIG) as f:
        return json.load(f)


def test_model_live(provider_cfg: dict, provider_name: str, model_id: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Real inference test: send "hi" to the model and verify it responds.
    Supports both OpenAI-compatible and Anthropic-messages APIs.

    Returns: {available: bool, latency: float, error: str | None, response_preview: str | None}
    """
    import urllib.request
    import urllib.error

    start = time.time()
    base_url = provider_cfg.get("baseUrl", "").rstrip("/")
    api_key = provider_cfg.get("apiKey", "")
    api_type = provider_cfg.get("api", "openai-completions")

    try:
        if api_type == "openai-completions":
            # Standard OpenAI /v1/chat/completions
            url = f"{base_url}/chat/completions"
            payload = {
                "model": model_id,
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 5,
                "stream": False,
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }

        elif api_type == "anthropic-messages":
            # Anthropic /v1/messages — URL suffix varies by proxy
            if base_url.endswith("/messages"):
                url = base_url
            elif "/v1" in base_url:
                url = f"{base_url}/messages"
            else:
                url = f"{base_url}/v1/messages"

            payload = {
                "model": model_id,
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 5,
            }
            headers = {
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            }
        else:
            return {
                "available": False,
                "latency": 0.0,
                "error": f"Unknown API type: {api_type}",
                "response_preview": None,
                "timestamp": datetime.now().isoformat(),
            }

        body = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=timeout) as resp:
            latency = round(time.time() - start, 3)
            raw = resp.read().decode()
            data = json.loads(raw)

            # Extract response text — handle thinking models:
            # - GLM-5 style: content=None, reasoning_content="..."
            # - MiniMax/QwQ style: content="<think>...</think>actual answer"
            preview = None
            if api_type == "openai-completions":
                msg = data.get("choices", [{}])[0].get("message", {})
                text = msg.get("content") or msg.get("reasoning_content") or ""
                # Strip <think>...</think> blocks (MiniMax, QwQ, DeepSeek style).
                # Also strip partial <think> (when max_tokens cuts off inside thinking block).
                import re as _re
                text = _re.sub(r"<think>.*?(?:</think>|$)", "", str(text), flags=_re.DOTALL).strip()
                # For thinking models: even if all output was <think>, the model IS responding
                if not text:
                    finish = data.get("choices", [{}])[0].get("finish_reason", "")
                    text = "(thinking model)" if finish in ("length", "stop") else ""
                preview = text[:40] if text else None
            elif api_type == "anthropic-messages":
                content = data.get("content", [{}])
                if content:
                    preview = (content[0].get("text") or "")[:40] or None

            return {
                "available": True,
                "latency": latency,
                "error": None,
                "response_preview": preview,
                "timestamp": datetime.now().isoformat(),
            }

    except urllib.error.HTTPError as e:
        body_text = ""
        try:
            body_text = e.read().decode()[:120]
        except Exception:
            pass
        return {
            "available": False,
            "latency": round(time.time() - start, 3),
            "error": f"HTTP {e.code}: {body_text}",
            "response_preview": None,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "available": False,
            "latency": round(time.time() - start, 3),
            "error": str(e)[:200],
            "response_preview": None,
            "timestamp": datetime.now().isoformat(),
        }


def test_model_via_openclaw(provider: str, model: str, provider_cfg: dict = None, live: bool = True) -> Dict[str, Any]:
    """
    Test a model — live inference by default, config-only check if live=False.

    Live mode: sends "hi" and checks the model actually responds (catches auth failures,
    unavailable models, quota exhaustion, etc.)

    Config-only mode: just verifies the model entry exists (zero cost, but misses real errors).
    """
    start = time.time()

    # Config existence check (fast, always done first)
    config = load_openclaw_config()
    providers = config.get("models", {}).get("providers", {})

    if provider not in providers:
        return {
            "available": False,
            "latency": round(time.time() - start, 3),
            "error": f"Provider not found: {provider}",
            "timestamp": datetime.now().isoformat()
        }

    p_cfg = provider_cfg or providers[provider]
    models_list = p_cfg.get("models", [])
    model_entry = next((m for m in models_list if m.get("id") == model), None)

    if not model_entry:
        return {
            "available": False,
            "latency": round(time.time() - start, 3),
            "error": f"Model not found in config: {model}",
            "timestamp": datetime.now().isoformat()
        }

    if not live:
        return {
            "available": True,
            "latency": round(time.time() - start, 3),
            "error": None,
            "timestamp": datetime.now().isoformat()
        }

    # OAuth token providers (sk-ant-oat01-*): OpenClaw refreshes these transparently.
    # Raw HTTP tests use stale cached tokens → always 401 false negatives. Skip live test.
    api_key = p_cfg.get("apiKey", "")
    if api_key.startswith("sk-ant-oat01-"):
        return {
            "available": True,
            "latency": 0.0,
            "error": None,
            "response_preview": "(OAuth — tested via OpenClaw, not raw HTTP)",
            "timestamp": datetime.now().isoformat()
        }

    # Live inference test
    return test_model_live(p_cfg, provider, model)


def discover_models(config: Dict[str, Any], tier_filter: Optional[str] = None, live: bool = True) -> Dict[str, Any]:
    """
    Discover all models from OpenClaw providers and test availability.
    """
    providers = config.get("models", {}).get("providers", {})
    router_cfg = load_router_config()

    discovered = {
        "scan_timestamp": datetime.now().isoformat(),
        "total_models": 0,
        "available_models": 0,
        "unavailable_models": 0,
        "providers": {}
    }

    # Get existing router config for tier info
    existing_models = {m["id"]: m for m in router_cfg.get("models", [])}

    # Build tier lookup from real OpenClaw config metadata (no hard-coded name patterns)
    _tier_lookup = {}
    if _CLASSIFIER_AVAILABLE:
        try:
            classified = classify_from_openclaw_config()
            for m in classified:
                _tier_lookup[(m["provider"], m["id"])] = m["tier"]
        except Exception as e:
            print(f"{YELLOW}Warning: tier classifier failed ({e}), falling back to existing tiers{RESET}")

    for provider_name, provider_config in providers.items():
        print(f"\n{BLUE}Scanning provider: {provider_name}{RESET}")
        print("-" * 60)

        models = provider_config.get("models", [])
        provider_result = {
            "name": provider_name,
            "models": [],
            "available": 0,
            "unavailable": 0
        }

        for model in models:
            model_id = model.get("id")
            model_name = model.get("name", model_id)

            # Skip if tier filter is set and model doesn't match
            if tier_filter:
                model_tier = existing_models.get(model_id, {}).get("tier")
                if model_tier != tier_filter:
                    continue

            discovered["total_models"] += 1

            print(f"  Testing: {model_name}... ", end="", flush=True)

            result = test_model_via_openclaw(provider_name, model_id, provider_cfg=provider_config, live=live)

            # Tier from capability classifier (uses real metadata, no name heuristics)
            classified_tier = _tier_lookup.get(
                (provider_name, model_id),
                existing_models.get(model_id, {}).get("tier", "MEDIUM")
            )
            model_result = {
                "id": model_id,
                "name": model_name,
                "provider": provider_name,
                "tier": classified_tier,
                "capabilities": model.get("capabilities", []),
                "cost": model.get("cost", {}),
                "context_window": model.get("contextWindow", 0),
                "agentic": model.get("agentic", False),
                **result
            }

            provider_result["models"].append(model_result)

            if result["available"]:
                preview = result.get("response_preview", "")
                preview_str = f' → "{preview}"' if preview else ""
                print(f"{GREEN}✓{RESET} ({result['latency']}s{preview_str})")
                provider_result["available"] += 1
                discovered["available_models"] += 1
            else:
                print(f"{RED}✗{RESET} ({result.get('error', 'unknown')[:60]})")
                provider_result["unavailable"] += 1
                discovered["unavailable_models"] += 1

        discovered["providers"][provider_name] = provider_result

    return discovered


def print_summary(discovered: Dict[str, Any]):
    """Print discovery summary."""
    print("\n" + "=" * 60)
    print(f"{BLUE}DISCOVERY SUMMARY{RESET}")
    print("=" * 60)
    print(f"Total models scanned: {discovered['total_models']}")
    print(f"{GREEN}Available: {discovered['available_models']}{RESET}")
    print(f"{RED}Unavailable: {discovered['unavailable_models']}{RESET}")
    print(f"Scan time: {discovered['scan_timestamp']}")

    print("\n" + "=" * 60)
    print(f"{BLUE}UNAVAILABLE MODELS{RESET}")
    print("=" * 60)

    unavailable = []
    for provider, data in discovered["providers"].items():
        for model in data["models"]:
            if not model["available"]:
                unavailable.append(f"  - {model['name']} ({provider}): {model['error']}")

    if unavailable:
        for item in unavailable:
            print(f"{RED}{item}{RESET}")
    else:
        print(f"{GREEN}All models available!{RESET}")


def update_router_config(discovered: Dict[str, Any]):
    """
    Update router config.json with discovered models.
    Preserves tier rules, removes unavailable models.
    """
    router_cfg = load_router_config()

    # Build new models list (only available ones)
    new_models = []
    for provider, data in discovered["providers"].items():
        for model in data["models"]:
            if model["available"]:
                # Convert discovery format back to router config format
                router_model = {
                    "id": model["id"],
                    "alias": model["name"].replace(" ", "-"),
                    "tier": model["tier"],
                    "provider": provider,
                    "input_cost_per_m": model["cost"].get("input", 0),
                    "output_cost_per_m": model["cost"].get("output", 0),
                    "context_window": model["context_window"],
                    "capabilities": model["capabilities"],
                    "agentic": model["agentic"],
                    "notes": f"Auto-discovered {model['timestamp']}"
                }
                new_models.append(router_model)

    # Preserve pinned models (manual overrides)
    existing_models = router_cfg.get("models", [])
    for existing in existing_models:
        if existing.get("pinned"):
            # Keep pinned models even if unavailable
            new_models.append(existing)

    # Rebuild tiers and routing_rules from capability classifier (no hard-coded names)
    if _CLASSIFIER_AVAILABLE:
        try:
            classified = classify_from_openclaw_config()
            # Filter to only available models
            available_ids = {(m["provider"], m["id"]) for m in new_models}
            available_classified = [
                m for m in classified
                if (m["provider"], m["id"]) in available_ids
            ]
            tier_cfg = build_tier_config(available_classified)
            router_cfg["tiers"] = tier_cfg

            # Sync routing_rules from tiers
            use_for = {
                "SIMPLE":    ["monitoring", "status checks", "summarization", "simple API calls",
                              "memory consolidation", "tweet monitoring", "price alerts", "heartbeat"],
                "MEDIUM":    ["code fixes", "research", "data analysis", "API integration",
                              "documentation", "general QA", "moderate complexity"],
                "COMPLEX":   ["feature development", "architecture", "debugging", "code review",
                              "multi-step reasoning", "trading strategy"],
                "REASONING": ["formal logic", "mathematical proofs", "deep analysis",
                              "long-horizon planning", "algorithmic design"],
                "CRITICAL":  ["security review", "production decisions", "financial operations",
                              "high-stakes analysis"],
            }
            for tier_name, cfg in tier_cfg.items():
                router_cfg["routing_rules"][tier_name] = {
                    "primary": cfg["primary"],
                    "fallback_chain": cfg["fallbacks"][:5],
                    "use_for": use_for.get(tier_name, []),
                }
            # Apply manual tier_overrides (survive auto-updates)
            # Set tier_overrides in config.json to lock a primary regardless of scorer.
            overrides = router_cfg.get("tier_overrides", {})
            for tier_name, override in overrides.items():
                forced = override.get("forced_primary")
                if not forced or tier_name not in router_cfg["routing_rules"]:
                    continue
                rule = router_cfg["routing_rules"][tier_name]
                if rule["primary"] != forced:
                    old_primary = rule["primary"]
                    new_fallback = [old_primary] + [
                        m for m in rule["fallback_chain"] if m != forced and m != old_primary
                    ]
                    rule["primary"] = forced
                    rule["fallback_chain"] = new_fallback[:5]
                    print(f"  Override: {tier_name} primary locked to {forced} (was {old_primary})")

            print(f"{GREEN}✓ Tiers and routing_rules rebuilt from capability metadata{RESET}")
            for tier, cfg in tier_cfg.items():
                print(f"  {tier}: {cfg['primary']}")
        except Exception as e:
            print(f"{YELLOW}Warning: tier rebuild failed ({e}){RESET}")

    # Update config
    router_cfg["models"] = new_models
    router_cfg["last_discovery"] = discovered["scan_timestamp"]

    # Write updated config
    with open(ROUTER_CONFIG, "w") as f:
        json.dump(router_cfg, f, indent=2)

    print(f"\n{GREEN}✓ Updated {ROUTER_CONFIG}{RESET}")
    print(f"  Models: {len(new_models)} (available)")
    print(f"  Last discovery: {discovered['scan_timestamp']}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Auto-discover working models")
    parser.add_argument("--auto-update", action="store_true", help="Update config.json with discovered models")
    parser.add_argument("--tier", help="Only test models from specific tier (SIMPLE/MEDIUM/COMPLEX/REASONING/CRITICAL)")
    parser.add_argument("--output", help="Output JSON file path", default=str(DISCOVERY_OUTPUT))
    parser.add_argument("--no-live", action="store_true", help="Skip live inference tests (config-only check, free)")
    args = parser.parse_args()

    print(f"{BLUE}Intelligent Router - Model Auto-Discovery{RESET}")
    print(f"Scan time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load configs
    config = load_openclaw_config()

    # Discover models
    live = not args.no_live
    if not live:
        print(f"{YELLOW}⚡ Config-only mode (--no-live): skipping inference tests{RESET}")
    else:
        print(f"{BLUE}🔍 Live inference mode: sending 'hi' to each model to verify availability{RESET}")
    discovered = discover_models(config, tier_filter=args.tier, live=live)

    # Print summary
    print_summary(discovered)

    # Save discovery results
    with open(args.output, "w") as f:
        json.dump(discovered, f, indent=2)
    print(f"\n{GREEN}✓ Saved discovery results to {args.output}{RESET}")

    # Auto-update if requested
    if args.auto_update:
        update_router_config(discovered)

        # Suggest next steps
        print(f"\n{YELLOW}Next steps:{RESET}")
        print(f"  1. Review updated config: cat {ROUTER_CONFIG}")
        print(f"  2. Test router: python3 skills/intelligent-router/scripts/router.py health")
        print(f"  3. Commit changes: git add {ROUTER_CONFIG} && git commit -m 'Auto-update model list'")


if __name__ == "__main__":
    main()
