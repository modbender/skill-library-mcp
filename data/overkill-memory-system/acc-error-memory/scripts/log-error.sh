#!/bin/bash
# ACC: Log an error pattern
# Usage: log-error.sh --pattern "name" --context "what happened" [--mitigation "how to avoid"]

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
STATE_FILE="$WORKSPACE/memory/acc-state.json"

# Parse arguments
PATTERN=""
CONTEXT=""
MITIGATION=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --pattern) PATTERN="$2"; shift 2 ;;
        --context) CONTEXT="$2"; shift 2 ;;
        --mitigation) MITIGATION="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

if [ -z "$PATTERN" ]; then
    echo "Usage: log-error.sh --pattern 'name' --context 'what happened' [--mitigation 'how to avoid']"
    exit 1
fi

PATTERN="$PATTERN" CONTEXT="$CONTEXT" MITIGATION="$MITIGATION" python3 << 'PYTHON'
import json
from datetime import datetime, timezone
from pathlib import Path
import os

workspace = os.environ.get('WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
state_file = Path(workspace) / 'memory' / 'acc-state.json'

pattern = os.environ.get('PATTERN', '')
context = os.environ.get('CONTEXT', '')
mitigation = os.environ.get('MITIGATION', '')

# Load state
with open(state_file) as f:
    state = json.load(f)

now = datetime.now(timezone.utc).isoformat()
active = state.setdefault('activePatterns', {})
resolved = state.setdefault('resolved', {})
config = state.get('config', {})
stats = state.setdefault('stats', {})

# Check if this was a resolved pattern (regression!)
regression = False
if pattern in resolved:
    print(f"⚠️ REGRESSION: '{pattern}' was resolved but occurred again!")
    # Extract lesson from old resolved data (supports both old and new format)
    old_data = resolved[pattern]
    old_lesson = old_data.get('lesson', {})
    old_mitigation = ''
    if isinstance(old_lesson, dict):
        old_mitigation = old_lesson.get('mitigation', '')
    if not old_mitigation:
        old_mitigation = old_data.get('lessonLearned', old_data.get('mitigation', ''))
    # Move back to active
    old_data_copy = resolved.pop(pattern)
    active[pattern] = {
        'count': old_data_copy.get('count', 0) + 1,
        'severity': 'critical',  # Regressions are always critical
        'firstSeen': old_data_copy.get('firstSeen', now),
        'lastSeen': now,
        'context': context or old_data_copy.get('context', ''),
        'mitigation': mitigation or old_mitigation,
        'regression': True,
        'previouslyResolvedOn': old_data_copy.get('resolvedOn'),
        'failedLesson': old_lesson if isinstance(old_lesson, dict) else {'mitigation': old_mitigation},
    }
    if isinstance(old_lesson, dict) and old_lesson:
        print(f"   Previous lesson was: {old_lesson.get('mitigation', 'unknown')}")
        print(f"   Resolution type was: {old_lesson.get('resolutionType', 'unknown')}")
    stats['totalRegressions'] = stats.get('totalRegressions', 0) + 1
    regression = True

elif pattern in active:
    # Existing pattern - increment
    data = active[pattern]
    data['count'] = data.get('count', 0) + 1
    data['lastSeen'] = now
    if context:
        data['context'] = context
    if mitigation:
        data['mitigation'] = mitigation
    
    # Update severity based on count
    count = data['count']
    if count >= config.get('criticalThreshold', 3):
        data['severity'] = 'critical'
    elif count >= config.get('warningThreshold', 2):
        data['severity'] = 'warning'
    
    print(f"📈 Error pattern '{pattern}' count: {count} (severity: {data['severity']})")

else:
    # New pattern
    active[pattern] = {
        'count': 1,
        'severity': 'normal',
        'firstSeen': now,
        'lastSeen': now,
        'context': context,
        'mitigation': mitigation or 'be more careful'
    }
    print(f"📝 New error pattern logged: '{pattern}'")

stats['totalErrorsLogged'] = stats.get('totalErrorsLogged', 0) + 1
state['lastUpdated'] = now

with open(state_file, 'w') as f:
    json.dump(state, f, indent=2)

# Check if we should alert (5+ occurrences)
if pattern in active:
    count = active[pattern].get('count', 0)
    if count >= config.get('alertThreshold', 5) and count % 5 == 0:
        print(f"🔴 ALERT: Error pattern '{pattern}' has occurred {count} times!")
        print(f"   Consider structural fix.")
PYTHON

# Sync state to markdown
"$WORKSPACE/skills/anterior-cingulate-memory/scripts/sync-state.sh"
