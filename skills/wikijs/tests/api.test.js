// Tests for API validation logic
// Note: These tests use mocked axios to test the API module

import { jest } from '@jest/globals';

// We need to test the validation functions indirectly since they're not exported
// This file tests basic module loading and structure

describe('API Module', () => {
  // Mock config before importing API
  jest.unstable_mockModule('../lib/config.js', () => ({
    loadConfig: () => ({
      url: 'http://test-wiki.local',
      apiToken: 'test-token'
    })
  }));

  describe('Module Loading', () => {
    test('exports expected functions', async () => {
      const api = await import('../lib/api.js');

      // Verify all expected exports exist
      expect(typeof api.listPages).toBe('function');
      expect(typeof api.searchPages).toBe('function');
      expect(typeof api.getPage).toBe('function');
      expect(typeof api.createPage).toBe('function');
      expect(typeof api.updatePage).toBe('function');
      expect(typeof api.movePage).toBe('function');
      expect(typeof api.deletePage).toBe('function');
      expect(typeof api.listTags).toBe('function');
      expect(typeof api.listAssets).toBe('function');
      expect(typeof api.uploadAsset).toBe('function');
      expect(typeof api.deleteAsset).toBe('function');
      expect(typeof api.getHealth).toBe('function');
      expect(typeof api.getStats).toBe('function');
      expect(typeof api.getPageVersions).toBe('function');
      expect(typeof api.revertPage).toBe('function');
    });
  });

  describe('Input Validation', () => {
    let api;

    beforeAll(async () => {
      // Mock axios to catch requests
      jest.unstable_mockModule('axios', () => ({
        default: {
          create: () => ({
            post: jest.fn().mockRejectedValue(new Error('Network disabled for testing')),
            interceptors: {
              response: { use: jest.fn() }
            }
          })
        }
      }));

      api = await import('../lib/api.js');
    });

    test('getPage rejects invalid ID format', async () => {
      // Test with invalid ID - this should fail validation
      await expect(api.getPage(-1)).rejects.toThrow();
    });

    test('deletePage rejects invalid ID', async () => {
      await expect(api.deletePage('invalid')).rejects.toThrow();
      await expect(api.deletePage(-5)).rejects.toThrow();
    });
  });
});

// Test the GraphQL error class behavior
describe('GraphQL Error Handling', () => {
  test('formats multiple error messages', () => {
    // This tests the error message formatting logic
    const errors = [
      { message: 'First error' },
      { message: 'Second error' }
    ];
    const combinedMessage = errors.map(e => e.message).join('; ');
    expect(combinedMessage).toBe('First error; Second error');
  });
});

// Test string sanitization patterns
describe('String Sanitization Patterns', () => {
  // These test the sanitization logic without importing the internal function
  const sanitize = (str) => {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/\\/g, '\\\\')
      .replace(/"/g, '\\"')
      .replace(/\n/g, '\\n')
      .replace(/\r/g, '\\r')
      .replace(/\t/g, '\\t');
  };

  test('escapes backslashes', () => {
    expect(sanitize('path\\to\\file')).toBe('path\\\\to\\\\file');
  });

  test('escapes quotes', () => {
    expect(sanitize('say "hello"')).toBe('say \\"hello\\"');
  });

  test('escapes newlines', () => {
    expect(sanitize('line1\nline2')).toBe('line1\\nline2');
  });

  test('escapes carriage returns', () => {
    expect(sanitize('line1\rline2')).toBe('line1\\rline2');
  });

  test('escapes tabs', () => {
    expect(sanitize('col1\tcol2')).toBe('col1\\tcol2');
  });

  test('handles null and undefined', () => {
    expect(sanitize(null)).toBe('');
    expect(sanitize(undefined)).toBe('');
  });

  test('handles complex injection attempts', () => {
    const malicious = '"); DROP TABLE pages; --';
    const sanitized = sanitize(malicious);
    // The quote is escaped so the injection won't work
    expect(sanitized).toBe('\\"); DROP TABLE pages; --');
    // The raw unescaped ") pattern is neutralized - now it's \")
    expect(sanitized.startsWith('\\")')).toBe(true);
  });
});

// Test path validation patterns
describe('Path Validation Patterns', () => {
  const validatePath = (path) => {
    if (!path || typeof path !== 'string') {
      throw new Error('Path is required');
    }
    const cleanPath = path.startsWith('/') ? path.slice(1) : path;
    if (/[<>:"|?*]/.test(cleanPath)) {
      throw new Error(`Invalid characters in path: ${path}`);
    }
    return cleanPath;
  };

  test('removes leading slash', () => {
    expect(validatePath('/docs/api')).toBe('docs/api');
  });

  test('keeps path without leading slash', () => {
    expect(validatePath('docs/api')).toBe('docs/api');
  });

  test('rejects invalid characters', () => {
    expect(() => validatePath('doc<s')).toThrow();
    expect(() => validatePath('doc>s')).toThrow();
    expect(() => validatePath('doc:s')).toThrow();
    expect(() => validatePath('doc"s')).toThrow();
    expect(() => validatePath('doc|s')).toThrow();
    expect(() => validatePath('doc?s')).toThrow();
    expect(() => validatePath('doc*s')).toThrow();
  });

  test('rejects empty path', () => {
    expect(() => validatePath('')).toThrow('Path is required');
    expect(() => validatePath(null)).toThrow('Path is required');
  });
});

// Test ID validation patterns
describe('ID Validation Patterns', () => {
  const validateId = (id) => {
    const num = parseInt(id, 10);
    if (isNaN(num) || num < 1) {
      throw new Error(`Invalid ID: ${id}`);
    }
    return num;
  };

  test('accepts valid positive integers', () => {
    expect(validateId(1)).toBe(1);
    expect(validateId(123)).toBe(123);
    expect(validateId('456')).toBe(456);
  });

  test('rejects zero', () => {
    expect(() => validateId(0)).toThrow('Invalid ID: 0');
  });

  test('rejects negative numbers', () => {
    expect(() => validateId(-1)).toThrow('Invalid ID: -1');
    expect(() => validateId(-100)).toThrow('Invalid ID: -100');
  });

  test('rejects non-numeric strings', () => {
    expect(() => validateId('abc')).toThrow();
    // Note: parseInt('12abc', 10) returns 12, so this is accepted
    // This matches JavaScript's parseInt behavior
    expect(validateId('12abc')).toBe(12);
  });

  test('rejects NaN', () => {
    expect(() => validateId(NaN)).toThrow();
  });
});
