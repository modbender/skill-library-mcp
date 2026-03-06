#!/bin/bash
# ACC: Retrieve lessons learned from resolved patterns
# Use this to check what worked before making decisions in similar contexts
#
# Usage:
#   get-lessons.sh                    # List all lessons
#   get-lessons.sh --pattern "name"   # Get specific lesson
#   get-lessons.sh --json             # Output raw JSON

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
STATE_FILE="$WORKSPACE/memory/acc-state.json"

PATTERN=""
JSON_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --pattern) PATTERN="$2"; shift 2 ;;
        --json) JSON_MODE=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

export PATTERN JSON_MODE

python3 << 'PYTHON'
import json
import os
import sys

workspace = os.environ.get('WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
state_file = os.path.join(workspace, 'memory', 'acc-state.json')
pattern_filter = os.environ.get('PATTERN', '')
json_mode = os.environ.get('JSON_MODE', 'false') == 'true'

with open(state_file) as f:
    state = json.load(f)

resolved = state.get('resolved', {})

if not resolved:
    print("No resolved patterns yet. Lessons accumulate as error patterns are resolved (30+ days clear).")
    sys.exit(0)

# Filter if pattern specified
if pattern_filter:
    if pattern_filter in resolved:
        resolved = {pattern_filter: resolved[pattern_filter]}
    else:
        # Fuzzy match
        matches = {k: v for k, v in resolved.items() if pattern_filter.lower() in k.lower()}
        if matches:
            resolved = matches
        else:
            print(f"No resolved pattern matching '{pattern_filter}'")
            sys.exit(1)

if json_mode:
    print(json.dumps(resolved, indent=2))
    sys.exit(0)

# Human-readable output
print(f"📚 Lessons Learned ({len(resolved)} resolved pattern(s))")
print("=" * 50)

for name, data in resolved.items():
    print(f"\n🎓 {name}")
    print(f"   Context: {data.get('context', 'unknown')}")
    count = data.get('count', 0)
    days_clear = data.get('daysClear', 0)
    print(f"   Occurred {count}x, clear for {days_clear} days")

    lesson = data.get('lesson', {})
    if isinstance(lesson, dict) and lesson:
        print(f"   What worked: {lesson.get('mitigation', 'unknown')}")
        print(f"   Resolution type: {lesson.get('resolutionType', 'unknown')}")
        insight = lesson.get('insight', '')
        if insight:
            print(f"   Insight: {insight}")
        note = lesson.get('note', '')
        if note:
            print(f"   Note: {note}")
    else:
        # Legacy format
        lesson_text = data.get('lessonLearned', str(lesson) if lesson else 'unknown')
        print(f"   Lesson: {lesson_text}")

    resolved_on = data.get('resolvedOn', 'unknown')
    if resolved_on != 'unknown':
        print(f"   Resolved: {resolved_on[:10]}")
PYTHON
