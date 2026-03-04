#!/usr/bin/env node
/**
 * Apply JSONL records to DIY_PC Notion tables (JS version).
 *
 * This is a port of notion_apply_records.py. It is intentionally deterministic:
 * - reads JSONL from stdin
 * - upserts by configured keys
 * - patches only missing fields unless overwrite=true
 *
 * Config:
 * - DIY_PC_INGEST_CONFIG (path) OR ~/.config/diy-pc-ingest/config.json
 * - Notion token: NOTION_API_KEY (or NOTION_TOKEN) env, else NOTION_API_KEY_FILE, else ~/.config/notion/api_key
 * - Notion version: NOTION_VERSION env or default 2025-09-03
 */

import fs from 'fs';
import os from 'os';
import path from 'path';

const API = 'https://api.notion.com/v1';
const DEFAULT_NOTION_VERSION = '2025-09-03';

function die(msg) {
  process.stderr.write(String(msg) + '\n');
  process.exit(1);
}

function readJsonFile(p) {
  try {
    return JSON.parse(fs.readFileSync(p, 'utf-8'));
  } catch {
    return null;
  }
}


async function bootstrapConfig(outPath) {
  // Inline bootstrap (same behavior as scripts/bootstrap_config.js) to keep a single entrypoint.
  const names = {
    pcconfig: 'PCConfig',
    pcinput: 'PCInput',
    storage: 'ストレージ',
    enclosure: 'エンクロージャー',
  };

  async function searchDataSources(query) {
    const j = await notionReq({}, 'POST', '/search', { query, page_size: 50 });
    const results = j.results || [];
    return results.filter(r => r && r.object === 'data_source');
  }

  function plainTitle(obj) {
    const t = obj?.title || [];
    return t.map(x => x?.plain_text || '').join('').trim();
  }

  async function resolveOneByName(wantName) {
    const hits = await searchDataSources(wantName);
    const exact = hits.filter(h => plainTitle(h) === wantName);
    const cand = exact.length ? exact : hits;

    if (cand.length === 0) {
      die(`Notion data source not found via search: ${wantName}\n- Ensure the database is shared with your integration (Connect to).`);
    }
    if (cand.length > 1) {
      const lines = cand.slice(0, 10).map(h => `- ${plainTitle(h)} (data_source_id=${h.id})`).join('\n');
      die(`Multiple matches for data source name: ${wantName}\n${lines}\nPlease disambiguate by renaming the DB.`);
    }

    const ds = cand[0];
    const dsFull = await notionReq({}, 'GET', `/data_sources/${ds.id}`);
    const databaseId = dsFull?.database_id;
    if (!databaseId) die(`Could not resolve database_id for data_source_id=${ds.id}`);
    return { data_source_id: ds.id, database_id: databaseId, title: plainTitle(ds) };
  }

  const pcconfig = await resolveOneByName(names.pcconfig);
  const pcinput = await resolveOneByName(names.pcinput);
  const storage = await resolveOneByName(names.storage);
  const enclosure = await resolveOneByName(names.enclosure);

  const config = {
    notion: {
      version: process.env.NOTION_VERSION || '2025-09-03',
      targets: {
        pcconfig: { data_source_id: pcconfig.data_source_id, database_id: pcconfig.database_id, title_prop: 'Name', key: ['Name', 'Purchase Date'] },
        pcinput: { data_source_id: pcinput.data_source_id, database_id: pcinput.database_id, title_prop: '名前', key: ['型番', 'Serial', '名前'] },
        storage: { data_source_id: storage.data_source_id, database_id: storage.database_id, title_prop: 'Name', key: ['シリアル'] },
        enclosure: { data_source_id: enclosure.data_source_id, database_id: enclosure.database_id, title_prop: 'Name', key: ['取り外し表示名', 'Name'] },
      },
    },
  };

  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, JSON.stringify(config, null, 2), 'utf-8');
  return config;
}
async function loadConfig() {
  let p = process.env.DIY_PC_INGEST_CONFIG;
  if (!p) p = path.join(os.homedir(), '.config', 'diy-pc-ingest', 'config.json');
  if (!fs.existsSync(p)) {
    // Auto-bootstrap: discover Notion IDs via /v1/search when config is missing.
    // Requires NOTION_API_KEY and that target DBs are shared with the integration.
    const cfg = await bootstrapConfig(p);
    return cfg;
  }
  return readJsonFile(p) || {};
}

function notionVersion(cfg) {
  return (cfg?.notion?.version || process.env.NOTION_VERSION || DEFAULT_NOTION_VERSION).trim();
}

function notionApiKey(cfg) {
  const envTok = (process.env.NOTION_API_KEY || process.env.NOTION_TOKEN || '').trim();
  if (envTok) return envTok;

  const inlineTok = (cfg?.notion?.api_key || '').trim();
  if (inlineTok && !inlineTok.includes('PUT_YOUR_')) return inlineTok;

  const keyPath = (process.env.NOTION_API_KEY_FILE || path.join(os.homedir(), '.config', 'notion', 'api_key'));
  if (!fs.existsSync(keyPath)) {
    die(`Notion api_key not found: ${keyPath}. Set NOTION_API_KEY env (recommended) or create the file.`);
  }
  const key = fs.readFileSync(keyPath, 'utf-8').trim();
  if (!key) die(`Notion api_key empty: ${keyPath}`);
  return key;
}

function idsFromConfig(cfg) {
  const t = cfg?.notion?.targets || {};
  // Public-safe default structure: users must fill IDs.
  const defaults = {
    pcconfig: { data_source_id: null, database_id: null, title_prop: 'Name', key: ['Name', 'Purchase Date'] },
    pcinput: { data_source_id: null, database_id: null, title_prop: '名前', key: ['型番', 'Serial', '名前'] },
    storage: { data_source_id: null, database_id: null, title_prop: 'Name', key: ['シリアル'] },
    enclosure: { data_source_id: null, database_id: null, title_prop: 'Name', key: ['取り外し表示名', 'Name'] },
  };

  const out = { ...defaults };
  for (const [k, v] of Object.entries(t)) {
    if (!v || typeof v !== 'object') continue;
    out[k] = {
      data_source_id: v.data_source_id ?? out[k]?.data_source_id ?? null,
      database_id: v.database_id ?? out[k]?.database_id ?? null,
      title_prop: v.title_prop ?? out[k]?.title_prop ?? 'Name',
      key: Array.isArray(v.key) ? v.key : (out[k]?.key ?? []),
    };
  }
  return out;
}

async function notionReq(cfg, method, apiPath, body) {
  const url = API + apiPath;
  const headers = {
    'Authorization': `Bearer ${notionApiKey(cfg)}`,
    'Notion-Version': notionVersion(cfg),
  };
  let payload;
  if (body !== undefined && body !== null) {
    headers['Content-Type'] = 'application/json';
    payload = JSON.stringify(body);
  }
  const res = await fetch(url, { method, headers, body: payload });
  const text = await res.text();
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} ${apiPath}: ${text}`);
  }
  return text ? JSON.parse(text) : {};
}

function normalize(s) {
  return String(s ?? '').trim().replace(/\s+/g, ' ');
}

function propPlainText(prop) {
  if (!prop) return '';
  const t = prop.type;
  if (t === 'title' || t === 'rich_text') {
    const arr = prop[t] || [];
    return arr.map(x => x?.plain_text || '').join('').trim();
  }
  return '';
}

function propDateStart(prop) {
  if (!prop || prop.type !== 'date') return null;
  return prop.date?.start ?? null;
}

function propNumber(prop) {
  if (!prop || prop.type !== 'number') return null;
  return prop.number;
}

function getValueFromRow(row, propName) {
  const props = row?.properties || {};
  const p = props[propName];
  if (!p) return null;
  const t = p.type;
  if (t === 'title' || t === 'rich_text') return propPlainText(p);
  if (t === 'date') return propDateStart(p);
  if (t === 'number') return propNumber(p);
  if (t === 'select') return p.select?.name ?? null;
  if (t === 'status') return p.status?.name ?? null;
  if (t === 'url') return p.url ?? null;
  return null;
}

async function queryByTitle(cfg, dataSourceId, titleProp, contains, pageSize = 10) {
  const body = { page_size: pageSize, filter: { property: titleProp, title: { contains } } };
  const j = await notionReq(cfg, 'POST', `/data_sources/${dataSourceId}/query`, body);
  return j.results || [];
}

async function queryByRichText(cfg, dataSourceId, prop, contains, pageSize = 10) {
  const body = { page_size: pageSize, filter: { property: prop, rich_text: { contains } } };
  const j = await notionReq(cfg, 'POST', `/data_sources/${dataSourceId}/query`, body);
  return j.results || [];
}

function buildProp(schemaProp, value) {
  const t = schemaProp?.type;
  if (!t) return null;

  if (t === 'title') {
    return { title: [{ type: 'text', text: { content: String(value) } }] };
  }
  if (t === 'rich_text') {
    return { rich_text: [{ type: 'text', text: { content: String(value) } }] };
  }
  if (t === 'number') {
    if (value === null || value === undefined || value === '') return { number: null };
    return { number: Number(value) };
  }
  if (t === 'date') {
    if (!value) return { date: null };
    return { date: { start: String(value) } };
  }
  if (t === 'checkbox') {
    return { checkbox: Boolean(value) };
  }
  if (t === 'select') {
    if (value === null || value === undefined || String(value).trim() === '') return { select: null };
    return { select: { name: String(value) } };
  }
  if (t === 'status') {
    if (value === null || value === undefined || String(value).trim() === '') return { status: null };
    return { status: { name: String(value) } };
  }
  if (t === 'multi_select') {
    let names = [];
    if (Array.isArray(value)) names = value.map(v => String(v).trim()).filter(Boolean);
    else if (typeof value === 'string') names = value.split(',').map(v => v.trim()).filter(Boolean);
    return { multi_select: names.map(n => ({ name: n })) };
  }
  if (t === 'relation') {
    const ids = Array.isArray(value) ? value : [];
    return { relation: ids.map(pid => ({ id: pid })) };
  }
  if (t === 'url') {
    if (!value) return { url: null };
    return { url: String(value) };
  }

  return null;
}

function patchSkipsExisting(ep) {
  if (!ep) return false;
  const et = ep.type;
  if (et === 'rich_text' || et === 'title') {
    const arr = ep[et] || [];
    return arr.some(x => (x?.plain_text || '').trim());
  }
  if (et === 'number') return ep.number !== null && ep.number !== undefined;
  if (et === 'date') return Boolean(ep.date?.start);
  if (et === 'checkbox') return ep.checkbox === true;
  if (et === 'select') return Boolean(ep.select?.name);
  if (et === 'status') return Boolean(ep.status?.name);
  if (et === 'multi_select') return (ep.multi_select || []).length > 0;
  if (et === 'relation') return (ep.relation || []).length > 0;
  if (et === 'url') return Boolean(ep.url);
  return false;
}

function buildPatch(schema, incoming, existingProps, overwrite) {
  const out = {};
  const schProps = schema?.properties || {};

  for (const [k, v] of Object.entries(incoming || {})) {
    if (!(k in schProps)) continue;
    const schemaProp = schProps[k];

    if (!overwrite) {
      const ep = existingProps?.[k];
      if (patchSkipsExisting(ep)) continue;
    }

    const built = buildProp(schemaProp, v);
    if (built !== null) out[k] = built;
  }

  return out;
}

async function findExisting(cfg, ids, target, schema, propsIn) {
  const tcfg = ids[target];
  const ds = tcfg.data_source_id;
  const schProps = schema?.properties || {};
  const keyProps = Array.from(tcfg.key || []);

  // composite key
  if (keyProps.length >= 2 && keyProps.every(k => propsIn?.[k])) {
    const first = keyProps[0];
    const firstSchema = schProps[first] || {};
    const firstType = firstSchema.type;
    const firstVal = normalize(propsIn[first]);

    let hits = [];
    if (firstType === 'title') hits = await queryByTitle(cfg, ds, first, firstVal, 25);
    else if (firstType === 'rich_text') hits = await queryByRichText(cfg, ds, first, firstVal, 25);

    const narrowed = hits.filter(row => {
      for (const k of keyProps) {
        const wantRaw = propsIn[k];
        if (wantRaw === null || wantRaw === undefined || wantRaw === '') return false;
        const got = getValueFromRow(row, k);
        const want = typeof wantRaw === 'string' ? normalize(wantRaw) : String(wantRaw);
        const gotN = typeof got === 'string' ? normalize(got) : (got === null || got === undefined ? null : String(got));
        if (gotN !== want) return false;
      }
      return true;
    });

    if (narrowed.length === 1) return narrowed[0];
    return null;
  }

  // single-key legacy
  for (const keyProp of keyProps) {
    const v0 = propsIn?.[keyProp];
    if (!v0) continue;
    const v = normalize(v0);
    if (!v) continue;
    const schemaProp = schProps[keyProp];
    if (!schemaProp) continue;

    let hits = [];
    if (schemaProp.type === 'rich_text') hits = await queryByRichText(cfg, ds, keyProp, v, 10);
    else if (schemaProp.type === 'title') hits = await queryByTitle(cfg, ds, keyProp, v, 10);

    if (hits.length === 1) return hits[0];
  }

  // storage safe fallback: title + (optional) purchase date/price
  if (target === 'storage') {
    const title = propsIn?.Name || propsIn?.名前;
    if (!title) return null;
    const titleN = normalize(title);
    const hits = await queryByTitle(cfg, ds, tcfg.title_prop, titleN, 10);
    if (!hits || hits.length === 0) return null;

    const wantDate = propsIn?.['購入日'];
    const wantPrice = propsIn?.['価格(円)'];

    function ok(row) {
      const props = row?.properties || {};
      if (wantDate) {
        const got = propDateStart(props['購入日']);
        if (String(got) !== String(wantDate)) return false;
      }
      if (wantPrice !== null && wantPrice !== undefined) {
        const got = propNumber(props['価格(円)']);
        if (got === null || got === undefined) return false;
        if (Number(got) !== Number(wantPrice)) return false;
      }
      return true;
    }

    const narrowed = hits.filter(ok);
    if (narrowed.length === 1) return narrowed[0];

    if (hits.length === 1) {
      const serial = propPlainText((hits[0].properties || {})['シリアル']);
      if (!serial) return hits[0];
    }
  }

  return null;
}

async function createPage(cfg, ids, target, schema, title, properties) {
  const tcfg = ids[target];
  const titleProp = tcfg.title_prop;
  const schProps = schema?.properties || {};

  const outProps = {};
  if (title) {
    if (schProps[titleProp]) outProps[titleProp] = buildProp(schProps[titleProp], title);
    else if (schProps['Name']) outProps['Name'] = buildProp(schProps['Name'], title);
  }

  for (const [k, v] of Object.entries(properties || {})) {
    if (k === titleProp) continue;
    if (!(k in schProps)) continue;
    const built = buildProp(schProps[k], v);
    if (built !== null) outProps[k] = built;
  }

  const body = { parent: { database_id: tcfg.database_id }, properties: outProps };
  return await notionReq(cfg, 'POST', '/pages', body);
}

function requireIds(cfg, ids, target) {
  const t = ids[target] || {};
  const missing = [];
  if (!t.data_source_id) missing.push(`${target}.data_source_id`);
  if (!t.database_id) missing.push(`${target}.database_id`);
  if (missing.length) {
    const cfgPath = process.env.DIY_PC_INGEST_CONFIG || '~/.config/diy-pc-ingest/config.json';
    die(`Missing Notion IDs in config: ${missing.join(', ')}. Set them in ${cfgPath} (see references/config.example.json).`);
  }
}

async function main() {
  const cfg = await loadConfig();
  const ids = idsFromConfig(cfg);

  const raw = fs.readFileSync(0, 'utf-8');
  const lines = raw.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
  if (!lines.length) {
    console.log('NO_RECORDS');
    return;
  }

  const records = lines.map(l => JSON.parse(l));
  const cacheSchema = {};

  const summary = { created: 0, updated: 0, skipped: 0, errors: 0 };
  const results = [];

  for (const rec of records) {
    const target = rec.target;
    if (!ids[target]) {
      summary.errors += 1;
      results.push({ error: `unknown target: ${target}`, record: rec });
      continue;
    }

    requireIds(cfg, ids, target);

    const overwrite = Boolean(rec.overwrite);
    const pageId = rec.page_id || rec.id;
    const archive = Boolean(rec.archive || rec.archived);

    if (!cacheSchema[target]) {
      cacheSchema[target] = await notionReq(cfg, 'GET', `/data_sources/${ids[target].data_source_id}`);
    }
    const schema = cacheSchema[target];

    const title = rec.title || rec.properties?.Name || rec.properties?.名前;
    const propsIn = rec.properties || {};

    // direct page update
    if (pageId) {
      const existingPage = await notionReq(cfg, 'GET', `/pages/${pageId}`);
      const patch = buildPatch(schema, propsIn, existingPage.properties || {}, overwrite);
      const body = {};
      if (Object.keys(patch).length) body.properties = patch;
      if (archive) body.archived = true;

      if (Object.keys(body).length) {
        const updated = await notionReq(cfg, 'PATCH', `/pages/${pageId}`, body);
        summary.updated += 1;
        results.push({ action: 'updated', target, id: updated.id, url: updated.url });
      } else {
        summary.skipped += 1;
        results.push({ action: 'skipped', target, id: existingPage.id, url: existingPage.url });
      }
      continue;
    }

    const existing = await findExisting(cfg, ids, target, schema, propsIn);
    if (existing) {
      const patch = buildPatch(schema, propsIn, existing.properties || {}, overwrite);
      if (Object.keys(patch).length) {
        const updated = await notionReq(cfg, 'PATCH', `/pages/${existing.id}`, { properties: patch });
        summary.updated += 1;
        results.push({ action: 'updated', target, id: updated.id, url: updated.url });
      } else {
        summary.skipped += 1;
        results.push({ action: 'skipped', target, id: existing.id, url: existing.url });
      }
    } else {
      const created = await createPage(cfg, ids, target, schema, String(title || '(untitled)'), propsIn);
      summary.created += 1;
      results.push({ action: 'created', target, id: created.id, url: created.url });
    }

    // mirror storage -> pcconfig
    if (target === 'storage' && rec.mirror_to_pcconfig) {
      const pc = propsIn['現在の接続先PC'];
      const purchaseDate = propsIn['購入日'];
      const name = propsIn['Name'];
      if (!(pc && purchaseDate && name)) {
        summary.skipped += 1;
        results.push({ action: 'skipped', target: 'pcconfig', reason: 'mirror_missing_fields' });
      } else {
        requireIds(cfg, ids, 'pcconfig');
        if (!cacheSchema.pcconfig) {
          cacheSchema.pcconfig = await notionReq(cfg, 'GET', `/data_sources/${ids.pcconfig.data_source_id}`);
        }
        const pcSchema = cacheSchema.pcconfig;
        const pcProps = {
          PC: pc,
          Category: 'ストレージ',
          Name: String(name),
          'Purchase Date': String(purchaseDate),
          'Purchase Vendor': propsIn['購入店'],
          'Purchase Price': propsIn['価格(円)'],
          Spec: `S/N: ${propsIn['シリアル'] || ''}`,
          Installed: true,
          Active: true,
          Notes: 'mirrored from storage',
        };
        const pcExisting = await findExisting(cfg, ids, 'pcconfig', pcSchema, pcProps);
        if (pcExisting) {
          const pcPatch = buildPatch(pcSchema, pcProps, pcExisting.properties || {}, false);
          if (Object.keys(pcPatch).length) {
            const pcUpdated = await notionReq(cfg, 'PATCH', `/pages/${pcExisting.id}`, { properties: pcPatch });
            summary.updated += 1;
            results.push({ action: 'updated', target: 'pcconfig', id: pcUpdated.id, url: pcUpdated.url, reason: 'mirrored' });
          } else {
            summary.skipped += 1;
            results.push({ action: 'skipped', target: 'pcconfig', id: pcExisting.id, url: pcExisting.url, reason: 'mirrored_no_changes' });
          }
        } else {
          const pcCreated = await createPage(cfg, ids, 'pcconfig', pcSchema, String(name), pcProps);
          summary.created += 1;
          results.push({ action: 'created', target: 'pcconfig', id: pcCreated.id, url: pcCreated.url, reason: 'mirrored' });
        }
      }
    }
  }

  console.log(JSON.stringify({ summary, results }, null, 2));
}

main().catch(err => {
  process.stderr.write(String(err?.message || err) + '\n');
  process.exit(1);
});
