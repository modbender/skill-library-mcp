import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

export function secretsDir() {
  return path.join(os.homedir(), '.openclaw', 'secrets', 'm365-mailbox');
}

export function profilePaths(profile) {
  const dir = secretsDir();
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
  if (idx === -1 || !process.argv[idx + 1]) throw new Error(`Missing --${name}`);
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
