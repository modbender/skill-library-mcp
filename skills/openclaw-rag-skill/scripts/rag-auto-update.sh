#!/bin/bash
# RAG Automatic Ingestion - Daily update of knowledge base
# This script checks for new content and intelligently updates the RAG system

set -e

# Use dynamic paths for portability
HOME="${HOME:-$(cd ~ && pwd)}"
OPENCLAW_DIR="${OPENCLAW_DIR:-$HOME/.openclaw}"
WORKSPACE_DIR="${OPENCLAW_DIR}/workspace"

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAG_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
STATE_FILE="$WORKSPACE_DIR/memory/rag-auto-state.json"
LOG_FILE="$WORKSPACE_DIR/memory/rag-auto-update.log"

# Timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE=$(date +%Y-%m-%d)

# Create memory directory
mkdir -p "$(dirname "$STATE_FILE")"

# Initialize state if needed
if [ ! -f "$STATE_FILE" ]; then
    cat > "$STATE_FILE" << EOF
{
  "lastSessionIndex": 0,
  "lastWorkspaceIndex": 0,
  "lastSkillsIndex": 0,
  "updatedAt": "$TIMESTAMP"
}
EOF
fi

# log function
log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

# Get latest session file modification time
latest_session_time() {
    find "$OPENCLAW_DIR/agents/main/sessions" -name "*.jsonl" -type f -printf '%T@\n' 2>/dev/null | sort -rn | head -1 | cut -d. -f1 || echo "0"
}

log "=== RAG Auto-Update Started ==="

# Get current stats
SESSION_COUNT=$(find "$OPENCLAW_DIR/agents/main/sessions" -name "*.jsonl" 2>/dev/null | wc -l)
WORKSPACE_COUNT=$(find "$WORKSPACE_DIR" -type f \( -name "*.py" -o -name "*.js" -o -name "*.md" -o -name "*.json" \) 2>/dev/null | wc -l)
LATEST_SESSION=$(latest_session_time)

# Read last indexed timestamp
LAST_SESSION_INDEX=$(python3 -c "import json; print(json.load(open('$STATE_FILE')).get('lastSessionIndex', 0))" 2>/dev/null || echo "0")

log "Current status:"
log "  Sessions: $SESSION_COUNT files"
log "  Workspace: $WORKSPACE_COUNT searchable files"
log "  Latest session: $LATEST_SESSION"
log "  Last indexed: $LAST_SESSION_INDEX"

# Update sessions if new ones exist
if [ "$LATEST_SESSION" -gt "$LAST_SESSION_INDEX" ]; then
    log "✓ New/updated sessions detected, re-indexing..."

    cd "$RAG_DIR"
    python3 ingest_sessions.py --sessions-dir "$OPENCLAW_DIR/agents/main/sessions" >> "$LOG_FILE" 2>&1

    if [ $? -eq 0 ]; then
        log "✅ Sessions re-indexed successfully"
    else
        log "❌ Session indexing failed (see log)"
        exit 1
    fi
else
    log "✓ Sessions up to date (no new files)"
fi

# Update workspace (always do it - captures code changes)
log "Re-indexing workspace files..."
cd "$RAG_DIR"
python3 ingest_docs.py workspace >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    log "✅ Workspace re-indexed successfully"
else
    log "❌ Workspace indexing failed (see log)"
    exit 1
fi

# Update skills
log "Re-indexing skills..."
cd "$RAG_DIR"
python3 ingest_docs.py skills >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    log "✅ Skills re-indexed successfully"
else
    log "❌ Skills indexing failed (see log)"
    exit 1
fi

# Get document count
DOC_COUNT=$(cd "$RAG_DIR" && python3 -c "
import sys
sys.path.insert(0, '.')
from rag_system import RAGSystem
rag = RAGSystem()
print(rag.collection.count())
" 2>/dev/null || echo "unknown")

# Update state
python3 << EOF
import json

state = {
    "lastSessionIndex": $LATEST_SESSION,
    "lastWorkspaceIndex": $(date +%s),
    "lastSkillsIndex": $(date +%s),
    "updatedAt": "$TIMESTAMP",
    "totalDocuments": $DOC_COUNT,
    "sessionCount": $SESSION_COUNT
}

with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
EOF

log "=== RAG Auto-Update Complete ==="
log "Total documents in knowledge base: $DOC_COUNT"
log "Next run: $(date -u -d '+24 hours' +%Y-%m-%dT%H:%M:%SZ)"

exit 0