#!/usr/bin/env node
import { loadConfig, requireIds, httpJson } from './ltm_common.js';

function textOf(prop) {
  if (!prop) return '';
  const t = prop.type;
  if (t === 'title' || t === 'rich_text') return (prop[t] || []).map(x => x?.plain_text || '').join('').trim();
  if (t === 'select') return prop.select?.name || '';
  if (t === 'multi_select') return (prop.multi_select || []).map(x => x?.name).filter(Boolean).join(',');
  if (t === 'url') return prop.url || '';
  return '';
}

function queryDs(dsId, prop, kind, q, pageSize) {
  const body = { page_size: pageSize, filter: { property: prop, [kind]: { contains: q } } };
  const res = httpJson('POST', `/data_sources/${dsId}/query`, body);
  return res?.results || [];
}

function parseArgs(argv) {
  const out = { query: '', limit: 5 };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--query') out.query = argv[++i] || '';
    else if (a === '--limit') out.limit = Number(argv[++i] || 5);
  }
  return out;
}

function main() {
  const args = parseArgs(process.argv);
  if (!args.query.trim()) throw new Error('Empty query');
  const cfg = loadConfig();
  requireIds(cfg);
  const dsId = cfg.data_source_id;

  const pageSize = Math.min(50, Math.max(args.limit, 5) * 5);
  const hits = [
    ...queryDs(dsId, 'Name', 'title', args.query, pageSize),
    ...queryDs(dsId, 'Content', 'rich_text', args.query, pageSize),
  ];

  const seen = new Set();
  const out = [];
  for (const r of hits) {
    const rid = r?.id;
    if (!rid || seen.has(rid)) continue;
    seen.add(rid);
    const p = r.properties || {};
    out.push({
      id: rid,
      url: r.url,
      title: textOf(p.Name),
      type: textOf(p.Type),
      tags: textOf(p.Tags),
      content: textOf(p.Content).slice(0, 400),
      source: textOf(p.Source),
      confidence: textOf(p.Confidence),
    });
    if (out.length >= args.limit) break;
  }
  console.log(JSON.stringify({ ok: true, query: args.query, results: out }, null, 2));
}

try { main(); } catch (e) { console.error(String(e?.stack || e)); process.exit(1); }
