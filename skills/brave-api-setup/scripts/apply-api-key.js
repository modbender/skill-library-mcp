#!/usr/bin/env node
/**
 * Apply Brave API key to OpenClaw config
 * 
 * Usage:
 *   node apply-api-key.js <api-key>
 *   echo "BSA9..." | node apply-api-key.js --stdin
 * 
 * This writes directly to config, bypassing LLM transcription.
 */

const fs = require('fs');
const path = require('path');

const CONFIG_PATH = path.join(process.env.HOME, '.openclaw', 'openclaw.json');

function applyApiKey(apiKey) {
  // Validate key format
  if (!apiKey || !apiKey.startsWith('BSA') || apiKey.length < 20) {
    console.error('ERROR: Invalid API key format. Must start with "BSA" and be 20+ chars.');
    process.exit(1);
  }
  
  try {
    const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    
    // Ensure nested structure
    if (!config.tools) config.tools = {};
    if (!config.tools.web) config.tools.web = {};
    if (!config.tools.web.search) config.tools.web.search = {};
    
    config.tools.web.search.apiKey = apiKey;
    
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
    
    console.log('SUCCESS: Brave API key applied.');
    console.log('Key: ' + apiKey.substring(0, 8) + '...' + apiKey.substring(apiKey.length - 4));
    console.log('');
    console.log('Restart gateway to apply changes:');
    console.log('  openclaw gateway restart');
  } catch (err) {
    console.error('ERROR:', err.message);
    process.exit(1);
  }
}

// Main
const args = process.argv.slice(2);

if (args.includes('--help') || args.includes('-h')) {
  console.log('Apply Brave API key to OpenClaw config');
  console.log('');
  console.log('Usage:');
  console.log('  node apply-api-key.js <api-key>');
  console.log('  node apply-api-key.js --stdin  (read from stdin)');
  process.exit(0);
}

if (args.includes('--stdin')) {
  let data = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', chunk => data += chunk);
  process.stdin.on('end', () => applyApiKey(data.trim()));
} else if (args[0]) {
  applyApiKey(args[0]);
} else {
  console.error('ERROR: No API key provided.');
  console.error('Usage: node apply-api-key.js <api-key>');
  process.exit(1);
}
