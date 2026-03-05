#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const DEFAULT_STATE_PATH = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', 'state', 'runs.json');

function nowIso() { return new Date().toISOString(); }

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

function loadState(p) {
  if (!fs.existsSync(p)) return { runs: {} };
  const txt = fs.readFileSync(p, 'utf-8').trim();
  if (!txt) return { runs: {} };
  try {
    const d = JSON.parse(txt);
    if (!d || typeof d !== 'object') return { runs: {} };
    if (!d.runs || typeof d.runs !== 'object') d.runs = {};
    return d;
  } catch {
    return { runs: {} };
  }
}

function saveState(p, d) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(d, null, 2), 'utf-8');
}

function main() {
  const a = parseArgs(process.argv);
  const cmd = a._[0];
  const statePath = String(a.state || DEFAULT_STATE_PATH);
  const state = loadState(statePath);
  const runs = state.runs || (state.runs = {});

  if (cmd === 'upsert') {
    if (!a['run-id'] || !a['book-id'] || !a.title) throw new Error('upsert requires --run-id --book-id --title');
    runs[a['run-id']] = {
      runId: a['run-id'],
      book_id: Number(a['book-id']),
      title: String(a.title),
      status: 'running',
      started_at: nowIso(),
    };
    saveState(statePath, state);
    console.log(JSON.stringify({ ok: true, action: 'upsert', runId: a['run-id'], count: Object.keys(runs).length }));
    return;
  }

  if (cmd === 'remove') {
    if (!a['run-id']) throw new Error('remove requires --run-id');
    const existed = Object.prototype.hasOwnProperty.call(runs, a['run-id']);
    delete runs[a['run-id']];
    saveState(statePath, state);
    console.log(JSON.stringify({ ok: true, action: 'remove', runId: a['run-id'], existed, count: Object.keys(runs).length }));
    return;
  }

  if (cmd === 'fail') {
    if (!a['run-id'] || !a.error) throw new Error('fail requires --run-id --error');
    const e = runs[a['run-id']];
    if (!e) {
      console.log(JSON.stringify({ ok: false, error: 'run_not_found', runId: a['run-id'] }));
      process.exit(1);
    }
    e.status = 'failed';
    e.error = String(a.error);
    e.updated_at = nowIso();
    saveState(statePath, state);
    console.log(JSON.stringify({ ok: true, action: 'fail', runId: a['run-id'] }));
    return;
  }

  if (cmd === 'get') {
    if (!a['run-id']) throw new Error('get requires --run-id');
    console.log(JSON.stringify({ ok: true, run: runs[a['run-id']] || null }));
    return;
  }

  throw new Error('usage: run_state.mjs <upsert|remove|fail|get> [--state path] ...');
}

try { main(); } catch (e) { console.error(String(e?.stack || e)); process.exit(1); }
