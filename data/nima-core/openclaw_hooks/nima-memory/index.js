/**
 * NIMA Unified Memory Hook
 * ========================
 * Captures ALL three memory layers from a single agent_end hook:
 *   1. INPUT  - what was said to the agent (user message)
 *   2. CONTEMPLATION - the agent's thinking/reasoning (strange loop)
 *   3. OUTPUT - what the agent responded
 *
 * Each layer is bound to the current affect state at time of capture.
 * Memories are stored to a SQLite graph for relationship-aware recall.
 *
 * Replaces: nima-capture hook (now redundant)
 * Requires: nima-affect plugin (for affect state)
 *
 * Hook Events:
 *   agent_end → extract 3 layers from messages snapshot, bind affect, store
 *
 * Author: David Dorta + Lilu
 * Date: 2026-02-13
 * Updated: 2026-02-13 (Security & correctness fixes)
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync, unlinkSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";
import os from "node:os";
import { randomBytes } from "node:crypto";

// ═══════════════════════════════════════════════════════════════════════════════
// INLINED: shared/error-handling.js + utils/async-python.js
// Self-contained — no cross-directory imports needed.
// ═══════════════════════════════════════════════════════════════════════════════

import { promisify } from "node:util";
import { execFile } from "node:child_process";

// --- Error Handling Utilities ---

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function isTransientError(err) {
  if (!err) return false;
  const message = (err.message || '').toLowerCase();
  const code = err.code || '';
  const status = err.status || err.statusCode || 0;
  if (['ETIMEDOUT', 'ECONNRESET', 'ECONNREFUSED', 'ENOTFOUND', 'EPIPE'].includes(code)) return true;
  if (message.includes('sqlite_busy') || message.includes('sqlite_locked') || message.includes('database is locked')) return true;
  if (status === 429 || (status >= 500 && status < 600)) return true;
  if (message.includes('timeout') || message.includes('timed out')) return true;
  if (message.includes('rate limit') || message.includes('too many requests')) return true;
  return false;
}

async function retryWithBackoff(fn, options = {}) {
  const { maxRetries = 3, baseDelayMs = 1000, maxDelayMs = 10000, shouldRetry = isTransientError, onRetry = null } = options;
  let lastError;
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try { return await fn(); } catch (err) {
      lastError = err;
      if (attempt >= maxRetries || !shouldRetry(err)) throw err;
      const exponentialDelay = baseDelayMs * Math.pow(2, attempt - 1);
      const delay = Math.min(exponentialDelay + Math.random() * 0.3 * exponentialDelay, maxDelayMs);
      if (onRetry) onRetry(attempt, err, delay);
      await sleep(delay);
    }
  }
  throw lastError || new Error('Retry failed');
}

function retrySync(fn, options = {}) {
  const { maxRetries = 3, baseDelayMs = 500, maxDelayMs = 5000, shouldRetry = isTransientError, onRetry = null } = options;
  let lastError;
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try { return fn(); } catch (err) {
      lastError = err;
      if (attempt >= maxRetries || !shouldRetry(err)) throw err;
      const delay = Math.min(baseDelayMs * Math.pow(2, attempt - 1), maxDelayMs);
      if (onRetry) onRetry(attempt, err, delay);
      const buffer = new SharedArrayBuffer(4);
      Atomics.wait(new Int32Array(buffer), 0, 0, delay);
    }
  }
  throw lastError || new Error('Retry failed');
}

function safeJsonParse(jsonString, options = {}) {
  const { context = 'JSON', validator = null, defaultValue = undefined } = options;
  if (jsonString === null || jsonString === undefined || jsonString === '') {
    if (defaultValue !== undefined) return defaultValue;
    throw new Error(`${context}: Empty or null input`);
  }
  const str = String(jsonString).trim();
  if (!str) {
    if (defaultValue !== undefined) return defaultValue;
    throw new Error(`${context}: Empty string after trimming`);
  }
  let parsed;
  try { parsed = JSON.parse(str); } catch (parseErr) {
    const preview = str.length > 500 ? str.substring(0, 500) + '...' : str;
    const err = new Error(`${context}: Invalid JSON - ${parseErr.message}. Preview: ${preview}`);
    if (defaultValue !== undefined) { console.error(`[safe-json-parse] ${err.message}`); return defaultValue; }
    throw err;
  }
  if (validator && typeof validator === 'function') {
    try { if (!validator(parsed)) {
      const err = new Error(`${context}: Validation failed`);
      if (defaultValue !== undefined) return defaultValue;
      throw err;
    }} catch (e) {
      if (e.message.includes('Validation failed')) throw e;
      if (defaultValue !== undefined) return defaultValue;
      throw e;
    }
  }
  return parsed;
}

function wrapError(err, context, metadata = {}) {
  const wrapped = new Error(`[${context}] ${err.message}`);
  wrapped.cause = err;
  wrapped.originalStack = err.stack;
  if (err.code) wrapped.code = err.code;
  for (const [k, v] of Object.entries(metadata)) wrapped[k] = v;
  wrapped.stack = `${wrapped.stack}\n\nCaused by:\n${err.stack}`;
  return wrapped;
}

function createCircuitBreaker(options = {}) {
  const { failureThreshold = 5, resetTimeoutMs = 30000, successThreshold = 2 } = options;
  let state = 'CLOSED', failures = 0, successes = 0, lastFailureTime = 0;
  return {
    getState() { return state; },
    async execute(fn) {
      if (state === 'OPEN') {
        if (Date.now() - lastFailureTime > resetTimeoutMs) { state = 'HALF_OPEN'; successes = 0; }
        else throw new Error('Circuit breaker is OPEN');
      }
      try {
        const result = await fn();
        if (state === 'HALF_OPEN') { successes++; if (successes >= successThreshold) { state = 'CLOSED'; failures = 0; } }
        else failures = 0;
        return result;
      } catch (err) { failures++; lastFailureTime = Date.now(); if (failures >= failureThreshold) state = 'OPEN'; throw err; }
    },
    reset() { state = 'CLOSED'; failures = 0; successes = 0; lastFailureTime = 0; }
  };
}

// --- Async Python Execution ---

const execFileAsync = promisify(execFile);

class SimpleRateLimiter {
  constructor(tokensPerInterval, interval) {
    this.tokensPerInterval = tokensPerInterval;
    this.interval = interval === 'second' ? 1000 : interval;
    this.tokens = tokensPerInterval;
    this.lastRefill = Date.now();
  }
  async removeTokens(count) {
    this.refill();
    if (this.tokens >= count) { this.tokens -= count; return true; }
    const timeToNext = this.interval - (Date.now() - this.lastRefill);
    if (timeToNext > 0) { await new Promise(r => setTimeout(r, timeToNext)); this.refill(); }
    if (this.tokens >= count) { this.tokens -= count; return true; }
    return false;
  }
  refill() {
    if (Date.now() - this.lastRefill >= this.interval) { this.tokens = this.tokensPerInterval; this.lastRefill = Date.now(); }
  }
}

const pythonSpawnLimiter = new SimpleRateLimiter(10, 'second');

async function execPython(scriptPath, args = [], options = {}) {
  const { breakerId = "default", ...execOptions } = options;
  // Simple per-id breaker
  if (!execPython._breakers) execPython._breakers = new Map();
  if (!execPython._breakers.has(breakerId)) {
    execPython._breakers.set(breakerId, { failures: 0, lastFail: 0, state: "CLOSED" });
  }
  const b = execPython._breakers.get(breakerId);
  if (b.state === "OPEN") {
    if (Date.now() - b.lastFail > 60000) b.state = "HALF-OPEN";
    else throw new Error(`Circuit breaker '${breakerId}' is OPEN`);
  }
  await pythonSpawnLimiter.removeTokens(1);
  try {
    const venvPython = join(os.homedir(), ".openclaw", "workspace", ".venv", "bin", "python3");
    let cmd, finalArgs;
    if (scriptPath.endsWith(".py") || scriptPath === "python3") {
      cmd = venvPython; finalArgs = scriptPath === "python3" ? args : [scriptPath, ...args];
    } else { cmd = scriptPath; finalArgs = args; }
    const { stdout } = await execFileAsync(cmd, finalArgs, { encoding: "utf-8", maxBuffer: 10 * 1024 * 1024, ...execOptions });
    b.failures = 0; b.state = "CLOSED";
    return stdout;
  } catch (err) { b.failures++; b.lastFail = Date.now(); if (b.failures >= 5) b.state = "OPEN"; throw err; }
}

// ═══════════════════════════════════════════════════════════════════════════════
// END INLINED UTILITIES
// ═══════════════════════════════════════════════════════════════════════════════

// Circuit breaker to prevent cascading failures to SQLite
const dbCircuitBreaker = createCircuitBreaker({
  failureThreshold: 5,
  resetTimeoutMs: 60000,  // 1 minute cooldown
  successThreshold: 2
});

// Log helper (set by plugin init)
let log = console;

// CONCURRENCY CONTROL
const writeQueue = [];
let isWriting = false;
let initPromise = null;

// PHASE 4 FIX: Memory capture metrics for monitoring noise filtering
const captureMetrics = {
  totalProcessed: 0,
  stored: 0,
  filteredEmpty: 0,
  filteredNoise: 0,
  filteredFE: 0,
  filteredHeartbeat: 0,
  errors: 0,
  lastReset: Date.now(),
  
  // Log and reset daily
  logAndReset() {
    const log = console;
    log.info?.(`[nima-memory] 📊 Daily Stats: processed=${this.totalProcessed}, stored=${this.stored}, ` +
      `filtered={empty:${this.filteredEmpty}, noise:${this.filteredNoise}, fe:${this.filteredFE}, hb:${this.filteredHeartbeat}}, ` +
      `errors=${this.errors}`);
    
    // Reset counters
    this.totalProcessed = 0;
    this.stored = 0;
    this.filteredEmpty = 0;
    this.filteredNoise = 0;
    this.filteredFE = 0;
    this.filteredHeartbeat = 0;
    this.errors = 0;
    this.lastReset = Date.now();
  }
};

// Schedule daily metrics log (if not in test environment)
if (typeof process !== 'undefined' && !process.env.NIMA_TEST_MODE) {
  setInterval(() => {
    captureMetrics.logAndReset();
  }, 24 * 60 * 60 * 1000); // 24 hours
}

// =============================================================================
// CONFIGURATION
// =============================================================================

const NIMA_HOME = join(os.homedir(), ".nima");
const MEMORY_DIR = join(NIMA_HOME, "memory");
const GRAPH_DB = join(MEMORY_DIR, "graph.sqlite");
const LADYBUG_DB = join(MEMORY_DIR, "ladybug.lbug");
const AFFECT_DIR = join(NIMA_HOME, "affect", "conversations");
const EMERGENCY_DIR = join(MEMORY_DIR, "emergency_backups");
const USE_LADYBUG_WRITE = true; // Dual-write to LadybugDB (default: true)

// Content length limits (security - prevent DoS via oversized content)
const MAX_TEXT_LENGTH = 3000;
const MAX_SUMMARY_LENGTH = 300;

// Max lengths for compressed summaries (Layer 2)
const MAX_SUMMARY_INPUT = 80; // ~10-20 tokens
const MAX_THINKING_SUMMARY = 120;
const MAX_OUTPUT_SUMMARY = 100;

// =============================================================================
// SECURITY: Path Sanitization
// =============================================================================

/**
 * Sanitize a string for safe use in file paths.
 * Prevents path traversal attacks (e.g., "../../etc/passwd").
 * 
 * @param {string} name - Input string (e.g., identityName, conversationId)
 * @param {number} maxLength - Maximum allowed length (default 100)
 * @returns {string} Sanitized string containing only [a-zA-Z0-9_-]
 */
function sanitizePathComponent(name, maxLength = 100) {
  if (typeof name !== "string") {
    name = name != null ? String(name) : "";
  }
  // Remove path separators and parent directory references
  name = name.replace(/\//g, "_").replace(/\\/g, "_").replace(/\.\./g, "");
  // Keep only alphanumeric, dash, underscore
  name = name.replace(/[^a-zA-Z0-9_-]/g, "_");
  // Collapse multiple underscores
  name = name.replace(/_+/g, "_");
  // Remove leading/trailing underscores
  name = name.replace(/^_+|_+$/g, "");
  // Ensure non-empty
  if (!name) name = "default";
  // Truncate if too long
  if (name.length > maxLength) name = name.slice(0, maxLength);
  return name;
}

// =============================================================================
// MEMORY RECORD
// =============================================================================

/**
 * Truncate text to max length (security boundary).
 * 
 * SECURITY: Applies Unicode normalization to prevent injection bypass.
 * Fixed 2026-02-16 - CVE pending assignment.
 */
function truncateText(text, maxLen) {
  if (!text) return "";
  // SECURITY FIX: Normalize Unicode before processing
  const normalized = typeof text === 'string' ? text.normalize('NFKC') : String(text);
  if (normalized.length <= maxLen) return normalized;
  return normalized.substring(0, maxLen);
}

/**
 * Calculate Free Energy (FE) score for a memory.
 * FE = prediction_error = how surprising/novel an experience is.
 * 
 * Factors:
 *   - Affect variance (emotional dynamism)
 *   - Text length (very short = likely monotonous)
 *   - Repetition detection (similar to recent memories)
 * 
 * Returns: 0.0 (monotonous) to 1.0 (highly novel)
 */
function calculateFEScore(input, contemplation, output, affect) {
  let fe = 0.5; // Default: moderately novel
  
  // Factor 1: Affect variance (emotional dynamism)
  if (affect && Object.keys(affect).length > 0) {
    const values = Object.values(affect);
    const max = Math.max(...values);
    const min = Math.min(...values);
    const variance = max - min;
    // High variance = more novel experience
    fe += variance * 0.3;
  }
  
  // Factor 2: Content richness
  const inputLen = (input?.text || "").length;
  const thinkLen = (contemplation?.text || "").length;
  const outLen = (output?.text || "").length;
  
  // Very short exchanges are likely routine
  if (inputLen < 20 && outLen < 50) {
    fe -= 0.2; // Likely short acknowledgment
  }
  if (thinkLen > 100) {
    fe += 0.1; // Agent did real thinking
  }
  
  // Factor 3: Check for monotonous patterns
  const inputSummary = (input?.summary || "").toLowerCase().trim();
  const monotonousPatterns = [
    /^heartbeat_ok$/i,
    /^heartbeat check$/i,
    /^hygiene check$/i,
    /^ok$/i,
    /^yes$/i,
    /^no$/i,
    /^sure$/i,
    /^got it$/i,
    /^thanks$/i,
    /^thank you$/i,
    /gateway.?restart/i,
  ];
  for (const pattern of monotonousPatterns) {
    if (pattern.test(inputSummary)) {
      fe -= 0.4;
      break;
    }
  }
  
  // Clamp to [0, 1]
  return Math.max(0, Math.min(1, fe));
}

/**
 * Calculate FE score with configurable weights.
 * Uses config values for tuning without code changes.
 */
function calculateFEScoreWithConfig(input, contemplation, output, affect, config) {
  let fe = 0.5; // Default: moderately novel
  
  // Factor 1: Affect variance (emotional dynamism)
  if (affect && Object.keys(affect).length > 0) {
    const values = Object.values(affect);
    const max = Math.max(...values);
    const min = Math.min(...values);
    const variance = max - min;
    // High variance = more novel experience
    fe += variance * config.affectVarianceWeight;
  }
  
  // Factor 2: Content richness
  const inputLen = (input?.text || "").length;
  const thinkLen = (contemplation?.text || "").length;
  const outLen = (output?.text || "").length;
  
  // Very short exchanges are likely routine
  if (inputLen < 20 && outLen < 50) {
    fe -= config.routinePenalty;
  }
  if (thinkLen > 100) {
    fe += config.thinkingBoost;
  }
  
  // Factor 3: Check for monotonous patterns
  const inputSummary = (input?.summary || "").toLowerCase().trim();
  const monotonousPatterns = [
    /^heartbeat_ok$/i,
    /^heartbeat check$/i,
    /^hygiene check$/i,
    /^ok$/i,
    /^yes$/i,
    /^no$/i,
    /^sure$/i,
    /^got it$/i,
    /^thanks$/i,
    /^thank you$/i,
    /gateway.?restart/i,
  ];
  for (const pattern of monotonousPatterns) {
    if (pattern.test(inputSummary)) {
      fe -= config.monotonousPenalty;
      break;
    }
  }
  
  // Clamp to [0, 1]
  return Math.max(0, Math.min(1, fe));
}

/**
 * A single memory record with all three layers + affect binding.
 */
function createMemoryRecord(input, contemplation, output, affect, metadata) {
  return {
    timestamp: Date.now(),
    layers: {
      input: {
        text: truncateText(input?.text || "", MAX_TEXT_LENGTH),
        summary: summarize(input?.text, MAX_SUMMARY_INPUT),
        who: truncateText(input?.who || "unknown", 100),
      },
      contemplation: {
        text: truncateText(contemplation?.text || "", MAX_TEXT_LENGTH),
        summary: summarize(contemplation?.text, MAX_THINKING_SUMMARY),
      },
      output: {
        text: truncateText(output?.text || "", MAX_TEXT_LENGTH),
        summary: summarize(output?.text, MAX_OUTPUT_SUMMARY),
      },
    },
    affect: affect ? { ...affect } : null,
    metadata: {
      sessionKey: truncateText(metadata.sessionKey || "", 200),
      conversationId: truncateText(metadata.conversationId || "", 200),
      agentId: truncateText(metadata.agentId || "", 100),
      durationMs: metadata.durationMs || 0,
      feScore: metadata.feScore || 0.5,
    },
  };
}

/**
 * Compress text to a short summary (Layer 2).
 * Simple truncation with ellipsis - can be replaced with LLM summarization later.
 * Enforces MAX_SUMMARY_LENGTH limit.
 */
function summarize(text, maxLen) {
  if (!text) return "";
  // Enforce global summary length limit
  const effectiveMax = Math.min(maxLen, MAX_SUMMARY_LENGTH);
  // Strip newlines, collapse whitespace
  const clean = text.replace(/\n+/g, " ").replace(/\s+/g, " ").trim();
  if (clean.length <= effectiveMax) return clean;
  return clean.substring(0, effectiveMax - 3) + "...";
}

// =============================================================================
// AFFECT STATE READER
// =============================================================================

function readAffectState(conversationId, identityName) {
  try {
    // Security: Sanitize inputs to prevent path traversal attacks
    const safeIdentity = sanitizePathComponent(identityName, 64);
    const safeConvId = conversationId ? sanitizePathComponent(conversationId, 64) : null;
    
    // Try conversation-specific state first
    if (safeConvId) {
      const convPath = join(AFFECT_DIR, `${safeIdentity}_${safeConvId}.json`);
      if (existsSync(convPath)) {
        const data = JSON.parse(readFileSync(convPath, "utf-8"));
        return data.current?.named || null;
      }
    }
    // Fall back to shared state
    const sharedPath = join(NIMA_HOME, "affect", `affect_state_${safeIdentity}.json`);
    if (existsSync(sharedPath)) {
      const data = JSON.parse(readFileSync(sharedPath, "utf-8"));
      return data.current?.named || null;
    }
  } catch (err) {
    console.error(`[nima-memory] Failed to read affect state: ${err.message}`);
  }
  return null;
}

// =============================================================================
// INPUT TEXT CLEANING
// =============================================================================

/**
 * Strip injected context blocks from input text.
 * Removes:
 *   - [NIMA RECALL - ...] blocks (injected by recall hooks)
 *   - 🎭 AFFECT STATE blocks (injected by affect plugin)
 *   - [message_id: ...] trailers
 *   - Heartbeat instruction text (system mechanics, not user message)
 *
 * This prevents feedback loops where recall output gets stored as memory input.
 * 
 * SECURITY: Applies Unicode normalization (NFKC) to prevent bypass attacks
 * using homoglyphs or fullwidth characters.
 * Fixed 2026-02-16 - CVE pending assignment.
 */
function cleanInputText(text) {
  if (!text || typeof text !== "string") return "";

  // SECURITY FIX: Unicode normalization prevents bypass via homoglyphs
  // NFKC: Canonical decomposition + compatibility composition
  // This normalizes fullwidth chars (e.g., \uff07 → ') and other Unicode tricks
  let cleaned = text.normalize('NFKC');

  // Remove NIMA RECALL blocks (multiline, non-greedy)
  cleaned = cleaned.replace(/\[NIMA RECALL[^\]]*\][\s\S]*?\[End recall[^\]]*\]\s*/gi, "");

  // Remove 🎭 AFFECT STATE blocks (usually single-line or short multi-line)
  cleaned = cleaned.replace(/🎭\s*AFFECT STATE[^\n]*(\n[^\n]*){0,3}\n*/g, "");

  // Remove [Dynamic affect... line
  cleaned = cleaned.replace(/\[Dynamic affect[^\]]*\]\s*/gi, "");

  // Remove [message_id: ...] trailers
  cleaned = cleaned.replace(/\[message_id:\s*[^\]]+\]\s*/gi, "");

  // Remove "Conversation info (untrusted metadata)" blocks (JSON metadata injected by gateway)
  cleaned = cleaned.replace(/Conversation info \(untrusted metadata\)[^\n]*\n?```json[\s\S]*?```\s*/gi, "");
  cleaned = cleaned.replace(/Conversation info \(untrusted metadata\)[^\n]*\n/gi, "");

  // Remove inbound metadata JSON blocks
  cleaned = cleaned.replace(/```json\s*\{\s*"(?:schema|message_id|sender)"[\s\S]*?\}\s*```\s*/g, "");

  // Remove heartbeat instruction text (system mechanics)
  cleaned = cleaned.replace(/Read HEARTBEAT\.md if it exists[^\n]*\n*/gi, "");

  // Remove multiple consecutive blank lines
  cleaned = cleaned.replace(/\n{3,}/g, "\n\n");

  return cleaned.trim();
}

/**
 * Check if a contemplation is just heartbeat mechanics (noise).
 * These repeated internal thoughts aren't meaningful experiences.
 */
function isHeartbeatNoise(text) {
  if (!text || typeof text !== "string") return false;

  const noisePatterns = [
    /heartbeat (check|poll|cycle)/i,
    /hygiene check/i,
    /HEARTBEAT_OK/i,
    /run.*hygiene/i,
    /another heartbeat/i,
    /sending another heartbeat/i,
  ];

  return noisePatterns.some(p => p.test(text));
}

/**
 * Load and cache .nimaignore patterns.
 * Reads from ~/.nima/.nimaignore or package directory.
 */
let nimaIgnorePatterns = null;
function loadNimaIgnore() {
  if (nimaIgnorePatterns !== null) return nimaIgnorePatterns;
  
  const fs = require('fs');
  const path = require('path');
  const homedir = require('os').homedir();
  
  // Try multiple locations
  const locations = [
    path.join(homedir, '.nima', '.nimaignore'),
    path.join(__dirname, '..', '..', '.nimaignore'),
    path.join(__dirname, '.nimaignore'),
  ];
  
  for (const loc of locations) {
    try {
      if (fs.existsSync(loc)) {
        const content = fs.readFileSync(loc, 'utf8');
        const lines = content.split('\n');
        nimaIgnorePatterns = lines
          .map(l => l.trim())
          .filter(l => l && !l.startsWith('#'))
          .map(pattern => {
            // Convert glob to regex
            const escaped = pattern
              .replace(/[.+^${}()|[\]\\]/g, '\\$&')  // Escape special regex chars
              .replace(/\*/g, '.*')                   // * → .*
              .replace(/\?/g, '.');                   // ? → .
            return new RegExp(escaped, 'i');
          });
        console.log(`[nima-memory] Loaded ${nimaIgnorePatterns.length} .nimaignore patterns from ${loc}`);
        return nimaIgnorePatterns;
      }
    } catch (e) {
      // Ignore errors, try next location
    }
  }
  
  nimaIgnorePatterns = [];
  return nimaIgnorePatterns;
}

/**
 * Check if text matches any .nimaignore pattern.
 */
function matchesNimaIgnore(text) {
  if (!text || typeof text !== 'string') return false;
  
  const patterns = loadNimaIgnore();
  if (!patterns.length) return false;
  
  return patterns.some(p => p.test(text));
}

/**
 * Check if content is system noise that shouldn't be stored as memory.
 * Filters out gateway restarts, doctor hints, session metadata, etc.
 */
function isSystemNoise(text) {
  if (!text || typeof text !== "string") return false;

  const noisePatterns = [
    // Gateway/system messages
    /^GatewayRestart:/i,
    /"kind":\s*"restart"/i,
    /"status":\s*"ok"/i,
    /doctorHint/i,
    /Run: openclaw doctor/i,
    
    // Session/channel metadata
    /"sessionKey":/i,
    /"deliveryContext":/i,
    /"accountId":/i,
    /"channel":/i,
    
    // Queue/compaction markers (the prefix, not user content after)
    /^\[Queued messages while agent was busy\]/i,
    /^---\s*Queue/i,
    /^Queued #\d+$/i,
    
    // Raw JSON that looks like system output
    /^\{[\s\S]*"kind":/i,
    /^\{[\s\S]*"stats":/i,
    
    // Compaction messages
    /Pre-compaction memory flush/i,
    /HEARTBEAT_OK/i,
    /NO_REPLY/i,
    
    // PHASE 2 FIX: HEARTBEAT instruction mentions (not the literal OK, but context)
    /Read HEARTBEAT\.md if it exists/i,
    /If nothing needs attention.*HEARTBEAT_OK/i,
    
    // PHASE 2 FIX: Tool output noise
    /\[object Object\]/,
    /^undefined$/,
    /^null$/,
    /^\[?[\s\S]*"tool":\s*"exec"[\s\S]*\]?$/, // Raw tool JSON
    /^\{[\s\S]*"tool"[\s\S]*\}$/, // Tool result JSON
    
    // Empty or too short after cleaning
    /^\.+$/,  // Just dots
    /^!+$/,   // Just exclamation marks
    /^\?+$/,  // Just question marks
  ];

  // Check .nimaignore patterns
  if (matchesNimaIgnore(text)) return true;

  return noisePatterns.some(p => p.test(text));
}

/**
 * Check if a memory would be low quality (not worth storing).
 * Uses FE score heuristic and content quality checks.
 * PHASE 1 FIX: Added empty string validation and contemplation checks
 */
function isLowQualityMemory(input, output, contemplation) {
  // PHASE 1 FIX: Skip empty strings in any layer
  const inputTrimmed = (input || "").trim();
  const outputTrimmed = (output || "").trim();
  const contemplationTrimmed = (contemplation || "").trim();
  
  // Skip if ALL layers are empty (nothing to store)
  if (!inputTrimmed && !outputTrimmed && !contemplationTrimmed) return true;
  
  // PHASE 1 FIX: Skip if input is empty string (not just falsy)
  if (input === "" || (inputTrimmed === "" && input !== undefined)) return true;
  
  // PHASE 1 FIX: Skip empty contemplation unless input/output have substance
  if (contemplation === "" && !inputTrimmed && !outputTrimmed) return true;
  
  // Skip if input is system noise
  if (isSystemNoise(input)) return true;
  
  // Skip if output is system noise (gateway restarts, etc.)
  if (isSystemNoise(output)) return true;
  
  // PHASE 1 FIX: Skip if contemplation is system noise
  if (isSystemNoise(contemplation)) return true;
  
  // Skip if both input and output are empty
  if (!input && !output) return true;
  
  // Skip very short exchanges (likely noise)
  const inputLen = inputTrimmed.length;
  const outputLen = outputTrimmed.length;
  if (inputLen < 5 && outputLen < 20) return true;
  
  // PHASE 1 FIX: Skip if contemplation is very short and input is also short
  const contemplationLen = contemplationTrimmed.length;
  if (contemplationLen < 3 && inputLen < 10 && outputLen < 30) return true;
  
  // Skip single-word inputs (likely routine acknowledgment)
  const inputWords = inputTrimmed.split(/\s+/).filter(w => w.length > 0);
  if (inputWords.length <= 1 && inputLen < 10) return true;
  
  // PHASE 2 FIX: Skip punctuation-only content
  const isJustPunctuation = /^[^a-zA-Z0-9]*$/.test(inputTrimmed) 
    && /^[^a-zA-Z0-9]*$/.test(outputTrimmed)
    && inputLen > 0;
  if (isJustPunctuation) return true;
  
  return false;
}

// =============================================================================
// MESSAGE EXTRACTION
// =============================================================================

/**
 * Extract the three layers from the messages snapshot.
 * Returns { input, contemplation, output }
 */
function extractLayers(messages, ctx) {
  if (!messages || !Array.isArray(messages) || messages.length === 0) {
    return null;
  }

  // Find the last user message (INPUT)
  let lastUserMsg = null;
  let lastAssistantMsg = null;

  // Walk backwards to find the last user→assistant pair
  for (let i = messages.length - 1; i >= 0; i--) {
    const msg = messages[i];
    // Handle both nested (msg.message.role) and flat (msg.role) structures
    const role = msg.role || msg.message?.role;
    if (!lastAssistantMsg && role === "assistant") {
      lastAssistantMsg = msg.message || msg;
    }
    if (lastAssistantMsg && role === "user") {
      lastUserMsg = msg.message || msg;
      break;
    }
  }

  if (!lastAssistantMsg) return null;

  // Extract input text
  let inputText = "";
  let inputWho = "unknown";
  if (lastUserMsg) {
    const content = lastUserMsg.content;
    if (typeof content === "string") {
      inputText = content;
    } else if (Array.isArray(content)) {
      inputText = content
        .filter((c) => c.type === "text")
        .map((c) => c.text)
        .join("\n");
    }
    // Try to extract sender from message format (expanded channel support)
    const senderMatch = inputText.match(/\[(?:Telegram|Discord|Signal|SMS|Slack|Matrix|WhatsApp|iMessage|Email)\s+(.+?)\s+(?:id|ID|Id):/);
    if (senderMatch) {
      inputWho = senderMatch[1];
    } else if (ctx) {
      // Debug: Log ctx fields to understand what's available
      if (process.env.DEBUG_NIMA) {
        console.error('[nima-memory] DEBUG ctx keys:', Object.keys(ctx));
      }
      // Fallback: Use context metadata for webchat and other channels
      // Check common field names for user identity
      if (ctx.userName) {
        inputWho = ctx.userName;
      } else if (ctx.userDisplayName) {
        inputWho = ctx.userDisplayName;
      } else if (ctx.userId) {
        inputWho = ctx.userId;
      } else if (ctx.senderId) {
        inputWho = ctx.senderId;
      } else if (ctx.from) {
        inputWho = ctx.from;
      } else if (ctx.accountId) {
        inputWho = ctx.accountId;
      } else if (ctx.conversationId) {
        // Last resort: Use conversationId as part of attribution
        inputWho = "user";
      }
    }
    
    // HEURISTIC: If still "unknown" or generic "user"/"User" and in main session, default to owner
    // This handles messages with timestamp prefixes (no channel prefix) in direct chats
    // Also handles TUI/webchat where sender info may not be properly passed
    const isGenericUser = inputWho === "unknown" || String(inputWho).toLowerCase() === "user";
    const isMainSession = ctx?.sessionKey === "agent:main:main" || String(ctx?.conversationId ?? "").includes("main");
    const isDavidUser = String(ctx?.userId ?? "") === "5556407150" || String(ctx?.from ?? "").includes("5556407150") || ctx?.accountId === "default";
    
    if ((isGenericUser && isMainSession) || isDavidUser) {
      inputWho = "David Dorta";
    }

    // Clean injected context blocks (NIMA RECALL, AFFECT STATE) to prevent feedback loops
    inputText = cleanInputText(inputText);
  }

  // Extract thinking (CONTEMPLATION) and response (OUTPUT)
  let thinkingText = "";
  let outputText = "";
  const content = lastAssistantMsg.content;
  
  if (typeof content === "string") {
    outputText = content;
  } else if (Array.isArray(content)) {
    for (const block of content) {
      if (block.type === "thinking" && block.thinking) {
        thinkingText += block.thinking + "\n";
      } else if (block.type === "text" && block.text) {
        outputText += block.text + "\n";
      }
    }
  }

  // Filter out heartbeat noise from contemplation
  // These are repetitive system mechanics, not meaningful experiences
  if (isHeartbeatNoise(thinkingText)) {
    thinkingText = "";  // Don't store heartbeat mechanics as contemplation
  }

  return {
    input: { text: inputText.trim(), who: inputWho },
    contemplation: { text: thinkingText.trim() },
    output: { text: outputText.trim() },
  };
}

// =============================================================================
// STORAGE (SQLite Graph)
// =============================================================================

/**
 * Internal DB initialization logic.
 * Called via atomic ensureInitialized().
 */
async function _initDatabase() {
  ensureDir(MEMORY_DIR);
  ensureDir(EMERGENCY_DIR);  // Emergency backup directory for fallback storage

  // Python script with parameterized DB path (no injection)
  const initSQL = `
import sqlite3, sys

# Read DB path from argument (no injection risk)
db_path = sys.argv[1] if len(sys.argv) > 1 else None
if not db_path:
    print("error:no_db_path", file=sys.stderr)
    sys.exit(1)

try:
  with sqlite3.connect(db_path, timeout=5.0) as db:
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")

    # Nodes table - each memory record
    db.execute("""
    CREATE TABLE IF NOT EXISTS memory_nodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp INTEGER NOT NULL,
        layer TEXT NOT NULL CHECK(layer IN ('input', 'contemplation', 'output', 'legacy_vsa')),
        text TEXT NOT NULL,
        summary TEXT NOT NULL,
        who TEXT DEFAULT '',
        affect_json TEXT DEFAULT '{}',
        session_key TEXT DEFAULT '',
        conversation_id TEXT DEFAULT '',
        turn_id TEXT DEFAULT '',
        fe_score REAL DEFAULT 0.5,
        created_at TEXT DEFAULT (datetime('now'))
    )""")

    # Edges table - relationships between nodes
    db.execute("""
    CREATE TABLE IF NOT EXISTS memory_edges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id INTEGER NOT NULL,
        target_id INTEGER NOT NULL,
        relation TEXT NOT NULL,
        weight REAL DEFAULT 1.0,
        FOREIGN KEY (source_id) REFERENCES memory_nodes(id),
        FOREIGN KEY (target_id) REFERENCES memory_nodes(id)
    )""")

    # Turn groups - links the 3 layers of a single conversational turn
    db.execute("""
    CREATE TABLE IF NOT EXISTS memory_turns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        turn_id TEXT UNIQUE NOT NULL,
        input_node_id INTEGER,
        contemplation_node_id INTEGER,
        output_node_id INTEGER,
        timestamp INTEGER NOT NULL,
        affect_json TEXT DEFAULT '{}',
        FOREIGN KEY (input_node_id) REFERENCES memory_nodes(id),
        FOREIGN KEY (contemplation_node_id) REFERENCES memory_nodes(id),
        FOREIGN KEY (output_node_id) REFERENCES memory_nodes(id)
    )""")

    # FTS5 virtual table for full-text search
    db.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
        text, summary, who, layer,
        content=memory_nodes,
        content_rowid=id
    )""")

    # Triggers to keep FTS5 in sync with memory_nodes
    db.execute("""
    CREATE TRIGGER IF NOT EXISTS memory_nodes_ai AFTER INSERT ON memory_nodes BEGIN
        INSERT INTO memory_fts(rowid, text, summary, who, layer)
        VALUES (new.id, new.text, new.summary, new.who, new.layer);
    END""")

    db.execute("""
    CREATE TRIGGER IF NOT EXISTS memory_nodes_ad AFTER DELETE ON memory_nodes BEGIN
        INSERT INTO memory_fts(memory_fts, rowid, text, summary, who, layer)
        VALUES ('delete', old.id, old.text, old.summary, old.who, old.layer);
    END""")

    db.execute("""
    CREATE TRIGGER IF NOT EXISTS memory_nodes_au AFTER UPDATE ON memory_nodes BEGIN
        INSERT INTO memory_fts(memory_fts, rowid, text, summary, who, layer)
        VALUES ('delete', old.id, old.text, old.summary, old.who, old.layer);
        INSERT INTO memory_fts(rowid, text, summary, who, layer)
        VALUES (new.id, new.text, new.summary, new.who, new.layer);
    END""")

    # Indexes for fast lookup
    db.execute("CREATE INDEX IF NOT EXISTS idx_nodes_timestamp ON memory_nodes(timestamp)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_nodes_layer ON memory_nodes(layer)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_nodes_who ON memory_nodes(who)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_nodes_turn ON memory_nodes(turn_id)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_edges_source ON memory_edges(source_id)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_edges_target ON memory_edges(target_id)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_turns_timestamp ON memory_turns(timestamp)")
    
    # CONCURRENCY FIX: Add unique constraint on (turn_id, layer) to prevent duplicates
    db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_nodes_turn_layer_unique ON memory_nodes(turn_id, layer)")
    
    # Add fe_score column if it doesn't exist (migration)
    try:
        db.execute("ALTER TABLE memory_nodes ADD COLUMN fe_score REAL DEFAULT 0.5")
    except sqlite3.OperationalError:
        pass  # Column already exists

    db.commit()
    print("ok")

except Exception as e:
    print(f"error:{str(e)}", file=sys.stderr)
    sys.exit(1)
`;

  try {
    const result = await execPython("python3", ["-c", initSQL, GRAPH_DB], {
      timeout: 5000,
      encoding: "utf-8",
      breakerId: "db-init"
    });
    
    // AUDIT FIX: Validate response (Issue #4)
    const trimmed = (result || '').trim();
    if (trimmed !== "ok") {
      throw new Error(`Unexpected init response: ${trimmed.substring(0, 100)}`);
    }
    return true;
  } catch (err) {
    // AUDIT FIX: Propagate errors instead of returning false (Issue #1)
    log.error?.(`[nima-memory] DB init failed: ${err.message}`);
    if (err.stderr) {
      log.error?.(`[nima-memory] Python error: ${err.stderr}`);
    }
    throw wrapError(err, 'initDatabase', { dbPath: GRAPH_DB });
  }
}

/**
 * Atomic DB initialization with double-check locking.
 */
async function ensureInitialized() {
  if (initPromise) return initPromise;
  
  initPromise = (async () => {
    try {
      // Retry logic for robustness
      return await retryWithBackoff(
        async () => {
          const result = await _initDatabase();
          if (!result) throw new Error("DB init returned false");
          return result;
        },
        {
          maxRetries: 3,
          baseDelayMs: 1000,
          maxDelayMs: 5000,
          onRetry: (attempt, err, delay) => {
            log.warn?.(`[nima-memory] DB init attempt ${attempt} failed: ${err.message}`);
          }
        }
      );
    } catch (err) {
      log.error?.(`[nima-memory] CRITICAL: DB init failed after retries: ${err.message}`);
      initPromise = null; // Reset so we can try again
      throw err;
    }
  })();
  
  return initPromise;
}

/**
 * Health check: Verify database connectivity and return stats.
 * 
 * Returns:
 *   { ok: true, stats: { nodes, turns, layers, ... } }
 *   { ok: false, error: "..." }
 */
async function healthCheck() {
  if (!existsSync(GRAPH_DB)) {
    return { ok: false, error: "Database file not found", path: GRAPH_DB };
  }

  const healthSQL = `
import sqlite3, sys, json

db_path = sys.argv[1] if len(sys.argv) > 1 else None
if not db_path:
    print(json.dumps({"ok": False, "error": "no_db_path"}))
    sys.exit(1)

try:
  with sqlite3.connect(db_path, timeout=2.0) as db:
    # Check table exists
    tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    table_names = [t[0] for t in tables]
    
    if 'memory_nodes' not in table_names:
        print(json.dumps({"ok": False, "error": "memory_nodes table missing"}))
        sys.exit(1)
    
    # Get stats
    node_count = db.execute("SELECT COUNT(*) FROM memory_nodes").fetchone()[0]
    turn_count = db.execute("SELECT COUNT(*) FROM memory_turns").fetchone()[0]
    
    # Layer distribution
    layers = db.execute("SELECT layer, COUNT(*) FROM memory_nodes GROUP BY layer").fetchall()
    layer_dist = {layer: count for layer, count in layers}
    
    # Recent activity (last 24h)
    now_ts = int(__import__('time').time() * 1000)
    day_ago = now_ts - (24 * 60 * 60 * 1000)
    recent_count = db.execute("SELECT COUNT(*) FROM memory_nodes WHERE timestamp > ?", (day_ago,)).fetchone()[0]
    
    # Database file size
    import os
    db_size = os.path.getsize(db_path)
    
    result = {
        "ok": True,
        "stats": {
            "nodes": node_count,
            "turns": turn_count,
            "layers": layer_dist,
            "recent_24h": recent_count,
            "db_size_bytes": db_size,
            "db_size_mb": round(db_size / (1024 * 1024), 2),
            "tables": table_names
        }
    }
    
    print(json.dumps(result))

except Exception as e:
    print(json.dumps({"ok": False, "error": str(e)}))
    sys.exit(1)
`;

  try {
    const result = await execPython("python3", ["-c", healthSQL, GRAPH_DB], {
      timeout: 3000,
      encoding: "utf-8",
      breakerId: "db-health"
    });
    
    // AUDIT FIX: Safe JSON parsing with validation (Issue #4)
    return safeJsonParse(result, {
      context: "healthCheck Python output",
      validator: (obj) => typeof obj === 'object' && obj !== null && 'ok' in obj,
      defaultValue: { ok: false, error: "Invalid JSON from health check script" }
    });
  } catch (err) {
    // AUDIT FIX: Log full error for debugging (Issue #1)
    log.error?.(`[nima-memory] healthCheck failed: ${err.message}`);
    return {
      ok: false,
      error: err.message,
      stderr: err.stderr?.substring(0, 200),
    };
  }
}

/**
 * Internal storage logic (renamed from storeMemory).
 * Execute this ONLY via queuedWrite().
 *
 * SECURITY FIX: Data passed via JSON temp file, not embedded in Python code.
 * CORRECTNESS FIX: All inserts wrapped in transaction (atomicity).
 */
async function _storeMemoryInternal(record) {
  // UNIQUE ID FIX: Add random suffix to prevent collisions
  const turnId = `turn_${record.timestamp}_${randomBytes(4).toString("hex")}`;

  // Prepare data structure to pass to Python
  const data = {
    db_path: GRAPH_DB,
    turn_id: turnId,
    timestamp: record.timestamp,
    affect_json: JSON.stringify(record.affect || {}),
    session_key: record.metadata.sessionKey,
    conversation_id: record.metadata.conversationId,
    fe_score: record.metadata.feScore || 0.5,
    input: {
      text: record.layers.input?.text ?? "",
      summary: record.layers.input?.summary ?? "",
      who: record.layers.input?.who ?? "unknown",
    },
    contemplation: {
      text: record.layers.contemplation?.text ?? "",
      summary: record.layers.contemplation?.summary ?? "",
    },
    output: {
      text: record.layers.output?.text ?? "",
      summary: record.layers.output?.summary ?? "",
    },
  };

  // Write data to temp file
  const tempFile = join(os.tmpdir(), `nima-memory-${randomBytes(8).toString("hex")}.json`);
  let success = false;

  try {
    writeFileSync(tempFile, JSON.stringify(data), "utf-8");

    // Python script reads from temp file (no injection risk)
    const storeSQL = `
import sqlite3, json, sys

# Read data from temp file
data_file = sys.argv[1] if len(sys.argv) > 1 else None
if not data_file:
    print("error:no_data_file", file=sys.stderr)
    sys.exit(1)

try:
    with open(data_file, 'r') as f:
        data = json.load(f)

    db = sqlite3.connect(data['db_path'], timeout=5.0)
    db.execute("PRAGMA journal_mode=WAL")

    # BEGIN TRANSACTION - all or nothing (atomicity fix)
    db.execute("BEGIN TRANSACTION")

    # Insert input node
    cur = db.execute(
        "INSERT INTO memory_nodes (timestamp, layer, text, summary, who, affect_json, session_key, conversation_id, turn_id, fe_score) VALUES (?, 'input', ?, ?, ?, ?, ?, ?, ?, ?)",
        (data['timestamp'], data['input']['text'], data['input']['summary'], data['input']['who'],
         data['affect_json'], data['session_key'], data['conversation_id'], data['turn_id'], data.get('fe_score', 0.5))
    )
    input_id = cur.lastrowid

    # Insert contemplation node
    cur = db.execute(
        "INSERT INTO memory_nodes (timestamp, layer, text, summary, who, affect_json, session_key, conversation_id, turn_id, fe_score) VALUES (?, 'contemplation', ?, ?, 'self', ?, ?, ?, ?, ?)",
        (data['timestamp'], data['contemplation']['text'], data['contemplation']['summary'],
         data['affect_json'], data['session_key'], data['conversation_id'], data['turn_id'], data.get('fe_score', 0.5))
    )
    contemp_id = cur.lastrowid

    # Insert output node
    cur = db.execute(
        "INSERT INTO memory_nodes (timestamp, layer, text, summary, who, affect_json, session_key, conversation_id, turn_id, fe_score) VALUES (?, 'output', ?, ?, 'self', ?, ?, ?, ?, ?)",
        (data['timestamp'], data['output']['text'], data['output']['summary'],
         data['affect_json'], data['session_key'], data['conversation_id'], data['turn_id'], data.get('fe_score', 0.5))
    )
    output_id = cur.lastrowid

    # Create edges: input → contemplation → output (temporal flow)
    db.execute("INSERT INTO memory_edges (source_id, target_id, relation, weight) VALUES (?, ?, 'triggered', 1.0)", (input_id, contemp_id))
    db.execute("INSERT INTO memory_edges (source_id, target_id, relation, weight) VALUES (?, ?, 'produced', 1.0)", (contemp_id, output_id))
    db.execute("INSERT INTO memory_edges (source_id, target_id, relation, weight) VALUES (?, ?, 'responded_to', 1.0)", (output_id, input_id))

    # Create turn group
    db.execute(
        "INSERT INTO memory_turns (turn_id, input_node_id, contemplation_node_id, output_node_id, timestamp, affect_json) VALUES (?, ?, ?, ?, ?, ?)",
        (data['turn_id'], input_id, contemp_id, output_id, data['timestamp'], data['affect_json'])
    )

    # COMMIT TRANSACTION - make all changes permanent
    db.commit()
    print(f"stored:{input_id},{contemp_id},{output_id}")

except Exception as e:
    print(f"error:{str(e)}", file=sys.stderr)
    sys.exit(1)
finally:
    try:
        db.close()
    except:
        pass
`;

    // AUDIT FIX: Add retry logic for transient failures (Issue #3)
    const result = await retryWithBackoff(
      async () => execPython("python3", ["-c", storeSQL, tempFile], {
        timeout: 10000,
        encoding: "utf-8",
        breakerId: "store-memory"
      }),
      {
        maxRetries: 3,
        baseDelayMs: 500,
        maxDelayMs: 5000,
        onRetry: (attempt, err, delay) => {
          log.warn?.(`[nima-memory] SQLite write attempt ${attempt} failed, retrying in ${delay}ms: ${err.message}`);
        }
      }
    );

    // AUDIT FIX: Validate response format (Issue #4)
    if (!result || typeof result !== 'string') {
      throw new Error('Invalid response from storage script: expected string');
    }
    
    const trimmed = result.trim();
    if (!trimmed.startsWith("stored:")) {
      // Check for error prefix
      if (trimmed.startsWith("error:")) {
        throw new Error(`Storage script error: ${trimmed.substring(6)}`);
      }
      throw new Error(`Unexpected response: ${trimmed.substring(0, 100)}`);
    }
    
    success = true;
    const nodeIds = trimmed.substring(7).split(',');
    log.debug?.(`[nima-memory] Stored nodes: ${nodeIds.join(', ')}`);
    
    // DUAL-WRITE: Also write to LadybugDB if enabled
    if (success && USE_LADYBUG_WRITE && existsSync(LADYBUG_DB)) {
      try {
        const ladybugStorePath = join(dirname(fileURLToPath(import.meta.url)), "ladybug_store.py");
        if (existsSync(ladybugStorePath)) {
          // Fire and forget (don't await) to speed up response?
          // No, we should await to ensure data integrity, but use separate breaker
          await execPython(ladybugStorePath, [tempFile], {
            timeout: 5000,
            encoding: "utf-8",
            breakerId: "store-ladybug"
          });
          log.debug?.(`[nima-memory] ✅ Dual-write to LadybugDB successful`);
        }
      } catch (lbErr) {
        // Non-critical: LadybugDB write failed but SQLite succeeded
        log.warn?.(`[nima-memory] ⚠️ LadybugDB dual-write failed (non-critical): ${lbErr.message}`);
      }
    }
    
    return success;

  } catch (err) {
    // AUDIT FIX: Always log full error context (Issue #1)
    log.error?.(`[nima-memory] ❌ Primary storage failed: ${err.message}`);
    if (err.stderr) {
      log.error?.(`[nima-memory] Python stderr: ${err.stderr}`);
    }
    if (err.stack) {
      log.debug?.(`[nima-memory] Stack trace: ${err.stack}`);
    }
    
    // FALLBACK: Emergency backup to prevent data loss
    try {
      const backupFile = join(EMERGENCY_DIR, `backup_${Date.now()}_${randomBytes(4).toString("hex")}.json`);
      writeFileSync(backupFile, JSON.stringify(data, null, 2), { encoding: "utf-8", mode: 0o600 });
      log.warn?.(`[nima-memory] ⚠️  EMERGENCY BACKUP saved: ${backupFile}`);
      log.warn?.(`[nima-memory] ⚠️  To recover, run: python3 scripts/recover_backups.py`);
      
      // AUDIT FIX: Propagate error instead of returning false (Issue #1)
      // This allows the caller to decide how to handle the failure
      throw wrapError(err, 'storeMemory', { 
        backupFile, 
        turnId,
        recovered: true 
      });
    } catch (backupErr) {
      // Check if this is our wrapped error being re-thrown
      if (backupErr.cause === err) {
        throw backupErr;
      }
      
      log.error?.(`[nima-memory] ❌ CRITICAL: Emergency backup ALSO failed!`);
      log.error?.(`[nima-memory] ❌ Lost memory: ${data.input?.summary || 'unknown'}`);
      log.error?.(`[nima-memory] Backup error: ${backupErr.message}`);
      
      // AUDIT FIX: Propagate error with full context (Issue #1)
      throw wrapError(err, 'storeMemory', { 
        backupFailed: true,
        backupError: backupErr.message,
        turnId,
        lostData: data.input?.summary 
      });
    }
  } finally {
    // Clean up temp file
    try {
      if (existsSync(tempFile)) {
        unlinkSync(tempFile);
      }
    } catch (cleanupErr) {
      console.error(`[nima-memory] Failed to clean up temp file: ${cleanupErr.message}`);
    }
  }
}

/**
 * Queue a write operation to ensure sequential SQLite access (WAL mode limitation).
 * Returns a promise that resolves when the operation completes.
 */
async function queuedWrite(operation) {
  return new Promise((resolve, reject) => {
    writeQueue.push({ operation, resolve, reject });
    if (!isWriting) processQueue();
  });
}

/**
 * Process the write queue sequentially.
 */
async function processQueue() {
  if (isWriting || writeQueue.length === 0) return;
  isWriting = true;
  
  const { operation, resolve, reject } = writeQueue.shift();
  try {
    const result = await operation();
    resolve(result);
  } catch (err) {
    reject(err);
  } finally {
    isWriting = false;
    // Process next item
    if (writeQueue.length > 0) {
      setImmediate ? setImmediate(processQueue) : setTimeout(processQueue, 0);
    }
  }
}

/**
 * Public storage entry point.
 * Queues the write operation to prevent race conditions.
 */
async function storeMemory(record) {
  return queuedWrite(() => _storeMemoryInternal(record));
}

// =============================================================================
// UTILITIES
// =============================================================================

function ensureDir(dir) {
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }
}

/**
 * Escape LIKE pattern wildcards for safe SQL LIKE queries.
 * Escapes: %, _, \
 */
function escapeLikePattern(pattern) {
  if (!pattern) return "";
  return pattern
    .replace(/\\/g, "\\\\")  // Escape backslash first
    .replace(/%/g, "\\%")     // Escape %
    .replace(/_/g, "\\_");    // Escape _
}

// =============================================================================
// PLUGIN EXPORT
// =============================================================================

// Live recall hook is handled by nima-recall-live extension (disabled here to prevent double injection)
// import nimaRecallLivePlugin from "./recall-hook.js";

export default function nimaMemoryPlugin(api, config) {
  // ─── Config with defaults ───
  const identityName = config?.identity_name || "agent";
  const skipSubagents = config?.skip_subagents !== false;
  const skipHeartbeats = config?.skip_heartbeats !== false;

  // Content limits
  const contentLimits = {
    maxTextLength: config?.content_limits?.max_text_length || 3000,
    maxSummaryLength: config?.content_limits?.max_summary_length || 300,
    maxSummaryInput: config?.content_limits?.max_summary_input || 80,
    maxThinkingSummary: config?.content_limits?.max_thinking_summary || 120,
    maxOutputSummary: config?.content_limits?.max_output_summary || 100,
  };

  // Free Energy config
  const feConfig = {
    minThreshold: config?.free_energy?.min_threshold ?? 0.2,
    affectVarianceWeight: config?.free_energy?.affect_variance_weight ?? 0.3,
    thinkingBoost: config?.free_energy?.thinking_boost ?? 0.1,
    routinePenalty: config?.free_energy?.routine_penalty ?? 0.2,
    monotonousPenalty: config?.free_energy?.monotonous_penalty ?? 0.4,
  };

  // Noise filtering config
  const noiseConfig = {
    filterHeartbeatMechanics: config?.noise_filtering?.filter_heartbeat_mechanics !== false,
    filterSystemNoise: config?.noise_filtering?.filter_system_noise !== false,
    filterEmptyExchanges: config?.noise_filtering?.filter_empty_exchanges !== false,
    minExchangeLength: config?.noise_filtering?.min_exchange_length || 5,
  };

  const log = api.log || console;

  // ─── Health Check on Gateway Start ───
  if (config?.database?.health_check_on_startup !== false) {
    // Run health check after a short delay (let gateway fully start)
    setTimeout(async () => {
      const health = await healthCheck();
      if (health.ok) {
        log.info?.(`[nima-memory] ✅ Health check passed`);
        log.info?.(`[nima-memory] Database: ${health.stats.nodes} nodes, ${health.stats.turns} turns, ${health.stats.db_size_mb}MB`);
        if (health.stats.recent_24h > 0) {
          log.info?.(`[nima-memory] Recent activity: ${health.stats.recent_24h} memories in last 24h`);
        }
      } else {
        log.warn?.(`[nima-memory] ⚠️ Health check failed: ${health.error}`);
        if (health.path) {
          log.warn?.(`[nima-memory] Database path: ${health.path}`);
        }
      }
    }, 1000);
  }

  // ─── Auto-Migration to LadybugDB (if enabled) ───
  if (config?.database?.auto_migrate === true && config?.database?.backend === "ladybugdb") {
    setTimeout(async () => {
      const batchSize = config?.database?.migration_batch_size || 500;
      log.info?.(`[nima-memory] Starting auto-migration to LadybugDB (batch size: ${batchSize})...`);
      
      const migrationScript = join(os.homedir(), ".openclaw", "extensions", "nima-memory", "migrate_to_ladybug.py");
      
      try {
        await execPython("python3", [
          migrationScript,
          "--batch-size", String(batchSize),
          "--auto"
        ], {
          timeout: 600000, // 10 minutes max
          encoding: "utf-8",
          breakerId: "migration"
        });
        
        log.info?.(`[nima-memory] ✅ Migration completed`);
        log.info?.(`[nima-memory] Check ${MEMORY_DIR}/migration.log for details`);
      } catch (err) {
        log.error?.(`[nima-memory] ❌ Migration failed: ${err.message}`);
        log.error?.(`[nima-memory] See ${MEMORY_DIR}/migration.log for details`);
        log.warn?.(`[nima-memory] Falling back to SQLite...`);
      }
    }, 2000);
  }

  // ─── Single Hook: agent_end ───
  api.on("agent_end", async (event, ctx) => {
    try {
      // PHASE 4 FIX: Track total processed
      captureMetrics.totalProcessed++;
      
      // CONCURRENCY FIX: Atomic initialization with double-check locking
      try {
        await ensureInitialized();
      } catch (initErr) {
        log.error?.(`[nima-memory] DB init failed, skipping capture: ${initErr.message}`);
        captureMetrics.errors++;
        return;
      }

      // Skip subagents and heartbeats
      if (skipSubagents && ctx.sessionKey?.includes(":subagent:")) return;
      if (skipHeartbeats && ctx.sessionKey?.includes("heartbeat")) {
        captureMetrics.filteredHeartbeat++;
        return;
      }

      // Skip failed runs
      if (!event.success) {
        captureMetrics.errors++;
        return;
      }

      // Extract all three layers from messages
      const layers = extractLayers(event.messages, ctx);
      if (!layers) {
        captureMetrics.filteredEmpty++;
        return;
      }

      // PHASE 1 FIX: Validate contemplation layer - skip if empty but allow if input/output have content
      if (layers.contemplation && (!layers.contemplation.text || layers.contemplation.text.trim() === "")) {
        // Contemplation is empty - check if we still have meaningful input/output
        const hasInput = layers.input?.text?.trim()?.length > 5;
        const hasOutput = layers.output?.text?.trim()?.length > 20;
        if (!hasInput && !hasOutput) {
          log.debug?.(`[nima-memory] Skipping turn with empty contemplation and minimal content`);
          captureMetrics.filteredEmpty++;
          return;
        }
        // If we have good input/output, set contemplation to null rather than empty string
        layers.contemplation = null;
      }

      // Skip if no meaningful content (heartbeat acks, etc.)
      if (!layers.input?.text && !layers.output?.text) {
        captureMetrics.filteredEmpty++;
        return;
      }
      if (layers.output.text === "HEARTBEAT_OK" || layers.output.text === "NO_REPLY") {
        captureMetrics.filteredHeartbeat++;
        return;
      }
      
      // Skip if input was purely heartbeat instruction (already filtered by cleanInputText)
      if (!layers.input.text && !layers.contemplation?.text) {
        captureMetrics.filteredEmpty++;
        return;
      }

      // Skip system noise (gateway restarts, doctor hints, JSON system messages)
      if (isLowQualityMemory(layers.input.text, layers.output.text, layers.contemplation?.text || "")) {
        log.debug?.(`[nima-memory] Skipping system noise memory`);
        captureMetrics.filteredNoise++;
        return;
      }

      // Get current affect state
      const conversationId = ctx.conversationId || ctx.channelId || ctx.chatId || null;
      const affect = readAffectState(conversationId, identityName);
      
      // Calculate FE (Free Energy) score for novelty filtering
      const feScore = calculateFEScoreWithConfig(
        layers.input,
        layers.contemplation,
        layers.output,
        affect,
        feConfig
      );
      
      // Skip monotonous memories (very low FE = repetitive/routine)
      if (feScore < feConfig.minThreshold) {
        log.info?.(`[nima-memory] Skipping low-FE memory (fe=${feScore.toFixed(2)}, threshold=${feConfig.minThreshold})`);
        captureMetrics.filteredFE++;
        return;
      }

      // Create memory record
      const record = createMemoryRecord(
        layers.input,
        layers.contemplation,
        layers.output,
        affect,
        {
          sessionKey: ctx.sessionKey || "",
          conversationId: conversationId || "",
          agentId: ctx.agentId || "",
          durationMs: event.durationMs || 0,
          feScore: feScore,
        }
      );

      // AUDIT FIX: Store to graph with proper error handling (Issue #1)
      // storeMemory now throws on failure instead of returning false
      try {
        await storeMemory(record);
        captureMetrics.stored++;
        const topAffect = affect ? Object.entries(affect).sort((a,b) => b[1]-a[1])[0]?.[0] : 'none';
        log.info?.(`[nima-memory] ✅ Stored turn: ${layers.input?.who || 'user'} → thinking → response (affect: ${topAffect})`);
      } catch (storeErr) {
        // AUDIT FIX: Log but don't crash the hook (Issue #1)
        // Error is already logged and backed up by storeMemory
        captureMetrics.errors++;
        log.error?.(`[nima-memory] ❌ Failed to store memory turn: ${storeErr.message}`);
        
        // If there's a backup file, mention it
        if (storeErr.backupFile) {
          log.info?.(`[nima-memory] 📁 Data preserved in: ${storeErr.backupFile}`);
        }
        
        // Don't re-throw - this is a background task, failing shouldn't crash the agent
        // The error has already been logged and data backed up
      }
    } catch (err) {
      // AUDIT FIX: Log full context on unexpected errors (Issue #1)
      captureMetrics.errors++;
      log.error?.(`[nima-memory] agent_end error: ${err.message}`);
      if (err.stack) {
        log.debug?.(`[nima-memory] Stack: ${err.stack}`);
      }
    }
  });

  // ─── Compaction Hooks ───
  // before_compaction: Flush recent memories before context window compaction
  api.on("before_compaction", (event, ctx) => {
    try {
      log.info?.(`[nima-memory] Pre-compaction flush (${event.messageCount} messages, ${event.tokenCount || '?'} tokens)`);
      // No special action needed - agent_end already captures memories
      // This hook is here to prevent the "Summarization failed" error
    } catch (err) {
      console.error(`[nima-memory] before_compaction error: ${err.message}`);
    }
  });

  // after_compaction: Log compaction stats + trigger embedding indexing
  api.on("after_compaction", async (event, ctx) => {
    try {
      log.info?.(`[nima-memory] Compaction complete (compacted ${event.compactedCount} messages, ${event.messageCount} remain)`);
      
      // Trigger embedding indexing for newly stored memories
      // This makes recent memories immediately searchable without waiting for 3 AM cron
      const embeddingScript = join(MEMORY_DIR, "..", "..", "openclaw_hooks", "nima-memory", "embeddings.py");
      if (existsSync(embeddingScript)) {
        try {
          const result = await execPython("python3", [embeddingScript, "backfill", "--batch-size", "100"], {
            timeout: 30000,
            encoding: "utf-8",
            cwd: dirname(embeddingScript),
            breakerId: "embeddings"
          });
          log.info?.(`[nima-memory] Embedding index updated: ${result.trim()}`);
        } catch (embErr) {
          log.warn?.(`[nima-memory] Embedding indexing failed (non-critical): ${embErr.message}`);
        }
      }
    } catch (err) {
      console.error(`[nima-memory] after_compaction error: ${err.message}`);
    }
  });

  // ─── Gateway Hooks ───
  api.on("gateway_start", () => {
    // Health check already runs via setTimeout above
    log.info?.(`[nima-memory] Plugin loaded - three-layer capture active`);
  });

  // ─── Expose Health Check API ───
  // Other plugins or tools can call this
  if (api.registerMethod) {
    api.registerMethod("nima-memory.healthCheck", async () => {
      return await healthCheck();
    });
  }

  // Live recall handled by nima-recall-live extension (removed duplicate here)
}
