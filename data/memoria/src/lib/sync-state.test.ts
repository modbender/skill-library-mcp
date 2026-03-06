import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { readSyncState, writeSyncState, getEntry, setEntry, removeEntry } from './sync-state.js';

describe('sync-state', () => {
  let dir: string;

  beforeEach(async () => {
    dir = await mkdtemp(join(tmpdir(), 'memoria-sync-'));
  });

  afterEach(async () => {
    await rm(dir, { recursive: true, force: true });
  });

  it('returns empty state when file does not exist', async () => {
    const state = await readSyncState(dir);
    expect(state.lastSyncAt).toBe('');
    expect(state.databases).toEqual({});
    expect(state.entries).toEqual({});
  });

  it('writes and reads sync state', async () => {
    const state = {
      lastSyncAt: '2026-01-01T00:00:00Z',
      databases: { decisions: 'db-123' },
      entries: {},
    };

    await writeSyncState(dir, state);
    const read = await readSyncState(dir);
    expect(read.lastSyncAt).toBe('2026-01-01T00:00:00Z');
    expect(read.databases.decisions).toBe('db-123');
  });

  it('manages entries', () => {
    const state = { lastSyncAt: '', databases: {}, entries: {} };

    setEntry(state, 'decisions/foo.md', {
      localPath: 'decisions/foo.md',
      notionPageId: 'page-1',
      lastSyncedAt: '2026-01-01',
      localUpdatedAt: '2026-01-01',
      notionUpdatedAt: '2026-01-01',
    });

    expect(getEntry(state, 'decisions/foo.md')?.notionPageId).toBe('page-1');

    removeEntry(state, 'decisions/foo.md');
    expect(getEntry(state, 'decisions/foo.md')).toBeUndefined();
  });
});
