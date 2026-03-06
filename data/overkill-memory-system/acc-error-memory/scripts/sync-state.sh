#!/bin/bash
# ACC: Generate ACC_STATE.md from acc-state.json
# Creates human-readable state for context injection

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
STATE_FILE="$WORKSPACE/memory/acc-state.json"
STATE_MD="$WORKSPACE/ACC_STATE.md"

if [ ! -f "$STATE_FILE" ]; then
    echo "No acc-state.json found"
    exit 1
fi

# Generate markdown using Python for JSON parsing
python3 << 'PYTHON'
import json
from datetime import datetime, timezone
from pathlib import Path
import os

workspace = os.environ.get('WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
state_file = Path(workspace) / 'memory' / 'acc-state.json'
state_md = Path(workspace) / 'ACC_STATE.md'

with open(state_file) as f:
    state = json.load(f)

now = datetime.now(timezone.utc)
lines = []
lines.append(f"# ACC State — {now.strftime('%b %d, %Y %H:%M')} UTC")
lines.append("")

active = state.get('activePatterns', {})
resolved = state.get('resolved', {})
config = state.get('config', {})

# Sort active by severity and count
critical = {k: v for k, v in active.items() if v.get('severity') == 'critical'}
warning = {k: v for k, v in active.items() if v.get('severity') == 'warning'}
normal = {k: v for k, v in active.items() if v.get('severity') not in ('critical', 'warning')}

if critical:
    lines.append("## 🔴 REPEATED ERRORS — Act on these!")
    lines.append("")
    lines.append("| Pattern | Count | Last | Mitigation |")
    lines.append("|---------|-------|------|------------|")
    for name, data in sorted(critical.items(), key=lambda x: -x[1].get('count', 0)):
        count = data.get('count', 0)
        last = data.get('lastSeen', 'unknown')[:10]
        mitigation = data.get('mitigation', 'be careful')
        regression = " ⚠️ REGRESSION" if data.get('regression') else ""
        lines.append(f"| {name}{regression} | {count}x | {last} | {mitigation} |")
    lines.append("")

if warning:
    lines.append("## ⚠️ Emerging Patterns (2x)")
    lines.append("")
    lines.append("| Pattern | Count | Last | Watch for |")
    lines.append("|---------|-------|------|-----------|")
    for name, data in sorted(warning.items(), key=lambda x: -x[1].get('count', 0)):
        count = data.get('count', 0)
        last = data.get('lastSeen', 'unknown')[:10]
        context = data.get('context', 'unknown situation')
        lines.append(f"| {name} | {count}x | {last} | {context} |")
    lines.append("")

if normal:
    lines.append("## 📝 Recent Errors (1x)")
    lines.append("")
    for name, data in normal.items():
        last = data.get('lastSeen', 'unknown')[:10]
        context = data.get('context', '')
        lines.append(f"- **{name}** ({last}): {context}")
    lines.append("")

if resolved:
    lines.append("## ✅ Resolved — Lessons Learned")
    lines.append("")
    for name, data in resolved.items():
        was_count = data.get('count', 0)
        days_clear = data.get('daysClear', 0)
        context = data.get('context', '')
        lesson = data.get('lesson', {})
        # Support both old format (lessonLearned string) and new format (lesson object)
        if isinstance(lesson, dict) and lesson:
            mitigation = lesson.get('mitigation', 'learned to avoid')
            resolution_type = lesson.get('resolutionType', 'unknown')
            insight = lesson.get('insight', '')
            peak = lesson.get('peakSeverity', 'normal')
            lines.append(f"### {name}")
            lines.append(f"- **Was:** {was_count}x (peak: {peak}) | **Clear:** {days_clear}d | **Type:** {resolution_type}")
            if context:
                lines.append(f"- **Context:** {context}")
            lines.append(f"- **What worked:** {mitigation}")
            if insight:
                lines.append(f"- **Insight:** {insight}")
            if lesson.get('note'):
                lines.append(f"- **Note:** {lesson['note']}")
            lines.append("")
        else:
            # Legacy format fallback
            lesson_text = data.get('lessonLearned', str(lesson) if lesson else 'learned to avoid')
            lines.append(f"- **{name}** ({was_count}x, {days_clear}d clear): {lesson_text}")
            lines.append("")

if not active and not resolved:
    lines.append("## ✨ Clean Slate")
    lines.append("")
    lines.append("No error patterns detected yet. This will populate as the daily analysis runs.")
    lines.append("")

# Stats
stats = state.get('stats', {})
lines.append("---")
lines.append(f"*Total errors logged: {stats.get('totalErrorsLogged', 0)} | Resolved: {stats.get('totalResolved', 0)} | Regressions: {stats.get('totalRegressions', 0)}*")

with open(state_md, 'w') as f:
    f.write('\n'.join(lines))

print(f"✅ ACC_STATE.md updated")
PYTHON
