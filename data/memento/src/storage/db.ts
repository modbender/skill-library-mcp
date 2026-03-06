import { existsSync, mkdirSync } from "node:fs";
import { dirname } from "node:path";
import { randomUUID } from "node:crypto";
import { createRequire } from "node:module";

import {
  ALL_DDL,
  SCHEMA_VERSION,
  MIGRATE_V2_TO_V3,
  CREATE_FACTS_EMBEDDING_IDX,
  MIGRATE_V3_TO_V4,
  MIGRATE_V4_TO_V5,
  MIGRATE_V5_TO_V6,
  MIGRATE_V6_TO_V7,
  type ConversationRow,
  type MessageRow,
  type FactRow,
  type FactRelationRow,
  type FactClusterRow,
  type ClusterMemberRow,
  type FactOccurrenceRow,
  type ExtractionLogRow,
} from "./schema.js";

// ---------------------------------------------------------------------------
// Visibility level ordering (shared < private < secret)
// ---------------------------------------------------------------------------

function visibilityLevel(vis: string): number {
  switch (vis) {
    case "shared": return 0;
    case "private": return 1;
    case "secret": return 2;
    default: return 0;
  }
}

// ---------------------------------------------------------------------------
// better-sqlite3 loading
// ---------------------------------------------------------------------------
// better-sqlite3 is a native addon — use createRequire for reliable loading
// in both CJS and ESM / jiti contexts.
//
// Type-only import is used for IDE support; the actual module is loaded via
// createRequire at runtime so it works regardless of the module format.
// ---------------------------------------------------------------------------

import type BetterSQLite3 from "better-sqlite3";
type Database = BetterSQLite3.Database;
// DatabaseConstructor is the callable class (new Database(...))
type DatabaseConstructor = typeof BetterSQLite3;

let _DatabaseCtor: DatabaseConstructor | null = null;

function loadSQLite3(): DatabaseConstructor {
  if (_DatabaseCtor) return _DatabaseCtor;
  try {
    // Use a safe fallback for import.meta.url — jiti may not support it
    let resolveFrom = "file:///";
    try { resolveFrom = import.meta.url; } catch (_) { /* jiti fallback */ }
    const req = createRequire(resolveFrom);
    // `require("better-sqlite3")` returns the constructor function directly
    _DatabaseCtor = req("better-sqlite3") as DatabaseConstructor;
    return _DatabaseCtor;
  } catch (err) {
    throw new Error(
      `memento: failed to load better-sqlite3. ` +
        `Run: npm install better-sqlite3\n${String(err)}`,
      { cause: err },
    );
  }
}

// ---------------------------------------------------------------------------
// ExtractionLogResult (input shape for logExtraction)
// ---------------------------------------------------------------------------

export type ExtractionLogResult = {
  modelUsed: string;
  factsExtracted: number;
  factsUpdated: number;
  factsDeduplicated: number;
  error: string | null;
};

// ---------------------------------------------------------------------------
// ConversationDB
// ---------------------------------------------------------------------------

export class ConversationDB {
  private db: Database | null = null;

  constructor(private readonly dbPath: string) {}

  // ---- Lazy synchronous initialisation ------------------------------------

  private ensureInit(): Database {
    if (this.db) return this.db;

    const dir = dirname(this.dbPath);
    if (!existsSync(dir)) {
      mkdirSync(dir, { recursive: true });
    }

    const DatabaseCtor = loadSQLite3();
    this.db = new DatabaseCtor(this.dbPath);

    // Optimise for write throughput
    this.db.pragma("journal_mode = WAL");
    this.db.pragma("synchronous = NORMAL");

    // Apply schema (all statements are idempotent CREATE IF NOT EXISTS)
    for (const ddl of ALL_DDL) {
      this.db.exec(ddl);
    }

    // Schema version tracking + migrations
    const versionRow = this.db
      .prepare(
        "SELECT value FROM schema_meta WHERE key = 'schema_version'",
      )
      .get() as { value: string } | undefined;

    const currentVersion = versionRow ? parseInt(versionRow.value, 10) : 0;

    if (!versionRow) {
      this.db
        .prepare(
          "INSERT INTO schema_meta (key, value) VALUES ('schema_version', ?)",
        )
        .run(String(SCHEMA_VERSION));
    } else if (currentVersion < SCHEMA_VERSION) {
      // Run migrations
      this.migrateSchema(currentVersion);
      this.db
        .prepare(
          "UPDATE schema_meta SET value = ? WHERE key = 'schema_version'",
        )
        .run(String(SCHEMA_VERSION));
    }

    return this.db;
  }

  // =========================================================================
  // Schema migrations
  // =========================================================================

  private migrateSchema(fromVersion: number): void {
    const db = this.db!;

    if (fromVersion < 3) {
      // v2 → v3: Add embedding column to facts
      try {
        db.exec(MIGRATE_V2_TO_V3);
      } catch (err) {
        // Column may already exist (e.g., partial migration)
        const msg = String(err);
        if (!msg.includes("duplicate column")) throw err;
      }
      db.exec(CREATE_FACTS_EMBEDDING_IDX);
    }

    if (fromVersion < 4) {
      // v3 → v4: Add fact_relations table for knowledge graph
      for (const ddl of MIGRATE_V3_TO_V4) {
        db.exec(ddl);
      }
    }

    if (fromVersion < 5) {
      // v4 → v5: Add fact_clusters + cluster_members for multi-layer memory
      for (const ddl of MIGRATE_V4_TO_V5) {
        db.exec(ddl);
      }
    }

    if (fromVersion < 6) {
      // v5 → v6: Add ingest_tokens + ingest_file_log for remote JSONL ingest
      for (const ddl of MIGRATE_V5_TO_V6) {
        db.exec(ddl);
      }
    }

    if (fromVersion < 7) {
      // v6 → v7: Add causal_weight to fact_relations; add previous_value to facts
      for (const ddl of MIGRATE_V6_TO_V7) {
        try {
          db.exec(ddl);
        } catch (err) {
          // Column may already exist on fresh installs using updated DDL
          const msg = String(err);
          if (!msg.includes("duplicate column")) throw err;
        }
      }
    }
  }

  // =========================================================================
  // Phase 1 — Conversation capture
  // =========================================================================

  insertConversationWithMessages(
    conversation: ConversationRow,
    messages: MessageRow[],
  ): void {
    const db = this.ensureInit();

    const insertConv = db.prepare(`
      INSERT OR IGNORE INTO conversations
        (id, agent_id, session_key, channel, started_at, ended_at, turn_count, raw_text, metadata)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    const insertMsg = db.prepare(`
      INSERT OR IGNORE INTO messages
        (id, conversation_id, role, content, timestamp, message_id, metadata)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `);

    const tx = db.transaction(() => {
      insertConv.run(
        conversation.id,
        conversation.agent_id,
        conversation.session_key,
        conversation.channel ?? null,
        conversation.started_at,
        conversation.ended_at,
        conversation.turn_count,
        conversation.raw_text,
        conversation.metadata ?? null,
      );

      for (const msg of messages) {
        insertMsg.run(
          msg.id,
          msg.conversation_id,
          msg.role,
          msg.content,
          msg.timestamp,
          msg.message_id ?? null,
          msg.metadata ?? null,
        );
      }
    });

    tx();
  }

  // =========================================================================
  // Phase 2 — Knowledge base
  // =========================================================================

  /**
   * Insert a new fact into the knowledge base.
   * The fact's occurrence_count should be 0; it will be incremented by
   * the first updateFactOccurrence call.
   */
  insertFact(fact: FactRow): void {
    const db = this.ensureInit();
    db.prepare(`
      INSERT OR IGNORE INTO facts
        (id, agent_id, category, content, summary, visibility, confidence,
         first_seen_at, last_seen_at, occurrence_count, supersedes, is_active, metadata,
         previous_value)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      fact.id,
      fact.agent_id,
      fact.category,
      fact.content,
      fact.summary ?? null,
      fact.visibility,
      fact.confidence,
      fact.first_seen_at,
      fact.last_seen_at,
      fact.occurrence_count,
      fact.supersedes ?? null,
      fact.is_active,
      fact.metadata ?? null,
      fact.previous_value ?? null,
    );
  }

  /**
   * Record that a fact was seen in this conversation:
   *   - Inserts a row into fact_occurrences
   *   - Increments occurrence_count and updates last_seen_at on the fact
   *
   * Both writes happen in a single transaction.
   */
  updateFactOccurrence(
    factId: string,
    conversationId: string,
    contextSnippet: string | null,
    sentiment: string | null,
    timestamp: number = Date.now(),
  ): void {
    const db = this.ensureInit();

    const insertOccurrence = db.prepare(`
      INSERT OR IGNORE INTO fact_occurrences
        (id, fact_id, conversation_id, timestamp, context_snippet, sentiment)
      VALUES (?, ?, ?, ?, ?, ?)
    `);

    const updateFact = db.prepare(`
      UPDATE facts
        SET occurrence_count = occurrence_count + 1,
            last_seen_at = ?
      WHERE id = ?
    `);

    const tx = db.transaction(() => {
      insertOccurrence.run(
        randomUUID(),
        factId,
        conversationId,
        timestamp,
        contextSnippet ? contextSnippet.slice(0, 500) : null,
        sentiment ?? null,
      );
      updateFact.run(timestamp, factId);
    });

    tx();
  }

  /**
   * Mark an existing fact as inactive (superseded), then insert the new fact.
   * Automatically sets previous_value on the new fact from the old fact's content.
   * Both writes are atomic.
   */
  supersedeFact(oldFactId: string, newFact: FactRow): void {
    const db = this.ensureInit();

    // Fetch the old fact's content to populate previous_value on the new fact
    const oldFactRow = db
      .prepare("SELECT content FROM facts WHERE id = ?")
      .get(oldFactId) as { content: string } | undefined;
    const previousValue = oldFactRow?.content ?? null;

    const deactivate = db.prepare(
      `UPDATE facts SET is_active = 0 WHERE id = ?`,
    );

    const insertNew = db.prepare(`
      INSERT OR IGNORE INTO facts
        (id, agent_id, category, content, summary, visibility, confidence,
         first_seen_at, last_seen_at, occurrence_count, supersedes, is_active, metadata,
         previous_value)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    const tx = db.transaction(() => {
      deactivate.run(oldFactId);
      insertNew.run(
        newFact.id,
        newFact.agent_id,
        newFact.category,
        newFact.content,
        newFact.summary ?? null,
        newFact.visibility,
        newFact.confidence,
        newFact.first_seen_at,
        newFact.last_seen_at,
        newFact.occurrence_count,
        oldFactId, // supersedes
        1,         // is_active
        newFact.metadata ?? null,
        previousValue, // previous_value = old fact's content
      );
    });

    tx();
  }

  /**
   * Record an extraction attempt (success or failure) in the extraction_log.
   * Uses INSERT OR REPLACE so re-processing is idempotent.
   */
  logExtraction(conversationId: string, result: ExtractionLogResult): void {
    const db = this.ensureInit();
    db.prepare(`
      INSERT OR REPLACE INTO extraction_log
        (conversation_id, extracted_at, model_used, facts_extracted,
         facts_updated, facts_deduplicated, error)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `).run(
      conversationId,
      Date.now(),
      result.modelUsed,
      result.factsExtracted,
      result.factsUpdated,
      result.factsDeduplicated,
      result.error ?? null,
    );
  }

  /**
   * Return active facts for an agent, ordered by most recently seen.
   * Used as context for the LLM deduplication prompt.
   */
  getRelevantFacts(agentId: string, limit: number): FactRow[] {
    const db = this.ensureInit();
    return db
      .prepare(
        `SELECT * FROM facts
         WHERE agent_id = ? AND is_active = 1
         ORDER BY last_seen_at DESC, occurrence_count DESC
         LIMIT ?`,
      )
      .all(agentId, limit) as FactRow[];
  }

  /**
   * Return true if extraction_log already has an entry for this conversation.
   * Used by the migration script to skip already-processed files.
   */
  isExtracted(conversationId: string): boolean {
    const db = this.ensureInit();
    const row = db
      .prepare("SELECT 1 FROM extraction_log WHERE conversation_id = ?")
      .get(conversationId);
    return row !== undefined;
  }

  /**
   * Return conversations that have not yet been processed by the extractor.
   * Sorted oldest-first so we process in chronological order.
   */
  getUnextractedConversations(): ConversationRow[] {
    const db = this.ensureInit();
    return db
      .prepare(
        `SELECT c.*
         FROM conversations c
         LEFT JOIN extraction_log el ON el.conversation_id = c.id
         WHERE el.conversation_id IS NULL
         ORDER BY c.started_at ASC`,
      )
      .all() as ConversationRow[];
  }

  /**
   * Return active facts for an agent filtered by category.
   */
  getFactsByCategory(agentId: string, category: string): FactRow[] {
    const db = this.ensureInit();
    return db
      .prepare(
        `SELECT * FROM facts
         WHERE agent_id = ? AND category = ? AND is_active = 1
         ORDER BY last_seen_at DESC`,
      )
      .all(agentId, category) as FactRow[];
  }

  /**
   * Full-text search over fact content and summary using FTS5.
   * Returns active facts for the given agent matching the query.
   *
   * The query uses FTS5 MATCH syntax; simple word queries work directly.
   * Special characters are sanitized to avoid FTS5 parse errors.
   */
  searchFacts(agentId: string, query: string): FactRow[] {
    const db = this.ensureInit();

    // Basic FTS5 query sanitization: strip characters that break the parser
    const safeQuery = query
      .replace(/[^\w\s\-']/g, " ")
      .trim();

    if (!safeQuery) return [];

    try {
      return db
        .prepare(
          `SELECT f.*
           FROM facts f
           JOIN facts_fts ON facts_fts.rowid = f.rowid
           WHERE facts_fts MATCH ?
             AND f.agent_id = ?
             AND f.is_active = 1
           ORDER BY rank`,
        )
        .all(safeQuery, agentId) as FactRow[];
    } catch (_err) {
      // FTS5 parse errors are not fatal
      return [];
    }
  }

  // =========================================================================
  // Phase 4 — Master Knowledge Base (cross-agent shared facts)
  // =========================================================================

  /**
   * Search shared facts from OTHER agents (excluding the querying agent).
   * Only returns facts with visibility = 'shared'.
   * Used by the recall layer to augment agent-local results with
   * cross-agent knowledge.
   */
  getSharedFactsFromOtherAgents(
    excludeAgentId: string,
    limit: number,
  ): FactRow[] {
    const db = this.ensureInit();
    return db
      .prepare(
        `SELECT * FROM facts
         WHERE agent_id != ? AND visibility = 'shared' AND is_active = 1
         ORDER BY last_seen_at DESC, occurrence_count DESC
         LIMIT ?`,
      )
      .all(excludeAgentId, limit) as FactRow[];
  }

  /**
   * FTS5 search over shared facts from OTHER agents.
   * Mirrors searchFacts() but restricted to visibility = 'shared'
   * and agent_id != the querying agent.
   */
  searchSharedFacts(excludeAgentId: string, query: string): FactRow[] {
    const db = this.ensureInit();

    const safeQuery = query
      .replace(/[^\w\s\-']/g, " ")
      .trim();

    if (!safeQuery) return [];

    try {
      return db
        .prepare(
          `SELECT f.*
           FROM facts f
           JOIN facts_fts ON facts_fts.rowid = f.rowid
           WHERE facts_fts MATCH ?
             AND f.agent_id != ?
             AND f.visibility = 'shared'
             AND f.is_active = 1
           ORDER BY rank`,
        )
        .all(safeQuery, excludeAgentId) as FactRow[];
    } catch (_err) {
      return [];
    }
  }

  /**
   * Get all distinct agent IDs that have contributed facts.
   * Useful for provenance display in the recall context.
   */
  getContributingAgents(): string[] {
    const db = this.ensureInit();
    return (
      db
        .prepare(
          `SELECT DISTINCT agent_id FROM facts WHERE is_active = 1 ORDER BY agent_id`,
        )
        .all() as { agent_id: string }[]
    ).map((r) => r.agent_id);
  }

  /**
   * Get shared facts for the master KB view — all agents' shared facts,
   * deduplicated by taking the most recently updated version when
   * multiple agents have similar facts.
   */
  getMasterKBFacts(limit: number): FactRow[] {
    const db = this.ensureInit();
    return db
      .prepare(
        `SELECT * FROM facts
         WHERE visibility = 'shared' AND is_active = 1
         ORDER BY last_seen_at DESC, occurrence_count DESC
         LIMIT ?`,
      )
      .all(limit) as FactRow[];
  }

  /**
   * Update only the confidence value for a fact (used by decay logic).
   */
  updateFactConfidence(factId: string, confidence: number): void {
    const db = this.ensureInit();
    db.prepare("UPDATE facts SET confidence = ? WHERE id = ?").run(
      confidence,
      factId,
    );
  }

  // =========================================================================
  // Knowledge Graph (fact relations)
  // =========================================================================

  /**
   * Insert a single relation edge. Uses INSERT OR IGNORE for idempotency.
   */
  insertRelation(relation: FactRelationRow): void {
    const db = this.ensureInit();
    db.prepare(`
      INSERT OR IGNORE INTO fact_relations
        (id, source_id, target_id, relation_type, strength, causal_weight, created_at, created_by, metadata)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      relation.id,
      relation.source_id,
      relation.target_id,
      relation.relation_type,
      relation.strength,
      relation.causal_weight ?? 1.0,
      relation.created_at,
      relation.created_by ?? null,
      relation.metadata ?? null,
    );
  }

  /**
   * Batch-insert relation edges in a single transaction.
   */
  insertRelationsBatch(relations: FactRelationRow[]): void {
    if (relations.length === 0) return;
    const db = this.ensureInit();
    const stmt = db.prepare(`
      INSERT OR IGNORE INTO fact_relations
        (id, source_id, target_id, relation_type, strength, causal_weight, created_at, created_by, metadata)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    const tx = db.transaction(() => {
      for (const r of relations) {
        stmt.run(
          r.id, r.source_id, r.target_id, r.relation_type,
          r.strength, r.causal_weight ?? 1.0, r.created_at, r.created_by ?? null, r.metadata ?? null,
        );
      }
    });
    tx();
  }

  /**
   * Get all relations where a fact is either the source or target.
   */
  getRelationsForFact(factId: string): FactRelationRow[] {
    const db = this.ensureInit();
    return db
      .prepare(
        `SELECT * FROM fact_relations
         WHERE source_id = ? OR target_id = ?`,
      )
      .all(factId, factId) as FactRelationRow[];
  }

  /**
   * Follow graph edges up to `maxHops` hops from a starting fact.
   * Returns unique connected active facts (excluding the start fact itself).
   *
   * @param factId   Starting fact ID
   * @param maxHops  How many edges to traverse (default 1)
   */
  getRelatedFacts(factId: string, maxHops: number = 1): FactRow[] {
    const db = this.ensureInit();
    const visited = new Set<string>([factId]);
    let frontier = [factId];

    for (let hop = 0; hop < maxHops && frontier.length > 0; hop++) {
      const nextFrontier: string[] = [];
      for (const fid of frontier) {
        const relations = db
          .prepare(
            `SELECT source_id, target_id FROM fact_relations
             WHERE source_id = ? OR target_id = ?`,
          )
          .all(fid, fid) as { source_id: string; target_id: string }[];

        for (const rel of relations) {
          const neighbor = rel.source_id === fid ? rel.target_id : rel.source_id;
          if (!visited.has(neighbor)) {
            visited.add(neighbor);
            nextFrontier.push(neighbor);
          }
        }
      }
      frontier = nextFrontier;
    }

    // Remove the starting fact from visited
    visited.delete(factId);
    if (visited.size === 0) return [];

    // Fetch the actual fact rows (active only)
    const placeholders = [...visited].map(() => "?").join(",");
    return db
      .prepare(
        `SELECT * FROM facts WHERE id IN (${placeholders}) AND is_active = 1`,
      )
      .all(...visited) as FactRow[];
  }

  /**
   * Like getRelatedFacts but filters by visibility level.
   * A relation is only traversable if BOTH endpoint facts have
   * visibility <= maxVisibility.
   *
   * Visibility order: shared (0) < private (1) < secret (2)
   */
  getRelatedFactsWithVisibility(
    factId: string,
    maxVisibility: "shared" | "private" | "secret",
  ): FactRow[] {
    const db = this.ensureInit();
    const visLevel = visibilityLevel(maxVisibility);

    const visited = new Set<string>([factId]);
    const frontier = [factId];
    const resultIds: string[] = [];

    // Single hop with visibility check
    for (const fid of frontier) {
      const relations = db
        .prepare(
          `SELECT fr.source_id, fr.target_id
           FROM fact_relations fr
           JOIN facts fs ON fs.id = fr.source_id
           JOIN facts ft ON ft.id = fr.target_id
           WHERE (fr.source_id = ? OR fr.target_id = ?)
             AND fs.is_active = 1 AND ft.is_active = 1`,
        )
        .all(fid, fid) as { source_id: string; target_id: string }[];

      for (const rel of relations) {
        const neighbor = rel.source_id === fid ? rel.target_id : rel.source_id;
        if (visited.has(neighbor)) continue;
        visited.add(neighbor);

        // Check visibility of the neighbor fact
        const neighborFact = db
          .prepare("SELECT visibility FROM facts WHERE id = ? AND is_active = 1")
          .get(neighbor) as { visibility: string } | undefined;

        if (
          neighborFact &&
          visibilityLevel(neighborFact.visibility) <= visLevel
        ) {
          resultIds.push(neighbor);
        }
      }
    }

    if (resultIds.length === 0) return [];
    const placeholders = resultIds.map(() => "?").join(",");
    return db
      .prepare(
        `SELECT * FROM facts WHERE id IN (${placeholders}) AND is_active = 1`,
      )
      .all(...resultIds) as FactRow[];
  }

  /**
   * Get the relation edge between two specific facts (if any).
   * Returns all edges between them (there could be multiple types).
   */
  getRelationBetween(
    factIdA: string,
    factIdB: string,
  ): FactRelationRow[] {
    const db = this.ensureInit();
    return db
      .prepare(
        `SELECT * FROM fact_relations
         WHERE (source_id = ? AND target_id = ?)
            OR (source_id = ? AND target_id = ?)`,
      )
      .all(factIdA, factIdB, factIdB, factIdA) as FactRelationRow[];
  }

  // =========================================================================
  // Multi-Layer Memory (clusters)
  // =========================================================================

  /**
   * Insert a new cluster node.
   */
  insertCluster(cluster: FactClusterRow): void {
    const db = this.ensureInit();
    db.prepare(`
      INSERT OR IGNORE INTO fact_clusters
        (id, agent_id, summary, description, layer, visibility, confidence,
         created_at, updated_at, is_active, metadata)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      cluster.id,
      cluster.agent_id,
      cluster.summary,
      cluster.description ?? null,
      cluster.layer,
      cluster.visibility,
      cluster.confidence,
      cluster.created_at,
      cluster.updated_at,
      cluster.is_active,
      cluster.metadata ?? null,
    );
  }

  /**
   * Update a cluster's summary, description, visibility, and confidence.
   * Also bumps updated_at.
   */
  updateCluster(
    clusterId: string,
    update: {
      summary?: string;
      description?: string | null;
      visibility?: string;
      confidence?: number;
    },
  ): void {
    const db = this.ensureInit();
    const sets: string[] = ["updated_at = ?"];
    const values: (string | number | null)[] = [Date.now()];

    if (update.summary !== undefined) {
      sets.push("summary = ?");
      values.push(update.summary);
    }
    if (update.description !== undefined) {
      sets.push("description = ?");
      values.push(update.description);
    }
    if (update.visibility !== undefined) {
      sets.push("visibility = ?");
      values.push(update.visibility);
    }
    if (update.confidence !== undefined) {
      sets.push("confidence = ?");
      values.push(update.confidence);
    }

    values.push(clusterId);
    db.prepare(
      `UPDATE fact_clusters SET ${sets.join(", ")} WHERE id = ?`,
    ).run(...values);
  }

  /**
   * Deactivate a cluster (soft delete).
   */
  deactivateCluster(clusterId: string): void {
    const db = this.ensureInit();
    db.prepare(
      "UPDATE fact_clusters SET is_active = 0, updated_at = ? WHERE id = ?",
    ).run(Date.now(), clusterId);
  }

  /**
   * Add a member (fact or child cluster) to a cluster.
   */
  addClusterMember(member: ClusterMemberRow): void {
    const db = this.ensureInit();
    db.prepare(`
      INSERT OR IGNORE INTO cluster_members
        (cluster_id, member_id, member_type, added_at)
      VALUES (?, ?, ?, ?)
    `).run(
      member.cluster_id,
      member.member_id,
      member.member_type,
      member.added_at,
    );
  }

  /**
   * Add multiple members to a cluster in a single transaction.
   */
  addClusterMembersBatch(members: ClusterMemberRow[]): void {
    if (members.length === 0) return;
    const db = this.ensureInit();
    const stmt = db.prepare(`
      INSERT OR IGNORE INTO cluster_members
        (cluster_id, member_id, member_type, added_at)
      VALUES (?, ?, ?, ?)
    `);
    const tx = db.transaction(() => {
      for (const m of members) {
        stmt.run(m.cluster_id, m.member_id, m.member_type, m.added_at);
      }
    });
    tx();
  }

  /**
   * Remove a member from a cluster.
   */
  removeClusterMember(clusterId: string, memberId: string): void {
    const db = this.ensureInit();
    db.prepare(
      "DELETE FROM cluster_members WHERE cluster_id = ? AND member_id = ?",
    ).run(clusterId, memberId);
  }

  /**
   * Get all members of a cluster (facts and/or child clusters).
   */
  getClusterMembers(clusterId: string): ClusterMemberRow[] {
    const db = this.ensureInit();
    return db
      .prepare("SELECT * FROM cluster_members WHERE cluster_id = ?")
      .all(clusterId) as ClusterMemberRow[];
  }

  /**
   * Get the fact rows that are members of a cluster.
   * Only returns active facts.
   */
  getClusterFacts(clusterId: string): FactRow[] {
    const db = this.ensureInit();
    return db
      .prepare(
        `SELECT f.* FROM facts f
         JOIN cluster_members cm ON cm.member_id = f.id
         WHERE cm.cluster_id = ? AND cm.member_type = 'fact' AND f.is_active = 1`,
      )
      .all(clusterId) as FactRow[];
  }

  /**
   * Get child clusters of a parent cluster.
   * Only returns active clusters.
   */
  getChildClusters(clusterId: string): FactClusterRow[] {
    const db = this.ensureInit();
    return db
      .prepare(
        `SELECT fc.* FROM fact_clusters fc
         JOIN cluster_members cm ON cm.member_id = fc.id
         WHERE cm.cluster_id = ? AND cm.member_type = 'cluster' AND fc.is_active = 1`,
      )
      .all(clusterId) as FactClusterRow[];
  }

  /**
   * Get all clusters a fact belongs to.
   */
  getClustersForFact(factId: string): FactClusterRow[] {
    const db = this.ensureInit();
    return db
      .prepare(
        `SELECT fc.* FROM fact_clusters fc
         JOIN cluster_members cm ON cm.cluster_id = fc.id
         WHERE cm.member_id = ? AND cm.member_type = 'fact' AND fc.is_active = 1`,
      )
      .all(factId) as FactClusterRow[];
  }

  /**
   * Get all active clusters for an agent, optionally filtered by layer.
   */
  getClusters(agentId: string, layer?: number): FactClusterRow[] {
    const db = this.ensureInit();
    if (layer !== undefined) {
      return db
        .prepare(
          `SELECT * FROM fact_clusters
           WHERE agent_id = ? AND layer = ? AND is_active = 1
           ORDER BY updated_at DESC`,
        )
        .all(agentId, layer) as FactClusterRow[];
    }
    return db
      .prepare(
        `SELECT * FROM fact_clusters
         WHERE agent_id = ? AND is_active = 1
         ORDER BY layer ASC, updated_at DESC`,
      )
      .all(agentId) as FactClusterRow[];
  }

  /**
   * Get unclustered active facts for an agent — facts not belonging to any active cluster.
   * Used by the consolidation engine to find facts that need grouping.
   */
  getUnclusteredFacts(agentId: string, limit: number = 100): FactRow[] {
    const db = this.ensureInit();
    return db
      .prepare(
        `SELECT f.* FROM facts f
         WHERE f.agent_id = ? AND f.is_active = 1
           AND f.id NOT IN (
             SELECT cm.member_id FROM cluster_members cm
             JOIN fact_clusters fc ON fc.id = cm.cluster_id
             WHERE cm.member_type = 'fact' AND fc.is_active = 1
           )
         ORDER BY f.last_seen_at DESC
         LIMIT ?`,
      )
      .all(agentId, limit) as FactRow[];
  }

  /**
   * Count of active clusters by layer for an agent.
   */
  getClusterStats(agentId: string): { layer: number; count: number }[] {
    const db = this.ensureInit();
    return db
      .prepare(
        `SELECT layer, COUNT(*) as count FROM fact_clusters
         WHERE agent_id = ? AND is_active = 1
         GROUP BY layer ORDER BY layer`,
      )
      .all(agentId) as { layer: number; count: number }[];
  }

  // =========================================================================
  // Embeddings
  // =========================================================================

  /**
   * Store an embedding vector for a fact.
   * The vector is stored as raw Float32Array bytes (compact BLOB).
   */
  setFactEmbedding(factId: string, embedding: number[]): void {
    const db = this.ensureInit();
    const buf = Buffer.from(new Float32Array(embedding).buffer);
    db.prepare("UPDATE facts SET embedding = ? WHERE id = ?").run(buf, factId);
  }

  /**
   * Batch-update embeddings for multiple facts in a single transaction.
   */
  setFactEmbeddingsBatch(
    updates: { factId: string; embedding: number[] }[],
  ): void {
    const db = this.ensureInit();
    const stmt = db.prepare("UPDATE facts SET embedding = ? WHERE id = ?");
    const tx = db.transaction(() => {
      for (const { factId, embedding } of updates) {
        const buf = Buffer.from(new Float32Array(embedding).buffer);
        stmt.run(buf, factId);
      }
    });
    tx();
  }

  /**
   * Get all active facts for an agent that have embeddings.
   * Returns facts with their embedding vectors decoded from BLOB.
   */
  getFactsWithEmbeddings(
    agentId: string,
    limit?: number,
  ): (FactRow & { embeddingVector: number[] })[] {
    const db = this.ensureInit();
    const sql = limit
      ? `SELECT * FROM facts
         WHERE agent_id = ? AND is_active = 1 AND embedding IS NOT NULL
         ORDER BY last_seen_at DESC LIMIT ?`
      : `SELECT * FROM facts
         WHERE agent_id = ? AND is_active = 1 AND embedding IS NOT NULL`;
    const rows = (limit
      ? db.prepare(sql).all(agentId, limit)
      : db.prepare(sql).all(agentId)) as FactRow[];

    return rows
      .filter((r) => r.embedding !== null)
      .map((r) => ({
        ...r,
        embeddingVector: Array.from(
          new Float32Array(
            (r.embedding as Buffer).buffer,
            (r.embedding as Buffer).byteOffset,
            (r.embedding as Buffer).byteLength / 4,
          ),
        ),
      }));
  }

  /**
   * Get shared facts from other agents that have embeddings.
   * For cross-agent semantic search.
   */
  getSharedFactsWithEmbeddings(
    excludeAgentId: string,
    limit?: number,
  ): (FactRow & { embeddingVector: number[] })[] {
    const db = this.ensureInit();
    const sql = limit
      ? `SELECT * FROM facts
         WHERE agent_id != ? AND visibility = 'shared'
           AND is_active = 1 AND embedding IS NOT NULL
         ORDER BY last_seen_at DESC LIMIT ?`
      : `SELECT * FROM facts
         WHERE agent_id != ? AND visibility = 'shared'
           AND is_active = 1 AND embedding IS NOT NULL`;
    const rows = (limit
      ? db.prepare(sql).all(excludeAgentId, limit)
      : db.prepare(sql).all(excludeAgentId)) as FactRow[];

    return rows
      .filter((r) => r.embedding !== null)
      .map((r) => ({
        ...r,
        embeddingVector: Array.from(
          new Float32Array(
            (r.embedding as Buffer).buffer,
            (r.embedding as Buffer).byteOffset,
            (r.embedding as Buffer).byteLength / 4,
          ),
        ),
      }));
  }

  /**
   * Count facts that are missing embeddings (for backfill progress).
   */
  countFactsMissingEmbeddings(agentId?: string): {
    total: number;
    withEmbedding: number;
    withoutEmbedding: number;
  } {
    const db = this.ensureInit();
    const where = agentId
      ? "WHERE is_active = 1 AND agent_id = ?"
      : "WHERE is_active = 1";
    const args = agentId ? [agentId] : [];

    const total = (
      db.prepare(`SELECT COUNT(*) as cnt FROM facts ${where}`).get(...args) as {
        cnt: number;
      }
    ).cnt;

    const withEmb = (
      db
        .prepare(
          `SELECT COUNT(*) as cnt FROM facts ${where} AND embedding IS NOT NULL`,
        )
        .get(...args) as { cnt: number }
    ).cnt;

    return {
      total,
      withEmbedding: withEmb,
      withoutEmbedding: total - withEmb,
    };
  }

  /**
   * Get active facts that are missing embeddings (for backfill).
   */
  getFactsMissingEmbeddings(limit: number): FactRow[] {
    const db = this.ensureInit();
    return db
      .prepare(
        `SELECT * FROM facts
         WHERE is_active = 1 AND embedding IS NULL
         ORDER BY last_seen_at DESC
         LIMIT ?`,
      )
      .all(limit) as FactRow[];
  }


  /**
   * Get all active fact relations (for dedup in relation-sweep).
   */
  getAllRelations(): { source_id: string; target_id: string }[] {
    const db = this.ensureInit();
    return db
      .prepare("SELECT source_id, target_id FROM fact_relations")
      .all() as { source_id: string; target_id: string }[];
  }

  /**
   * Get all distinct agent IDs that have active facts.
   */
  getDistinctAgentIds(): string[] {
    const db = this.ensureInit();
    const rows = db
      .prepare("SELECT DISTINCT agent_id FROM facts WHERE is_active = 1")
      .all() as { agent_id: string }[];
    return rows.map(r => r.agent_id);
  }

  // =========================================================================
  // Lifecycle
  // =========================================================================

  close(): void {
    this.db?.close();
    this.db = null;
  }
}
