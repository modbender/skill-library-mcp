#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const distDir = path.join(root, 'dist');

function fail(message) {
  console.error(`[verify:release] ${message}`);
  process.exit(1);
}

if (!fs.existsSync(distDir)) {
  fail('dist/ is missing. Run npm run build first.');
}

const bannedFiles = [
  'config-v1.js',
  'config-v1.d.ts',
  'index-v1.js',
  'index-v1.d.ts',
  'store-v1.js',
  'store-v1.d.ts',
  'embeddings.js',
  'embeddings.d.ts',
];

for (const rel of bannedFiles) {
  if (fs.existsSync(path.join(distDir, rel))) {
    fail(`legacy artifact found in dist: ${rel}`);
  }
}

const bannedPatterns = [
  /from ['"]openai['"]/i,
  /from ['"]@lancedb\/lancedb['"]/i,
  /OPENAI_API_KEY/i,
  /embedding\s*:\s*\{\s*apiKey/i,
];

const files = fs.readdirSync(distDir).filter(f => f.endsWith('.js') || f.endsWith('.d.ts'));
for (const file of files) {
  const fullPath = path.join(distDir, file);
  const content = fs.readFileSync(fullPath, 'utf8');
  for (const pattern of bannedPatterns) {
    if (pattern.test(content)) {
      fail(`banned pattern ${pattern} found in dist/${file}`);
    }
  }
}

console.log('[verify:release] OK');
