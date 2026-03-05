/**
 * OpenClaw Memory System v1
 * Storage Layer - SQLite + Vector Search
 * 
 * Local-first, Ollama-compatible memory system
 * Forked from Engram patterns, optimized for OpenClaw
 */

import Database from 'better-sqlite3';
import { v4 as uuidv4 } from 'uuid';
import path from 'path';

// Types
export type MemoryType = 'episodic' | 'semantic' | 'procedural';

// ============================================================================
// PHASE 1.4 RETRIEVAL FEATURES - IMPORTS
// ============================================================================

import { hybridSearch } from '../retrieval/hybrid.js';
import { filterMemories, scoreForQuestionType } from '../retrieval/filter.js';
import { normalizeEntities, createAliasStore, type EntityAliasStore } from '../extractors/normalize.js';

// Alias store for spelling variants and entity aliases
let aliasStore: EntityAliasStore | null = null;

function getAliasStore(): EntityAliasStore {
  if (!aliasStore) {
    aliasStore = createAliasStore();
  }
  return aliasStore;
}

// ============================================================================
// ENTITY EXTRACTION (simple version for storage)
// ============================================================================

function extractEntitiesFromText(text: string): string[] {
  const entities: string[] = [];
  const patterns = [
    'Phillip', 'KakāpōHiko', 'Kakāpō', 'Hiko',
    'Elev8Advisory', 'BrandForge', 'Muninn', 'OpenClaw',
    'Sammy Clemens', 'Charlie Babbage', 'Donna Paulsen',
    'Brisbane', 'Australia', 'React', 'Node.js', 'PostgreSQL',
    'SQLite', 'Ollama', 'Stripe'
  ];
  
  for (const p of patterns) {
    if (text.toLowerCase().includes(p.toLowerCase())) {
      entities.push(p);
    }
  }
  
  return [...new Set(entities)];
}

// ============================================================================
// QUERY EXPANSION FOR SPELLING VARIANTS
// ============================================================================

/**
 * Expand query with spelling variants (UK↔US English)
 */
function expandQueryWithVariants(query: string): string[] {
  const expandedQueries: string[] = [query];
  
  // Common spelling variants to check
  const variantPairs = [
    ['colour', 'color'],
    ['flavour', 'flavor'],
    ['honour', 'honor'],
    ['organise', 'organize'],
    ['realise', 'realize'],
    ['recognise', 'recognize'],
    ['analyse', 'analyze'],
    ['centre', 'center'],
    ['theatre', 'theater'],
    ['defence', 'defense'],
    ['offence', 'offense'],
    ['licence', 'license'],
    ['programme', 'program'],
    ['behaviour', 'behavior'],
  ];
  
  for (const [uk, us] of variantPairs) {
    // If query contains UK form, add US version
    if (query.toLowerCase().includes(uk)) {
      expandedQueries.push(query.replace(new RegExp(uk, 'gi'), us));
    }
    // If query contains US form, add UK version  
    if (query.toLowerCase().includes(us)) {
      expandedQueries.push(query.replace(new RegExp(us, 'gi'), uk));
    }
  }
  
  return [...new Set(expandedQueries)];
}

export interface Memory {
  id: string;
  type: MemoryType;
  content: string;
  title?: string;
  summary?: string;
  entities: string[];
  topics: string[];
  embedding: number[];
  salience: number;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}

export interface Procedure {
  id: string;
  title: string;
  description?: string;
  steps: ProcedureStep[];
  version: number;
  success_count: number;
  failure_count: number;
  is_reliable: boolean;
  evolution_log: EvolutionEvent[];
  created_at: string;
  updated_at: string;
}

export interface ProcedureStep {
  id: string;
  order: number;
  description: string;
  expected_outcome?: string;
}

export interface EvolutionEvent {
  version: number;
  trigger: 'failure' | 'success_pattern' | 'manual';
  change: string;
  timestamp: string;
}

export interface Entity {
  name: string;
  memory_count: number;
  last_seen: string;
}

export interface MemoryEdge {
  id: string;
  source_id: string;
  target_id: string;
  relationship: string;
  created_at: string;
}

export interface VaultStats {
  total: number;
  byType: Record<MemoryType, number>;
  entities: number;
  edges: number;
  procedures: number;
}

// Embedding function using Ollama
export async function generateEmbedding(text: string): Promise<number[]> {
  const response = await fetch('http://localhost:11434/api/embeddings', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'nomic-embed-text',
      prompt: text
    })
  });
  
  if (!response.ok) {
    throw new Error(`Ollama embedding failed: ${response.statusText}`);
  }
  
  const data = await response.json() as { embedding: number[] };
  return data.embedding;
}

// Cosine similarity
function cosineSimilarity(a: number[], b: number[]): number {
  if (a.length !== b.length) return 0;
  
  let dotProduct = 0;
  let normA = 0;
  let normB = 0;
  
  for (let i = 0; i < a.length; i++) {
    dotProduct += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  
  return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

export class MemoryStore {
  private db: Database.Database;
  
  constructor(dbPath?: string) {
    const defaultPath = path.join(process.cwd(), 'openclaw-memory.db');
    this.db = new Database(dbPath || defaultPath);
    this.init();
  }
  
  private init(): void {
    // Enable vector similarity search using simple implementation
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS memories (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL CHECK(type IN ('episodic', 'semantic', 'procedural')),
        content TEXT NOT NULL,
        title TEXT,
        summary TEXT,
        entities TEXT DEFAULT '[]',
        topics TEXT DEFAULT '[]',
        embedding BLOB,
        salience REAL DEFAULT 0.5,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')),
        deleted_at TEXT
      );
      
      CREATE TABLE IF NOT EXISTS entities (
        name TEXT PRIMARY KEY,
        memory_count INTEGER DEFAULT 0,
        last_seen TEXT DEFAULT (datetime('now'))
      );
      
      CREATE TABLE IF NOT EXISTS edges (
        id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        target_id TEXT NOT NULL,
        relationship TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (source_id) REFERENCES memories(id) ON DELETE CASCADE,
        FOREIGN KEY (target_id) REFERENCES memories(id) ON DELETE CASCADE
      );
      
      CREATE TABLE IF NOT EXISTS procedures (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        steps TEXT DEFAULT '[]',
        version INTEGER DEFAULT 1,
        success_count INTEGER DEFAULT 0,
        failure_count INTEGER DEFAULT 0,
        is_reliable INTEGER DEFAULT 0,
        evolution_log TEXT DEFAULT '[]',
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
      );
      
      CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type);
      CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at);
      CREATE INDEX IF NOT EXISTS idx_memories_deleted ON memories(deleted_at);
      CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
      CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);
      CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
    `);
    
    console.log('📦 Memory database initialized');
  }
  
  // Memory CRUD
  async remember(
    content: string,
    type: MemoryType = 'semantic',
    options: {
      title?: string;
      summary?: string;
      entities?: string[];
      topics?: string[];
      salience?: number;
    } = {}
  ): Promise<Memory> {
    const id = `m_${uuidv4().slice(0, 8)}`;
    const embedding = await generateEmbedding(content);
    const now = new Date().toISOString();
    
    // ========================================================================
    // PHASE 1.4: ENTITY NORMALIZATION
    // ========================================================================
    
    // Extract entities if not provided
    const extractedEntities = options.entities || extractEntitiesFromText(content);
    
    // Create properly typed entities for normalization
    const entitiesForNormalization = extractedEntities.map(e => ({
      text: e,
      type: 'concept' as const,
      confidence: 0.8,
      context: '',
    }));
    
    // Normalize entities and store aliases
    const normalized = await normalizeEntities(content, entitiesForNormalization);
    
    // Store aliases for retrieval
    const aliasStore = getAliasStore();
    for (const norm of normalized) {
      for (const alias of norm.aliases) {
        aliasStore.addAlias(norm.canonical, alias);
      }
    }
    
    // Get canonical entity names
    const canonicalEntities = [...new Set(normalized.map(n => n.canonical))];
    
    // Convert embedding to base64 for storage
    const embeddingBuffer = Buffer.from(new Float32Array(embedding).buffer);
    
    const stmt = this.db.prepare(`
      INSERT INTO memories (id, type, content, title, summary, entities, topics, embedding, salience, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    
    stmt.run(
      id,
      type,
      content,
      options.title || null,
      options.summary || null,
      JSON.stringify(canonicalEntities),
      JSON.stringify(options.topics || []),
      embeddingBuffer,
      options.salience || 0.5,
      now,
      now
    );
    
    // Update entity counts (use canonical names)
    if (canonicalEntities.length) {
      const entityStmt = this.db.prepare(`
        INSERT INTO entities (name, memory_count, last_seen)
        VALUES (?, 1, ?)
        ON CONFLICT(name) DO UPDATE SET
          memory_count = memory_count + 1,
          last_seen = ?
      `);
      
      for (const entity of canonicalEntities) {
        entityStmt.run(entity, now, now);
      }
    }
    
    return this.getMemory(id)!;
  }
  
  getMemory(id: string): Memory | null {
    const stmt = this.db.prepare('SELECT * FROM memories WHERE id = ? AND deleted_at IS NULL');
    const row = stmt.get(id) as any;
    
    if (!row) return null;
    
    return {
      ...row,
      entities: JSON.parse(row.entities || '[]'),
      topics: JSON.parse(row.topics || '[]'),
      embedding: Array.from(new Float32Array(row.embedding?.buffer || new ArrayBuffer(0)))
    };
  }
  
  async recall(
    context: string,
    options: {
      types?: MemoryType[];
      entities?: string[];
      topics?: string[];
      limit?: number;
    } = {}
  ): Promise<Memory[]> {
    const limit = options.limit || 10;
    
    // Get all non-deleted memories
    let memories = this.db.prepare(`
      SELECT * FROM memories WHERE deleted_at IS NULL
    `).all() as any[];
    
    // Parse stored fields
    memories = memories.map(row => ({
      ...row,
      entities: JSON.parse(row.entities || '[]'),
      topics: JSON.parse(row.topics || '[]'),
      embedding: Array.from(new Float32Array(row.embedding?.buffer || new ArrayBuffer(0)))
    }));
    
    // Filter by type
    if (options.types?.length) {
      memories = memories.filter(m => options.types!.includes(m.type));
    }
    
    // Filter by entities
    if (options.entities?.length) {
      memories = memories.filter(m => 
        options.entities!.some(e => m.entities.includes(e))
      );
    }
    
    // If too few memories, fall back to simple similarity
    if (memories.length < 3) {
      return this.simpleRecall(context, limit);
    }
    
    // ========================================================================
    // PHASE 1.4: HYBRID RETRIEVAL + TYPE-AWARE FILTERING
    // ========================================================================
    
    try {
      // Detect factual questions that should prioritize semantic memories
      // Expanded keyword list for better detection
      const isFactualQuery = /^(what|who|which|when|where|how (does|do|is|did|can|was|were)|why|whose)/i.test(context) ||
        /name|called|mean|stand for|relationship|port|model|database|stack|agents?|team|projects?|revenue|target|priority|embedding|spelling/i.test(context);
      
      // For factual questions, prioritize semantic memories first
      if (isFactualQuery && !options.types) {
        const semanticOnly = memories.filter(m => m.type === 'semantic' && (m.salience || 0.5) >= 0.5);
        if (semanticOnly.length > 0) {
          const semanticResults = await this.recallInternal(context, semanticOnly, limit);
          // If we got good results from semantic, return them
          if (semanticResults.length > 0) {
            return semanticResults;
          }
        }
        // Fallback: if semantic returned nothing, try all memories with hybrid
        // Don't return empty - try the full set
      }
      
      return this.recallInternal(context, memories, limit);
    } catch (error) {
      console.warn('Hybrid retrieval failed, using fallback:', error);
      return this.simpleRecall(context, limit);
    }
  }
  
  /**
   * Internal recall with hybrid search
   */
  private async recallInternal(context: string, memories: Memory[], limit: number): Promise<Memory[]> {
    try {
      // 1. Expand query with spelling variants (UK↔US)
      const expandedQueries = expandQueryWithVariants(context);
      
      // 2. Extract entities from query for boosting
      const queryEntities = extractEntitiesFromText(context);
      
      // 3. Run hybrid search with BM25 + semantic
      let candidates = await hybridSearch(context, memories, { 
        k: limit * 3,
        enableLLMFilter: false
      });
      
      // 4. Also search with expanded queries and merge results
      for (const expandedQuery of expandedQueries.slice(1)) {
        const expandedResults = await hybridSearch(expandedQuery, memories, { 
          k: limit * 2,
          enableLLMFilter: false
        });
        
        // Merge unique results
        const existingIds = new Set(candidates.map(m => m.id));
        for (const m of expandedResults) {
          if (!existingIds.has(m.id)) {
            candidates.push(m);
          }
        }
      }
      
      // 5. Boost by entity overlap
      if (queryEntities.length > 0) {
        for (const c of candidates) {
          const memoryEntities = c.entities || [];
          const overlap = memoryEntities.filter((e: string) => 
            queryEntities.some((qe: string) => e.toLowerCase() === qe.toLowerCase())
          );
          if (overlap.length > 0) {
            (c as any)._entityBoost = 1 + (overlap.length * 0.5); // 50% boost per matching entity
          }
        }
      }
      
      // 6. Re-sort with entity boost
      candidates.sort((a, b) => {
        const scoreA = (a as any)._finalScore || (a as any)._rrfScore || 0;
        const scoreB = (b as any)._finalScore || (b as any)._rrfScore || 0;
        const boostA = (a as any)._entityBoost || 1;
        const boostB = (b as any)._entityBoost || 1;
        return (scoreB * boostB) - (scoreA * boostA);
      });
      
      // 7. Apply question-type specific scoring (temporal/contradiction handling)
      const scored = scoreForQuestionType(candidates.slice(0, limit), context);
      
      return scored;
    } catch (error) {
      console.warn('Recall internal failed:', error);
      return [];
    }
  }
  
  /**
   * Simple semantic recall fallback
   */
  private async simpleRecall(context: string, limit: number): Promise<Memory[]> {
    const queryEmbedding = await generateEmbedding(context);
    
    let memories = this.db.prepare(`
      SELECT * FROM memories WHERE deleted_at IS NULL
    `).all() as any[];
    
    memories = memories.map(row => ({
      ...row,
      entities: JSON.parse(row.entities || '[]'),
      topics: JSON.parse(row.topics || '[]'),
      embedding: Array.from(new Float32Array(row.embedding?.buffer || new ArrayBuffer(0)))
    }));
    
    const scored = memories.map(m => ({
      ...m,
      _similarity: m.embedding.length > 0 ? cosineSimilarity(queryEmbedding, m.embedding) : 0
    }));
    
    scored.sort((a, b) => b._similarity - a._similarity);
    
    return scored.slice(0, limit).map(({ _similarity, ...m }) => m as Memory);
  }
  
  forget(id: string, hard: boolean = false): boolean {
    if (hard) {
      const stmt = this.db.prepare('DELETE FROM memories WHERE id = ?');
      return stmt.run(id).changes > 0;
    } else {
      const stmt = this.db.prepare("UPDATE memories SET deleted_at = datetime('now') WHERE id = ?");
      return stmt.run(id).changes > 0;
    }
  }
  
  // Entity management
  getEntities(): Entity[] {
    return this.db.prepare('SELECT * FROM entities ORDER BY memory_count DESC').all() as Entity[];
  }
  
  // Graph edges
  connect(sourceId: string, targetId: string, relationship: string): MemoryEdge {
    const id = `e_${uuidv4().slice(0, 8)}`;
    const now = new Date().toISOString();
    
    const stmt = this.db.prepare(`
      INSERT INTO edges (id, source_id, target_id, relationship, created_at)
      VALUES (?, ?, ?, ?, ?)
    `);
    
    stmt.run(id, sourceId, targetId, relationship, now);
    
    return { id, source_id: sourceId, target_id: targetId, relationship, created_at: now };
  }
  
  getNeighbors(memoryId: string, depth: number = 1): Memory[] {
    const neighbors: Set<string> = new Set([memoryId]);
    const result: Memory[] = [];
    
    for (let i = 0; i < depth; i++) {
      const ids = Array.from(neighbors);
      if (ids.length === 0) break;
      
      const rows = this.db.prepare(`
        SELECT DISTINCT target_id FROM edges WHERE source_id IN (${ids.map(() => '?').join(',')})
      `).all(...ids) as { target_id: string }[];
      
      for (const row of rows) {
        if (!neighbors.has(row.target_id)) {
          neighbors.add(row.target_id);
        }
      }
    }
    
    const memStmt = this.db.prepare(`SELECT * FROM memories WHERE id IN (${Array.from(neighbors).map(() => '?').join(',')})`);
    const rows = memStmt.all(...Array.from(neighbors)) as any[];
    
    return rows.map(row => ({
      ...row,
      entities: JSON.parse(row.entities || '[]'),
      topics: JSON.parse(row.topics || '[]'),
      embedding: Array.from(new Float32Array(row.embedding?.buffer || new ArrayBuffer(0)))
    }));
  }
  
  // Stats
  getStats(): VaultStats {
    const total = (this.db.prepare('SELECT COUNT(*) as count FROM memories WHERE deleted_at IS NULL').get() as any).count;
    
    const byType: Record<MemoryType, number> = {
      episodic: (this.db.prepare("SELECT COUNT(*) as count FROM memories WHERE type = 'episodic' AND deleted_at IS NULL").get() as any).count,
      semantic: (this.db.prepare("SELECT COUNT(*) as count FROM memories WHERE type = 'semantic' AND deleted_at IS NULL").get() as any).count,
      procedural: (this.db.prepare("SELECT COUNT(*) as count FROM memories WHERE type = 'procedural' AND deleted_at IS NULL").get() as any).count
    };
    
    const entities = (this.db.prepare('SELECT COUNT(*) as count FROM entities').get() as any).count;
    const edges = (this.db.prepare('SELECT COUNT(*) as count FROM edges').get() as any).count;
    const procedures = (this.db.prepare('SELECT COUNT(*) as count FROM procedures').get() as any).count;
    
    return { total, byType, entities, edges, procedures };
  }
  
  // Procedure management
  async createProcedure(
    title: string,
    steps: string[],
    description?: string
  ): Promise<Procedure> {
    const id = `proc_${uuidv4().slice(0, 8)}`;
    const now = new Date().toISOString();
    
    const procedureSteps: ProcedureStep[] = steps.map((desc, i) => ({
      id: `step_${uuidv4().slice(0, 8)}`,
      order: i + 1,
      description: desc
    }));
    
    const stmt = this.db.prepare(`
      INSERT INTO procedures (id, title, description, steps, version, success_count, failure_count, is_reliable, evolution_log, created_at, updated_at)
      VALUES (?, ?, ?, ?, 1, 0, 0, 0, '[]', ?, ?)
    `);
    
    stmt.run(id, title, description || null, JSON.stringify(procedureSteps), now, now);
    
    return this.getProcedure(id)!;
  }
  
  getProcedure(id: string): Procedure | null {
    const stmt = this.db.prepare('SELECT * FROM procedures WHERE id = ?');
    const row = stmt.get(id) as any;
    
    if (!row) return null;
    
    return {
      ...row,
      steps: JSON.parse(row.steps || '[]'),
      evolution_log: JSON.parse(row.evolution_log || '[]'),
      is_reliable: Boolean(row.is_reliable)
    };
  }
  
  getAllProcedures(): Procedure[] {
    const rows = this.db.prepare('SELECT * FROM procedures ORDER BY updated_at DESC').all() as any[];
    
    return rows.map(row => ({
      ...row,
      steps: JSON.parse(row.steps || '[]'),
      evolution_log: JSON.parse(row.evolution_log || '[]'),
      is_reliable: Boolean(row.is_reliable)
    }));
  }
  
  async procedureFeedback(
    procedureId: string,
    success: boolean,
    failedAtStep?: number,
    context?: string
  ): Promise<Procedure> {
    const proc = this.getProcedure(procedureId);
    if (!proc) throw new Error('Procedure not found');
    
    const now = new Date().toISOString();
    const newVersion = proc.version + 1;
    
    if (success) {
      const newCount = proc.success_count + 1;
      const isReliable = newCount >= 3 && !proc.is_reliable;
      
      const evolutionEvent: EvolutionEvent = {
        version: newVersion,
        trigger: 'success_pattern',
        change: `Success count: ${newCount}. ${isReliable ? 'Promoted to reliable workflow.' : ''}`,
        timestamp: now
      };
      
      this.db.prepare(`
        UPDATE procedures SET 
          success_count = ?,
          is_reliable = ?,
          evolution_log = ?,
          updated_at = ?
        WHERE id = ?
      `).run(newCount, isReliable ? 1 : 0, JSON.stringify([...proc.evolution_log, evolutionEvent]), now, procedureId);
    } else {
      // On failure, create new version with modified step if provided
      let newSteps = proc.steps;
      if (failedAtStep) {
        newSteps = proc.steps.map((step, i) => {
          if (i + 1 === failedAtStep) {
            return {
              ...step,
              description: `${step.description} [RETRY: add error handling]`
            };
          }
          return step;
        });
      }
      
      const evolutionEvent: EvolutionEvent = {
        version: newVersion,
        trigger: 'failure',
        change: `Failed at step ${failedAtStep || 'unknown'}. ${context || ''} New version created.`,
        timestamp: now
      };
      
      this.db.prepare(`
        UPDATE procedures SET 
          version = ?,
          failure_count = failure_count + 1,
          steps = ?,
          evolution_log = ?,
          updated_at = ?
        WHERE id = ?
      `).run(newVersion, JSON.stringify(newSteps), JSON.stringify([...proc.evolution_log, evolutionEvent]), now, procedureId);
    }
    
    return this.getProcedure(procedureId)!;
  }
  
  close(): void {
    this.db.close();
  }
}

// Default export
export default MemoryStore;
