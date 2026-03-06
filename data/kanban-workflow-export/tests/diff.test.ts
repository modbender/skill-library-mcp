import { describe, expect, it } from 'vitest';

import { diffWorkItems } from '../src/diff.js';
import { Stage } from '../src/stage.js';
import type { WorkItem } from '../src/models.js';

describe('diffWorkItems', () => {
  it('emits deleted, created, stage changed, then updated in sorted id order', () => {
    const prev: Record<string, WorkItem> = {
      a: { id: 'a', title: 'A', stage: Stage.fromAny('backlog'), labels: [], raw: {} },
      b: { id: 'b', title: 'B', stage: Stage.fromAny('backlog'), labels: [], raw: {} },
      d: { id: 'd', title: 'D', stage: Stage.fromAny('backlog'), labels: ['x'], raw: {} },
    };

    const curr: Record<string, WorkItem> = {
      b: { id: 'b', title: 'B', stage: Stage.fromAny('in-progress'), labels: [], raw: {} },
      c: { id: 'c', title: 'C', stage: Stage.fromAny('backlog'), labels: [], raw: {} },
      d: { id: 'd', title: 'D2', stage: Stage.fromAny('backlog'), labels: ['x'], raw: {} },
    };

    const events = diffWorkItems(prev, curr);

    expect(events).toEqual([
      { type: 'WorkItemDeleted', workItemId: 'a' },
      { type: 'WorkItemCreated', workItem: curr.c },
      {
        type: 'StageChanged',
        workItemId: 'b',
        old: { key: 'stage:backlog' },
        new: { key: 'stage:in-progress' },
      },
      { type: 'WorkItemUpdated', workItemId: 'd' },
    ]);
  });
});
