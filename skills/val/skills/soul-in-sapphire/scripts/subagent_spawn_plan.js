#!/usr/bin/env node
import fs from 'fs';
import path from 'path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const STATE_DIR = path.join(ROOT, 'state');
const CFG_PATH = path.join(STATE_DIR, 'subagent-models.json');
const LOG_PATH = path.join(STATE_DIR, 'subagent-spawn-log.jsonl');

function loadCfg() {
  if (!fs.existsSync(CFG_PATH)) throw new Error(`Missing config: ${CFG_PATH}`);
  return JSON.parse(fs.readFileSync(CFG_PATH, 'utf-8'));
}

function parseArgs(argv) {
  const out = { profile: '', task: '', label: '' };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--profile') out.profile = argv[++i] || '';
    else if (a === '--task') out.task = argv[++i] || '';
    else if (a === '--label') out.label = argv[++i] || '';
  }
  return out;
}

function main() {
  const args = parseArgs(process.argv);
  if (!args.profile || !args.task) throw new Error('Usage: --profile <name> --task <text> [--label <label>]');
  const cfg = loadCfg();
  const p = (cfg.profiles || {})[args.profile];
  if (!p) throw new Error(`Unknown profile: ${args.profile}`);
  const d = cfg.defaults || {};
  const runTimeout = Number(d.runTimeoutSeconds || 180);

  const payload = {
    label: args.label || `${args.profile}-${Math.floor(Date.now() / 1000)}`,
    task: args.task,
    model: p.model,
    thinking: p.thinking,
    runTimeoutSeconds: runTimeout,
    timeoutSeconds: runTimeout,
    cleanup: d.cleanup || 'keep',
  };

  fs.mkdirSync(STATE_DIR, { recursive: true });
  fs.appendFileSync(LOG_PATH, JSON.stringify({ ts: Math.floor(Date.now() / 1000), profile: args.profile, payload }, null, 0) + '\n', 'utf-8');
  console.log(JSON.stringify(payload, null, 2));
}

try { main(); } catch (e) { console.error(String(e?.stack || e)); process.exit(1); }
