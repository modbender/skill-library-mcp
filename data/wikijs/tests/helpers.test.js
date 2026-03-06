import {
  diffStrings,
  formatDiff,
  extractLinks,
  isInternalLink,
  lintMarkdown,
  renderTree,
  sleep
} from '../lib/helpers.js';

describe('diffStrings', () => {
  test('identifies unchanged lines', () => {
    const result = diffStrings('line1\nline2', 'line1\nline2');
    expect(result).toHaveLength(2);
    expect(result[0]).toEqual({ type: 'unchanged', lineNum: 1, content: 'line1' });
    expect(result[1]).toEqual({ type: 'unchanged', lineNum: 2, content: 'line2' });
  });

  test('identifies added lines', () => {
    const result = diffStrings('line1', 'line1\nline2');
    expect(result).toHaveLength(2);
    expect(result[0]).toEqual({ type: 'unchanged', lineNum: 1, content: 'line1' });
    expect(result[1]).toEqual({ type: 'add', lineNum: 2, content: 'line2' });
  });

  test('identifies removed lines', () => {
    const result = diffStrings('line1\nline2', 'line1');
    expect(result).toHaveLength(2);
    expect(result[0]).toEqual({ type: 'unchanged', lineNum: 1, content: 'line1' });
    expect(result[1]).toEqual({ type: 'remove', lineNum: 2, content: 'line2' });
  });

  test('identifies changed lines', () => {
    const result = diffStrings('old', 'new');
    expect(result).toHaveLength(2);
    expect(result[0]).toEqual({ type: 'remove', lineNum: 1, content: 'old' });
    expect(result[1]).toEqual({ type: 'add', lineNum: 1, content: 'new' });
  });
});

describe('extractLinks', () => {
  test('extracts markdown links', () => {
    const links = extractLinks('Check [this link](http://example.com) out');
    expect(links).toHaveLength(1);
    expect(links[0]).toEqual({
      text: 'this link',
      url: 'http://example.com',
      type: 'markdown'
    });
  });

  test('extracts wiki-style links', () => {
    const links = extractLinks('See [[some-page]] for more info');
    expect(links).toHaveLength(1);
    expect(links[0]).toEqual({
      text: 'some-page',
      url: 'some-page',
      type: 'wiki'
    });
  });

  test('extracts wiki links with custom text', () => {
    const links = extractLinks('See [[some-page|Custom Text]] here');
    expect(links).toHaveLength(1);
    expect(links[0]).toEqual({
      text: 'Custom Text',
      url: 'some-page',
      type: 'wiki'
    });
  });

  test('extracts multiple links', () => {
    const markdown = '[Link 1](/page1) and [Link 2](/page2) and [[wiki-link]]';
    const links = extractLinks(markdown);
    expect(links).toHaveLength(3);
  });

  test('returns empty array for no links', () => {
    const links = extractLinks('No links here');
    expect(links).toHaveLength(0);
  });
});

describe('isInternalLink', () => {
  test('identifies external http links', () => {
    expect(isInternalLink('http://example.com')).toBe(false);
    expect(isInternalLink('https://example.com')).toBe(false);
  });

  test('identifies mailto links as external', () => {
    expect(isInternalLink('mailto:test@example.com')).toBe(false);
  });

  test('identifies internal relative links', () => {
    expect(isInternalLink('/some/path')).toBe(true);
    expect(isInternalLink('relative/path')).toBe(true);
    expect(isInternalLink('../parent/path')).toBe(true);
  });

  test('identifies anchor links as external', () => {
    expect(isInternalLink('#section')).toBe(false);
  });
});

describe('lintMarkdown', () => {
  test('validates clean markdown', () => {
    const result = lintMarkdown('# Heading\n\nSome content here.');
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  test('detects trailing whitespace', () => {
    const result = lintMarkdown('Line with trailing space   \n');
    expect(result.warnings.some(w => w.rule === 'no-trailing-spaces')).toBe(true);
  });

  test('detects multiple blank lines', () => {
    const result = lintMarkdown('Line 1\n\n\nLine 2');
    expect(result.warnings.some(w => w.rule === 'no-multiple-blanks')).toBe(true);
  });

  test('detects missing space after heading marker', () => {
    const result = lintMarkdown('#No space');
    expect(result.errors.some(e => e.rule === 'heading-space')).toBe(true);
  });

  test('detects empty document', () => {
    const result = lintMarkdown('   \n  \n   ');
    expect(result.errors.some(e => e.rule === 'no-empty')).toBe(true);
  });

  test('detects tabs', () => {
    const result = lintMarkdown('Line with\ttab');
    expect(result.warnings.some(w => w.rule === 'no-tabs')).toBe(true);
  });

  test('warns if first heading is not H1', () => {
    const result = lintMarkdown('## Second level heading');
    expect(result.warnings.some(w => w.rule === 'first-heading-h1')).toBe(true);
  });

  test('returns correct structure', () => {
    const result = lintMarkdown('# Valid');
    expect(result).toHaveProperty('valid');
    expect(result).toHaveProperty('errors');
    expect(result).toHaveProperty('warnings');
    expect(result).toHaveProperty('all');
    expect(Array.isArray(result.errors)).toBe(true);
    expect(Array.isArray(result.warnings)).toBe(true);
  });
});

describe('renderTree', () => {
  test('renders single item', () => {
    const items = [{ id: 1, path: 'page', title: 'Page Title' }];
    const output = renderTree(items);
    expect(output).toContain('Page Title');
    expect(output).toContain('(1)');
  });

  test('renders nested structure', () => {
    const items = [
      { id: 1, path: 'docs/api', title: 'API Docs' },
      { id: 2, path: 'docs/guide', title: 'Guide' }
    ];
    const output = renderTree(items);
    expect(output).toContain('docs/');
    expect(output).toContain('API Docs');
    expect(output).toContain('Guide');
  });

  test('uses custom accessors', () => {
    const items = [{ customId: 99, customPath: 'test', customTitle: 'Test' }];
    const output = renderTree(items, {
      getId: item => item.customId,
      getPath: item => item.customPath,
      getLabel: item => item.customTitle
    });
    expect(output).toContain('Test');
    expect(output).toContain('(99)');
  });
});

describe('sleep', () => {
  test('delays execution', async () => {
    const start = Date.now();
    await sleep(50);
    const elapsed = Date.now() - start;
    expect(elapsed).toBeGreaterThanOrEqual(45); // Allow some margin
  });
});

describe('formatDiff', () => {
  test('formats diff output', () => {
    const diff = [
      { type: 'unchanged', lineNum: 1, content: 'same' },
      { type: 'remove', lineNum: 2, content: 'old' },
      { type: 'add', lineNum: 2, content: 'new' }
    ];
    const output = formatDiff(diff);
    expect(output).toContain('old');
    expect(output).toContain('new');
  });
});

// Tests for TOC generation logic
describe('TOC Generation', () => {
  const extractHeadings = (content, maxDepth = 6) => {
    const headingRegex = /^(#{1,6})\s+(.+)$/gm;
    const headings = [];
    let match;

    while ((match = headingRegex.exec(content)) !== null) {
      const level = match[1].length;
      if (level <= maxDepth) {
        const text = match[2].trim();
        const slug = text.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-');
        headings.push({ level, text, slug });
      }
    }
    return headings;
  };

  test('extracts headings from markdown', () => {
    const content = '# Title\n\n## Section 1\n\n### Subsection\n\n## Section 2';
    const headings = extractHeadings(content);
    expect(headings).toHaveLength(4);
    expect(headings[0]).toEqual({ level: 1, text: 'Title', slug: 'title' });
    expect(headings[1]).toEqual({ level: 2, text: 'Section 1', slug: 'section-1' });
  });

  test('respects max depth', () => {
    const content = '# H1\n## H2\n### H3\n#### H4';
    const headings = extractHeadings(content, 2);
    expect(headings).toHaveLength(2);
  });

  test('generates correct slugs', () => {
    const content = '# Hello World!\n## Test: Section';
    const headings = extractHeadings(content);
    expect(headings[0].slug).toBe('hello-world');
    expect(headings[1].slug).toBe('test-section');
  });
});

// Tests for similarity calculation
describe('Content Similarity', () => {
  const getWords = (text) => {
    return text.toLowerCase()
      .replace(/[^\w\s]/g, '')
      .split(/\s+/)
      .filter(w => w.length > 3);
  };

  const similarity = (words1, words2) => {
    const set1 = new Set(words1);
    const set2 = new Set(words2);
    const intersection = [...set1].filter(w => set2.has(w));
    const union = new Set([...set1, ...set2]);
    return intersection.length / union.size;
  };

  test('extracts words correctly', () => {
    const words = getWords('Hello, World! This is a test.');
    expect(words).toContain('hello');
    expect(words).toContain('world');
    expect(words).toContain('this');
    expect(words).toContain('test');
    expect(words).not.toContain('is'); // Too short
    expect(words).not.toContain('a'); // Too short
  });

  test('calculates similarity of identical content', () => {
    const words = getWords('This is some test content');
    expect(similarity(words, words)).toBe(1);
  });

  test('calculates similarity of different content', () => {
    const words1 = getWords('This is about programming');
    const words2 = getWords('Cooking recipes for dinner');
    const sim = similarity(words1, words2);
    expect(sim).toBeLessThan(0.5);
  });

  test('calculates similarity of partially similar content', () => {
    const words1 = getWords('JavaScript programming tutorial');
    const words2 = getWords('JavaScript coding tutorial guide');
    const sim = similarity(words1, words2);
    expect(sim).toBeGreaterThan(0.3);
    expect(sim).toBeLessThan(1);
  });
});

// Tests for sitemap XML generation
describe('Sitemap Generation', () => {
  test('generates valid XML structure', () => {
    const pages = [
      { path: 'docs/api', updatedAt: '2026-01-15', isPublished: true },
      { path: 'docs/guide', updatedAt: '2026-01-20', isPublished: true }
    ];
    const baseUrl = 'https://wiki.example.com';

    const xml = [];
    xml.push('<?xml version="1.0" encoding="UTF-8"?>');
    xml.push('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">');
    for (const page of pages) {
      xml.push(`  <url><loc>${baseUrl}/${page.path}</loc></url>`);
    }
    xml.push('</urlset>');

    const output = xml.join('\n');
    expect(output).toContain('<?xml version="1.0"');
    expect(output).toContain('<urlset');
    expect(output).toContain('docs/api');
    expect(output).toContain('docs/guide');
    expect(output).toContain('</urlset>');
  });
});
