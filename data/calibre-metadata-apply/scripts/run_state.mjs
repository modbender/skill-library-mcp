#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const STATE_PATH = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', 'state', 'runs.json');
const nowIso = () => new Date().toISOString();

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const k = a.slice(2);
      const v = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
      out[k] = v;
    } else out._.push(a);
  }
  return out;
}

function loadState() {
  if (!fs.existsSync(STATE_PATH)) return { runs: {} };
  try {
    const d = JSON.parse(fs.readFileSync(STATE_PATH, 'utf-8'));
    if (!d.runs || typeof d.runs !== 'object') d.runs = {};
    return d;
  } catch {
    return { runs: {} };
  }
}

function saveState(s) {
  fs.mkdirSync(path.dirname(STATE_PATH), { recursive: true });
  fs.writeFileSync(STATE_PATH, JSON.stringify(s, null, 2), 'utf-8');
}

function main() {
  const a = parseArgs(process.argv);
  const cmd = a._[0];
  const state = loadState();
  const runs = state.runs || (state.runs = {});

  if (cmd === 'upsert') {
    if (!a['run-id'] || !a['session-key'] || !a.task) throw new Error('upsert requires --run-id --session-key --task');
    const rec = runs[a['run-id']] || {};
    rec.run_id = a['run-id'];
    rec.session_key = a['session-key'];
    rec.status = a.status || 'running';
    rec.task = a.task;
    rec.created_at = rec.created_at || nowIso();
    rec.updated_at = nowIso();
    if (a['meta-json']) rec.meta = JSON.parse(String(a['meta-json']));
    runs[a['run-id']] = rec;
    saveState(state);
    console.log(JSON.stringify(rec));
    return;
  }

  if (cmd === 'get') {
    if (!a['run-id']) throw new Error('get requires --run-id');
    const rec = runs[a['run-id']];
    if (!rec) console.log(JSON.stringify({ error: 'not_found', run_id: a['run-id'] }));
    else console.log(JSON.stringify(rec));
    return;
  }

  if (cmd === 'remove') {
    if (!a['run-id']) throw new Error('remove requires --run-id');
    const existed = !!runs[a['run-id']];
    delete runs[a['run-id']];
    saveState(state);
    console.log(JSON.stringify({ removed: existed, run_id: a['run-id'] }));
    return;
  }

  if (cmd === 'list') {
    let arr = Object.values(runs).sort((x, y) => String(y.updated_at || '').localeCompare(String(x.updated_at || '')));
    if (a.status) arr = arr.filter(r => r.status === a.status);
    const lim = Number(a.limit || 20);
    if (lim > 0) arr = arr.slice(0, lim);
    console.log(JSON.stringify({ count: arr.length, runs: arr }));
    return;
  }

  if (cmd === 'fail') {
    if (!a['run-id'] || !a.error) throw new Error('fail requires --run-id --error');
    const rec = runs[a['run-id']];
    if (!rec) {
      console.log(JSON.stringify({ error: 'not_found', run_id: a['run-id'] }));
      return;
    }
    rec.status = 'failed';
    rec.error = String(a.error);
    rec.updated_at = nowIso();
    runs[a['run-id']] = rec;
    saveState(state);
    console.log(JSON.stringify(rec));
    return;
  }

  throw new Error('usage: run_state.mjs <upsert|get|remove|list|fail> ...');
}

try { main(); } catch (e) { console.error(String(e?.stack || e)); process.exit(1); }
