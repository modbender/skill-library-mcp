#!/usr/bin/env node
/**
 * OpenClaw Docs Index Builder
 * Builds file-level index with FTS5 + embeddings
 * 
 * Usage: node docs-index.js rebuild
 */

const fs = require('fs');
const path = require('path');
const { buildIndex } = require('../lib/indexer');

const DOCS_PATH = process.env.DOCS_PATH || '/usr/lib/node_modules/openclaw/docs';
const INDEX_DIR = path.join(process.env.HOME, '.openclaw/docs-index');
const INDEX_PATH = path.join(INDEX_DIR, 'openclaw-docs.sqlite');
const META_PATH = path.join(INDEX_DIR, 'index-meta.json');

async function rebuild() {
  console.log('🔨 Building OpenClaw docs index...');
  console.log(`📁 Docs path: ${DOCS_PATH}`);
  console.log(`💾 Index path: ${INDEX_PATH}`);
  console.log('');
  
  if (!fs.existsSync(DOCS_PATH)) {
    console.error(`❌ Docs path not found: ${DOCS_PATH}`);
    process.exit(1);
  }
  
  const startTime = Date.now();
  
  const result = await buildIndex(DOCS_PATH, INDEX_PATH, {
    onProgress: ({ current, total, indexed, errors }) => {
      console.log(`  📊 Progress: ${current}/${total} files (${indexed} indexed, ${errors} errors)`);
    }
  });
  
  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  
  // Save metadata
  const meta = {
    version: '2.0.0',
    indexedAt: new Date().toISOString(),
    docsPath: DOCS_PATH,
    filesIndexed: result.indexed,
    errors: result.errors,
    buildTimeSeconds: parseFloat(elapsed),
    indexType: 'file-level',
    features: ['fts5', 'vector-rerank']
  };
  
  fs.mkdirSync(INDEX_DIR, { recursive: true });
  fs.writeFileSync(META_PATH, JSON.stringify(meta, null, 2));
  
  console.log('');
  console.log('✅ Index built successfully!');
  console.log(`   Files indexed: ${result.indexed}`);
  console.log(`   Errors: ${result.errors}`);
  console.log(`   Build time: ${elapsed}s`);
  
  if (fs.existsSync(INDEX_PATH)) {
    const stats = fs.statSync(INDEX_PATH);
    console.log(`   Index size: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
  }
  
  // Post-install guidance
  console.log('');
  console.log('─'.repeat(50));
  console.log('📋 SETUP TIPS:');
  console.log('');
  console.log('1. Add to your AGENTS.md (recommended):');
  console.log('   "When asked about OpenClaw, search docs first:');
  console.log('    node ~/.openclaw/skills/search-openclaw-docs/scripts/docs-search.js query"');
  console.log('');
  console.log('2. Test it:');
  console.log('   node ~/.openclaw/skills/search-openclaw-docs/scripts/docs-search.js "discord"');
  console.log('');
  console.log('Full setup guide: ~/.openclaw/skills/search-openclaw-docs/POST_INSTALL.md');
  console.log('─'.repeat(50));
}

function status() {
  require('./docs-status.js');
}

// Main
const command = process.argv[2];

switch (command) {
  case 'rebuild':
    rebuild().catch(err => {
      console.error('❌ Error:', err.message);
      process.exit(1);
    });
    break;
  case 'status':
    status();
    break;
  default:
    console.log('OpenClaw Docs Index Builder');
    console.log('');
    console.log('Usage: node docs-index.js <command>');
    console.log('');
    console.log('Commands:');
    console.log('  rebuild  - Build/rebuild the docs index');
    console.log('  status   - Check index status');
}
