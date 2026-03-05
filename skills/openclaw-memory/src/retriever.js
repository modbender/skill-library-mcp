/**
 * MemoryRetriever - Semantic search and retrieval for OpenClaw Memory System
 *
 * Features:
 * - Semantic search with embeddings
 * - Ranking by importance + recency + access count
 * - License tier enforcement (free = 7 days, pro = unlimited)
 * - Access logging
 * - Multiple retrieval methods (semantic, recent, by-type)
 */

export class MemoryRetriever {
  constructor(storage, embeddingProvider) {
    this.storage = storage;
    this.embeddingProvider = embeddingProvider;
  }

  /**
   * Main retrieval method - semantic search with ranking
   * @param {string} query - Search query text
   * @param {Object} options - Retrieval options
   * @param {string} options.agent_wallet - Agent wallet address
   * @param {number} options.limit - Maximum results to return (default: 5)
   * @param {number} options.minScore - Minimum similarity score (default: 0.7)
   * @param {string} options.memory_type - Filter by memory type
   * @param {number} options.timeframeDays - Limit to recent N days
   * @returns {Promise<Array>} Ranked relevant memories
   */
  async retrieveRelevant(query, options = {}) {
    const {
      agent_wallet,
      limit = 5,
      minScore = 0.7,
      memory_type,
      timeframeDays
    } = options;

    // Check license tier restrictions
    if (timeframeDays) {
      await this.checkTierAccess(agent_wallet, timeframeDays);
    }

    // Generate query embedding
    const queryEmbedding = await this.embeddingProvider.generate(query);

    // Semantic search - get top candidates
    const candidateLimit = Math.max(limit * 4, 20); // Get more candidates for filtering
    const candidates = await this.storage.searchMemories(
      queryEmbedding,
      candidateLimit,
      minScore,
      { agent_wallet, memory_type }
    );

    // Apply timeframe filter if specified
    const filtered = this.applyFilters(candidates, { timeframeDays });

    // Rank by importance + recency + access count
    const ranked = this.rankMemories(filtered);

    // Take top results
    const results = ranked.slice(0, limit);

    // Record access for each returned memory
    for (const memory of results) {
      await this.storage.recordAccess(memory.memory_id, 'read', query);
    }

    return results;
  }

  /**
   * Check license tier and enforce access restrictions
   * @param {string} agentWallet - Agent wallet address
   * @param {number} timeframeDays - Requested timeframe in days
   * @throws {Error} If free tier tries to access beyond 7 days
   */
  async checkTierAccess(agentWallet, timeframeDays) {
    const quota = await this.storage.getQuota(agentWallet);

    if (quota.tier === 'free' && timeframeDays > 7) {
      throw new Error(
        'Free tier limited to 7-day history. Upgrade to Pro for unlimited access. ' +
        'Visit /api/x402/subscribe to upgrade for 0.5 USDT/month.'
      );
    }

    // Check if Pro tier has expired
    if (quota.tier === 'pro' && quota.paid_until) {
      const now = new Date();
      const expiry = new Date(quota.paid_until);

      if (expiry < now) {
        throw new Error(
          'Pro tier license has expired. Please renew to access full history. ' +
          'Visit /api/x402/subscribe to renew.'
        );
      }
    }
  }

  /**
   * Apply filters to candidate memories
   * @param {Array} memories - Candidate memories
   * @param {Object} filters - Filter options
   * @returns {Array} Filtered memories
   */
  applyFilters(memories, filters = {}) {
    let filtered = [...memories];

    // Timeframe filter
    if (filters.timeframeDays) {
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - filters.timeframeDays);

      filtered = filtered.filter(memory => {
        const memoryDate = new Date(memory.timestamp);
        return memoryDate >= cutoffDate;
      });
    }

    return filtered;
  }

  /**
   * Rank memories by composite score
   * Score = importance * 0.5 + recency * 0.3 + access_count * 0.2
   * @param {Array} memories - Memories to rank
   * @returns {Array} Sorted memories (highest rank first)
   */
  rankMemories(memories) {
    const now = Date.now();
    const MAX_AGE_MS = 90 * 24 * 60 * 60 * 1000; // 90 days for recency calculation

    return memories
      .map(memory => {
        const rank = this.calculateRank(memory, now, MAX_AGE_MS);
        return { ...memory, rank };
      })
      .sort((a, b) => b.rank - a.rank);
  }

  /**
   * Calculate composite rank score for a memory
   * @param {Object} memory - Memory object
   * @param {number} now - Current timestamp
   * @param {number} maxAge - Maximum age for recency calculation
   * @returns {number} Rank score (0.0 to 1.0)
   */
  calculateRank(memory, now, maxAge) {
    // Importance score (0.0 to 1.0, already normalized)
    const importanceScore = memory.importance_score || 0.5;

    // Recency score (newer = higher score)
    const memoryTimestamp = new Date(memory.timestamp).getTime();
    const age = now - memoryTimestamp;
    const recencyScore = Math.max(0, 1 - (age / maxAge));

    // Access count score (normalize by max seen, cap at 100 accesses)
    const maxAccesses = 100;
    const accessScore = Math.min(memory.accessed_count || 0, maxAccesses) / maxAccesses;

    // Weighted composite score
    const rank =
      importanceScore * 0.5 +
      recencyScore * 0.3 +
      accessScore * 0.2;

    return rank;
  }

  /**
   * Get recent memories (no embedding needed)
   * @param {string} agentWallet - Agent wallet address
   * @param {number} limit - Maximum results (default: 10)
   * @param {Object} options - Additional options
   * @returns {Promise<Array>} Recent memories
   */
  async getRecent(agentWallet, limit = 10, options = {}) {
    // Check tier for timeframe
    if (options.timeframeDays) {
      await this.checkTierAccess(agentWallet, options.timeframeDays);
    }

    const filters = {
      agent_wallet: agentWallet,
      limit: options.timeframeDays ? 1000 : limit, // Get more if filtering by time
      order: 'timestamp DESC'
    };

    let memories = await this.storage.getMemories(filters);

    // Apply timeframe filter if specified
    if (options.timeframeDays) {
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - options.timeframeDays);
      memories = memories.filter(m => new Date(m.timestamp) >= cutoffDate);
      memories = memories.slice(0, limit);
    }

    // Record access
    for (const memory of memories) {
      await this.storage.recordAccess(memory.memory_id, 'read', 'recent_query');
    }

    return memories;
  }

  /**
   * Get memories by type
   * @param {string} agentWallet - Agent wallet address
   * @param {string} type - Memory type ('fact', 'conversation', 'preference', 'pattern')
   * @param {Object} options - Additional options
   * @returns {Promise<Array>} Memories of specified type
   */
  async getByType(agentWallet, type, options = {}) {
    const { limit = 50, order = 'timestamp DESC' } = options;

    // Check tier for timeframe
    if (options.timeframeDays) {
      await this.checkTierAccess(agentWallet, options.timeframeDays);
    }

    const filters = {
      agent_wallet: agentWallet,
      memory_type: type,
      limit: options.timeframeDays ? 1000 : limit, // Get more if filtering by time
      order
    };

    let memories = await this.storage.getMemories(filters);

    // Apply timeframe filter if specified
    if (options.timeframeDays) {
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - options.timeframeDays);
      memories = memories.filter(m => new Date(m.timestamp) >= cutoffDate);
      memories = memories.slice(0, limit);
    }

    // Record access
    for (const memory of memories) {
      await this.storage.recordAccess(memory.memory_id, 'read', `type_query:${type}`);
    }

    return memories;
  }

  /**
   * Get memories related to a specific memory
   * @param {string} memoryId - Memory ID to find relations for
   * @param {Object} options - Options
   * @returns {Promise<Array>} Related memories with relation metadata
   */
  async getRelated(memoryId, options = {}) {
    const { limit = 10, relationType } = options;

    // Get all relations (storage.getRelations doesn't accept relationType parameter)
    let relations = await this.storage.getRelations(memoryId);

    // Filter by relation type if specified
    if (relationType) {
      relations = relations.filter(r => r.relation_type === relationType);
    }

    // Fetch full memory objects for related memories
    const relatedMemories = [];
    for (const relation of relations.slice(0, limit)) {
      const memory = await this.storage.getMemory(relation.to_memory_id);
      if (memory) {
        relatedMemories.push({
          ...memory,
          relation_type: relation.relation_type,
          relation_strength: relation.strength
        });
      }
    }

    // Record access
    for (const memory of relatedMemories) {
      await this.storage.recordAccess(memory.memory_id, 'read', `related_to:${memoryId}`);
    }

    return relatedMemories;
  }

  /**
   * Search memories by session ID
   * @param {string} sessionId - Session ID
   * @param {Object} options - Options
   * @returns {Promise<Array>} Memories from session
   */
  async getBySession(sessionId, options = {}) {
    const { limit = 100, order = 'timestamp ASC' } = options;

    const filters = {
      session_id: sessionId,
      limit,
      order
    };

    const memories = await this.storage.getMemories(filters);

    // Record access
    for (const memory of memories) {
      await this.storage.recordAccess(memory.memory_id, 'read', `session_query:${sessionId}`);
    }

    return memories;
  }

  /**
   * Get memory statistics for an agent
   * @param {string} agentWallet - Agent wallet address
   * @returns {Promise<Object>} Memory statistics
   */
  async getStats(agentWallet) {
    const quota = await this.storage.getQuota(agentWallet);
    const memories = await this.storage.getMemories({ agent_wallet: agentWallet });

    // Calculate statistics
    const stats = {
      total_count: memories.length,
      tier: quota.tier,
      memory_limit: quota.memory_limit,
      quota_used: `${memories.length}/${quota.memory_limit === -1 ? '∞' : quota.memory_limit}`,
      by_type: {},
      avg_importance: 0,
      total_accesses: 0,
      most_accessed: null
    };

    // Count by type and calculate averages
    let totalImportance = 0;
    let mostAccessed = null;

    for (const memory of memories) {
      // Count by type
      stats.by_type[memory.memory_type] = (stats.by_type[memory.memory_type] || 0) + 1;

      // Sum importance
      totalImportance += memory.importance_score || 0;

      // Sum accesses
      stats.total_accesses += memory.accessed_count || 0;

      // Track most accessed
      if (!mostAccessed || (memory.accessed_count > mostAccessed.accessed_count)) {
        mostAccessed = memory;
      }
    }

    stats.avg_importance = memories.length > 0 ? totalImportance / memories.length : 0;
    stats.most_accessed = mostAccessed ? {
      memory_id: mostAccessed.memory_id,
      content: mostAccessed.content.substring(0, 100),
      accessed_count: mostAccessed.accessed_count
    } : null;

    // Add tier info
    if (quota.tier === 'pro' && quota.paid_until) {
      const expiry = new Date(quota.paid_until);
      const now = new Date();
      const daysRemaining = Math.ceil((expiry - now) / (1000 * 60 * 60 * 24));

      stats.pro_expires = quota.paid_until;
      stats.pro_days_remaining = Math.max(0, daysRemaining);
    }

    return stats;
  }
}
