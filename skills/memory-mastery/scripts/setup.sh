#!/usr/bin/env bash
# Memory Mastery - Setup Script
# Sets up the three-layer memory system in an OpenClaw workspace.
# Usage: bash setup.sh [workspace_path]
# Non-destructive: backs up existing files before modifying.

set -euo pipefail

WORKSPACE="${1:-${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/../templates"
BACKUP_SUFFIX=".bak.$(date +%Y%m%d%H%M%S)"

log() { echo "✅ $*"; }
warn() { echo "⚠️  $*"; }
skip() { echo "⏭️  $*"; }

echo "🧠 Memory Mastery Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Workspace: $WORKSPACE"
echo ""

# --- Step 1: Create memory/ directory ---
if [ ! -d "$WORKSPACE/memory" ]; then
  mkdir -p "$WORKSPACE/memory"
  log "Created memory/ directory"
else
  skip "memory/ directory already exists"
fi

# --- Step 2: MEMORY.md ---
if [ ! -f "$WORKSPACE/MEMORY.md" ]; then
  if [ -f "$TEMPLATE_DIR/MEMORY.md.template" ]; then
    cp "$TEMPLATE_DIR/MEMORY.md.template" "$WORKSPACE/MEMORY.md"
    log "Created MEMORY.md from template"
  else
    cat > "$WORKSPACE/MEMORY.md" << 'MEMTEMPLATE'
# MEMORY.md - Long-Term Memory

## About Me
- **Created**: $(date +%Y-%m-%d)
- **Role**: (describe your role)

## About My Human
- **Name**: (your human's name)
- **Preferences**: (what they like)

## Key Decisions
(Record important decisions here)

## Lessons Learned
(What you've learned from mistakes)

## Important Context
(Durable facts, preferences, configurations)
MEMTEMPLATE
    log "Created MEMORY.md with default template"
  fi
else
  skip "MEMORY.md already exists ($(wc -l < "$WORKSPACE/MEMORY.md" | tr -d ' ') lines)"
fi

# --- Step 3: Create today's daily log ---
TODAY=$(date +%Y-%m-%d)
TODAY_LOG="$WORKSPACE/memory/$TODAY.md"
if [ ! -f "$TODAY_LOG" ]; then
  echo "# $TODAY" > "$TODAY_LOG"
  echo "" >> "$TODAY_LOG"
  echo "### Memory Mastery Setup" >> "$TODAY_LOG"
  echo "- Installed memory-mastery skill" >> "$TODAY_LOG"
  echo "- Three-layer memory system activated (L1: daily, L2: long-term, L3: vector search)" >> "$TODAY_LOG"
  log "Created today's daily log: memory/$TODAY.md"
else
  skip "Today's daily log already exists"
fi

# --- Step 4: Add memory rules to AGENTS.md ---
AGENTS_MD="$WORKSPACE/AGENTS.md"
if [ -f "$AGENTS_MD" ]; then
  if grep -q "Memory Mastery" "$AGENTS_MD" 2>/dev/null; then
    skip "AGENTS.md already has Memory Mastery rules"
  else
    cp "$AGENTS_MD" "${AGENTS_MD}${BACKUP_SUFFIX}"
    warn "Backed up AGENTS.md → AGENTS.md${BACKUP_SUFFIX}"
    
    if [ -f "$TEMPLATE_DIR/memory-rules.md" ]; then
      echo "" >> "$AGENTS_MD"
      cat "$TEMPLATE_DIR/memory-rules.md" >> "$AGENTS_MD"
    else
      cat >> "$AGENTS_MD" << 'RULESBLOCK'

## 🧠 Memory System (Memory Mastery)

### Three-Layer Architecture
| Layer | Location | Purpose |
|-------|----------|---------|
| L1 | `memory/YYYY-MM-DD.md` | Daily log (append-only) |
| L2 | `MEMORY.md` | Long-term curated memory |
| L3 | `memory_search` | Vector search (memory-core) |

### Writing Rules
1. **On task completion** → Write to L1
2. **Important decisions** → Write to L1 AND L2
3. **When searching** → Use `memory_search` tool
4. **Weekly** → Review L1 files, distill into L2
5. **"Remember this"** → Write to file immediately (no mental notes!)
6. **MEMORY.md** → Only load in main/private sessions (security)
7. **Mistakes** → Record them so you don't repeat them
RULESBLOCK
    fi
    log "Added memory rules to AGENTS.md"
  fi
else
  warn "AGENTS.md not found — creating with memory rules"
  if [ -f "$TEMPLATE_DIR/memory-rules.md" ]; then
    cp "$TEMPLATE_DIR/memory-rules.md" "$AGENTS_MD"
  fi
  log "Created AGENTS.md with memory rules"
fi

# --- Step 5: Add maintenance task to HEARTBEAT.md ---
HEARTBEAT_MD="$WORKSPACE/HEARTBEAT.md"
if [ -f "$HEARTBEAT_MD" ]; then
  if grep -q "Memory Mastery\|memory maintenance\|L1.*L2" "$HEARTBEAT_MD" 2>/dev/null; then
    skip "HEARTBEAT.md already has memory maintenance task"
  else
    cp "$HEARTBEAT_MD" "${HEARTBEAT_MD}${BACKUP_SUFFIX}"
    warn "Backed up HEARTBEAT.md → HEARTBEAT.md${BACKUP_SUFFIX}"
    
    if [ -f "$TEMPLATE_DIR/heartbeat-memory.md" ]; then
      echo "" >> "$HEARTBEAT_MD"
      cat "$TEMPLATE_DIR/heartbeat-memory.md" >> "$HEARTBEAT_MD"
    else
      cat >> "$HEARTBEAT_MD" << 'HBBLOCK'

## 🧠 Memory Maintenance (Memory Mastery)
# Every few days, review recent daily logs and update MEMORY.md:
# 1. Read memory/YYYY-MM-DD.md files from the past week
# 2. Identify significant decisions, lessons, or insights
# 3. Update MEMORY.md with distilled learnings
# 4. Remove outdated info from MEMORY.md
HBBLOCK
    fi
    log "Added memory maintenance to HEARTBEAT.md"
  fi
else
  if [ -f "$TEMPLATE_DIR/heartbeat-memory.md" ]; then
    cp "$TEMPLATE_DIR/heartbeat-memory.md" "$HEARTBEAT_MD"
  else
    cat > "$HEARTBEAT_MD" << 'HBNEW'
# HEARTBEAT.md

## 🧠 Memory Maintenance (Memory Mastery)
# Every few days, review recent daily logs and update MEMORY.md:
# 1. Read memory/YYYY-MM-DD.md files from the past week
# 2. Identify significant decisions, lessons, or insights
# 3. Update MEMORY.md with distilled learnings
# 4. Remove outdated info from MEMORY.md
HBNEW
  fi
  log "Created HEARTBEAT.md with memory maintenance task"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Memory Mastery setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit MEMORY.md with your agent's identity and context"
echo "  2. Start writing daily logs to memory/YYYY-MM-DD.md"
echo "  3. (Optional) Configure memory-core plugin for L3 vector search"
echo "  4. Review AGENTS.md to customize memory rules"
