#!/bin/bash
# ACC Pattern Calibration — Self-improving regex system
# Samples exchanges, sends to LLM, compares against regex coverage.
# Learns new patterns from gaps between regex and LLM classification.
#
# Usage:
#   calibrate-patterns.sh <pending-errors.json>
#   calibrate-patterns.sh <pending-errors.json> 0.20   # 20% sample
#
# Output: Stats to stderr, updates learned-patterns.json in place

set -e

INPUT_FILE="${1:?Usage: calibrate-patterns.sh <pending-errors.json> [sample_rate]}"
SAMPLE_RATE="${2:-0.15}"

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
LEARNED_FILE="$WORKSPACE/memory/learned-patterns.json"
CALIBRATION_STATE="$WORKSPACE/memory/calibration-state.json"

if [ ! -f "$INPUT_FILE" ]; then
    echo "No input file, skipping calibration" >&2
    exit 0
fi

ACC_MODELS="${ACC_MODELS:-claude --model haiku -p,claude --model sonnet -p}"
export INPUT_FILE SAMPLE_RATE LEARNED_FILE CALIBRATION_STATE ACC_MODELS

python3 << 'PYTHON'
import json
import random
import re
import subprocess
import sys
import os
from datetime import datetime, timezone

input_file = os.environ['INPUT_FILE']
sample_rate = float(os.environ['SAMPLE_RATE'])
learned_file = os.environ['LEARNED_FILE']
calibration_state_file = os.environ['CALIBRATION_STATE']

# --- Load data ---

try:
    with open(input_file) as f:
        all_exchanges = json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
    print("Cannot read input file, skipping calibration", file=sys.stderr)
    sys.exit(0)

if not isinstance(all_exchanges, list) or len(all_exchanges) < 5:
    print(f"Too few exchanges ({len(all_exchanges) if isinstance(all_exchanges, list) else 0}), skipping calibration", file=sys.stderr)
    sys.exit(0)

try:
    with open(learned_file) as f:
        learned_data = json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
    learned_data = {"patterns": [], "maxPatterns": 50, "version": 1}

try:
    with open(calibration_state_file) as f:
        cal_state = json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
    cal_state = {
        "runCount": 0, "calibrationInterval": 10, "lastCalibration": None,
        "stats": {"calibrationRuns": 0, "samplesAnalyzed": 0, "regexMisses": 0, "patternsAdded": 0}
    }

# --- Hardcoded patterns (same as prefilter-exchanges.sh) ---

HARDCODED_PATTERNS = [
    # Corrections
    r'\bno,', r'^no\s', r'\bwrong\b', r'\bactually[,.\s]',
    r'\bnot what i\b', r'\bthats not\b', r"\bthat\'s not\b", r'\bthat is not\b',
    r'\bshould be\b', r'\bshould have\b', r'\bwhy did you\b', r"\bwhy didn\'?t you\b",
    r'\bnot right\b', r'\bmistake\b', r'\bincorrect\b',
    # Frustration
    r'\byou missed\b', r'\bi already said\b', r'\bi already told\b',
    r'\bagain\b', r'\bstill not\b', r'\bcheck again\b', r'\btry again\b',
    r'\bfix\b', r'\bfixed\b',
    # Confusion
    r"\bi don\'?t understand\b", r'\bwhat do you mean\b', r'\bhuh\?', r'\bwhat\?',
]

def get_all_patterns():
    """Combine hardcoded + learned patterns."""
    all_p = list(HARDCODED_PATTERNS)
    for entry in learned_data.get("patterns", []):
        all_p.append(entry["pattern"])
    return all_p

def regex_would_catch(user_text, patterns):
    """Check if any pattern matches the user text."""
    for p in patterns:
        try:
            if re.search(p, user_text, re.IGNORECASE):
                return True
        except re.error:
            continue
    return False

# --- Sample exchanges ---

sample_size = max(3, int(len(all_exchanges) * sample_rate))
sample_size = min(sample_size, len(all_exchanges))
sample = random.sample(all_exchanges, sample_size)

print(f"CALIBRATION: Sampling {sample_size}/{len(all_exchanges)} exchanges ({sample_rate*100:.0f}%)", file=sys.stderr)

# --- LLM classification (bypass regex, send raw to LLM) ---

CLASSIFY_PROMPT = """You are classifying a conversation exchange. The user message follows an assistant message.

Assistant said:
{assistant_text}

User replied:
{user_text}

Is the user's message a correction, complaint, or expression of frustration with the assistant? Answer YES or NO only."""

# Parse models from ACC_MODELS env var (comma-separated CLI commands)
acc_models_str = os.environ.get('ACC_MODELS', 'claude --model haiku -p,claude --model sonnet -p')
MODELS = []
for i, cmd_str in enumerate(acc_models_str.split(',')):
    cmd_parts = cmd_str.strip().split()
    if cmd_parts:
        model_name = f"model_{i+1}" if len(MODELS) > 0 else cmd_parts[0]
        MODELS.append((model_name, cmd_parts))

def llm_classify(assistant_text, user_text):
    """Classify via LLM. Returns True if error, False if not, None if failed."""
    prompt = CLASSIFY_PROMPT.format(
        assistant_text=assistant_text[:500],
        user_text=user_text[:500]
    )
    for model_name, cmd_prefix in MODELS:
        try:
            result = subprocess.run(
                cmd_prefix + [prompt],
                capture_output=True, text=True, timeout=45
            )
            if result.returncode == 0 and result.stdout.strip():
                return 'YES' in result.stdout.strip().upper()
        except (subprocess.TimeoutExpired, Exception):
            continue
    return None

# Classify each sample exchange
llm_errors = []      # LLM says YES
llm_non_errors = []  # LLM says NO

for exchange in sample:
    user_text = exchange.get('user_text', '')
    assistant_text = exchange.get('assistant_text', '')
    if not user_text:
        continue

    is_error = llm_classify(assistant_text, user_text)
    if is_error is None:
        print(f"  LLM failed on exchange, skipping", file=sys.stderr)
        continue
    if is_error:
        llm_errors.append(exchange)
    else:
        llm_non_errors.append(exchange)

print(f"CALIBRATION: LLM classified {len(llm_errors)} errors, {len(llm_non_errors)} non-errors from {sample_size} samples", file=sys.stderr)

# --- Find regex misses (LLM found error but regex wouldn't catch it) ---

all_patterns = get_all_patterns()
regex_misses = []

for exchange in llm_errors:
    user_text = exchange.get('user_text', '')
    if not regex_would_catch(user_text, all_patterns):
        regex_misses.append(exchange)

print(f"CALIBRATION: {len(regex_misses)} regex misses (LLM caught but regex missed)", file=sys.stderr)

# --- Extract patterns from misses ---

# Strong keywords that signal errors
STRONG_KEYWORDS = [
    'hallucinated', 'outdated', 'broken', 'borked', 'nonsense',
    'fabricated', 'invented', 'terrible', 'useless', 'disappeared',
    'doesnt work', "doesn't work", 'not working', 'stopped working',
    'you forgot', 'you broke', 'you deleted', 'you removed',
    'thats wrong', "that's wrong", 'completely wrong',
]

# Phrase templates to try
PHRASE_TEMPLATES = [
    r"you \w+ed",
    r"thats \w+",
    r"that's \w+",
    r"this is \w+",
    r"not \w+ing",
    r"why didn'?t",
    r"where is the \w+",
    r"where did the \w+",
]

def extract_candidate_patterns(user_text):
    """Try to extract a useful pattern from user text."""
    text_lower = user_text.lower()
    candidates = []

    # Check for strong keywords
    for kw in STRONG_KEYWORDS:
        if kw in text_lower:
            # Build a word-boundary pattern from the keyword
            escaped = re.escape(kw)
            pattern = r'\b' + escaped + r'\b'
            candidates.append(pattern)

    # Check phrase templates
    for template in PHRASE_TEMPLATES:
        match = re.search(template, text_lower)
        if match:
            # Use the matched phrase as a pattern
            matched_text = match.group()
            # Only if it's specific enough (>5 chars)
            if len(matched_text) > 5:
                candidates.append(r'\b' + re.escape(matched_text) + r'\b')

    return candidates

def validate_pattern(pattern, non_errors, max_false_positives=2):
    """Reject if pattern matches too many non-errors."""
    false_positives = 0
    try:
        compiled = re.compile(pattern, re.IGNORECASE)
    except re.error:
        return False

    for exchange in non_errors:
        user_text = exchange.get('user_text', '')
        if compiled.search(user_text):
            false_positives += 1
            if false_positives > max_false_positives:
                return False
    return True

def pattern_already_exists(pattern, existing_patterns):
    """Check if pattern is already in learned or hardcoded patterns."""
    for p in existing_patterns:
        if p == pattern:
            return True
    return False

new_patterns_added = 0
max_patterns = learned_data.get("maxPatterns", 50)

for exchange in regex_misses:
    user_text = exchange.get('user_text', '')
    candidates = extract_candidate_patterns(user_text)

    for candidate in candidates:
        # Skip if already known
        if pattern_already_exists(candidate, all_patterns):
            continue

        # Validate against non-errors
        if not validate_pattern(candidate, llm_non_errors):
            print(f"  REJECTED (false positives): {candidate}", file=sys.stderr)
            continue

        # Check max patterns cap
        if len(learned_data["patterns"]) >= max_patterns:
            print(f"  SKIPPED (max patterns reached): {candidate}", file=sys.stderr)
            break

        # Add the pattern
        learned_data["patterns"].append({
            "pattern": candidate,
            "source_text": user_text[:200],
            "added": datetime.now(timezone.utc).isoformat(),
            "calibration_run": cal_state["stats"]["calibrationRuns"] + 1
        })
        all_patterns.append(candidate)
        new_patterns_added += 1
        print(f"  LEARNED: {candidate}", file=sys.stderr)

# --- Update state files ---

cal_state["stats"]["calibrationRuns"] += 1
cal_state["stats"]["samplesAnalyzed"] += len(sample)
cal_state["stats"]["regexMisses"] += len(regex_misses)
cal_state["stats"]["patternsAdded"] += new_patterns_added
cal_state["lastCalibration"] = datetime.now(timezone.utc).isoformat()

with open(learned_file, 'w') as f:
    json.dump(learned_data, f, indent=2)
    f.write('\n')

with open(calibration_state_file, 'w') as f:
    json.dump(cal_state, f, indent=2)
    f.write('\n')

# --- Save confirmed errors for pipeline to use ---
# This allows calibration runs to skip Haiku screening
workspace = os.environ.get('WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
calib_errors_file = os.path.join(workspace, 'memory', 'calibration-errors.json')
with open(calib_errors_file, 'w') as f:
    json.dump(llm_errors, f, indent=2)
    f.write('\n')

# --- Report ---

print(f"", file=sys.stderr)
print(f"CALIBRATION COMPLETE:", file=sys.stderr)
print(f"  Samples analyzed: {len(sample)}", file=sys.stderr)
print(f"  LLM errors found: {len(llm_errors)}", file=sys.stderr)
print(f"  Regex misses: {len(regex_misses)}", file=sys.stderr)
print(f"  New patterns learned: {new_patterns_added}", file=sys.stderr)
print(f"  Total learned patterns: {len(learned_data['patterns'])}", file=sys.stderr)
PYTHON
