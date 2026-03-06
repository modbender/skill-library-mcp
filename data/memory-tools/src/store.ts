/**
 * Memory Store v2
 *
 * File-based storage with QMD search.
 * No SQLite, no LanceDB, no OpenAI.
 */

import type {
  Memory,
  MemorySearchResult,
  CreateMemoryInput,
  UpdateMemoryInput,
  SearchOptions,
  ListOptions,
  MemoryCategory,
} from './types.js';
import { MemoryFileManager } from './file-manager.js';
import { QMDClient } from './qmd.js';

export class MemoryStoreV2 {
  private fileManager: MemoryFileManager;
  private qmd: QMDClient;
  private memoriesPath: string;

  constructor(memoriesPath: string, qmdCollection: string = 'memories') {
    this.memoriesPath = memoriesPath;
    this.fileManager = new MemoryFileManager(memoriesPath);
    this.qmd = new QMDClient(memoriesPath, qmdCollection);
  }

  /**
   * Initialize the store and QMD collection
   */
  async init(): Promise<void> {
    await this.qmd.ensureCollection();
  }

  /**
   * Check if QMD is available
   */
  async isQMDAvailable(): Promise<boolean> {
    return this.qmd.isInstalled();
  }

  /**
   * Create a new memory
   */
  async create(input: CreateMemoryInput): Promise<Memory> {
    const memory = this.fileManager.create(input);

    // Schedule QMD index update
    this.qmd.scheduleUpdate();

    return memory;
  }

  /**
   * Get a memory by ID
   */
  get(id: string): Memory | null {
    return this.fileManager.get(id);
  }

  /**
   * Async version of get (for API compatibility)
   */
  async getAsync(id: string): Promise<Memory | null> {
    return this.fileManager.get(id);
  }

  /**
   * Update an existing memory
   */
  async update(id: string, updates: UpdateMemoryInput): Promise<Memory> {
    const updated = this.fileManager.update(id, updates);
    if (!updated) {
      throw new Error(`Memory ${id} not found`);
    }

    // Schedule QMD index update
    this.qmd.scheduleUpdate();

    return updated;
  }

  /**
   * Delete a memory (soft delete)
   */
  async delete(id: string, reason?: string): Promise<void> {
    const success = this.fileManager.delete(id, reason);
    if (!success) {
      throw new Error(`Memory ${id} not found`);
    }

    // Schedule QMD index update
    this.qmd.scheduleUpdate();
  }

  /**
   * Search memories using QMD
   */
  async search(opts: SearchOptions): Promise<MemorySearchResult[]> {
    const limit = opts.limit ?? 10;
    let results: MemorySearchResult[] = [];

    // If we have a query, use QMD semantic search
    if (opts.query) {
      const qmdResults = await this.qmd.query(opts.query, limit * 2); // Over-fetch for filtering

      if (qmdResults.length === 0) {
        return this.fallbackQuerySearch(opts.query, opts, limit);
      }

      for (const qr of qmdResults) {
        const memoryId = this.qmd.extractMemoryId(qr);
        if (!memoryId) continue;

        const memory = this.fileManager.get(memoryId);
        if (!memory || memory.deletedAt) continue;

        // Apply filters
        if (opts.category && memory.category !== opts.category) continue;
        if (opts.minConfidence !== undefined && memory.confidence < opts.minConfidence) continue;
        if (opts.minImportance !== undefined && memory.importance < opts.minImportance) continue;

        if (opts.tags?.length) {
          const hasAllTags = opts.tags.every(tag => memory.tags.includes(tag));
          if (!hasAllTags) continue;
        }

        // Check decay
        if (opts.excludeDecayed !== false && memory.decayDays) {
          const expiresAt = memory.createdAt + (memory.decayDays * 86400000);
          if (Date.now() > expiresAt) continue;
        }

        results.push({ memory, score: qr.score });
      }
    } else {
      // No query - just list with filters
      const listed = this.fileManager.list({
        category: opts.category,
        limit: limit,
      });

      results = listed.items
        .filter(memory => {
          if (opts.minConfidence !== undefined && memory.confidence < opts.minConfidence) return false;
          if (opts.minImportance !== undefined && memory.importance < opts.minImportance) return false;

          if (opts.tags?.length) {
            const hasAllTags = opts.tags.every(tag => memory.tags.includes(tag));
            if (!hasAllTags) return false;
          }

          if (opts.excludeDecayed !== false && memory.decayDays) {
            const expiresAt = memory.createdAt + (memory.decayDays * 86400000);
            if (Date.now() > expiresAt) return false;
          }

          return true;
        })
        .map(memory => ({ memory, score: 1.0 }));
    }

    return results.slice(0, limit);
  }

  private fallbackQuerySearch(
    query: string,
    opts: SearchOptions,
    limit: number
  ): MemorySearchResult[] {
    const all = this.fileManager.list({ category: opts.category, limit: 10000 }).items;
    const queryText = query.toLowerCase().trim();
    const queryTokens = queryText.split(/\s+/).filter(t => t.length > 1);

    const scored = all
      .filter(memory => {
        if (memory.deletedAt) return false;
        if (opts.minConfidence !== undefined && memory.confidence < opts.minConfidence) return false;
        if (opts.minImportance !== undefined && memory.importance < opts.minImportance) return false;

        if (opts.tags?.length) {
          const hasAllTags = opts.tags.every(tag => memory.tags.includes(tag));
          if (!hasAllTags) return false;
        }

        if (opts.excludeDecayed !== false && memory.decayDays) {
          const expiresAt = memory.createdAt + (memory.decayDays * 86400000);
          if (Date.now() > expiresAt) return false;
        }

        return true;
      })
      .map(memory => {
        const haystack = `${memory.content} ${memory.tags.join(' ')}`.toLowerCase();
        let score = 0;

        if (haystack.includes(queryText)) {
          score += 0.8;
        }

        if (queryTokens.length > 0) {
          let tokenHits = 0;
          for (const token of queryTokens) {
            if (haystack.includes(token)) tokenHits++;
          }
          score += (tokenHits / queryTokens.length) * 0.2;
        }

        return { memory, score };
      })
      .filter(r => r.score > 0)
      .sort((a, b) => b.score - a.score);

    return scored.slice(0, limit);
  }

  /**
   * Find potential duplicates using semantic similarity
   */
  async findDuplicates(content: string, threshold: number = 0.95): Promise<MemorySearchResult[]> {
    const qmdResults = await this.qmd.findSimilar(content, threshold);

    const results: MemorySearchResult[] = [];
    for (const qr of qmdResults) {
      const memoryId = this.qmd.extractMemoryId(qr);
      if (!memoryId) continue;

      const memory = this.fileManager.get(memoryId);
      if (!memory || memory.deletedAt) continue;

      results.push({ memory, score: qr.score });
    }

    return results;
  }

  /**
   * List memories with pagination
   */
  list(opts: ListOptions = {}): { total: number; items: Memory[] } {
    return this.fileManager.list(opts);
  }

  /**
   * Async version of list
   */
  async listAsync(opts: ListOptions = {}): Promise<{ total: number; items: Memory[] }> {
    return this.fileManager.list(opts);
  }

  /**
   * Get memories by category
   */
  getByCategory(category: MemoryCategory, limit: number = 50): Memory[] {
    return this.fileManager.getByCategory(category, limit);
  }

  /**
   * Async version of getByCategory
   */
  async getByCategoryAsync(category: MemoryCategory, limit: number = 50): Promise<Memory[]> {
    return this.fileManager.getByCategory(category, limit);
  }

  /**
   * Update last accessed time for multiple memories
   */
  touchMany(ids: string[]): void {
    this.fileManager.touchMany(ids);
  }

  /**
   * Async version of touchMany
   */
  async touchManyAsync(ids: string[]): Promise<void> {
    this.fileManager.touchMany(ids);
  }

  /**
   * Count non-deleted memories
   */
  count(): number {
    return this.fileManager.count();
  }

  /**
   * Async version of count
   */
  async countAsync(): Promise<number> {
    return this.fileManager.count();
  }

  /**
   * Get the memories directory path
   */
  getMemoriesPath(): string {
    return this.memoriesPath;
  }

  /**
   * Force QMD to re-index
   */
  async reindex(): Promise<void> {
    await this.qmd.forceUpdate();
  }

  /**
   * Close the store (cleanup)
   */
  close(): void {
    // Nothing to close - file-based storage
  }
}

// Export as MemoryStore for backwards compatibility
export { MemoryStoreV2 as MemoryStore };
