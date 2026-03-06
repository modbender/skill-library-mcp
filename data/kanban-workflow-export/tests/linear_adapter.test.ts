import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('execa', () => {
  return {
    execa: vi.fn(),
  };
});

import { execa } from 'execa';

import { LinearAdapter } from '../src/adapters/linear.js';

type ExecaMock = typeof execa & {
  mockResolvedValueOnce: (value: unknown) => unknown;
  mockReset: () => unknown;
  mockImplementationOnce: (fn: any) => unknown;
};

describe('LinearAdapter', () => {
  beforeEach(() => {
    (execa as any as ExecaMock).mockReset();
  });

  it('parses whoami output', async () => {
    (execa as any as ExecaMock).mockResolvedValueOnce({
      stdout: JSON.stringify({
        data: {
          viewer: {
            id: 'u1',
            name: 'User One',
            displayName: 'user1',
          },
        },
      }),
    });

    const adapter = new LinearAdapter({
      teamId: 'team-123',
      stageMap: {
        'stage:backlog': 'stage:backlog',
        'stage:blocked': 'stage:blocked',
        'stage:in-progress': 'stage:in-progress',
        'stage:in-review': 'stage:in-review',
      },
    });

    await expect(adapter.whoami()).resolves.toEqual({ id: 'u1', username: 'user1', name: 'User One' });

    expect(execa).toHaveBeenCalledWith(
      'scripts/linear_json.sh',
      ['whoami'],
      expect.objectContaining({
        stdout: 'pipe',
        stderr: 'pipe',
      }),
    );
  });

  it('lists team issues and maps state.name to canonical Stage', async () => {
    (execa as any as ExecaMock).mockResolvedValueOnce({
      stdout: JSON.stringify({
        data: {
          issues: {
            nodes: [
              {
                id: 'l1',
                title: 'No stage',
                state: { name: 'Todo' },
              },
              {
                id: 'l2',
                title: 'Queued',
                url: 'https://linear.example/issue/l2',
                updatedAt: '2026-02-26T08:31:00Z',
                state: { name: 'stage:backlog' },
              },
            ],
          },
        },
      }),
    });

    const adapter = new LinearAdapter({
      teamId: 'team-123',
      stageMap: {
        'stage:backlog': 'stage:backlog',
        'stage:blocked': 'stage:blocked',
        'stage:in-progress': 'stage:in-progress',
        'stage:in-review': 'stage:in-review',
      },
    });

    const snap = await adapter.fetchSnapshot();

    expect(Array.from(snap.keys())).toEqual(['l2']);
    expect(snap.get('l2')?.stage.toString()).toBe('stage:backlog');
    expect(snap.get('l2')?.updatedAt?.toISOString()).toBe('2026-02-26T08:31:00.000Z');
  });

  it('supports calling a2c directly via bin + baseArgs and supports stageMap', async () => {
    (execa as any as ExecaMock).mockResolvedValueOnce({
      stdout: JSON.stringify({
        data: {
          issues: {
            nodes: [
              {
                id: 'l3',
                title: 'Mapped',
                state: { name: 'Doing' },
              },
            ],
          },
        },
      }),
    });

    const adapter = new LinearAdapter({
      projectId: 'proj-123',
      bin: 'a2c',
      baseArgs: ['--config', '/tmp/linear-cli/a2c', '--workspace', 'linear'],
      stageMap: {
        Doing: 'stage:in-progress',
      },
    });

    const snap = await adapter.fetchSnapshot();

    expect(snap.get('l3')?.stage.toString()).toBe('stage:in-progress');

    expect(execa).toHaveBeenCalledWith(
      'a2c',
      ['--config', '/tmp/linear-cli/a2c', '--workspace', 'linear', 'issues-project', 'proj-123'],
      expect.objectContaining({
        stdout: 'pipe',
        stderr: 'pipe',
      }),
    );
  });
});
