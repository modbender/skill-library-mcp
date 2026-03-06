import fs from 'node:fs';
import path from 'node:path';

/**
 * @typedef {Object} Lock
 * @property {number} fd - File descriptor
 * @property {string} lockPath - Path to the lock file
 */

/**
 * Acquire an advisory flock-based lock on a .lock file adjacent to the target path.
 * @param {string} filePath - Path to the file being locked
 * @param {number} [timeout=5000] - Timeout in ms
 * @returns {Promise<Lock>}
 */
export async function acquireLock(filePath, timeout = 5000) {
  const lockPath = filePath + '.lock';
  fs.mkdirSync(path.dirname(lockPath), { recursive: true });

  const start = Date.now();
  let staleCleaned = false;
  while (true) {
    try {
      const fd = fs.openSync(lockPath, fs.constants.O_WRONLY | fs.constants.O_CREAT | fs.constants.O_EXCL, 0o644);
      fs.writeSync(fd, String(process.pid));
      fs.fsyncSync(fd);
      return { fd, lockPath };
    } catch (err) {
      if (err.code !== 'EEXIST') throw err;

      // Stale lock detection (once per acquire attempt to avoid TOCTOU loop).
      // If the PID in the lock file is dead, attempt to atomically replace it
      // by renaming to a .stale file, then retrying O_EXCL. Only one process
      // wins the rename; the other gets ENOENT on rename and retries normally.
      if (!staleCleaned) {
        staleCleaned = true;
        try {
          const lockPid = parseInt(fs.readFileSync(lockPath, 'utf8').trim(), 10);
          if (lockPid && !isProcessAlive(lockPid)) {
            const stalePath = `${lockPath}.stale.${process.pid}`;
            try {
              fs.renameSync(lockPath, stalePath); // Atomic — only one process wins
              fs.unlinkSync(stalePath);
            } catch {
              // Another process already renamed it — that's fine, retry
            }
            continue; // Retry the O_EXCL open
          }
        } catch {
          // Lock file unreadable or gone — retry the O_EXCL open
          continue;
        }
      }

      if (Date.now() - start > timeout) {
        throw new Error(`Lock timeout: could not acquire lock on ${lockPath} within ${timeout}ms`);
      }
      await new Promise(r => setTimeout(r, 50 + Math.random() * 50));
    }
  }
}

/**
 * Check if a process is still alive.
 * @param {number} pid
 * @returns {boolean}
 */
function isProcessAlive(pid) {
  try {
    process.kill(pid, 0); // Signal 0 = existence check, no actual signal sent
    return true;
  } catch {
    return false;
  }
}

/**
 * Release a previously acquired lock.
 * @param {Lock} lock
 */
export function releaseLock(lock) {
  try { fs.closeSync(lock.fd); } catch {}
  try { fs.unlinkSync(lock.lockPath); } catch {}
}
