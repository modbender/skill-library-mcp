#!/bin/bash
# ContextKeeper Checkpoint Script v0.1.1
# Auto-detects project from git, creates structured checkpoint

set -e

CKPT_DIR="$HOME/.memory/contextkeeper"
CHECKPOINTS_DIR="$CKPT_DIR/checkpoints"
PROJECTS_DIR="$CKPT_DIR/projects"

# Ensure directories exist
mkdir -p "$CHECKPOINTS_DIR" "$PROJECTS_DIR"

# JSON escape function - handles all JSON special characters
json_escape() {
    local str="$1"
    # Escape backslashes first (order matters)
    str="${str//\\/\\\\}"           # \
    str="${str//\"/\\\"}"           # \"
    str="${str//$'\t'/\\t}"          # tab
    str="${str//$'\b'/\\b}"          # backspace
    str="${str//$'\f'/\\f}"          # formfeed
    # Replace newlines/carriage returns with spaces (JSON doesn't allow raw newlines in strings)
    str="${str//$'\n'/ }"
    str="${str//$'\r'/ }"
    printf '%s' "$str"
}

# Auto-detect project from git
auto_detect_project() {
    local git_dir=""
    local project_id="P000"
    local project_name="unknown"
    
    # Find git root
    if git rev-parse --git-dir > /dev/null 2>&1; then
        git_dir=$(git rev-parse --show-toplevel 2>/dev/null)
        project_name=$(basename "$git_dir")
        
        # Map common repos to project IDs
        case "$project_name" in
            spirit) project_id="P003";project_name="SPIRIT" ;;
            botcall) project_id="P002";project_name="BotCall" ;;
            clawhub) project_id="P004";project_name="ClawHub" ;;
            *) project_id="P001";project_name="Workspace" ;;
        esac
        
        echo "$project_id|$project_name|$git_dir"
    else
        echo "P000|unknown|none"
    fi
}

# Get recent git activity
git_activity() {
    local project_dir="$1"
    cd "$project_dir" 2>/dev/null || return
    
    local recent_files=$(git diff --name-only HEAD 2>/dev/null | head -10 | tr '\n' ', ' | sed 's/,$//')
    local recent_commits=$(git log --oneline -3 2>/dev/null | head -1)
    local branch=$(git branch --show-current 2>/dev/null)
    
    echo "files:$recent_files|commits:$recent_commits|branch:$branch"
}

# Parse arguments
MESSAGE="${1:-Auto checkpoint}"
PROJECT_OVERRIDE="${2:-}"

# Auto-detect or use override
if [ -n "$PROJECT_OVERRIDE" ]; then
    PROJECT_ID="$PROJECT_OVERRIDE"
    PROJECT_NAME="Manual"
    GIT_DIR="$PWD"
else
    DETECTED=$(auto_detect_project)
    PROJECT_ID=$(echo "$DETECTED" | cut -d'|' -f1)
    PROJECT_NAME=$(echo "$DETECTED" | cut -d'|' -f2)
    GIT_DIR=$(echo "$DETECTED" | cut -d'|' -f3)
fi

# Skip if not in a project
if [ "$PROJECT_ID" = "P000" ]; then
    echo "⚠️  No git project detected. Run from within a git repository."
    echo "   Or specify project: ckpt.sh 'message' P002"
    exit 1
fi

TIMESTAMP=$(date '+%Y-%m-%d-%H%M%S')
ISO_TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

# Get git activity if available
if [ "$GIT_DIR" != "none" ]; then
    ACTIVITY=$(git_activity "$GIT_DIR")
    RECENT_FILES=$(echo "$ACTIVITY" | grep -o 'files:[^|]*' | sed 's/files://')
    RECENT_COMMITS=$(echo "$ACTIVITY" | grep -o 'commits:[^|]*' | sed 's/commits://')
    BRANCH=$(echo "$ACTIVITY" | grep -o 'branch:[^|]*' | sed 's/branch://')
else
    RECENT_FILES=""
    RECENT_COMMITS=""
    BRANCH=""
fi

# Build checkpoint JSON
# Handle empty files_touched array properly
if [ -z "$RECENT_FILES" ]; then
  FILES_JSON=""
else
  FILES_JSON=$(echo "$RECENT_FILES" | awk '{gsub(/, */, "\",\""); print "\"" $0 "\""}')
fi

# Escape values for JSON
SAFE_MESSAGE=$(json_escape "$MESSAGE")
SAFE_PROJECT_NAME=$(json_escape "$PROJECT_NAME")
SAFE_BRANCH=$(json_escape "$BRANCH")
SAFE_RECENT_COMMITS=$(json_escape "$RECENT_COMMITS")

cat > "$CHECKPOINTS_DIR/$TIMESTAMP.json" << JSON
{
  "id": "$TIMESTAMP",
  "timestamp": "$ISO_TIMESTAMP",
  "project_id": "$PROJECT_ID",
  "project_name": "$SAFE_PROJECT_NAME",
  "session_type": "active_development",
  "summary": "$SAFE_MESSAGE",
  "git_branch": "$SAFE_BRANCH",
  "recent_commits": "$SAFE_RECENT_COMMITS",
  "files_touched": [$FILES_JSON],
  "urls": [],
  "commands": [],
  "next_steps": [],
  "auto_detected": true
}
JSON

# Create/update project state
mkdir -p "$PROJECTS_DIR/$PROJECT_ID"
cat > "$PROJECTS_DIR/$PROJECT_ID/latest.json" << JSON
{
  "project_id": "$PROJECT_ID",
  "project_name": "$PROJECT_NAME",
  "last_checkpoint": "$TIMESTAMP",
  "git_dir": "$GIT_DIR",
  "status": "active"
}
JSON

# Update current-state symlink
ln -sf "$CHECKPOINTS_DIR/$TIMESTAMP.json" "$CKPT_DIR/current-state.json" 2>/dev/null || true

echo "🔮 ContextKeeper Checkpoint"
echo "=========================="
echo "✅ Created: $TIMESTAMP"
echo "📁 Project: $PROJECT_NAME ($PROJECT_ID)"
echo "💬 Summary: $MESSAGE"
echo "📂 Files: ${RECENT_FILES:-none}"
echo "🌿 Branch: ${BRANCH:-none}"
echo "📍 Location: $CHECKPOINTS_DIR/$TIMESTAMP.json"
