import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const skillRoot = path.resolve(__dirname, '..');

function read(relativePath) {
  return fs.readFileSync(path.join(skillRoot, relativePath), 'utf8');
}

test('SKILL.md documents phase-1 tokenization endpoint flow', () => {
  const content = read('SKILL.md');

  assert.match(content, /Series Tokenization \(Phase 1, Agent-Driven\)/i);
  assert.match(content, /POST \/api\/v1\/series\/:seriesId\/tokenization\/open/);
  assert.match(content, /POST \/api\/v1\/series\/:seriesId\/tokenization\/platform-fee\/pay/);
  assert.match(content, /POST \/api\/v1\/series\/:seriesId\/tokenization\/launch\/prepare/);
  assert.match(content, /POST \/api\/v1\/series\/:seriesId\/tokenization\/launch\/submit/);
  assert.match(content, /402.*X-PAYMENT/i);
  assert.match(content, /Never ask for private keys or seed phrases/i);
});

test('PLATFORM_API.md lists tokenization endpoints', () => {
  const content = read('PLATFORM_API.md');

  assert.match(content, /Series Tokenization \(Phase 1\)/i);
  assert.match(content, /GET \/api\/v1\/series\/:seriesId\/tokenization\/claimable\?wallet=\.\.\./);
  assert.match(content, /POST \/api\/v1\/series\/:seriesId\/tokenization\/claim\/prepare/);
  assert.match(content, /POST \/api\/v1\/series\/:seriesId\/tokenization\/claim\/submit/);
});
