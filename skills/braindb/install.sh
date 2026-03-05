#!/usr/bin/env bash
set -euo pipefail

# BrainDB Install — OpenClaw Memory Plugin
# Handles: Docker setup, config patching, optional migration, backup

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OPENCLAW_CONFIG="${OPENCLAW_CONFIG:-$HOME/.openclaw/openclaw.json}"
BRAINDB_PORT="${BRAINDB_PORT:-3333}"
BACKUP_DIR="$HOME/.openclaw/braindb-backup"
DO_MIGRATE=false

for arg in "$@"; do
  case "$arg" in
    --migrate) DO_MIGRATE=true ;;
    --port=*) BRAINDB_PORT="${arg#*=}" ;;
  esac
done

echo "🧠 BrainDB Installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ─── Pre-flight checks ───────────────────────────
if ! command -v docker &>/dev/null; then
  echo "❌ Docker not found. Install: https://docs.docker.com/get-docker/"
  exit 1
fi

if ! docker compose version &>/dev/null 2>&1; then
  echo "❌ Docker Compose not found."
  exit 1
fi

if ! command -v node &>/dev/null; then
  echo "❌ Node.js not found."
  exit 1
fi

# Check if port is available
if curl -sf "http://localhost:$BRAINDB_PORT/health" >/dev/null 2>&1; then
  echo "⚠️  Port $BRAINDB_PORT is already in use."
  echo "   If BrainDB is already running, you're good!"
  ALREADY_RUNNING=true
else
  ALREADY_RUNNING=false
fi

# ─── Backup existing memory files ─────────────────
echo ""
echo "📋 Step 1: Backing up existing memory files..."

# Find workspace
WORKSPACE=""
if [ -f "$OPENCLAW_CONFIG" ]; then
  WORKSPACE=$(node -e "
    try {
      const c = require('$OPENCLAW_CONFIG');
      console.log(c.agents?.defaults?.workspace || '');
    } catch { console.log(''); }
  " 2>/dev/null || echo "")
fi

if [ -z "$WORKSPACE" ] || [ ! -d "$WORKSPACE" ]; then
  WORKSPACE="$PWD"
  echo "   Could not detect workspace, using: $WORKSPACE"
fi

mkdir -p "$BACKUP_DIR"
BACKUP_TIME=$(date +%Y%m%d-%H%M%S)

# Backup memory files (never modify originals)
for f in MEMORY.md USER.md SOUL.md IDENTITY.md TOOLS.md AGENTS.md HEARTBEAT.md; do
  if [ -f "$WORKSPACE/$f" ]; then
    cp "$WORKSPACE/$f" "$BACKUP_DIR/${f%.md}-$BACKUP_TIME.md"
  fi
done

# Backup daily notes
if [ -d "$WORKSPACE/memory" ]; then
  mkdir -p "$BACKUP_DIR/memory-$BACKUP_TIME"
  cp -r "$WORKSPACE/memory/"*.md "$BACKUP_DIR/memory-$BACKUP_TIME/" 2>/dev/null || true
fi

echo "   ✅ Backed up to $BACKUP_DIR"

# ─── Start Docker containers ─────────────────────
if [ "$ALREADY_RUNNING" = false ]; then
  echo ""
  echo "🐳 Step 2: Starting BrainDB containers..."
  
  cd "$SCRIPT_DIR"
  
  # Create .env with secure random password if missing
  if [ ! -f .env ]; then
    RANDOM_PASS=$(openssl rand -base64 18 | tr -d '/+=' | head -c 24)
    sed "s/CHANGE_ME/$RANDOM_PASS/" .env.example > .env
    echo "   🔐 Generated secure Neo4j password"
  fi
  
  docker compose build --quiet 2>&1 | tail -1 || true
  docker compose up -d 2>&1 | grep -v "^$"
  
  # Wait for services
  echo -n "   Waiting for services"
  for i in $(seq 1 60); do
    if curl -sf "http://localhost:$BRAINDB_PORT/health" >/dev/null 2>&1; then
      echo " ✅"
      break
    fi
    [ "$i" -eq 60 ] && echo " ❌ timeout (check: docker compose logs)" && exit 1
    echo -n "."
    sleep 2
  done
else
  echo ""
  echo "🐳 Step 2: BrainDB already running ✅"
fi

# ─── Configure OpenClaw ──────────────────────────
echo ""
echo "⚙️  Step 3: Configuring OpenClaw..."

if [ -f "$OPENCLAW_CONFIG" ]; then
  # Check if braindb is already configured
  HAS_BRAINDB=$(node -e "
    const c = require('$OPENCLAW_CONFIG');
    console.log(c.plugins?.entries?.braindb ? 'yes' : 'no');
  " 2>/dev/null || echo "no")
  
  if [ "$HAS_BRAINDB" = "yes" ]; then
    echo "   BrainDB plugin already configured ✅"
  else
    # Patch config to add BrainDB plugin
    node -e "
      const fs = require('fs');
      const config = JSON.parse(fs.readFileSync('$OPENCLAW_CONFIG', 'utf8'));
      
      // Add plugin slot
      if (!config.plugins) config.plugins = {};
      if (!config.plugins.slots) config.plugins.slots = {};
      config.plugins.slots.memory = 'braindb';
      
      // Add plugin entry
      if (!config.plugins.entries) config.plugins.entries = {};
      config.plugins.entries.braindb = {
        enabled: true,
        config: {
          gatewayUrl: 'http://localhost:$BRAINDB_PORT',
          autoCapture: true,
          autoRecall: true,
          maxRecallResults: 7,
          minMessageLength: 20
        }
      };
      
      fs.writeFileSync('$OPENCLAW_CONFIG', JSON.stringify(config, null, 2));
      console.log('   ✅ OpenClaw config updated');
    " 2>/dev/null || echo "   ⚠️  Could not update config automatically. See manual setup below."
  fi
else
  echo "   ⚠️  OpenClaw config not found at $OPENCLAW_CONFIG"
  echo "   Add this to your config manually:"
  echo '   "plugins": {'
  echo '     "slots": { "memory": "braindb" },'
  echo '     "entries": {'
  echo '       "braindb": {'
  echo '         "enabled": true,'
  echo '         "config": {'
  echo "           \"gatewayUrl\": \"http://localhost:$BRAINDB_PORT\","
  echo '           "autoCapture": true,'
  echo '           "autoRecall": true,'
  echo '           "maxRecallResults": 7,'
  echo '           "minMessageLength": 20'
  echo '         }'
  echo '       }'
  echo '     }'
  echo '   }'
fi

# ─── Migration offer ─────────────────────────────
echo ""
echo "📚 Step 4: Memory migration"
echo ""

MEMORY_COUNT=$(curl -sf "http://localhost:$BRAINDB_PORT/health" 2>/dev/null | node -e "
  let d=''; process.stdin.on('data',c=>d+=c); process.stdin.on('end',()=>{
    try { console.log(JSON.parse(d).totalMemories||0); } catch { console.log(0); }
  });
" 2>/dev/null || echo "0")

if [ "$MEMORY_COUNT" -gt "0" ]; then
  echo "   BrainDB already has $MEMORY_COUNT memories."
  echo "   Skipping migration. Run manually if needed:"
  echo "   node $SCRIPT_DIR/migrate.cjs $WORKSPACE"
else
  # Count available files
  FILE_COUNT=$(node "$SCRIPT_DIR/migrate.cjs" --scan "$WORKSPACE" 2>/dev/null | grep "Found" | grep -oE '[0-9]+' || echo "0")
  
  if [ "$FILE_COUNT" -gt "0" ]; then
    echo "   Found $FILE_COUNT workspace files to import."
    echo ""
    if [ "$DO_MIGRATE" = true ]; then
      echo "   Migrating (local-only, no external API calls)..."
      echo ""
      node "$SCRIPT_DIR/migrate.cjs" "$WORKSPACE" --braindb "http://localhost:$BRAINDB_PORT"
    else
      echo "   Run migration to import existing knowledge:"
      echo "   node $SCRIPT_DIR/migrate.cjs $WORKSPACE --braindb http://localhost:$BRAINDB_PORT"
      echo ""
      echo "   Or re-run with: ./install.sh --migrate"
    fi
  else
    echo "   No workspace files found to migrate."
    echo "   BrainDB will learn from your conversations automatically."
  fi
fi

# ─── Done ─────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ BrainDB installed!"
echo ""
echo "   Gateway:  http://localhost:$BRAINDB_PORT"
echo "   Memories:  $(curl -sf http://localhost:$BRAINDB_PORT/health 2>/dev/null | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{console.log(JSON.parse(d).totalMemories||0)}catch{console.log('?')}})" 2>/dev/null || echo "?")"
echo "   Backup:   $BACKUP_DIR"
echo ""
echo "   Restart OpenClaw to activate: openclaw gateway restart"
echo ""
echo "   Your MEMORY.md and other files are untouched."
echo "   BrainDB enhances — it doesn't replace."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
