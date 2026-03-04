import { readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import type { SyncState, SyncStateEntry } from '../types.js';

const SYNC_STATE_FILE = '.sync-state.json';

function syncStatePath(vaultPath: string): string {
  return join(vaultPath, SYNC_STATE_FILE);
}

export async function readSyncState(vaultPath: string): Promise<SyncState> {
  try {
    const raw = await readFile(syncStatePath(vaultPath), 'utf-8');
    return JSON.parse(raw) as SyncState;
  } catch {
    return {
      lastSyncAt: '',
      databases: {},
      entries: {},
    };
  }
}

export async function writeSyncState(
  vaultPath: string,
  state: SyncState,
): Promise<void> {
  await writeFile(
    syncStatePath(vaultPath),
    JSON.stringify(state, null, 2) + '\n',
    'utf-8',
  );
}

export function getEntry(
  state: SyncState,
  localPath: string,
): SyncStateEntry | undefined {
  return state.entries[localPath];
}

export function setEntry(
  state: SyncState,
  localPath: string,
  entry: SyncStateEntry,
): void {
  state.entries[localPath] = entry;
}

export function removeEntry(state: SyncState, localPath: string): void {
  delete state.entries[localPath];
}
