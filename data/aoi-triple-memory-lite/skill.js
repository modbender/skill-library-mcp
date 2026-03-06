#!/usr/bin/env node
/**
 * AOI Triple Memory (Lite)
 * S-DNA: AOI-2026-0215-SDNA-MEM01
 */

import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const __sdna__ = {
  protocol: 'aoineco-sdna-v1',
  id: 'AOI-2026-0215-SDNA-MEM01',
  org: 'aoineco-co',
  classification: 'public-safe',
};

function die(msg, code = 1) {
  console.error(msg);
  process.exit(code);
}

function parseArgs(argv) {
  const [cmd, ...rest] = argv;
  const args = {};
  for (let i = 0; i < rest.length; i++) {
    const a = rest[i];
    if (!a.startsWith('--')) continue;
    const key = a.slice(2);
    const next = rest[i + 1];
    if (next && !next.startsWith('--')) {
      args[key] = next;
      i++;
    } else {
      args[key] = 'true';
    }
  }
  return { cmd, args };
}

function workspaceRoot() {
  // best-effort: assume this skill is run from within workspace
  return process.env.WORKSPACE || process.cwd();
}

function search({ q, n }) {
  if (!q) die('--q required');
  const limit = Number(n || 20);
  const root = workspaceRoot();
  const res = spawnSync('rg', ['-n', q, root], { encoding: 'utf8' });
  const out = (res.stdout || '').split('\n').filter(Boolean).slice(0, limit);
  console.log(JSON.stringify({ __sdna__, kind: 'search', q, results: out }, null, 2));
}

function newNote({ title, tag }) {
  if (!title) die('--title required');
  const root = workspaceRoot();
  const safe = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 80) || 'note';
  const dir = path.join(root, 'context');
  fs.mkdirSync(dir, { recursive: true });
  const file = path.join(dir, `${safe}.md`);
  const tags = (tag || '').split(',').map(s => s.trim()).filter(Boolean);

  const body = `# ${title}\n\n` +
    `- Tags: ${tags.map(t => `\`${t}\``).join(' ')}\n` +
    `- Date: ${new Date().toISOString()}\n\n` +
    `## Decision\n- \n\n## Rationale\n- \n\n## Next actions\n- \n`;

  fs.writeFileSync(file, body, 'utf8');
  console.log(JSON.stringify({ __sdna__, kind: 'new-note', file }, null, 2));
}

function help() {
  console.log(JSON.stringify({
    __sdna__,
    usage: {
      search: 'aoi-memory search --q "text" --n 20',
      newNote: 'aoi-memory new-note --title "..." --tag a,b,c'
    }
  }, null, 2));
}

function main() {
  const { cmd, args } = parseArgs(process.argv.slice(2));
  if (!cmd || ['help', '-h', '--help'].includes(cmd)) return help();
  if (cmd === 'search') return search({ q: args.q, n: args.n });
  if (cmd === 'new-note') return newNote({ title: args.title, tag: args.tag });
  die(`Unknown command: ${cmd}`);
}

main();
