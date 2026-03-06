import { describe, expect, it } from 'vitest';

import { Stage } from '../src/stage.js';

describe('Stage.fromAny', () => {
  it('accepts canonical stage keys', () => {
    expect(Stage.fromAny('stage:in-progress').key).toBe('stage:in-progress');
  });

  it('accepts common shorthands', () => {
    expect(Stage.fromAny('In Progress').key).toBe('stage:in-progress');
    expect(Stage.fromAny('in_progress').key).toBe('stage:in-progress');
    expect(Stage.fromAny('stage/in-review').key).toBe('stage:in-review');
  });

  it('rejects unknown stages', () => {
    expect(() => Stage.fromAny('stage:banana')).toThrow(/Unknown stage/);
  });
});
