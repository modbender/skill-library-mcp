/**
 * OpenClaw Hook: request-before
 *
 * Compresses context before request processing to reduce token usage.
 * Uses intelligent pattern recognition and summarization to maintain quality.
 */

import { getContextOptimizer } from '../src/index.js';

export default async function requestBefore(context) {
  try {
    const { requestId, agentWallet, requestData } = context;

    // Skip if no agent wallet (anonymous requests)
    if (!agentWallet) {
      return;
    }

    const optimizer = getContextOptimizer();

    // Extract context to compress
    const contextToCompress = requestData.context || requestData.prompt || requestData.query || '';

    if (!contextToCompress || typeof contextToCompress !== 'string') {
      return;
    }

    // Compress context using intelligent optimization
    const compressionResult = await optimizer.compressor.compress(contextToCompress, {
      agent_wallet: agentWallet,
      request_id: requestId,
      target_reduction: 0.5, // Target 50% reduction
      preserve_quality: true
    });

    // Replace context with compressed version
    if (compressionResult && compressionResult.compressed) {
      // Update the request data with compressed context
      if (typeof requestData.context === 'string') {
        requestData.context = compressionResult.compressed;
      } else if (typeof requestData.context === 'object') {
        requestData.context.text = compressionResult.compressed;
        requestData.context.original_length = compressionResult.original_length;
        requestData.context.compressed_length = compressionResult.compressed_length;
        requestData.context.compression_ratio = compressionResult.compression_ratio;
      } else if (requestData.prompt) {
        requestData.prompt = compressionResult.compressed;
      }

      // Store compression metrics
      requestData._compression_metrics = {
        original_length: compressionResult.original_length,
        compressed_length: compressionResult.compressed_length,
        tokens_saved: compressionResult.tokens_saved,
        compression_ratio: compressionResult.compression_ratio
      };

      console.log(`[Context Optimizer] Compressed context for request ${requestId}`);
      console.log(`  Original: ${compressionResult.original_length} tokens`);
      console.log(`  Compressed: ${compressionResult.compressed_length} tokens`);
      console.log(`  Saved: ${compressionResult.tokens_saved} tokens (${(compressionResult.compression_ratio * 100).toFixed(1)}%)`);
    }
  } catch (error) {
    // Don't block the request if compression fails
    console.error('[Context Optimizer] Error in request-before hook:', error.message);
  }
}
