#!/bin/bash
# ACC Quick Check — Lightweight real-time error signal detection
# Runs inline during conversation (no LLM, pure pattern matching)
#
# Usage:
#   quick-check.sh --user "user's message" [--assistant "your last response"]
#   quick-check.sh --user "No, that's wrong. I meant the other file."
#
# Output:
#   JSON with signal level (none/low/medium/high) and matched indicators
#   Exit code: 0 = no signal, 1 = low, 2 = medium, 3 = high
#
# Design: Fast heuristic only. For deep analysis, use the full cron pipeline.

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
STATE_FILE="$WORKSPACE/memory/acc-state.json"

# Parse arguments
USER_TEXT=""
ASSISTANT_TEXT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --user) USER_TEXT="$2"; shift 2 ;;
        --assistant) ASSISTANT_TEXT="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

if [ -z "$USER_TEXT" ]; then
    echo '{"signal":"none","reason":"no input provided"}'
    exit 0
fi

export USER_TEXT ASSISTANT_TEXT

python3 << 'PYTHON'
import re
import json
import sys
import os

user_text = os.environ.get('USER_TEXT', '')
assistant_text = os.environ.get('ASSISTANT_TEXT', '')

# Normalize for matching
user_lower = user_text.lower().strip()

# Skip very short messages or obvious non-corrections
if len(user_lower) < 3:
    print(json.dumps({"signal": "none", "reason": "message too short"}))
    sys.exit(0)

# === SIGNAL PATTERNS ===
# Each pattern has a weight. We sum weights to determine signal level.

signals = []
weight = 0

# --- HIGH weight indicators (direct corrections) ---
high_patterns = [
    (r'\bno[,.]?\s+(that\'s |it\'s |you\'re )?(not |in)?correct\b', 'direct correction'),
    (r'\bthat\'s (wrong|incorrect|not right|not what)\b', 'direct correction'),
    (r'\byou\'re wrong\b', 'direct correction'),
    (r'\bwrong\b.{0,20}\b(answer|response|file|approach)\b', 'wrong answer'),
    (r'^no[.!,]', 'starts with no'),
    (r'\bstop\b.{0,15}\b(doing|that)\b', 'stop command'),
    (r'\bi (said|asked|meant|wanted)\b.{0,30}\bnot\b', 'user restating intent'),
    (r'\bdon\'t (do|change|touch|delete|modify|remove)\b', 'prohibition'),
    (r'\bundo\b|\brevert\b|\broll\s*back\b', 'undo request'),
    (r'\byou (broke|messed|screwed|ruined)\b', 'blame signal'),
]

for pattern, label in high_patterns:
    if re.search(pattern, user_lower):
        signals.append({"indicator": label, "weight": "high"})
        weight += 3

# --- MEDIUM weight indicators (implicit corrections) ---
medium_patterns = [
    (r'\bactually[,.]?\s', 'implicit correction (actually)'),
    (r'\bi meant\b', 'clarification (i meant)'),
    (r'\bnot what i\b', 'not what i wanted'),
    (r'\bthat\'s not\b', 'negation'),
    (r'\bplease (re-?read|look again|try again)\b', 'retry request'),
    (r'\bi already (said|told|mentioned|asked)\b', 'repeated instruction'),
    (r'\byou (missed|forgot|ignored|skipped|overlooked)\b', 'oversight signal'),
    (r'\bwhy (did you|are you|would you)\b', 'questioning decision'),
    (r'\bthat doesn\'t (work|make sense|help)\b', 'failure signal'),
    (r'\bstill (wrong|broken|not working|failing)\b', 'persistent error'),
]

for pattern, label in medium_patterns:
    if re.search(pattern, user_lower):
        signals.append({"indicator": label, "weight": "medium"})
        weight += 2

# --- LOW weight indicators (possible dissatisfaction) ---
low_patterns = [
    (r'^(no|nope|nah)\b', 'negative opener'),
    (r'\b(confused|confusing|unclear)\b', 'confusion signal'),
    (r'\bwhat\?\s*$', 'confused reaction'),
    (r'\bhuh\?\s*$', 'confused reaction'),
    (r'\b(sigh|ugh|ffs|smh)\b', 'frustration expression'),
    (r'\bnever\s*mind\b', 'giving up'),
    (r'\bforget (it|about)\b', 'giving up'),
    (r'\blet me (just |try to )?do it (myself|manually)\b', 'taking over'),
    (r'[!?]{2,}', 'emphatic punctuation'),
    (r'\.\.\.\s*$', 'trailing off (possible frustration)'),
]

for pattern, label in low_patterns:
    if re.search(pattern, user_lower):
        signals.append({"indicator": label, "weight": "low"})
        weight += 1

# --- Context boost: check against active patterns ---
# If user text matches context of an existing active pattern, boost the signal
workspace = os.environ.get('WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
state_file = os.path.join(workspace, 'memory', 'acc-state.json')
matched_patterns = []
try:
    with open(state_file) as f:
        state = json.load(f)
    for name, data in state.get('activePatterns', {}).items():
        context_words = data.get('context', '').lower().split()
        # Check if 2+ context words appear in user message
        matches = sum(1 for w in context_words if len(w) > 3 and w in user_lower)
        if matches >= 2:
            matched_patterns.append(name)
            weight += 2
except:
    pass

# === DETERMINE SIGNAL LEVEL ===
if weight >= 5:
    signal = "high"
    exit_code = 3
elif weight >= 3:
    signal = "medium"
    exit_code = 2
elif weight >= 1:
    signal = "low"
    exit_code = 1
else:
    signal = "none"
    exit_code = 0

result = {
    "signal": signal,
    "weight": weight,
    "indicators": signals,
}

if matched_patterns:
    result["matchedActivePatterns"] = matched_patterns

# Add suggestion for high signals
if signal == "high":
    result["suggestion"] = "Strong error signal. Consider acknowledging the mistake and adjusting approach."
elif signal == "medium":
    result["suggestion"] = "Possible correction detected. Double-check your last response."

print(json.dumps(result, indent=2))
sys.exit(exit_code)
PYTHON
