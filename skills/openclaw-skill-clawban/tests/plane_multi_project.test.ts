import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('execa', () => {
  return {
    execa: vi.fn(),
  };
});

import { execa } from 'execa';
import { PlaneAdapter } from '../src/adapters/plane.js';

type ExecaMock = typeof execa & {
  mockResolvedValueOnce: (value: unknown) => unknown;
  mockReset: () => unknown;
};

describe('PlaneAdapter (multi-project)', () => {
  beforeEach(() => {
    (execa as any as ExecaMock).mockReset();
  });

  it('combines backlog order across projects (config order) and is assignee-only', async () => {
    (execa as any as ExecaMock)
      // whoami -> me + projects list
      .mockResolvedValueOnce({ stdout: JSON.stringify({ id: 'me1' }) })
      .mockResolvedValueOnce({ stdout: JSON.stringify([]) })
      // project A issues list
      .mockResolvedValueOnce({
        stdout: JSON.stringify([
          { id: 'A1', name: 'A1', state: { name: 'stage:backlog' }, updated_at: '2026-02-26T00:00:00Z' },
        ]),
      })
      // project B issues list
      .mockResolvedValueOnce({
        stdout: JSON.stringify([
          { id: 'B1', name: 'B1', state: { name: 'stage:backlog' }, updated_at: '2026-02-26T00:00:01Z' },
        ]),
      });

    const adapter = new PlaneAdapter({
      workspaceSlug: 'ws',
      projectIds: ['projA', 'projB'],
      stageMap: {
        'stage:backlog': 'stage:backlog',
        'stage:blocked': 'stage:blocked',
        'stage:in-progress': 'stage:in-progress',
        'stage:in-review': 'stage:in-review',
      },
    });

    const ids = await adapter.listBacklogIdsInOrder();

    expect(execa).toHaveBeenNthCalledWith(3, 'plane', ['issues', 'list', '-p', 'projA', '--assignee', 'me1', '-f', 'json'], {
      stdout: 'pipe',
      stderr: 'pipe',
    });

    expect(execa).toHaveBeenNthCalledWith(4, 'plane', ['issues', 'list', '-p', 'projB', '--assignee', 'me1', '-f', 'json'], {
      stdout: 'pipe',
      stderr: 'pipe',
    });

    // config order, not updatedAt across projects.
    expect(ids).toEqual(['A1', 'B1']);
  });
});
