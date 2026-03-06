import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('execa', () => {
  return {
    execa: vi.fn()
  };
});

import { execa } from 'execa';
import { PlaneAdapter } from '../src/adapters/plane.js';

type ExecaMock = typeof execa & {
  mockResolvedValueOnce: (value: unknown) => unknown;
  mockReset: () => unknown;
};

describe('PlaneAdapter', () => {
  beforeEach(() => {
    (execa as any as ExecaMock).mockReset();
  });

  it('lists assigned issues and maps state.name to canonical Stage', async () => {
    // ensureMeId() -> whoami()
    (execa as any as ExecaMock)
      .mockResolvedValueOnce({
        stdout: JSON.stringify({ id: 'me1', email: 'me@example.com' }),
      })
      .mockResolvedValueOnce({ stdout: JSON.stringify([]) })
      // issues list
      .mockResolvedValueOnce({
        stdout: JSON.stringify([
          {
            id: 'i1',
            name: 'No stage',
            state_detail: { name: 'Doing' },
          },
          {
            id: 'i2',
            name: 'Queued',
            url: 'https://plane.example/issues/i2',
            updated_at: '2026-02-26T08:31:00Z',
            state: { name: 'stage:backlog' },
            labels: [{ name: 'bug' }, { name: 'stage:backlog' }],
          },
        ]),
      });

    const adapter = new PlaneAdapter({
      workspaceSlug: 'ws',
      projectId: 'proj',
      bin: 'plane',
      stageMap: {
        'stage:backlog': 'stage:backlog',
        'stage:blocked': 'stage:blocked',
        'stage:in-progress': 'stage:in-progress',
        'stage:in-review': 'stage:in-review',
      },
    });

    const snap = await adapter.fetchSnapshot();

    expect(execa).toHaveBeenNthCalledWith(1, 'plane', ['me', '-f', 'json'], { stdout: 'pipe', stderr: 'pipe' });
    expect(execa).toHaveBeenNthCalledWith(2, 'plane', ['projects', 'list', '-f', 'json'], { stdout: 'pipe', stderr: 'pipe' });
    expect(execa).toHaveBeenNthCalledWith(
      3,
      'plane',
      ['issues', 'list', '-p', 'proj', '--assignee', 'me1', '-f', 'json'],
      {
        stdout: 'pipe',
        stderr: 'pipe',
      },
    );

    expect(Array.from(snap.keys())).toEqual(['i2']);
    expect(snap.get('i2')?.stage.toString()).toBe('stage:backlog');
    expect(snap.get('i2')?.labels).toEqual(['bug', 'stage:backlog']);
  });

  it('supports mapping non-canonical Plane state names via stageMap', async () => {
    (execa as any as ExecaMock)
      .mockResolvedValueOnce({ stdout: JSON.stringify({ id: 'me1' }) })
      .mockResolvedValueOnce({ stdout: JSON.stringify([]) })
      .mockResolvedValueOnce({
        stdout: JSON.stringify([
          {
            id: 'i3',
            name: 'Mapped',
            state_detail: { name: 'Doing' },
          },
        ]),
      });

    const adapter = new PlaneAdapter({
      workspaceSlug: 'ws',
      projectId: 'proj',
      stageMap: {
        Doing: 'stage:in-progress',
      },
    });

    const snap = await adapter.fetchSnapshot();

    expect(execa).toHaveBeenNthCalledWith(
      3,
      'plane',
      ['issues', 'list', '-p', 'proj', '--assignee', 'me1', '-f', 'json'],
      {
        stdout: 'pipe',
        stderr: 'pipe',
      },
    );

    expect(snap.get('i3')?.stage.toString()).toBe('stage:in-progress');
  });
});
