import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const skillRoot = path.resolve(__dirname, '..');

function read(relPath) {
  return fs.readFileSync(path.join(skillRoot, relPath), 'utf8');
}

test('local skill copy has expected core files', () => {
  const required = [
    'SKILL.md',
    'README.md',
    'JOBS.md',
    'HEARTBEAT.md',
    'AI-SELF-IMPROVEMENT.md',
    path.join('references', 'api.md'),
    path.join('scripts', 'consensus_quickstart.sh')
  ];

  for (const rel of required) {
    const full = path.join(skillRoot, rel);
    assert.equal(fs.existsSync(full), true, `missing ${rel}`);
  }
});

test('README references local docs (not stale /public paths)', () => {
  const readme = read('README.md');
  assert.ok(!readme.includes('/public/'), 'README still references /public paths');
  assert.match(readme, /SKILL\.md/);
  assert.match(readme, /JOBS\.md/);
  assert.match(readme, /AI-SELF-IMPROVEMENT\.md/);
});

test('quickstart uses supported default consensus policy key', () => {
  const script = read(path.join('scripts', 'consensus_quickstart.sh'));
  assert.ok(!script.includes('"type": "SINGLE_WINNER"'), 'deprecated policy SINGLE_WINNER found');
  assert.ok(script.includes('"type": "FIRST_SUBMISSION_WINS"'), 'missing FIRST_SUBMISSION_WINS default policy');
});
