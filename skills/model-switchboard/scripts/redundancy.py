#!/usr/bin/env python3
"""
Model Switchboard — Redundancy Engine
Generates optimal 3-deep fallback configurations based on available providers.
Enforces provider diversity (never stack same provider in a chain).
Zero external dependencies. Python 3.8+.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

SKILL_DIR = Path(__file__).resolve().parent.parent
REGISTRY_PATH = SKILL_DIR / "model-registry.json"
CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"


def load_registry() -> Dict[str, Any]:
    """Load model registry."""
    try:
        with open(REGISTRY_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(json.dumps({"error": f"Cannot load registry: {e}"}), file=sys.stderr)
        return {"models": {}, "providers": {}, "roles": {}}


def detect_available_providers() -> Dict[str, Dict[str, Any]]:
    """
    Detect which providers have auth configured.
    Checks environment variables and common auth patterns.
    """
    registry = load_registry()
    available = {}

    for pid, pinfo in registry.get("providers", {}).items():
        auth_envs = pinfo.get("authEnv", [])
        has_auth = False
        auth_via = None

        # Check environment variables
        for env_var in auth_envs:
            if os.environ.get(env_var):
                has_auth = True
                auth_via = env_var
                break

        # Special cases
        if pid == "openai-codex":
            # OAuth-based — check if auth profile exists
            auth_profile = Path.home() / ".openclaw" / "auth" / "openai-codex.json"
            if auth_profile.exists():
                has_auth = True
                auth_via = "OAuth profile"

        if pid == "anthropic":
            # May use setup-token instead of env var
            auth_store = Path.home() / ".openclaw" / "auth"
            if auth_store.exists():
                for f in auth_store.glob("anthropic*"):
                    has_auth = True
                    auth_via = "setup-token/auth profile"
                    break
            # Also check if we're running on Anthropic (we are if this agent is alive)
            if not has_auth and os.environ.get("ANTHROPIC_API_KEY"):
                has_auth = True
                auth_via = "ANTHROPIC_API_KEY"

        if has_auth:
            available[pid] = {
                "displayName": pinfo.get("displayName", pid),
                "authVia": auth_via,
                "models": []
            }
            # Find compatible models for this provider
            for mid, minfo in registry.get("models", {}).items():
                if mid.startswith(pid + "/") and not minfo.get("blocked"):
                    available[pid]["models"].append({
                        "id": mid,
                        "displayName": minfo.get("displayName", mid),
                        "capabilities": minfo.get("capabilities", []),
                        "costTier": minfo.get("costTier", "unknown"),
                        "safeRoles": minfo.get("safeRoles", [])
                    })

    return available


def build_fallback_chain(
    role: str,
    available: Dict[str, Dict[str, Any]],
    min_depth: int = 3,
    exclude_providers: Optional[List[str]] = None
) -> List[str]:
    """
    Build a fallback chain for a role with provider diversity.
    Returns ordered list of model IDs.

    Rules:
    1. Never repeat a provider in the chain
    2. Minimum 3 deep (if enough providers available)
    3. Higher quality models first
    4. Cost-appropriate for the role
    """
    registry = load_registry()
    role_info = registry.get("roles", {}).get(role, {})
    required_caps = set(role_info.get("requiredCapabilities", []))
    preferred_cost = role_info.get("preferCostTier", [])

    candidates: List[Tuple[int, str, str]] = []  # (score, model_id, provider)

    for pid, pdata in available.items():
        if exclude_providers and pid in exclude_providers:
            continue
        for model in pdata["models"]:
            mid = model["id"]
            caps = set(model.get("capabilities", []))
            safe = model.get("safeRoles", [])

            # Must have required capabilities
            if not required_caps.issubset(caps):
                continue

            # Must be safe for this role
            if role not in safe:
                continue

            # Score: higher = better
            score = 0

            # Cost tier scoring (varies by role)
            cost = model.get("costTier", "medium")
            if role in ("heartbeat",):
                # Prefer cheap for heartbeat
                cost_scores = {"very-low": 100, "low": 80, "medium": 40, "high": 10, "subscription": 30, "proxy": 50}
            elif role in ("primary", "coding"):
                # Prefer quality for primary/coding
                cost_scores = {"high": 100, "medium": 70, "proxy": 90, "subscription": 85, "low": 30, "very-low": 10}
            else:
                # Balanced for others
                cost_scores = {"medium": 80, "high": 70, "proxy": 75, "low": 60, "very-low": 40, "subscription": 65}

            score += cost_scores.get(cost, 50)

            # Bonus for preferred cost tier
            if preferred_cost and cost in preferred_cost:
                score += 50

            # Bonus for recommended capabilities
            recommended = set(role_info.get("recommendedCapabilities", []))
            score += len(caps & recommended) * 15

            # Bonus for vision capability (useful for many roles)
            if "vision" in caps:
                score += 10

            candidates.append((score, mid, pid))

    # Sort by score descending
    candidates.sort(key=lambda x: x[0], reverse=True)

    # Build chain with provider diversity
    chain: List[str] = []
    used_providers: set = set()

    for score, mid, pid in candidates:
        if pid in used_providers:
            continue
        chain.append(mid)
        used_providers.add(pid)
        if len(chain) >= min_depth:
            break

    # If we couldn't hit min_depth with diversity, allow provider repeats
    if len(chain) < min_depth:
        for score, mid, pid in candidates:
            if mid not in chain:
                chain.append(mid)
                if len(chain) >= min_depth:
                    break

    return chain


def generate_redundant_config(min_depth: int = 3) -> Dict[str, Any]:
    """
    Generate a complete redundant model configuration.
    Returns a config snippet ready to merge into openclaw.json.
    """
    registry = load_registry()
    if not registry.get("models"):
        return {"error": "Model registry is empty or corrupt. Cannot generate redundancy config."}

    available = detect_available_providers()

    if not available:
        return {
            "error": "No providers detected. Configure at least one provider API key.",
            "hint": "Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY in your environment."
        }

    # Build chains for each role
    primary_chain = build_fallback_chain("primary", available, min_depth)
    image_chain = build_fallback_chain("image", available, min_depth)
    heartbeat_chain = build_fallback_chain("heartbeat", available, min_depth)
    coding_chain = build_fallback_chain("coding", available, min_depth)
    fallback_chain = build_fallback_chain("fallback", available, min_depth)

    # Build the config
    config = {
        "generatedAt": datetime.now().isoformat(),
        "generatedBy": "model-switchboard/redundancy-engine",
        "minDepth": min_depth,
        "providersDetected": list(available.keys()),
        "providerCount": len(available),
        "config": {
            "agents": {
                "defaults": {
                    "model": {
                        "primary": primary_chain[0] if primary_chain else None,
                        "fallbacks": primary_chain[1:] if len(primary_chain) > 1 else []
                    },
                    "imageModel": {
                        "primary": image_chain[0] if image_chain else None,
                        "fallbacks": image_chain[1:] if len(image_chain) > 1 else []
                    },
                    "models": {}
                }
            }
        },
        "taskRouting": {
            "primary": {
                "chain": primary_chain,
                "depth": len(primary_chain),
                "description": "Main conversational model — highest quality"
            },
            "image": {
                "chain": image_chain,
                "depth": len(image_chain),
                "description": "Vision/image processing"
            },
            "heartbeat": {
                "chain": heartbeat_chain,
                "depth": len(heartbeat_chain),
                "description": "Low-cost periodic polling"
            },
            "coding": {
                "chain": coding_chain,
                "depth": len(coding_chain),
                "description": "Code generation sub-agents"
            }
        },
        "redundancyReport": {
            "totalModelsAvailable": sum(len(p["models"]) for p in available.values()),
            "uniqueProviders": len(available),
            "primaryDepth": len(primary_chain),
            "imageDepth": len(image_chain),
            "heartbeatDepth": len(heartbeat_chain),
            "codingDepth": len(coding_chain),
            "meetsMininumDepth": all(
                len(c) >= min_depth
                for c in [primary_chain, image_chain]
            ),
            "singlePointsOfFailure": []
        }
    }

    # Build allowlist from all chains
    all_models = set()
    for chain in [primary_chain, image_chain, heartbeat_chain, coding_chain]:
        all_models.update(chain)

    for mid in sorted(all_models):
        registry = load_registry()
        minfo = registry.get("models", {}).get(mid, {})
        config["config"]["agents"]["defaults"]["models"][mid] = {
            "alias": minfo.get("displayName", mid.split("/")[-1])
        }

    # Check for single points of failure
    spof = []
    for role, chain_data in config["taskRouting"].items():
        chain = chain_data["chain"]
        if len(chain) < 2:
            spof.append(f"{role}: only {len(chain)} model(s) — needs at least 2")
        providers_in_chain = set(m.split("/")[0] for m in chain)
        if len(providers_in_chain) < 2 and len(chain) > 1:
            spof.append(f"{role}: all models from same provider ({list(providers_in_chain)[0]})")

    config["redundancyReport"]["singlePointsOfFailure"] = spof

    # Provider details
    config["providers"] = {}
    for pid, pdata in available.items():
        config["providers"][pid] = {
            "displayName": pdata["displayName"],
            "authVia": pdata["authVia"],
            "modelsAvailable": len(pdata["models"]),
            "modelIds": [m["id"] for m in pdata["models"]]
        }

    return config


def generate_deployment_config(min_depth: int = 3) -> Dict[str, Any]:
    """
    Generate a deployment-ready openclaw.json config snippet.
    This is what gets merged into the live config.
    """
    full = generate_redundant_config(min_depth)
    if "error" in full:
        return full
    return full.get("config", {})


def print_redundancy_report(config: Dict[str, Any]) -> None:
    """Pretty-print the redundancy report to terminal."""
    if "error" in config:
        print(f"\n  ❌ {config['error']}")
        if "hint" in config:
            print(f"  💡 {config['hint']}")
        return

    print(f"\n  🔀 Model Switchboard — Redundancy Report")
    print(f"  {'═' * 50}")
    print(f"  Generated: {config.get('generatedAt', 'unknown')}")
    print(f"  Providers: {config.get('providerCount', 0)} detected")
    print(f"  Min depth: {config.get('minDepth', 3)}")
    print()

    # Provider inventory
    print(f"  🔑 Provider Inventory")
    for pid, pdata in config.get("providers", {}).items():
        print(f"     ✅ {pdata['displayName']:<20} {pdata['modelsAvailable']} models  (via {pdata['authVia']})")

    print()

    # Task routing
    print(f"  📋 Task Routing Chains")
    for role, data in config.get("taskRouting", {}).items():
        chain = data.get("chain", [])
        depth = data.get("depth", 0)
        status = "✅" if depth >= config.get("minDepth", 3) else "⚠️"
        print(f"     {status} {role:<12} [{depth} deep]  {' → '.join(chain) if chain else '(none)'}")

    print()

    # Redundancy assessment
    report = config.get("redundancyReport", {})
    spof = report.get("singlePointsOfFailure", [])
    meets = report.get("meetsMininumDepth", False)

    if meets and not spof:
        print(f"  🛡️  Redundancy: STRONG — all roles meet minimum depth, no single points of failure")
    elif meets:
        print(f"  ⚠️  Redundancy: MODERATE — meets minimum depth but has warnings:")
        for s in spof:
            print(f"     ⚠️  {s}")
    else:
        print(f"  🔴 Redundancy: WEAK — does NOT meet minimum depth requirement")
        for s in spof:
            print(f"     ❌ {s}")

    print()


# ── CLI ────────────────────────────────────────────────────────

def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "report"
    min_depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    if command == "report":
        config = generate_redundant_config(min_depth)
        print_redundancy_report(config)

    elif command == "json":
        config = generate_redundant_config(min_depth)
        print(json.dumps(config, indent=2))

    elif command == "deploy":
        config = generate_deployment_config(min_depth)
        print(json.dumps(config, indent=2))

    elif command == "providers":
        available = detect_available_providers()
        print(json.dumps(available, indent=2))

    elif command == "chains":
        available = detect_available_providers()
        roles = ["primary", "image", "heartbeat", "coding", "fallback"]
        chains = {}
        for role in roles:
            chain = build_fallback_chain(role, available, min_depth)
            chains[role] = {"chain": chain, "depth": len(chain)}
        print(json.dumps(chains, indent=2))

    else:
        print("Usage: redundancy.py <command> [min_depth]")
        print("")
        print("Commands:")
        print("  report     Pretty-print redundancy assessment")
        print("  json       Full redundancy config as JSON")
        print("  deploy     Deployment-ready config snippet")
        print("  providers  Detected providers and their models")
        print("  chains     Fallback chains for all roles")
        sys.exit(1)


if __name__ == "__main__":
    main()
