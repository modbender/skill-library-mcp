import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../src/setup.js', () => {
  return {
    runSetup: vi.fn(async () => undefined),
  };
});

vi.mock('../src/config.js', () => {
  return {
    loadConfigFromFile: vi.fn(async () => ({
      version: 1,
      adapter: { kind: 'github', repo: 'o/r', stageMap: {} },
    })),
  };
});

vi.mock('../src/adapters/github.js', () => {
  return {
    GitHubAdapter: vi.fn().mockImplementation(() => ({})),
  };
});

vi.mock('../src/adapters/linear.js', () => ({
  LinearAdapter: vi.fn().mockImplementation(() => ({})),
}));
vi.mock('../src/adapters/plane.js', () => ({
  PlaneAdapter: vi.fn().mockImplementation(() => ({})),
}));
vi.mock('../src/adapters/planka.js', () => ({
  PlankaAdapter: vi.fn().mockImplementation(() => ({})),
}));

vi.mock('../src/verbs/verbs.js', () => {
  return {
    show: vi.fn(async () => ({ id: 'X' })),
    next: vi.fn(async () => ({ id: 'X' })),
    start: vi.fn(async () => undefined),
    update: vi.fn(async () => undefined),
    ask: vi.fn(async () => undefined),
    complete: vi.fn(async () => undefined),
    create: vi.fn(async () => ({ id: 'X' })),
  };
});

import { runCli } from '../src/cli.js';
import { loadConfigFromFile } from '../src/config.js';
import { runSetup } from '../src/setup.js';
import { next as nextVerb, start as startVerb } from '../src/verbs/verbs.js';

type IoCapture = { out: string[]; err: string[] };

function createIo(): { io: any; cap: IoCapture } {
  const cap: IoCapture = { out: [], err: [] };
  return {
    cap,
    io: {
      stdout: { write: (chunk: string) => cap.out.push(chunk) },
      stderr: { write: (chunk: string) => cap.err.push(chunk) },
    },
  };
}

describe('cli what-next tips', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('prints a what-next tip after setup', async () => {
    const { io, cap } = createIo();

    const code = await runCli(
      [
        'setup',
        '--adapter',
        'planka',
        '--force',
        '--map-backlog',
        'Backlog',
        '--map-blocked',
        'Blocked',
        '--map-in-progress',
        'In Progress',
        '--map-in-review',
        'In Review',
        '--planka-board-id',
        'b1',
        '--planka-backlog-list-id',
        'l1',
      ],
      io,
    );

    expect(code).toBe(0);
    expect(runSetup).toHaveBeenCalledOnce();
    expect(cap.out.join('')).toMatch(/Wrote config\/kanban-workflow\.json/);
    expect(cap.out.join('')).toMatch(/What next: run `kanban-workflow next`/);
  });

  it('prints a what-next tip after next', async () => {
    const { io, cap } = createIo();

    const code = await runCli(['next'], io);

    expect(code).toBe(0);
    expect(nextVerb).toHaveBeenCalledOnce();
    expect(cap.out.join('')).toMatch(/What next: run `kanban-workflow start --id <id>`/);
  });

  it('prints a what-next tip after start', async () => {
    const { io, cap } = createIo();

    const code = await runCli(['start', '--id', '123'], io);

    expect(code).toBe(0);
    expect(startVerb).toHaveBeenCalledOnce();
    expect(cap.out.join('')).toMatch(/What next: run the actual execution in a subagent/);
    expect(cap.out.join('')).toMatch(/then `kanban-workflow ask --id <id> --text/);
    expect(cap.out.join('')).toMatch(/or `kanban-workflow update --id <id> --text/);
  });

  it.each([
    ['show', ['show', '--id', '1']],
    ['next', ['next']],
    ['start', ['start', '--id', '1']],
    ['update', ['update', '--id', '1', '--text', 'x']],
    ['ask', ['ask', '--id', '1', '--text', 'x']],
    ['complete', ['complete', '--id', '1', '--summary', 'x']],
    ['create', ['create', '--title', 't', '--body', 'b']],
  ])('errors with setup instructions when config is missing/invalid (%s)', async (_name, argv) => {
    const { io, cap } = createIo();

    vi.mocked(loadConfigFromFile).mockRejectedValueOnce(new Error('ENOENT'));

    const code = await runCli(argv, io);

    expect(code).toBe(1);
    expect(cap.err.join('')).toMatch(/Setup not completed/i);
    expect(cap.err.join('')).toMatch(/What next: run `kanban-workflow setup`/);
  });
});
