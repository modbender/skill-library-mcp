import Database from 'better-sqlite3';
import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

/**
 * MemoryStorage - SQLite storage with vector similarity search
 * Handles persistent memory storage for OpenClaw agents
 */
export class MemoryStorage {
  constructor(dbPath) {
    this.db = new Database(dbPath);
    this.db.pragma('journal_mode = WAL');
  }

  /**
   * Initialize database with migrations
   * Run this separately via setup.js
   */
  initialize() {
    // Run core memory schema
    const migration1 = readFileSync(
      join(__dirname, '../migrations/001-init.sql'),
      'utf-8'
    );
    this.db.exec(migration1);

    // Run x402 payment tables
    const migration2 = readFileSync(
      join(__dirname, '../migrations/002-x402-payments.sql'),
      'utf-8'
    );
    this.db.exec(migration2);
  }

  // ============================================
  // Memory CRUD Operations
  // ============================================

  /**
   * Record a new memory
   */
  recordMemory(data) {
    const stmt = this.db.prepare(`
      INSERT INTO memories (
        memory_id, agent_wallet, session_id, memory_type, content,
        embedding_vector, importance_score, context_metadata, expires_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    return stmt.run(
      data.memory_id,
      data.agent_wallet || null,
      data.session_id || null,
      data.memory_type,
      data.content,
      data.embedding_vector || null, // BLOB (serialized Float32Array)
      data.importance_score || 0.5,
      data.context_metadata ? JSON.stringify(data.context_metadata) : null,
      data.expires_at || null
    );
  }

  /**
   * Get a single memory by ID
   */
  getMemory(memoryId) {
    const stmt = this.db.prepare(`
      SELECT * FROM memories WHERE memory_id = ?
    `);
    const memory = stmt.get(memoryId);

    if (memory && memory.context_metadata) {
      memory.context_metadata = JSON.parse(memory.context_metadata);
    }

    return memory;
  }

  /**
   * Query memories with filters
   * @param {Object} filters - { agent_wallet, session_id, memory_type, timeframe, limit, order }
   */
  getMemories(filters = {}) {
    let query = 'SELECT * FROM memories WHERE 1=1';
    const params = [];

    if (filters.agent_wallet) {
      query += ' AND agent_wallet = ?';
      params.push(filters.agent_wallet);
    }

    if (filters.session_id) {
      query += ' AND session_id = ?';
      params.push(filters.session_id);
    }

    if (filters.memory_type) {
      query += ' AND memory_type = ?';
      params.push(filters.memory_type);
    }

    if (filters.timeframe) {
      query += " AND timestamp >= datetime('now', '-' || ?)";
      params.push(filters.timeframe);
    }

    if (filters.min_importance) {
      query += ' AND importance_score >= ?';
      params.push(filters.min_importance);
    }

    // Default ordering
    const order = filters.order || 'timestamp DESC';
    query += ` ORDER BY ${order}`;

    if (filters.limit) {
      query += ' LIMIT ?';
      params.push(filters.limit);
    }

    const stmt = this.db.prepare(query);
    const memories = stmt.all(...params);

    // Parse JSON metadata
    return memories.map(m => ({
      ...m,
      context_metadata: m.context_metadata ? JSON.parse(m.context_metadata) : null
    }));
  }

  /**
   * Update an existing memory
   */
  updateMemory(memoryId, updates) {
    const fields = [];
    const params = [];

    if (updates.content !== undefined) {
      fields.push('content = ?');
      params.push(updates.content);
    }

    if (updates.importance_score !== undefined) {
      fields.push('importance_score = ?');
      params.push(updates.importance_score);
    }

    if (updates.context_metadata !== undefined) {
      fields.push('context_metadata = ?');
      params.push(JSON.stringify(updates.context_metadata));
    }

    if (updates.embedding_vector !== undefined) {
      fields.push('embedding_vector = ?');
      params.push(updates.embedding_vector);
    }

    if (updates.expires_at !== undefined) {
      fields.push('expires_at = ?');
      params.push(updates.expires_at);
    }

    if (fields.length === 0) {
      throw new Error('No valid update fields provided');
    }

    params.push(memoryId);

    const stmt = this.db.prepare(`
      UPDATE memories SET ${fields.join(', ')}
      WHERE memory_id = ?
    `);

    return stmt.run(...params);
  }

  /**
   * Delete a memory (hard delete)
   */
  deleteMemory(memoryId) {
    const stmt = this.db.prepare('DELETE FROM memories WHERE memory_id = ?');
    return stmt.run(memoryId);
  }

  /**
   * Delete multiple memories by IDs
   */
  deleteMemories(memoryIds) {
    const placeholders = memoryIds.map(() => '?').join(',');
    const stmt = this.db.prepare(`
      DELETE FROM memories WHERE memory_id IN (${placeholders})
    `);
    return stmt.run(...memoryIds);
  }

  // ============================================
  // Vector Similarity Search
  // ============================================

  /**
   * Search memories by semantic similarity (cosine similarity)
   * @param {Float32Array|Buffer} queryEmbedding - Query vector
   * @param {number} limit - Max results
   * @param {number} minScore - Minimum similarity score (0.0 to 1.0)
   * @param {Object} filters - Additional filters (agent_wallet, memory_type, etc.)
   */
  searchMemories(queryEmbedding, limit = 10, minScore = 0.7, filters = {}) {
    // Convert Float32Array to Buffer if needed
    const queryBuffer = queryEmbedding instanceof Float32Array
      ? Buffer.from(queryEmbedding.buffer)
      : queryEmbedding;

    let query = `
      SELECT *, 0 as similarity_score
      FROM memories
      WHERE embedding_vector IS NOT NULL
    `;
    const params = [];

    if (filters.agent_wallet) {
      query += ' AND agent_wallet = ?';
      params.push(filters.agent_wallet);
    }

    if (filters.memory_type) {
      query += ' AND memory_type = ?';
      params.push(filters.memory_type);
    }

    if (filters.timeframe) {
      query += " AND timestamp >= datetime('now', '-' || ?)";
      params.push(filters.timeframe);
    }

    const stmt = this.db.prepare(query);
    const candidates = stmt.all(...params);

    // Calculate cosine similarity in JavaScript
    const results = candidates
      .map(memory => ({
        ...memory,
        similarity_score: this.cosineSimilarity(queryBuffer, memory.embedding_vector),
        context_metadata: memory.context_metadata ? JSON.parse(memory.context_metadata) : null
      }))
      .filter(m => m.similarity_score >= minScore)
      .sort((a, b) => b.similarity_score - a.similarity_score)
      .slice(0, limit);

    return results;
  }

  /**
   * Calculate cosine similarity between two vectors
   * @param {Buffer} vec1 - First vector (BLOB)
   * @param {Buffer} vec2 - Second vector (BLOB)
   * @returns {number} - Similarity score (0.0 to 1.0)
   */
  cosineSimilarity(vec1, vec2) {
    if (!vec1 || !vec2) return 0;

    // Convert buffers to Float32Arrays
    const a = new Float32Array(vec1.buffer || vec1);
    const b = new Float32Array(vec2.buffer || vec2);

    if (a.length !== b.length) return 0;

    let dotProduct = 0;
    let normA = 0;
    let normB = 0;

    for (let i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }

    const magnitude = Math.sqrt(normA) * Math.sqrt(normB);
    return magnitude === 0 ? 0 : dotProduct / magnitude;
  }

  // ============================================
  // Memory Relations
  // ============================================

  /**
   * Add a relationship between two memories
   */
  addRelation(fromMemoryId, toMemoryId, relationType, strength = 1.0) {
    const stmt = this.db.prepare(`
      INSERT INTO memory_relations (from_memory_id, to_memory_id, relation_type, strength)
      VALUES (?, ?, ?, ?)
    `);
    return stmt.run(fromMemoryId, toMemoryId, relationType, strength);
  }

  /**
   * Get all relations for a memory (both incoming and outgoing)
   */
  getRelations(memoryId) {
    const stmt = this.db.prepare(`
      SELECT * FROM memory_relations
      WHERE from_memory_id = ? OR to_memory_id = ?
      ORDER BY strength DESC
    `);
    return stmt.all(memoryId, memoryId);
  }

  /**
   * Get outgoing relations (this memory relates to others)
   */
  getOutgoingRelations(memoryId) {
    const stmt = this.db.prepare(`
      SELECT * FROM memory_relations
      WHERE from_memory_id = ?
      ORDER BY strength DESC
    `);
    return stmt.all(memoryId);
  }

  /**
   * Get incoming relations (other memories relate to this one)
   */
  getIncomingRelations(memoryId) {
    const stmt = this.db.prepare(`
      SELECT * FROM memory_relations
      WHERE to_memory_id = ?
      ORDER BY strength DESC
    `);
    return stmt.all(memoryId);
  }

  /**
   * Delete a relation
   */
  deleteRelation(fromMemoryId, toMemoryId) {
    const stmt = this.db.prepare(`
      DELETE FROM memory_relations
      WHERE from_memory_id = ? AND to_memory_id = ?
    `);
    return stmt.run(fromMemoryId, toMemoryId);
  }

  // ============================================
  // Access Tracking
  // ============================================

  /**
   * Record memory access
   */
  recordAccess(memoryId, accessType, context = null) {
    // Insert access log
    const logStmt = this.db.prepare(`
      INSERT INTO memory_access_log (memory_id, access_type, context)
      VALUES (?, ?, ?)
    `);
    logStmt.run(memoryId, accessType, context);

    // Update memory access count and timestamp
    const updateStmt = this.db.prepare(`
      UPDATE memories
      SET accessed_count = accessed_count + 1,
          last_accessed = CURRENT_TIMESTAMP
      WHERE memory_id = ?
    `);
    return updateStmt.run(memoryId);
  }

  /**
   * Get access statistics for a memory
   */
  getAccessStats(memoryId) {
    const stmt = this.db.prepare(`
      SELECT
        COUNT(*) as total_accesses,
        MAX(accessed_at) as last_accessed,
        MIN(accessed_at) as first_accessed
      FROM memory_access_log
      WHERE memory_id = ?
    `);
    return stmt.get(memoryId);
  }

  /**
   * Get recent access log
   */
  getAccessLog(memoryId, limit = 10) {
    const stmt = this.db.prepare(`
      SELECT * FROM memory_access_log
      WHERE memory_id = ?
      ORDER BY accessed_at DESC
      LIMIT ?
    `);
    return stmt.all(memoryId, limit);
  }

  // ============================================
  // Quota Management
  // ============================================

  /**
   * Get agent's memory quota
   */
  getQuota(agentWallet) {
    const stmt = this.db.prepare(`
      SELECT * FROM agent_memory_quotas WHERE agent_wallet = ?
    `);
    let quota = stmt.get(agentWallet);

    // Initialize quota if doesn't exist
    if (!quota) {
      quota = this.initializeQuota(agentWallet);
    }

    return quota;
  }

  /**
   * Initialize default quota for new agent
   */
  initializeQuota(agentWallet) {
    const stmt = this.db.prepare(`
      INSERT INTO agent_memory_quotas (agent_wallet, tier, memory_count, memory_limit)
      VALUES (?, 'free', 0, 100)
    `);
    stmt.run(agentWallet);

    return this.getQuota(agentWallet);
  }

  /**
   * Update agent's memory quota
   */
  updateQuota(agentWallet, updates) {
    const fields = [];
    const params = [];

    if (typeof updates === 'number') {
      // Simple count update
      fields.push('memory_count = ?');
      params.push(updates);
    } else {
      // Object with multiple fields
      if (updates.memory_count !== undefined) {
        fields.push('memory_count = ?');
        params.push(updates.memory_count);
      }

      if (updates.tier !== undefined) {
        fields.push('tier = ?');
        params.push(updates.tier);
      }

      if (updates.memory_limit !== undefined) {
        fields.push('memory_limit = ?');
        params.push(updates.memory_limit);
      }

      if (updates.paid_until !== undefined) {
        fields.push('paid_until = ?');
        params.push(updates.paid_until);
      }
    }

    fields.push("updated_at = CURRENT_TIMESTAMP");
    params.push(agentWallet);

    const stmt = this.db.prepare(`
      UPDATE agent_memory_quotas
      SET ${fields.join(', ')}
      WHERE agent_wallet = ?
    `);

    return stmt.run(...params);
  }

  /**
   * Check if agent has quota available
   * @returns {Object} { available: boolean, remaining: number, limit: number }
   */
  checkQuotaAvailable(agentWallet) {
    const quota = this.getQuota(agentWallet);

    // Pro tier has unlimited quota
    if (quota.tier === 'pro' && quota.memory_limit === -1) {
      return {
        available: true,
        remaining: -1,
        limit: -1,
        tier: 'pro'
      };
    }

    const remaining = quota.memory_limit - quota.memory_count;
    return {
      available: remaining > 0,
      remaining: Math.max(0, remaining),
      limit: quota.memory_limit,
      tier: quota.tier
    };
  }

  /**
   * Increment memory count for agent
   */
  incrementMemoryCount(agentWallet, delta = 1) {
    const stmt = this.db.prepare(`
      UPDATE agent_memory_quotas
      SET memory_count = memory_count + ?,
          updated_at = CURRENT_TIMESTAMP
      WHERE agent_wallet = ?
    `);
    return stmt.run(delta, agentWallet);
  }

  /**
   * Recalculate memory count from actual memories
   */
  recalculateMemoryCount(agentWallet) {
    const countStmt = this.db.prepare(`
      SELECT COUNT(*) as count FROM memories WHERE agent_wallet = ?
    `);
    const { count } = countStmt.get(agentWallet);

    return this.updateQuota(agentWallet, { memory_count: count });
  }

  /**
   * Update agent tier and paid_until date
   */
  updateAgentTier(agentWallet, tier, paidUntil) {
    const stmt = this.db.prepare(`
      UPDATE agent_memory_quotas
      SET tier = ?,
          paid_until = ?,
          memory_limit = ?,
          updated_at = CURRENT_TIMESTAMP
      WHERE agent_wallet = ?
    `);

    // Pro tier gets unlimited memory
    const memoryLimit = tier === 'pro' ? -1 : 100;

    return stmt.run(tier, paidUntil, memoryLimit, agentWallet);
  }

  // ============================================
  // Pruning Queries
  // ============================================

  /**
   * Get expired memories
   */
  getExpiredMemories() {
    const stmt = this.db.prepare(`
      SELECT * FROM memories
      WHERE expires_at IS NOT NULL
        AND expires_at < CURRENT_TIMESTAMP
      ORDER BY expires_at ASC
    `);
    return stmt.all();
  }

  /**
   * Get least accessed memories
   */
  getLeastAccessedMemories(agentWallet, limit = 10) {
    const stmt = this.db.prepare(`
      SELECT * FROM memories
      WHERE agent_wallet = ?
      ORDER BY accessed_count ASC, importance_score ASC, timestamp ASC
      LIMIT ?
    `);
    return stmt.all(agentWallet, limit);
  }

  /**
   * Get oldest memories for an agent
   */
  getOldestMemories(agentWallet, limit = 10) {
    const stmt = this.db.prepare(`
      SELECT * FROM memories
      WHERE agent_wallet = ?
      ORDER BY timestamp ASC
      LIMIT ?
    `);
    return stmt.all(agentWallet, limit);
  }

  /**
   * Get memories to prune (low importance + low access + old)
   */
  getMemoriesToPrune(agentWallet, limit = 10) {
    const stmt = this.db.prepare(`
      SELECT * FROM memories
      WHERE agent_wallet = ?
      ORDER BY
        importance_score ASC,
        accessed_count ASC,
        timestamp ASC
      LIMIT ?
    `);
    return stmt.all(agentWallet, limit);
  }

  /**
   * Get memory count by agent
   */
  getMemoryCount(agentWallet) {
    const stmt = this.db.prepare(`
      SELECT COUNT(*) as count FROM memories WHERE agent_wallet = ?
    `);
    return stmt.get(agentWallet).count;
  }

  /**
   * Get memory statistics for agent
   */
  getMemoryStats(agentWallet) {
    const quota = this.getQuota(agentWallet);

    const typeStmt = this.db.prepare(`
      SELECT memory_type, COUNT(*) as count
      FROM memories
      WHERE agent_wallet = ?
      GROUP BY memory_type
    `);
    const byType = typeStmt.all(agentWallet);

    const avgStmt = this.db.prepare(`
      SELECT
        AVG(importance_score) as avg_importance,
        AVG(accessed_count) as avg_access_count
      FROM memories
      WHERE agent_wallet = ?
    `);
    const averages = avgStmt.get(agentWallet);

    return {
      agent_wallet: agentWallet,
      tier: quota.tier,
      memory_count: quota.memory_count,
      memory_limit: quota.memory_limit,
      paid_until: quota.paid_until,
      by_type: byType.reduce((acc, row) => {
        acc[row.memory_type] = row.count;
        return acc;
      }, {}),
      avg_importance: averages.avg_importance || 0,
      avg_access_count: averages.avg_access_count || 0
    };
  }

  // ============================================
  // x402 Payment Methods
  // ============================================

  /**
   * Record a payment request
   */
  recordPaymentRequest(requestId, agentWallet, amount, token) {
    const stmt = this.db.prepare(`
      INSERT INTO payment_requests (request_id, agent_wallet, amount_requested, token, status)
      VALUES (?, ?, ?, ?, 'pending')
    `);
    return stmt.run(requestId, agentWallet, amount, token);
  }

  /**
   * Get payment request
   */
  getPaymentRequest(requestId) {
    const stmt = this.db.prepare(`
      SELECT * FROM payment_requests WHERE request_id = ?
    `);
    return stmt.get(requestId);
  }

  /**
   * Update payment request status
   */
  updatePaymentRequest(requestId, status, txHash = null) {
    const stmt = this.db.prepare(`
      UPDATE payment_requests
      SET status = ?,
          completed_at = CURRENT_TIMESTAMP,
          tx_hash = ?
      WHERE request_id = ?
    `);
    return stmt.run(status, txHash, requestId);
  }

  /**
   * Record a payment transaction
   */
  recordPaymentTransaction(data) {
    const stmt = this.db.prepare(`
      INSERT INTO payment_transactions (
        agent_wallet, tx_hash, amount, token, chain,
        verified, tier_granted, duration_months
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `);

    return stmt.run(
      data.agent_wallet,
      data.tx_hash,
      data.amount,
      data.token,
      data.chain,
      data.verified ? 1 : 0,
      data.tier_granted,
      data.duration_months || 1
    );
  }

  /**
   * Get payment transactions for an agent
   */
  getPaymentTransactions(agentWallet) {
    const stmt = this.db.prepare(`
      SELECT * FROM payment_transactions
      WHERE agent_wallet = ?
      ORDER BY timestamp DESC
    `);
    return stmt.all(agentWallet);
  }

  /**
   * Get latest payment transaction
   */
  getLatestPayment(agentWallet) {
    const stmt = this.db.prepare(`
      SELECT * FROM payment_transactions
      WHERE agent_wallet = ?
      ORDER BY timestamp DESC
      LIMIT 1
    `);
    return stmt.get(agentWallet);
  }

  /**
   * Verify if transaction hash exists
   */
  hasTransaction(txHash) {
    const stmt = this.db.prepare(`
      SELECT COUNT(*) as count FROM payment_transactions WHERE tx_hash = ?
    `);
    return stmt.get(txHash).count > 0;
  }

  // ============================================
  // Utility Methods
  // ============================================

  /**
   * Clean up expired memories
   */
  cleanupExpired() {
    const stmt = this.db.prepare(`
      DELETE FROM memories
      WHERE expires_at IS NOT NULL
        AND expires_at < CURRENT_TIMESTAMP
    `);
    return stmt.run();
  }

  /**
   * Clean up old access logs (keep last 30 days)
   */
  cleanupAccessLogs(days = 30) {
    const stmt = this.db.prepare(`
      DELETE FROM memory_access_log
      WHERE accessed_at < datetime('now', '-' || ? || ' days')
    `);
    return stmt.run(days);
  }

  /**
   * Vacuum database to reclaim space
   */
  vacuum() {
    this.db.exec('VACUUM');
  }

  /**
   * Close database connection
   */
  close() {
    this.db.close();
  }
}
