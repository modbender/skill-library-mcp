import { describe, it, expect } from 'vitest';
import { parseDocument, serializeDocument, slugify } from './document.js';

describe('slugify', () => {
  it('converts title to slug', () => {
    expect(slugify('Use PostgreSQL')).toBe('use-postgresql');
  });

  it('strips special characters', () => {
    expect(slugify('Hello, World! #123')).toBe('hello-world-123');
  });

  it('trims leading/trailing dashes', () => {
    expect(slugify('--hello--')).toBe('hello');
  });
});

describe('parseDocument', () => {
  it('parses frontmatter and content', () => {
    const raw = `---
title: My Decision
type: decision
tags: [db, infra]
created: "2026-01-01T00:00:00Z"
updated: "2026-01-01T00:00:00Z"
---
We chose PostgreSQL.`;

    const doc = parseDocument(raw, 'decisions/my-decision.md', 'decisions');
    expect(doc.title).toBe('My Decision');
    expect(doc.category).toBe('decisions');
    expect(doc.tags).toEqual(['db', 'infra']);
    expect(doc.content).toBe('We chose PostgreSQL.');
    expect(doc.frontmatter.type).toBe('decision');
  });

  it('handles missing frontmatter gracefully', () => {
    const raw = 'Just plain content';
    const doc = parseDocument(raw, 'inbox/note.md', 'inbox');
    expect(doc.title).toBe('note');
    expect(doc.content).toBe('Just plain content');
    expect(doc.tags).toEqual([]);
  });
});

describe('serializeDocument', () => {
  it('serializes with frontmatter', () => {
    const raw = serializeDocument({
      title: 'Test',
      content: 'Hello world',
      type: 'fact',
      tags: ['test'],
    });

    expect(raw).toContain('title: Test');
    expect(raw).toContain('type: fact');
    expect(raw).toContain('Hello world');
    expect(raw).toContain('tags:');
  });

  it('includes created and updated timestamps', () => {
    const raw = serializeDocument({ title: 'T', content: '' });
    expect(raw).toContain('created:');
    expect(raw).toContain('updated:');
  });
});
