import { describe, expect, it } from 'vitest';

import { selectNextFromStages } from '../src/verbs/next_selection.js';

describe('selectNextFromStages', () => {
  it('errors if any in-progress items exist (1)', () => {
    expect(() =>
      selectNextFromStages({
        inProgressIds: ['A'],
        backlogOrderedIds: ['B'],
      }),
    ).toThrow(/in-progress/i);
  });

  it('errors if any in-progress items exist (>1)', () => {
    expect(() =>
      selectNextFromStages({
        inProgressIds: ['A', 'B'],
        backlogOrderedIds: ['C'],
      }),
    ).toThrow(/in-progress/i);
  });

  it('returns none when backlog is empty', () => {
    expect(
      selectNextFromStages({
        inProgressIds: [],
        backlogOrderedIds: [],
      }),
    ).toEqual({ kind: 'none' });
  });

  it('selects first item from ordered backlog', () => {
    expect(
      selectNextFromStages({
        inProgressIds: [],
        backlogOrderedIds: ['B', 'C'],
      }),
    ).toEqual({ kind: 'selected', id: 'B' });
  });
});
