#!/bin/bash
#
# NIMA Core Installation Script v3.1
# ================================
# Bulletproof installer for AI agents running on OpenClaw
#
# Usage:
#   ./install.sh                    # SQLite only (recommended)
#   ./install.sh --with-ladybug     # Include LadybugDB (optional upgrade)
#   ./install.sh --help             # Show all options
#
# What this does:
#   1. Checks prerequisites (Python 3.9+, Node.js 18+)
#   2. Creates data directories (~/.nima/)
#   3. Installs Python dependencies
#   4. Initializes SQLite database with ALL tables
#   5. Installs 3 OpenClaw hooks to ~/.openclaw/extensions/
#   6. Runs health check
#   7. Prints ready-to-paste openclaw.json config
#
# After running: openclaw gateway restart
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script location
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Defaults
INSTALL_LADYBUG=false
VERBOSE=false

# ============================================
# Helper Functions
# ============================================

step() {
    echo -e "\n${CYAN}▶${NC} $1"
}

success() {
    echo -e "${GREEN}✅${NC} $1"
}

warn() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

error() {
    echo -e "${RED}❌${NC} $1"
}

info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

die() {
    error "$1"
    echo ""
    echo "Recovery suggestions:"
    echo "  - Ensure Python 3.9+ and Node.js 18+ are installed"
    echo "  - Check you have write permissions to ~/.nima and ~/.openclaw"
    echo "  - Run with --verbose for detailed error output"
    exit 1
}

# ============================================
# Argument Parsing
# ============================================

for arg in "$@"; do
    case $arg in
        --with-ladybug)
            INSTALL_LADYBUG=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "NIMA Core Installer v3.1"
            echo ""
            echo "Usage: ./install.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --with-ladybug    Include LadybugDB backend (optional upgrade)"
            echo "  --verbose, -v     Show detailed output"
            echo "  --help, -h        Show this help"
            echo ""
            echo "Default: SQLite-only installation (simplest, recommended)"
            echo ""
            echo "After installation: openclaw gateway restart"
            exit 0
            ;;
        *)
            warn "Unknown argument: $arg"
            shift
            ;;
    esac
done

# ============================================
# Step 1: Banner & Prerequisites
# ============================================

echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}       🧠 NIMA Core Installer v3.1        ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}   Persistent Memory for AI Agents        ${CYAN}║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════╝${NC}"

step "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    die "Python 3 is required but not found"
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [[ "$PYTHON_MAJOR" -lt 3 ]] || [[ "$PYTHON_MAJOR" -eq 3 && "$PYTHON_MINOR" -lt 9 ]]; then
    die "Python 3.9+ required, found $PYTHON_VERSION"
fi
success "Python $PYTHON_VERSION"

# Check Node.js
if ! command -v node &> /dev/null; then
    die "Node.js 18+ is required but not found"
fi

NODE_VERSION=$(node -v 2>/dev/null | sed 's/v//' | cut -d. -f1)
if [[ "$NODE_VERSION" -lt 18 ]]; then
    die "Node.js 18+ required, found v$NODE_VERSION"
fi
success "Node.js v$(node -v 2>/dev/null | sed 's/v//')"

# Check pip
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    die "pip is required but not found"
fi
success "pip available"

# Detect virtual environment
if [[ -n "$VIRTUAL_ENV" ]]; then
    info "Using virtual environment: $VIRTUAL_ENV"
else
    info "No virtual environment detected (system Python)"
fi

# ============================================
# Step 2: Resolve Data Directory
# ============================================

step "Resolving data directory..."

NIMA_HOME="${NIMA_DATA_DIR:-$HOME/.nima}"
if [[ "$NIMA_HOME" == */memory ]]; then
    NIMA_HOME="${NIMA_HOME%/memory}"
fi

info "Data directory: $NIMA_HOME"

# ============================================
# Step 3: Create Directories
# ============================================

step "Creating directories..."

mkdir -p "$NIMA_HOME/memory" || die "Failed to create $NIMA_HOME/memory"
mkdir -p "$NIMA_HOME/affect" || die "Failed to create $NIMA_HOME/affect"
mkdir -p "$NIMA_HOME/logs" || die "Failed to create $NIMA_HOME/logs"
mkdir -p "$HOME/.openclaw/extensions" || die "Failed to create ~/.openclaw/extensions"

success "Directories created:"
echo "   $NIMA_HOME/memory/   (databases)"
echo "   $NIMA_HOME/affect/   (emotional state)"
echo "   $NIMA_HOME/logs/     (debug logs)"

# ============================================
# Step 4: Install Python Dependencies
# ============================================

step "Installing Python dependencies..."

# Core dependencies (always needed)
PIP_CMD="pip"
if ! command -v pip &> /dev/null; then
    PIP_CMD="pip3"
fi

$PIP_CMD install -q numpy pandas 2>/dev/null || {
    warn "Core install had issues, trying with --user..."
    $PIP_CMD install --user -q numpy pandas || die "Failed to install numpy/pandas"
}
success "Core: numpy, pandas"

# Optional: LadybugDB
if [ "$INSTALL_LADYBUG" = true ]; then
    info "Installing LadybugDB (optional backend)..."
    $PIP_CMD install -q real-ladybug 2>/dev/null && {
        success "LadybugDB installed"
    } || {
        warn "LadybugDB install failed — SQLite will be used instead"
    }
fi

# Optional: Local embeddings (sentence-transformers)
# Note: This is large (~500MB). Users can install manually if needed.
if [ "$VERBOSE" = true ]; then
    info "Local embeddings use sentence-transformers (install manually if needed):"
    echo "   pip install sentence-transformers"
fi

# ============================================
# Step 5: Initialize SQLite Database
# ============================================

step "Initializing SQLite database..."

DB_PATH="$NIMA_HOME/memory/graph.sqlite"

if [ -f "$DB_PATH" ]; then
    info "Database exists: $DB_PATH"
    info "Running init to ensure all tables exist..."
fi

NIMA_DATA_DIR="$NIMA_HOME" python3 "$SCRIPT_DIR/scripts/init_db.py" --verbose || {
    warn "Database init had issues, attempting manual creation..."
    # Fallback: create tables manually
    export NIMA_DATA_DIR="$NIMA_HOME"
    python3 << 'PYEOF'
import sqlite3
import os
from pathlib import Path

db_path = os.environ.get('NIMA_DATA_DIR', os.path.expanduser('~/.nima'))
db_path = Path(db_path) / 'memory' / 'graph.sqlite'
db_path.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(str(db_path))
conn.executescript("""
    CREATE TABLE IF NOT EXISTS memory_nodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp INTEGER NOT NULL,
        layer TEXT NOT NULL,
        text TEXT NOT NULL,
        summary TEXT NOT NULL,
        who TEXT DEFAULT '',
        affect_json TEXT DEFAULT '{}',
        session_key TEXT DEFAULT '',
        conversation_id TEXT DEFAULT '',
        turn_id TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now')),
        embedding BLOB DEFAULT NULL,
        fe_score REAL DEFAULT 0.5,
        strength REAL DEFAULT 1.0,
        decay_rate REAL DEFAULT 0.01,
        last_accessed INTEGER DEFAULT 0,
        is_ghost INTEGER DEFAULT 0,
        dismissal_count INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS memory_edges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id INTEGER NOT NULL,
        target_id INTEGER NOT NULL,
        relation TEXT NOT NULL,
        weight REAL DEFAULT 1.0,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (source_id) REFERENCES memory_nodes(id) ON DELETE CASCADE,
        FOREIGN KEY (target_id) REFERENCES memory_nodes(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS memory_turns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        turn_id TEXT UNIQUE NOT NULL,
        input_node_id INTEGER,
        contemplation_node_id INTEGER,
        output_node_id INTEGER,
        timestamp INTEGER NOT NULL,
        affect_json TEXT DEFAULT '{}',
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (input_node_id) REFERENCES memory_nodes(id) ON DELETE SET NULL,
        FOREIGN KEY (contemplation_node_id) REFERENCES memory_nodes(id) ON DELETE SET NULL,
        FOREIGN KEY (output_node_id) REFERENCES memory_nodes(id) ON DELETE SET NULL
    );
    CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
        text, summary, who, layer,
        content=memory_nodes,
        content_rowid=id
    );
""")
conn.commit()
conn.close()
print("✅ Database created manually")
PYEOF
}

# Verify database
TABLE_COUNT=$(python3 -c "
import sqlite3
conn = sqlite3.connect('$DB_PATH')
cursor = conn.execute(\"SELECT COUNT(*) FROM sqlite_master WHERE type='table'\")
print(cursor.fetchone()[0])
conn.close()
" 2>/dev/null || echo "0")

if [[ "$TABLE_COUNT" -ge 4 ]]; then
    success "Database ready: $TABLE_COUNT tables at $DB_PATH"
else
    warn "Database may be incomplete (found $TABLE_COUNT tables)"
fi

# ============================================
# Step 6: Install OpenClaw Hooks
# ============================================

step "Installing OpenClaw hooks..."

HOOKS_SRC="$SCRIPT_DIR/openclaw_hooks"
HOOKS_DEST="$HOME/.openclaw/extensions"

if [[ ! -d "$HOOKS_SRC" ]]; then
    die "Hooks source not found: $HOOKS_SRC"
fi

# Install nima-memory
if [[ -d "$HOOKS_SRC/nima-memory" ]]; then
    if cp -r "$HOOKS_SRC/nima-memory" "$HOOKS_DEST/"; then
        success "nima-memory → $HOOKS_DEST/nima-memory/"
    else
        warn "Failed to copy nima-memory"
    fi
else
    warn "nima-memory hook not found in source"
fi

# Install nima-recall-live
if [[ -d "$HOOKS_SRC/nima-recall-live" ]]; then
    if cp -r "$HOOKS_SRC/nima-recall-live" "$HOOKS_DEST/"; then
        success "nima-recall-live → $HOOKS_DEST/nima-recall-live/"
    else
        warn "Failed to copy nima-recall-live"
    fi
else
    warn "nima-recall-live hook not found in source"
fi

# Install nima-affect
if [[ -d "$HOOKS_SRC/nima-affect" ]]; then
    if cp -r "$HOOKS_SRC/nima-affect" "$HOOKS_DEST/"; then
        success "nima-affect → $HOOKS_DEST/nima-affect/"
    else
        warn "Failed to copy nima-affect"
    fi
else
    warn "nima-affect hook not found in source"
fi

# ============================================
# Step 7: Health Check
# ============================================

step "Running health check..."

HEALTH_OK=true

# Check Python import
python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
try:
    from nima_core import get_affect_system
    print('OK')
except ImportError as e:
    print(f'FAIL: {e}')
except Exception as e:
    print(f'WARN: {e}')
" 2>/dev/null || {
    warn "nima_core Python package not importable (advanced features may not work)"
    info "Core memory hooks will still function via SQLite"
}

# Check database is writable
if [[ -f "$DB_PATH" ]]; then
    python3 -c "
import sqlite3
conn = sqlite3.connect('$DB_PATH')
conn.execute('SELECT 1 FROM memory_nodes LIMIT 1')
conn.close()
" 2>/dev/null && success "Database is readable and writable" || warn "Database may be locked or corrupted"
fi

# Check hooks exist
for hook in nima-memory nima-recall-live nima-affect; do
    if [[ -d "$HOOKS_DEST/$hook" ]]; then
        if [[ -f "$HOOKS_DEST/$hook/openclaw.plugin.json" ]]; then
            :
        else
            warn "$hook missing openclaw.plugin.json"
            HEALTH_OK=false
        fi
    else
        warn "$hook not installed"
        HEALTH_OK=false
    fi
done

# ============================================
# Step 8: Print Configuration
# ============================================

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
if [[ "$HEALTH_OK" = true ]]; then
    echo -e "${GREEN}                    🎉 INSTALLATION COMPLETE               ${NC}"
else
    echo -e "${YELLOW}              ⚠️  INSTALLATION COMPLETE (WITH WARNINGS)     ${NC}"
fi
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"

echo ""
echo -e "${CYAN}📂 Data Location:${NC}"
echo "   $NIMA_HOME/"
echo "   ├── memory/graph.sqlite   (SQLite database)"
echo "   ├── affect/               (emotional state)"
echo "   └── logs/                 (debug logs)"
echo ""
echo -e "${CYAN}🔌 Hooks Installed:${NC}"
echo "   ~/.openclaw/extensions/nima-memory/       (captures memories)"
echo "   ~/.openclaw/extensions/nima-recall-live/  (injects context)"
echo "   ~/.openclaw/extensions/nima-affect/       (emotion tracking)"
echo ""

# Generate openclaw.json snippet
echo -e "${CYAN}📝 Add to ~/.openclaw/openclaw.json:${NC}"
echo ""
echo -e "${YELLOW}┌─────────────────────────────────────────────────────────────┐${NC}"
cat << 'JSONEOF'
  {
    "plugins": {
      "entries": {
        "nima-memory": {
          "enabled": true,
          "identity_name": "your_bot_name"
        },
        "nima-recall-live": {
          "enabled": true
        },
        "nima-affect": {
          "enabled": true,
          "identity_name": "your_bot_name",
          "baseline": "guardian"
        }
      }
    }
  }
JSONEOF
echo -e "${YELLOW}└─────────────────────────────────────────────────────────────┘${NC}"
echo ""
echo -e "${CYAN}🔄 Next Step:${NC}"
echo -e "   ${GREEN}openclaw gateway restart${NC}"
echo ""
echo -e "${CYAN}📚 Documentation:${NC}"
echo "   QUICKSTART.md — Minimal getting started"
echo "   INSTALL.md    — Full installation guide"
echo "   SKILL.md      — Complete feature reference"
echo ""

if [ "$INSTALL_LADYBUG" = true ]; then
    echo -e "${YELLOW}⚡ LadybugDB Mode:${NC}"
    echo "   You installed with --with-ladybug. To use it:"
    echo "   1. pip install real-ladybug (if not already installed)"
    echo "   2. Add to nima-memory config: \"database\": {\"backend\": \"ladybugdb\"}"
    echo ""
    echo -e "${RED}⚠️  IMPORTANT:${NC} LadybugDB requires LOAD VECTOR before writes."
    echo "   If you see SIGSEGV, ensure you've called LOAD VECTOR first."
    echo "   SQLite is the safer default for most users."
    echo ""
fi

echo -e "${GREEN}Done! Your bot now has persistent memory.${NC}"
