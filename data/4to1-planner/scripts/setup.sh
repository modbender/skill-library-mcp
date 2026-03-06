#!/bin/bash
# 4To1 Planner — Quick Setup
# Creates config directory and initializes chosen backend

set -e

CONFIG_DIR="$HOME/.config/4to1"
mkdir -p "$CONFIG_DIR"

echo "🎯 4To1 Planner Setup"
echo "====================="
echo ""
echo "Choose your planning backend:"
echo "  1) Notion (recommended — rich databases, visual dashboards)"
echo "  2) Todoist (task-focused, great mobile app)"
echo "  3) Google Calendar + Tasks (time-block planning)"
echo "  4) Local Markdown (no account needed, works offline)"
echo ""

read -p "Enter choice [1-4]: " choice

case $choice in
  1)
    echo "BACKEND=notion" > "$CONFIG_DIR/config"
    echo ""
    echo "📝 Notion Setup:"
    echo "1. Go to https://www.notion.so/my-integrations"
    echo "2. Click '+ New integration'"
    echo "3. Name it '4To1 Planner', select your workspace"
    echo "4. Copy the 'Internal Integration Secret' (starts with ntn_)"
    echo ""
    read -p "Paste your Notion API key: " notion_key
    echo "NOTION_API_KEY=$notion_key" >> "$CONFIG_DIR/config"
    echo ""
    echo "5. In Notion, create or open the page where you want your planning hub"
    echo "6. Click ··· → Connections → select '4To1 Planner'"
    echo "7. Copy the page ID from the URL (the 32-char hex string after the page name)"
    echo ""
    read -p "Paste the parent page ID: " parent_page
    echo "NOTION_PARENT_PAGE=$parent_page" >> "$CONFIG_DIR/config"
    echo ""
    echo "✅ Notion configured! Tell your AI: 'Set up my 4to1 planning system'"
    ;;
  2)
    echo "BACKEND=todoist" > "$CONFIG_DIR/config"
    echo ""
    echo "📋 Todoist Setup:"
    echo "1. Go to https://app.todoist.com/app/settings/integrations/developer"
    echo "2. Copy your API token"
    echo ""
    read -p "Paste your Todoist API token: " todoist_key
    echo "TODOIST_API_KEY=$todoist_key" >> "$CONFIG_DIR/config"
    echo ""
    echo "✅ Todoist configured! Tell your AI: 'Set up my 4to1 planning system'"
    ;;
  3)
    echo "BACKEND=gcal" > "$CONFIG_DIR/config"
    echo ""
    echo "📅 Google Calendar setup requires OAuth. Run:"
    echo "   python3 $(dirname $0)/gcal_setup.py"
    ;;
  4)
    LOCAL_DIR="$HOME/4to1-plans"
    echo "BACKEND=local" > "$CONFIG_DIR/config"
    echo "LOCAL_DIR=$LOCAL_DIR" >> "$CONFIG_DIR/config"
    mkdir -p "$LOCAL_DIR"/{vision,goals,sprints,weekly,projects,not-to-do}
    
    # Create initial files
    cat > "$LOCAL_DIR/vision.md" << 'EOF'
---
created: $(date +%Y-%m-%d)
last_reviewed: $(date +%Y-%m-%d)
---

# 🔭 4-Year Vision

> Where do I want to be in 4 years?

## Area 1: [Career/Business]
**Vision:** 
**Success looks like:**

## Area 2: [Health/Wellness]
**Vision:**
**Success looks like:**

## Area 3: [Skills/Growth]
**Vision:**
**Success looks like:**
EOF

    cat > "$LOCAL_DIR/not-to-do.md" << 'EOF'
# 🚫 Not-To-Do List

## Projects I'm Saying NO To
_Things that sound good but don't serve my 4-year vision_

1. 

## Time Wasters I'm Eliminating
_Daily habits that steal my time_

1. 
EOF

    echo ""
    echo "✅ Local backend created at $LOCAL_DIR"
    echo "Tell your AI: 'Set up my 4to1 planning system'"
    ;;
  *)
    echo "Invalid choice. Run again."
    exit 1
    ;;
esac

echo ""
echo "Config saved to $CONFIG_DIR/config"
echo ""
echo "🚀 Next: Start a conversation with your OpenClaw agent and say:"
echo "   'Help me set up my 4to1 planning system'"
