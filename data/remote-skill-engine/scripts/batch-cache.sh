#!/bin/bash
# Batch cache multiple skills from a JSON file

if [ -z "$1" ]; then
    echo "Usage: batch-cache.sh <skills-file.json>"
    echo ""
    echo "JSON format:"
    echo '{'
    echo '  "skills": ['
    echo '    {"name": "skill-a", "source": "clawhub://skill-a"},'
    echo '    {"name": "skill-b", "source": "github://user/repo/main"}'
    echo '  ]'
    echo '}'
    exit 1
fi

SKILLS_FILE="$1"
SCRIPT_DIR="$(dirname "$0")"

if [ ! -f "$SKILLS_FILE" ]; then
    echo "❌ File not found: $SKILLS_FILE"
    exit 1
fi

echo "📦 Batch caching skills from: $SKILLS_FILE"
echo ""

# Parse JSON and cache each skill
python3 -c "
import json
import sys
import subprocess

with open('$SKILLS_FILE', 'r') as f:
    data = json.load(f)

skills = data.get('skills', [])
print(f'Found {len(skills)} skills to cache')
print('=' * 60)

success_count = 0
fail_count = 0

for skill in skills:
    name = skill.get('name')
    source = skill.get('source')
    
    if not name or not source:
        print(f'⚠️  Skipping invalid entry: {skill}')
        fail_count += 1
        continue
    
    print(f'\\n[{success_count + fail_count + 1}/{len(skills)}] Caching: {name}')
    result = subprocess.run(['python3', '$SCRIPT_DIR/cache-skill.py', name, source])
    
    if result.returncode == 0:
        success_count += 1
    else:
        fail_count += 1

print('')
print('=' * 60)
print(f'✅ Success: {success_count}')
print(f'❌ Failed: {fail_count}')
"

echo ""
echo "🎉 Batch caching complete!"
