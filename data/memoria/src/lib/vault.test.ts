import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { initVault, storeDocument, getDocument, listDocuments, deleteDocument } from './vault.js';
import { configExists } from './config.js';

describe('vault', () => {
  let vaultPath: string;

  beforeEach(async () => {
    vaultPath = await mkdtemp(join(tmpdir(), 'memoria-test-'));
  });

  afterEach(async () => {
    await rm(vaultPath, { recursive: true, force: true });
  });

  describe('initVault', () => {
    it('creates vault with config and category dirs', async () => {
      const config = await initVault(vaultPath, 'test-vault');
      expect(config.name).toBe('test-vault');
      expect(config.path).toBe(vaultPath);
      expect(await configExists(vaultPath)).toBe(true);
    });
  });

  describe('storeDocument', () => {
    it('stores and retrieves a document', async () => {
      await initVault(vaultPath, 'test');
      const doc = await storeDocument(vaultPath, {
        category: 'decisions',
        title: 'Use TypeScript',
        content: 'Chosen for type safety.',
      });

      expect(doc.title).toBe('Use TypeScript');
      expect(doc.category).toBe('decisions');

      const retrieved = await getDocument(vaultPath, doc.path);
      expect(retrieved.title).toBe('Use TypeScript');
      expect(retrieved.content).toBe('Chosen for type safety.');
    });

    it('rejects duplicate without overwrite', async () => {
      await initVault(vaultPath, 'test');
      await storeDocument(vaultPath, {
        category: 'facts',
        title: 'Earth',
        content: 'A planet.',
      });

      await expect(
        storeDocument(vaultPath, {
          category: 'facts',
          title: 'Earth',
          content: 'Updated.',
        }),
      ).rejects.toThrow(/already exists/);
    });

    it('allows overwrite', async () => {
      await initVault(vaultPath, 'test');
      await storeDocument(vaultPath, {
        category: 'facts',
        title: 'Earth',
        content: 'A planet.',
      });

      const doc = await storeDocument(vaultPath, {
        category: 'facts',
        title: 'Earth',
        content: 'Updated planet info.',
        overwrite: true,
      });

      expect(doc.content).toBe('Updated planet info.');
    });
  });

  describe('listDocuments', () => {
    it('lists documents across categories', async () => {
      await initVault(vaultPath, 'test');
      await storeDocument(vaultPath, { category: 'facts', title: 'A', content: '' });
      await storeDocument(vaultPath, { category: 'decisions', title: 'B', content: '' });

      const docs = await listDocuments(vaultPath);
      expect(docs.length).toBe(2);
    });

    it('filters by category', async () => {
      await initVault(vaultPath, 'test');
      await storeDocument(vaultPath, { category: 'facts', title: 'A', content: '' });
      await storeDocument(vaultPath, { category: 'decisions', title: 'B', content: '' });

      const docs = await listDocuments(vaultPath, 'facts');
      expect(docs.length).toBe(1);
      expect(docs[0].category).toBe('facts');
    });
  });

  describe('deleteDocument', () => {
    it('deletes a document', async () => {
      await initVault(vaultPath, 'test');
      const doc = await storeDocument(vaultPath, { category: 'facts', title: 'Gone', content: '' });
      await deleteDocument(vaultPath, doc.path);

      const docs = await listDocuments(vaultPath, 'facts');
      expect(docs.length).toBe(0);
    });
  });
});
