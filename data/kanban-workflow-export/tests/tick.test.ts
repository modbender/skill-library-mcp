import { describe, expect, it } from 'vitest';

import { tick } from '../src/runner.js';
import { Stage } from '../src/stage.js';
import type { Adapter } from '../src/adapter.js';
import type { WorkItem } from '../src/models.js';

describe('tick', () => {
  it('returns adapter name, snapshot, and diff events', async () => {
    const snapshot1: Record<string, WorkItem> = {
      x: { id: 'x', title: 'X', stage: Stage.fromAny('stage:backlog'), labels: [], raw: {} },
    };
    const snapshot2: Record<string, WorkItem> = {
      x: { id: 'x', title: 'X2', stage: Stage.fromAny('stage:backlog'), labels: [], raw: {} },
    };

    let call = 0;
    const adapter: Adapter = {
      name: () => 'demo',
      fetchSnapshot: async () => {
        call += 1;
        return call === 1 ? snapshot1 : snapshot2;
      },
    };

    const r1 = await tick(adapter);
    expect(r1.adapterName).toBe('demo');
    expect([...r1.snapshot.keys()]).toEqual(['x']);
    expect(r1.events).toEqual([{ type: 'WorkItemCreated', workItem: snapshot1.x }]);

    const r2 = await tick(adapter, r1.snapshot);
    expect(r2.events).toEqual([{ type: 'WorkItemUpdated', workItemId: 'x' }]);
  });
});
