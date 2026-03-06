#!/usr/bin/env node
/**
 * AOI Sandbox Shield (Lite)
 * S-DNA: AOI-2026-0215-SDNA-SS02
 * License: MIT
 */

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';

const __sdna__ = {
  protocol: 'aoineco-sdna-v1',
  id: 'AOI-2026-0215-SDNA-SS02',
  org: 'aoineco-co',
  classification: 'public-safe',
};

function sha256(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

function nowKST() {
  // KST = UTC+9
  const d = new Date(Date.now() + 9 * 60 * 60 * 1000);
  return d.toISOString().replace('Z', '+09:00');
}

function parseArgs(argv) {
  const [cmd, ...rest] = argv;
  const args = {};
  for (const r of rest) {
    if (r.startsWith('--')) {
      const [k, v = 'true'] = r.slice(2).split('=');
      args[k] = v;
    }
  }
  return { cmd, args };
}

function readFileIfExists(p) {
  try {
    const data = fs.readFileSync(p);
    return { ok: true, path: p, bytes: data.length, sha256: sha256(data) };
  } catch {
    return { ok: false, path: p, error: 'missing' };
  }
}

function snapshot({ reason }) {
  const workspace = path.join(os.homedir(), '.openclaw', 'workspace');
  const snapRoot = path.join(workspace, '.sandbox_snapshots_lite');
  fs.mkdirSync(snapRoot, { recursive: true });

  const snapId = new Date().toISOString().replace(/[:.]/g, '-');
  const dir = path.join(snapRoot, snapId);
  fs.mkdirSync(dir);

  const targets = [
    path.join(os.homedir(), '.openclaw', 'openclaw.json'),
    path.join(workspace, 'AGENTS.md'),
    path.join(workspace, 'SOUL.md'),
    path.join(workspace, 'CURRENT_STATE.md'),
    path.join(workspace, 'MEMORY.md'),
  ];

  const manifest = {
    __sdna__,
    kind: 'snapshot',
    snapId,
    reason: reason || '',
    createdAt: nowKST(),
    files: [],
  };

  for (const p of targets) {
    const info = readFileIfExists(p);
    manifest.files.push(info);
    if (info.ok) {
      const base = path.basename(p);
      fs.copyFileSync(p, path.join(dir, base));
    }
  }

  fs.writeFileSync(path.join(dir, 'manifest.json'), JSON.stringify(manifest, null, 2));
  return { ...manifest, snapshotDir: dir };
}

function validateConfig({ p }) {
  const requiredPaths = [
    ['agents', 'defaults', 'model', 'primary'],
    ['channels'],
    ['gateway'],
  ];

  const raw = fs.readFileSync(p, 'utf-8');
  let obj;
  try {
    obj = JSON.parse(raw);
  } catch (e) {
    return {
      __sdna__,
      kind: 'validate-config',
      ok: false,
      path: p,
      error: String(e?.message || e),
      createdAt: nowKST(),
    };
  }

  const issues = [];
  for (const parts of requiredPaths) {
    let cur = obj;
    let ok = true;
    for (const part of parts) {
      if (cur && typeof cur === 'object' && part in cur) cur = cur[part];
      else {
        ok = false;
        break;
      }
    }
    if (!ok) issues.push(`Missing required key: ${parts.join('.')}`);
  }

  const primary = obj?.agents?.defaults?.model?.primary;
  if (!primary) issues.push('No primary model configured');

  return {
    __sdna__,
    kind: 'validate-config',
    ok: issues.length === 0,
    path: p,
    issues,
    createdAt: nowKST(),
  };
}

function main() {
  const { cmd, args } = parseArgs(process.argv.slice(2));

  if (!cmd || ['-h', '--help', 'help'].includes(cmd)) {
    console.log(JSON.stringify({
      __sdna__,
      usage: {
        snapshot: 'node skill.js snapshot --reason="..."',
        validateConfig: 'node skill.js validate-config --path=/path/to/openclaw.json',
      }
    }, null, 2));
    return;
  }

  if (cmd === 'snapshot') {
    const out = snapshot({ reason: args.reason });
    console.log(JSON.stringify(out, null, 2));
    return;
  }

  if (cmd === 'validate-config') {
    const p = args.path;
    if (!p) throw new Error('--path is required');
    const out = validateConfig({ p });
    console.log(JSON.stringify(out, null, 2));
    return;
  }

  throw new Error(`Unknown command: ${cmd}`);
}

main();
