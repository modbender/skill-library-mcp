#!/usr/bin/env python3
"""Print a terminal dashboard showing local LLM status and adaptive routing savings."""
import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def run(args: list) -> dict:
    try:
        result = subprocess.run(
            [PY] + args, capture_output=True, text=True, timeout=5
        )
        return json.loads(result.stdout) if result.returncode == 0 and result.stdout.strip() else {}
    except Exception:
        return {}


local = run([f"{SCRIPT_DIR}/check_local.py"])
savings = run([f"{SCRIPT_DIR}/track_savings.py", "summary"])

W = 47  # box width


def row(label: str, value: str) -> str:
    content = f"  {label:<24}{value:>21}"
    return f"│{content}│"


def divider() -> str:
    return "├" + "─" * W + "┤"


def top() -> str:
    return "┌" + "─" * W + "┐"


def bottom() -> str:
    return "└" + "─" * W + "┘"


def title(text: str) -> str:
    padded = text.center(W)
    return f"│{padded}│"


print()
print(top())
print(title("🔀  Adaptive Routing  ·  Dashboard"))
print(divider())

# Local LLM status
if local.get("any_available"):
    best = local["best"]
    models = best.get("models", [])
    model_str = models[0] if models else "unknown"
    if len(model_str) > 16:
        model_str = model_str[:13] + "..."
    status = f"✅  {best['provider']} ({model_str})"
else:
    status = "❌  Not running"
label = "Local LLM:"
print(f"│  {label:<12}{status:<{W - 14}}│")

# List available models (up to 3)
if local.get("any_available"):
    models = local["best"].get("models", [])
    for m in models[:3]:
        display = m if len(m) <= W - 6 else m[:W - 9] + "..."
        print(f"│    · {display:<{W - 6}}│")

print(divider())

# Request counts
total = savings.get("total_requests", 0)
local_success = savings.get("local_success", 0)
escalated = savings.get("escalated", 0)
cloud = savings.get("cloud", 0)
pct = savings.get("pct_local", 0.0)
escalation_rate = savings.get("escalation_rate", 0.0)

print(row("Total requests:", str(total)))
print(row("Local (passed):", f"{local_success}  ({pct}%)"))
print(row("Escalated to cloud:", str(escalated)))
print(row("Cloud (direct):", str(cloud)))
if escalated + local_success > 0:
    print(row("Escalation rate:", f"{escalation_rate}%"))
print(divider())

# Token savings
tokens_local = savings.get("tokens_local", 0)
tokens_cloud = savings.get("tokens_cloud", 0)
cost_saved = savings.get("cost_saved_usd", 0.0)

print(row("Tokens (local):", f"{tokens_local:,}"))
print(row("Tokens (cloud):", f"{tokens_cloud:,}"))
print(row("Cost saved (USD):", f"${cost_saved:.4f}"))
print(bottom())
print()

if total == 0:
    print("  No requests tracked yet. Start routing with this skill.")
    print("  Run: python3 skills/adaptive-routing/scripts/track_savings.py --help")
    print()
