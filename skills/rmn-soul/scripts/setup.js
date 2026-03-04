#!/usr/bin/env node
/**
 * RMN Soul Setup — Auto-migrate agent memory files into recursive neural network
 */

const fs = require('fs');
const path = require('path');
const { RecursiveMemoryNetwork } = require('./rmn-engine');

const WORKSPACE = process.env.OPENCLAW_WORKSPACE || path.resolve(__dirname, '../../../');
const DATA_DIR = path.join(WORKSPACE, 'rmn-soul-data');
const DB_PATH = path.join(DATA_DIR, 'memory.json');

function findMemoryFiles(workspace) {
  const files = [];
  
  // MEMORY.md
  const memoryMd = path.join(workspace, 'MEMORY.md');
  if (fs.existsSync(memoryMd)) files.push({ path: memoryMd, type: 'memory' });
  
  // SOUL.md
  const soulMd = path.join(workspace, 'SOUL.md');
  if (fs.existsSync(soulMd)) files.push({ path: soulMd, type: 'soul' });
  
  // USER.md
  const userMd = path.join(workspace, 'USER.md');
  if (fs.existsSync(userMd)) files.push({ path: userMd, type: 'identity' });
  
  // IDENTITY.md
  const identityMd = path.join(workspace, 'IDENTITY.md');
  if (fs.existsSync(identityMd)) files.push({ path: identityMd, type: 'identity' });
  
  // memory/*.md
  const memDir = path.join(workspace, 'memory');
  if (fs.existsSync(memDir)) {
    for (const f of fs.readdirSync(memDir)) {
      if (f.endsWith('.md') && f !== 'INDEX.md') {
        files.push({ path: path.join(memDir, f), type: 'daily' });
      }
    }
  }
  
  // .issues/open-*
  const issuesDir = path.join(workspace, '.issues');
  if (fs.existsSync(issuesDir)) {
    for (const f of fs.readdirSync(issuesDir)) {
      if (f.startsWith('open-')) {
        files.push({ path: path.join(issuesDir, f), type: 'issue' });
      }
    }
  }
  
  return files;
}

function parseMemoryMd(content) {
  const entries = [];
  const lines = content.split('\n');
  let currentSection = '';
  let currentContent = [];
  let currentPriority = 1; // default working
  
  for (const line of lines) {
    if (line.startsWith('## ')) {
      if (currentContent.length > 0) {
        entries.push({
          section: currentSection,
          content: currentContent.join('\n').trim(),
          priority: currentPriority,
        });
        currentContent = [];
      }
      currentSection = line.replace(/^##\s*/, '').trim();
      // Detect priority from [P0], [P1], etc.
      const pMatch = currentSection.match(/\[P(\d)\]/);
      currentPriority = pMatch ? parseInt(pMatch[1]) : 1;
    } else if (line.startsWith('### ')) {
      if (currentContent.length > 0) {
        entries.push({
          section: currentSection,
          content: currentContent.join('\n').trim(),
          priority: currentPriority,
        });
        currentContent = [];
      }
      const sub = line.replace(/^###\s*/, '').trim();
      const pMatch = sub.match(/\[P(\d)\]/);
      if (pMatch) currentPriority = parseInt(pMatch[1]);
      currentSection = sub;
    } else if (line.trim()) {
      currentContent.push(line);
    }
  }
  
  if (currentContent.length > 0) {
    entries.push({ section: currentSection, content: currentContent.join('\n').trim(), priority: currentPriority });
  }
  
  return entries;
}

function priorityToLayer(priority) {
  // P0 → semantic/identity, P1 → episodic, P2 → working
  if (priority === 0) return 3; // semantic
  if (priority === 1) return 2; // episodic
  return 1; // working
}

function setup() {
  console.log('🧠 RMN Soul Setup\n');
  console.log(`Workspace: ${WORKSPACE}`);
  console.log(`Data dir:  ${DATA_DIR}\n`);
  
  fs.mkdirSync(DATA_DIR, { recursive: true });
  
  // Find memory files
  const files = findMemoryFiles(WORKSPACE);
  console.log(`Found ${files.length} memory files:`);
  for (const f of files) console.log(`  [${f.type}] ${path.relative(WORKSPACE, f.path)}`);
  
  // Initialize RMN
  const rmn = new RecursiveMemoryNetwork(DB_PATH);
  let totalNodes = 0;
  
  // Process SOUL.md → Identity layer
  for (const f of files.filter(f => f.type === 'soul')) {
    const content = fs.readFileSync(f.path, 'utf-8');
    const lines = content.split('\n').filter(l => l.trim() && !l.startsWith('#'));
    for (const line of lines) {
      if (line.trim().length > 10) {
        rmn.inscribe(line.trim(), 'soul,identity,core', 4);
        totalNodes++;
      }
    }
  }
  
  // Process IDENTITY.md → Identity layer
  for (const f of files.filter(f => f.type === 'identity')) {
    const content = fs.readFileSync(f.path, 'utf-8');
    const lines = content.split('\n').filter(l => l.trim() && !l.startsWith('#'));
    for (const line of lines) {
      if (line.trim().length > 5) {
        rmn.inscribe(line.trim(), 'identity', 4);
        totalNodes++;
      }
    }
  }
  
  // Process MEMORY.md → Mixed layers
  for (const f of files.filter(f => f.type === 'memory')) {
    const content = fs.readFileSync(f.path, 'utf-8');
    const entries = parseMemoryMd(content);
    for (const entry of entries) {
      if (entry.content.length > 10) {
        const layer = priorityToLayer(entry.priority);
        rmn.inscribe(`[${entry.section}] ${entry.content}`, `memory,${entry.section.toLowerCase().replace(/\s+/g, '-')}`, layer);
        totalNodes++;
      }
    }
  }
  
  // Process daily logs → Episodic layer
  for (const f of files.filter(f => f.type === 'daily')) {
    const content = fs.readFileSync(f.path, 'utf-8');
    const date = path.basename(f.path, '.md');
    // Split by ## sections
    const sections = content.split(/^## /m).filter(Boolean);
    for (const section of sections) {
      const firstLine = section.split('\n')[0].trim();
      const body = section.split('\n').slice(1).join('\n').trim();
      if (body.length > 20) {
        rmn.inscribe(`[${date}] ${firstLine}: ${body.slice(0, 300)}`, `daily,${date}`, 2);
        totalNodes++;
      }
    }
  }
  
  // Process issues → Working layer
  for (const f of files.filter(f => f.type === 'issue')) {
    const content = fs.readFileSync(f.path, 'utf-8');
    const name = path.basename(f.path, '.md');
    rmn.inscribe(`[Issue] ${name}: ${content.slice(0, 500)}`, `issue,${name}`, 1);
    totalNodes++;
  }
  
  // Generate episodic summaries
  const stats = rmn.stats();
  const summary = `RMN initialized: ${stats.totalNodes} nodes across 5 layers. Identity: ${stats.layers.identity}, Semantic: ${stats.layers.semantic}, Episodic: ${stats.layers.episodic}, Working: ${stats.layers.working}, Sensory: ${stats.layers.sensory}`;
  rmn.inscribe(summary, 'rmn,setup,milestone', 2);
  
  console.log(`\n✅ Migration complete!`);
  console.log(`  Total nodes: ${rmn.stats().totalNodes}`);
  console.log(`  Layers: ${JSON.stringify(rmn.stats().layers)}`);
  console.log(`  Connections: ${rmn.stats().totalConnections}`);
  console.log(`  Tags: ${rmn.stats().tags}`);
  console.log(`  Data: ${DB_PATH}`);
  
  // Save config
  const configPath = path.join(DATA_DIR, 'config.json');
  if (!fs.existsSync(configPath)) {
    fs.writeFileSync(configPath, JSON.stringify({
      chain: 'base',
      chainId: 8453,
      identityRegistry: '0x8004A169FB4a3325136EB29fA0ceB6D2e539a432',
      reputationRegistry: '0x8004BAa17C55a88189AE136b182e5fdA19dE9b63',
      sponsorKey: process.env.RMN_SPONSOR_KEY || '',
      autoAnchorDays: 7,
      ipfsEnabled: true,
      agentId: null,
      lastAnchor: null,
    }, null, 2));
    console.log(`  Config: ${configPath}`);
  }
  
  return rmn;
}

if (require.main === module) {
  setup();
}

module.exports = { setup, findMemoryFiles, parseMemoryMd };
