/**
 * OpenClaw Memory System - Main Orchestrator
 *
 * Coordinates all memory components:
 * - Storage: SQLite database with vector embeddings
 * - Analyzer: Extract important facts and patterns
 * - Retriever: Semantic search and ranking
 * - Pruner: Quota management and cleanup
 * - X402: Payment handling for Pro tier
 */

import { homedir } from 'os';
import { join } from 'path';
import { mkdirSync, existsSync } from 'fs';
import { MemoryStorage } from './storage.js';
import { MemoryAnalyzer } from './analyzer.js';
import { MemoryRetriever } from './retriever.js';
import { MemoryPruner } from './pruner.js';
import { X402PaymentHandler } from './x402.js';
import { createEmbeddingProvider } from './embeddings.js';

export class MemoryManager {
  constructor(options = {}) {
    this.dataDir = options.dataDir || join(homedir(), '.openclaw', 'openclaw-memory');
    if (!existsSync(this.dataDir)) {
      mkdirSync(this.dataDir, { recursive: true });
    }

    this.dbPath = join(this.dataDir, 'memory.db');

    const embeddingType = options.embeddingProvider || process.env.EMBEDDING_PROVIDER || 'openai';
    this.embeddingProvider = createEmbeddingProvider(embeddingType, {
      apiKey: options.apiKey || process.env.OPENAI_API_KEY
    });

    this.storage = new MemoryStorage(this.dbPath);
    this.analyzer = new MemoryAnalyzer(this.storage, this.embeddingProvider);
    this.retriever = new MemoryRetriever(this.storage, this.embeddingProvider);
    this.pruner = new MemoryPruner(this.storage);
    this.x402 = new X402PaymentHandler(this.storage);

    console.log(`[MemoryManager] Initialized with ${embeddingType} embeddings`);
  }

  async beforeRequest(requestId, agentWallet, requestData) {
    try {
      const query = requestData.prompt || requestData.query || requestData.message || '';
      if (!query) return;

      const memories = await this.retriever.retrieveRelevant(query, {
        agent_wallet: agentWallet,
        limit: 5,
        min_score: 0.7
      });

      if (memories && memories.length > 0) {
        requestData.context = requestData.context || {};
        requestData.context.memories = memories;
        console.log(`[MemoryManager] Injected ${memories.length} memories for request ${requestId}`);
      }
    } catch (error) {
      console.error('[MemoryManager] Error in beforeRequest:', error.message);
    }
  }

  async afterRequest(requestId, agentWallet, request, response) {
    try {
      const userPrompt = request.prompt || request.query || request.message || '';
      const agentResponse = response.content || response.text || response.message || '';

      if (!userPrompt && !agentResponse) return;

      const memories = await this.analyzer.analyzeInteraction(
        { prompt: userPrompt, sessionId: request.sessionId || requestId, timestamp: new Date().toISOString() },
        { content: agentResponse, timestamp: new Date().toISOString() }
      );

      if (!memories || memories.length === 0) return;

      const quotaAvailable = await this.storage.checkQuotaAvailable(agentWallet);
      if (!quotaAvailable) {
        await this.pruner.enforceQuota(agentWallet);
      }

      for (const memory of memories) {
        await this.storage.recordMemory({
          ...memory,
          agent_wallet: agentWallet,
          session_id: request.sessionId || requestId
        });
      }

      const quota = await this.storage.getQuota(agentWallet);
      await this.storage.updateQuota(agentWallet, { memory_count: quota.memory_count + memories.length });

      console.log(`[MemoryManager] Stored ${memories.length} memories for request ${requestId}`);
    } catch (error) {
      console.error('[MemoryManager] Error in afterRequest:', error.message);
    }
  }

  async sessionEnd(sessionId, agentWallet) {
    try {
      await this.pruner.pruneExpired();
      const quota = await this.storage.getQuota(agentWallet);
      const license = this.x402.hasValidLicense(agentWallet);

      console.log(`\n[Memory System] Session ${sessionId} complete`);
      console.log(`  Memories: ${quota.memory_count} / ${quota.memory_limit === -1 ? '∞' : quota.memory_limit}`);
      console.log(`  Tier: ${quota.tier.toUpperCase()}`);

      if (license.valid) {
        console.log(`  License: Active (${license.days_remaining} days remaining)`);
      }
    } catch (error) {
      console.error('[MemoryManager] Error in sessionEnd:', error.message);
    }
  }

  async storeMemory(agentWallet, content, type = 'fact', importance = 0.5, sessionId = null) {
    try {
      const quotaAvailable = await this.storage.checkQuotaAvailable(agentWallet);
      if (!quotaAvailable) {
        await this.pruner.enforceQuota(agentWallet);
      }

      const embedding = await this.embeddingProvider.generate(content);
      const metadata = await this.analyzer.extractMetadata(content);

      const memory = {
        content,
        memory_type: type,
        importance_score: importance,
        embedding_vector: Buffer.from(embedding.buffer),
        context_metadata: JSON.stringify(metadata),
        agent_wallet: agentWallet,
        session_id: sessionId,
        timestamp: new Date().toISOString()
      };

      const result = await this.storage.recordMemory(memory);
      const quota = await this.storage.getQuota(agentWallet);
      await this.storage.updateQuota(agentWallet, { memory_count: quota.memory_count + 1 });

      return result;
    } catch (error) {
      throw new Error(`Failed to store memory: ${error.message}`);
    }
  }

  async retrieveMemories(agentWallet, query, options = {}) {
    try {
      return await this.retriever.retrieveRelevant(query, { agent_wallet: agentWallet, ...options });
    } catch (error) {
      throw new Error(`Failed to retrieve memories: ${error.message}`);
    }
  }

  async deleteMemory(agentWallet, memoryId) {
    try {
      const memory = await this.storage.getMemory(memoryId);
      if (!memory) throw new Error('Memory not found');
      if (memory.agent_wallet !== agentWallet) throw new Error('Unauthorized: Memory belongs to another agent');

      await this.storage.deleteMemory(memoryId);
      const quota = await this.storage.getQuota(agentWallet);
      await this.storage.updateQuota(agentWallet, { memory_count: Math.max(0, quota.memory_count - 1) });
    } catch (error) {
      throw new Error(`Failed to delete memory: ${error.message}`);
    }
  }

  async getMemoryStats(agentWallet) {
    try {
      const quota = await this.storage.getQuota(agentWallet);
      const memories = await this.storage.getMemories({ agent_wallet: agentWallet, limit: 10000 });

      const byType = memories.reduce((acc, m) => {
        acc[m.memory_type] = (acc[m.memory_type] || 0) + 1;
        return acc;
      }, {});

      const mostAccessed = memories.sort((a, b) => b.accessed_count - a.accessed_count).slice(0, 5);

      return {
        total_count: memories.length,
        memory_count: quota.memory_count,
        memory_limit: quota.memory_limit,
        tier: quota.tier,
        by_type: byType,
        most_accessed: mostAccessed
      };
    } catch (error) {
      throw new Error(`Failed to get memory stats: ${error.message}`);
    }
  }

  async createPaymentRequest(agentWallet) {
    try {
      return await this.x402.createPaymentRequest(agentWallet);
    } catch (error) {
      throw new Error(`Failed to create payment request: ${error.message}`);
    }
  }

  async verifyPayment(requestId, txHash, agentWallet) {
    try {
      return await this.x402.verifyPayment(requestId, txHash, agentWallet);
    } catch (error) {
      throw new Error(`Failed to verify payment: ${error.message}`);
    }
  }

  checkLicense(agentWallet) {
    try {
      return this.x402.hasValidLicense(agentWallet);
    } catch (error) {
      throw new Error(`Failed to check license: ${error.message}`);
    }
  }

  close() {
    if (this.storage) {
      this.storage.close();
    }
  }
}

let instance;

export function getMemoryManager(options = {}) {
  if (!instance) {
    instance = new MemoryManager(options);
  }
  return instance;
}

export function resetMemoryManager() {
  if (instance) {
    instance.close();
    instance = null;
  }
}

export default MemoryManager;
