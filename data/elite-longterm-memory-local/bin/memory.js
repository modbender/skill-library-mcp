#!/usr/bin/env node
/**
 * Elite Longterm Memory - Local Edition
 * CLI tool for memory management
 */

const { MemoryManager } = require('../lib/memory');
const path = require('path');

const WORKSPACE = process.cwd();
const DB_PATH = path.join(WORKSPACE, 'memory', 'vectors');
const OLLAMA_URL = process.env.OLLAMA_URL || 'http://localhost:11434';
const EMBEDDING_MODEL = process.env.EMBEDDING_MODEL || 'nomic-embed-text';

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  const memory = new MemoryManager({
    dbPath: DB_PATH,
    ollamaUrl: OLLAMA_URL,
    embeddingModel: EMBEDDING_MODEL
  });

  try {
    switch (command) {
      case 'init':
        await initWorkspace();
        break;
      case 'store':
        await storeMemory(memory, args);
        break;
      case 'search':
        await searchMemory(memory, args);
        break;
      case 'stats':
        await showStats(memory);
        break;
      case 'forget':
        await forgetMemory(memory, args);
        break;
      case 'help':
      default:
        showHelp();
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  } finally {
    await memory.close();
  }
}

async function initWorkspace() {
  const fs = require('fs').promises;
  
  // Create directories
  await fs.mkdir(path.join(WORKSPACE, 'memory'), { recursive: true });
  await fs.mkdir(path.join(WORKSPACE, 'memory', 'vectors'), { recursive: true });
  
  // Create SESSION-STATE.md
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
  
  // Create MEMORY.md
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
  
  console.log('✅ Memory system initialized:');
  console.log('  - SESSION-STATE.md (Hot RAM)');
  console.log('  - MEMORY.md (Curated archive)');
  console.log('  - memory/ (Daily logs)');
  console.log('  - memory/vectors/ (LanceDB)');
}

async function storeMemory(memory, args) {
  const text = args[1];
  if (!text) {
    console.error('Usage: memory.js store "text to remember" [--importance 0.9] [--category preference]');
    process.exit(1);
  }
  
  let importance = 0.7;
  let category = 'other';
  
  for (let i = 2; i < args.length; i++) {
    if (args[i] === '--importance' && args[i + 1]) {
      importance = parseFloat(args[i + 1]);
      i++;
    }
    if (args[i] === '--category' && args[i + 1]) {
      category = args[i + 1];
      i++;
    }
  }
  
  await memory.init();
  const result = await memory.store(text, { importance, category });
  console.log(`✅ Stored: "${text.slice(0, 60)}..."`);
  console.log(`   ID: ${result.id}`);
  console.log(`   Category: ${category}, Importance: ${importance}`);
}

async function searchMemory(memory, args) {
  const query = args[1];
  if (!query) {
    console.error('Usage: memory.js search "query text" [--limit 5]');
    process.exit(1);
  }
  
  let limit = 5;
  for (let i = 2; i < args.length; i++) {
    if (args[i] === '--limit' && args[i + 1]) {
      limit = parseInt(args[i + 1]);
      i++;
    }
  }
  
  await memory.init();
  const results = await memory.search(query, limit);
  
  if (results.length === 0) {
    console.log('No relevant memories found.');
    return;
  }
  
  console.log(`Found ${results.length} memories:\n`);
  results.forEach((r, i) => {
    console.log(`${i + 1}. [${r.entry.category}] ${r.entry.text.slice(0, 80)}...`);
    console.log(`   Score: ${(r.score * 100).toFixed(0)}% | Importance: ${r.entry.importance}`);
    console.log();
  });
}

async function showStats(memory) {
  await memory.init();
  const count = await memory.count();
  console.log(`Memory Statistics:`);
  console.log(`  Total memories: ${count}`);
  console.log(`  Database: ${DB_PATH}`);
  console.log(`  Ollama: ${OLLAMA_URL}`);
  console.log(`  Model: ${EMBEDDING_MODEL}`);
}

async function forgetMemory(memory, args) {
  const queryIndex = args.indexOf('--query');
  if (queryIndex === -1 || !args[queryIndex + 1]) {
    console.error('Usage: memory.js forget --query "text to find"');
    process.exit(1);
  }
  
  const query = args[queryIndex + 1];
  await memory.init();
  
  const results = await memory.search(query, 5);
  if (results.length === 0) {
    console.log('No matching memories found.');
    return;
  }
  
  if (results.length === 1 && results[0].score > 0.9) {
    await memory.delete(results[0].entry.id);
    console.log(`✅ Forgotten: "${results[0].entry.text.slice(0, 60)}..."`);
    return;
  }
  
  console.log('Found multiple candidates. Use --id to specify:');
  results.forEach((r, i) => {
    console.log(`  ${r.entry.id.slice(0, 8)}: ${r.entry.text.slice(0, 60)}...`);
  });
}

function showHelp() {
  console.log(`
Elite Longterm Memory - Local Edition

Commands:
  init                    Initialize memory system
  store "text"            Store a memory
    --importance 0.9      Set importance (0-1)
    --category name       Set category (preference/decision/fact/entity/other)
  search "query"          Search memories
    --limit N             Max results (default: 5)
  stats                   Show statistics
  forget --query "text"   Delete memories
  help                    Show this help

Environment:
  OLLAMA_URL              Ollama server URL (default: http://localhost:11434)
  EMBEDDING_MODEL         Model name (default: nomic-embed-text)
`);
}

main();
