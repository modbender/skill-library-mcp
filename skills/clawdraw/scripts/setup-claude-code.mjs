#!/usr/bin/env node
// @security-manifest
// env: none
// endpoints: none
// files: ~/.claude/skills/clawdraw/ (write on install), ~/.claude/agents/ (write on install)
// exec: none

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';

const pkgDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const claudeDir = path.join(os.homedir(), '.claude');

// Only register if Claude Code is installed — silently skip otherwise
if (!fs.existsSync(claudeDir)) process.exit(0);

const skillDir = path.join(claudeDir, 'skills', 'clawdraw');

try {
  fs.mkdirSync(skillDir, { recursive: true });
  // Replace {baseDir} so reference doc paths resolve to the npm package location
  const content = fs.readFileSync(path.join(pkgDir, 'SKILL.md'), 'utf-8')
    .replaceAll('{baseDir}', pkgDir);
  fs.writeFileSync(path.join(skillDir, 'SKILL.md'), content, 'utf-8');
  console.log('[clawdraw] Registered with Claude Code — skill available as /clawdraw');
  console.log('[clawdraw] First time? Run: clawdraw setup');
} catch (err) {
  // Non-critical — never fail the install
  console.log('[clawdraw] Claude Code registration skipped:', err.message);
}

// Install worker sub-agent definition
const agentsDir = path.join(claudeDir, 'agents');
try {
  fs.mkdirSync(agentsDir, { recursive: true });
  fs.copyFileSync(
    path.join(pkgDir, 'agents', 'clawdraw-worker.md'),
    path.join(agentsDir, 'clawdraw-worker.md')
  );
  console.log('[clawdraw] Installed clawdraw-worker agent definition');
} catch { /* skip silently if source missing */ }
