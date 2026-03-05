#!/bin/bash
# 4To1 Planner — Status Check
# Reads config and tests backend connectivity

CONFIG="$HOME/.config/4to1/config"

if [ ! -f "$CONFIG" ]; then
  echo "❌ Not configured. Run: bash {baseDir}/scripts/setup.sh"
  exit 1
fi

source "$CONFIG"

echo "🎯 4To1 Planner Status"
echo "======================"
echo "Backend: $BACKEND"

case $BACKEND in
  notion)
    echo "Testing Notion connection..."
    RESULT=$(curl -s -o /dev/null -w "%{http_code}" \
      "https://api.notion.com/v1/users/me" \
      -H "Authorization: Bearer $NOTION_API_KEY" \
      -H "Notion-Version: 2025-09-03")
    if [ "$RESULT" = "200" ]; then
      echo "✅ Notion API: Connected"
      echo "Parent page: $NOTION_PARENT_PAGE"
      # Search for planning databases
      SEARCH=$(curl -s -X POST "https://api.notion.com/v1/search" \
        -H "Authorization: Bearer $NOTION_KEY" \
        -H "Notion-Version: 2025-09-03" \
        -H "Content-Type: application/json" \
        -d '{"query": "4To1", "filter": {"value": "database", "property": "object"}}')
      DB_COUNT=$(echo "$SEARCH" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('results',[])))" 2>/dev/null || echo "?")
      echo "Planning databases found: $DB_COUNT"
    else
      echo "❌ Notion API: Error (HTTP $RESULT)"
      echo "Check your API key in $CONFIG"
    fi
    ;;
  todoist)
    echo "Testing Todoist connection..."
    RESULT=$(curl -s -o /dev/null -w "%{http_code}" \
      "https://api.todoist.com/rest/v2/projects" \
      -H "Authorization: Bearer $TODOIST_API_KEY")
    if [ "$RESULT" = "200" ]; then
      echo "✅ Todoist API: Connected"
      PROJECTS=$(curl -s "https://api.todoist.com/rest/v2/projects" \
        -H "Authorization: Bearer $TODOIST_API_KEY" | \
        python3 -c "import sys,json; ps=json.load(sys.stdin); [print(f'  - {p[\"name\"]}') for p in ps if '4' in p['name'] or 'Vision' in p['name'] or 'Sprint' in p['name'] or 'Not-To-Do' in p['name']]" 2>/dev/null)
      if [ -n "$PROJECTS" ]; then
        echo "Planning projects:"
        echo "$PROJECTS"
      else
        echo "No 4To1 projects found yet. Say 'Set up my 4to1 planning system' to create them."
      fi
    else
      echo "❌ Todoist API: Error (HTTP $RESULT)"
    fi
    ;;
  local)
    echo "Local directory: $LOCAL_DIR"
    if [ -d "$LOCAL_DIR" ]; then
      echo "✅ Directory exists"
      echo "Files:"
      find "$LOCAL_DIR" -name "*.md" -type f | head -20 | while read f; do
        echo "  - ${f#$LOCAL_DIR/}"
      done
    else
      echo "❌ Directory not found. Run setup again."
    fi
    ;;
  *)
    echo "⚠️ Unknown backend: $BACKEND"
    ;;
esac
