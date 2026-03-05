import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';

export function defaultSecretsPath() {
  return path.join(os.homedir(), '.config', 'openclaw', 'secrets.env');
}

export function maskSecret(s) {
  if (!s) return '';
  if (s.length <= 8) return '********';
  return `${s.slice(0, 4)}…${s.slice(-4)}`;
}

export function parseEnv(text) {
  const out = {};
  for (const line of text.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const m = /^([A-Za-z_][A-Za-z0-9_]*)=(.*)$/.exec(line);
    if (!m) continue;
    const key = m[1];
    let val = m[2] ?? '';
    // remove optional surrounding quotes
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    out[key] = val;
  }
  return out;
}

export async function loadSecretsEnv(filePath = defaultSecretsPath()) {
  try {
    const text = await fs.readFile(filePath, 'utf8');
    return parseEnv(text);
  } catch (e) {
    if (e && (e.code === 'ENOENT' || e.code === 'ENOTDIR')) return {};
    throw e;
  }
}

export async function upsertSecrets({ filePath = defaultSecretsPath(), updates }) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });

  let original = '';
  try {
    original = await fs.readFile(filePath, 'utf8');
  } catch (e) {
    if (!(e && e.code === 'ENOENT')) throw e;
  }

  const lines = original ? original.split(/\r?\n/) : [];
  const keys = Object.keys(updates);
  const seen = new Set();

  const newLines = lines.map((line) => {
    const m = /^([A-Za-z_][A-Za-z0-9_]*)=/.exec(line);
    if (!m) return line;
    const k = m[1];
    if (!Object.prototype.hasOwnProperty.call(updates, k)) return line;
    seen.add(k);
    return `${k}=${updates[k]}`;
  });

  for (const k of keys) {
    if (seen.has(k)) continue;
    newLines.push(`${k}=${updates[k]}`);
  }

  const outText = newLines.filter((l, idx, arr) => !(l === '' && idx === arr.length - 1)).join('\n') + '\n';
  await fs.writeFile(filePath, outText, { mode: 0o600 });

  // Ensure perms are tight even when file already existed.
  try {
    await fs.chmod(filePath, 0o600);
  } catch {
    // ignore (e.g., on some FS)
  }

  return { filePath };
}
