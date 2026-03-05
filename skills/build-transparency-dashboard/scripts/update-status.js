#!/usr/bin/env node
/**
 * update-status.js
 * Runs after every deploy (or on schedule via GitHub Actions).
 * Reads git log from the current repo and writes status.json
 * to your public site repo.
 *
 * Environment variables:
 *   SITE_REPO_PATH  — absolute or relative path to the public site repo
 *                     (default: ../my-site relative to this script's parent dir)
 *
 * Usage:
 *   SITE_REPO_PATH=../my-site node scripts/update-status.js
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// ── Config ──
// SITE_REPO_PATH: set via env or falls back to a sibling directory
// In GitHub Actions: SITE_REPO_PATH is set to the checkout path of the public site
const SITE_REPO_PATH = process.env.SITE_REPO_PATH
  ? path.resolve(process.env.SITE_REPO_PATH)
  : path.join(__dirname, '../../my-site'); // fallback for local dev

const STATUS_PATH = path.join(SITE_REPO_PATH, 'status.json');

// ── Git helpers ──

/**
 * Count commits in the last 7 days from the current repo.
 */
function getCommitCount() {
  try {
    const since = new Date(Date.now() - 7 * 86400000).toISOString();
    const count = execSync(
      `git log --oneline --since="${since}" 2>/dev/null | wc -l`,
      { cwd: path.join(__dirname, '..') }
    ).toString().trim();
    return parseInt(count) || 0;
  } catch {
    return 0;
  }
}

/**
 * Get the last commit message and timestamp.
 */
function getLastCommit() {
  try {
    const msg  = execSync('git log -1 --pretty="%s"',  { cwd: path.join(__dirname, '..') }).toString().trim();
    const time = execSync('git log -1 --pretty="%ci"', { cwd: path.join(__dirname, '..') }).toString().trim();
    return { message: msg, time: new Date(time).toISOString() };
  } catch {
    return { message: 'unknown', time: new Date().toISOString() };
  }
}

/**
 * Read version from package.json (if present).
 */
function getVersion() {
  try {
    const pkg = JSON.parse(fs.readFileSync(path.join(__dirname, '../package.json'), 'utf8'));
    return pkg.version || 'unknown';
  } catch {
    return 'unknown';
  }
}

// ── Read existing status (to preserve community data) ──
let existing = {};
try {
  existing = JSON.parse(fs.readFileSync(STATUS_PATH, 'utf8'));
} catch {
  // First run — no existing status yet
}

// ── Build new status ──
const lastCommit  = getLastCommit();
const commitCount = getCommitCount();
const version     = getVersion();

const status = {
  generatedAt: new Date().toISOString(),
  version,

  // ── Project identity ──
  // TODO: Customize these fields for your project.
  // They are used by build.html to populate the status panel and ticker.
  project: {
    name:        process.env.PROJECT_NAME    || 'MyProject',
    description: process.env.PROJECT_DESC    || 'A project being built in public.',
    born:        process.env.PROJECT_BORN    || new Date().toISOString(),
    status:      'building',       // building | thinking | offline
    statusText:  'Online · Building',
  },

  // ── Git stats (auto-generated) ──
  lastCommit,
  commitsThisWeek: commitCount,

  // ── Shipped log ──
  // Persist across runs from existing status.json.
  // Update this array manually, or write a separate script to manage it.
  shipped: existing.shipped || [
    // Example entries — replace with your own:
    // { date: 'Mar 01', text: 'Initial launch', type: 'build' },
    // { date: 'Mar 02', text: 'Dark mode', type: 'feature' },
    // { date: 'Mar 02', text: 'Fix login bug', type: 'fix' },
  ],

  // ── Up Next queue ──
  // Update manually to show what you're working on.
  queue: existing.queue || [
    // Example:
    // { num: '01', title: 'Feature Name', desc: 'What it does.' },
  ],

  // ── Community data (persisted) ──
  ideas:    existing.ideas    || [],
  projects: existing.projects || [],
};

// ── Write status.json to the public site repo ──
fs.mkdirSync(path.dirname(STATUS_PATH), { recursive: true });
fs.writeFileSync(STATUS_PATH, JSON.stringify(status, null, 2));

console.log('✅ status.json written to:', STATUS_PATH);
console.log('   Version:            ', version);
console.log('   Last commit:        ', lastCommit.message);
console.log('   Commits this week:  ', commitCount);
console.log('   Generated at:       ', status.generatedAt);
