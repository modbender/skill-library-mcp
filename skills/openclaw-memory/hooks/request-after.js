/**
 * OpenClaw Hook: request-after
 *
 * Extracts and stores memories from the completed request/response interaction.
 * Analyzes conversation for facts, preferences, patterns, and important information.
 */

import { getMemoryManager } from '../src/index.js';

export default async function requestAfter(context) {
  try {
    const { requestId, agentWallet, request, response } = context;

    // Skip if no agent wallet (anonymous requests)
    if (!agentWallet) {
      return;
    }

    const manager = getMemoryManager();

    // Extract prompt and response text
    const userPrompt = request.prompt || request.query || request.message || '';
    const agentResponse = response.content || response.text || response.message || '';

    if (!userPrompt && !agentResponse) {
      return;
    }

    // Analyze the interaction to extract memories
    const memories = await manager.analyzer.analyzeInteraction(
      {
        prompt: userPrompt,
        sessionId: request.sessionId || requestId,
        timestamp: new Date().toISOString()
      },
      {
        content: agentResponse,
        timestamp: new Date().toISOString()
      }
    );

    if (!memories || memories.length === 0) {
      return;
    }

    // Check quota before storing
    const quota = await manager.storage.getQuota(agentWallet);
    const quotaAvailable = await manager.storage.checkQuotaAvailable(agentWallet);

    if (quotaAvailable) {
      // Store memories directly
      for (const memory of memories) {
        await manager.storage.recordMemory({
          ...memory,
          agent_wallet: agentWallet,
          session_id: request.sessionId || requestId
        });
      }

      // Update quota count
      await manager.storage.updateQuota(agentWallet, {
        memory_count: quota.memory_count + memories.length
      });

      console.log(`[Memory System] Stored ${memories.length} new memories for request ${requestId}`);
    } else {
      // Quota exceeded - enforce pruning first
      console.log(`[Memory System] Quota limit reached, pruning old memories...`);
      await manager.pruner.enforceQuota(agentWallet);

      // Try storing again after pruning
      for (const memory of memories) {
        await manager.storage.recordMemory({
          ...memory,
          agent_wallet: agentWallet,
          session_id: request.sessionId || requestId
        });
      }

      console.log(`[Memory System] Stored ${memories.length} new memories after pruning`);
    }
  } catch (error) {
    // Don't fail the request if memory storage fails
    console.error('[Memory System] Error in request-after hook:', error.message);
  }
}
