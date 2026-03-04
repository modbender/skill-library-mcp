import fs from "node:fs";
import path from "node:path";
import os from "node:os";

const SESSIONS_FILE = path.join(os.homedir(), ".openclaw", "agents", "main", "sessions", "sessions.json");
const ALERT_FILE = path.join(os.homedir(), ".openclaw", "workspace", "memory", "context-alert.txt");

// ============================================================================
// Context pressure levels — controls budget scaling
// ============================================================================

/** Budget scale factors based on estimated context utilization. */
export const PRESSURE_LEVELS = {
  normal: 1.0,     // < 60% context used
  elevated: 0.75,  // 60-80% context used
  high: 0.5,       // 80-90% context used
  critical: 0.0,   // > 90% context used — stop injecting
};

// ============================================================================
// Startup health check (runs once at service start)
// ============================================================================

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

// ============================================================================
// Runtime context pressure (lightweight, called every Nth turn)
// ============================================================================

/**
 * Estimate current context pressure based on message count or byte estimate.
 * Returns a pressure level that the recall system uses to scale its budget.
 *
 * This is a lightweight check designed to run frequently (every 5-10 turns).
 * It does NOT read session files — it uses the event data available at runtime.
 *
 * @param {object} opts
 * @param {number} [opts.messageCount=0] - Number of messages in current session
 * @param {number} [opts.estimatedBytes=0] - Estimated session size in bytes (if available)
 * @param {number} [opts.contextCap=120000] - Context token cap for the model
 * @param {Function} [opts.log] - Logger
 * @returns {{ level: string, scale: number, pct: number }}
 */
export function getContextPressure(opts = {}) {
  const { messageCount = 0, estimatedBytes = 0, contextCap = 120000, log } = opts;

  // If we have a direct byte estimate, use it
  if (estimatedBytes > 0) {
    const estTokens = Math.floor(estimatedBytes / 4);
    const pct = estTokens / contextCap;

    let level, scale;
    if (pct >= 0.90) {
      level = "critical";
      scale = PRESSURE_LEVELS.critical;
    } else if (pct >= 0.80) {
      level = "high";
      scale = PRESSURE_LEVELS.high;
    } else if (pct >= 0.60) {
      level = "elevated";
      scale = PRESSURE_LEVELS.elevated;
    } else {
      level = "normal";
      scale = PRESSURE_LEVELS.normal;
    }

    if (log && level !== "normal") {
      log(`session-guard: context pressure ${level} (${(pct * 100).toFixed(0)}% of ${contextCap} cap)`);
    }
    return { level, scale, pct };
  }

  // Fallback: estimate from message count (rough heuristic: ~2000 tokens/message avg)
  if (messageCount > 0) {
    const estTokens = messageCount * 2000;
    const pct = estTokens / contextCap;

    let level, scale;
    if (pct >= 0.90) {
      level = "critical";
      scale = PRESSURE_LEVELS.critical;
    } else if (pct >= 0.80) {
      level = "high";
      scale = PRESSURE_LEVELS.high;
    } else if (pct >= 0.60) {
      level = "elevated";
      scale = PRESSURE_LEVELS.elevated;
    } else {
      level = "normal";
      scale = PRESSURE_LEVELS.normal;
    }

    if (log && level !== "normal") {
      log(`session-guard: context pressure ${level} (~${messageCount} msgs, est ${(pct * 100).toFixed(0)}% of cap)`);
    }
    return { level, scale, pct };
  }

  return { level: "normal", scale: PRESSURE_LEVELS.normal, pct: 0 };
}
