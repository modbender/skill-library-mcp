#!/usr/bin/env node
/**
 * Main runner script - orchestrates fetch → process pipeline
 */

const { execSync } = require('child_process');
const path = require('path');

const SCRIPTS_DIR = __dirname;

/**
 * Run a script and capture output
 * @param {string} script - Script name to run
 */
function runScript(script) {
  const scriptPath = path.join(SCRIPTS_DIR, script);
  try {
    execSync(`node "${scriptPath}"`, {
      stdio: 'inherit',
      cwd: process.cwd()
    });
  } catch (e) {
    // Script may exit with non-zero, that's ok
    if (e.status !== 0) {
      process.exit(e.status);
    }
  }
}

/**
 * Main function
 */
function main() {
  const args = process.argv.slice(2);
  const force = args.includes('--force');
  
  console.log('═══════════════════════════════════════');
  console.log('   X Bookmark Archiver');
  console.log('═══════════════════════════════════════\n');
  
  // Step 1: Fetch (always run unless --force)
  if (!force) {
    console.log('📥 STEP 1: Fetching bookmarks\n');
    runScript('fetch.cjs');
    console.log('');
  } else {
    console.log('⚡ Force mode: skipping fetch, processing existing pending\n');
  }
  
  // Step 2: Process
  console.log('📤 STEP 2: Processing bookmarks\n');
  runScript('process.cjs');
  
  console.log('\n═══════════════════════════════════════');
  console.log('   Done!');
  console.log('═══════════════════════════════════════');
}

if (require.main === module) {
  main();
}
