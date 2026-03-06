/**
 * MemoryPruner - Quota enforcement and memory management for OpenClaw Memory System
 *
 * Features:
 * - Enforce quotas (free = 100, pro = unlimited)
 * - Prune by composite score (importance + access + age)
 * - Clean expired memories
 * - Deduplicate similar memories
 * - Return detailed pruning statistics
 */

export class MemoryPruner {
  constructor(storage, embeddingProvider = null) {
    this.storage = storage;
    this.embeddingProvider = embeddingProvider; // Optional, for deduplication
  }

  /**
   * Check and enforce memory quotas
   * @param {string} agentWallet - Agent wallet address
   * @returns {Promise<Object>} Pruning results
   */
  async enforceQuota(agentWallet) {
    const quota = await this.storage.getQuota(agentWallet);
    const currentCount = quota.memory_count;

    // Pro tier with unlimited quota
    if (quota.tier === 'pro' && quota.memory_limit === -1) {
      return {
        pruned: 0,
        reason: 'unlimited',
        tier: 'pro',
        message: 'Pro tier has unlimited memory storage'
      };
    }

    // Check if over quota
    if (currentCount > quota.memory_limit) {
      const toPrune = currentCount - quota.memory_limit;
      return await this.pruneMemories(agentWallet, toPrune);
    }

    return {
      pruned: 0,
      reason: 'within_quota',
      current_count: currentCount,
      limit: quota.memory_limit,
      message: `Memory usage: ${currentCount}/${quota.memory_limit}`
    };
  }

  /**
   * Prune low-value memories
   * Strategy: Remove memories with lowest composite score (importance + access + age)
   * @param {string} agentWallet - Agent wallet address
   * @param {number} count - Number of memories to prune
   * @returns {Promise<Object>} Pruning results with stats
   */
  async pruneMemories(agentWallet, count) {
    // Get all memories for this agent
    const allMemories = await this.storage.getMemories({
      agent_wallet: agentWallet
    });

    if (allMemories.length === 0) {
      return {
        pruned: 0,
        reason: 'no_memories',
        message: 'No memories to prune'
      };
    }

    // Calculate pruning scores for all memories
    const scored = this.calculatePruningScores(allMemories);

    // Sort by score (lowest first = highest priority for pruning)
    scored.sort((a, b) => a.score - b.score);

    // Select candidates to prune
    const candidates = scored.slice(0, Math.min(count, scored.length));

    // Delete selected memories
    const pruned = [];
    const stats = {
      by_type: {},
      avg_importance: 0,
      avg_age_days: 0,
      avg_access_count: 0
    };

    let totalImportance = 0;
    let totalAgeDays = 0;
    let totalAccesses = 0;
    const now = Date.now();

    for (const candidate of candidates) {
      const memory = candidate.memory;

      // Delete memory
      await this.storage.deleteMemory(memory.memory_id);

      pruned.push({
        memory_id: memory.memory_id,
        content_preview: memory.content.substring(0, 50),
        type: memory.memory_type,
        importance: memory.importance_score,
        accessed_count: memory.accessed_count,
        age_days: candidate.ageDays,
        pruning_score: candidate.score
      });

      // Update stats
      stats.by_type[memory.memory_type] = (stats.by_type[memory.memory_type] || 0) + 1;
      totalImportance += memory.importance_score || 0;
      totalAgeDays += candidate.ageDays;
      totalAccesses += memory.accessed_count || 0;
    }

    // Calculate averages
    if (pruned.length > 0) {
      stats.avg_importance = totalImportance / pruned.length;
      stats.avg_age_days = totalAgeDays / pruned.length;
      stats.avg_access_count = totalAccesses / pruned.length;
    }

    // Update quota count
    const newCount = allMemories.length - pruned.length;
    await this.storage.updateQuota(agentWallet, newCount);

    return {
      pruned: pruned.length,
      reason: 'quota_exceeded',
      memory_ids: pruned.map(m => m.memory_id),
      details: pruned,
      statistics: stats,
      new_count: newCount,
      message: `Pruned ${pruned.length} low-value memories to enforce quota`
    };
  }

  /**
   * Calculate pruning scores for memories
   * Lower score = higher priority for pruning
   * Score = importance * 0.4 + access_value * 0.3 + recency * 0.3
   * @param {Array} memories - Memories to score
   * @returns {Array} Memories with pruning scores
   */
  calculatePruningScores(memories) {
    const now = Date.now();
    const MAX_AGE_MS = 90 * 24 * 60 * 60 * 1000; // 90 days
    const MAX_ACCESSES = 100;

    return memories.map(memory => {
      // Importance (already normalized 0.0 to 1.0)
      const importance = memory.importance_score || 0.5;

      // Access value (normalize by max accesses)
      const accessCount = memory.accessed_count || 0;
      const accessValue = Math.min(accessCount, MAX_ACCESSES) / MAX_ACCESSES;

      // Recency (newer = higher score, older = lower score = higher pruning priority)
      const memoryTimestamp = new Date(memory.timestamp).getTime();
      const age = now - memoryTimestamp;
      const ageDays = age / (24 * 60 * 60 * 1000);
      const recency = Math.max(0, 1 - (age / MAX_AGE_MS));

      // Composite score (weighted)
      const score =
        importance * 0.4 +
        accessValue * 0.3 +
        recency * 0.3;

      return {
        memory,
        score,
        importance,
        accessValue,
        recency,
        ageDays
      };
    });
  }

  /**
   * Clean expired memories
   * @returns {Promise<Object>} Pruning results
   */
  async pruneExpired() {
    const expired = await this.storage.getExpiredMemories();

    if (expired.length === 0) {
      return {
        pruned: 0,
        reason: 'no_expired',
        message: 'No expired memories found'
      };
    }

    const pruned = [];
    const stats = {
      by_type: {},
      by_agent: {}
    };

    for (const memory of expired) {
      // Delete memory
      await this.storage.deleteMemory(memory.memory_id);

      pruned.push({
        memory_id: memory.memory_id,
        agent_wallet: memory.agent_wallet,
        type: memory.memory_type,
        expired_at: memory.expires_at
      });

      // Update stats
      stats.by_type[memory.memory_type] = (stats.by_type[memory.memory_type] || 0) + 1;
      stats.by_agent[memory.agent_wallet] = (stats.by_agent[memory.agent_wallet] || 0) + 1;
    }

    // Update quota counts for affected agents
    for (const [agentWallet, count] of Object.entries(stats.by_agent)) {
      const quota = await this.storage.getQuota(agentWallet);
      await this.storage.updateQuota(agentWallet, quota.memory_count - count);
    }

    return {
      pruned: pruned.length,
      reason: 'expired',
      memory_ids: pruned.map(m => m.memory_id),
      details: pruned,
      statistics: stats,
      message: `Pruned ${pruned.length} expired memories`
    };
  }

  /**
   * Deduplicate similar memories using embedding similarity
   * @param {string} agentWallet - Agent wallet address
   * @param {number} similarityThreshold - Minimum similarity to consider duplicates (default: 0.95)
   * @returns {Promise<Object>} Deduplication results
   */
  async deduplicateMemories(agentWallet, similarityThreshold = 0.95) {
    if (!this.embeddingProvider) {
      return {
        pruned: 0,
        reason: 'no_embedding_provider',
        message: 'Embedding provider required for deduplication'
      };
    }

    // Get all memories for agent
    const memories = await this.storage.getMemories({
      agent_wallet: agentWallet
    });

    if (memories.length < 2) {
      return {
        pruned: 0,
        reason: 'insufficient_memories',
        message: 'Need at least 2 memories to deduplicate'
      };
    }

    // Find duplicate pairs
    const duplicates = [];
    const processed = new Set();

    for (let i = 0; i < memories.length; i++) {
      if (processed.has(memories[i].memory_id)) continue;

      const memoryA = memories[i];
      if (!memoryA.embedding_vector) continue;

      for (let j = i + 1; j < memories.length; j++) {
        if (processed.has(memories[j].memory_id)) continue;

        const memoryB = memories[j];
        if (!memoryB.embedding_vector) continue;

        // Calculate cosine similarity
        const similarity = this.cosineSimilarity(
          this.deserializeEmbedding(memoryA.embedding_vector),
          this.deserializeEmbedding(memoryB.embedding_vector)
        );

        if (similarity >= similarityThreshold) {
          // Keep the one with higher importance or more accesses
          const keepA =
            (memoryA.importance_score || 0) >= (memoryB.importance_score || 0) &&
            (memoryA.accessed_count || 0) >= (memoryB.accessed_count || 0);

          duplicates.push({
            keep: keepA ? memoryA : memoryB,
            remove: keepA ? memoryB : memoryA,
            similarity
          });

          processed.add(keepA ? memoryB.memory_id : memoryA.memory_id);
        }
      }
    }

    if (duplicates.length === 0) {
      return {
        pruned: 0,
        reason: 'no_duplicates',
        message: `No duplicates found (similarity >= ${similarityThreshold})`
      };
    }

    // Delete duplicates
    const pruned = [];
    const stats = {
      by_type: {},
      avg_similarity: 0
    };

    let totalSimilarity = 0;

    for (const dup of duplicates) {
      await this.storage.deleteMemory(dup.remove.memory_id);

      pruned.push({
        removed_id: dup.remove.memory_id,
        kept_id: dup.keep.memory_id,
        similarity: dup.similarity,
        removed_content: dup.remove.content.substring(0, 50),
        kept_content: dup.keep.content.substring(0, 50)
      });

      stats.by_type[dup.remove.memory_type] = (stats.by_type[dup.remove.memory_type] || 0) + 1;
      totalSimilarity += dup.similarity;
    }

    stats.avg_similarity = totalSimilarity / duplicates.length;

    // Update quota count
    const quota = await this.storage.getQuota(agentWallet);
    await this.storage.updateQuota(agentWallet, quota.memory_count - pruned.length);

    return {
      pruned: pruned.length,
      reason: 'duplicates',
      memory_ids: pruned.map(m => m.removed_id),
      details: pruned,
      statistics: stats,
      message: `Removed ${pruned.length} duplicate memories (similarity >= ${similarityThreshold})`
    };
  }

  /**
   * Prune memories older than specified days for free tier
   * @param {string} agentWallet - Agent wallet address
   * @param {number} maxAgeDays - Maximum age in days (default: 7 for free tier)
   * @returns {Promise<Object>} Pruning results
   */
  async pruneOldMemories(agentWallet, maxAgeDays = 7) {
    const quota = await this.storage.getQuota(agentWallet);

    // Only enforce on free tier
    if (quota.tier !== 'free') {
      return {
        pruned: 0,
        reason: 'pro_tier',
        message: 'Age-based pruning only applies to free tier'
      };
    }

    // Calculate cutoff date
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - maxAgeDays);

    // Get old memories
    const allMemories = await this.storage.getMemories({
      agent_wallet: agentWallet
    });

    const oldMemories = allMemories.filter(memory => {
      const memoryDate = new Date(memory.timestamp);
      return memoryDate < cutoffDate;
    });

    if (oldMemories.length === 0) {
      return {
        pruned: 0,
        reason: 'no_old_memories',
        message: `No memories older than ${maxAgeDays} days found`
      };
    }

    // Delete old memories
    const pruned = [];
    const stats = {
      by_type: {},
      avg_age_days: 0
    };

    let totalAgeDays = 0;
    const now = Date.now();

    for (const memory of oldMemories) {
      await this.storage.deleteMemory(memory.memory_id);

      const memoryTimestamp = new Date(memory.timestamp).getTime();
      const ageDays = (now - memoryTimestamp) / (24 * 60 * 60 * 1000);

      pruned.push({
        memory_id: memory.memory_id,
        type: memory.memory_type,
        age_days: Math.round(ageDays)
      });

      stats.by_type[memory.memory_type] = (stats.by_type[memory.memory_type] || 0) + 1;
      totalAgeDays += ageDays;
    }

    stats.avg_age_days = totalAgeDays / pruned.length;

    // Update quota count
    await this.storage.updateQuota(agentWallet, quota.memory_count - pruned.length);

    return {
      pruned: pruned.length,
      reason: 'age_limit',
      memory_ids: pruned.map(m => m.memory_id),
      statistics: stats,
      max_age_days: maxAgeDays,
      message: `Pruned ${pruned.length} memories older than ${maxAgeDays} days (free tier limit)`
    };
  }

  /**
   * Calculate cosine similarity between two vectors
   * @param {Float32Array} a - First vector
   * @param {Float32Array} b - Second vector
   * @returns {number} Cosine similarity (0.0 to 1.0)
   */
  cosineSimilarity(a, b) {
    if (a.length !== b.length) {
      throw new Error('Vectors must have same length');
    }

    let dotProduct = 0;
    let magnitudeA = 0;
    let magnitudeB = 0;

    for (let i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
      magnitudeA += a[i] * a[i];
      magnitudeB += b[i] * b[i];
    }

    magnitudeA = Math.sqrt(magnitudeA);
    magnitudeB = Math.sqrt(magnitudeB);

    if (magnitudeA === 0 || magnitudeB === 0) {
      return 0;
    }

    return dotProduct / (magnitudeA * magnitudeB);
  }

  /**
   * Deserialize embedding vector from BLOB
   * @param {Buffer} blob - Serialized embedding
   * @returns {Float32Array} Deserialized embedding
   */
  deserializeEmbedding(blob) {
    if (Buffer.isBuffer(blob)) {
      return new Float32Array(blob.buffer, blob.byteOffset, blob.length / 4);
    }
    return new Float32Array(blob);
  }

  /**
   * Run comprehensive cleanup (expired + quota enforcement + old memories)
   * @param {string} agentWallet - Agent wallet address (optional, cleans all if not specified)
   * @returns {Promise<Object>} Combined cleanup results
   */
  async runCleanup(agentWallet = null) {
    const results = {
      total_pruned: 0,
      operations: []
    };

    // Clean expired memories (all agents)
    const expiredResult = await this.pruneExpired();
    results.operations.push({
      type: 'expired',
      ...expiredResult
    });
    results.total_pruned += expiredResult.pruned;

    if (agentWallet) {
      // Enforce quota for specific agent
      const quotaResult = await this.enforceQuota(agentWallet);
      results.operations.push({
        type: 'quota',
        ...quotaResult
      });
      results.total_pruned += quotaResult.pruned;

      // Prune old memories (free tier only)
      const oldResult = await this.pruneOldMemories(agentWallet, 7);
      results.operations.push({
        type: 'age_limit',
        ...oldResult
      });
      results.total_pruned += oldResult.pruned;
    }

    results.message = `Cleanup complete: pruned ${results.total_pruned} total memories`;

    return results;
  }
}
