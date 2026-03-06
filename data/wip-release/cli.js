#!/usr/bin/env node

/**
 * wip-release/cli.mjs
 * Release tool CLI. Bumps version, updates docs, publishes.
 */

import { release, detectCurrentVersion } from './core.mjs';

const args = process.argv.slice(2);
const level = args.find(a => ['patch', 'minor', 'major'].includes(a));

function flag(name) {
  const prefix = `--${name}=`;
  const found = args.find(a => a.startsWith(prefix));
  return found ? found.slice(prefix.length) : null;
}

const dryRun = args.includes('--dry-run');
const noPublish = args.includes('--no-publish');
const notes = flag('notes');

if (!level || args.includes('--help') || args.includes('-h')) {
  const cwd = process.cwd();
  let current = '';
  try { current = ` (current: ${detectCurrentVersion(cwd)})`; } catch {}

  console.log(`wip-release ... local release tool${current}

Usage:
  wip-release patch                    1.0.0 -> 1.0.1
  wip-release minor                    1.0.0 -> 1.1.0
  wip-release major                    1.0.0 -> 2.0.0

Flags:
  --notes="description"    Changelog entry text
  --dry-run                Show what would happen, change nothing
  --no-publish             Bump + tag only, skip npm/GitHub

Pipeline:
  1. Bump package.json version
  2. Sync SKILL.md version (if exists)
  3. Update CHANGELOG.md
  4. Git commit + tag
  5. Push to remote
  6. npm publish (via 1Password)
  7. GitHub Packages publish
  8. GitHub release create`);
  process.exit(level ? 0 : 1);
}

release({
  repoPath: process.cwd(),
  level,
  notes,
  dryRun,
  noPublish,
}).catch(err => {
  console.error(`  ✗ ${err.message}`);
  process.exit(1);
});
