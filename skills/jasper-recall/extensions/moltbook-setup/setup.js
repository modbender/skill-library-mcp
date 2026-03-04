#!/usr/bin/env node
/**
 * Moltbook Agent Setup for jasper-recall
 * 
 * Configures a sandboxed agent to use jasper-recall with --public-only restriction.
 * This ensures the agent can only access shared/public memories, not private ones.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const readline = require('readline');

const MOLTBOOK_WORKSPACE = path.join(os.homedir(), '.openclaw', 'workspace-moltbook');
const MAIN_WORKSPACE = path.join(os.homedir(), '.openclaw', 'workspace');
const RECALL_BIN = path.join(os.homedir(), '.local', 'bin', 'recall');

function log(msg) {
  console.log(`🦞 ${msg}`);
}

function warn(msg) {
  console.log(`⚠️  ${msg}`);
}

function error(msg) {
  console.error(`❌ ${msg}`);
}

function success(msg) {
  console.log(`✅ ${msg}`);
}

async function prompt(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  return new Promise(resolve => {
    rl.question(question, answer => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

async function setup() {
  console.log('');
  log('Moltbook Agent — jasper-recall Integration Setup');
  console.log('='.repeat(55));
  console.log('');
  console.log('  This configures the moltbook-scanner agent to use jasper-recall');
  console.log('  with the --public-only restriction for privacy.');
  console.log('');
  console.log('  What it does:');
  console.log('    1. Creates ~/bin/recall wrapper (forces --public-only)');
  console.log('    2. Symlinks shared/ folder from main workspace');
  console.log('    3. Verifies jasper-recall is installed');
  console.log('');

  // Check prerequisites
  if (!fs.existsSync(MOLTBOOK_WORKSPACE)) {
    error(`Moltbook workspace not found: ${MOLTBOOK_WORKSPACE}`);
    console.log('  Create it first or check your OpenClaw agent config.');
    process.exit(1);
  }

  if (!fs.existsSync(RECALL_BIN)) {
    error(`jasper-recall not installed: ${RECALL_BIN}`);
    console.log('  Install it first: npx jasper-recall setup');
    process.exit(1);
  }

  const proceed = await prompt('  Continue? (y/n): ');
  if (proceed.toLowerCase() !== 'y' && proceed.toLowerCase() !== 'yes') {
    console.log('\n  Setup cancelled.\n');
    process.exit(0);
  }

  console.log('');

  // Step 1: Create bin directory and wrapper
  const binDir = path.join(MOLTBOOK_WORKSPACE, 'bin');
  const wrapperPath = path.join(binDir, 'recall');
  
  fs.mkdirSync(binDir, { recursive: true });
  
  const wrapperScript = `#!/bin/bash
# Sandboxed recall wrapper - forces --public-only for privacy
# This agent can ONLY access shared/public memory

exec ${RECALL_BIN} "$@" --public-only
`;

  fs.writeFileSync(wrapperPath, wrapperScript);
  fs.chmodSync(wrapperPath, '755');
  success(`Created recall wrapper: ${wrapperPath}`);

  // Step 2: Create shared folder symlink
  const sharedSource = path.join(MAIN_WORKSPACE, 'memory', 'shared');
  const sharedTarget = path.join(MOLTBOOK_WORKSPACE, 'shared');

  // Ensure source exists
  fs.mkdirSync(sharedSource, { recursive: true });

  // Remove existing symlink/dir if needed
  try {
    const stat = fs.lstatSync(sharedTarget);
    if (stat.isSymbolicLink()) {
      fs.unlinkSync(sharedTarget);
    } else if (stat.isDirectory()) {
      warn(`${sharedTarget} is a directory, not a symlink. Skipping.`);
    }
  } catch (e) {
    // Doesn't exist, that's fine
  }

  if (!fs.existsSync(sharedTarget)) {
    fs.symlinkSync(sharedSource, sharedTarget);
    success(`Created symlink: shared/ → ${sharedSource}`);
  }

  // Step 3: Verify setup
  console.log('');
  log('Verifying setup...');
  
  const issues = verify({ quiet: true });
  
  if (issues.length === 0) {
    console.log('');
    console.log('='.repeat(55));
    success('Setup complete!');
    console.log('');
    console.log('  The moltbook-scanner agent can now use:');
    console.log('    ~/bin/recall "query"  — searches public memories only');
    console.log('    shared/               — symlink to main agent\'s shared memory');
    console.log('');
    console.log('  Test it:');
    console.log(`    ${wrapperPath} "test query"`);
    console.log('');
  } else {
    console.log('');
    warn('Setup completed with issues:');
    issues.forEach(issue => console.log(`  - ${issue}`));
  }
}

function verify(options = {}) {
  const { quiet = false } = options;
  const issues = [];

  if (!quiet) {
    console.log('');
    log('Moltbook Agent — jasper-recall Verification');
    console.log('='.repeat(55));
    console.log('');
  }

  // Check 1: Workspace exists
  if (!fs.existsSync(MOLTBOOK_WORKSPACE)) {
    issues.push(`Workspace missing: ${MOLTBOOK_WORKSPACE}`);
  } else if (!quiet) {
    success(`Workspace exists: ${MOLTBOOK_WORKSPACE}`);
  }

  // Check 2: Recall wrapper exists and is executable
  const wrapperPath = path.join(MOLTBOOK_WORKSPACE, 'bin', 'recall');
  if (!fs.existsSync(wrapperPath)) {
    issues.push(`Recall wrapper missing: ${wrapperPath}`);
  } else {
    // Check it has --public-only
    const content = fs.readFileSync(wrapperPath, 'utf8');
    if (!content.includes('--public-only')) {
      issues.push('Recall wrapper missing --public-only flag!');
    } else if (!quiet) {
      success('Recall wrapper has --public-only restriction');
    }
  }

  // Check 3: Shared folder is a symlink
  const sharedPath = path.join(MOLTBOOK_WORKSPACE, 'shared');
  try {
    const stat = fs.lstatSync(sharedPath);
    if (!stat.isSymbolicLink()) {
      issues.push(`shared/ is not a symlink (should link to main workspace)`);
    } else {
      const target = fs.readlinkSync(sharedPath);
      if (!quiet) {
        success(`shared/ symlink → ${target}`);
      }
    }
  } catch (e) {
    issues.push(`shared/ folder missing`);
  }

  // Check 4: jasper-recall is installed
  if (!fs.existsSync(RECALL_BIN)) {
    issues.push(`jasper-recall not installed: ${RECALL_BIN}`);
  } else if (!quiet) {
    success(`jasper-recall installed: ${RECALL_BIN}`);
  }

  // Check 5: AGENTS.md mentions recall restrictions
  const agentsMd = path.join(MOLTBOOK_WORKSPACE, 'AGENTS.md');
  if (fs.existsSync(agentsMd)) {
    const content = fs.readFileSync(agentsMd, 'utf8');
    if (!content.includes('public-only') && !content.includes('public_only')) {
      issues.push('AGENTS.md should document --public-only restriction');
    } else if (!quiet) {
      success('AGENTS.md documents recall restrictions');
    }
  }

  if (!quiet) {
    console.log('');
    if (issues.length === 0) {
      console.log('='.repeat(55));
      success('All checks passed! Moltbook agent is properly configured.');
    } else {
      console.log('='.repeat(55));
      warn(`Found ${issues.length} issue(s):`);
      issues.forEach(issue => console.log(`  ❌ ${issue}`));
      console.log('');
      console.log('  Run setup to fix: npx jasper-recall moltbook-setup');
    }
    console.log('');
  }

  return issues;
}

function showHelp() {
  console.log(`
Moltbook Agent — jasper-recall Integration

USAGE:
  npx jasper-recall moltbook-setup    Configure moltbook agent
  npx jasper-recall moltbook-verify   Verify configuration

WHAT IT DOES:
  Sets up the moltbook-scanner agent to use jasper-recall with privacy
  restrictions. The agent can only access shared/public memories, not
  private ones from the main workspace.

COMPONENTS:
  ~/bin/recall     Wrapper script that forces --public-only flag
  shared/          Symlink to main workspace's shared memory folder

PRIVACY MODEL:
  Main agent tags memories as [public] or [private] in daily notes.
  sync-shared.py extracts [public] content to memory/shared/.
  Sandboxed agents can ONLY search the shared collection.
`);
}

// Main
const command = process.argv[2];

switch (command) {
  case 'setup':
  case 'install':
    setup().catch(err => {
      error(err.message);
      process.exit(1);
    });
    break;
  case 'verify':
  case 'check':
    verify();
    break;
  case 'help':
  case '--help':
  case '-h':
  case undefined:
    showHelp();
    break;
  default:
    error(`Unknown command: ${command}`);
    showHelp();
    process.exit(1);
}
