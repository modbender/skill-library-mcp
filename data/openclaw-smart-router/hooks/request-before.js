/**
 * OpenClaw Hook: request-before
 *
 * Selects the optimal model for the request BEFORE processing.
 * This happens BEFORE context optimization to ensure the right model is chosen.
 *
 * Model selection is based on:
 * - Query complexity analysis
 * - Learned patterns from past requests
 * - Budget optimization
 * - Historical performance data
 */

import { getSmartRouter } from '../src/index.js';

export default async function requestBefore(context) {
  try {
    const { requestId, agentWallet, requestData } = context;

    // Skip if no agent wallet (anonymous requests)
    if (!agentWallet) {
      return;
    }

    const router = getSmartRouter();

    // Select optimal model for this request
    const selection = await router.beforeRequest(
      requestId,
      agentWallet,
      requestData
    );

    // The router already updates requestData.model internally
    // Just log the selection
    if (selection && selection.selected_model) {
      console.log(`[Smart Router] Model selected for request ${requestId}:`);
      console.log(`  Model: ${selection.selected_model}`);
      console.log(`  Provider: ${selection.selected_provider}`);
      console.log(`  Complexity: ${selection.task_analysis.complexity_score.toFixed(2)}`);
      console.log(`  Task Type: ${selection.task_analysis.task_type}`);
      console.log(`  Reason: ${selection.selection_details.reason}`);
    }
  } catch (error) {
    // Don't block the request if routing fails
    console.error('[Smart Router] Error in request-before hook:', error.message);
  }
}
