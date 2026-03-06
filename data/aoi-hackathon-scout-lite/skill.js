#!/usr/bin/env node
/**
 * AOI Hackathon Scout (Lite)
 * S-DNA: AOI-2026-0215-SDNA-HACK01
 */

import fs from 'node:fs';
import path from 'node:path';

const __sdna__ = {
  protocol: 'aoineco-sdna-v1',
  id: 'AOI-2026-0215-SDNA-HACK01',
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
  return process.env.WORKSPACE || process.cwd();
}

function readRegistry() {
  const root = workspaceRoot();
  const file = path.join(root, 'context', 'HACKATHON_SOURCES_REGISTRY.md');
  if (!fs.existsSync(file)) die(`Registry not found: ${file}`);
  const text = fs.readFileSync(file, 'utf8');
  return { file, text };
}

function extractSources(text) {
  // Best-effort parsing: each source section starts with ### Name and has fields.
  const lines = text.split('\n');
  const out = [];
  let cur = null;
  for (const line of lines) {
    const m = line.match(/^###\s+(.+)$/);
    if (m) {
      if (cur) out.push(cur);
      cur = { name: m[1].trim() };
      continue;
    }
    if (!cur) continue;
    const f = line.match(/^\-\s*([^:]+):\s*(.+)\s*$/);
    if (f) {
      const k = f[1].trim().toLowerCase();
      const v = f[2].trim();
      if (k === 'url') cur.url = v;
      if (k === 'type') cur.type = v.toLowerCase();
      if (k.includes('online-only fit')) cur.online = v;
      if (k.includes('discovery mode')) cur.discovery = v;
      continue;
    }
  }
  if (cur) out.push(cur);
  return out.filter(s => s.url);
}

function sources({ online, type }) {
  const { file, text } = readRegistry();
  let items = extractSources(text);

  if (type) {
    const t = String(type).toLowerCase();
    items = items.filter(s => (s.type || '').includes(t));
  }

  if (online) {
    const o = String(online).toLowerCase();
    if (o === 'ok') items = items.filter(s => (s.online || '').includes('✅') || (s.online || '').includes('⚠️'));
    if (o === 'good') items = items.filter(s => (s.online || '').includes('✅'));
  }

  console.log(JSON.stringify({ __sdna__, kind: 'sources', registry: file, count: items.length, items }, null, 2));
}

function readShortlist() {
  const root = workspaceRoot();
  const file = path.join(root, 'context', 'HACKATHON_SHORTLIST.md');
  if (!fs.existsSync(file)) die(`Shortlist not found: ${file}`);
  const text = fs.readFileSync(file, 'utf8');
  return { file, text };
}

function parseDeadlineTs(deadlineStr) {
  // Best-effort parsing.
  // Strong preference: ISO-8601 with timezone (e.g., 2026-07-07T23:59:00-12:00)
  // Fallback: anything Date.parse understands.
  if (!deadlineStr) return { ts: null, parseable: false };
  const s = String(deadlineStr).trim();

  // Extract ISO-like substring if present
  const iso = s.match(/\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}(?::\d{2})?)?(?:Z|[\+\-]\d{2}:?\d{2})?/);
  const candidate = iso ? iso[0].replace(' ', 'T') : s;
  const t = Date.parse(candidate);
  if (Number.isFinite(t)) return { ts: t, parseable: true };
  return { ts: null, parseable: false };
}

function extractShortlistItems(text) {
  // Very lightweight parser for the existing markdown template blocks.
  // Extracts: Name, URL, Location, Apply deadline, Status.
  const blocks = text.split(/\n\n(?=\- \*\*Name:\*\*)/g);
  const items = [];
  for (const b of blocks) {
    const name = (b.match(/\- \*\*Name:\*\*\s*(.+)/) || [])[1];
    const url = (b.match(/\- \*\*URL:\*\*\s*(https?:\/\/\S+)/) || [])[1];
    if (!name || !url) continue;
    const location = (b.match(/\- \*\*Location:\*\*\s*(.+)/) || [])[1] || '';
    // IMPORTANT: use [ \t]* instead of \s* so we don't accidentally consume newlines.
    const deadlineHuman = (b.match(/\- \*\*Apply deadline \(human\):\*\*[ \t]*(.+)/) || [])[1]
      || (b.match(/\- \*\*Apply deadline:\*\*[ \t]*(.+)/) || [])[1]
      || '';
    const deadlineIso = (b.match(/\- \*\*Apply deadline \(ISO\+TZ\):\*\*[ \t]*(.+)/) || [])[1] || '';
    const verifiedRaw = (b.match(/\- \*\*Deadline verified\?:\*\*[ \t]*(.+)/) || [])[1] || '';
    const verified = String(verifiedRaw).trim().toLowerCase().startsWith('yes') ? 'yes' : String(verifiedRaw).trim().toLowerCase().startsWith('no') ? 'no' : String(verifiedRaw).trim();
    const status = (b.match(/\- \*\*Status:\*\*\s*(.+)/) || [])[1] || '';

    const isRejected = /rejected/i.test(status);
    const onlineEligible = /online/i.test(location) && !/offline/i.test(location);
    const isHot = /🔥/.test(b) || /asap/i.test(String(deadlineHuman).toLowerCase());

    const d = parseDeadlineTs((deadlineIso || deadlineHuman).trim());
    const now = Date.now();
    const isExpired = d.ts !== null ? d.ts < now : false;

    items.push({
      name: name.trim(),
      url,
      location: location.trim(),
      deadline: String(deadlineHuman).trim(),
      deadlineIso: String(deadlineIso).trim(),
      deadlineVerified: String(verified).trim(),
      deadlineTs: d.ts,
      deadlineParseable: d.parseable,
      isExpired,
      status: status.trim(),
      onlineEligible,
      isHot,
      isRejected,
    });
  }
  return items;
}

function recommend({ n }) {
  const limit = Number(n || 5);
  const { file, text } = readShortlist();
  let items = extractShortlistItems(text);

  // Exclude rejected and (if parseable) expired deadlines.
  items = items.filter(i => !i.isRejected);
  items = items.filter(i => !(i.deadlineParseable && i.isExpired));

  // Prefer online-eligible; if none, still show.
  const online = items.filter(i => i.onlineEligible);
  const pool = online.length ? online : items;

  pool.sort((a, b) => {
    // 1) hot first
    const hot = (b.isHot ? 1 : 0) - (a.isHot ? 1 : 0);
    if (hot) return hot;

    // 2) earliest known deadline first (so we don't miss near due)
    const ad = a.deadlineTs ?? Number.POSITIVE_INFINITY;
    const bd = b.deadlineTs ?? Number.POSITIVE_INFINITY;
    if (ad !== bd) return ad - bd;

    // 3) status priority
    const rank = (s) => /applying/i.test(s) ? 0 : /watching/i.test(s) ? 1 : /new/i.test(s) ? 2 : 3;
    return rank(a.status) - rank(b.status);
  });

  const top = pool.slice(0, limit);
  console.log(JSON.stringify({ __sdna__, kind: 'recommend', shortlist: file, count: top.length, items: top }, null, 2));
}

function template() {
  const root = workspaceRoot();
  const file = path.join(root, 'context', 'HACKATHON_NOTION_PASTE_TEMPLATE.md');
  const text = fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : 'Template not found.';
  console.log(JSON.stringify({ __sdna__, kind: 'template', file, text }, null, 2));
}

function help() {
  console.log(JSON.stringify({
    __sdna__,
    usage: {
      sources: 'aoi-hackathon sources [--online ok|good] [--type web3|platform|calendar|challenge|os/bounties|accelerator/grant]',
      recommend: 'aoi-hackathon recommend --n 5',
      template: 'aoi-hackathon template'
    },
    notes: [
      'Public-safe: this skill does not crawl websites or submit forms.',
      'Update sources by editing context/HACKATHON_SOURCES_REGISTRY.md'
    ]
  }, null, 2));
}

function main() {
  const { cmd, args } = parseArgs(process.argv.slice(2));
  if (!cmd || ['help', '-h', '--help'].includes(cmd)) return help();
  if (cmd === 'sources') return sources({ online: args.online, type: args.type });
  if (cmd === 'recommend') return recommend({ n: args.n });
  if (cmd === 'template') return template();
  die(`Unknown command: ${cmd}`);
}

main();
