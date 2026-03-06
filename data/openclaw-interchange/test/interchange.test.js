import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {
  readMd, writeMd, atomicWrite,
  acquireLock, releaseLock,
  validateFrontmatter, validateLayer,
  contentHash, nextGenerationId,
  serializeFrontmatter, serializeTable,
  isStale,
  reconcileDbToInterchange,
  CircuitBreaker,
  slugify, formatTable, formatCurrency, relativeTime,
} from '../src/index.js';

let tmpDir;

beforeEach(() => {
  tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'interchange-test-'));
});

afterEach(() => {
  fs.rmSync(tmpDir, { recursive: true, force: true });
});

describe('atomicWrite', () => {
  it('writes file atomically', () => {
    const fp = path.join(tmpDir, 'test.md');
    atomicWrite(fp, 'hello world');
    expect(fs.readFileSync(fp, 'utf8')).toBe('hello world');
  });

  it('creates parent directories', () => {
    const fp = path.join(tmpDir, 'a', 'b', 'c.md');
    atomicWrite(fp, 'deep');
    expect(fs.readFileSync(fp, 'utf8')).toBe('deep');
  });

  it('leaves no tmp files on success', () => {
    const fp = path.join(tmpDir, 'clean.md');
    atomicWrite(fp, 'data');
    const files = fs.readdirSync(tmpDir);
    expect(files).toEqual(['clean.md']);
  });
});

const VALID_META = {
  skill: 'test', type: 'summary', layer: 'ops',
  version: 1, generator: 'test@1.0', tags: ['test'],
};

describe('readMd / writeMd', () => {
  it('round-trips frontmatter and content', async () => {
    const fp = path.join(tmpDir, 'doc.md');
    await writeMd(fp, VALID_META, '# Hello\n\nWorld');
    const { meta, content } = readMd(fp);
    expect(meta.skill).toBe('test');
    expect(meta.generation_id).toBe(1);
    expect(meta.content_hash).toMatch(/^sha256:/);
    expect(content).toContain('# Hello');
  });

  it('idempotent: same content does not increment generation_id', async () => {
    const fp = path.join(tmpDir, 'idem.md');
    await writeMd(fp, VALID_META, 'same content');
    const { meta: m1 } = readMd(fp);
    await writeMd(fp, VALID_META, 'same content');
    const { meta: m2 } = readMd(fp);
    expect(m2.generation_id).toBe(m1.generation_id);
  });

  it('increments generation_id on content change', async () => {
    const fp = path.join(tmpDir, 'gen.md');
    await writeMd(fp, VALID_META, 'v1');
    await writeMd(fp, VALID_META, 'v2');
    const { meta } = readMd(fp);
    expect(meta.generation_id).toBe(2);
  });

  it('rejects invalid frontmatter by default', async () => {
    const fp = path.join(tmpDir, 'invalid.md');
    await expect(writeMd(fp, { skill: 'test' }, 'content')).rejects.toThrow(/Invalid frontmatter/);
  });

  it('allows skipValidation for internal use', async () => {
    const fp = path.join(tmpDir, 'skip.md');
    await writeMd(fp, { skill: 'test' }, 'content', { skipValidation: true });
    expect(readMd(fp).meta.skill).toBe('test');
  });

  it('handles CRLF line endings', () => {
    const fp = path.join(tmpDir, 'crlf.md');
    atomicWrite(fp, '---\r\nskill: test\r\n---\r\n# Content\r\n');
    const { meta, content } = readMd(fp);
    expect(meta.skill).toBe('test');
    expect(content).toContain('# Content');
  });
});

describe('locking', () => {
  it('acquire and release', async () => {
    const fp = path.join(tmpDir, 'locktest.md');
    const lock = await acquireLock(fp);
    expect(fs.existsSync(fp + '.lock')).toBe(true);
    releaseLock(lock);
    expect(fs.existsSync(fp + '.lock')).toBe(false);
  });

  it('times out on contended lock', async () => {
    const fp = path.join(tmpDir, 'contend.md');
    const lock1 = await acquireLock(fp);
    await expect(acquireLock(fp, 200)).rejects.toThrow(/Lock timeout/);
    releaseLock(lock1);
  });
});

describe('concurrent writes', () => {
  it('do not corrupt file', async () => {
    const fp = path.join(tmpDir, 'concurrent.md');
    const writes = Array.from({ length: 10 }, (_, i) =>
      writeMd(fp, VALID_META, `content-${i}`, { force: true })
    );
    await Promise.allSettled(writes);
    // File must be parseable
    const { meta, content } = readMd(fp);
    expect(meta.skill).toBe('test');
    expect(content).toMatch(/^content-\d+$/);
  });
});

describe('validateFrontmatter', () => {
  it('passes valid meta', () => {
    const result = validateFrontmatter({
      skill: 'crm', type: 'summary', layer: 'ops',
      updated: '2026-01-01', version: 1, generation_id: 1,
      content_hash: 'sha256:abc', generator: 'crm@1.0', tags: ['a'],
    });
    expect(result.valid).toBe(true);
  });

  it('fails on missing fields', () => {
    const result = validateFrontmatter({});
    expect(result.valid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
  });

  it('rejects invalid layer', () => {
    const result = validateFrontmatter({
      skill: 'x', type: 'summary', layer: 'bad',
      updated: 'now', version: 1, generation_id: 1,
      content_hash: 'sha256:abc', generator: 'x@1', tags: [],
    });
    expect(result.valid).toBe(false);
  });
});

describe('validateLayer', () => {
  it('passes matching path', () => {
    const r = validateLayer('/interchange/crm/ops/file.md', { layer: 'ops' });
    expect(r.valid).toBe(true);
  });
  it('fails mismatched path', () => {
    const r = validateLayer('/interchange/crm/state/file.md', { layer: 'ops' });
    expect(r.valid).toBe(false);
  });
});

describe('contentHash', () => {
  it('is deterministic', () => {
    expect(contentHash('hello')).toBe(contentHash('hello'));
  });
  it('starts with sha256:', () => {
    expect(contentHash('test')).toMatch(/^sha256:[a-f0-9]{64}$/);
  });
});

describe('serializeFrontmatter', () => {
  it('produces sorted keys', () => {
    const a = serializeFrontmatter({ z: 1, a: 2 });
    const b = serializeFrontmatter({ a: 2, z: 1 });
    expect(a).toBe(b);
  });

  it('is deterministic across calls', () => {
    const meta = { skill: 'crm', tags: ['a', 'b'], version: 1 };
    expect(serializeFrontmatter(meta)).toBe(serializeFrontmatter(meta));
  });
});

describe('serializeTable', () => {
  it('produces deterministic output', () => {
    const h = ['Name', 'Value'];
    const r = [['a', '1'], ['b', '2']];
    expect(serializeTable(h, r)).toBe(serializeTable(h, r));
  });

  it('formats correctly', () => {
    const table = serializeTable(['A', 'B'], [['x', 'y']]);
    expect(table).toContain('| A');
    expect(table).toContain('---');
    expect(table).toContain('| x');
  });
});

describe('isStale', () => {
  it('returns true for expired TTL', async () => {
    const fp = path.join(tmpDir, 'stale.md');
    const oldDate = new Date(Date.now() - 10000).toISOString();
    const yaml = `---\nupdated: ${oldDate}\nttl: 1\n---\nstale content`;
    atomicWrite(fp, yaml);
    expect(isStale(fp)).toBe(true);
  });

  it('returns false for fresh file', async () => {
    const fp = path.join(tmpDir, 'fresh.md');
    const now = new Date().toISOString();
    const yaml = `---\nupdated: ${now}\nttl: 9999\n---\nfresh`;
    atomicWrite(fp, yaml);
    expect(isStale(fp)).toBe(false);
  });
});

describe('reconcileDbToInterchange', () => {
  it('detects added, removed, changed, unchanged', () => {
    const db = { a: { hash: 'sha256:1' }, b: { hash: 'sha256:new' }, d: { hash: 'sha256:4' } };
    const files = [
      { id: 'a', content_hash: 'sha256:1' },
      { id: 'b', content_hash: 'sha256:old' },
      { id: 'c', content_hash: 'sha256:3' },
    ];
    const diff = reconcileDbToInterchange(db, files);
    expect(diff.added).toEqual(['d']);
    expect(diff.removed).toEqual(['c']);
    expect(diff.changed).toEqual(['b']);
    expect(diff.unchanged).toEqual(['a']);
  });
});

describe('CircuitBreaker', () => {
  it('opens after threshold failures', async () => {
    const cb = new CircuitBreaker({ threshold: 2, cooldownMs: 100000 });
    const fail = () => Promise.reject(new Error('fail'));
    await expect(cb.call(fail)).rejects.toThrow();
    await expect(cb.call(fail)).rejects.toThrow();
    expect(cb.state).toBe('OPEN');
  });

  it('serves stale data when open', async () => {
    const cb = new CircuitBreaker({ threshold: 1, cooldownMs: 100000 });
    await cb.call(() => Promise.resolve('fresh'));
    await cb.call(() => Promise.reject(new Error('fail')));
    expect(cb.state).toBe('OPEN');
    const result = await cb.call(() => Promise.reject(new Error('still down')));
    expect(result).toBe('fresh');
  });

  it('recovers after cooldown', async () => {
    const cb = new CircuitBreaker({ threshold: 1, cooldownMs: 1 });
    await expect(cb.call(() => Promise.reject(new Error('fail')))).rejects.toThrow();
    await new Promise(r => setTimeout(r, 10));
    const result = await cb.call(() => Promise.resolve('recovered'));
    expect(result).toBe('recovered');
    expect(cb.state).toBe('CLOSED');
  });
});

describe('helpers', () => {
  it('slugify', () => {
    expect(slugify('Hello World!')).toBe('hello-world');
    expect(slugify('  Acme Corp - Series B  ')).toBe('acme-corp-series-b');
  });

  it('formatCurrency', () => {
    expect(formatCurrency(1234.5)).toContain('1,234.50');
  });

  it('relativeTime', () => {
    const past = new Date(Date.now() - 3600000);
    expect(relativeTime(past)).toContain('ago');
  });
});
