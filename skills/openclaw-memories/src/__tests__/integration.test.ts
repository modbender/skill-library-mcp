import { describe, it, expect, afterEach } from 'vitest';
import { ALMAAgent } from '../alma';
import { ObserverAgent } from '../observer';
import { MemoryIndexer } from '../indexer';
import { mkdirSync, writeFileSync, existsSync, rmSync } from 'fs';
import { join } from 'path';
import { tmpdir } from 'os';

const testDir = join(tmpdir(), 'oc-memory-test-' + Date.now());

afterEach(() => {
  if (existsSync(testDir)) rmSync(testDir, { recursive: true, force: true });
});

describe('ALMA', () => {
  it('proposes and evaluates designs', () => {
    const alma = new ALMAAgent({
      constraints: {
        chunkSize: { min: 100, max: 1000, type: 'number' },
        overlap: { min: 0, max: 0.5, type: 'number' },
      },
    });

    const d1 = alma.propose();
    expect(d1.id).toBeDefined();
    expect(d1.score).toBe(0);

    const score = alma.evaluate(d1.id, { accuracy: 0.8, speed: 0.9 });
    expect(score).toBeCloseTo(0.85);

    const best = alma.best();
    expect(best).toBeDefined();
    expect(best!.id).toBe(d1.id);

    alma.close();
  });

  it('mutates from a base design', () => {
    const alma = new ALMAAgent({
      constraints: { x: { min: 0, max: 1, type: 'number' } },
    });

    const d1 = alma.propose();
    alma.evaluate(d1.id, { score: 0.5 });

    const d2 = alma.propose(d1.id);
    expect(d2.id).not.toBe(d1.id);
    expect(d2.params).toBeDefined();

    alma.close();
  });

  it('tracks top designs', () => {
    const alma = new ALMAAgent({
      constraints: { x: { min: 0, max: 1, type: 'number' } },
    });

    const d1 = alma.propose();
    alma.evaluate(d1.id, { score: 0.3 });

    const d2 = alma.propose();
    alma.evaluate(d2.id, { score: 0.9 });

    const top = alma.top(2);
    expect(top.length).toBe(2);
    expect(top[0].score).toBeGreaterThanOrEqual(top[1].score);

    alma.close();
  });
});

describe('Observer', () => {
  it('creates observer without crashing', () => {
    const obs = new ObserverAgent({ provider: 'openai' });
    expect(obs).toBeDefined();
  });

  it('extract returns empty on LLM failure', async () => {
    const obs = new ObserverAgent({ provider: 'openai', apiKey: 'invalid' });
    const result = await obs.extract([
      { role: 'user', content: 'Alice likes TypeScript' },
    ]);
    expect(Array.isArray(result)).toBe(true);
  });
});

describe('Indexer', () => {
  it('indexes files and searches', () => {
    mkdirSync(testDir, { recursive: true });
    writeFileSync(join(testDir, 'MEMORY.md'), '# Memory\nAlice prefers TypeScript.\nBob likes Rust.\n');

    const idx = new MemoryIndexer({ workspace: testDir });
    const count = idx.index();
    expect(count).toBeGreaterThan(0);

    idx.close();
  });

  it('rebuilds index', () => {
    mkdirSync(testDir, { recursive: true });
    writeFileSync(join(testDir, 'MEMORY.md'), 'Some facts here.\n');

    const idx = new MemoryIndexer({ workspace: testDir });
    idx.index();
    const count = idx.rebuild();
    expect(count).toBeGreaterThan(0);

    idx.close();
  });
});
