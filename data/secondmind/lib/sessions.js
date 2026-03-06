// lib/sessions.js – Robust OpenClaw sessions.json parser
// Handles multiple possible formats since the structure isn't documented precisely.
const path = require('path');
const fs = require('fs');
const os = require('os');
const { getConfig } = require('./db');

/**
 * Get the sessions directory path (resolved ~)
 * Auto-discovers: checks configured path first, then sessions/ subdirectory
 */
function getSessionsDir() {
  const config = getConfig();
  const configured = config.openclaw.sessionsDir.replace(/^~/, os.homedir());

  // Check if JSONL files exist at configured path
  if (hasJsonlFiles(configured)) return configured;

  // Auto-discover: check sessions/ subdirectory
  const withSub = path.join(configured, 'sessions');
  if (hasJsonlFiles(withSub)) return withSub;

  // Check parent (in case user pointed to sessions/ but JSONLs are one level up)
  const parent = path.dirname(configured);
  if (parent !== configured && hasJsonlFiles(parent)) return parent;

  // Also try: ~/.openclaw/agents/<agentId>/sessions/
  const agentId = config.openclaw.agentId || 'main';
  const agentSessions = path.join(os.homedir(), '.openclaw', 'agents', agentId, 'sessions');
  if (hasJsonlFiles(agentSessions)) return agentSessions;

  // Fallback: return configured path (will fail gracefully in callers)
  return configured;
}

function hasJsonlFiles(dir) {
  try {
    if (!fs.existsSync(dir)) return false;
    return fs.readdirSync(dir).some(f => f.endsWith('.jsonl'));
  } catch { return false; }
}

/**
 * Parse sessions.json robustly – handles all known/possible formats:
 *   - Array of objects: [{id: "abc", ...}, ...]
 *   - Array of strings: ["abc", "def"]
 *   - Object with channel keys: {":main": {sessionId: "abc"}, "telegram:topic:123": {...}}
 *   - Object with session IDs as keys: {"abc-def-123": {...}}
 *   - Single string (just the ID)
 *
 * Returns: Array of {sessionId, channel} objects, newest/main first
 */
function parseSessionsJson(sessionsDir) {
  const jsonPath = path.join(sessionsDir, 'sessions.json');
  if (!fs.existsSync(jsonPath)) return [];

  let raw;
  try {
    raw = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
  } catch {
    return [];
  }

  const results = [];

  if (typeof raw === 'string') {
    // Single session ID string
    results.push({ sessionId: raw, channel: 'default' });

  } else if (Array.isArray(raw)) {
    for (const item of raw) {
      if (typeof item === 'string') {
        results.push({ sessionId: item, channel: 'default' });
      } else if (typeof item === 'object' && item) {
        const sid = item.id || item.sessionId || item.session_id;
        if (sid) results.push({ sessionId: sid, channel: item.channel || 'default' });
      }
    }

  } else if (typeof raw === 'object' && raw) {
    // Object form – keys could be channel names OR session IDs
    for (const [key, value] of Object.entries(raw)) {
      if (typeof value === 'object' && value) {
        // Key is probably channel (":main", "telegram:topic:123")
        const sid = value.id || value.sessionId || value.session_id;
        if (sid) {
          results.push({ sessionId: sid, channel: key });
        } else if (looksLikeSessionId(key)) {
          // Key IS the session ID, value is metadata
          results.push({ sessionId: key, channel: value.channel || 'default' });
        }
      } else if (typeof value === 'string') {
        // {channel: sessionId} or {sessionId: status}
        if (looksLikeSessionId(value)) {
          results.push({ sessionId: value, channel: key });
        } else if (looksLikeSessionId(key)) {
          results.push({ sessionId: key, channel: 'default' });
        }
      }
    }
  }

  // Deduplicate by sessionId
  const seen = new Set();
  return results.filter(r => {
    if (!r.sessionId || seen.has(r.sessionId)) return false;
    seen.add(r.sessionId);
    return true;
  });
}

/**
 * Heuristic: Does this string look like a session ID?
 * UUIDs, hex strings, or similar patterns (not channel names like ":main")
 */
function looksLikeSessionId(s) {
  if (!s || typeof s !== 'string') return false;
  if (s.startsWith(':') || s.startsWith('telegram:') || s.startsWith('discord:')) return false;
  // UUID-ish or hex-ish (at least 8 chars, contains digits)
  return s.length >= 8 && /[0-9a-f-]{8,}/i.test(s);
}

/**
 * Get all active session IDs (convenience)
 */
function getActiveSessions(sessionsDir) {
  return parseSessionsJson(sessionsDir || getSessionsDir());
}

/**
 * Get the "current" / most likely active session
 * Prefers :main channel, falls back to first entry
 */
function getCurrentSession(sessionsDir) {
  const sessions = getActiveSessions(sessionsDir);
  if (sessions.length === 0) return null;
  // Prefer main channel
  const main = sessions.find(s =>
    s.channel === 'default' || s.channel === ':main' || s.channel === 'main'
  );
  return main || sessions[0];
}

/**
 * Fallback: Scan JSONL files to find most recently modified session
 * Used when sessions.json is missing or unparseable
 */
function getMostRecentSession(sessionsDir) {
  const dir = sessionsDir || getSessionsDir();
  if (!fs.existsSync(dir)) return null;

  const files = fs.readdirSync(dir)
    .filter(f => f.endsWith('.jsonl'))
    .map(f => ({
      name: f,
      sessionId: f.replace('.jsonl', '').split('-topic-')[0],
      mtime: fs.statSync(path.join(dir, f)).mtimeMs
    }))
    .sort((a, b) => b.mtime - a.mtime);

  return files.length > 0 ? { sessionId: files[0].sessionId, channel: 'default' } : null;
}

module.exports = {
  getSessionsDir, parseSessionsJson, getActiveSessions,
  getCurrentSession, getMostRecentSession, looksLikeSessionId
};
