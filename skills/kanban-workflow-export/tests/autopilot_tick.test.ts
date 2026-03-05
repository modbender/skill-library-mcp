import { describe, expect, test, vi } from 'vitest';

import { runAutopilotTick } from '../src/automation/autopilot_tick.js';

function fakeLock() {
  return {
    tryAcquireLock: vi.fn(async () => ({ release: vi.fn(async () => undefined) })),
  };
}

describe('autopilot-tick', () => {
  test('returns in_progress when there is an in-progress item', async () => {
    const lock = fakeLock();
    const adapter = {
      listIdsByStage: vi.fn(async () => ['A']),
      listBacklogIdsInOrder: vi.fn(async () => ['B']),
      setStage: vi.fn(async () => undefined),
    };

    const res = await runAutopilotTick({ adapter, lock, now: new Date('2026-02-26T00:00:00Z') });
    expect(res).toEqual({ kind: 'in_progress', id: 'A', inProgressIds: ['A'] });
    expect(adapter.setStage).not.toHaveBeenCalled();
  });

  test('starts the first backlog item when idle', async () => {
    const lock = fakeLock();
    const adapter = {
      listIdsByStage: vi.fn(async () => []),
      listBacklogIdsInOrder: vi.fn(async () => ['B', 'C']),
      setStage: vi.fn(async () => undefined),
    };

    const res = await runAutopilotTick({ adapter, lock, now: new Date('2026-02-26T00:00:00Z') });
    expect(res).toEqual({ kind: 'started', id: 'B' });
    expect(adapter.setStage).toHaveBeenCalledWith('B', 'stage:in-progress');
  });

  test('returns no_work when backlog is empty and idle', async () => {
    const lock = fakeLock();
    const adapter = {
      listIdsByStage: vi.fn(async () => []),
      listBacklogIdsInOrder: vi.fn(async () => []),
      setStage: vi.fn(async () => undefined),
    };

    const res = await runAutopilotTick({ adapter, lock, now: new Date('2026-02-26T00:00:00Z') });
    expect(res).toEqual({ kind: 'no_work' });
    expect(adapter.setStage).not.toHaveBeenCalled();
  });
});
