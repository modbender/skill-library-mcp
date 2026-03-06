import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const skillRoot = path.resolve(__dirname, '..');

function walk(dirPath) {
  const entries = fs.readdirSync(dirPath, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    const fullPath = path.join(dirPath, entry.name);
    if (entry.isDirectory()) {
      files.push(...walk(fullPath));
      continue;
    }
    files.push(fullPath);
  }

  return files;
}

test('repo contains a single canonical MoltMotion skill definition', () => {
  const matches = walk(skillRoot)
    .filter((filePath) => path.basename(filePath) === 'SKILL.md')
    .filter((filePath) => fs.readFileSync(filePath, 'utf8').includes('name: moltmotion-skill'))
    .map((filePath) => path.relative(skillRoot, filePath))
    .sort();

  assert.deepEqual(matches, ['SKILL.md']);
});

test('eval sources reference only the canonical skill id', () => {
  const filesToCheck = [
    path.join(skillRoot, 'evals', 'run-evals.mjs'),
    path.join(skillRoot, 'evals', 'analyze-artifacts.mjs'),
    path.join(skillRoot, 'evals', 'README.md'),
    path.join(skillRoot, 'evals', 'style-rubric.schema.json'),
  ];

  for (const filePath of filesToCheck) {
    const content = fs.readFileSync(filePath, 'utf8');
    assert.doesNotMatch(content, /moltmotion-production-assistant/);
  }
});
