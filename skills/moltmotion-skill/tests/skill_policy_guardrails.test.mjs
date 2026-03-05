import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const skillRoot = path.resolve(__dirname, '..');

const skillFiles = [
  path.join(skillRoot, 'SKILL.md'),
  path.join(skillRoot, 'skills', 'molt-motion', 'SKILL.md'),
];

function read(filePath) {
  return fs.readFileSync(filePath, 'utf8');
}

function section(content, startHeading, endHeading) {
  const start = content.indexOf(startHeading);
  const end = content.indexOf(endHeading);
  assert.notEqual(start, -1, `Missing heading: ${startHeading}`);
  assert.notEqual(end, -1, `Missing heading: ${endHeading}`);
  assert.ok(end > start, `${endHeading} must appear after ${startHeading}`);
  return content.slice(start, end).trim();
}

test('skill docs block broad always-use trigger language', () => {
  const bannedPatterns = [
    /Trigger Keywords \(Always Use This Skill\)/i,
    /\*\*always\*\* use this skill/i,
    /Proceeding with registration now/i,
    /Do not wait for user permission/i,
    /register immediately/i,
  ];

  for (const filePath of skillFiles) {
    const content = read(filePath);
    for (const pattern of bannedPatterns) {
      assert.equal(
        pattern.test(content),
        false,
        `Unexpected unsafe pattern ${pattern} in ${path.relative(skillRoot, filePath)}`
      );
    }
  }
});

test('skill docs require hard opt-in for registration and writes', () => {
  for (const filePath of skillFiles) {
    const content = read(filePath);
    assert.match(content, /Onboarding Flow \(Hard Opt-In\)/);
    assert.match(content, /Never execute network registration calls .* explicit user confirmation/i);
    assert.match(content, /Use the \*\*simplified registration endpoint\*\* only after explicit user confirmation/i);
    assert.match(content, /Prefer `MOLTMOTION_API_KEY` from environment at runtime\./);
    assert.match(content, /Ask for explicit confirmation before writing credentials or state files\./i);
    assert.match(content, /Never print full API keys or credential file contents in chat\/logs\./i);
  }
});

test('onboarding and security sections remain synchronized across duplicated skill docs', () => {
  const [rootSkill, nestedSkill] = skillFiles.map(read);
  const rootSection = section(rootSkill, '## When to use this skill', '## Creating a Studio');
  const nestedSection = section(nestedSkill, '## When to use this skill', '## Creating a Studio');
  assert.equal(nestedSection, rootSection);
});
