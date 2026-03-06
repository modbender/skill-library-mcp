#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const SKILL_NAME = 'shelter';
const FILES_TO_COPY = ['SKILL.md'];
const DIRS_TO_COPY = ['references'];

// Determine install location: project-level if inside node_modules, else global
const isProjectInstall = __dirname.includes('node_modules');
const skillDir = isProjectInstall
  ? path.join(process.cwd(), '.claude', 'skills', SKILL_NAME)
  : path.join(require('os').homedir(), '.claude', 'skills', SKILL_NAME);

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

try {
  fs.mkdirSync(skillDir, { recursive: true });

  for (const file of FILES_TO_COPY) {
    const src = path.join(__dirname, file);
    if (fs.existsSync(src)) {
      fs.copyFileSync(src, path.join(skillDir, file));
    }
  }

  for (const dir of DIRS_TO_COPY) {
    const src = path.join(__dirname, dir);
    if (fs.existsSync(src)) {
      copyDir(src, path.join(skillDir, dir));
    }
  }

  console.log(`Shelter skill installed to ${skillDir}`);
  console.log('');
  console.log('Setup:');
  console.log('  1. Create an API key at https://shelter.money/settings/api-keys');
  console.log('  2. Set the environment variable:');
  console.log('     export SHELTER_API_KEY="wv_your_key_here"');
  console.log('');
} catch (err) {
  console.error('Failed to install Shelter skill:', err.message);
}
