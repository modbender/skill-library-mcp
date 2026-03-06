#!/usr/bin/env node
/**
 * Session-start Hook
 *
 * Runs when a new session begins (after gateway restart or new conversation).
 * Reads SESSION_STATE.md and injects a summary into the initial context
 * so the agent immediately knows what it was working on.
 *
 * Context:
 *   - session: the new session object
 *
 * If state file is missing or stale (>24h), we skip injection.
 *
 * SECURITY MANIFEST:
 *   Environment variables accessed: none
 *   External endpoints called: none
 *   Local files read: SESSION_STATE.md
 *   Local files written: none (only injects system message)
 */

const { readState } = require('../scripts/state');

module.exports = async function (ctx) {
  const { session } = ctx;

  try {
    const state = await readState();

    if (!state) {
      console.log('[session-state-tracker] session-start: no state file found');
      return { ok: true, skipped: 'no_state_file' };
    }

    // Check freshness: skip if >24 hours old
    if (state.updated) {
      const updated = new Date(state.updated);
      const ageHours = (Date.now() - updated.getTime()) / (1000 * 60 * 60);
      if (ageHours > 24) {
        console.log(`[session-state-tracker] session-start: state is stale (${ageHours.toFixed(1)}h old), skipping injection`);
        return { ok: true, skipped: 'stale_state', ageHours };
      }
    }

    // Build a concise summary
    const parts = [];
    if (state.project) parts.push(`Project: ${state.project}`);
    if (state.task) parts.push(`Task: ${state.task}`);
    if (state.status) parts.push(`Status: ${state.status}`);
    if (state.next_steps && Array.isArray(state.next_steps) && state.next_steps.length > 0) {
      const steps = state.next_steps.slice(0, 3).join('; ');
      parts.push(`Next: ${steps}`);
    }

    if (parts.length === 0) {
      console.log('[session-state-tracker] session-start: state is empty, skipping injection');
      return { ok: true, skipped: 'empty_state' };
    }

    const summary = `[Resume] ${parts.join(' | ')}`;

    // Inject as early system message
    if (typeof session.addSystemMessage === 'function') {
      session.addSystemMessage(summary);
    } else if (typeof session.push === 'function') {
      session.push({ role: 'system', content: summary });
    } else {
      console.warn('[session-state-tracker] session-start: session object has no addSystemMessage/push; cannot inject');
      return { ok: false, error: 'session_api_mismatch' };
    }

    console.log('[session-state-tracker] session-start: state injected');
    return { ok: true, action: 'injected', summary };
  } catch (err) {
    console.error('[session-state-tracker] session-start error:', err.message);
    return { ok: false, error: err.message };
  }
};
