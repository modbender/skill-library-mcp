#!/usr/bin/env node
// SECURITY MANIFEST:
//   Environment variables accessed: NONE
//   External endpoints called: NONE (checks local index and may invoke local search tool)
//   Local files read: config.yaml, data/index/*
//   Local files written: NONE
/**
 * Health check for Curated Search skill
 *
 * Verifies index exists and search tool returns valid results.
 * Exit 0 = healthy, non-zero = failure.
 */

const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const skillDir = path.resolve(__dirname, '..');

function fail(msg) {
  console.error(`[ERROR] ${msg}`);
  process.exit(1);
}

function log(msg) {
  console.log(`[INFO] ${msg}`);
}

// 1. Check index files exist
const indexPath = path.join(skillDir, 'data', 'index.json');
const docsPath = path.join(skillDir, 'data', 'index-docs.json');

if (!fs.existsSync(indexPath)) {
  fail('Index missing: ' + indexPath);
}
if (!fs.existsSync(docsPath)) {
  fail('Documents file missing: ' + docsPath);
}

// 2. Run quick query
try {
  const result = spawnSync(process.execPath || 'node', [
    path.join(skillDir, 'scripts', 'search.js'),
    '--query=test',
    '--limit=1'
  ], {
    cwd: skillDir,
    encoding: 'utf8',
    env: process.env
  });

  if (result.exitCode !== 0) {
    fail('Search tool exited ' + result.exitCode + ': ' + result.stderr);
  }

  const output = JSON.parse(result.stdout);
  if (!Array.isArray(output)) {
    fail('Invalid output format (expected array)');
  }

  log('Index healthy: ' + output.length + ' results returned');
} catch (e) {
  fail('Health check exception: ' + e.message);
}

log('All checks passed');
process.exit(0);
