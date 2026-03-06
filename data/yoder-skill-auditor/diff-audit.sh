#!/bin/bash
# Skill Auditor v2.0.0 - Diff Audit
# Compare a skill before and after update, highlight new security concerns
# Usage: bash diff-audit.sh /path/to/old-version /path/to/new-version [--json]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AUDIT="$SCRIPT_DIR/audit.sh"

OLD_DIR="${1:?Usage: diff-audit.sh /path/to/old-version /path/to/new-version [--json]}"
NEW_DIR="${2:?Usage: diff-audit.sh /path/to/old-version /path/to/new-version [--json]}"
JSON_MODE=false
[ "$3" = "--json" ] && JSON_MODE=true

RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'; BLUE='\033[0;34m'; NC='\033[0m'

OLD_RESULT=$(bash "$AUDIT" "$OLD_DIR" --json 2>/dev/null)
NEW_RESULT=$(bash "$AUDIT" "$NEW_DIR" --json 2>/dev/null)

if $JSON_MODE; then
    python3 -c "
import json, sys
old = json.loads('''$OLD_RESULT''')
new = json.loads('''$NEW_RESULT''')

old_checks = {(i['check'], i['severity']): i for i in old.get('items', [])}
new_checks = {(i['check'], i['severity']): i for i in new.get('items', [])}

added = [v for k, v in new_checks.items() if k not in old_checks and v['severity'] in ('critical', 'warning')]
removed = [v for k, v in old_checks.items() if k not in new_checks and v['severity'] in ('critical', 'warning')]

result = {
    'old': {'skill': old['skill'], 'criticals': old['criticals'], 'warnings': old['warnings'], 'verdict': old['verdict']},
    'new': {'skill': new['skill'], 'criticals': new['criticals'], 'warnings': new['warnings'], 'verdict': new['verdict']},
    'new_issues': added,
    'resolved_issues': removed,
    'delta_criticals': new['criticals'] - old['criticals'],
    'delta_warnings': new['warnings'] - old['warnings']
}
print(json.dumps(result, indent=2))
" 2>/dev/null
else
    OLD_NAME=$(echo "$OLD_RESULT" | python3 -c "import json,sys;print(json.load(sys.stdin)['skill'])" 2>/dev/null)
    NEW_NAME=$(echo "$NEW_RESULT" | python3 -c "import json,sys;print(json.load(sys.stdin)['skill'])" 2>/dev/null)
    
    echo "========================================="
    echo "  Diff Audit: $OLD_NAME → $NEW_NAME"
    echo "========================================="
    echo ""
    
    python3 -c "
import json, sys
old = json.loads('''$OLD_RESULT''')
new = json.loads('''$NEW_RESULT''')

print(f\"  Old: {old['criticals']}C / {old['warnings']}W → {old['verdict'].upper()}\")
print(f\"  New: {new['criticals']}C / {new['warnings']}W → {new['verdict'].upper()}\")
print()

old_checks = {(i['check'], i['severity']): i for i in old.get('items', [])}
new_checks = {(i['check'], i['severity']): i for i in new.get('items', [])}

added = [(k, v) for k, v in new_checks.items() if k not in old_checks and v['severity'] in ('critical', 'warning')]
removed = [(k, v) for k, v in old_checks.items() if k not in new_checks and v['severity'] in ('critical', 'warning')]

if added:
    print('  🔴 NEW ISSUES:')
    for (check, sev), item in added:
        print(f'    [{sev.upper()}] {check}: {item[\"message\"]}')
    print()

if removed:
    print('  🟢 RESOLVED:')
    for (check, sev), item in removed:
        print(f'    [{sev.upper()}] {check}: {item[\"message\"]}')
    print()

if not added and not removed:
    print('  No security changes detected.')
    print()

dc = new['criticals'] - old['criticals']
dw = new['warnings'] - old['warnings']
if dc > 0 or dw > 0:
    print(f'  ⚠️  REGRESSION: +{dc} criticals, +{dw} warnings')
elif dc < 0 or dw < 0:
    print(f'  ✅ IMPROVEMENT: {dc} criticals, {dw} warnings')
else:
    print(f'  ➡️  No change in finding counts')
" 2>/dev/null
fi
