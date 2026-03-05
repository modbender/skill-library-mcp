#!/usr/bin/env node
/**
 * bootstrap_config.js
 *
 * Create ~/.config/diy-pc-ingest/config.json by discovering Notion IDs via /v1/search.
 * Requires NOTION_API_KEY (or NOTION_TOKEN) and that the target data sources are shared with the integration.
 *
 * Usage:
 *   node scripts/bootstrap_config.js
 *   node scripts/bootstrap_config.js --out ~/.config/diy-pc-ingest/config.json
 *   node scripts/bootstrap_config.js --names pcconfig=PCConfig pcinput=PCInput storage=ストレージ enclosure=エンクロージャー
 */

import fs from 'fs';
import os from 'os';
import path from 'path';

const API = 'https://api.notion.com/v1';
const NOTION_VERSION = process.env.NOTION_VERSION || '2025-09-03';

function die(msg, code = 1) {
  process.stderr.write(String(msg) + '\n');
  process.exit(code);
}

function token() {
  const t = (process.env.NOTION_API_KEY || process.env.NOTION_TOKEN || '').trim();
  if (!t) die('Missing NOTION_API_KEY (or NOTION_TOKEN) environment variable.');
  return t;
}

async function req(method, p, body) {
  const res = await fetch(API + p, {
    method,
    headers: {
      'Authorization': `Bearer ${token()}`,
      'Notion-Version': NOTION_VERSION,
      'Content-Type': 'application/json',
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} ${p}: ${text}`);
  }
  return text ? JSON.parse(text) : {};
}

function plainTitle(obj) {
  const t = obj?.title || [];
  return t.map(x => x?.plain_text || '').join('').trim();
}

async function searchDataSources(query) {
  const body = { query, page_size: 50 };
  const j = await req('POST', '/search', body);
  const results = j.results || [];
  return results.filter(r => r && r.object === 'data_source');
}

async function resolveOneByName(wantName) {
  const hits = await searchDataSources(wantName);
  // Prefer exact title match
  const exact = hits.filter(h => plainTitle(h) === wantName);
  const cand = exact.length ? exact : hits;

  if (cand.length === 0) {
    die(`Notion data source not found via search: ${wantName}\n- Ensure the database is shared with your integration (Connect to).\n- Or rename it to match, or pass --names to adjust.`);
  }
  if (cand.length > 1) {
    const lines = cand.slice(0, 10).map(h => `- ${plainTitle(h)} (data_source_id=${h.id})`).join('\n');
    die(`Multiple matches for data source name: ${wantName}\n${lines}\nPlease disambiguate by renaming the DB or refining --names.`);
  }

  const ds = cand[0];
  const dsFull = await req('GET', `/data_sources/${ds.id}`);
  const databaseId = dsFull?.database_id;
  if (!databaseId) {
    die(`Could not resolve database_id for data_source_id=${ds.id}. Notion API response missing database_id.`);
  }
  return { data_source_id: ds.id, database_id: databaseId, title: plainTitle(ds) };
}

function parseArgs(argv) {
  const out = {
    outPath: path.join(os.homedir(), '.config', 'diy-pc-ingest', 'config.json'),
    names: {
      pcconfig: 'PCConfig',
      pcinput: 'PCInput',
      storage: 'ストレージ',
      enclosure: 'エンクロージャー',
    },
  };

  const args = argv.slice(2);
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === '--out') {
      out.outPath = args[++i];
      continue;
    }
    if (a === '--names') {
      // consume until next -- or end
      while (i + 1 < args.length && !args[i + 1].startsWith('--')) {
        const kv = args[++i];
        const [k, ...rest] = kv.split('=');
        const v = rest.join('=');
        if (!k || !v) die(`Invalid --names entry: ${kv}`);
        if (!(k in out.names)) die(`Unknown target for --names: ${k} (expected one of: pcconfig, pcinput, storage, enclosure)`);
        out.names[k] = v;
      }
      continue;
    }
    if (a === '--help' || a === '-h') {
      console.log('Usage: node scripts/bootstrap_config.js [--out PATH] [--names pcconfig=... pcinput=... storage=... enclosure=...]');
      process.exit(0);
    }
    die(`Unknown arg: ${a}`);
  }
  return out;
}

async function main() {
  const { outPath, names } = parseArgs(process.argv);

  const pcconfig = await resolveOneByName(names.pcconfig);
  const pcinput = await resolveOneByName(names.pcinput);
  const storage = await resolveOneByName(names.storage);
  const enclosure = await resolveOneByName(names.enclosure);

  const config = {
    notion: {
      version: NOTION_VERSION,
      targets: {
        pcconfig: { data_source_id: pcconfig.data_source_id, database_id: pcconfig.database_id, title_prop: 'Name', key: ['Name', 'Purchase Date'] },
        pcinput: { data_source_id: pcinput.data_source_id, database_id: pcinput.database_id, title_prop: '名前', key: ['型番', 'Serial', '名前'] },
        storage: { data_source_id: storage.data_source_id, database_id: storage.database_id, title_prop: 'Name', key: ['シリアル'] },
        enclosure: { data_source_id: enclosure.data_source_id, database_id: enclosure.database_id, title_prop: 'Name', key: ['取り外し表示名', 'Name'] },
      },
    },
  };

  const dir = path.dirname(outPath);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(outPath, JSON.stringify(config, null, 2), 'utf-8');

  console.log(JSON.stringify({
    ok: true,
    out: outPath,
    resolved: {
      pcconfig: { name: pcconfig.title, data_source_id: pcconfig.data_source_id, database_id: pcconfig.database_id },
      pcinput: { name: pcinput.title, data_source_id: pcinput.data_source_id, database_id: pcinput.database_id },
      storage: { name: storage.title, data_source_id: storage.data_source_id, database_id: storage.database_id },
      enclosure: { name: enclosure.title, data_source_id: enclosure.data_source_id, database_id: enclosure.database_id },
    }
  }, null, 2));
}

main().catch(err => die(err?.stack || err?.message || String(err)));
