#!/usr/bin/env node
/**
 * Pre-compaction Hook
 *
 * Runs just before compaction begins. Captures current working state
 * and persists it to SESSION_STATE.md without requiring agent involvement.
 *
 * Expected context (passed by OpenClaw plugin runner):
 *   - session: current session object
 *   - agent: agent instance with tools access
 *   - config: plugin configuration
 *
 * If memory_search is available, we use it to synthesize state from recent messages.
 * If not, we skip silently — the state file will retain its previous value.
 *
 * This hook should be fast (<10s) to avoid delaying compaction.
 *
 * SECURITY MANIFEST:
 *   Environment variables accessed: none
 *   External endpoints called: none
 *   Local files read: SESSION_STATE.md (via writeState/readState)
 *   Local files written: SESSION_STATE.md (atomic write)
 */

const { discoverFromSessions, writeState } = require('../scripts/state');

module.exports = async function (ctx) {
  const { agent } = ctx;

  // Access to other tools via agent.tools (if provided by OpenClaw)
  const memorySearch = agent.tools?.memory_search;

  if (!memorySearch) {
    console.log('[session-state-tracker] pre-compaction: memory_search tool not available, skipping auto-save');
    return { ok: true, skipped: 'no_memory_search' };
  }

  try {
    // Quick discovery from last few messages (limit to keep it fast)
    const state = await discoverFromSessions(memorySearch, {
      limit: 8,
      minScore: 0.35
    });

    // Only write if we have a meaningful task
    if (state.task && state.task.trim().length > 0 && state.project && state.project.trim().length > 0) {
      await writeState(state, { validate: false }); // discovery state is valid
      console.log('[session-state-tracker] pre-compaction: state saved');
      return { ok: true, action: 'saved', task: state.task };
    } else {
      console.log('[session-state-tracker] pre-compaction: no clear task/project found, skipping write');
      return { ok: true, skipped: 'no_clear_task' };
    }
  } catch (err) {
    // Log but do not fail compaction
    console.error('[session-state-tracker] pre-compaction error:', err.message);
    return { ok: false, error: err.message };
  }
};
