#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const repoRoot = process.cwd();

const mustExist = [
  'SKILL.md',
  'README.md',
  'JOBS.md',
  'HEARTBEAT.md',
  'AI-SELF-IMPROVEMENT.md',
  '_meta.json',
  'metadata.json',
  'package.json',
  path.join('references', 'api.md'),
  path.join('scripts', 'consensus_quickstart.sh')
];

const forbiddenNested = [
  path.join('consensus-interact', 'SKILL.md'),
  path.join('consensus-interact', 'README.md'),
  path.join('consensus-interact', 'JOBS.md'),
  path.join('consensus-interact', 'HEARTBEAT.md'),
  path.join('consensus-interact', 'AI-SELF-IMPROVEMENT.md')
];

function fail(msg) {
  console.error(`❌ ${msg}`);
  process.exitCode = 1;
}

for (const rel of mustExist) {
  if (!fs.existsSync(path.join(repoRoot, rel))) {
    fail(`Missing required file: ${rel}`);
  }
}

for (const rel of forbiddenNested) {
  if (fs.existsSync(path.join(repoRoot, rel))) {
    fail(`Nested duplicate layout detected: ${rel}`);
  }
}

const pkg = JSON.parse(fs.readFileSync(path.join(repoRoot, 'package.json'), 'utf8'));
const meta = JSON.parse(fs.readFileSync(path.join(repoRoot, '_meta.json'), 'utf8'));
const metadata = JSON.parse(fs.readFileSync(path.join(repoRoot, 'metadata.json'), 'utf8'));

const versions = {
  package: pkg.version,
  _meta: meta.version,
  metadata: metadata.version
};

if (!(versions.package && versions._meta && versions.metadata)) {
  fail(`Missing version in one of package.json/_meta.json/metadata.json: ${JSON.stringify(versions)}`);
}

if (new Set(Object.values(versions)).size !== 1) {
  fail(`Version mismatch: ${JSON.stringify(versions)}`);
}

function walk(dir) {
  const out = [];
  for (const item of fs.readdirSync(dir, { withFileTypes: true })) {
    if (item.name === '.git' || item.name === 'node_modules') continue;
    const full = path.join(dir, item.name);
    if (item.isDirectory()) out.push(...walk(full));
    else out.push(full);
  }
  return out;
}

const conflictMarkerRegex = /^(<{7} .*|={7}|>{7} .*)$/m;
const textExt = new Set(['.md', '.json', '.yaml', '.yml', '.mjs', '.js', '.sh', '.txt']);
for (const file of walk(repoRoot)) {
  const ext = path.extname(file).toLowerCase();
  if (!textExt.has(ext)) continue;
  const content = fs.readFileSync(file, 'utf8');
  if (conflictMarkerRegex.test(content)) {
    fail(`Merge conflict marker found in ${path.relative(repoRoot, file)}`);
  }
}

if (!process.exitCode) {
  console.log('✅ CI guardrails passed');
}
