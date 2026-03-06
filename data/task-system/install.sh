#!/bin/bash
# Task System Skill Installation Script
# Adds task-system.sh to PATH

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Add to PATH via bashrc.d (preferred) or .bashrc
if [ -d "$HOME/.bashrc.d" ]; then
    echo "Adding task-system to PATH via ~/.bashrc.d"
    echo 'export PATH="'$SCRIPT_DIR':$PATH"' > "$HOME/.bashrc.d/task-system.sh"
else
    echo "Adding task-system to PATH via ~/.bashrc"
    echo 'export PATH="'$SCRIPT_DIR':$PATH"' >> "$HOME/.bashrc"
fi

# Also create symlink in ~/.local/bin if exists
if [ -d "$HOME/.local/bin" ]; then
    ln -sf "$SCRIPT_DIR/task-system.sh" "$HOME/.local/bin/task-system"
    echo "Created symlink: ~/.local/bin/task-system"
fi

echo "✓ task-system installed!"
echo "  Usage: task-system.sh create 'Your task'"
echo "  Or:    task-system status"
echo ""
echo "Restart your terminal or run: source ~/.bashrc"
