import path from 'node:path';
import fs from 'node:fs';
import crypto from 'node:crypto';

const DEFAULT_STATE_FILE = 'board-state.json';

function toSafeRelative(raw) {
  if (path.isAbsolute(raw)) {
    const base = path.basename(raw) || DEFAULT_STATE_FILE;
    const hash = crypto.createHash('sha256').update(raw).digest('hex').slice(0, 12);
    return path.join('_abs', `${hash}-${base}`);
  }

  return path
    .normalize(raw)
    .split(path.sep)
    .filter((part) => part && part !== '.' && part !== '..')
    .join(path.sep);
}

export function resolveStatePath(opts = {}) {
  const raw = String(opts.statePath || process.env.CONSENSUS_STATE_FILE || DEFAULT_STATE_FILE);
  const configuredRoot = String(opts.stateRoot || process.env.CONSENSUS_STATE_ROOT || '.consensus');
  const root = path.resolve(configuredRoot);

  const safeRelative = toSafeRelative(raw || DEFAULT_STATE_FILE) || DEFAULT_STATE_FILE;
  let resolved = path.resolve(root, safeRelative);

  if (!resolved.startsWith(root + path.sep) && resolved !== root) {
    resolved = path.join(root, path.basename(safeRelative));
  }
  if (path.extname(resolved) !== '.json') resolved = `${resolved}.json`;

  fs.mkdirSync(path.dirname(resolved), { recursive: true });
  return resolved;
}
