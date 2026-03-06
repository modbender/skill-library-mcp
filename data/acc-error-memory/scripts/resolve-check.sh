#!/bin/bash
# ACC: Check for patterns that should be resolved (30+ days without occurrence)
# Run as part of daily analysis

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
STATE_FILE="$WORKSPACE/memory/acc-state.json"

python3 << 'PYTHON'
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import os

workspace = os.environ.get('WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
state_file = Path(workspace) / 'memory' / 'acc-state.json'

with open(state_file) as f:
    state = json.load(f)

now = datetime.now(timezone.utc)
active = state.get('activePatterns', {})
resolved = state.setdefault('resolved', {})
config = state.get('config', {})
stats = state.setdefault('stats', {})

threshold_days = config.get('resolutionThresholdDays', 30)
to_resolve = []

for name, data in list(active.items()):
    last_seen_str = data.get('lastSeen', '')
    if not last_seen_str:
        continue
    
    try:
        last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
        days_since = (now - last_seen).days
        
        if days_since >= threshold_days:
            to_resolve.append((name, data, days_since))
    except:
        continue

if not to_resolve:
    print("✅ No patterns ready for resolution")
else:
    for name, data, days_since in to_resolve:
        print(f"🎓 Resolving '{name}' — {days_since} days without error")

        # Analyze what likely led to resolution
        mitigation = data.get('mitigation', '')
        context = data.get('context', '')
        count = data.get('count', 0)
        severity = data.get('severity', 'normal')
        first_seen = data.get('firstSeen', '')
        last_seen = data.get('lastSeen', '')
        was_regression = data.get('regression', False)

        # Derive resolution analysis
        # How long was the pattern active before it stopped?
        active_duration_days = 0
        if first_seen and last_seen:
            try:
                fs = datetime.fromisoformat(first_seen.replace('Z', '+00:00'))
                ls = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                active_duration_days = (ls - fs).days
            except:
                pass

        # Classify resolution type based on available data
        if count == 1 and active_duration_days == 0:
            resolution_type = 'one-off'
            resolution_insight = 'Single occurrence that never repeated. Likely situational rather than systematic.'
        elif was_regression:
            resolution_type = 'regression-fixed'
            resolution_insight = f'Pattern regressed but was corrected again. Mitigation needed reinforcement.'
        elif severity == 'critical':
            resolution_type = 'critical-resolved'
            resolution_insight = f'Repeated {count}x over {active_duration_days} day(s) before being resolved. The mitigation strategy worked after sustained effort.'
        elif count >= 2:
            resolution_type = 'pattern-broken'
            resolution_insight = f'Occurred {count}x over {active_duration_days} day(s). Behavioral change took hold.'
        else:
            resolution_type = 'natural'
            resolution_insight = 'Pattern resolved through normal behavioral adjustment.'

        # Build lesson learned object
        lesson = {
            'mitigation': mitigation or 'learned to avoid this',
            'resolutionType': resolution_type,
            'insight': resolution_insight,
            'activeDurationDays': active_duration_days,
            'peakSeverity': severity,
            'totalOccurrences': count,
        }

        if was_regression:
            lesson['previouslyResolvedOn'] = data.get('previouslyResolvedOn', '')
            lesson['note'] = 'This pattern regressed before being resolved again. Extra vigilance recommended.'

        # Move to resolved with enriched data
        resolved[name] = {
            'count': count,
            'severity': severity,
            'firstSeen': first_seen,
            'lastSeen': last_seen,
            'resolvedOn': now.isoformat(),
            'daysClear': days_since,
            'context': context,
            'lesson': lesson,
        }

        print(f"   Type: {resolution_type}")
        print(f"   Lesson: {resolution_insight}")
        if mitigation:
            print(f"   Mitigation: {mitigation}")

        # Remove from active
        del active[name]
        stats['totalResolved'] = stats.get('totalResolved', 0) + 1

    state['lastUpdated'] = now.isoformat()

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    print(f"\n✅ Resolved {len(to_resolve)} pattern(s)")
PYTHON

# Sync state
"$WORKSPACE/skills/anterior-cingulate-memory/scripts/sync-state.sh"
