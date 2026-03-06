import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('execa', () => {
  return {
    execa: vi.fn()
  };
});

import { execa } from 'execa';
import * as fs from 'node:fs/promises';
import * as os from 'node:os';
import * as path from 'node:path';
import { GitHubAdapter } from '../src/adapters/github.js';

type ExecaMock = typeof execa & {
  mockResolvedValueOnce: (value: unknown) => unknown;
  mockReset: () => unknown;
};

function iso(dt: string): string {
  return new Date(dt).toISOString();
}

describe('GitHubAdapter', () => {
  let dir: string;
  let snapshotPath: string;

  beforeEach(async () => {
    dir = await fs.mkdtemp(path.join(os.tmpdir(), 'clawban-gh-'));
    snapshotPath = path.join(dir, 'snapshot.json');
    (execa as any as ExecaMock).mockReset();
  });

  afterEach(async () => {
    await fs.rm(dir, { recursive: true, force: true });
  });

  it('lists open issues that have stage:* labels', async () => {
    (execa as any as ExecaMock).mockResolvedValueOnce({
      stdout: JSON.stringify([
        {
          number: 1,
          title: 'No stage',
          url: 'u1',
          state: 'open',
          updatedAt: iso('2026-02-26T08:30:00Z'),
          labels: [{ name: 'bug' }]
        },
        {
          number: 2,
          title: 'Has stage',
          url: 'u2',
          state: 'open',
          updatedAt: iso('2026-02-26T08:31:00Z'),
          labels: [{ name: 'z' }, { name: 'stage:backlog' }, { name: 'a' }]
        }
      ])
    });

    const adapter = new GitHubAdapter({
      repo: 'o/r',
      snapshotPath,
      stageMap: {
        'stage:backlog': 'stage:backlog',
        'stage:blocked': 'stage:blocked',
        'stage:in-progress': 'stage:in-progress',
        'stage:in-review': 'stage:in-review',
      },
    });
    const items = await adapter.listOpenIssuesWithStageLabels();

    expect(items.map((i) => i.number)).toEqual([2]);
    expect(items[0]?.labels).toEqual(['stage:backlog', 'a', 'z']);
  });

  it('pollEventsSince emits created + persists snapshot', async () => {
    (execa as any as ExecaMock).mockResolvedValueOnce({
      stdout: JSON.stringify([
        {
          number: 10,
          title: 'New',
          url: 'u10',
          state: 'open',
          updatedAt: iso('2026-02-26T08:40:00Z'),
          labels: [{ name: 'stage:backlog' }]
        }
      ])
    });

    const adapter = new GitHubAdapter({
      repo: 'o/r',
      snapshotPath,
      stageMap: {
        'stage:backlog': 'stage:backlog',
        'stage:blocked': 'stage:blocked',
        'stage:in-progress': 'stage:in-progress',
        'stage:in-review': 'stage:in-review',
      },
    });
    const events = await adapter.pollEventsSince({ since: new Date('2026-02-26T08:39:00Z') });

    expect(events).toHaveLength(1);
    expect(events[0]?.kind).toBe('created');

    const snap = JSON.parse(await fs.readFile(snapshotPath, 'utf-8'));
    expect(snap['10']?.labels).toEqual(['stage:backlog']);
    expect(snap._meta?.repo).toBe('o/r');
  });

  it('pollEventsSince synthesizes labels_changed', async () => {
    await fs.writeFile(
      snapshotPath,
      JSON.stringify({
        '7': {
          updatedAt: '2026-02-26T08:00:00.000Z',
          labels: ['stage:backlog', 'bug'],
          title: 'T',
          url: 'u7',
          state: 'open'
        }
      })
    );

    (execa as any as ExecaMock).mockResolvedValueOnce({
      stdout: JSON.stringify([
        {
          number: 7,
          title: 'T',
          url: 'u7',
          state: 'open',
          updatedAt: iso('2026-02-26T08:10:00Z'),
          labels: [{ name: 'stage:backlog' }, { name: 'enhancement' }]
        }
      ])
    });

    const adapter = new GitHubAdapter({
      repo: 'o/r',
      snapshotPath,
      stageMap: {
        'stage:backlog': 'stage:backlog',
        'stage:blocked': 'stage:blocked',
        'stage:in-progress': 'stage:in-progress',
        'stage:in-review': 'stage:in-review',
      },
    });
    const events = await adapter.pollEventsSince({ since: new Date('2026-02-26T08:09:00Z') });

    expect(events).toHaveLength(1);
    expect(events[0]?.kind).toBe('labels_changed');
    expect(events[0]?.details).toEqual({
      added: ['enhancement'],
      removed: ['bug']
    });
  });

  it('addComment uses gh issue comment (id/body)', async () => {
    (execa as any as ExecaMock).mockResolvedValueOnce({ stdout: '' });

    const adapter = new GitHubAdapter({
      repo: 'o/r',
      snapshotPath,
      stageMap: {
        'stage:backlog': 'stage:backlog',
        'stage:blocked': 'stage:blocked',
        'stage:in-progress': 'stage:in-progress',
        'stage:in-review': 'stage:in-review',
      },
    });

    await adapter.addComment('123', 'hello');

    expect(execa).toHaveBeenCalledWith(
      'gh',
      ['issue', 'comment', '123', '--repo', 'o/r', '--body', 'hello'],
      { stdout: 'pipe', stderr: 'pipe' },
    );
  });

  it('listAttachments extracts github.com/user-attachments URLs from the body', async () => {
    (execa as any as ExecaMock).mockResolvedValueOnce({
      stdout: JSON.stringify({
        body: 'See https://github.com/user-attachments/files/12345/demo.txt and https://github.com/user-attachments/assets/aaa-bbb'
      })
    });

    const adapter = new GitHubAdapter({
      repo: 'o/r',
      snapshotPath,
      stageMap: {
        'stage:backlog': 'stage:backlog',
        'stage:blocked': 'stage:blocked',
        'stage:in-progress': 'stage:in-progress',
        'stage:in-review': 'stage:in-review',
      },
    });

    const attachments = await adapter.listAttachments('9');

    expect(execa).toHaveBeenCalledWith(
      'gh',
      ['issue', 'view', '9', '--repo', 'o/r', '--json', 'body'],
      { stdout: 'pipe', stderr: 'pipe' },
    );

    expect(attachments).toEqual([
      { filename: 'demo.txt', url: 'https://github.com/user-attachments/files/12345/demo.txt' },
      { filename: 'aaa-bbb', url: 'https://github.com/user-attachments/assets/aaa-bbb' },
    ]);
  });
});
