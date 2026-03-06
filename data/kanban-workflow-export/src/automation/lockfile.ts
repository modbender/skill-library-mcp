import * as fs from 'node:fs/promises';

export type LockfilePort = {
  tryAcquireLock(path: string, now: Date, ttlMs: number): Promise<{ release: () => Promise<void> }>;
};

function isStale(now: Date, startedAtIso: string | undefined, ttlMs: number): boolean {
  if (!startedAtIso) return true;
  const ms = Date.parse(startedAtIso);
  if (!Number.isFinite(ms)) return true;
  return now.getTime() - ms > ttlMs;
}

export const lockfile: LockfilePort = {
  async tryAcquireLock(path: string, now: Date, ttlMs: number) {
    await fs.mkdir(path.includes('/') ? path.split('/').slice(0, -1).join('/') : '.', { recursive: true });

    const payload = JSON.stringify({ pid: process.pid, startedAt: now.toISOString() });

    try {
      const handle = await fs.open(path, 'wx');
      await handle.writeFile(payload, { encoding: 'utf8' });
      return {
        release: async () => {
          await handle.close();
          await fs.rm(path, { force: true });
        },
      };
    } catch (err: any) {
      if (err?.code !== 'EEXIST') throw err;

      // Best-effort stale lock recovery.
      let stale = false;
      try {
        const raw = await fs.readFile(path, 'utf8');
        const data = JSON.parse(raw);
        stale = isStale(now, data?.startedAt, ttlMs);
      } catch {
        stale = true;
      }

      if (!stale) {
        throw new Error(`autopilot lock is already held: ${path}`);
      }

      // Remove stale and retry once.
      await fs.rm(path, { force: true });
      const handle = await fs.open(path, 'wx');
      await handle.writeFile(payload, { encoding: 'utf8' });
      return {
        release: async () => {
          await handle.close();
          await fs.rm(path, { force: true });
        },
      };
    }
  },
};
