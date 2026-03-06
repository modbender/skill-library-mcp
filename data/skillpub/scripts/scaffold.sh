#!/usr/bin/env bash
set -euo pipefail

# scaffold.sh - Create a new skill from template
# Usage: scaffold.sh <skill-name> [--dir <output-dir>]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/../templates/starter"

usage() {
  echo "Usage: $0 <skill-name> [--dir <output-dir>]"
  echo ""
  echo "Creates a new skill folder with SKILL.md template."
  echo ""
  echo "Options:"
  echo "  --dir <path>    Output directory (default: ./skills)"
  echo ""
  echo "Example:"
  echo "  $0 my-cool-skill"
  echo "  $0 my-cool-skill --dir /path/to/skills"
  exit 1
}

# Parse args
SKILL_NAME=""
OUTPUT_DIR="./skills"

while [[ $# -gt 0 ]]; do
  case $1 in
    --dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    -*)
      echo "Unknown option: $1"
      usage
      ;;
    *)
      if [[ -z "$SKILL_NAME" ]]; then
        SKILL_NAME="$1"
      else
        echo "Unexpected argument: $1"
        usage
      fi
      shift
      ;;
  esac
done

if [[ -z "$SKILL_NAME" ]]; then
  echo "Error: skill-name is required"
  usage
fi

# Validate skill name (lowercase, hyphens, digits only)
if ! [[ "$SKILL_NAME" =~ ^[a-z0-9-]+$ ]]; then
  echo "Error: Skill name must be lowercase letters, digits, and hyphens only."
  echo "Got: $SKILL_NAME"
  exit 1
fi

if [[ ${#SKILL_NAME} -gt 64 ]]; then
  echo "Error: Skill name must be 64 characters or less."
  exit 1
fi

# Create skill directory
SKILL_DIR="$OUTPUT_DIR/$SKILL_NAME"

if [[ -d "$SKILL_DIR" ]]; then
  echo "Error: Directory already exists: $SKILL_DIR"
  exit 1
fi

mkdir -p "$SKILL_DIR/scripts"

# Generate SKILL.md from template
cat > "$SKILL_DIR/SKILL.md" << 'EOF'
---
name: {{SKILL_NAME}}
description: >
  TODO: Describe what this skill does and when to use it.
  Be specific about triggers: "Use when asked to...", "Use for..."
  This description determines when the skill gets activated.
---

# {{SKILL_NAME}}

TODO: Write instructions for using this skill.

## Usage

```bash
# TODO: Add usage examples
```

## Notes

- TODO: Add any important notes
EOF

# Replace placeholder
sed -i "s/{{SKILL_NAME}}/$SKILL_NAME/g" "$SKILL_DIR/SKILL.md"

# Create placeholder script
cat > "$SKILL_DIR/scripts/.gitkeep" << 'EOF'
# Add your scripts here
# Example: main.sh, run.py, etc.
EOF

echo "✅ Created skill: $SKILL_DIR"
echo ""
echo "Next steps:"
echo "  1. Edit $SKILL_DIR/SKILL.md"
echo "  2. Add scripts to $SKILL_DIR/scripts/"
echo "  3. Validate: bash $(dirname "$0")/validate.sh $SKILL_DIR"
echo "  4. Security scan: bash $(dirname "$0")/security-scan.sh $SKILL_DIR"
echo "  5. Publish: bash $(dirname "$0")/publish.sh $SKILL_DIR --slug $SKILL_NAME --version 1.0.0"
