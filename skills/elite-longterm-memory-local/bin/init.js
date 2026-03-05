#!/usr/bin/env node
/**
 * Initialize Elite Longterm Memory workspace
 */

const fs = require('fs').promises;
const path = require('path');

const WORKSPACE = process.cwd();

async function init() {
  console.log('🧠 Initializing Elite Longterm Memory...\n');
  
  // Create directories
  await fs.mkdir(path.join(WORKSPACE, 'memory'), { recursive: true });
  await fs.mkdir(path.join(WORKSPACE, 'memory', 'vectors'), { recursive: true });
  
  // Create SESSION-STATE.md (Hot RAM)
  const sessionState = `# SESSION-STATE.md — Active Working Memory

This file is the agent's "RAM" — survives compaction, restarts, distractions.

## Current Task
[None]

## Key Context
[None yet]

## Pending Actions
- [ ] None

## Recent Decisions
[None yet]

---
*Last updated: ${new Date().toISOString()}*
`;
  await fs.writeFile(path.join(WORKSPACE, 'SESSION-STATE.md'), sessionState);
  console.log('✅ SESSION-STATE.md (Hot RAM)');
  
  // Create MEMORY.md (Curated archive)
  const memoryMd = `# MEMORY.md — Curated Long-term Memory

Distilled wisdom. The good stuff.

## About User

## Preferences

## Important Decisions

## Lessons Learned

## Projects

---
*Created: ${new Date().toISOString()}*
`;
  await fs.writeFile(path.join(WORKSPACE, 'MEMORY.md'), memoryMd);
  console.log('✅ MEMORY.md (Curated archive)');
  
  // Create today's log
  const today = new Date().toISOString().split('T')[0];
  const dailyLog = `# ${today}.md — Daily Log

## Sessions

## Key Events

## Decisions Made

## Notes

---
*Created: ${new Date().toISOString()}*
`;
  await fs.writeFile(path.join(WORKSPACE, 'memory', `${today}.md`), dailyLog);
  console.log(`✅ memory/${today}.md (Daily log)`);
  
  // Create .gitignore for vectors
  await fs.writeFile(
    path.join(WORKSPACE, 'memory', '.gitignore'),
    'vectors/\n*.db\n'
  );
  console.log('✅ memory/.gitignore');
  
  console.log('\n📁 Directory structure:');
  console.log('  workspace/');
  console.log('  ├── SESSION-STATE.md    ← Hot RAM (active context)');
  console.log('  ├── MEMORY.md           ← Curated long-term memory');
  console.log('  └── memory/');
  console.log('      ├── YYYY-MM-DD.md   ← Daily logs');
  console.log('      └── vectors/        ← LanceDB (auto-created)');
  
  console.log('\n🚀 Next steps:');
  console.log('  1. Ensure Ollama is running: ollama serve');
  console.log('  2. Pull embedding model: ollama pull nomic-embed-text');
  console.log('  3. Test: node skills/elite-longterm-memory/bin/memory.js store "Hello memory"');
}

init().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
