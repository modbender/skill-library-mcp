import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

export function secretsDir() {
  return path.join(os.homedir(), '.openclaw', 'secrets', 'm365-calendar');
}

export function ensureSecretsDir() {
  const dir = secretsDir();
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

export function profilePaths(profile) {
  const dir = ensureSecretsDir();
  return {
    cfgPath: path.join(dir, `${profile}.json`),
    cachePath: path.join(dir, `${profile}-token-cache.json`),
  };
}

export function readJson(p) {
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

export function writeJson(p, obj) {
  fs.writeFileSync(p, JSON.stringify(obj, null, 2) + '\n', 'utf8');
}

export function mustGetArg(name) {
  const idx = process.argv.indexOf(`--${name}`);
  if (idx === -1 || !process.argv[idx + 1]) {
    throw new Error(`Missing --${name}`);
  }
  return process.argv[idx + 1];
}

export function getArg(name, def = undefined) {
  const idx = process.argv.indexOf(`--${name}`);
  if (idx === -1) return def;
  return process.argv[idx + 1] ?? def;
}

export function hasFlag(name) {
  return process.argv.includes(`--${name}`);
}

export function tzPreferHeader(tz) {
  return tz ? { Prefer: `outlook.timezone=\"${tz}\"` } : {};
}

export function dayRangeIsoLocal(offsetDays) {
  const now = new Date();
  const start = new Date(now.getFullYear(), now.getMonth(), now.getDate() + offsetDays, 0, 0, 0);
  const end = new Date(now.getFullYear(), now.getMonth(), now.getDate() + offsetDays + 1, 0, 0, 0);
  return { start, end };
}

export function whenToRange(when) {
  if (when === 'today') {
    const now = new Date();
    const { end } = dayRangeIsoLocal(0);
    return { start: now, end };
  }
  if (when === 'tomorrow') {
    const { start, end } = dayRangeIsoLocal(1);
    return { start, end };
  }
  throw new Error(`Unsupported --when ${when} (use today|tomorrow)`);
}
