import fs from "node:fs";
import path from "node:path";
import os from "node:os";

const SESSIONS_FILE = path.join(os.homedir(), ".openclaw", "agents", "main", "sessions", "sessions.json");
const ALERT_FILE = path.join(os.homedir(), ".openclaw", "workspace", "memory", "context-alert.txt");

/**
 * Check session health and reset overflowing sessions.
 * @param {object} opts
 * @param {number} [opts.threshold=0.8] - Reset when estimated tokens exceed this fraction of contextTokens
 * @param {Function} [opts.log] - Logger function
 * @returns {{ checked: number, reset: string[] }} - Sessions checked and reset
 */
export function checkSessionHealth(opts = {}) {
  const threshold = opts.threshold || 0.8;
  const log = opts.log || console.log;
  const result = { checked: 0, reset: [] };

  if (!fs.existsSync(SESSIONS_FILE)) {
    log("session-guard: sessions.json not found, skipping");
    return result;
  }

  let sessions;
  try {
    sessions = JSON.parse(fs.readFileSync(SESSIONS_FILE, "utf-8"));
  } catch (e) {
    log(`session-guard: failed to parse sessions.json: ${e.message}`);
    return result;
  }

  let modified = false;

  for (const [key, entry] of Object.entries(sessions)) {
    if (!entry || typeof entry !== "object") continue;
    if (!entry.sessionFile || !entry.contextTokens) continue;

    result.checked++;
    const sessionFile = entry.sessionFile;
    const contextCap = entry.contextTokens;

    if (!fs.existsSync(sessionFile)) continue;

    let stat;
    try {
      stat = fs.statSync(sessionFile);
    } catch {
      continue;
    }

    const estTokens = Math.floor(stat.size / 4);
    const maxTokens = Math.floor(contextCap * threshold);

    if (estTokens > maxTokens) {
      log(`session-guard: ${key} overflow detected — ${estTokens} est tokens > ${maxTokens} max (file: ${(stat.size / 1024 / 1024).toFixed(1)} MB)`);

      // Back up the session file
      const ts = new Date().toISOString().replace(/[:.]/g, "-");
      const bakPath = sessionFile.replace(/\.jsonl$/, `.overflow-${ts}.bak`);
      try {
        fs.renameSync(sessionFile, bakPath);
        log(`session-guard: backed up to ${path.basename(bakPath)}`);
      } catch (e) {
        log(`session-guard: backup failed: ${e.message}`);
        continue;
      }

      // Reset session entry
      delete entry.sessionId;
      delete entry.sessionFile;
      delete entry.inputTokens;
      delete entry.outputTokens;
      delete entry.totalTokens;
      delete entry.systemSent;
      modified = true;
      result.reset.push(key);

      // Write alert
      try {
        const alertDir = path.dirname(ALERT_FILE);
        if (!fs.existsSync(alertDir)) fs.mkdirSync(alertDir, { recursive: true });
        fs.writeFileSync(ALERT_FILE, `Session ${key} auto-reset at ${new Date().toISOString()} (${estTokens} est tokens > ${maxTokens} cap).\n`);
      } catch {}
    }
  }

  if (modified) {
    try {
      fs.writeFileSync(SESSIONS_FILE, JSON.stringify(sessions, null, 2));
      log(`session-guard: sessions.json updated (${result.reset.length} sessions reset)`);
    } catch (e) {
      log(`session-guard: failed to write sessions.json: ${e.message}`);
    }
  }

  return result;
}
