#!/usr/bin/env python3
"""Print a terminal dashboard showing local LLM status and cumulative token savings."""
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

W = 45  # box width

def row(label: str, value: str) -> str:
    # 2 + 22 + 21 = 45 = W, keeping content flush with box edges
    content = f"  {label:<22}{value:>21}"
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
print(title("🧠  Local-First LLM  ·  Dashboard"))
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
content = f"  {label:<12}{status}"
# Use ljust with a byte-width-safe length (emoji chars are wide; keep it simple)
print(f"│  {label:<12}{status:<{W - 14}}│")

# Available models (up to 3)
if local.get("any_available"):
    models = local["best"].get("models", [])
    for m in models[:3]:
        display = m if len(m) <= W - 6 else m[:W - 9] + "..."
        print(f"│    · {display:<{W - 6}}│")

print(divider())

# Request counts
total = savings.get("total_requests", 0)
local_req = savings.get("local_requests", 0)
cloud_req = savings.get("cloud_requests", 0)
pct = savings.get("pct_local", 0.0)

print(row("Total requests:", str(total)))
print(row("Routed locally:", f"{local_req}  ({pct}%)"))
print(row("Routed to cloud:", str(cloud_req)))
print(divider())

# Savings
tokens_saved = savings.get("tokens_saved", 0)
cost_saved = savings.get("cost_saved_usd", 0.0)

print(row("Tokens saved:", f"{tokens_saved:,}"))
print(row("Cost saved (USD):", f"${cost_saved:.4f}"))
print(bottom())
print()

if total == 0:
    print("  No requests tracked yet. Start routing requests with this skill.")
    print("  Run: python3 skills/local-first-llm/scripts/track_savings.py --help")
    print()
