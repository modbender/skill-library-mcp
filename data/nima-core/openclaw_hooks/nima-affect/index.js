/**
 * NIMA Dynamic Affect System Plugin
 * ==================================
 * Real-time emotion detection and Panksepp 7-affect state management.
 * 
 * Detection Stack (all <1ms combined):
 *   Tier 1: Emotion Lexicon (~500 words → Panksepp affects)
 *   Tier 2: Emoji affect map (30+ emoji → direct affect weights)
 *   Tier 3: Contextual signals (caps, exclamations, message structure)
 * 
 * Hooks:
 *   message_received  → detect emotions, update affect state (fire-and-forget)
 *   before_agent_start → inject current affect into prompt context (blocking)
 *   agent_end          → log conversation affect drift
 * 
 * Configuration:
 *   Set custom baseline in openclaw.plugin.json config section.
 * 
 * Author: NIMA Core Team
 * Date: Feb 13, 2026
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync, renameSync } from "node:fs";
import { join } from "node:path";
import os from "node:os";
import { LEXICON, EMOJI_AFFECTS } from "./emotion-lexicon.js";
import { analyzeAffect } from "./vader-affect.js";
// --- Inlined: shared/resilient.js (self-contained, no cross-dir imports) ---
function _logHookError(name, err) { console.error(`[HookError] Hook '${name}' failed: ${err.message}`); }
function resilientHook(name, fn, fallback = undefined) {
  return async function(event, ctx) { try { return await fn(event, ctx); } catch (err) { _logHookError(name, err); return fallback; } };
}
function resilientHookSync(name, fn, fallback = undefined) {
  return function(event, ctx) { try { return fn(event, ctx); } catch (err) { _logHookError(name, err); return fallback; } };
}
// --- End inlined ---

// =============================================================================
// CONSTANTS
// =============================================================================

const AFFECTS = ["SEEKING", "RAGE", "FEAR", "LUST", "CARE", "PANIC", "PLAY"];

const ARCHETYPES = {
  "guardian": { baseline: [0.6, 0.05, 0.2, 0.05, 0.8, 0.15, 0.3], description: "Protective, alert, caring" },
  "explorer": { baseline: [0.8, 0.05, 0.1, 0.1, 0.4, 0.05, 0.5], description: "Curious, adventurous" },
  "trickster": { baseline: [0.7, 0.1, 0.05, 0.1, 0.3, 0.05, 0.8], description: "Playful, mischievous" },
  "stoic": { baseline: [0.4, 0.05, 0.05, 0.05, 0.3, 0.05, 0.2], description: "Calm, measured" },
  "empath": { baseline: [0.5, 0.05, 0.15, 0.1, 0.9, 0.2, 0.4], description: "Deep feeling, high care" },
  "warrior": { baseline: [0.7, 0.3, 0.1, 0.05, 0.4, 0.05, 0.3], description: "Action-oriented, higher rage tolerance" },
  "sage": { baseline: [0.7, 0.05, 0.05, 0.05, 0.5, 0.05, 0.3], description: "Wisdom-seeking, balanced" },
  "nurturer": { baseline: [0.4, 0.02, 0.1, 0.1, 0.9, 0.15, 0.5], description: "Maximum care, gentle" },
  "rebel": { baseline: [0.8, 0.2, 0.05, 0.15, 0.2, 0.05, 0.6], description: "Independent, defiant" },
  "sentinel": { baseline: [0.5, 0.1, 0.3, 0.05, 0.5, 0.25, 0.1], description: "Vigilant, watchful, anxious" }
};

// Default balanced baseline (agents should configure their own)
const DEFAULT_BASELINE = [0.5, 0.1, 0.1, 0.1, 0.5, 0.1, 0.4];

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

// Dynamics — tuned for responsive emotional shifts
const MOMENTUM = 0.3;
const BLEND_STRENGTH = 0.8;
const BASELINE_PULL = 0.005;
const DECAY_RATE = 0.1; // per hour

// =============================================================================
// CONTEXTUAL SIGNAL DETECTOR (Tier 3 — zero cost metadata)
// =============================================================================

function detectContextualSignals(text) {
  const signals = {
    intensityMultiplier: 1.0,
    affects: {},
  };
  
  if (!text) return signals;
  
  // Exclamation density → amplifies intensity
  const exclamations = (text.match(/!/g) || []).length;
  if (exclamations >= 3) signals.intensityMultiplier = 1.4;
  else if (exclamations >= 1) signals.intensityMultiplier = 1.15;
  
  // ALL CAPS words → amplifies intensity + slight RAGE/PLAY
  const capsWords = (text.match(/\b[A-Z]{2,}\b/g) || []).filter(w => 
    !["OK", "I", "AI", "API", "JS", "CSS", "HTML", "HTTP", "URL", "CLI", "SQL", "SSH",
      "NIMA", "VSA", "ONNX", "NRC", "TF", "ML", "LLM", "GPU", "CPU", "RAM", "SSD",
      "SEEKING", "RAGE", "FEAR", "LUST", "CARE", "PANIC", "PLAY", "AM", "PM", "EST",
      "UTC", "ID", "PR", "CI", "CD"].includes(w)
  );
  if (capsWords.length >= 2) {
    signals.intensityMultiplier *= 1.3;
    signals.affects.PLAY = (signals.affects.PLAY || 0) + 0.15;
  }
  
  // Question marks → SEEKING
  const questions = (text.match(/\?/g) || []).length;
  if (questions >= 1) {
    signals.affects.SEEKING = (signals.affects.SEEKING || 0) + 0.1 * Math.min(questions, 3);
  }
  
  // Message length signals
  if (text.length > 500) {
    signals.affects.SEEKING = (signals.affects.SEEKING || 0) + 0.1;
  }
  
  // Ellipsis → uncertainty, slight FEAR or PANIC
  if (text.includes("...") || text.includes("…")) {
    signals.affects.FEAR = (signals.affects.FEAR || 0) + 0.05;
    signals.affects.PANIC = (signals.affects.PANIC || 0) + 0.05;
  }
  
  // Multiple emoji → amplifies detected emotion
  const emojiCount = (text.match(/[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu) || []).length;
  if (emojiCount >= 3) signals.intensityMultiplier *= 1.2;
  
  return signals;
}

// =============================================================================
// LEXICON-BASED EMOTION DETECTOR (Tier 1+2 — <1ms)
// =============================================================================

// Pre-compute lowercase lexicon keys for fast lookup
const LEXICON_LOWER = {};
for (const [word, affects] of Object.entries(LEXICON)) {
  LEXICON_LOWER[word.toLowerCase()] = affects;
}

function detectEmotions(text) {
  if (!text || typeof text !== "string") return { emotions: [], affects: {}, signals: null };
  
  const affects = {};
  const matchedWords = [];
  
  // Tier 1: Lexicon word lookup
  const words = text.toLowerCase().replace(/['']/g, "'").split(/[\s,.:;!?()\[\]{}"]+/).filter(Boolean);
  
  for (const word of words) {
    // Strip common suffixes for basic stemming
    const stems = [word];
    if (word.endsWith("ing") && word.length > 5) stems.push(word.slice(0, -3));
    if (word.endsWith("ed") && word.length > 4) stems.push(word.slice(0, -2));
    if (word.endsWith("ly") && word.length > 4) stems.push(word.slice(0, -2));
    if (word.endsWith("ness") && word.length > 6) stems.push(word.slice(0, -4));
    if (word.endsWith("ful") && word.length > 5) stems.push(word.slice(0, -3));
    if (word.endsWith("less") && word.length > 6) stems.push(word.slice(0, -4));
    if (word.endsWith("ment") && word.length > 6) stems.push(word.slice(0, -4));
    if (word.endsWith("s") && word.length > 3 && !word.endsWith("ss")) stems.push(word.slice(0, -1));
    
    for (const stem of stems) {
      const mapping = LEXICON_LOWER[stem];
      if (mapping) {
        matchedWords.push({ word, stem, mapping });
        for (const [affect, weight] of Object.entries(mapping)) {
          affects[affect] = (affects[affect] || 0) + weight;
        }
        break;
      }
    }
  }
  
  // Tier 2: Emoji detection
  for (const [emoji, mapping] of Object.entries(EMOJI_AFFECTS)) {
    const count = (text.split(emoji).length - 1);
    if (count > 0) {
      matchedWords.push({ word: emoji, stem: emoji, mapping });
      for (const [affect, weight] of Object.entries(mapping)) {
        affects[affect] = (affects[affect] || 0) + weight * Math.min(count, 3);
      }
    }
  }
  
  // Tier 3: Contextual signals
  const signals = detectContextualSignals(text);
  
  // Merge contextual affects
  for (const [affect, weight] of Object.entries(signals.affects)) {
    affects[affect] = (affects[affect] || 0) + weight;
  }
  
  // Normalize: if we matched multiple words, scale sub-linearly
  const matchCount = matchedWords.length || 1;
  if (matchCount > 1) {
    for (const affect of AFFECTS) {
      if (affects[affect]) {
        affects[affect] = Math.min(1.0, affects[affect] / Math.sqrt(matchCount));
      }
    }
  }
  
  // Apply intensity multiplier from contextual signals
  for (const affect of AFFECTS) {
    if (affects[affect]) {
      affects[affect] = Math.min(1.0, affects[affect] * signals.intensityMultiplier);
    }
  }
  
  return { 
    emotions: matchedWords.map(m => ({ word: m.word, mapping: m.mapping })),
    affects, 
    signals,
    matchCount,
  };
}

// =============================================================================
// AFFECT STATE MANAGER
// =============================================================================

function getStatePath(identityName, conversationId = null) {
  // Support NIMA_HOME env var, fallback to ~/.nima/affect
  const nimaHome = process.env.NIMA_HOME || join(os.homedir(), ".nima");
  const affectDir = join(nimaHome, "affect");
  
  // Security: Sanitize both identityName and conversationId to prevent path traversal
  const safeIdentity = sanitizePathComponent(identityName, 64);
  
  // Conversation isolation: separate state file per conversation
  if (conversationId) {
    // Create conversations subdirectory
    const convDir = join(affectDir, "conversations");
    if (!existsSync(convDir)) {
      mkdirSync(convDir, { recursive: true });
    }
    // Use sanitized conversation ID in filename
    const safeId = sanitizePathComponent(conversationId, 64);
    return join(convDir, `${safeIdentity}_${safeId}.json`);
  }
  
  return join(affectDir, `affect_state_${safeIdentity}.json`);
}

function loadState(statePath, baseline) {
  try {
    if (existsSync(statePath)) {
      const state = JSON.parse(readFileSync(statePath, "utf-8"));
      
      // Ensure version exists (migration)
      if (!state.version) state.version = 1;
      
      // Apply temporal decay since last save
      if (state.current && state.current.timestamp) {
        const hoursElapsed = (Date.now() / 1000 - state.current.timestamp) / 3600;
        if (hoursElapsed > 0) {
          const decayFactor = Math.exp(-DECAY_RATE * hoursElapsed);
          const baselineVals = state.baseline?.values || baseline;
          state.current.values = state.current.values.map((v, i) => 
            baselineVals[i] + decayFactor * (v - baselineVals[i])
          );
          state.current.values = state.current.values.map(v => Math.max(0, Math.min(1, v)));
          state.current.timestamp = Date.now() / 1000;
          state.current.source = "loaded_with_decay";
        }
      }
      
      return state;
    }
  } catch (e) { /* corrupted, start fresh */ }
  
  return {
    version: 1,
    current: { values: [...baseline], timestamp: Date.now() / 1000, source: "baseline" },
    baseline: { values: [...baseline], timestamp: Date.now() / 1000, source: "baseline" },
    saved_at: new Date().toISOString(),
  };
}

function saveState(statePath, state) {
  try {
    const dir = statePath.substring(0, statePath.lastIndexOf("/"));
    if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
    // Atomic write: write to .tmp file, then rename
    const tmpPath = statePath + '.tmp';
    writeFileSync(tmpPath, JSON.stringify(state, null, 2));
    renameSync(tmpPath, statePath);
  } catch (e) {
    console.error("[nima-affect] Failed to save state:", e.message);
  }
}

function applyDecay(current, baselineVals, timestampSec) {
  const hoursElapsed = (Date.now() / 1000 - timestampSec) / 3600;
  if (hoursElapsed <= 0) return current;
  const decayFactor = Math.exp(-DECAY_RATE * hoursElapsed);
  return current.map((val, i) => 
    Math.max(0, Math.min(1, baselineVals[i] + decayFactor * (val - baselineVals[i])))
  );
}

function blendAffect(currentVals, inputAffects, intensity, baseline) {
  const inputVec = AFFECTS.map(name => inputAffects[name] || 0);
  
  // Apply intensity scaling
  const scaledInput = inputVec.map(v => v * intensity);
  
  // Calculate effective blend with momentum
  // Momentum makes current state "sticky" - high momentum = slower changes
  const effectiveBlend = BLEND_STRENGTH * intensity;
  
  return currentVals.map((val, i) => {
    const shift = effectiveBlend * (scaledInput[i] - val);
    let newVal = val + (1 - MOMENTUM) * shift;
    // Baseline pull (separate from input blending)
    newVal += BASELINE_PULL * (baseline[i] - newVal);
    return Math.max(0, Math.min(1, newVal));
  });
}

/**
 * Sleep helper for retry backoff.
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise<void>}
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Calculate exponential backoff delay with jitter.
 * Jitter helps prevent thundering herd when multiple processes retry simultaneously.
 * @param {number} attempt - Retry attempt number (0-indexed)
 * @param {number} baseDelay - Base delay in milliseconds
 * @returns {number} Delay with jitter applied
 */
function calculateBackoff(attempt, baseDelay = 10) {
  // Exponential backoff: baseDelay * 2^attempt
  const exponentialDelay = baseDelay * Math.pow(2, attempt);
  // Add +/- 25% jitter to distribute retries
  const jitter = 0.25;
  const randomFactor = 1 + (Math.random() * 2 - 1) * jitter; // 0.75 to 1.25
  return Math.floor(exponentialDelay * randomFactor);
}

/**
 * Synchronous busy-wait for very short delays in sync context.
 * Only used for sub-millisecond waits; for longer delays we skip the retry.
 * @param {number} ms - Milliseconds to wait (max 5ms recommended)
 */
function busyWait(ms) {
  const start = Date.now();
  while (Date.now() - start < ms) {
    // Spin
  }
}

/**
 * Core affect state update logic with optimistic locking.
 * Shared between sync and async variants.
 * @returns {Object} - { success: boolean, current: Object, shouldRetry: boolean }
 */
function updateAffectStateCore(statePath, detectedAffects, intensity, baseline, attempt) {
  const state = loadState(statePath, baseline);
  const initialVersion = state.version;

  let values = applyDecay(state.current.values, baseline, state.current.timestamp);

  if (Object.keys(detectedAffects).length > 0) {
    values = blendAffect(values, detectedAffects, intensity, baseline);
  }

  state.current = {
    values,
    timestamp: Date.now() / 1000,
    source: "plugin_lexicon",
    named: Object.fromEntries(AFFECTS.map((name, i) => [name, values[i]])),
  };
  state.saved_at = new Date().toISOString();

  // OPTIMISTIC LOCK CHECK
  // Verify version hasn't changed on disk before writing
  try {
    if (existsSync(statePath)) {
      const onDisk = JSON.parse(readFileSync(statePath, "utf-8"));
      if ((onDisk.version || 1) !== initialVersion) {
        // Conflict: Version mismatch (someone else wrote)
        return { success: false, shouldRetry: true, conflict: true };
      }
    }
  } catch (e) {
    // Read failed (locked/deleted), treat as conflict
    return { success: false, shouldRetry: true, conflict: false, error: e };
  }

  state.version = initialVersion + 1;
  saveState(statePath, state);
  return { success: true, current: state.current };
}

/**
 * Update affect state with exponential backoff retry (synchronous version).
 * Uses busy-wait for very short delays only; skips retry for longer delays.
 * This is safe for message_received hook which must be sync.
 */
function updateAffectState(identityName, detectedAffects, intensity, baseline, conversationId = null) {
  const statePath = getStatePath(identityName, conversationId);
  const MAX_RETRIES = 5;
  const BASE_DELAY_MS = 5; // Start very small for sync context
  const MAX_SYNC_DELAY_MS = 10; // Only busy-wait up to 10ms per retry

  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    const result = updateAffectStateCore(statePath, detectedAffects, intensity, baseline, attempt);

    if (result.success) {
      return result.current;
    }

    if (!result.shouldRetry || attempt >= MAX_RETRIES - 1) {
      break;
    }

    // Calculate backoff delay
    const delay = calculateBackoff(attempt, BASE_DELAY_MS);

    if (delay <= MAX_SYNC_DELAY_MS) {
      // Short enough for busy-wait
      busyWait(delay);
      const reason = result.conflict ? "contention" : "read error";
      console.error(`[nima-affect] ${reason} retry ${attempt + 1}/${MAX_RETRIES} after ${delay}ms wait`);
    } else {
      // Too long for sync context, skip retry but log it
      const reason = result.conflict ? "contention" : "read error";
      console.error(`[nima-affect] ${reason} detected (would wait ${delay}ms, skipping retry ${attempt + 1}/${MAX_RETRIES} in sync context)`);
      break;
    }
  }

  console.error("[nima-affect] Failed to update state after retries (contention)");
  return loadState(statePath, baseline).current;
}

/**
 * Update affect state with exponential backoff retry (async version).
 * Uses proper async sleep for backoff delays.
 * This is safe for before_agent_start hook which is async.
 */
async function updateAffectStateAsync(identityName, detectedAffects, intensity, baseline, conversationId = null) {
  const statePath = getStatePath(identityName, conversationId);
  const MAX_RETRIES = 5;
  const BASE_DELAY_MS = 10; // Can afford longer delays in async context

  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    const result = updateAffectStateCore(statePath, detectedAffects, intensity, baseline, attempt);

    if (result.success) {
      return result.current;
    }

    if (!result.shouldRetry || attempt >= MAX_RETRIES - 1) {
      break;
    }

    // Calculate backoff with jitter and sleep
    const delay = calculateBackoff(attempt, BASE_DELAY_MS);
    const reason = result.conflict ? "contention" : "read error";
    console.error(`[nima-affect] ${reason} retry ${attempt + 1}/${MAX_RETRIES} after ${delay}ms wait`);
    await sleep(delay);
  }

  console.error("[nima-affect] Failed to update state after retries (contention)");
  return loadState(statePath, baseline).current;
}

function getCurrentAffect(identityName, baseline, conversationId = null) {
  const statePath = getStatePath(identityName, conversationId);
  const state = loadState(statePath, baseline);
  
  const values = applyDecay(state.current.values, baseline, state.current.timestamp);
  const named = Object.fromEntries(AFFECTS.map((name, i) => [name, values[i]]));
  const dominant = AFFECTS.reduce((best, name, i) => 
    values[i] > best.val ? { name, val: values[i] } : best, 
    { name: "CARE", val: 0 }
  );
  const deviation = Math.sqrt(values.reduce((sum, v, i) => sum + (v - baseline[i]) ** 2, 0));
  
  return { values, named, dominant, deviation };
}

function formatAffectContext(affect) {
  const { named, dominant, deviation } = affect;
  
  const sorted = Object.entries(named).sort((a, b) => b[1] - a[1]).slice(0, 3);
  const topStr = sorted.map(([name, val]) => `${name}(${val.toFixed(2)})`).join(" ");
  
  const moodWords = [];
  if (named.CARE > 0.6) moodWords.push("nurturing");
  if (named.SEEKING > 0.55) moodWords.push("curious");
  if (named.PLAY > 0.45) moodWords.push("playful");
  if (named.RAGE > 0.3) moodWords.push("fired up");
  if (named.FEAR > 0.3) moodWords.push("cautious");
  if (named.PANIC > 0.3) moodWords.push("distressed");
  if (named.LUST > 0.3) moodWords.push("passionate");
  
  const mood = moodWords.length > 0 ? moodWords.join(", ") : "balanced";
  
  return [
    `🎭 AFFECT STATE [${dominant.name} ${dominant.val.toFixed(2)}]`,
    `Top: ${topStr}`,
    `Mood: ${mood} | Deviation: ${deviation.toFixed(3)}`,
    `[Dynamic affect system active — emotions shift organically based on conversation]`,
  ].join("\n");
}

function getBaselineFromConfig(configValue, log) {
  // 1. Array (legacy raw baseline)
  if (Array.isArray(configValue)) {
    if (configValue.length === 7 && configValue.every(v => typeof v === 'number' && v >= 0 && v <= 1)) {
      return configValue;
    }
    log.warn('[nima-affect] Invalid array baseline (must be 7 floats 0-1). Using default.');
    return [...DEFAULT_BASELINE];
  }

  // 2. String (Archetype name)
  if (typeof configValue === 'string') {
    const key = configValue.toLowerCase();
    if (ARCHETYPES[key]) {
      return [...ARCHETYPES[key].baseline];
    }
    log.warn(`[nima-affect] Unknown archetype '${configValue}'. Using default.`);
    return [...DEFAULT_BASELINE];
  }

  // 3. Object (Archetype + modifiers)
  if (typeof configValue === 'object' && configValue !== null) {
    if (configValue.archetype) {
      const key = configValue.archetype.toLowerCase();
      if (ARCHETYPES[key]) {
        let baseline = [...ARCHETYPES[key].baseline];
        
        // Apply modifiers
        if (configValue.modifiers) {
          for (const [affect, delta] of Object.entries(configValue.modifiers)) {
            const idx = AFFECTS.indexOf(affect.toUpperCase());
            if (idx !== -1) {
              baseline[idx] = Math.max(0, Math.min(1, baseline[idx] + delta));
            }
          }
        }
        return baseline;
      }
      log.warn(`[nima-affect] Unknown archetype '${configValue.archetype}'. Using default.`);
    }
  }

  // Fallback
  return [...DEFAULT_BASELINE];
}

// =============================================================================
// PLUGIN REGISTRATION
// =============================================================================

export default function register(api) {
  const log = api.logger;
  
  // Get configuration (env vars override config for OpenClaw validation bug workaround)
  const pluginConfig = api.config?.plugins?.["nima-affect"] || {};
  const identityName = process.env.NIMA_IDENTITY_NAME || pluginConfig.identity_name || "agent";
  const customBaseline = process.env.NIMA_BASELINE || pluginConfig.baseline || null;
  const skipSubagents = pluginConfig.skipSubagents !== false; // default true
  
  // Validate custom baseline (IMPORTANT FIX 14)
  let baseline = DEFAULT_BASELINE;
  if (customBaseline) {
    baseline = getBaselineFromConfig(customBaseline, log);
  }
  
  const lexiconSize = Object.keys(LEXICON).length;
  const emojiSize = Object.keys(EMOJI_AFFECTS).length;
  log.info(`[nima-affect] registering — identity: ${identityName}, lexicon: ${lexiconSize} words, ${emojiSize} emoji`);
  
  // ─── Hook 1: message_received (fire-and-forget) ───
  api.on("message_received", resilientHookSync("message_received", (event, ctx) => {
    const { content } = event;
    if (!content || content.length < 2) return;

    // Skip system compaction messages
    if (content.startsWith("Pre-compaction")) return;

    // Extract conversation ID for isolation (if available)
    const conversationId = ctx.conversationId || ctx.channelId || ctx.chatId || null;

    const t0 = performance.now();
    const { emotions, affects, signals, matchCount } = detectEmotions(content);
    const detectMs = (performance.now() - t0).toFixed(2);

    if (matchCount === 0) return;

    const intensity = Math.min(1.0,
      Object.values(affects).reduce((sum, v) => sum + v, 0) / Math.max(1, Object.keys(affects).length)
    );

    const updated = updateAffectState(identityName, affects, intensity, baseline, conversationId);

    const dominant = AFFECTS.reduce((best, name, i) =>
      updated.values[i] > best.val ? { name, val: updated.values[i] } : best,
      { name: "CARE", val: 0 }
    );

    const topAffects = Object.entries(affects)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([k, v]) => `${k}:${v.toFixed(2)}`)
      .join(" ");

    log.info(`[nima-affect] ${detectMs}ms | ${matchCount} words | [${topAffects}] → ${dominant.name}(${dominant.val.toFixed(2)}) | intensity=${signals?.intensityMultiplier?.toFixed(2) || "1.00"}x`);
  }, undefined));
  
  // ─── Hook 2: before_agent_start (blocking, VADER detection + inject context) ───
  api.on("before_agent_start", resilientHook("before_agent_start", async (event, ctx) => {
    if (skipSubagents && ctx.sessionKey?.includes(":subagent:")) return;

    // Extract conversation ID for isolation (if available)
    const conversationId = ctx.conversationId || ctx.channelId || ctx.chatId || null;

    // Extract user message from event.prompt
    // Format: "[Tue 2026-02-17 08:18 EST] message text\n[message_id: xxx]"
    let detectTarget = "";
    const prompt = event.prompt || "";
    if (prompt) {
      detectTarget = prompt
        // Remove [message_id: ...] suffix
        .replace(/\[message_id:[^\]]*\]/g, "")
        // Remove timestamp prefix [Day YYYY-MM-DD HH:MM TZ]
        .replace(/^\[[\w\s:+-]+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}[^\]]*\]\s*/gm, "")
        // Remove [Telegram ...] prefix
        .replace(/^\[Telegram[^\]]*\]\s*/gm, "")
        .trim();
    }

    // VADER analysis — deterministic, no API calls
    const result = analyzeAffect(detectTarget);

    if (result.matchCount > 0) {
      // Use async variant for proper backoff in async context
      await updateAffectStateAsync(identityName, result.affects, result.intensity, baseline, conversationId);
    }

    const affect = getCurrentAffect(identityName, baseline, conversationId);
    const context = formatAffectContext(affect);

    return { prependContext: context };
  }, undefined), { priority: 10 });
  
  // ─── Hook 3: agent_end (fire-and-forget) ───
  api.on("agent_end", (event, ctx) => {
    try {
      if (skipSubagents && ctx.sessionKey?.includes(":subagent:")) return;
      const conversationId = ctx.conversationId || ctx.channelId || ctx.chatId || null;
      const affect = getCurrentAffect(identityName, baseline, conversationId);
      log.info(`[nima-affect] session end: ${affect.dominant.name}(${affect.dominant.val.toFixed(2)}) dev=${affect.deviation.toFixed(3)}`);
    } catch (err) { /* silent */ }
  });
  
  // ─── Hook 4: before_response_send (injects affect style hints) ───
  api.on("before_response_send", (event, ctx) => {
    try {
      if (skipSubagents && ctx.sessionKey?.includes(":subagent:")) return;
      
      const conversationId = ctx.conversationId || ctx.channelId || ctx.chatId || null;
      const affect = getCurrentAffect(identityName, baseline, conversationId);
      const { named, dominant } = affect;
      
      // Build affect hint based on dominant affect
      let hint = "";
      
      if (dominant.name === "CARE" && named.CARE > 0.6) {
        hint = "💚 [express warmth and nurturing]";
      } else if (dominant.name === "PLAY" && named.PLAY > 0.6) {
        hint = "😊 [light-hearted, humor welcome]";
      } else if (dominant.name === "SEEKING" && named.SEEKING > 0.6) {
        hint = "🔍 [curious, exploratory tone]";
      } else if (dominant.name === "RAGE" && named.RAGE > 0.4) {
        hint = "⚡ [direct, firm, boundary-setting]";
      } else if (dominant.name === "FEAR" && named.FEAR > 0.4) {
        hint = "⚠️ [cautious, thorough, careful]";
      } else if (dominant.name === "PANIC" && named.PANIC > 0.4) {
        hint = "💜 [gentle, reassuring, grounding]";
      }
      
      // Inject hint as metadata (agent can use this for tone guidance)
      if (hint && event.response) {
        event.response.metadata = event.response.metadata || {};
        event.response.metadata.affect_hint = hint;
        event.response.metadata.affect_state = {
          dominant: dominant.name,
          value: Math.round(dominant.val * 100) / 100,
          deviation: Math.round(affect.deviation * 100) / 100,
          top3: Object.entries(named)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 3)
            .map(([name, val]) => ({ name, val: Math.round(val * 100) / 100 }))
        };
      }
      
    } catch (err) {
      log.debug?.(`[nima-affect] before_response_send error: ${err.message}`);
    }
  }, { priority: 5 });
  
  log.info("[nima-affect] registered ✅ (lexicon + emoji + contextual signals + response hints)");
}
