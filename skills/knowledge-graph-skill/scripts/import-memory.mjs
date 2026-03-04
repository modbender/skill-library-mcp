#!/usr/bin/env node
// import-memory.mjs — Scan memory/*.md files and extract potential KG entities
// Usage:
//   node scripts/import-memory.mjs             (--dry-run is default)
//   node scripts/import-memory.mjs --dry-run   Show suggestions only
//   node scripts/import-memory.mjs --apply     Actually add to KG

import { readFileSync, readdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { load, save, addNode } from '../lib/graph.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
// Resolve workspace: walk up from skill dir to find workspace root
// Skill lives at <workspace>/skills/knowledge-graph/ or ~/.openclaw/skills/knowledge-graph/
// Memory lives at <workspace>/memory/ and <workspace>/MEMORY.md
function findWorkspace() {
  // Try: skill is inside workspace/skills/
  const wsCandidate = join(__dirname, '..', '..', '..');
  if (existsSync(join(wsCandidate, 'MEMORY.md')) || existsSync(join(wsCandidate, 'memory'))) {
    return wsCandidate;
  }
  // Fallback: standard openclaw workspace
  const home = process.env.HOME || require('os').homedir();
  return join(home, '.openclaw', 'workspace');
}
const WORKSPACE = findWorkspace();
const MEMORY_DIR = join(WORKSPACE, 'memory');
const MEMORY_FILE = join(WORKSPACE, 'MEMORY.md');

const args = process.argv.slice(2);
const applyMode = args.includes('--apply');
const dryRun = !applyMode;

// ── Pattern definitions ──
// Keep it conservative — better to miss than to add junk

const PATTERNS = [
  // IP addresses
  {
    name: 'ip',
    regex: /\b(\d{1,3}(?:\.\d{1,3}){3})\b/g,
    extract: m => ({ label: m[1], type: 'network', tags: ['ip', 'address'], id: `ip-${m[1].replace(/\./g, '-')}` }),
    minLen: 7
  },
  // Tailscale / VPN IPs (100.x.x.x pattern)
  {
    name: 'tailscale-ip',
    regex: /\b(100\.\d{1,3}\.\d{1,3}\.\d{1,3})\b/g,
    extract: m => ({ label: m[1], type: 'network', tags: ['tailscale', 'ip', 'vpn'], id: `tailscale-ip-${m[1].replace(/\./g, '-')}` }),
    minLen: 7
  },
  // Hostnames (lowercase.domain or words ending in common TLDs)
  {
    name: 'hostname',
    regex: /\b([a-z][a-z0-9\-]+\.(?:local|lan|home|internal|pi|dev))\b/gi,
    extract: m => ({ label: m[1].toLowerCase(), type: 'device', tags: ['hostname'], id: m[1].toLowerCase().replace(/[^a-z0-9]/g, '-') }),
    minLen: 4
  },
  // @telegram_handle or @bot_names
  {
    name: 'telegram',
    regex: /@([a-zA-Z][a-zA-Z0-9_]{4,}(?:bot|Bot|AI|ai)?)\b/g,
    extract: m => ({ label: '@' + m[1], type: 'service', tags: ['telegram', 'bot', 'handle'], id: 'tg-' + m[1].toLowerCase() }),
    minLen: 3
  },
  // Docker image names: must appear near docker context (docker, image, container, pull, run)
  // Excludes file paths by requiring docker keyword within 50 chars
  {
    name: 'docker-image',
    regex: /(?:docker|image|container|pull|run|FROM)\s+(?:[^\n]{0,30}?\s)?([a-z][a-z0-9\-]+\/[a-z][a-z0-9\-]+(?::[a-z0-9\.\-]+)?)\b/gi,
    extract: m => ({ label: m[1], type: 'service', tags: ['docker', 'image', 'container'], id: 'docker-' + m[1].replace(/[^a-z0-9]/g, '-').replace(/-+/g, '-') }),
    minLen: 5
  },
  // Project names: CamelCase identifiers that appear with "project", "repo", "app", "skill"
  {
    name: 'project',
    regex: /(?:project|repo|app|skill|plugin)\s+["']?([A-Z][a-zA-Z0-9\-_]{2,})["']?/g,
    extract: m => ({ label: m[1], type: 'project', tags: ['project'], id: m[1].toLowerCase().replace(/[^a-z0-9]/g, '-') }),
    minLen: 3
  },
  // Decisions (lines starting with "decided", "decision:", "✓ decided")
  {
    name: 'decision',
    regex: /(?:^|\n)(?:decided|decision:|✓\s*decided)[:\s]+(.{10,80})/gi,
    extract: m => {
      const text = m[1].trim().replace(/[^\w\s\-]/g, '').slice(0, 60);
      const id = text.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9\-]/g, '').slice(0, 40);
      return { label: text, type: 'decision', tags: ['decision'], id: `dec-${id}` };
    },
    minLen: 10
  },
  // Port numbers in context: "port 8080" or ":3000"
  {
    name: 'port',
    regex: /(?:port\s+|:)(\d{2,5})\b/gi,
    extract: m => {
      const port = parseInt(m[1]);
      if (port < 80 || port > 65535) return null;
      return { label: `Port ${m[1]}`, type: 'network', tags: ['port', 'service'], id: `port-${m[1]}` };
    },
    minLen: 2
  },
  // Named persons: "Anh X" or "Mr/Ms X" patterns
  {
    name: 'person',
    regex: /\b(?:Anh|Chị|Mr\.|Ms\.|Dr\.)\s+([A-Z][a-z]+)\b/g,
    extract: m => ({ label: m[1], type: 'human', tags: ['person'], id: m[1].toLowerCase() }),
    minLen: 2
  },
  // GitHub repos: github.com/user/repo
  {
    name: 'github',
    regex: /github\.com\/([a-zA-Z0-9\-_]+\/[a-zA-Z0-9\-_\.]+)/gi,
    extract: m => ({ label: m[1], type: 'project', tags: ['github', 'repo'], id: 'gh-' + m[1].toLowerCase().replace(/[^a-z0-9]/g, '-') }),
    minLen: 4
  },
  // Version strings with project name: "X v1.2.3" or "X version 1.2.3"
  {
    name: 'version',
    regex: /\b([A-Za-z][a-zA-Z0-9\-]{2,})\s+v(\d+\.\d+[\.\d]*)\b/g,
    extract: m => ({ label: m[1], type: 'platform', tags: ['software', 'version'], id: m[1].toLowerCase().replace(/[^a-z0-9]/g, '-'), attrs: { version: m[2] } }),
    minLen: 2
  }
];

// ── Read files ──
function readMemory() {
  const files = [];

  if (existsSync(MEMORY_FILE)) {
    files.push({ path: MEMORY_FILE, content: readFileSync(MEMORY_FILE, 'utf8') });
  }

  if (existsSync(MEMORY_DIR)) {
    const mdFiles = readdirSync(MEMORY_DIR)
      .filter(f => f.endsWith('.md'))
      .sort()
      .reverse() // recent first
      .slice(0, 30); // limit to last 30 files
    for (const f of mdFiles) {
      const p = join(MEMORY_DIR, f);
      files.push({ path: p, content: readFileSync(p, 'utf8') });
    }
  }

  return files;
}

// ── Extract entities ──
function extractEntities(files) {
  const candidates = new Map(); // id → candidate

  for (const { path, content } of files) {
    for (const pattern of PATTERNS) {
      const matches = [...content.matchAll(pattern.regex)];
      for (const m of matches) {
        const result = pattern.extract(m);
        if (!result) continue;
        if (!result.id || result.id.length < 2) continue;
        if (!result.label || result.label.length < (pattern.minLen || 2)) continue;
        // Skip obvious junk
        if (/^(and|the|for|not|but|are|was|has|had|can|may)$/i.test(result.label)) continue;

        const id = result.id.slice(0, 50);
        if (candidates.has(id)) {
          candidates.get(id).count++;
          candidates.get(id).sources.add(path);
        } else {
          candidates.set(id, {
            id,
            label: result.label,
            type: result.type,
            tags: result.tags || [],
            attrs: result.attrs || {},
            count: 1,
            sources: new Set([path]),
            patternName: pattern.name
          });
        }
      }
    }
  }

  // Filter: require count >= 1 for most, but ports/IPs need >= 2 appearances
  const filtered = [...candidates.values()].filter(c => {
    if (c.type === 'network') return c.count >= 2;
    return true;
  });

  // Sort by count desc
  filtered.sort((a, b) => b.count - a.count);
  return filtered;
}

// ── Dedup against existing KG ──
function dedup(candidates, store) {
  const existingIds = new Set(Object.keys(store.nodes));
  const existingLabels = new Set(Object.values(store.nodes).map(n => n.label.toLowerCase()));

  return candidates.filter(c => {
    if (existingIds.has(c.id)) return false; // exact id match
    if (existingLabels.has(c.label.toLowerCase())) return false; // label match
    return true;
  });
}

// ── Main ──
const files = readMemory();
if (!files.length) {
  console.log('⚠️  No memory files found. Checked:');
  console.log(`   ${MEMORY_FILE}`);
  console.log(`   ${MEMORY_DIR}/*.md`);
  process.exit(0);
}

console.log(`📂 Scanning ${files.length} file(s)...`);

const store = load();
const raw = extractEntities(files);
const candidates = dedup(raw, store);

if (!candidates.length) {
  console.log('✅ No new entities found (all already in KG or none detected).');
  process.exit(0);
}

console.log(`\n🔍 Found ${candidates.length} candidate entities (${raw.length} raw, deduped against ${Object.keys(store.nodes).length} existing):`);
console.log('');

for (const c of candidates) {
  const sources = [...c.sources].map(s => s.split('/').pop()).join(', ');
  const attrsStr = Object.keys(c.attrs).length ? ` attrs:${JSON.stringify(c.attrs)}` : '';
  console.log(`  [${c.type}] ${c.label}`);
  console.log(`    id: ${c.id} | pattern: ${c.patternName} | seen: ${c.count}x | in: ${sources}${attrsStr}`);
  if (c.tags.length) console.log(`    tags: ${c.tags.join(', ')}`);
}

if (dryRun) {
  console.log(`\n💡 Dry-run mode. Use --apply to add these ${candidates.length} entities to the KG.`);
  console.log(`   Note: Review carefully — some may be noise. KG principle: depth > breadth.`);
} else {
  // Apply mode
  console.log(`\n⚙️  Applying ${candidates.length} entities to KG...`);
  let added = 0, skipped = 0;
  for (const c of candidates) {
    try {
      addNode(store, {
        id: c.id,
        label: c.label,
        type: c.type,
        tags: c.tags,
        attrs: { ...c.attrs, imported_from: 'import-memory' },
        confidence: 0.5, // imported entities are reasonable guesses
      });
      console.log(`  ✅ Added: ${c.label} (${c.id}) [${c.type}]`);
      added++;
    } catch (e) {
      console.log(`  ⚠️  Skipped ${c.id}: ${e.message}`);
      skipped++;
    }
  }
  save(store);
  console.log(`\n✅ Done: ${added} added, ${skipped} skipped.`);
  console.log(`   Run 'node scripts/summarize.mjs' to update KGML.`);
}
