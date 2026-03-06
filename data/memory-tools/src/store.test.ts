/**
 * Tests for Memory Store v2
 *
 * Tests file-based storage and migration from v1.
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import * as fs from 'node:fs';
import * as path from 'node:path';
import * as os from 'node:os';
import { MemoryFileManager } from './file-manager.js';
import { MemoryStore } from './store.js';
import {
  hasLegacyDatabase,
  hasNewMemories,
  migrateFromV1,
} from './migration.js';

// Helper to create temp directory
function createTempDir(): string {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'memory-tools-test-'));
}

// Helper to clean up temp directory
function cleanupTempDir(dir: string): void {
  if (fs.existsSync(dir)) {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

describe('MemoryFileManager', () => {
  let tempDir: string;
  let fileManager: MemoryFileManager;

  beforeEach(() => {
    tempDir = createTempDir();
    fileManager = new MemoryFileManager(tempDir);
  });

  afterEach(() => {
    cleanupTempDir(tempDir);
  });

  it('should create memory files with correct structure', () => {
    const memory = fileManager.create({
      content: 'User prefers dark mode',
      category: 'preference',
      confidence: 0.9,
      importance: 0.7,
      tags: ['ui', 'settings'],
    });

    expect(memory.id).toBeDefined();
    expect(memory.content).toBe('User prefers dark mode');
    expect(memory.category).toBe('preference');
    expect(memory.confidence).toBe(0.9);
    expect(memory.importance).toBe(0.7);
    expect(memory.tags).toEqual(['ui', 'settings']);

    // Check file exists
    const filePath = path.join(tempDir, 'preferences', `${memory.id}.md`);
    expect(fs.existsSync(filePath)).toBe(true);

    // Check file content
    const content = fs.readFileSync(filePath, 'utf-8');
    expect(content).toContain('---');
    expect(content).toContain('category: preference');
    expect(content).toContain('confidence: 0.9');
    expect(content).toContain('User prefers dark mode');
  });

  it('should read memory by ID', () => {
    const created = fileManager.create({
      content: 'Test memory content',
      category: 'fact',
    });

    const retrieved = fileManager.get(created.id);
    expect(retrieved).not.toBeNull();
    expect(retrieved!.id).toBe(created.id);
    expect(retrieved!.content).toBe('Test memory content');
    expect(retrieved!.category).toBe('fact');
  });

  it('should read memory by short ID (first 8 chars)', () => {
    const created = fileManager.create({
      content: 'Test memory',
      category: 'fact',
    });

    const shortId = created.id.slice(0, 8);
    const retrieved = fileManager.get(shortId);
    expect(retrieved).not.toBeNull();
    expect(retrieved!.id).toBe(created.id);
  });

  it('should update memory', async () => {
    const created = fileManager.create({
      content: 'Original content',
      category: 'fact',
      confidence: 0.5,
    });

    // Small delay to ensure timestamp difference
    await new Promise(resolve => setTimeout(resolve, 10));

    const updated = fileManager.update(created.id, {
      content: 'Updated content',
      confidence: 0.9,
    });

    expect(updated).not.toBeNull();
    expect(updated!.content).toBe('Updated content');
    expect(updated!.confidence).toBe(0.9);
    expect(updated!.updatedAt).toBeGreaterThanOrEqual(created.updatedAt);
  });

  it('should soft delete memory', () => {
    const created = fileManager.create({
      content: 'To be deleted',
      category: 'fact',
    });

    const success = fileManager.delete(created.id, 'Test deletion');
    expect(success).toBe(true);

    // Should not be retrievable
    const retrieved = fileManager.get(created.id);
    expect(retrieved).toBeNull();

    // Should exist in .deleted folder
    const deletedPath = path.join(tempDir, '.deleted', `${created.id}.md`);
    expect(fs.existsSync(deletedPath)).toBe(true);

    // Check deletion metadata
    const content = fs.readFileSync(deletedPath, 'utf-8');
    expect(content).toContain('delete_reason: Test deletion');
  });

  it('should list memories with pagination', () => {
    // Create 5 memories
    for (let i = 0; i < 5; i++) {
      fileManager.create({
        content: `Memory ${i}`,
        category: 'fact',
      });
    }

    const page1 = fileManager.list({ limit: 2, offset: 0 });
    expect(page1.total).toBe(5);
    expect(page1.items.length).toBe(2);

    const page2 = fileManager.list({ limit: 2, offset: 2 });
    expect(page2.total).toBe(5);
    expect(page2.items.length).toBe(2);

    const page3 = fileManager.list({ limit: 2, offset: 4 });
    expect(page3.total).toBe(5);
    expect(page3.items.length).toBe(1);
  });

  it('should filter by category', () => {
    fileManager.create({ content: 'Fact 1', category: 'fact' });
    fileManager.create({ content: 'Fact 2', category: 'fact' });
    fileManager.create({ content: 'Preference 1', category: 'preference' });

    const facts = fileManager.list({ category: 'fact' });
    expect(facts.total).toBe(2);
    expect(facts.items.every(m => m.category === 'fact')).toBe(true);

    const prefs = fileManager.list({ category: 'preference' });
    expect(prefs.total).toBe(1);
  });

  it('should count memories', () => {
    expect(fileManager.count()).toBe(0);

    fileManager.create({ content: 'Memory 1', category: 'fact' });
    fileManager.create({ content: 'Memory 2', category: 'preference' });

    expect(fileManager.count()).toBe(2);

    // Delete one
    const toDelete = fileManager.list().items[0];
    fileManager.delete(toDelete.id);

    expect(fileManager.count()).toBe(1);
  });

  it('should get memories by category sorted by importance', () => {
    fileManager.create({ content: 'Low importance', category: 'fact', importance: 0.3 });
    fileManager.create({ content: 'High importance', category: 'fact', importance: 0.9 });
    fileManager.create({ content: 'Medium importance', category: 'fact', importance: 0.6 });

    const facts = fileManager.getByCategory('fact');
    expect(facts.length).toBe(3);
    expect(facts[0].importance).toBe(0.9);
    expect(facts[1].importance).toBe(0.6);
    expect(facts[2].importance).toBe(0.3);
  });
});

describe('Migration', () => {
  let legacyDir: string;
  let newDir: string;

  beforeEach(() => {
    legacyDir = createTempDir();
    newDir = createTempDir();
  });

  afterEach(() => {
    cleanupTempDir(legacyDir);
    cleanupTempDir(newDir);
  });

  it('should detect legacy database', () => {
    expect(hasLegacyDatabase(legacyDir)).toBe(false);

    // Create fake legacy database
    fs.writeFileSync(path.join(legacyDir, 'memory.db'), 'fake db');
    expect(hasLegacyDatabase(legacyDir)).toBe(true);
  });

  it('should detect new memories directory', () => {
    expect(hasNewMemories(newDir)).toBe(false);

    // Create category directory with a memory file
    const factsDir = path.join(newDir, 'facts');
    fs.mkdirSync(factsDir, { recursive: true });
    fs.writeFileSync(path.join(factsDir, 'test.md'), 'test');

    expect(hasNewMemories(newDir)).toBe(true);
  });

  // Note: Full migration test requires a real SQLite database
  // This is tested in the integration tests with Docker
});

describe('MemoryStore', () => {
  let tempDir: string;
  let store: MemoryStore;

  beforeEach(() => {
    tempDir = createTempDir();
    store = new MemoryStore(tempDir);
  });

  afterEach(() => {
    store.close();
    cleanupTempDir(tempDir);
  });

  it('should create and retrieve memories', async () => {
    const memory = await store.create({
      content: 'Test memory',
      category: 'fact',
      confidence: 0.8,
    });

    expect(memory.id).toBeDefined();
    expect(memory.content).toBe('Test memory');

    const retrieved = await store.getAsync(memory.id);
    expect(retrieved).not.toBeNull();
    expect(retrieved!.content).toBe('Test memory');
  });

  it('should update memories', async () => {
    const memory = await store.create({
      content: 'Original',
      category: 'fact',
    });

    const updated = await store.update(memory.id, {
      content: 'Updated',
      confidence: 0.95,
    });

    expect(updated.content).toBe('Updated');
    expect(updated.confidence).toBe(0.95);
  });

  it('should delete memories', async () => {
    const memory = await store.create({
      content: 'To delete',
      category: 'fact',
    });

    await store.delete(memory.id, 'Test reason');

    const retrieved = await store.getAsync(memory.id);
    expect(retrieved).toBeNull();
  });

  it('should list memories', async () => {
    await store.create({ content: 'Memory 1', category: 'fact' });
    await store.create({ content: 'Memory 2', category: 'preference' });
    await store.create({ content: 'Memory 3', category: 'fact' });

    const all = await store.listAsync();
    expect(all.total).toBe(3);

    const factsOnly = await store.listAsync({ category: 'fact' });
    expect(factsOnly.total).toBe(2);
  });

  it('should count memories', async () => {
    expect(await store.countAsync()).toBe(0);

    await store.create({ content: 'Memory 1', category: 'fact' });
    await store.create({ content: 'Memory 2', category: 'fact' });

    expect(await store.countAsync()).toBe(2);
  });

  it('should get memories by category', async () => {
    await store.create({ content: 'Instruction 1', category: 'instruction', importance: 0.9 });
    await store.create({ content: 'Instruction 2', category: 'instruction', importance: 0.5 });
    await store.create({ content: 'Fact 1', category: 'fact' });

    const instructions = await store.getByCategoryAsync('instruction');
    expect(instructions.length).toBe(2);
    expect(instructions[0].importance).toBe(0.9); // Sorted by importance
  });

  // Note: Search tests require QMD to be installed
  // They are skipped if QMD is not available
  it.skip('should search memories with QMD', async () => {
    // This test requires QMD to be installed
    await store.init();

    await store.create({ content: 'User loves TypeScript programming', category: 'preference' });
    await store.create({ content: 'User has a meeting tomorrow', category: 'event' });

    // Wait for QMD index update
    await new Promise(resolve => setTimeout(resolve, 3000));

    const results = await store.search({ query: 'programming languages' });
    expect(results.length).toBeGreaterThan(0);
    expect(results[0].memory.content).toContain('TypeScript');
  });
});
