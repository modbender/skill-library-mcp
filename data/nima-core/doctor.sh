#!/bin/bash
# NIMA Doctor — Diagnose installation issues
# Usage: ./doctor.sh
#
# Run this if NIMA isn't working. It checks everything and tells you
# exactly what's wrong and how to fix it.

echo "🩺 NIMA Doctor — Checking your installation..."
echo "================================================"
echo ""

NIMA_HOME="${NIMA_HOME:-$HOME/.nima}"
EXTENSIONS_DIR="$HOME/.openclaw/extensions"
ISSUES=0

# ── Python ───────────────────────────────────────────────────────────────────
echo "🐍 Python"
if command -v python3 &> /dev/null; then
    PY_VERSION=$(python3 --version 2>&1)
    echo "   ✅ $PY_VERSION"
else
    echo "   ❌ Python 3 not found"
    echo "   FIX: Install Python 3.9+ (brew install python3 / apt install python3)"
    ISSUES=$((ISSUES + 1))
fi

# Check numpy/pandas
python3 -c "import numpy" 2>/dev/null && echo "   ✅ numpy" || { echo "   ❌ numpy missing (pip install numpy)"; ISSUES=$((ISSUES + 1)); }
python3 -c "import pandas" 2>/dev/null && echo "   ✅ pandas" || { echo "   ❌ pandas missing (pip install pandas)"; ISSUES=$((ISSUES + 1)); }

# Check real_ladybug (optional)
python3 -c "import real_ladybug; print(f'   ✅ real_ladybug {real_ladybug.version}')" 2>/dev/null || echo "   ℹ️  real_ladybug not installed (optional — needed for LadybugDB)"

echo ""

# ── Node.js ──────────────────────────────────────────────────────────────────
echo "📦 Node.js"
if command -v node &> /dev/null; then
    echo "   ✅ Node $(node -v)"
else
    echo "   ❌ Node.js not found"
    echo "   FIX: Install Node.js 18+ (brew install node / nvm install 22)"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# ── Data Directory ───────────────────────────────────────────────────────────
echo "📂 Data Directory ($NIMA_HOME)"
if [ -d "$NIMA_HOME" ]; then
    echo "   ✅ Exists"
else
    echo "   ❌ Missing"
    echo "   FIX: mkdir -p $NIMA_HOME/memory $NIMA_HOME/affect $NIMA_HOME/logs"
    ISSUES=$((ISSUES + 1))
fi

if [ -d "$NIMA_HOME/memory" ]; then
    echo "   ✅ memory/ exists"
else
    echo "   ❌ memory/ missing"
    echo "   FIX: mkdir -p $NIMA_HOME/memory"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# ── Databases ────────────────────────────────────────────────────────────────
echo "🗄️  Databases"

SQLITE_DB="$NIMA_HOME/memory/graph.sqlite"
if [ -f "$SQLITE_DB" ]; then
    SIZE=$(du -h "$SQLITE_DB" | cut -f1)
    echo "   ✅ SQLite: $SQLITE_DB ($SIZE)"
    
    # Check tables
    TABLES=$(python3 -c "
import sqlite3
conn = sqlite3.connect('$SQLITE_DB')
tables = [r[0] for r in conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()]
print(' '.join(tables))
conn.close()
" 2>/dev/null)
    
    REQUIRED_TABLES="memory_nodes memory_edges memory_turns"
    DREAM_TABLES="nima_insights nima_patterns nima_dream_runs nima_suppressed_memories nima_pruner_runs nima_lucid_moments"
    
    for t in $REQUIRED_TABLES; do
        if echo "$TABLES" | grep -q "$t"; then
            echo "   ✅ Table: $t"
        else
            echo "   ❌ Table: $t MISSING"
            echo "      FIX: python3 scripts/init_db.py --verbose"
            ISSUES=$((ISSUES + 1))
        fi
    done
    
    MISSING_DREAM=0
    for t in $DREAM_TABLES; do
        if ! echo "$TABLES" | grep -q "$t"; then
            MISSING_DREAM=$((MISSING_DREAM + 1))
        fi
    done
    if [ $MISSING_DREAM -gt 0 ]; then
        echo "   ⚠️  $MISSING_DREAM dream tables missing (v3.1.0 feature)"
        echo "      FIX: python3 scripts/init_db.py --verbose"
    else
        echo "   ✅ All 6 dream tables present"
    fi
    
    # Check FTS
    if echo "$TABLES" | grep -q "memory_fts"; then
        echo "   ✅ Full-text search (FTS5) enabled"
    else
        echo "   ⚠️  FTS5 missing — text search won't work"
        echo "      FIX: python3 scripts/init_db.py --verbose"
    fi
    
    # Row counts
    python3 -c "
import sqlite3
conn = sqlite3.connect('$SQLITE_DB')
try:
    nodes = conn.execute('SELECT count(*) FROM memory_nodes').fetchone()[0]
    embedded = conn.execute('SELECT count(*) FROM memory_nodes WHERE embedding IS NOT NULL').fetchone()[0]
    print(f'   📊 {nodes} memories, {embedded} with embeddings ({100*embedded//max(nodes,1)}%)')
except:
    pass
conn.close()
" 2>/dev/null

else
    echo "   ⚠️  SQLite not found at $SQLITE_DB"
    echo "      FIX: python3 scripts/init_db.py --verbose"
fi

LADYBUG_DB="$NIMA_HOME/memory/ladybug.lbug"
if [ -f "$LADYBUG_DB" ]; then
    SIZE=$(du -h "$LADYBUG_DB" | cut -f1)
    echo "   ✅ LadybugDB: $LADYBUG_DB ($SIZE)"
    
    # Test LOAD VECTOR
    python3 -c "
import real_ladybug as lb
db = lb.Database('$LADYBUG_DB')
conn = lb.Connection(db)
try:
    conn.execute('LOAD VECTOR')
    print('   ✅ LOAD VECTOR: works (mutations safe)')
except Exception as e:
    print(f'   ⚠️  LOAD VECTOR failed: {e}')
    print('      This means SET/CREATE/DELETE will SIGSEGV!')
nodes = list(conn.execute('MATCH (n:MemoryNode) RETURN count(n)'))[0][0]
ghosts = list(conn.execute('MATCH (n:MemoryNode) WHERE n.is_ghost = true RETURN count(n)'))[0][0]
print(f'   📊 {nodes} nodes, {ghosts} ghosted')
" 2>/dev/null || echo "   ⚠️  Could not connect to LadybugDB"
else
    echo "   ℹ️  LadybugDB not installed (optional)"
fi
echo ""

# ── Hooks ────────────────────────────────────────────────────────────────────
echo "🔌 Hooks ($EXTENSIONS_DIR)"

for hook in nima-memory nima-recall-live nima-affect; do
    HOOK_DIR="$EXTENSIONS_DIR/$hook"
    if [ -d "$HOOK_DIR" ]; then
        # Check for required files
        case $hook in
            nima-memory)
                REQUIRED="index.js openclaw.plugin.json ladybug_store.py"
                ;;
            nima-recall-live)
                REQUIRED="index.js openclaw.plugin.json lazy_recall.py"
                ;;
            nima-affect)
                REQUIRED="index.js openclaw.plugin.json vader-affect.js"
                ;;
        esac
        
        ALL_PRESENT=true
        MISSING=""
        for f in $REQUIRED; do
            if [ ! -f "$HOOK_DIR/$f" ]; then
                ALL_PRESENT=false
                MISSING="$MISSING $f"
            fi
        done
        
        if $ALL_PRESENT; then
            echo "   ✅ $hook — all files present"
        else
            echo "   ⚠️  $hook — missing:$MISSING"
            echo "      FIX: cp -r openclaw_hooks/$hook $EXTENSIONS_DIR/"
            ISSUES=$((ISSUES + 1))
        fi
    else
        echo "   ❌ $hook — not installed"
        echo "      FIX: cp -r openclaw_hooks/$hook $EXTENSIONS_DIR/"
        ISSUES=$((ISSUES + 1))
    fi
done
echo ""

# ── OpenClaw Config ──────────────────────────────────────────────────────────
echo "⚙️  OpenClaw Config"

CONFIG="$HOME/.openclaw/openclaw.json"
if [ -f "$CONFIG" ]; then
    HOOK_ISSUES=$(python3 -c "
import json
count = 0
with open('$CONFIG') as f:
    cfg = json.load(f)
plugins = cfg.get('plugins', {}).get('entries', {})
hooks = ['nima-memory', 'nima-recall-live', 'nima-affect']
for h in hooks:
    if h in plugins:
        enabled = plugins[h].get('enabled', True)
        status = '✅' if enabled else '⚠️  disabled'
        print(f'   {status} {h} in config')
        if not enabled:
            count += 1
    else:
        print(f'   ❌ {h} NOT in config')
        print(f'      FIX: Add to plugins.entries in openclaw.json')
        count += 1
print(f'HOOK_ISSUE_COUNT={count}')
" 2>/dev/null || echo "   ⚠️  Could not parse config")
    HOOK_COUNT=$(echo "$HOOK_ISSUES" | grep -o 'HOOK_ISSUE_COUNT=[0-9]*' | cut -d= -f2)
    echo "$HOOK_ISSUES" | grep -v 'HOOK_ISSUE_COUNT='
    if [ -n "$HOOK_COUNT" ] && [ "$HOOK_COUNT" -gt 0 ] 2>/dev/null; then
        ISSUES=$((ISSUES + HOOK_COUNT))
    fi
else
    echo "   ❌ Config not found at $CONFIG"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# ── Embedding Provider ───────────────────────────────────────────────────────
echo "🔤 Embeddings"
EMBEDDER="${NIMA_EMBEDDER:-local}"
echo "   Provider: $EMBEDDER"

case $EMBEDDER in
    voyage)
        if [ -n "$VOYAGE_API_KEY" ]; then
            echo "   ✅ VOYAGE_API_KEY is set"
        else
            echo "   ❌ VOYAGE_API_KEY not set"
            echo "      FIX: export VOYAGE_API_KEY=pa-xxx"
            ISSUES=$((ISSUES + 1))
        fi
        ;;
    openai)
        if [ -n "$OPENAI_API_KEY" ]; then
            echo "   ✅ OPENAI_API_KEY is set"
        else
            echo "   ❌ OPENAI_API_KEY not set"
            ISSUES=$((ISSUES + 1))
        fi
        ;;
    local)
        echo "   ✅ Using local embeddings (no API key needed)"
        ;;
    ollama)
        echo "   ✅ Using Ollama (${NIMA_OLLAMA_MODEL:-nomic-embed-text})"
        ;;
esac
echo ""

# ── Summary ──────────────────────────────────────────────────────────────────
echo "════════════════════════════════════════════════"
if [ $ISSUES -eq 0 ]; then
    echo "✅ All checks passed! NIMA is healthy."
else
    echo "⚠️  Found $ISSUES issue(s). See FIX instructions above."
fi
echo ""
echo "Need help? https://github.com/lilubot/nima-core/issues"
