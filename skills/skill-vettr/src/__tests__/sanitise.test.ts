import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import os from 'node:os';
import path from 'node:path';
import {
  sanitiseSlug,
  sanitiseUrl,
  sanitisePath,
  truncateEvidence,
  generateFindingId,
  getAllowedRoots,
} from '../utils/sanitise.js';

describe('sanitiseSlug', () => {
  it('accepts valid slugs', () => {
    assert.equal(sanitiseSlug('my-skill'), 'my-skill');
    assert.equal(sanitiseSlug('skill123'), 'skill123');
    assert.equal(sanitiseSlug('a1'), 'a1');
  });

  it('normalises to lowercase', () => {
    assert.equal(sanitiseSlug('My-Skill'), 'my-skill');
  });

  it('rejects invalid slugs', () => {
    assert.throws(() => sanitiseSlug(''), /Invalid slug/);
    assert.throws(() => sanitiseSlug('-invalid'), /Invalid slug/);
    assert.throws(() => sanitiseSlug('a'), /Invalid slug/);
    assert.throws(() => sanitiseSlug('has spaces'), /Invalid slug/);
    assert.throws(() => sanitiseSlug('has_underscore'), /Invalid slug/);
  });
});

describe('sanitiseUrl', () => {
  it('accepts valid HTTPS URLs', () => {
    assert.equal(sanitiseUrl('https://example.com'), 'https://example.com');
    assert.equal(sanitiseUrl('https://example.com/path'), 'https://example.com/path');
  });

  it('rejects HTTP URLs', () => {
    assert.throws(() => sanitiseUrl('http://example.com'), /Invalid URL/);
  });

  it('rejects URLs with embedded credentials', () => {
    // URL with credentials fails the URL regex before reaching the credentials check
    assert.throws(() => sanitiseUrl('https://user:pass@example.com'), /Invalid URL/);
  });

  it('rejects URLs with path traversal in pathname', () => {
    // URL() normalises ../ away, but sanitiseUrl checks parsed.pathname for '..'
    // Use a path that keeps '..' after URL parsing
    assert.throws(() => sanitiseUrl('https://example.com/foo/..%2e/etc'), /Invalid URL/);
  });
});

describe('sanitisePath', () => {
  const allowedRoots = [os.tmpdir(), path.join(os.homedir(), '.openclaw')];

  it('accepts paths within allowed roots', () => {
    const validPath = path.join(os.tmpdir(), 'test-skill');
    const result = sanitisePath(validPath, allowedRoots);
    assert.equal(result, path.resolve(validPath));
  });

  it('rejects path traversal with ..', () => {
    assert.throws(() => sanitisePath('../../../etc/passwd', allowedRoots), /traversal/);
  });

  it('rejects null bytes', () => {
    assert.throws(() => sanitisePath('/tmp/test\0.txt', allowedRoots), /traversal/);
  });

  it('rejects paths outside allowed roots', () => {
    assert.throws(() => sanitisePath('/usr/bin/evil', allowedRoots), /outside allowed/);
  });
});

describe('truncateEvidence', () => {
  it('returns short strings unchanged', () => {
    assert.equal(truncateEvidence('short'), 'short');
  });

  it('truncates long strings', () => {
    const long = 'a'.repeat(100);
    const result = truncateEvidence(long, 20);
    assert.equal(result.length, 20);
    assert.ok(result.endsWith('...'));
  });

  it('replaces newlines and tabs with spaces', () => {
    assert.equal(truncateEvidence('a\nb\tc'), 'a b c');
  });

  it('collapses multiple spaces', () => {
    assert.equal(truncateEvidence('a   b   c'), 'a b c');
  });
});

describe('generateFindingId', () => {
  it('returns a 16-character hex string', () => {
    const id = generateFindingId();
    assert.match(id, /^[0-9a-f]{16}$/);
  });

  it('generates unique ids', () => {
    const ids = new Set(Array.from({ length: 100 }, () => generateFindingId()));
    assert.equal(ids.size, 100);
  });
});


/**
 * getAllowedRoots: verifies base set and allowCwd behavior
 * Validates: Requirements 2.2, 2.3, 2.4
 */
describe('getAllowedRoots', () => {
  it('excludes process.cwd() by default (no config)', () => {
    const roots = getAllowedRoots();
    assert.ok(
      !roots.includes(process.cwd()),
      `Expected getAllowedRoots() to exclude process.cwd() by default, got: ${JSON.stringify(roots)}`,
    );
  });

  it('excludes process.cwd() when allowCwd is false', () => {
    const roots = getAllowedRoots({ allowCwd: false });
    assert.ok(!roots.includes(process.cwd()), 'process.cwd() should not be in roots when allowCwd is false');
  });

  it('includes process.cwd() when allowCwd is true', () => {
    const roots = getAllowedRoots({ allowCwd: true });
    assert.ok(roots.includes(process.cwd()), 'process.cwd() should be in roots when allowCwd is true');
  });

  it('includes base roots without config', () => {
    const roots = getAllowedRoots();
    assert.ok(roots.includes(os.tmpdir()), 'Missing os.tmpdir()');
    assert.ok(
      roots.includes(path.join(os.homedir(), '.openclaw')),
      'Missing ~/.openclaw',
    );
    assert.ok(
      roots.includes(path.join(os.homedir(), 'Downloads')),
      'Missing ~/Downloads',
    );
  });

  it('returns exactly 3 roots by default', () => {
    const roots = getAllowedRoots();
    assert.equal(roots.length, 3);
  });

  it('returns 4 roots when allowCwd is true', () => {
    const roots = getAllowedRoots({ allowCwd: true });
    assert.equal(roots.length, 4);
  });

  it('includes additionalRoots when provided', () => {
    const roots = getAllowedRoots({ additionalRoots: ['/custom/path'] });
    assert.ok(roots.includes('/custom/path'), 'Missing additional root');
  });
});
