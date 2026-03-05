const fs = require('node:fs');
const path = require('node:path');

function readJson(file) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch {
    return null;
  }
}

function acquireLock(lockPath, { staleMs = 5 * 60 * 1000 } = {}) {
  const resolved = path.resolve(lockPath);
  fs.mkdirSync(path.dirname(resolved), { recursive: true });

  const payload = {
    pid: process.pid,
    ts: Date.now(),
  };

  try {
    const fd = fs.openSync(resolved, 'wx');
    fs.writeFileSync(fd, JSON.stringify(payload), 'utf8');
    return {
      release() {
        try { fs.closeSync(fd); } catch {}
        try { fs.unlinkSync(resolved); } catch {}
      },
      path: resolved,
      created: true,
    };
  } catch (err) {
    if (err.code !== 'EEXIST') throw err;
    const current = readJson(resolved);
    const ts = current && Number(current.ts);
    const stale = Number.isFinite(ts) && (Date.now() - ts > staleMs);
    if (!stale) {
      return { release() {}, path: resolved, created: false, busy: true };
    }
    try { fs.unlinkSync(resolved); } catch {}
    return acquireLock(resolved, { staleMs });
  }
}

module.exports = { acquireLock };
