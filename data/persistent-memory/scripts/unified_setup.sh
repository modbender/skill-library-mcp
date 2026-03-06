#!/usr/bin/env bash
# Persistent Memory — One-command unified setup
# Creates memory system + configures OpenClaw integration automatically
set -e

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$(cd "$SKILL_DIR/../.." && pwd)}"
MEMORY_DIR="$WORKSPACE/vector_memory"

echo "🧠 Persistent Memory — Unified Setup"
echo "   Workspace: $WORKSPACE"
echo "   Memory dir: $MEMORY_DIR"
echo ""

# Step 1: Create memory system
echo "📁 Setting up 3-layer memory system..."
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

echo ""
echo "🔧 Configuring OpenClaw integration..."

# Step 2: Configure OpenClaw automatically
python3 -c "
import json
import os
import sys
import subprocess
from pathlib import Path

def find_openclaw_config():
    '''Find OpenClaw configuration file.'''
    possible_paths = [
        os.path.expanduser('~/.openclaw/openclaw.json'),
        os.path.expanduser('~/.openclaw/config.json'),
        './openclaw.json'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def get_memory_config():
    '''Memory search configuration for OpenClaw.'''
    return {
        'enabled': True,
        'sources': ['memory', 'sessions'],
        'extraPaths': [
            'SOUL.md', 'AGENTS.md', 'HEARTBEAT.md', 'PROJECTS.md',
            'TOOLS.md', 'IDENTITY.md', 'USER.md', 'reference/',
            'ARCHITECTURE.md'
        ],
        'experimental': {'sessionMemory': True},
        'chunking': {'maxChunkSize': 2048, 'overlap': 200},
        'provider': 'local',
        'sync': {'onSessionStart': True, 'onSearch': True, 'watch': True}
    }

def configure_openclaw():
    '''Configure OpenClaw memorySearch automatically.'''
    config_path = find_openclaw_config()
    if not config_path:
        print('⚠️  OpenClaw config not found - manual setup may be needed')
        print('   Expected locations: ~/.openclaw/openclaw.json')
        return False
    
    print(f'📍 Found OpenClaw config: {config_path}')
    
    try:
        # Load config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Ensure agents.defaults exists
        if 'agents' not in config:
            config['agents'] = {}
        if 'defaults' not in config['agents']:
            config['agents']['defaults'] = {}
        
        # Check existing memorySearch
        memory_config = get_memory_config()
        existing = config['agents']['defaults'].get('memorySearch', {})
        
        if existing:
            # Merge missing extraPaths
            current_paths = set(existing.get('extraPaths', []))
            new_paths = set(memory_config['extraPaths'])
            missing = new_paths - current_paths
            
            if missing:
                existing['extraPaths'] = existing.get('extraPaths', [])
                existing['extraPaths'].extend(list(missing))
                print(f'➕ Added missing paths: {list(missing)}')
            else:
                print('✅ memorySearch already configured properly')
                return True
        else:
            # Add complete config
            config['agents']['defaults']['memorySearch'] = memory_config
            print('➕ Added complete memorySearch configuration')
        
        # Write updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print('✅ OpenClaw configuration updated')
        return True
        
    except Exception as e:
        print(f'❌ Config update failed: {e}')
        return False

# Run configuration
configure_openclaw()
"

# Step 3: Initial indexing
if [ -f "$WORKSPACE/MEMORY.md" ]; then
    echo ""
    echo "🔢 Running initial indexing..."
    "$MEMORY_DIR/venv/bin/python" "$MEMORY_DIR/indexer.py"
else
    echo "⚠️  No MEMORY.md found - will index when you create one"
fi

echo ""
echo "✅ Persistent Memory fully installed and configured!"
echo ""
echo "📋 What was set up:"
echo "   • 3-layer memory system (Markdown + Vector + Graph)"
echo "   • Python environment with ChromaDB, NetworkX, sentence-transformers"
echo "   • OpenClaw memorySearch integration (directive compliance)"
echo "   • Daily memory maintenance scripts"
echo ""
echo "🎯 Usage:"
echo "   Index:  vector_memory/venv/bin/python vector_memory/indexer.py"
echo "   Search: vector_memory/venv/bin/python vector_memory/search.py \"query\""
echo "   Status: vector_memory/venv/bin/python vector_memory/auto_retrieve.py --status"
echo ""
echo "🚀 Your agent now has persistent memory across sessions!"
echo "   Try asking it about previous conversations or workspace directives."