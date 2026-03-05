#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const SKILL_NAME = 'shelter';

const isProjectInstall = __dirname.includes('node_modules');
const skillDir = isProjectInstall
  ? path.join(process.cwd(), '.claude', 'skills', SKILL_NAME)
  : path.join(require('os').homedir(), '.claude', 'skills', SKILL_NAME);

try {
  if (fs.existsSync(skillDir)) {
    fs.rmSync(skillDir, { recursive: true, force: true });
    console.log(`Shelter skill removed from ${skillDir}`);
  }
} catch (err) {
  console.error('Failed to uninstall Shelter skill:', err.message);
}
