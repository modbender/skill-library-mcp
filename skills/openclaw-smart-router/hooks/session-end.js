/**
 * OpenClaw Hook: session-end
 *
 * Reports routing statistics and cost savings when a session ends.
 * Shows:
 * - Total routing decisions
 * - Total cost vs baseline (Opus)
 * - Savings achieved
 * - Quota status
 * - Average quality maintained
 * - License status
 */

import { getSmartRouter } from '../src/index.js';

export default async function sessionEnd(context) {
  try {
    const { sessionId, agentWallet } = context;

    // Skip if no agent wallet (anonymous sessions)
    if (!agentWallet) {
      return;
    }

    const router = getSmartRouter();

    // Generate and display session report
    // The sessionEnd method in the router handles all the logging
    await router.sessionEnd(sessionId, agentWallet);

  } catch (error) {
    console.error('[Smart Router] Error in session-end hook:', error.message);
  }
}
