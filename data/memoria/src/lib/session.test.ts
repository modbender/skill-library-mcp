import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { initVault } from './vault.js';
import { getSession, startSession, updateCheckpoint, endSession, getRecentHandoffs } from './session.js';

describe('session', () => {
  let vaultPath: string;

  beforeEach(async () => {
    vaultPath = await mkdtemp(join(tmpdir(), 'memoria-session-'));
    await initVault(vaultPath, 'test');
  });

  afterEach(async () => {
    await rm(vaultPath, { recursive: true, force: true });
  });

  it('starts as idle', async () => {
    const session = await getSession(vaultPath);
    expect(session.state).toBe('idle');
  });

  it('transitions to active on start', async () => {
    const session = await startSession(vaultPath);
    expect(session.state).toBe('active');
    expect(session.startedAt).toBeDefined();
  });

  it('saves checkpoint', async () => {
    await startSession(vaultPath);
    const session = await updateCheckpoint(vaultPath, 'auth module', 'token refresh');
    expect(session.workingOn).toBe('auth module');
    expect(session.focus).toBe('token refresh');
    expect(session.lastCheckpoint).toBeDefined();
  });

  it('ends session and creates handoff', async () => {
    await startSession(vaultPath);
    await updateCheckpoint(vaultPath, 'auth module');
    const handoff = await endSession(vaultPath, 'Finished auth', 'Deploy to staging');

    expect(handoff.summary).toBe('Finished auth');
    expect(handoff.nextSteps).toBe('Deploy to staging');

    const session = await getSession(vaultPath);
    expect(session.state).toBe('idle');
  });

  it('retrieves recent handoffs', async () => {
    await startSession(vaultPath);
    await endSession(vaultPath, 'Session 1', 'Next 1');

    const handoffs = await getRecentHandoffs(vaultPath);
    expect(handoffs.length).toBe(1);
  });
});
