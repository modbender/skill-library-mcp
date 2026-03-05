import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { levenshtein } from '../utils/levenshtein.js';

describe('levenshtein', () => {
  it('returns 0 for identical strings', () => {
    assert.equal(levenshtein('hello', 'hello'), 0);
  });

  it('returns length of other string when one is empty', () => {
    assert.equal(levenshtein('', 'abc'), 3);
    assert.equal(levenshtein('abc', ''), 3);
  });

  it('returns 0 for two empty strings', () => {
    assert.equal(levenshtein('', ''), 0);
  });

  it('calculates single-character edits', () => {
    assert.equal(levenshtein('cat', 'bat'), 1); // substitution
    assert.equal(levenshtein('cat', 'cats'), 1); // insertion
    assert.equal(levenshtein('cats', 'cat'), 1); // deletion
  });

  it('handles multi-character differences', () => {
    assert.equal(levenshtein('kitten', 'sitting'), 3);
    assert.equal(levenshtein('saturday', 'sunday'), 3);
  });

  it('detects typosquatting-like names', () => {
    assert.equal(levenshtein('lodash', 'lodas'), 1);
    assert.equal(levenshtein('express', 'expres'), 1);
    assert.equal(levenshtein('react', 'reakt'), 1);
    assert.equal(levenshtein('axios', 'axois'), 2); // transposition = 2 edits in Levenshtein
  });
});
