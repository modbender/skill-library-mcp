#!/bin/bash

# Agent Sync - Project Initializer
# Usage: ./init.sh <project-name>

set -e

PROJECT_NAME="${1:-my-project}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATES_DIR="$SCRIPT_DIR/../templates"
TARGET_DIR="$(pwd)"

echo "Initializing agent-sync for: $PROJECT_NAME"
echo "Target directory: $TARGET_DIR"

# Create directories
mkdir -p "$TARGET_DIR/archive/weekly"
mkdir -p "$TARGET_DIR/docs"

# Copy templates (skip if exists)
files=("TASK.md" "CHANGELOG.md" "CONTEXT.md" "llms.txt" "WEEKLY-REPORT.md")

for file in "${files[@]}"; do
    if [ ! -f "$TARGET_DIR/$file" ]; then
        cp "$TEMPLATES_DIR/$file" "$TARGET_DIR/$file"
        echo "  Created $file"
    else
        echo "  $file already exists, skipping"
    fi
done

# Copy docs
if [ ! -f "$TARGET_DIR/docs/BEST-PRACTICES.md" ]; then
    cp "$SCRIPT_DIR/../docs/BEST-PRACTICES.md" "$TARGET_DIR/docs/"
    echo "  Created docs/BEST-PRACTICES.md"
fi

# Replace project name placeholder in llms.txt
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/\[项目名称\]/$PROJECT_NAME/g" "$TARGET_DIR/llms.txt"
else
    sed -i "s/\[项目名称\]/$PROJECT_NAME/g" "$TARGET_DIR/llms.txt"
fi

echo ""
echo "Done! Next steps:"
echo "  1. Edit llms.txt - fill in project description"
echo "  2. Add first task to TASK.md"
echo "  3. (Optional) qmd index . for search-based retrieval"
