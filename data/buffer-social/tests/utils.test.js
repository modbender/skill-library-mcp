import { describe, it, expect } from 'vitest';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import {
  parseScheduleTime,
  parseProfilesList,
  validatePostText,
  validateImagePath,
  validatePostOptions,
  parseLimit,
} from '../lib/utils.js';

describe('utils', () => {
  describe('validatePostText', () => {
    it('returns trimmed text when valid', () => {
      expect(validatePostText('  Hello Buffer  ')).toBe('Hello Buffer');
    });

    it('throws when text is missing', () => {
      expect(() => validatePostText('   ')).toThrow(/Post text is required/);
    });

    it('throws when text exceeds max length', () => {
      expect(() => validatePostText('a'.repeat(3001))).toThrow(/must be 3000 characters or less/);
    });
  });

  describe('parseScheduleTime', () => {
    it('returns null when no time provided', () => {
      expect(parseScheduleTime()).toBeNull();
    });

    it('returns normalized ISO string for valid datetime', () => {
      expect(parseScheduleTime('2026-03-03T14:00:00Z')).toBe('2026-03-03T14:00:00.000Z');
    });

    it('throws on invalid datetime input', () => {
      expect(() => parseScheduleTime('tomorrow 2pm')).toThrow(/Invalid schedule time/);
    });
  });

  describe('parseProfilesList', () => {
    it('parses comma-separated profiles and trims values', () => {
      expect(parseProfilesList('twitter, linkedin ,facebook')).toEqual([
        'twitter',
        'linkedin',
        'facebook',
      ]);
    });

    it('returns empty list when value not provided', () => {
      expect(parseProfilesList()).toEqual([]);
    });

    it('throws when list is provided but empty after trimming', () => {
      expect(() => parseProfilesList(' ,  , ')).toThrow(/No valid profile IDs found/);
    });
  });

  describe('validateImagePath', () => {
    it('returns null when no path provided', () => {
      expect(validateImagePath()).toBeNull();
    });

    it('returns resolved path when file exists', () => {
      const dir = mkdtempSync(join(tmpdir(), 'buffer-image-'));
      const file = join(dir, 'photo.jpg');
      writeFileSync(file, 'fake-image-bytes');

      expect(validateImagePath(file)).toContain('photo.jpg');

      rmSync(dir, { recursive: true, force: true });
    });

    it('throws when file does not exist', () => {
      expect(() => validateImagePath('/tmp/does-not-exist.jpg')).toThrow(/Image file not found/);
    });
  });

  describe('validatePostOptions', () => {
    it('allows exactly one targeting option', () => {
      expect(() => validatePostOptions({ profile: 'p1' })).not.toThrow();
    });

    it('throws when multiple targeting options are set', () => {
      expect(() => validatePostOptions({ profile: 'p1', all: true })).toThrow(
        /Choose only one target option/
      );
    });

    it('throws when queue and time are mixed', () => {
      expect(() =>
        validatePostOptions({ profile: 'p1', queue: true, time: '2026-03-03T14:00:00Z' })
      ).toThrow(/Cannot use --queue and --time together/);
    });
  });

  describe('parseLimit', () => {
    it('parses positive integer values', () => {
      expect(parseLimit('5')).toBe(5);
    });

    it('throws for invalid values', () => {
      expect(() => parseLimit('zero')).toThrow(/Invalid --limit value/);
      expect(() => parseLimit('0')).toThrow(/Invalid --limit value/);
    });
  });
});
