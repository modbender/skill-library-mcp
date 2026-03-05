#!/usr/bin/env python3
"""
Router Policy Enforcer v1.0 — Intelligent Router Skill

Pre-write-time enforcement for cron jobs and sub-agent spawns.
Catches bad model assignments BEFORE they are created, not after they fail.

Usage:
    # Validate a cron payload JSON
    python3 router_policy.py check '{"kind":"agentTurn","model":"ollama-gpu-server/glm-4.7-flash","message":"check server"}'

    # Get the correct model for a task (enforced recommendation)
    python3 router_policy.py recommend "monitor alphastrike service health"

    # Check all current cron jobs for policy violations
    python3 router_policy.py audit

    # Show known bad models and why
    python3 router_policy.py blocklist

Exit codes:
    0 = OK / compliant
    1 = policy violation found
    2 = usage error
"""

import json
import sys
import subprocess
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

SKILL_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILL_DIR / "config.json"

# Models that must never be used in isolated cron jobs.
# Reason: these are network-dependent local models that become SPOFs.
BLOCKED_MODELS: dict[str, str] = {
    "ollama-gpu-server/glm-4.7-flash":
        "GPU server Ollama binds to 127.0.0.1 by default — unreachable over LAN. "
        "Use anthropic-proxy-4/glm-4.7 or anthropic-proxy-6/glm-4.7 instead.",
    "ollama-gpu-server/qwen2.5:7b":
        "Same issue: GPU server Ollama localhost-only by default.",
    "ollama/qwen2.5:7b":
        "Local Ollama may not be running in isolated cron context. Use NIM fallback.",
    "ollama/llama3.3":
        "Local Ollama may not be running in isolated cron context. Use NIM fallback.",
    "ollama/llama3.2:3b":
        "Local Ollama may not be running in isolated cron context. Use NIM fallback.",
}

# Tier → preferred model for cron jobs (cloud-only, no local dependency)
CRON_TIER_MODELS: dict[str, str] = {
    "SIMPLE":    "anthropic-proxy-6/glm-4.7",    # $0.50/M, always available, alternates with proxy-4
    "MEDIUM":    "nvidia-nim/meta/llama-3.3-70b-instruct",  # $0.40/M, capable
    "COMPLEX":   "anthropic/claude-sonnet-4-6",   # $3/M, full coding ability
    "REASONING": "nvidia-nim/moonshotai/kimi-k2-thinking",  # $1/M, 1T MoE specialist
    "CRITICAL":  "anthropic/claude-opus-4-6",     # $5/M, highest capability
}

# Alternate SIMPLE model to distribute load (use for every other SIMPLE cron)
SIMPLE_ALT = "anthropic-proxy-4/glm-4.7"

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_router_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE) as f:
        return json.load(f)


def classify_task(task: str) -> str:
    """Call router.py to classify a task. Returns tier string."""
    result = subprocess.run(
        [sys.executable, str(SKILL_DIR / "scripts" / "router.py"), "classify", task],
        capture_output=True, text=True
    )
    for line in result.stdout.splitlines():
        for tier in ("SIMPLE", "MEDIUM", "COMPLEX", "REASONING", "CRITICAL"):
            if tier in line:
                return tier
    return "SIMPLE"  # safe default


def check_payload(payload: dict) -> list[str]:
    """
    Validate a cron/spawn payload. Returns list of violations (empty = OK).
    """
    violations = []
    model = payload.get("model", "")

    # Rule 1: model must be set
    if not model:
        violations.append(
            "VIOLATION: No model specified. "
            "Every cron/spawn must set 'model' explicitly. "
            "No model → default Sonnet → expensive waste."
        )
        return violations  # can't check further without a model

    # Rule 2: model must not be in blocklist
    if model in BLOCKED_MODELS:
        reason = BLOCKED_MODELS[model]
        task = payload.get("message", "")
        tier = classify_task(task) if task else "SIMPLE"
        recommended = CRON_TIER_MODELS.get(tier, CRON_TIER_MODELS["SIMPLE"])
        violations.append(
            f"VIOLATION: Blocked model '{model}'.\n"
            f"  Reason: {reason}\n"
            f"  Task tier: {tier}\n"
            f"  Recommended: {recommended}"
        )

    # Rule 3: CRITICAL tasks should not use cheap models
    task = payload.get("message", "")
    if task:
        tier = classify_task(task)
        if tier == "CRITICAL" and model not in (
            "anthropic/claude-opus-4-6",
            "anthropic-proxy-1/claude-opus-4-6",
        ):
            violations.append(
                f"WARNING: Task classified as CRITICAL but using '{model}'. "
                f"Consider anthropic/claude-opus-4-6 for high-stakes tasks."
            )

    return violations


def recommend_model(task: str, alternate: bool = False) -> dict:
    """
    Return the recommended model for a task with full context.
    """
    tier = classify_task(task)
    model = CRON_TIER_MODELS.get(tier, CRON_TIER_MODELS["SIMPLE"])
    if tier == "SIMPLE" and alternate:
        model = SIMPLE_ALT
    return {
        "tier": tier,
        "model": model,
        "task": task,
        "note": f"Cron-safe cloud model. No local GPU dependency.",
    }


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_check(payload_json: str) -> int:
    try:
        payload = json.loads(payload_json)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON — {e}", file=sys.stderr)
        return 2

    violations = check_payload(payload)
    if violations:
        for v in violations:
            print(v)
        return 1

    model = payload.get("model", "")
    print(f"✅ OK — model '{model}' is policy-compliant.")
    return 0


def cmd_recommend(task: str, alternate: bool = False) -> int:
    result = recommend_model(task, alternate=alternate)
    print(f"Tier:  {result['tier']}")
    print(f"Model: {result['model']}")
    print(f"Note:  {result['note']}")
    return 0


def cmd_audit() -> int:
    """
    Audit all current OpenClaw cron jobs for policy violations.
    Reads crons via openclaw CLI.
    """
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list", "--json"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            # Fallback: try reading via gateway API directly
            print("WARNING: openclaw CLI not available. Run from inside OpenClaw session.")
            return 2

        crons = json.loads(result.stdout).get("jobs", [])
    except (json.JSONDecodeError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"ERROR: Could not load cron list — {e}")
        return 2

    violations_found = 0
    for cron in crons:
        payload = cron.get("payload", {})
        if payload.get("kind") != "agentTurn":
            continue

        violations = check_payload(payload)
        if violations:
            violations_found += 1
            name = cron.get("name", cron.get("id", "unknown"))
            cron_id = cron.get("id", "?")
            print(f"\n[CRON] {name} ({cron_id[:8]}...)")
            for v in violations:
                print(f"  {v}")

    if violations_found == 0:
        print(f"✅ All {len(crons)} cron jobs are policy-compliant.")
    else:
        print(f"\n⚠️  {violations_found} cron job(s) have policy violations.")

    return 1 if violations_found > 0 else 0


def cmd_blocklist() -> int:
    print("Blocked models (never use in cron/spawn payloads):\n")
    for model, reason in BLOCKED_MODELS.items():
        print(f"  ❌ {model}")
        print(f"     {reason}\n")
    return 0


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    cmd = args[0]

    if cmd == "check":
        if len(args) < 2:
            print("Usage: router_policy.py check '<json_payload>'", file=sys.stderr)
            return 2
        return cmd_check(args[1])

    elif cmd == "recommend":
        if len(args) < 2:
            print("Usage: router_policy.py recommend 'task description'", file=sys.stderr)
            return 2
        alternate = "--alt" in args
        return cmd_recommend(args[1], alternate=alternate)

    elif cmd == "audit":
        return cmd_audit()

    elif cmd == "blocklist":
        return cmd_blocklist()

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print("Commands: check | recommend | audit | blocklist", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
