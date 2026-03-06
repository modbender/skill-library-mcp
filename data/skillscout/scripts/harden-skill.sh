#!/bin/bash
# harden-skill.sh — Deep security analysis for skills that passed initial review
# Usage: bash harden-skill.sh <skill-name>
# Reads from data/skills.json, fetches source, spawns hardening agent

set -e

SKILL_NAME="${1:?Usage: harden-skill.sh <skill-name>}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Find skill in catalog
SKILL_INFO=$(python3 -c "
import json
with open('$PROJECT_DIR/data/skills.json') as f:
    catalog = json.load(f)
for s in catalog['skills']:
    if s['name'] == '$SKILL_NAME':
        print(f'{s[\"author\"]}/{s[\"name\"]}')
        break
else:
    print('NOT_FOUND')
")

if [ "$SKILL_INFO" = "NOT_FOUND" ]; then
    echo "Error: Skill '$SKILL_NAME' not found in catalog. Run initial review first."
    exit 1
fi

echo "Fetching source for $SKILL_INFO..."
bash "$SCRIPT_DIR/fetch-skill.sh" "$SKILL_INFO" > "/tmp/skillscout-harden-$SKILL_NAME.md" 2>/dev/null

LINES=$(wc -l < "/tmp/skillscout-harden-$SKILL_NAME.md")
echo "Fetched $LINES lines. Ready for hardening review."
echo "Input file: /tmp/skillscout-harden-$SKILL_NAME.md"
