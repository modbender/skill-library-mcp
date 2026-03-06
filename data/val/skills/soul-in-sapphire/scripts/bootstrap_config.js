#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import { httpJson, expandHome } from './ltm_common.js';

function parseArgs(argv) {
  const out = { name: '', out: '~/.config/soul-in-sapphire/config.json' };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--name') out.name = argv[++i] || '';
    else if (a === '--out') out.out = argv[++i] || out.out;
  }
  return out;
}

function plainTitle(obj) {
  const parts = obj?.title || [];
  return parts.map(p => p?.plain_text || '').join('').trim();
}

function resolveOne(name) {
  const res = httpJson('POST', '/search', { query: name, page_size: 50 });
  const results = res?.results || [];
  const ds = results.filter(r => r.object === 'data_source' && plainTitle(r) === name);
  const db = results.filter(r => r.object === 'database' && plainTitle(r) === name);
  if (ds.length !== 1 || db.length !== 1) {
    throw new Error(`Notion database/data_source exact match failed for: ${name}`);
  }
  return { ltm_db_name: name, data_source_id: ds[0].id, database_id: db[0].id };
}

function main() {
  const { name, out } = parseArgs(process.argv);
  if (!name) throw new Error('Missing --name');
  const cfg = resolveOne(name);
  const outPath = expandHome(out);
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, JSON.stringify(cfg, null, 2) + '\n', 'utf-8');
  console.log(JSON.stringify({ ok: true, out: outPath, config: cfg }, null, 2));
}

try { main(); } catch (e) { console.error(String(e?.stack || e)); process.exit(1); }
