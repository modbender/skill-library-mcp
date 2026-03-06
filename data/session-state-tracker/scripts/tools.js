const { readState, writeState, discoverFromSessions, validate } = require('./state');

/**
 * OpenClaw tool implementations for session-state-tracker.
 *
 * These functions are called by OpenClaw when the agent uses the tools.
 * Each receives (ctx, args) where ctx provides access to other tools.
 *
 * SECURITY MANIFEST:
 *   Environment variables accessed: OPENCLAW_WORKSPACE (via state module)
 *   External endpoints called: none (except memory_search when using discover)
 *   Local files read: SESSION_STATE.md
 *   Local files written: SESSION_STATE.md
 */

module.exports = {
  /**
   * Read the current SESSION_STATE.md
   * @param {object} ctx - tool context (contains tools, agent, etc.)
   * @param {object} args - arguments (none)
   * @returns {Promise<object>} state object including frontmatter fields and optional body
   */
  async session_state_read(ctx, args) {
    const state = await readState();
    if (!state) {
      throw new Error('SESSION_STATE.md does not exist or is empty. Use session_state_write to create it.');
    }
    return state;
  },

  /**
   * Update one or more fields in SESSION_STATE.md.
   * Automatically updates `updated` timestamp unless provided.
   * Validates against schema before writing.
   *
   * @param {object} ctx - tool context
   * @param {object} args - partial state updates, e.g., { "task": "New task", "status": "active" }
   * @returns {Promise<object>} { success: true, fields: [...], updated: "ISO timestamp", path: "..." }
   */
  async session_state_write(ctx, args) {
    if (!args || typeof args !== 'object' || Object.keys(args).length === 0) {
      throw new Error('session_state_write requires at least one field to update');
    }

    // Ensure we don't accidentally pass a body that's not a string (the tool interface can do weird things)
    if (args.body !== undefined && typeof args.body !== 'string') {
      throw new Error('field "body" must be a string if provided');
    }

    const result = await writeState(args, { validate: true, dryRun: false });
    return {
      success: true,
      fields: Object.keys(args),
      updated: result.updated,
      path: result.path
    };
  },

  /**
   * Discover current state from session transcripts using memory_search.
   * Useful when SESSION_STATE.md is missing or you want to recover recent context.
   * Automatically writes discovered state to the file.
   *
   * @param {object} ctx - tool context (provides memory_search)
   * @param {object} args - optional overrides: { limit?, minScore?, query? }
   * @returns {Promise<object>} synthesized state object with _meta
   */
  async session_state_discover(ctx, args) {
    const memorySearch = ctx.tools?.memory_search;
    if (!memorySearch) {
      throw new Error('memory_search tool not available. Ensure session transcript indexing is enabled (agents.defaults.memorySearch.experimental.sessionMemory = true)');
    }

    const limit = args?.limit ?? 10;
    const minScore = args?.minScore ?? 0.3;
    const query = args?.query ?? 'project|task|working on|next step|implementing|building';

    try {
      const state = await discoverFromSessions(memorySearch, { limit, minScore, query });
      // Write automatically
      const writeResult = await writeState(state, { validate: false }); // discovery produces valid state
      return {
        ...state,
        _meta: {
          action: 'discovered',
          limit,
          minScore,
          query,
          written: writeResult.success,
          updated: writeResult.updated
        }
      };
    } catch (err) {
      throw new Error(`session_state_discover failed: ${err.message}`);
    }
  }
};
