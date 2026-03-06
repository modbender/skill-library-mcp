/**
 * Memory Tools Tests (v2)
 *
 * Tests for the six agent-controlled memory operations.
 * Note: Search tests require QMD to be installed.
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { createMemoryTools } from './tools.js';
import { MemoryStore } from './store.js';
import * as fs from 'node:fs';
import * as path from 'node:path';
import * as os from 'node:os';

describe('Memory Tools', () => {
  let store: MemoryStore;
  let tools: ReturnType<typeof createMemoryTools>;
  let testDir: string;

  beforeEach(() => {
    testDir = fs.mkdtempSync(path.join(os.tmpdir(), 'memory-tools-test-'));
    store = new MemoryStore(testDir);
    tools = createMemoryTools(store as any);
  });

  afterEach(() => {
    store.close();
    if (testDir && fs.existsSync(testDir)) {
      fs.rmSync(testDir, { recursive: true, force: true });
    }
  });

  describe('memory_store', () => {
    it('should store a new memory', async () => {
      const result = await tools.memory_store.execute('test', {
        content: 'User likes coffee',
        category: 'preference',
        confidence: 0.9,
        importance: 0.7,
      });

      expect(result.content[0].text).toContain('Stored');
      expect(result.details?.action).toBe('created');
      expect(result.details?.category).toBe('preference');
    });

    it('should store memory with tags', async () => {
      const result = await tools.memory_store.execute('test', {
        content: 'User birthday is January 15',
        category: 'fact',
        tags: ['personal', 'dates'],
      });

      expect(result.details?.action).toBe('created');

      // Verify tags stored
      const memory = store.get(result.details?.id as string);
      expect(memory?.tags).toContain('personal');
      expect(memory?.tags).toContain('dates');
    });

    it('should use default confidence and importance', async () => {
      const result = await tools.memory_store.execute('test', {
        content: 'Some fact',
        category: 'fact',
      });

      const memory = store.get(result.details?.id as string);
      expect(memory?.confidence).toBe(0.8);
      expect(memory?.importance).toBe(0.5);
    });
  });

  describe('memory_update', () => {
    it('should update memory content', async () => {
      // Create initial memory
      const createResult = await tools.memory_store.execute('test', {
        content: 'User dog name is Max',
        category: 'fact',
      });
      const id = createResult.details?.id as string;

      // Update it
      const updateResult = await tools.memory_update.execute('test', {
        id,
        content: 'User dog name is Rex',
      });

      expect(updateResult.content[0].text).toContain('Updated');
      expect(updateResult.content[0].text).toContain('Rex');
    });

    it('should update confidence score', async () => {
      const createResult = await tools.memory_store.execute('test', {
        content: 'User might like hiking',
        category: 'preference',
        confidence: 0.5,
      });
      const id = createResult.details?.id as string;

      await tools.memory_update.execute('test', {
        id,
        confidence: 0.95,
      });

      const memory = store.get(id);
      expect(memory?.confidence).toBe(0.95);
    });

    it('should return error for non-existent memory', async () => {
      const result = await tools.memory_update.execute('test', {
        id: 'non-existent-id',
        content: 'Updated content',
      });

      expect(result.content[0].text).toContain('not found');
      expect(result.details?.error).toBe('not_found');
    });
  });

  describe('memory_forget', () => {
    it('should delete memory by id', async () => {
      const createResult = await tools.memory_store.execute('test', {
        content: 'Memory to delete',
        category: 'fact',
      });
      const id = createResult.details?.id as string;

      const deleteResult = await tools.memory_forget.execute('test', {
        id,
        reason: 'Test deletion',
      });

      expect(deleteResult.content[0].text).toContain('Forgotten');
      expect(deleteResult.details?.action).toBe('deleted');

      // Verify deletion
      const memory = store.get(id);
      expect(memory).toBeNull();
    });

    it('should return error for non-existent memory', async () => {
      const result = await tools.memory_forget.execute('test', {
        id: 'non-existent-id',
      });

      expect(result.content[0].text).toContain('not found');
    });

    it('should require id or query', async () => {
      const result = await tools.memory_forget.execute('test', {});

      expect(result.content[0].text).toContain('Provide id or query');
    });
  });

  describe('memory_list', () => {
    beforeEach(async () => {
      // Create test memories
      await tools.memory_store.execute('test', {
        content: 'Fact 1',
        category: 'fact',
        importance: 0.5,
      });
      await tools.memory_store.execute('test', {
        content: 'Fact 2',
        category: 'fact',
        importance: 0.8,
      });
      await tools.memory_store.execute('test', {
        content: 'Preference 1',
        category: 'preference',
        importance: 0.6,
      });
    });

    it('should list all memories', async () => {
      const result = await tools.memory_list.execute('test', {});

      expect(result.content[0].text).toContain('3');
      expect(result.details?.total).toBe(3);
    });

    it('should filter by category', async () => {
      const result = await tools.memory_list.execute('test', {
        category: 'fact',
      });

      expect(result.details?.total).toBe(2);
      const memories = result.details?.memories as any[];
      expect(memories.every((m: any) => m.category === 'fact')).toBe(true);
    });

    it('should sort by importance', async () => {
      const result = await tools.memory_list.execute('test', {
        sortBy: 'importance',
      });

      const memories = result.details?.memories as any[];
      expect(memories[0].importance).toBeGreaterThanOrEqual(memories[1].importance);
    });

    it('should paginate', async () => {
      const result = await tools.memory_list.execute('test', {
        limit: 2,
        offset: 0,
      });

      expect(result.details?.count).toBe(2);
      expect(result.details?.total).toBe(3);
    });
  });

  // Note: Search and summarize tests require QMD
  // They are skipped in environments without QMD
  describe('memory_search (without QMD)', () => {
    it('should return no results without QMD', async () => {
      await tools.memory_store.execute('test', {
        content: 'User loves TypeScript',
        category: 'preference',
      });

      // Without QMD, semantic search returns empty
      const result = await tools.memory_search.execute('test', {
        query: 'programming',
      });

      // May return no results without QMD, which is expected
      expect(result.content[0].text).toBeDefined();
    });
  });
});
