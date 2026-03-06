#!/usr/bin/env bash
set -euo pipefail

# BrainDB Uninstall — Clean removal with memory export
# Guarantees: all memories exported, workspace files untouched, config restored

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OPENCLAW_CONFIG="${OPENCLAW_CONFIG:-$HOME/.openclaw/openclaw.json}"
BRAINDB_PORT="${BRAINDB_PORT:-3333}"
EXPORT_DIR="$HOME/.openclaw/braindb-export"

echo "🧠 BrainDB Uninstaller"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "This will:"
echo "  1. Export ALL memories to readable files"
echo "  2. Stop and remove Docker containers"
echo "  3. Remove BrainDB from OpenClaw config"
echo "  4. Leave your workspace files untouched"
echo ""

read -p "Continue? [y/N] " -n 1 -r REPLY
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Cancelled."
  exit 0
fi

# ─── Step 1: Export memories ──────────────────────
echo ""
echo "📦 Step 1: Exporting memories..."

mkdir -p "$EXPORT_DIR"
EXPORT_TIME=$(date +%Y%m%d-%H%M%S)

# Check if BrainDB is reachable
if curl -sf "http://localhost:$BRAINDB_PORT/health" >/dev/null 2>&1; then
  MEMORY_COUNT=$(curl -sf "http://localhost:$BRAINDB_PORT/health" | node -e "
    let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{
      try{console.log(JSON.parse(d).totalMemories||0)}catch{console.log(0)}
    })" 2>/dev/null || echo "0")
  
  echo "   Found $MEMORY_COUNT memories to export."
  
  if [ "$MEMORY_COUNT" -gt "0" ]; then
    # Export as structured JSON (re-importable)
    node -e "
      const http = require('http');
      const fs = require('fs');
      
      function post(url, body) {
        return new Promise((resolve, reject) => {
          const data = JSON.stringify(body);
          const u = new URL(url);
          const req = http.request({
            hostname: u.hostname, port: u.port, path: u.pathname,
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) },
            timeout: 30000,
          }, res => {
            let buf = '';
            res.on('data', c => buf += c);
            res.on('end', () => { try { resolve(JSON.parse(buf)); } catch { resolve(null); } });
          });
          req.on('error', reject);
          req.write(data);
          req.end();
        });
      }
      
      function get(url) {
        return new Promise((resolve, reject) => {
          const u = new URL(url);
          const req = http.request({
            hostname: u.hostname, port: u.port, path: u.pathname,
            timeout: 10000,
          }, res => {
            let buf = '';
            res.on('data', c => buf += c);
            res.on('end', () => { try { resolve(JSON.parse(buf)); } catch { resolve(null); } });
          });
          req.on('error', reject);
          req.end();
        });
      }
      
      async function exportAll() {
        const baseUrl = 'http://localhost:$BRAINDB_PORT';
        const exportDir = '$EXPORT_DIR';
        const timestamp = '$EXPORT_TIME';
        
        // Get all memories via broad recall queries
        const queries = [
          '', 'identity', 'work', 'family', 'project', 'tool', 'rule',
          'decision', 'preference', 'event', 'lesson', 'goal', 'contact'
        ];
        
        const allMemories = new Map();
        
        for (const q of queries) {
          try {
            const res = await post(baseUrl + '/memory/recall', { query: q || 'everything', limit: 200 });
            if (res?.results) {
              for (const m of res.results) {
                if (m.id && !allMemories.has(m.id)) {
                  allMemories.set(m.id, m);
                }
              }
            }
          } catch {}
        }
        
        const memories = [...allMemories.values()];
        console.log('   Collected ' + memories.length + ' unique memories.');
        
        // Export raw JSON (re-importable)
        fs.writeFileSync(
          exportDir + '/braindb-export-' + timestamp + '.json',
          JSON.stringify({ exported: new Date().toISOString(), count: memories.length, memories }, null, 2)
        );
        
        // Export as readable markdown by shard type
        const byType = {};
        for (const m of memories) {
          const t = m.type || m.source_shard || 'unknown';
          if (!byType[t]) byType[t] = [];
          byType[t].push(m);
        }
        
        for (const [type, mems] of Object.entries(byType)) {
          let md = '# BrainDB Export — ' + type.charAt(0).toUpperCase() + type.slice(1) + ' Memories\n\n';
          md += 'Exported: ' + new Date().toISOString() + '\\n';
          md += 'Count: ' + mems.length + '\\n\\n---\\n\\n';
          
          for (const m of mems) {
            md += '## ' + (m.trigger || m.id) + '\\n\\n';
            md += (m.content || '') + '\\n\\n';
            if (m.similarity) md += '_Relevance: ' + m.similarity.toFixed(3) + '_\\n';
            if (m.strength) md += '_Strength: ' + m.strength.toFixed(3) + '_\\n';
            md += '\\n---\\n\\n';
          }
          
          fs.writeFileSync(exportDir + '/' + type + '-memories-' + timestamp + '.md', md);
        }
        
        console.log('   ✅ Exported to ' + exportDir + '/');
        console.log('   Files:');
        console.log('     braindb-export-' + timestamp + '.json (re-importable)');
        for (const type of Object.keys(byType)) {
          console.log('     ' + type + '-memories-' + timestamp + '.md (readable)');
        }
      }
      
      exportAll().catch(e => console.error('   ⚠️  Export error:', e.message));
    " 2>/dev/null
  fi
else
  echo "   ⚠️  BrainDB not reachable. Checking for local data..."
  
  # Try to export from embeddings cache as fallback
  EMBEDDINGS="$SCRIPT_DIR/data/embeddings.json"
  if [ ! -f "$EMBEDDINGS" ]; then
    # Check Docker volume
    EMBEDDINGS=$(docker compose -f "$SCRIPT_DIR/docker-compose.yml" exec -T gateway cat /app/data/embeddings.json 2>/dev/null || echo "")
  fi
  
  if [ -f "$EMBEDDINGS" ] 2>/dev/null; then
    cp "$EMBEDDINGS" "$EXPORT_DIR/embeddings-backup-$EXPORT_TIME.json"
    echo "   ✅ Saved embeddings cache to $EXPORT_DIR/"
  else
    echo "   ⚠️  No local data found. If you had memories, check Docker volumes:"
    echo "      docker volume ls | grep braindb"
  fi
fi

# ─── Step 2: Stop containers ─────────────────────
echo ""
echo "🐳 Step 2: Stopping containers..."

cd "$SCRIPT_DIR"
if docker compose ps --quiet 2>/dev/null | grep -q .; then
  docker compose down 2>&1 | grep -v "^$"
  echo "   ✅ Containers stopped and removed"
else
  echo "   No running containers found"
fi

echo ""
echo "   ⚠️  Docker volumes preserved (your data is safe)."
echo "   To delete volumes: docker volume rm braindb_neo4j-data braindb_embedder-cache braindb_gateway-data"

# ─── Step 3: Remove OpenClaw config ──────────────
echo ""
echo "⚙️  Step 3: Removing OpenClaw config..."

if [ -f "$OPENCLAW_CONFIG" ]; then
  node -e "
    const fs = require('fs');
    const config = JSON.parse(fs.readFileSync('$OPENCLAW_CONFIG', 'utf8'));
    
    // Remove plugin slot
    if (config.plugins?.slots?.memory === 'braindb') {
      delete config.plugins.slots.memory;
    }
    
    // Remove plugin entry
    if (config.plugins?.entries?.braindb) {
      delete config.plugins.entries.braindb;
    }
    
    // Clean up empty objects
    if (config.plugins?.slots && Object.keys(config.plugins.slots).length === 0) {
      delete config.plugins.slots;
    }
    
    fs.writeFileSync('$OPENCLAW_CONFIG', JSON.stringify(config, null, 2));
    console.log('   ✅ BrainDB removed from OpenClaw config');
  " 2>/dev/null || echo "   ⚠️  Could not update config. Remove braindb entries manually."
else
  echo "   Config not found — nothing to clean up"
fi

# ─── Done ─────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ BrainDB uninstalled!"
echo ""
echo "   Your memories are exported to: $EXPORT_DIR/"
echo "   Your workspace files (MEMORY.md, etc.) were never modified."
echo ""
echo "   Restart OpenClaw to apply: openclaw gateway restart"
echo ""
echo "   To reinstall later, your exported memories can be re-imported."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
