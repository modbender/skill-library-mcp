/**
 * Tests for utility functions — slugify, hashing, formatting.
 */
import { describe, it, expect } from 'vitest';
import {
  slugify,
  zeroPad,
  contentHash,
  formatDuration,
  youtubeTimestamp,
  srtTimestamp,
} from './utils.js';

/* ------------------------------------------------------------------ */
/*  slugify                                                            */
/* ------------------------------------------------------------------ */

describe('slugify', () => {
  it('converts simple text to slug', () => {
    expect(slugify('Hello World')).toBe('hello-world');
  });

  it('removes special characters', () => {
    expect(slugify('What!? A Test...')).toBe('what-a-test');
  });

  it('handles apostrophes', () => {
    expect(slugify("It's a Creator's Life")).toBe('its-a-creators-life');
  });

  it('collapses multiple hyphens', () => {
    expect(slugify('too   many   spaces')).toBe('too-many-spaces');
  });

  it('strips leading and trailing hyphens', () => {
    expect(slugify('---hello---')).toBe('hello');
  });

  it('truncates to 60 characters', () => {
    const long = 'a'.repeat(100);
    expect(slugify(long).length).toBeLessThanOrEqual(60);
  });

  it('handles empty string', () => {
    expect(slugify('')).toBe('');
  });

  it('handles unicode characters', () => {
    const result = slugify('Über Cool Ñoño');
    expect(result).toBe('ber-cool-o-o');
  });
});

/* ------------------------------------------------------------------ */
/*  zeroPad                                                            */
/* ------------------------------------------------------------------ */

describe('zeroPad', () => {
  it('pads single digit', () => {
    expect(zeroPad(3)).toBe('003');
  });

  it('pads double digit', () => {
    expect(zeroPad(42)).toBe('042');
  });

  it('does not pad triple digit', () => {
    expect(zeroPad(100)).toBe('100');
  });

  it('supports custom width', () => {
    expect(zeroPad(5, 5)).toBe('00005');
  });
});

/* ------------------------------------------------------------------ */
/*  contentHash                                                        */
/* ------------------------------------------------------------------ */

describe('contentHash', () => {
  it('produces consistent hash for same input', () => {
    const h1 = contentHash('hello', 'world');
    const h2 = contentHash('hello', 'world');
    expect(h1).toBe(h2);
  });

  it('produces different hash for different input', () => {
    const h1 = contentHash('hello', 'world');
    const h2 = contentHash('hello', 'earth');
    expect(h1).not.toBe(h2);
  });

  it('returns 16-char hex string', () => {
    const h = contentHash('test');
    expect(h).toMatch(/^[0-9a-f]{16}$/);
  });

  it('handles single argument', () => {
    const h = contentHash('single');
    expect(h).toMatch(/^[0-9a-f]{16}$/);
  });

  it('handles many arguments', () => {
    const h = contentHash('a', 'b', 'c', 'd', 'e');
    expect(h).toMatch(/^[0-9a-f]{16}$/);
  });
});

/* ------------------------------------------------------------------ */
/*  formatDuration                                                     */
/* ------------------------------------------------------------------ */

describe('formatDuration', () => {
  it('formats seconds under a minute', () => {
    expect(formatDuration(45)).toBe('0:45');
  });

  it('formats minutes', () => {
    expect(formatDuration(125)).toBe('2:05');
  });

  it('formats hours', () => {
    expect(formatDuration(3661)).toBe('1:01:01');
  });

  it('handles zero', () => {
    expect(formatDuration(0)).toBe('0:00');
  });
});

/* ------------------------------------------------------------------ */
/*  youtubeTimestamp                                                    */
/* ------------------------------------------------------------------ */

describe('youtubeTimestamp', () => {
  it('formats zero as 0:00', () => {
    expect(youtubeTimestamp(0)).toBe('0:00');
  });

  it('formats minutes correctly', () => {
    expect(youtubeTimestamp(90)).toBe('1:30');
  });

  it('formats hours correctly', () => {
    expect(youtubeTimestamp(7200)).toBe('2:00:00');
  });
});

/* ------------------------------------------------------------------ */
/*  srtTimestamp                                                        */
/* ------------------------------------------------------------------ */

describe('srtTimestamp', () => {
  it('formats zero', () => {
    expect(srtTimestamp(0)).toBe('00:00:00,000');
  });

  it('formats fractional seconds', () => {
    expect(srtTimestamp(1.5)).toBe('00:00:01,500');
  });

  it('formats minutes and hours', () => {
    expect(srtTimestamp(3723.25)).toBe('01:02:03,250');
  });
});
