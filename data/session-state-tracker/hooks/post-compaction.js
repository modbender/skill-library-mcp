#!/usr/bin/env node
/**
 * Post-compaction Hook
 *
 * Runs after compaction completes. Older messages have been removed from active context.
 * We inject a system message reminding the agent of the current working state to preserve continuity.
 *
 * Context:
 *   - session: session object (we can add system messages)
 *   - agent: agent instance
 *
 * We read SESSION_STATE.md and add a system message like:
 *   [State Anchor] project: X | task: Y | status: Z | next: ...
 *
 * This ensures the agent is re-anchored without needing to remember to read the file.
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
      console.log('[session-state-tracker] post-compaction: no state file found, nothing to inject');
      return { ok: true, skipped: 'no_state_file' };
    }

    // Build a concise reminder. Use fields only; omit body to save tokens.
    const parts = [];

    if (state.project) parts.push(`project: ${state.project}`);
    if (state.task) parts.push(`task: ${state.task}`);
    if (state.status) parts.push(`status: ${state.status}`);
    if (state.next_steps && Array.isArray(state.next_steps) && state.next_steps.length > 0) {
      // Show up to 3 next steps
      const steps = state.next_steps.slice(0, 3).join('; ');
      parts.push(`next: ${steps}`);
    }

    if (parts.length === 0) {
      console.log('[session-state-tracker] post-compaction: state file is empty/default, skipping injection');
      return { ok: true, skipped: 'empty_state' };
    }

    const reminder = `[State Anchor] ${parts.join(' | ')}`;

    // Inject as a system message. The exact API depends on OpenClaw session object.
    // Likely: session.addSystemMessage(reminder) or session.pushSystemMessage(...).
    // We'll use a method that's standard in OpenClaw agents.
    if (typeof session.addSystemMessage === 'function') {
      session.addSystemMessage(reminder);
    } else if (typeof session.push === 'function') {
      session.push({ role: 'system', content: reminder });
    } else {
      // Fallback: log only; we can't inject
      console.warn('[session-state-tracker] post-compaction: session object has no addSystemMessage/push; cannot inject reminder');
      return { ok: false, error: 'session_api_mismatch' };
    }

    console.log('[session-state-tracker] post-compaction: state reminder injected');
    return { ok: true, action: 'injected', reminder };
  } catch (err) {
    console.error('[session-state-tracker] post-compaction error:', err.message);
    return { ok: false, error: err.message };
  }
};
