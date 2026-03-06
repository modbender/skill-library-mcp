/**
 * OpenClaw Hook: provider-after
 *
 * Called AFTER the provider API returns a response.
 * This hook learns from the outcome to improve future model selections.
 *
 * Using provider-after (not request-after) ensures we have access to:
 * - Actual token usage from the provider
 * - Real cost data
 * - Response quality metrics
 * - Error information
 *
 * This data is critical for:
 * - Learning which models work best for which tasks
 * - Tracking actual costs vs estimates
 * - Building confidence in learned patterns
 * - Calculating real savings vs baseline (Opus)
 */

import { getSmartRouter } from '../src/index.js';

export default async function providerAfter(context) {
  try {
    const { requestId, agentWallet, request, response } = context;

    if (!requestId || !response || !agentWallet) {
      return;
    }

    const router = getSmartRouter();

    // Learn from the outcome
    await router.afterRequest(requestId, agentWallet, request, response);

    // Log learning summary
    if (response.usage) {
      const inputTokens = response.usage.prompt_tokens || response.usage.input_tokens || 0;
      const outputTokens = response.usage.completion_tokens || response.usage.output_tokens || 0;

      console.log(`[Smart Router] Learned from request ${requestId}:`);
      console.log(`  Input tokens: ${inputTokens}`);
      console.log(`  Output tokens: ${outputTokens}`);
      console.log(`  Status: ${response.status || 'success'}`);
    }
  } catch (error) {
    // Don't fail the request if learning fails
    console.error('[Smart Router] Error in provider-after hook:', error.message);
  }
}
