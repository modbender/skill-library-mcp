/**
 * OpenClaw Hook: request-after
 *
 * Learns from request results to improve compression quality.
 * Analyzes whether compression maintained response quality.
 */

import { getContextOptimizer } from '../src/index.js';

export default async function requestAfter(context) {
  try {
    const { requestId, agentWallet, request, response } = context;

    // Skip if no agent wallet (anonymous requests)
    if (!agentWallet) {
      return;
    }

    const optimizer = getContextOptimizer();

    // Check if this request had compression applied
    const compressionMetrics = request._compression_metrics;
    if (!compressionMetrics) {
      return; // No compression was applied
    }

    // Extract response quality indicators
    const responseText = response.content || response.text || response.message || '';
    const wasSuccessful = response.status !== 'error' && responseText.length > 0;

    // Analyze compression quality based on response
    const qualityAnalysis = {
      request_id: requestId,
      agent_wallet: agentWallet,
      original_length: compressionMetrics.original_length,
      compressed_length: compressionMetrics.compressed_length,
      compression_ratio: compressionMetrics.compression_ratio,
      tokens_saved: compressionMetrics.tokens_saved,
      response_successful: wasSuccessful,
      response_length: responseText.length,
      timestamp: new Date().toISOString()
    };

    // Store feedback for learning
    await optimizer.learner.recordFeedback(qualityAnalysis);

    // Update compression statistics
    await optimizer.stats.recordCompression({
      agent_wallet: agentWallet,
      tokens_saved: compressionMetrics.tokens_saved,
      compression_ratio: compressionMetrics.compression_ratio,
      quality_maintained: wasSuccessful
    });

    // Learn patterns from the interaction
    if (wasSuccessful) {
      const originalContext = request.original_context || '';
      const compressedContext = request.context || request.prompt || '';

      if (originalContext && compressedContext) {
        await optimizer.learner.analyzePatterns({
          original: originalContext,
          compressed: compressedContext,
          agent_wallet: agentWallet,
          effectiveness: compressionMetrics.compression_ratio
        });
      }
    }

    console.log(`[Context Optimizer] Recorded compression feedback for request ${requestId}`);
    console.log(`  Quality maintained: ${wasSuccessful ? 'Yes' : 'No'}`);
    console.log(`  Tokens saved: ${compressionMetrics.tokens_saved}`);
  } catch (error) {
    // Don't fail the request if learning fails
    console.error('[Context Optimizer] Error in request-after hook:', error.message);
  }
}
