#!/bin/bash
# ACC LLM Screening — Multi-model error signal classification
# Uses configurable models (primary → fallback) to confirm whether regex-filtered
# exchanges are actual errors.
#
# Usage:
#   haiku-screen.sh <pending-errors.json>
#
# Environment:
#   ACC_MODELS  Comma-separated CLI commands to try in order (each invoked with prompt as final arg)
#               Default: "claude --model haiku -p,claude --model sonnet -p"
#               Example: "ollama run llama3 -p,openai gpt-4 -p"
#
# Output: Filtered JSON array to stdout (only confirmed errors)
# Logs screening stats to stderr (including which models were used)

set -e

INPUT_FILE="${1:?Usage: haiku-screen.sh <pending-errors.json>}"

if [ ! -f "$INPUT_FILE" ]; then
    echo "[]"
    exit 0
fi

ACC_MODELS="${ACC_MODELS:-claude --model haiku -p,claude --model sonnet -p}"
export INPUT_FILE ACC_MODELS

python3 << 'PYTHON'
import json
import subprocess
import sys
import os

input_file = os.environ.get('INPUT_FILE', '')

try:
    with open(input_file) as f:
        exchanges = json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
    print("[]")
    sys.exit(0)

if not isinstance(exchanges, list) or len(exchanges) == 0:
    print("[]")
    sys.exit(0)

PROMPT_TEMPLATE = """You are classifying a conversation exchange. The user message follows an assistant message.

Assistant said:
{assistant_text}

User replied:
{user_text}

Is the user's message a correction, complaint, or expression of frustration with the assistant? Answer YES or NO only."""

# Parse models from ACC_MODELS env var (comma-separated CLI commands)
# Default: "claude --model haiku -p,claude --model sonnet -p"
acc_models_str = os.environ.get('ACC_MODELS', 'claude --model haiku -p,claude --model sonnet -p')
MODELS = []
for i, cmd_str in enumerate(acc_models_str.split(',')):
    cmd_parts = cmd_str.strip().split()
    if cmd_parts:
        model_name = f"model_{i+1}" if len(MODELS) > 0 else cmd_parts[0]
        MODELS.append((model_name, cmd_parts))

def classify_exchange(prompt):
    """Try models in order until one succeeds."""
    for model_name, cmd_prefix in MODELS:
        try:
            result = subprocess.run(
                cmd_prefix + [prompt],
                capture_output=True, text=True, timeout=45
            )
            if result.returncode == 0 and result.stdout.strip():
                return model_name, result.stdout.strip().upper()
        except subprocess.TimeoutExpired:
            print(f"{model_name} timed out, trying fallback...", file=sys.stderr)
            continue
        except Exception as e:
            print(f"{model_name} error: {e}, trying fallback...", file=sys.stderr)
            continue
    return None, None

confirmed = []
model_stats = {}

for exchange in exchanges:
    assistant_text = exchange.get('assistant_text', '')[:500]
    user_text = exchange.get('user_text', '')[:500]

    if not user_text:
        continue

    prompt = PROMPT_TEMPLATE.format(
        assistant_text=assistant_text,
        user_text=user_text
    )

    model_used, answer = classify_exchange(prompt)
    
    if model_used:
        model_stats[model_used] = model_stats.get(model_used, 0) + 1
        if 'YES' in answer:
            confirmed.append(exchange)
    else:
        # All models failed — keep the exchange as safety fallback
        print(f"All models failed, keeping exchange as fallback", file=sys.stderr)
        confirmed.append(exchange)
        model_stats['fallback'] = model_stats.get('fallback', 0) + 1

total = len(exchanges)
kept = len(confirmed)
print(json.dumps(confirmed, indent=2), file=sys.stdout)

# Report stats
stats_str = ", ".join(f"{k}:{v}" for k, v in sorted(model_stats.items()))
print(f"LLM screening: {total} → {kept} confirmed errors (models: {stats_str})", file=sys.stderr)
PYTHON
