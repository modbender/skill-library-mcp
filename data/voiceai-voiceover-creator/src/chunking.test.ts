/**
 * Tests for chunking module — markdown parsing, auto-chunking, segment hashing.
 */
import { describe, it, expect } from 'vitest';
import { parseMarkdownHeadings, autoChunk, chunkScript } from './chunking.js';

/* ------------------------------------------------------------------ */
/*  parseMarkdownHeadings                                              */
/* ------------------------------------------------------------------ */

describe('parseMarkdownHeadings', () => {
  it('splits markdown by ## headings', () => {
    const md = `# Title

Some preamble text.

## Introduction

This is the intro paragraph.

## Main Content

This is the main body with details.

## Conclusion

Wrapping up here.
`;
    const sections = parseMarkdownHeadings(md);
    expect(sections).toHaveLength(4); // preamble + 3 sections
    expect(sections[0].title).toBe('Title');
    expect(sections[0].text).toContain('preamble');
    expect(sections[1].title).toBe('Introduction');
    expect(sections[1].text).toContain('intro paragraph');
    expect(sections[2].title).toBe('Main Content');
    expect(sections[3].title).toBe('Conclusion');
  });

  it('returns empty array for markdown with no content', () => {
    const sections = parseMarkdownHeadings('');
    expect(sections).toHaveLength(0);
  });

  it('handles markdown with only headings and no body text', () => {
    const md = `## First

## Second

Some text here.
`;
    const sections = parseMarkdownHeadings(md);
    // "First" heading with empty text should be filtered out
    expect(sections.length).toBeGreaterThanOrEqual(1);
    expect(sections.some((s) => s.title === 'Second')).toBe(true);
  });

  it('handles single section with no headings', () => {
    const text = 'Just a plain paragraph of text without any markdown headings.';
    const sections = parseMarkdownHeadings(text);
    expect(sections).toHaveLength(1);
    expect(sections[0].title).toBe('Preamble');
    expect(sections[0].text).toBe(text);
  });

  it('uses H1 as preamble title', () => {
    const md = `# My Video Title

Some preamble text.

## First Section

Content here.
`;
    const sections = parseMarkdownHeadings(md);
    expect(sections[0].title).toBe('My Video Title');
    expect(sections[0].text).toContain('preamble');
    expect(sections[1].title).toBe('First Section');
  });
});

/* ------------------------------------------------------------------ */
/*  autoChunk                                                          */
/* ------------------------------------------------------------------ */

describe('autoChunk', () => {
  it('returns single chunk for short text', () => {
    const text = 'This is a short sentence.';
    const chunks = autoChunk(text, 1500);
    expect(chunks).toHaveLength(1);
    expect(chunks[0].title).toBe('Segment 1');
    expect(chunks[0].text).toBe(text);
  });

  it('chunks long text by sentence boundaries', () => {
    const sentences = Array.from({ length: 20 }, (_, i) =>
      `This is sentence number ${i + 1} with some padding text to make it longer.`
    );
    const text = sentences.join(' ');
    const chunks = autoChunk(text, 200);
    expect(chunks.length).toBeGreaterThan(1);

    // Each chunk should be under maxChars (approximately)
    for (const chunk of chunks) {
      // Allow some overshoot due to sentence boundaries
      expect(chunk.text.length).toBeLessThan(400);
    }
  });

  it('handles text with no sentence-ending punctuation', () => {
    const text = 'This is a very long text without proper punctuation ' +
      'that just keeps going and going and going and should still be handled';
    const chunks = autoChunk(text, 50);
    expect(chunks.length).toBeGreaterThanOrEqual(1);
  });

  it('assigns sequential titles', () => {
    const text = 'First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence.';
    const chunks = autoChunk(text, 30);
    for (let i = 0; i < chunks.length; i++) {
      expect(chunks[i].title).toBe(`Segment ${i + 1}`);
    }
  });
});

/* ------------------------------------------------------------------ */
/*  chunkScript (integration)                                          */
/* ------------------------------------------------------------------ */

describe('chunkScript', () => {
  it('chunks markdown with headings mode', async () => {
    const md = `## Part One

First part content here.

## Part Two

Second part content here.
`;
    const segments = await chunkScript(md, {
      mode: 'headings',
      maxChars: 1500,
      voiceId: 'test-voice',
      templateDir: '/nonexistent',
    });

    expect(segments).toHaveLength(2);
    expect(segments[0].index).toBe(1);
    expect(segments[0].title).toBe('Part One');
    expect(segments[0].slug).toBe('part-one');
    expect(segments[0].source).toBe('heading');
    expect(segments[0].hash).toBeTruthy();
    expect(segments[1].index).toBe(2);
    expect(segments[1].title).toBe('Part Two');
  });

  it('falls back to auto when no headings found', async () => {
    const text = 'Just some text without headings. It should auto-chunk.';
    const segments = await chunkScript(text, {
      mode: 'headings',
      maxChars: 1500,
      voiceId: 'test-voice',
      templateDir: '/nonexistent',
    });

    expect(segments.length).toBeGreaterThanOrEqual(1);
    expect(segments[0].source).toBe('auto');
  });

  it('produces deterministic hashes for same input', async () => {
    const md = `## Section

Same text content.
`;
    const run1 = await chunkScript(md, {
      mode: 'headings',
      maxChars: 1500,
      voiceId: 'voice-a',
      templateDir: '/nonexistent',
    });
    const run2 = await chunkScript(md, {
      mode: 'headings',
      maxChars: 1500,
      voiceId: 'voice-a',
      templateDir: '/nonexistent',
    });

    expect(run1[0].hash).toBe(run2[0].hash);
  });

  it('produces different hashes for different voices', async () => {
    const md = `## Section

Same text content.
`;
    const run1 = await chunkScript(md, {
      mode: 'headings',
      maxChars: 1500,
      voiceId: 'voice-a',
      templateDir: '/nonexistent',
    });
    const run2 = await chunkScript(md, {
      mode: 'headings',
      maxChars: 1500,
      voiceId: 'voice-b',
      templateDir: '/nonexistent',
    });

    expect(run1[0].hash).not.toBe(run2[0].hash);
  });
});
