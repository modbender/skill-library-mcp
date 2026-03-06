#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const BASE = path.dirname(new URL(import.meta.url).pathname);
const RUN_STATE = path.join(BASE, 'run_state.mjs');

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

function buildSafeEnv() {
  return {
    PATH: process.env.PATH || '',
    HOME: process.env.HOME || '',
    LANG: process.env.LANG || 'C.UTF-8',
    LC_ALL: process.env.LC_ALL || '',
    LC_CTYPE: process.env.LC_CTYPE || '',
    SYSTEMROOT: process.env.SYSTEMROOT || '',
    WINDIR: process.env.WINDIR || '',
  };
}

function runNode(args) {
  const cp = spawnSync('node', [RUN_STATE, ...args], { encoding: 'utf-8', env: buildSafeEnv() });
  if (cp.status !== 0) throw new Error((cp.stderr || cp.stdout || '').trim());
  return JSON.parse((cp.stdout || '{}').trim() || '{}');
}

function main() {
  const a = parseArgs(process.argv);
  const runId = String(a['run-id'] || '');
  const resultJson = String(a['result-json'] || '');
  if (!runId || !resultJson) throw new Error('required: --run-id --result-json');

  const rec = runNode(['get', '--run-id', runId]);
  if (rec.error === 'not_found') {
    console.log(JSON.stringify({ error: 'run_not_found', run_id: runId }));
    return;
  }

  const resultPath = path.resolve(resultJson);
  const result = JSON.parse(fs.readFileSync(resultPath, 'utf-8'));

  runNode(['upsert', '--run-id', runId, '--session-key', rec.session_key, '--task', rec.task, '--status', 'completed']);
  runNode(['remove', '--run-id', runId]);

  console.log(JSON.stringify({ run_id: runId, status: 'completed', task: rec.task, result }));
}

try { main(); } catch (e) { console.error(String(e?.stack || e)); process.exit(1); }
