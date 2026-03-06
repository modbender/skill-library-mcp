#!/usr/bin/env node
/**
 * dist-watcher.js
 *
 * Watches runtime/dist/ for file changes. If any dist file is newer than
 * when the twilio-bridge process started, it restarts the LaunchAgent via
 * `launchctl kickstart -k`.
 *
 * This prevents the "stale runtime" problem where a security/code update
 * recompiles dist/ but the running process never picks it up.
 *
 * Run via LaunchAgent: com.jarvis.amber-dist-watcher.plist
 * Interval: every 60 seconds
 */

const fs = require('fs');
const path = require('path');
const { execFileSync, spawnSync } = require('child_process');

const DIST_DIR = path.resolve(__dirname, '../dist');
const LAUNCHCTL_LABEL = 'com.jarvis.twilio-bridge';
const CHECK_INTERVAL_MS = 60_000;

/** Get the start time (epoch ms) of the twilio-bridge process, or null if not running. */
function getRuntimeStartMs() {
  try {
    // Find the PID
    const result = spawnSync('pgrep', ['-f', 'dist/index.js'], { encoding: 'utf8' });
    if (result.status !== 0 || !result.stdout.trim()) return null;

    const pids = result.stdout.trim().split('\n').map(Number).filter(Boolean);
    if (!pids.length) return null;

    // Get start time for first matching PID using ps
    // ps lstart format: "Thu Feb 20 18:00:00 2026"
    const psResult = spawnSync('ps', ['-p', String(pids[0]), '-o', 'lstart='], { encoding: 'utf8' });
    if (psResult.status !== 0 || !psResult.stdout.trim()) return null;

    const startMs = Date.parse(psResult.stdout.trim());
    return isNaN(startMs) ? null : startMs;
  } catch {
    return null;
  }
}

/** Get the newest mtime (epoch ms) of any file in dist/. */
function getNewestDistMtimeMs() {
  try {
    let newest = 0;
    const scan = (dir) => {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        const full = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          scan(full);
        } else if (entry.isFile()) {
          const mtime = fs.statSync(full).mtimeMs;
          if (mtime > newest) newest = mtime;
        }
      }
    };
    scan(DIST_DIR);
    return newest;
  } catch {
    return 0;
  }
}

/** Restart the LaunchAgent. */
function restartRuntime() {
  try {
    const uid = process.getuid();
    execFileSync('launchctl', ['kickstart', '-k', `gui/${uid}/${LAUNCHCTL_LABEL}`], {
      encoding: 'utf8',
      timeout: 10_000,
    });
    console.log(`[dist-watcher] Restarted ${LAUNCHCTL_LABEL}`);
  } catch (e) {
    console.error(`[dist-watcher] Failed to restart ${LAUNCHCTL_LABEL}:`, e.message);
  }
}

function check() {
  const runtimeStartMs = getRuntimeStartMs();
  if (!runtimeStartMs) {
    // Runtime isn't running — launchd will start it on its own (KeepAlive: true)
    console.log('[dist-watcher] Runtime not running — skipping check.');
    return;
  }

  const newestDistMs = getNewestDistMtimeMs();
  if (!newestDistMs) {
    console.log('[dist-watcher] No dist files found — skipping.');
    return;
  }

  const lagSec = Math.round((newestDistMs - runtimeStartMs) / 1000);

  if (newestDistMs > runtimeStartMs) {
    console.log(
      `[dist-watcher] dist/ is ${lagSec}s newer than running process — restarting.`
    );
    restartRuntime();
  } else {
    console.log(
      `[dist-watcher] dist/ is current (runtime started ${Math.abs(lagSec)}s after last dist change). OK.`
    );
  }
}

console.log(`[dist-watcher] Watching ${DIST_DIR} every ${CHECK_INTERVAL_MS / 1000}s`);
check(); // Run once immediately on startup
setInterval(check, CHECK_INTERVAL_MS);
