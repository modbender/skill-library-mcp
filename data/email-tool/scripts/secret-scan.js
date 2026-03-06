#!/usr/bin/env node
/*
  Simple secret scanner for skills.
  Usage: node scripts/secret-scan.js

  Exits non-zero if it detects likely secrets in the skill folder.
*/

const fs = require('fs');
const path = require('path');

const SKILL_ROOT = path.resolve(__dirname, '..');

const IGNORE_DIRS = new Set(['node_modules', '.git', 'dist']);

const PATTERNS = [
  /EMAIL_PASS\s*[:=]/i,
  /API[_-]?KEY\s*[:=]/i,
  /SECRET\s*[:=]/i,
  /TOKEN\s*[:=]/i,
  /password\s*[:=]/i,
  /pass\s*[:=]/i,
  /"pass"\s*:\s*"[^\"]+"/i,
  /-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----/,
];

function walk(dir, out = []) {
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ent.isDirectory()) {
      if (IGNORE_DIRS.has(ent.name)) continue;
      walk(path.join(dir, ent.name), out);
    } else if (ent.isFile()) {
      out.push(path.join(dir, ent.name));
    }
  }
  return out;
}

function isTextFile(p) {
  // quick heuristic
  const ex = path.extname(p).toLowerCase();
  return [
    '.md', '.js', '.ts', '.json', '.yml', '.yaml', '.txt', '.env', '.py', '.ps1', '.sh'
  ].includes(ex);
}

const files = walk(SKILL_ROOT).filter(isTextFile);

let hits = [];
for (const f of files) {
  const rel = path.relative(SKILL_ROOT, f);
  const content = fs.readFileSync(f, 'utf8');
  const lines = content.split(/\r?\n/);

  lines.forEach((line, i) => {
    for (const re of PATTERNS) {
      if (re.test(line)) {
        hits.push({ file: rel, line: i + 1, text: line.trim().slice(0, 200) });
      }
    }
  });
}

if (hits.length) {
  console.error('Potential secrets detected. Refusing to proceed.');
  for (const h of hits.slice(0, 50)) {
    console.error(`- ${h.file}:${h.line} :: ${h.text}`);
  }
  process.exit(2);
}

console.log('Secret scan passed: no obvious secrets found.');
