import { describe, expect, it, vi } from 'vitest';

import { runSetup } from '../src/setup.js';

function createMemoryFs(initial: Record<string, string> = {}) {
  const store = new Map(Object.entries(initial));

  return {
    async readFile(p: string): Promise<string> {
      const v = store.get(p);
      if (v === undefined) {
        const err: any = new Error('ENOENT');
        err.code = 'ENOENT';
        throw err;
      }
      return v;
    },
    async writeFile(p: string, content: string): Promise<void> {
      store.set(p, content);
    },
    async mkdir(): Promise<void> {
      // noop
    },
    exists(p: string): boolean {
      return store.has(p);
    },
    get(p: string): string | undefined {
      return store.get(p);
    },
  };
}

describe('setup', () => {
  it('requires --force to overwrite existing config', async () => {
    const fs = createMemoryFs({ 'config/kanban-workflow.json': '{"x":1}' });
    const validate = vi.fn(async () => undefined);

    await expect(
      runSetup({
        fs,
        configPath: 'config/kanban-workflow.json',
        force: false,
        config: {
          version: 1,
          adapter: {
            kind: 'github',
            repo: 'o/r',
            stageMap: {
              'stage:backlog': 'stage:backlog',
              'stage:blocked': 'stage:blocked',
              'stage:in-progress': 'stage:in-progress',
              'stage:in-review': 'stage:in-review',
            },
          },
        },
        validate,
      }),
    ).rejects.toThrow(/--force/i);

    expect(validate).not.toHaveBeenCalled();
  });

  it('fails hard if adapter validation fails', async () => {
    const fs = createMemoryFs();
    const validate = vi.fn(async () => {
      throw new Error('not authenticated');
    });

    await expect(
      runSetup({
        fs,
        configPath: 'config/kanban-workflow.json',
        force: true,
        config: {
          version: 1,
          adapter: {
            kind: 'github',
            repo: 'o/r',
            stageMap: {
              'stage:backlog': 'stage:backlog',
              'stage:blocked': 'stage:blocked',
              'stage:in-progress': 'stage:in-progress',
              'stage:in-review': 'stage:in-review',
            },
          },
        },
        validate,
      }),
    ).rejects.toThrow(/not authenticated/);

    expect(fs.exists('config/kanban-workflow.json')).toBe(false);
  });

  it('writes config after successful validation', async () => {
    const fs = createMemoryFs();
    const validate = vi.fn(async () => undefined);

    await runSetup({
      fs,
      configPath: 'config/kanban-workflow.json',
      force: true,
      config: {
        version: 1,
        adapter: {
          kind: 'github',
          repo: 'o/r',
          stageMap: {
            'stage:backlog': 'stage:backlog',
            'stage:blocked': 'stage:blocked',
            'stage:in-progress': 'stage:in-progress',
            'stage:in-review': 'stage:in-review',
          },
        },
      },
      validate,
    });

    expect(validate).toHaveBeenCalledOnce();
    expect(fs.exists('config/kanban-workflow.json')).toBe(true);
    expect(fs.get('config/kanban-workflow.json')).toMatch(/"github"/);
  });
});
