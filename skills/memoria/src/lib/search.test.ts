import { describe, it, expect } from 'vitest';
import { searchDocuments } from './search.js';
import type { MemDocument } from '../types.js';

function makeDoc(overrides: Partial<MemDocument>): MemDocument {
  return {
    id: 'test/doc',
    path: 'test/doc.md',
    category: 'facts',
    title: 'Test Doc',
    content: '',
    frontmatter: {},
    tags: [],
    created: '2026-01-01T00:00:00Z',
    updated: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

describe('searchDocuments', () => {
  it('returns matching documents ranked by score', () => {
    const docs = [
      makeDoc({ title: 'PostgreSQL Decision', content: 'We chose PostgreSQL for JSONB.' }),
      makeDoc({ title: 'MySQL Note', content: 'MySQL is also fine.' }),
      makeDoc({ title: 'Redis Cache', content: 'Use Redis for caching.' }),
    ];

    const results = searchDocuments(docs, 'postgresql');
    expect(results.length).toBeGreaterThanOrEqual(1);
    expect(results[0].document.title).toBe('PostgreSQL Decision');
  });

  it('respects category filter', () => {
    const docs = [
      makeDoc({ category: 'decisions', title: 'DB Pick', content: 'PostgreSQL' }),
      makeDoc({ category: 'facts', title: 'DB Fact', content: 'PostgreSQL is open source' }),
    ];

    const results = searchDocuments(docs, 'postgresql', { category: 'facts' });
    expect(results.length).toBe(1);
    expect(results[0].document.category).toBe('facts');
  });

  it('returns empty for no matches', () => {
    const docs = [makeDoc({ content: 'Nothing relevant here.' })];
    const results = searchDocuments(docs, 'xyznonexistent');
    expect(results.length).toBe(0);
  });

  it('respects limit', () => {
    const docs = Array.from({ length: 20 }, (_, i) =>
      makeDoc({ id: `d${i}`, title: `Doc ${i}`, content: `keyword item ${i}` }),
    );
    const results = searchDocuments(docs, 'keyword', { limit: 5 });
    expect(results.length).toBeLessThanOrEqual(5);
  });
});
