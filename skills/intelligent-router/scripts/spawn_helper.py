#!/usr/bin/env python3
"""
Intelligent Router - Spawn Helper (Enforced Core Skill)

MANDATORY: Call this before ANY sessions_spawn or cron job creation.
It classifies the task and outputs the exact model to use.

Usage (show command):
    python3 skills/intelligent-router/scripts/spawn_helper.py "task description"

Usage (just get model id):
    python3 skills/intelligent-router/scripts/spawn_helper.py --model-only "task description"

Usage (validate payload has model set):
    python3 skills/intelligent-router/scripts/spawn_helper.py --validate '{"kind":"agentTurn","message":"..."}'
"""

import sys
import json
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR.parent / "config.json"

TIER_COLORS = {
    "SIMPLE": "🟢",
    "MEDIUM": "🟡",
    "COMPLEX": "🟠",
    "REASONING": "🔵",
    "CRITICAL": "🔴",
}


def load_config():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Router config not found: {CONFIG_FILE}")
    with open(CONFIG_FILE) as f:
        return json.load(f)


_CODING_PATTERNS = [
    r"\bimplement\b", r"\bwrite\s+\w+\s+(code|script|function|class|module|test)",
    r"\bcode\b", r"\bfix\s+\w*(bug|error|issue|crash)", r"\brefactor\b",
    r"\bdebug\b", r"\bunit\s+test", r"\bintegration\s+test", r"\btdd\b",
    r"\bgo\s+module", r"\brust\b", r"\bpython\s+script", r"\btypescript\b",
    r"\bapi\s+(client|server|endpoint)", r"\bmicroservice", r"\bwire\s+(up|into)",
    r"\bpallet\b", r"\bsmart\s+contract", r"\bsolidity\b",
]

def _is_coding_task(task_description: str) -> bool:
    """Return True if task description has clear coding intent."""
    import re
    text = task_description.lower()
    return any(re.search(p, text) for p in _CODING_PATTERNS)


def _get_complex_primary() -> str:
    """Return the forced COMPLEX primary from tier_overrides, or config primary."""
    try:
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
        override = cfg.get("tier_overrides", {}).get("COMPLEX", {})
        if override.get("forced_primary"):
            return override["forced_primary"]
        return cfg.get("routing_rules", {}).get("COMPLEX", {}).get("primary", "")
    except Exception:
        return ""


def classify_task(task_description):
    """Run router.py classify and return (tier, full_model_id, confidence).
    
    full_model_id is always provider/id (e.g. 'ollama-gpu-server/glm-4.7-flash'),
    which is the format required by sessions_spawn(model=...) and cron payloads.

    User override: coding tasks always route to COMPLEX (Sonnet 4.6 per tier_overrides).
    """
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "router.py"), "classify", task_description],
        capture_output=True, text=True, check=True
    )
    lines = result.stdout.strip().split('\n')
    tier = None
    bare_id = None
    provider = None
    confidence = None

    for line in lines:
        if line.startswith("Classification:"):
            tier = line.split(":", 1)[1].strip()
        elif "  ID:" in line:
            bare_id = line.split(":", 1)[1].strip()
        elif "  Provider:" in line:
            provider = line.split(":", 1)[1].strip()
        elif line.startswith("Confidence:"):
            confidence = line.split(":", 1)[1].strip()

    # Combine provider + id for the full model identifier
    if bare_id and provider:
        model_id = f"{provider}/{bare_id}"
    else:
        model_id = bare_id

    # User rule: ALL coding tasks → COMPLEX (Sonnet 4.6 via tier_overrides)
    if tier in ("SIMPLE", "MEDIUM") and _is_coding_task(task_description):
        complex_primary = _get_complex_primary()
        if complex_primary:
            tier = "COMPLEX"
            model_id = complex_primary
            confidence = "OVERRIDE (coding task → COMPLEX)"

    return tier, model_id, confidence


def validate_payload(payload_json):
    """
    Validate a cron job payload has the model field set.
    Returns (ok: bool, message: str)
    """
    try:
        payload = json.loads(payload_json) if isinstance(payload_json, str) else payload_json
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON payload: {e}"

    if payload.get("kind") != "agentTurn":
        return True, "Non-agentTurn payload — model not required"

    model = payload.get("model")
    if not model:
        return False, (
            "❌ VIOLATION: agentTurn payload missing 'model' field!\n"
            "   Without model, OpenClaw defaults to Sonnet = expensive waste.\n"
            "   Fix: add \"model\": \"<model-id>\" to the payload.\n"
            "   Run: python3 skills/intelligent-router/scripts/spawn_helper.py \"<task>\" to get the right model."
        )

    # Check if Sonnet/Opus is used for a non-critical payload
    expensive = ["claude-sonnet", "claude-opus", "claude-3"]
    for keyword in expensive:
        if keyword in model.lower():
            msg = payload.get("message", "")[:80]
            return None, (
                f"⚠️  WARNING: Expensive model '{model}' set for potentially simple task.\n"
                f"   Task preview: {msg}...\n"
                f"   Consider: python3 skills/intelligent-router/scripts/spawn_helper.py \"{msg}\""
            )

    return True, f"✅ Model set: {model}"


def main():
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(1)

    # --validate mode
    if args[0] == "--validate":
        if len(args) < 2:
            print("Usage: spawn_helper.py --validate '<payload_json>'")
            sys.exit(1)
        ok, msg = validate_payload(args[1])
        print(msg)
        sys.exit(0 if ok else 1)

    # --model-only mode (just print the model id)
    if args[0] == "--model-only":
        if len(args) < 2:
            print("Usage: spawn_helper.py --model-only 'task description'")
            sys.exit(1)
        task = " ".join(args[1:])
        config = load_config()
        tier, model_id, _ = classify_task(task)
        if not model_id:
            rules = config.get("routing_rules", {}).get(tier, {})
            model_id = rules.get("primary", "anthropic-proxy-4/glm-4.7")
        print(model_id)
        sys.exit(0)

    # Default: classify and show spawn command
    task = " ".join(args)
    config = load_config()
    tier, model_id, confidence = classify_task(task)

    if not model_id:
        rules = config.get("routing_rules", {}).get(tier, {})
        model_id = rules.get("primary", "anthropic-proxy-4/glm-4.7")

    icon = TIER_COLORS.get(tier, "⚪")
    fallback_chain = config.get("routing_rules", {}).get(tier, {}).get("fallback_chain", [])

    print(f"\n{icon} Task classified as: {tier} (confidence: {confidence})")
    print(f"💰 Recommended model: {model_id}")
    if fallback_chain:
        print(f"🔄 Fallbacks: {' → '.join(fallback_chain[:2])}")
    print(f"\n📋 Use in sessions_spawn:")
    print(f"""   sessions_spawn(
       task=\"{task[:60]}{'...' if len(task)>60 else ''}\",
       model=\"{model_id}\",
       label=\"<label>\"
   )""")
    print(f"\n📋 Use in cron job payload:")
    print(f"""   {{
       "kind": "agentTurn",
       "message": "...",
       "model": "{model_id}"
   }}""")


if __name__ == "__main__":
    main()
