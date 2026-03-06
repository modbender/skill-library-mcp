#!/usr/bin/env python3
"""
Sync OpenRouter models into this openclaw installation's config.

Accepts model IDs via --models (comma-separated) or stdin (one per line),
verifies each against the OpenRouter API, and adds missing ones.

Usage:
  python3 sync-openrouter-models.py --models "moonshotai/kimi-k2.5,stepfun/step-3.5-flash"
  echo "moonshotai/kimi-k2.5" | python3 sync-openrouter-models.py
  python3 sync-openrouter-models.py --dry-run --models "..."

Requires: OPENROUTER_API_KEY env var or key from existing config.
"""

import argparse
import json
import os
import re
import shutil
import sys
import urllib.request
import urllib.error
from datetime import datetime

# Auto-detect paths from OPENCLAW_DIR env or default ~/.openclaw
OPENCLAW_DIR = os.environ.get("OPENCLAW_DIR", os.path.expanduser("~/.openclaw"))
OPENCLAW_JSON = os.path.join(OPENCLAW_DIR, "openclaw.json")
OPENROUTER_API = "https://openrouter.ai/api/v1"


def find_agent_dir() -> str:
    """Auto-detect agent dir. Checks OPENCLAW_AGENT_DIR env, then default."""
    env = os.environ.get("OPENCLAW_AGENT_DIR")
    if env and os.path.isdir(env):
        return env
    default = os.path.join(OPENCLAW_DIR, "agents/main/agent")
    if os.path.isdir(default):
        return default
    # Fallback: scan agents/ for first agent with models.json
    agents_dir = os.path.join(OPENCLAW_DIR, "agents")
    if os.path.isdir(agents_dir):
        for name in sorted(os.listdir(agents_dir)):
            candidate = os.path.join(agents_dir, name, "agent")
            if os.path.exists(os.path.join(candidate, "models.json")):
                return candidate
    return default


AGENT_DIR = find_agent_dir()
AGENT_MODELS_JSON = os.path.join(AGENT_DIR, "models.json")


def get_api_key() -> str:
    """Get OpenRouter API key from env or config files."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key
    for path in [AGENT_MODELS_JSON, OPENCLAW_JSON]:
        try:
            with open(path) as f:
                cfg = json.load(f)
            for root in [cfg, cfg.get("models", {})]:
                key = root.get("providers", {}).get("openrouter", {}).get("apiKey")
                if key:
                    return key
        except (OSError, json.JSONDecodeError):
            continue
    print("ERROR: No OPENROUTER_API_KEY found in env or config.", file=sys.stderr)
    sys.exit(1)


def api_get(url: str, api_key: str) -> dict:
    """Make authenticated GET to OpenRouter API with error handling."""
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"ERROR: API returned {e.code}: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Cannot reach OpenRouter API: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


def fetch_all_models(api_key: str) -> dict:
    """Fetch all models from OpenRouter API. Returns {model_id: model_data}."""
    data = api_get(f"{OPENROUTER_API}/models", api_key)
    return {m["id"]: m for m in data.get("data", [])}


def model_to_config(m: dict) -> dict:
    """Convert OpenRouter API model to openclaw config format."""
    pricing = m.get("pricing", {})

    def to_f(v):
        try:
            return float(v) if v else 0
        except (ValueError, TypeError):
            return 0

    # Detect input modalities
    input_types = ["text"]
    arch = m.get("architecture", {}) or {}
    modality_in = arch.get("input_modalities") or arch.get("modality", "")
    if isinstance(modality_in, list) and "image" in modality_in:
        input_types.append("image")
    elif "image" in str(modality_in):
        input_types.append("image")
    if pricing.get("image") and "image" not in input_types:
        input_types.append("image")

    # Detect reasoning: check architecture field first, then name heuristics
    reasoning = False
    arch_family = str(arch.get("reasoning", "")).lower()
    if arch_family in ("true", "yes", "1"):
        reasoning = True
    # Fallback heuristics for known reasoning families
    mid = m.get("id", "")
    reasoning_patterns = [
        "gemini-2.5", "gemini-3-pro", "minimax-m2.5", "glm-5",
        "claude-sonnet", "claude-opus", "deepseek-r1", "o1-", "o3-",
    ]
    if any(p in mid for p in reasoning_patterns):
        reasoning = True
    name_lower = (m.get("name") or "").lower()
    if any(x in name_lower for x in ["reasoning", "think"]):
        reasoning = True

    return {
        "id": mid,
        "name": m.get("name", mid),
        "reasoning": reasoning,
        "input": input_types,
        "cost": {
            "input": to_f(pricing.get("prompt")),
            "output": to_f(pricing.get("completion")),
            "cacheRead": to_f(pricing.get("input_cache_read")),
            "cacheWrite": to_f(pricing.get("input_cache_write")),
        },
        "contextWindow": m.get("context_length", 128000),
        "maxTokens": (m.get("top_provider") or {}).get("max_completion_tokens") or 65536,
    }


def load_alias_map() -> dict:
    """Load alias map from references/aliases.json if present, else use defaults."""
    # Check for aliases.json next to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    aliases_file = os.path.join(script_dir, "..", "references", "aliases.json")
    if os.path.exists(aliases_file):
        try:
            with open(aliases_file) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            pass

    return {
        "moonshotai/kimi-k2.5": "kimi",
        "deepseek/deepseek-v3.2": "deepseek",
        "google/gemini-3-flash-preview": "gemini-flash",
        "google/gemini-2.5-pro-preview": "gemini-pro",
        "google/gemini-2.5-flash-lite": "flash-lite",
        "google/gemini-2.5-flash": "gemini-25-flash",
        "google/gemini-3-pro-preview": "gemini3-pro",
        "x-ai/grok-4.1-fast": "grok",
        "minimax/minimax-m2.5": "minimax",
        "minimax/minimax-m2.1": "minimax-m21",
        "z-ai/glm-5": "glm5",
        "z-ai/glm-4.5-air": "glm45-air",
        "stepfun/step-3.5-flash": "step-flash",
        "openai/gpt-5-nano": "gpt5-nano",
        "anthropic/claude-haiku-4.5": "haiku",
        "anthropic/claude-sonnet-4": "sonnet4",
        "arcee-ai/trinity-large-preview:free": "trinity",
    }


ALIAS_MAP = load_alias_map()


def generate_alias(model_id: str) -> str:
    """Generate alias from map or auto-derive from model ID."""
    if model_id in ALIAS_MAP:
        return ALIAS_MAP[model_id]
    parts = model_id.split("/")
    name = parts[-1] if len(parts) > 1 else model_id
    return re.sub(r":free$", "", name).replace("-preview", "").replace("-large", "")


def backup_file(filepath: str) -> str | None:
    """Create timestamped backup before modifying. Returns backup path."""
    if not os.path.exists(filepath):
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = f"{filepath}.bak.{ts}"
    shutil.copy2(filepath, backup)
    return backup


def safe_write_json(filepath: str, data: dict) -> None:
    """Write JSON atomically: write to temp, then rename."""
    tmp = filepath + ".tmp"
    try:
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, filepath)  # atomic on same filesystem
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def update_provider_models(filepath: str, new_models: list, dry_run: bool) -> int:
    """Add new models to the openrouter provider in a config file."""
    if not os.path.exists(filepath):
        return 0
    try:
        with open(filepath) as f:
            cfg = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"  WARN: Cannot read {filepath}: {e}", file=sys.stderr)
        return 0

    or_cfg = None
    for root in [cfg, cfg.get("models", {})]:
        if isinstance(root, dict) and "providers" in root and "openrouter" in root["providers"]:
            or_cfg = root["providers"]["openrouter"]
            break

    if not or_cfg:
        print(f"  WARN: No openrouter provider in {filepath}", file=sys.stderr)
        return 0

    if "models" not in or_cfg:
        or_cfg["models"] = []

    existing = {m["id"] for m in or_cfg["models"]}
    added = [m for m in new_models if m["id"] not in existing]
    or_cfg["models"].extend(added)

    if added and not dry_run:
        backup_file(filepath)
        safe_write_json(filepath, cfg)
    return len(added)


def update_aliases(new_models: list, dry_run: bool) -> int:
    """Add aliases for new models in openclaw.json."""
    if not os.path.exists(OPENCLAW_JSON):
        return 0
    try:
        with open(OPENCLAW_JSON) as f:
            cfg = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"  WARN: Cannot read {OPENCLAW_JSON}: {e}", file=sys.stderr)
        return 0

    aliases = cfg.get("agents", {}).get("defaults", {}).get("models")
    if not isinstance(aliases, dict):
        return 0

    added = 0
    for m in new_models:
        key = f"openrouter/{m['id']}"
        if key not in aliases:
            aliases[key] = {"alias": generate_alias(m["id"])}
            added += 1

    if added and not dry_run:
        backup_file(OPENCLAW_JSON)
        safe_write_json(OPENCLAW_JSON, cfg)
    return added


def main():
    p = argparse.ArgumentParser(description="Sync OpenRouter models into this openclaw")
    p.add_argument("--models", help="Comma-separated model IDs")
    p.add_argument("--dry-run", action="store_true", help="Preview without writing")
    p.add_argument("--json", action="store_true", help="Machine-readable output")
    args = p.parse_args()

    # Collect model IDs
    if args.models:
        input_ids = [m.strip() for m in args.models.split(",") if m.strip()]
    elif not sys.stdin.isatty():
        input_ids = [line.strip() for line in sys.stdin if line.strip()]
    else:
        print("ERROR: Provide model IDs via --models or stdin (one per line).", file=sys.stderr)
        sys.exit(1)

    if not input_ids:
        print("ERROR: No model IDs provided.", file=sys.stderr)
        sys.exit(1)

    api_key = get_api_key()

    print(f"Fetching OpenRouter catalog...", file=sys.stderr)
    catalog = fetch_all_models(api_key)
    print(f"  {len(catalog)} models in catalog", file=sys.stderr)

    # Verify each model exists
    verified, skipped = [], []
    for mid in input_ids:
        (verified if mid in catalog else skipped).append(mid)
    for s in skipped:
        print(f"  SKIP {s} (not in catalog)", file=sys.stderr)
    print(f"  Verified {len(verified)}/{len(input_ids)}", file=sys.stderr)

    if not verified:
        print("No valid models to add.", file=sys.stderr)
        if args.json:
            print(json.dumps({"added": 0, "skipped": skipped}))
        sys.exit(1)

    new_models = [model_to_config(catalog[mid]) for mid in verified]

    # Check what's already configured
    existing = set()
    if os.path.exists(AGENT_MODELS_JSON):
        try:
            with open(AGENT_MODELS_JSON) as f:
                for m in json.load(f).get("providers", {}).get("openrouter", {}).get("models", []):
                    existing.add(m["id"])
        except (OSError, json.JSONDecodeError):
            pass
    to_add = [m for m in new_models if m["id"] not in existing]

    if not to_add:
        print("\nAll models already configured.", file=sys.stderr)
        if args.json:
            print(json.dumps({"added": 0, "verified": len(verified), "skipped": skipped}))
        return

    tag = "[DRY RUN] " if args.dry_run else ""
    print(f"\n{tag}Adding {len(to_add)} models:", file=sys.stderr)
    for m in to_add:
        print(f"  + {m['id']} (alias: {generate_alias(m['id'])}, ctx: {m['contextWindow']})", file=sys.stderr)

    a1 = update_provider_models(AGENT_MODELS_JSON, to_add, args.dry_run)
    a2 = update_provider_models(OPENCLAW_JSON, to_add, args.dry_run)
    a3 = update_aliases(to_add, args.dry_run)

    print(f"\n{tag}agent/models.json: +{a1} | openclaw.json: +{a2} models, +{a3} aliases", file=sys.stderr)
    if not args.dry_run and (a1 or a2):
        print("\nRun: openclaw gateway restart", file=sys.stderr)

    if args.json:
        print(json.dumps({
            "added": len(to_add),
            "models": [m["id"] for m in to_add],
            "verified": len(verified),
            "skipped": skipped,
            "dry_run": args.dry_run,
        }))


if __name__ == "__main__":
    main()
