import { describe, it, expect } from 'vitest';
import { markdownToBlocks, blocksToMarkdown } from './notion-converter.js';

describe('markdownToBlocks', () => {
  it('converts headings', () => {
    const blocks = markdownToBlocks('# Title\n\n## Subtitle\n\n### Section');
    expect(blocks).toHaveLength(3);
    expect((blocks[0] as any).type).toBe('heading_1');
    expect((blocks[1] as any).type).toBe('heading_2');
    expect((blocks[2] as any).type).toBe('heading_3');
  });

  it('converts paragraphs', () => {
    const blocks = markdownToBlocks('Hello world');
    expect(blocks).toHaveLength(1);
    expect((blocks[0] as any).type).toBe('paragraph');
  });

  it('converts bullet lists', () => {
    const blocks = markdownToBlocks('- item one\n- item two');
    expect(blocks).toHaveLength(2);
    expect((blocks[0] as any).type).toBe('bulleted_list_item');
  });

  it('converts numbered lists', () => {
    const blocks = markdownToBlocks('1. first\n2. second');
    expect(blocks).toHaveLength(2);
    expect((blocks[0] as any).type).toBe('numbered_list_item');
  });

  it('converts code blocks', () => {
    const blocks = markdownToBlocks('```typescript\nconst x = 1;\n```');
    expect(blocks).toHaveLength(1);
    expect((blocks[0] as any).type).toBe('code');
  });

  it('converts blockquotes', () => {
    const blocks = markdownToBlocks('> A wise quote');
    expect(blocks).toHaveLength(1);
    expect((blocks[0] as any).type).toBe('quote');
  });

  it('converts dividers', () => {
    const blocks = markdownToBlocks('---');
    expect(blocks).toHaveLength(1);
    expect((blocks[0] as any).type).toBe('divider');
  });
});

describe('blocksToMarkdown', () => {
  it('converts blocks back to markdown', () => {
    const blocks = [
      { type: 'heading_1', heading_1: { rich_text: [{ type: 'text', text: { content: 'Title' } }] } },
      { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: 'Hello' } }] } },
      { type: 'bulleted_list_item', bulleted_list_item: { rich_text: [{ type: 'text', text: { content: 'item' } }] } },
    ];

    const md = blocksToMarkdown(blocks);
    expect(md).toContain('# Title');
    expect(md).toContain('Hello');
    expect(md).toContain('- item');
  });

  it('handles code blocks', () => {
    const blocks = [
      {
        type: 'code',
        code: {
          rich_text: [{ type: 'text', text: { content: 'const x = 1;' } }],
          language: 'typescript',
        },
      },
    ];

    const md = blocksToMarkdown(blocks);
    expect(md).toContain('```typescript');
    expect(md).toContain('const x = 1;');
    expect(md).toContain('```');
  });
});

describe('roundtrip', () => {
  it('preserves content through markdown -> blocks -> markdown', () => {
    const original = `# Hello

This is a paragraph.

- bullet one
- bullet two

> A quote

---

1. numbered
2. items`;

    const blocks = markdownToBlocks(original);
    const result = blocksToMarkdown(blocks);

    expect(result).toContain('# Hello');
    expect(result).toContain('This is a paragraph.');
    expect(result).toContain('- bullet one');
    expect(result).toContain('> A quote');
    expect(result).toContain('---');
    expect(result).toContain('1. numbered');
  });
});
