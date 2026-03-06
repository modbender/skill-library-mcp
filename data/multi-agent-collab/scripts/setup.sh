#!/bin/bash

# OpenClaw Multi-Agent Collaboration System (MACS) Initializer
# Version: 1.0.0

echo "🦞 Initializing Multi-Agent Collaboration System (MACS)..."

# 1. Create directory structure
mkdir -p archive docs memory

# 2. Copy templates to root if they don't exist
TEMPLATES_DIR="./templates"

files=("PROJECT-README.md" "TASK.md" "CHANGELOG.md" "CONTEXT.md" "llms.txt")

for file in "${files[@]}"; do
    if [ ! -f "../$file" ]; then
        cp "$TEMPLATES_DIR/$file" "../$file"
        echo "✅ Created $file"
    else
        echo "⚠️  $file already exists, skipping."
    fi
done

# 3. Create project-specific Best Practices and Model Router docs
cp ./docs/BEST-PRACTICES.md ../docs/BEST-PRACTICES.md
cp ./docs/MODEL-ROUTER.md ../docs/MODEL-ROUTER.md

echo ""
echo "🎉 MACS Initialization Complete!"
echo "------------------------------------------------"
echo "Next Steps:"
echo "1. Edit PROJECT-README.md to define your project."
echo "2. Add your first task to TASK.md."
echo "3. Let your agents know about the new workflow."
echo "------------------------------------------------"
echo "Happy collaborating! 🦞"
