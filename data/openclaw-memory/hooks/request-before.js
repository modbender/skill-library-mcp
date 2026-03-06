/**
 * OpenClaw Hook: request-before
 *
 * Injects relevant memories into the request context before processing.
 * This allows the agent to recall past conversations, facts, and preferences.
 */

import { getMemoryManager } from '../src/index.js';

export default async function requestBefore(context) {
  try {
    const { requestId, agentWallet, requestData } = context;

    // Skip if no agent wallet (anonymous requests)
    if (!agentWallet) {
      return;
    }

    const manager = getMemoryManager();

    // Extract the query/prompt from request
    const query = requestData.prompt || requestData.query || requestData.message || '';

    if (!query || typeof query !== 'string') {
      return;
    }

    // Retrieve relevant memories using semantic search
    const memories = await manager.retriever.retrieveRelevant(query, {
      agent_wallet: agentWallet,
      limit: 5, // Top 5 most relevant memories
      min_score: 0.7 // Minimum similarity threshold
    });

    // Inject memories into request context
    if (memories && memories.length > 0) {
      // Format memories for injection
      const memoryContext = memories.map(m => ({
        type: m.memory_type,
        content: m.content,
        importance: m.importance_score,
        timestamp: m.timestamp
      }));

      // Add to request data
      requestData.context = requestData.context || {};
      requestData.context.memories = memoryContext;

      // Also format as text for prompt injection
      const memoryText = memories
        .map(m => `[${m.memory_type}] ${m.content}`)
        .join('\n');

      requestData.context.memory_text = memoryText;

      console.log(`[Memory System] Injected ${memories.length} memories for request ${requestId}`);
    }
  } catch (error) {
    // Don't block the request if memory retrieval fails
    console.error('[Memory System] Error in request-before hook:', error.message);
  }
}
