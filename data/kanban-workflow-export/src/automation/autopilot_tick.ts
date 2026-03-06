import type { StageKey } from '../stage.js';

export type AutopilotTickResult =
  | { kind: 'no_work' }
  | { kind: 'in_progress'; id: string; inProgressIds: string[] }
  | { kind: 'started'; id: string };

export type AutopilotTickPort = {
  listIdsByStage(stage: StageKey): Promise<string[]>;
  listBacklogIdsInOrder(): Promise<string[]>;
  setStage(id: string, stage: StageKey): Promise<void>;
};

// Verb adapters already satisfy this shape; keep export for clarity.


export type AutopilotLockPort = {
  tryAcquireLock(path: string, now: Date, ttlMs: number): Promise<{ release: () => Promise<void> }>;
};

export async function runAutopilotTick(opts: {
  adapter: AutopilotTickPort;
  lock: AutopilotLockPort;
  now: Date;
  lockPath?: string;
  lockTtlMs?: number;
}): Promise<AutopilotTickResult> {
  const lockPath = opts.lockPath ?? '.tmp/kanban_autopilot.lock';
  const ttlMs = opts.lockTtlMs ?? 2 * 60 * 60 * 1000;

  const acquired = await opts.lock.tryAcquireLock(lockPath, opts.now, ttlMs);
  try {
    const inProgressIds = await opts.adapter.listIdsByStage('stage:in-progress');
    if (inProgressIds.length > 0) {
      return {
        kind: 'in_progress',
        id: inProgressIds[0]!,
        inProgressIds,
      };
    }

    const backlogOrderedIds = await opts.adapter.listBacklogIdsInOrder();
    const nextId = backlogOrderedIds[0];
    if (!nextId) return { kind: 'no_work' };

    await opts.adapter.setStage(nextId, 'stage:in-progress');
    return { kind: 'started', id: nextId };
  } finally {
    await acquired.release();
  }
}
