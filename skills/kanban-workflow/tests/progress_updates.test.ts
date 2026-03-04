import { describe, expect, it, vi } from 'vitest';

import { runProgressAutoUpdates } from '../src/automation/progress_updates.js';

describe('runProgressAutoUpdates', () => {
  it('posts an automatic comment every 5 minutes while in stage:in-progress', async () => {
    const addComment = vi.fn(async () => undefined);
    const listIdsByStage = vi.fn(async () => ['A']);

    const t0 = new Date('2026-01-01T00:00:00.000Z');
    const t1 = new Date('2026-01-01T00:04:59.000Z');
    const t2 = new Date('2026-01-01T00:05:00.000Z');

    const r0 = await runProgressAutoUpdates({ adapter: { addComment, listIdsByStage }, now: t0 });
    expect(r0.postedIds).toEqual(['A']);

    const r1 = await runProgressAutoUpdates({ adapter: { addComment, listIdsByStage }, now: t1, state: r0.state });
    expect(r1.postedIds).toEqual([]);

    const r2 = await runProgressAutoUpdates({ adapter: { addComment, listIdsByStage }, now: t2, state: r1.state });
    expect(r2.postedIds).toEqual(['A']);

    expect(addComment).toHaveBeenCalledTimes(2);
  });

  it('stops posting when the item leaves stage:in-progress', async () => {
    const addComment = vi.fn(async () => undefined);
    const listIdsByStage = vi.fn<
      (stage: string) => Promise<string[]>
    >();

    listIdsByStage.mockResolvedValueOnce(['A']);
    const t0 = new Date('2026-01-01T00:00:00.000Z');

    const r0 = await runProgressAutoUpdates({ adapter: { addComment, listIdsByStage: listIdsByStage as any }, now: t0 });
    expect(r0.postedIds).toEqual(['A']);

    // Now nothing is in-progress.
    listIdsByStage.mockResolvedValueOnce([]);
    const t1 = new Date('2026-01-01T00:10:00.000Z');
    const r1 = await runProgressAutoUpdates({ adapter: { addComment, listIdsByStage: listIdsByStage as any }, now: t1, state: r0.state });

    expect(r1.postedIds).toEqual([]);
    expect(Object.keys(r1.state.lastAutoCommentAt)).toEqual([]);
  });
});
