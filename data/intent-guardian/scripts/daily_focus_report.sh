#!/bin/bash
# Generate a daily focus summary from activity log data.
# Outputs structured data for the LLM to format into a human-readable report.

LOG_DIR="${INTENT_GUARDIAN_DATA_DIR:-$HOME/.openclaw/memory/skills/intent-guardian}"
LOG_FILE="$LOG_DIR/activity_log.jsonl"
FEEDBACK_FILE="$LOG_DIR/reminder_feedback.jsonl"
TARGET_DATE="${1:-$(date +%Y-%m-%d)}"

if [ ! -f "$LOG_FILE" ]; then
    echo '{"error": "No activity data found"}'
    exit 0
fi

python3 -c "
import json, sys
from collections import Counter, defaultdict
from datetime import datetime

target = '$TARGET_DATE'
activities = []
with open('$LOG_FILE') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
            ts = e.get('ts', '')
            if ts.startswith(target):
                activities.append(e)
        except json.JSONDecodeError:
            continue

if not activities:
    print(json.dumps({'date': target, 'error': 'No activity for this date'}))
    sys.exit(0)

app_time = Counter()
hourly = defaultdict(int)
transitions = []
prev_app = None

for a in activities:
    app = a.get('app', 'unknown')
    app_time[app] += 1
    ts = a.get('ts', '')
    try:
        hour = ts[11:13]
        hourly[hour] += 1
    except (IndexError, ValueError):
        pass
    if prev_app and prev_app != app:
        transitions.append({'from': prev_app, 'to': app})
    prev_app = app

feedback_stats = {'accepted': 0, 'dismissed': 0, 'ignored': 0}
feedback_file = '$FEEDBACK_FILE'
try:
    with open(feedback_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                fb = json.loads(line)
                if fb.get('ts', '').startswith(target):
                    r = fb.get('response', '')
                    if r in feedback_stats:
                        feedback_stats[r] += 1
            except json.JSONDecodeError:
                continue
except FileNotFoundError:
    pass

transition_counts = Counter()
for t in transitions:
    key = t['from'] + ' -> ' + t['to']
    transition_counts[key] += 1

report = {
    'date': target,
    'total_events': len(activities),
    'unique_apps': len(app_time),
    'top_apps': app_time.most_common(10),
    'hourly_distribution': dict(sorted(hourly.items())),
    'total_context_switches': len(transitions),
    'top_transitions': transition_counts.most_common(10),
    'reminder_stats': feedback_stats
}

print(json.dumps(report, ensure_ascii=True, indent=2))
" 2>/dev/null
