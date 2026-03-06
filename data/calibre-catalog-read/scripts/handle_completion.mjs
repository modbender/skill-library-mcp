#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const SCRIPT_DIR = path.dirname(new URL(import.meta.url).pathname);
const DEFAULT_STATE_PATH = path.resolve(SCRIPT_DIR, '..', 'state', 'runs.json');
const PIPELINE_PY = path.resolve(SCRIPT_DIR, 'run_analysis_pipeline.py');

function nowIso() { return new Date().toISOString(); }

function parseArgs(argv) {
  const out = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const k = a.slice(2);
      const v = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
      out[k] = v;
    }
  }
  return out;
}

function loadState(p) {
  if (!fs.existsSync(p)) return { runs: {} };
  const txt = fs.readFileSync(p, 'utf-8').trim();
  if (!txt) return { runs: {} };
  try {
    const d = JSON.parse(txt);
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

function markFailed(p, runId, error) {
  const d = loadState(p);
  const e = d.runs?.[runId];
  if (!e) return;
  e.status = 'failed';
  e.error = error;
  e.updated_at = nowIso();
  saveState(p, d);
}

function removeRun(p, runId) {
  const d = loadState(p);
  const existed = !!d.runs?.[runId];
  if (d.runs) delete d.runs[runId];
  saveState(p, d);
  return existed;
}

function runApply(args, bookId) {
  const cmd = ['uv', 'run', 'python', PIPELINE_PY, '--with-library', args['with-library'], '--book-id', String(bookId), '--lang', String(args.lang || 'ja'), '--analysis-json', String(args['analysis-json'])];
  if (args.username) cmd.push('--username', String(args.username));
  if (args['password-env']) cmd.push('--password-env', String(args['password-env']));

  const safeEnv = {
    PATH: process.env.PATH || '',
    HOME: process.env.HOME || '',
    LANG: process.env.LANG || 'C.UTF-8',
    LC_ALL: process.env.LC_ALL || '',
    LC_CTYPE: process.env.LC_CTYPE || '',
    CALIBRE_USERNAME: process.env.CALIBRE_USERNAME || '',
  };
  const penv = String(args['password-env'] || '');
  if (penv && process.env[penv]) safeEnv[penv] = process.env[penv];

  return spawnSync(cmd[0], cmd.slice(1), { encoding: 'utf-8', env: safeEnv });
}

function main() {
  const a = parseArgs(process.argv);
  const statePath = String(a.state || DEFAULT_STATE_PATH);
  const runId = String(a['run-id'] || '');
  const analysisJson = String(a['analysis-json'] || '');
  const withLibrary = String(a['with-library'] || '');
  if (!runId || !analysisJson || !withLibrary) throw new Error('required: --run-id --analysis-json --with-library');

  const d = loadState(statePath);
  const run = d.runs?.[runId];
  if (!run) {
    console.log(JSON.stringify({ ok: true, status: 'stale_or_duplicate', runId }));
    return;
  }

  const bookId = Number(run.book_id);
  if (!fs.existsSync(analysisJson)) {
    const err = `analysis_json_not_found: ${analysisJson}`;
    markFailed(statePath, runId, err);
    console.log(JSON.stringify({ ok: false, status: 'failed', runId, error: err }));
    process.exit(1);
  }

  const cp = runApply(a, bookId);
  if (cp.status !== 0) {
    const err = `apply_failed (exit=${cp.status})`;
    markFailed(statePath, runId, err);
    console.log(JSON.stringify({ ok: false, status: 'failed', runId, book_id: bookId, error: err, stdout: cp.stdout, stderr: cp.stderr }));
    process.exit(cp.status || 1);
  }

  removeRun(statePath, runId);
  console.log(JSON.stringify({ ok: true, status: 'applied_and_removed', runId, book_id: bookId, stdout: cp.stdout }));
}

try { main(); } catch (e) { console.error(String(e?.stack || e)); process.exit(1); }
