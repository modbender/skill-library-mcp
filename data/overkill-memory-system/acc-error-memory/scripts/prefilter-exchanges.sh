#!/bin/bash
# ACC Pre-filter — Cost optimization for error analysis pipeline
# Filters exchanges to only those containing error signals before sending to LLM
#
# Usage:
#   prefilter-exchanges.sh <pending-errors.json>
#   prefilter-exchanges.sh /path/to/pending-errors.json
#
# Output: Filtered JSON array to stdout
# Expects input: array of {assistant_text, user_text, timestamp, ...}

set -e

INPUT_FILE="${1:?Usage: prefilter-exchanges.sh <pending-errors.json>}"

if [ ! -f "$INPUT_FILE" ]; then
    echo "[]"
    exit 0
fi

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
LEARNED_FILE="$WORKSPACE/memory/learned-patterns.json"

export INPUT_FILE LEARNED_FILE

python3 << 'PYTHON'
import json
import re
import sys
import os

input_file = os.environ.get('INPUT_FILE', '')
learned_file = os.environ.get('LEARNED_FILE', '')

try:
    with open(input_file) as f:
        exchanges = json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
    print("[]")
    sys.exit(0)

if not isinstance(exchanges, list):
    print("[]")
    sys.exit(0)

# Error signal patterns (case-insensitive)
# Corrections: user is telling assistant it was wrong
corrections = [
    r'\bno,',
    r'^no\s',
    r'\bwrong\b',
    r'\bactually[,.\s]',
    r'\bnot what i\b',
    r'\bthats not\b',
    r'\bthat\'s not\b',
    r'\bthat is not\b',
    r'\bshould be\b',
    r'\bshould have\b',
    r'\bwhy did you\b',
    r'\bwhy didn\'?t you\b',
    r'\bnot right\b',
    r'\bmistake\b',
    r'\bincorrect\b',
]

# Frustration: user is annoyed at repeated mistakes
frustration = [
    r'\byou missed\b',
    r'\bi already said\b',
    r'\bi already told\b',
    r'\bagain\b',
    r'\bstill not\b',
    r'\bcheck again\b',
    r'\btry again\b',
    r'\bfix\b',
    r'\bfixed\b',
]

# Confusion: user doesn't understand assistant's response
confusion = [
    r'\bi don\'?t understand\b',
    r'\bwhat do you mean\b',
    r'\bhuh\?',
    r'\bwhat\?',
]

all_patterns = corrections + frustration + confusion

# Load learned patterns from calibration system
learned_patterns = []
if learned_file:
    try:
        with open(learned_file) as f:
            learned_data = json.load(f)
        for entry in learned_data.get("patterns", []):
            learned_patterns.append(entry["pattern"])
    except (json.JSONDecodeError, FileNotFoundError, KeyError):
        pass

if learned_patterns:
    print(f"Loaded {len(learned_patterns)} learned patterns", file=sys.stderr)

all_patterns = all_patterns + learned_patterns
compiled = [re.compile(p, re.IGNORECASE) for p in all_patterns]

filtered = []
for exchange in exchanges:
    user_text = exchange.get('user_text', '')
    if not user_text:
        continue
    for pattern in compiled:
        if pattern.search(user_text):
            filtered.append(exchange)
            break

total = len(exchanges)
kept = len(filtered)
print(json.dumps(filtered, indent=2), file=sys.stdout)
print(f"Filtered {total} exchanges to {kept} candidates", file=sys.stderr)
PYTHON
