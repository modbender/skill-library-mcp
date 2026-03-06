#!/usr/bin/env node
/**
 * OpenClaw Docs Search v2
 * File-centric retrieval with keyword filter + vector rerank
 * 
 * Usage: node docs-search.js "your query"
 */

const path = require('path');
const { search, formatResults } = require('../lib/search');

const INDEX_PATH = path.join(process.env.HOME, '.openclaw/docs-index/openclaw-docs.sqlite');

async function main() {
  const query = process.argv.slice(2).join(' ');
  
  if (!query) {
    console.log('OpenClaw Docs Search v2');
    console.log('');
    console.log('Usage: node docs-search.js "your query"');
    console.log('');
    console.log('Examples:');
    console.log('  node docs-search.js "discord requireMention"');
    console.log('  node docs-search.js "webhook setup"');
    console.log('  node docs-search.js "memory search configuration"');
    console.log('');
    console.log('Options:');
    console.log('  --top=N    Return top N results (default: 3)');
    console.log('  --json     Output as JSON');
    process.exit(1);
  }
  
  // Parse options
  const args = process.argv.slice(2);
  const options = {};
  const queryParts = [];
  
  for (const arg of args) {
    if (arg.startsWith('--top=')) {
      options.topK = parseInt(arg.split('=')[1]) || 3;
    } else if (arg === '--json') {
      options.json = true;
    } else {
      queryParts.push(arg);
    }
  }
  
  const searchQuery = queryParts.join(' ');
  
  try {
    const results = await search(INDEX_PATH, searchQuery, options);
    
    if (options.json) {
      console.log(JSON.stringify(results, null, 2));
    } else {
      console.log(formatResults(results, searchQuery));
    }
  } catch (e) {
    console.error(`❌ Error: ${e.message}`);
    process.exit(1);
  }
}

main();
