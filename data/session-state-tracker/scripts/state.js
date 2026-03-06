#!/usr/bin/env node
/**
 * Session State Tracker - Core Module (Refactored v2.0.0)
 *
 * Provides utilities for reading, writing, and discovering session state
 * from SESSION_STATE.md and indexed session transcripts.
 *
 * Improvements:
 * - Atomic file writes (temp + rename)
 * - Schema validation on write
 * - Configurable discover options
 * - Better error handling and logging
 * - Dynamic workspace resolution (no module-scope constant)
 *
 * SECURITY MANIFEST:
 *   Environment variables accessed: OPENCLAW_WORKSPACE (optional)
 *   External endpoints called: none
 *   Local files read: SESSION_STATE.md
 *   Local files written: SESSION_STATE.md (atomic)
 *
 * This module is used by hook scripts, CLI, and tool wrappers.
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

/**
 * Get the workspace directory from environment or cwd.
 * @returns {string}
 */
function getWorkspace() {
  return process.env.OPENCLAW_WORKSPACE || process.cwd();
}

/**
 * Get the absolute path to SESSION_STATE.md.
 * @returns {string}
 */
function getStateFilePath() {
  return path.resolve(getWorkspace(), 'SESSION_STATE.md');
}

// =====================
// Schema & Validation
// =====================

/**
 * State schema definition.
 * All fields are required unless marked optional.
 */
const SCHEMA = {
  project: { type: 'string', required: true },
  task: { type: 'string', required: true },
  status: { type: 'enum', values: ['active', 'blocked', 'done', 'in-progress'], required: true },
  last_action: { type: 'string', required: true },
  next_steps: { type: 'array', required: true },
  updated: { type: 'string', required: true }, // ISO 8601
  body: { type: 'string', required: false } // freeform notes (optional in frontmatter, may be separate body section)
};

/**
 * Validate a state object against schema.
 * Throws Error with detailed message if validation fails.
 * @param {object} state
 */
function validate(state) {
  const errors = [];

  for (const [field, rules] of Object.entries(SCHEMA)) {
    const value = state[field];

    // Required check
    if (rules.required && value === undefined) {
      errors.push(`missing required field: '${field}'`);
      continue;
    }

    if (value === undefined) continue; // skip optional fields that are absent

    // Type checks
    if (rules.type === 'string') {
      if (typeof value !== 'string') {
        errors.push(`field '${field}' must be string, got ${typeof value}`);
      } else if (value.trim() === '') {
        errors.push(`field '${field}' cannot be empty`);
      }
    } else if (rules.type === 'array') {
      if (!Array.isArray(value)) {
        errors.push(`field '${field}' must be array, got ${typeof value}`);
      }
    } else if (rules.type === 'enum') {
      if (!rules.values.includes(value)) {
        errors.push(`field '${field}' must be one of [${rules.values.join(', ')}], got '${value}'`);
      }
    }
  }

  // Additional cross-field validation
  if (state.updated && typeof state.updated === 'string') {
    const isoMatch = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z$/.test(state.updated);
    if (!isoMatch) {
      errors.push(`field 'updated' must be valid ISO 8601 timestamp (e.g., 2026-02-14T23:20:00.000Z)`);
    }
  }

  if (errors.length > 0) {
    throw new Error(`State validation failed: ${errors.join('; ')}`);
  }
}

// =====================
// File I/O
// =====================

/**
 * Parse YAML frontmatter and body from a Markdown file.
 * Uses js-yaml for robust parsing.
 * @param {string} content
 * @returns {{ frontmatter: object, body: string }}
 */
function parseFile(content) {
  // Split on '---' delimiter lines. We need at least: (content) --- fm --- body
  const parts = content.split(/^---$/m);
  if (parts.length < 3) {
    throw new Error('Invalid SESSION_STATE.md: missing YAML frontmatter delimiters (---)');
  }
  const fmStr = parts[1].trim();
  const body = parts.slice(2).join('---').trim(); // Rejoin in case body contains '---'

  try {
    const frontmatter = yaml.load(fmStr);
    if (!frontmatter || typeof frontmatter !== 'object') {
      throw new Error('Invalid YAML frontmatter: must be an object');
    }
    return { frontmatter, body };
  } catch (err) {
    err.message = `Failed to parse YAML frontmatter: ${err.message}`;
    throw err;
  }
}

/**
 * Read SESSION_STATE.md and return full state (frontmatter fields + body).
 * @returns {Promise<object|null>} state object or null if file doesn't exist
 */
async function readState() {
  const STATE_FILE = getStateFilePath();
  try {
    const content = fs.readFileSync(STATE_FILE, 'utf-8');
    const parsed = parseFile(content);
    return { ...parsed.frontmatter, body: parsed.body || '' };
  } catch (err) {
    if (err.code === 'ENOENT') {
      return null;
    }
    throw err;
  }
}

/**
 * Write SESSION_STATE.md with given updates.
 * Writes atomically via temp file + rename.
 * Preserves existing fields not mentioned in updates.
 * Always updates `updated` timestamp to current ISO unless explicitly provided.
 *
 * @param {object} updates - partial state updates
 * @param {object} options - { validate: boolean (default true), dryRun: boolean }
 * @returns {Promise<{success: boolean, updated: string, path: string}>}
 */
async function writeState(updates, options = {}) {
  const { validate: doValidate = true, dryRun = false } = options;
  const STATE_FILE = getStateFilePath();

  const current = await readState() || {};
  const { body: currentBody, ...currentFm } = current;

  // Separate body from updates; remaining updatesFm are frontmatter
  const { body: updateBody, ...updatesFm } = updates;

  // Merge frontmatter
  const merged = { ...currentFm, ...updatesFm };
  // Ensure updated timestamp (override if provided)
  merged.updated = updates.updated || new Date().toISOString();

  // Determine final body
  const finalBody = updateBody !== undefined ? updateBody : currentBody;

  if (doValidate) {
    try {
      validate(merged);
    } catch (err) {
      err.message = `writeState validation error: ${err.message}`;
      throw err;
    }
  }

  // Reconstruct file
  const fmYaml = yaml.dump(merged, {
    lineWidth: -1, // no wrapping
    indent: 2
  });
  const output = `---\n${fmYaml}---\n${finalBody ? finalBody + '\n' : ''}`;

  if (dryRun) {
    console.log('[session-state-tracker] writeState (dryRun): would write:', output.substring(0, 200) + '...');
    return { success: true, updated: merged.updated, path: STATE_FILE };
  }

  // Atomic write: write to temp file then rename
  const tmpPath = STATE_FILE + '.tmp';
  try {
    // Ensure directory exists
    fs.mkdirSync(path.dirname(STATE_FILE), { recursive: true });
    fs.writeFileSync(tmpPath, output, 'utf-8');
    fs.renameSync(tmpPath, STATE_FILE); // atomic on POSIX filesystems
  } catch (err) {
    // Cleanup temp file on failure
    try { fs.unlinkSync(tmpPath); } catch (e) { /* ignore */ }
    throw err;
  }

  return { success: true, updated: merged.updated, path: STATE_FILE };
}

// =====================
// Discovery
// =====================

/**
 * Discover current session state from indexed transcripts.
 * Uses memory_search on sessions to find recent mentions of project/task.
 *
 * @param {object} memorySearch - the memory_search tool function (injected)
 * @param {object} opts - { limit?: number, minScore?: number, query?: string }
 * @returns {Promise<object>} synthesized state object (includes body)
 */
async function discoverFromSessions(memorySearch, opts = {}) {
  const { limit = 10, minScore = 0.3, query = 'project|task|working on|next step|implementing|building' } = opts;

  try {
    const results = await memorySearch({
      query,
      sources: ['sessions'],
      limit,
      minScore
    });

    if (!results || results.length === 0) {
      return {
        project: '',
        task: '',
        status: 'active',
        last_action: '',
        next_steps: [],
        updated: new Date().toISOString(),
        body: 'Auto-discovered from session transcripts (no clear task found)'
      };
    }

    // Naive synthesis: take the top result's snippet as task hint
    const top = results[0];
    const snippet = (top.text || '').replace(/\n/g, ' ').substring(0, 200);
    const projectMatch = snippet.match(/(?:project|working on)\s+([A-Za-z0-9_-]+)/i);
    const taskMatch = snippet.match(/(?:task|implementing|building)\s+([A-Za-z0-9_-]+(?:\s+[A-Za-z0-9_-]+)*)/i);

    const project = projectMatch ? projectMatch[1] : '';
    const task = taskMatch ? taskMatch[1] : snippet.slice(0, 80);

    const body = `Top snippet: ${snippet}\n\nSource: ${top.file}~${top.fromLine}-${top.toLine}`;

    const state = {
      project: project || '',
      task: task || 'Discovered from recent conversation',
      status: 'active',
      last_action: `Discovered from ${results.length} session snippet(s)`,
      next_steps: [],
      updated: new Date().toISOString(),
      body
    };

    // Write automatically
    const writeResult = await writeState(state, { validate: false });
    return state;
  } catch (err) {
    // Discovery failure: return a safe empty state but log
    console.error('[session-state-tracker] discoverFromSessions error:', err.message);
    throw err;
  }
}

module.exports = {
  readState,
  writeState,
  discoverFromSessions,
  parseFile,
  validate,
  SCHEMA,
  getStateFilePath,
  // For backward compatibility, expose STATE_FILE computed at call time
  get STATE_FILE() { return getStateFilePath(); }
};
