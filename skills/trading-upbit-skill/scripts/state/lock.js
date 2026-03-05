const fs = require('fs').promises;

/**
 * Very small file-based lock.
 * - Designed for cron jobs: prevent overlapping runs.
 * - Uses a TTL so stale locks won't block forever.
 */

async function acquireLock(lockFile, ttlMs, meta = {}) {
  const now = Date.now();
  try {
    const raw = await fs.readFile(lockFile, 'utf8');
    const cur = JSON.parse(raw);
    const acquiredAt = new Date(cur.acquiredAt || 0).getTime();
    const age = now - acquiredAt;
    if (cur && acquiredAt && age < ttlMs) {
      return { ok: false, reason: 'LOCKED', ageMs: age, holder: cur };
    }
  } catch {
    // missing/invalid lock → can acquire
  }

  const payload = {
    acquiredAt: new Date(now).toISOString(),
    pid: process.pid,
    ...meta,
  };

  await fs.writeFile(lockFile, JSON.stringify(payload, null, 2), 'utf8');
  return { ok: true, holder: payload };
}

async function releaseLock(lockFile) {
  try {
    await fs.unlink(lockFile);
  } catch {
    // ignore
  }
}

module.exports = { acquireLock, releaseLock };
