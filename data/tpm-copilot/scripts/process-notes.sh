#!/usr/bin/env bash
set -euo pipefail

FILE=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --file) FILE="$2"; shift 2 ;;
    *) FILE="$1"; shift ;;
  esac
done

[ -z "$FILE" ] || [ ! -f "$FILE" ] && { echo "Usage: process-notes.sh --file <meeting-notes.md>"; exit 1; }

BASE_DIR="${TPM_DIR:-$HOME/.openclaw/workspace/tpm}"

export TPM_BASE_DIR="$BASE_DIR"
export TPM_NOTES_FILE="$FILE"

python3 << 'PYEOF'
import json, os, re
from datetime import datetime, timedelta

base_dir = os.environ["TPM_BASE_DIR"]
notes_file = os.environ["TPM_NOTES_FILE"]

with open(notes_file) as f:
    content = f.read()

# Extract action items using common patterns
patterns = [
    r'(?:^|\n)\s*(?:AI|ACTION|TODO|ACTION ITEM)[:\s]+(.+?)(?:\n|$)',
    r'(?:^|\n)\s*\[\s*\]\s+(.+?)(?:\n|$)',
    r'(?:^|\n)\s*-\s*\*\*ACTION\*\*[:\s]*(.+?)(?:\n|$)',
]

raw_actions = []
for pattern in patterns:
    matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
    raw_actions.extend(matches)

# Deduplicate
seen = set()
actions = []
for a in raw_actions:
    a = a.strip()
    if a and a not in seen:
        seen.add(a)
        
        # Try to extract owner (look for @name, "→ name", "- name", "(owner: name)")
        owner = ""
        owner_match = re.search(r'[@→→]\s*(\w+)', a) or re.search(r'\((?:owner|assigned)[:\s]*([^)]+)\)', a, re.IGNORECASE)
        if owner_match:
            owner = owner_match.group(1).strip()
        
        # Try to extract due date
        due = ""
        due_match = re.search(r'(?:by|due|before)[:\s]*(\d{4}-\d{2}-\d{2}|\w+ \d{1,2})', a, re.IGNORECASE)
        if due_match:
            due = due_match.group(1)
        elif re.search(r'(?:today|eod)', a, re.IGNORECASE):
            due = datetime.now().strftime("%Y-%m-%d")
        elif re.search(r'(?:tomorrow)', a, re.IGNORECASE):
            due = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif re.search(r'(?:this week|eow)', a, re.IGNORECASE):
            days_until_friday = (4 - datetime.now().weekday()) % 7
            due = (datetime.now() + timedelta(days=days_until_friday)).strftime("%Y-%m-%d")
        
        actions.append({
            "description": a,
            "owner": owner,
            "due_date": due,
            "status": "open",
            "source_file": notes_file,
            "extracted_at": datetime.now().isoformat(),
        })

print(f"📝 Processed: {notes_file}")
print(f"   Found {len(actions)} action item(s):\n")

for i, a in enumerate(actions, 1):
    owner_str = f" → {a['owner']}" if a['owner'] else ""
    due_str = f" (due: {a['due_date']})" if a['due_date'] else ""
    print(f"   {i}. {a['description']}{owner_str}{due_str}")

# Save/append to actions tracker
actions_file = os.path.join(base_dir, "meetings", "actions.json")
existing = []
if os.path.exists(actions_file):
    with open(actions_file) as f:
        existing = json.load(f)

existing.extend(actions)
os.makedirs(os.path.dirname(actions_file), exist_ok=True)
with open(actions_file, "w") as f:
    json.dump(existing, f, indent=2)

print(f"\n   ✅ Added to action tracker ({len(existing)} total items)")
print(f"   Run action-tracker.sh to view all items")
PYEOF
