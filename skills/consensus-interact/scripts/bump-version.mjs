#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const repoRoot = process.cwd();
const mode = process.argv[2] ?? 'patch';
const explicit = process.argv[3];

const files = ['package.json', '_meta.json', 'metadata.json'];

function parse(v) {
  const m = /^(\d+)\.(\d+)\.(\d+)$/.exec(v);
  if (!m) throw new Error(`Invalid semver: ${v}`);
  return { major: Number(m[1]), minor: Number(m[2]), patch: Number(m[3]) };
}

function fmt({ major, minor, patch }) {
  return `${major}.${minor}.${patch}`;
}

function next(v, m) {
  const s = parse(v);
  if (m === 'patch') return fmt({ ...s, patch: s.patch + 1 });
  if (m === 'minor') return fmt({ ...s, minor: s.minor + 1, patch: 0 });
  if (m === 'major') return fmt({ major: s.major + 1, minor: 0, patch: 0 });
  throw new Error(`Unknown bump mode: ${m}`);
}

const data = Object.fromEntries(files.map((f) => [f, JSON.parse(fs.readFileSync(path.join(repoRoot, f), 'utf8'))]));
const current = [data['package.json'].version, data['_meta.json'].version, data['metadata.json'].version];
if (new Set(current).size !== 1) {
  throw new Error(`Version mismatch before bump: ${JSON.stringify(current)}`);
}

const from = current[0];
const to = explicit ?? next(from, mode);
parse(to);

for (const f of files) {
  data[f].version = to;
  fs.writeFileSync(path.join(repoRoot, f), `${JSON.stringify(data[f], null, 2)}\n`);
}

console.log(`bumped ${from} -> ${to}`);
