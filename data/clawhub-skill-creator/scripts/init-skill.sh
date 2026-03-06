#!/bin/bash
#
# Initialize new skill for clawhub
# Usage: ./init-skill.sh <skill-name>
#

set -e

SKILL_NAME="${1:-}"

if [[ -z "$SKILL_NAME" ]]; then
    echo "Error: Skill name required"
    echo "Usage: $0 <skill-name>"
    exit 1
fi

if [[ ! "$SKILL_NAME" =~ ^[a-z0-9-]+$ ]]; then
    echo "Error: Skill name must be lowercase alphanumeric with hyphens"
    exit 1
fi

if [[ -d "$SKILL_NAME" ]]; then
    echo "Error: Directory already exists: $SKILL_NAME"
    exit 1
fi

mkdir -p "$SKILL_NAME"

cat > "$SKILL_NAME/SKILL.md" << EOF
---
name: $SKILL_NAME
description: What this skill does. Use when: (1) trigger-1, (2) trigger-2, (3) trigger-3.
---

# Skill Title

Brief purpose (1-2 sentences).

## Quick Start

\`\`\`bash
# Example command
\`\`\`

## Workflow

1. Step one
2. Step two
3. Step three

## Resources

- \`references/advanced.md\` - For complex cases
EOF

cat > "$SKILL_NAME/_meta.json" << EOF
{
  "name": "$SKILL_NAME",
  "version": "1.0.0",
  "description": "Short description for registry",
  "requires": {
    "env": [],
    "credentials": []
  },
  "tags": ["latest"]
}
EOF

cat > "$SKILL_NAME/LICENSE.txt" << EOF
MIT License

Copyright (c) $(date +%Y)

Permission is hereby granted...
EOF

echo "✅ Created: $SKILL_NAME/"
echo ""
echo "Next steps:"
echo "1. Edit $SKILL_NAME/SKILL.md"
echo "2. Update $SKILL_NAME/_meta.json"
echo "3. Add references/ if needed"
echo "4. Run: clawhub publish $SKILL_NAME --version 1.0.0"