#!/usr/bin/env bash
# Persistent Memory — One-command setup
# Creates venv, installs deps, initializes vector DB and knowledge graph.
set -e

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$(cd "$SKILL_DIR/../.." && pwd)}"
MEMORY_DIR="$WORKSPACE/vector_memory"

echo "🧠 Persistent Memory Setup"
echo "   Workspace: $WORKSPACE"
echo "   Memory dir: $MEMORY_DIR"
echo ""

# Create memory directory
mkdir -p "$MEMORY_DIR"

# Copy scripts
for f in indexer.py search.py graph.py auto_retrieve.py; do
    if [ -f "$SKILL_DIR/scripts/$f" ]; then
        cp "$SKILL_DIR/scripts/$f" "$MEMORY_DIR/$f"
        echo "   ✅ Copied $f"
    fi
done

# Create venv if needed
if [ ! -d "$MEMORY_DIR/venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$MEMORY_DIR/venv"
fi

echo "📦 Installing dependencies..."
"$MEMORY_DIR/venv/bin/pip" install -q --upgrade pip
"$MEMORY_DIR/venv/bin/pip" install -q \
    sentence-transformers==3.3.1 \
    chromadb==0.6.3 \
    networkx==3.4.2

# Create .gitignore
cat > "$MEMORY_DIR/.gitignore" << 'EOF'
chroma_db/
venv/
__pycache__/
*.pyc
EOF

# Create memory/ directory for daily logs
mkdir -p "$WORKSPACE/memory"

# Run initial index if MEMORY.md exists
if [ -f "$WORKSPACE/MEMORY.md" ]; then
    echo "🔢 Running initial index..."
    "$MEMORY_DIR/venv/bin/python" "$MEMORY_DIR/indexer.py"
else
    echo "⚠️  No MEMORY.md found. Create one and run: vector_memory/venv/bin/python vector_memory/indexer.py"
fi

echo ""
echo "✅ Persistent Memory 3-layer system installed!"
echo ""
echo "🔧 CRITICAL NEXT STEP: Configure OpenClaw integration"
echo "   This ensures OpenClaw automatically searches your directive files (SOUL.md, AGENTS.md, etc.)"
echo ""
echo "   Run: python skills/persistent-memory/scripts/configure_openclaw.py"
echo ""
echo "Usage:"
echo "  Index:  vector_memory/venv/bin/python vector_memory/indexer.py"
echo "  Search: vector_memory/venv/bin/python vector_memory/search.py \"your query\""
echo "  Status: vector_memory/venv/bin/python vector_memory/auto_retrieve.py --status"
echo ""
echo "⚠️  Without OpenClaw configuration, agents may ignore workspace directives!"
