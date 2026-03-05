#!/usr/bin/env node
/**
 * Repo Analyzer — first-run setup check
 */

const { execSync } = require('child_process');

let hasToken = false;

if (process.env.GITHUB_TOKEN) {
  console.log('✅ GITHUB_TOKEN is set.');
  hasToken = true;
} else {
  try {
    execSync('gh auth status', { stdio: 'pipe' });
    console.log('✅ gh CLI is authenticated.');
    hasToken = true;
  } catch {
    // not authenticated
  }
}

if (!hasToken) {
  console.log('⚠️  No GitHub token found. Analysis will be rate-limited (60 req/hr) and scores degraded.');
  console.log('');
  console.log('To fix, do one of:');
  console.log('  export GITHUB_TOKEN="ghp_..."');
  console.log('  gh auth login');
  console.log('');
}

console.log('Repo Analyzer ready — run: node scripts/analyze.js <owner/repo>');
