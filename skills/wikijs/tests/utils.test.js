import {
  formatJson,
  truncate,
  formatBytes,
  parseIdOrPath,
  parseTags
} from '../lib/utils.js';

describe('formatJson', () => {
  test('formats object as pretty JSON', () => {
    const result = formatJson({ key: 'value' });
    expect(result).toBe('{\n  "key": "value"\n}');
  });

  test('formats array as pretty JSON', () => {
    const result = formatJson([1, 2, 3]);
    expect(result).toBe('[\n  1,\n  2,\n  3\n]');
  });

  test('handles null and undefined', () => {
    expect(formatJson(null)).toBe('null');
    expect(formatJson(undefined)).toBe(undefined);
  });
});

describe('truncate', () => {
  test('returns original string if under max length', () => {
    expect(truncate('short', 10)).toBe('short');
  });

  test('truncates long strings with ellipsis', () => {
    expect(truncate('this is a very long string', 10)).toBe('this is...');
  });

  test('handles empty string', () => {
    expect(truncate('')).toBe('');
  });

  test('handles null/undefined', () => {
    expect(truncate(null)).toBe('');
    expect(truncate(undefined)).toBe('');
  });

  test('converts non-strings to string', () => {
    expect(truncate(12345, 10)).toBe('12345');
  });

  test('uses default max length of 50', () => {
    const longString = 'a'.repeat(60);
    const result = truncate(longString);
    expect(result.length).toBe(50);
    expect(result.endsWith('...')).toBe(true);
  });
});

describe('formatBytes', () => {
  test('formats 0 bytes', () => {
    expect(formatBytes(0)).toBe('0 B');
  });

  test('formats bytes', () => {
    expect(formatBytes(500)).toBe('500 B');
  });

  test('formats kilobytes', () => {
    expect(formatBytes(1024)).toBe('1 KB');
    expect(formatBytes(1536)).toBe('1.5 KB');
  });

  test('formats megabytes', () => {
    expect(formatBytes(1048576)).toBe('1 MB');
    expect(formatBytes(1572864)).toBe('1.5 MB');
  });

  test('formats gigabytes', () => {
    expect(formatBytes(1073741824)).toBe('1 GB');
  });
});

describe('parseIdOrPath', () => {
  test('parses numeric ID', () => {
    const result = parseIdOrPath('123');
    expect(result).toEqual({ type: 'id', value: 123 });
  });

  test('parses path string', () => {
    const result = parseIdOrPath('docs/api/overview');
    expect(result).toEqual({ type: 'path', value: 'docs/api/overview' });
  });

  test('treats number-like paths as paths', () => {
    const result = parseIdOrPath('123abc');
    expect(result).toEqual({ type: 'path', value: '123abc' });
  });

  test('handles paths starting with slash', () => {
    const result = parseIdOrPath('/some/path');
    expect(result).toEqual({ type: 'path', value: '/some/path' });
  });

  test('parses zero as ID', () => {
    const result = parseIdOrPath('0');
    expect(result).toEqual({ type: 'id', value: 0 });
  });
});

describe('parseTags', () => {
  test('parses comma-separated tags', () => {
    expect(parseTags('tag1,tag2,tag3')).toEqual(['tag1', 'tag2', 'tag3']);
  });

  test('trims whitespace from tags', () => {
    expect(parseTags('tag1 , tag2 , tag3')).toEqual(['tag1', 'tag2', 'tag3']);
  });

  test('filters empty tags', () => {
    expect(parseTags('tag1,,tag2,')).toEqual(['tag1', 'tag2']);
  });

  test('returns empty array for empty input', () => {
    expect(parseTags('')).toEqual([]);
    expect(parseTags(null)).toEqual([]);
    expect(parseTags(undefined)).toEqual([]);
  });

  test('handles single tag', () => {
    expect(parseTags('single')).toEqual(['single']);
  });
});
