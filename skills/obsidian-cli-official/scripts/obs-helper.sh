#!/bin/bash
# Obsidian CLI Wrapper for AI Agents
# Usage: obs <action> [args...]

set -e

# Check if Obsidian is running
if ! pgrep -x "Obsidian" > /dev/null; then
    echo "Error: Obsidian is not running"
    exit 1
fi

# Ensure CLI is in PATH
export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"

ACTION="$1"
shift

case "$ACTION" in
    daily)
        # Create or open today's daily note
        obsidian daily
        ;;
    
    daily-add)
        # Add content to today's daily note
        CONTENT="$1"
        obsidian daily:append content="$CONTENT"
        ;;
    
    note-create)
        # Create a new note
        NAME="$1"
        CONTENT="$2"
        obsidian create name="$NAME" content="$CONTENT"
        ;;
    
    note-read)
        # Read a note
        FILE="$1"
        obsidian read file="$FILE"
        ;;
    
    search)
        # Search notes
        QUERY="$1"
        obsidian search query="$QUERY"
        ;;
    
    tasks)
        # List tasks
        obsidian tasks daily todo
        ;;
    
    task-toggle)
        # Toggle task completion
        LINE="$1"
        obsidian task daily line="$LINE" toggle
        ;;
    
    help)
        cat << 'EOF'
Obsidian CLI Wrapper for AI Agents

Usage: obs <action> [args...]

Actions:
  daily                    Open today's daily note
  daily-add "content"      Add content to today's daily note
  note-create "name" "content"  Create a new note
  note-read "name"         Read a note
  search "query"           Search notes
  tasks                    List incomplete tasks
  task-toggle <line>       Toggle task completion
  help                     Show this help

Examples:
  obs daily
  obs daily-add "## Meeting Notes\n- Discussed project timeline"
  obs note-create "Ideas" "# New Ideas\n\n- Idea 1"
  obs search "project"
  obs tasks
  obs task-toggle 3

Full documentation:
https://github.com/alexanderkinging/obsidian-official-cli
EOF
        ;;
    
    *)
        echo "Unknown action: $ACTION"
        echo "Run 'obs help' for usage"
        exit 1
        ;;
esac
