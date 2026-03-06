import type { Adapter } from './adapter.js';
import type { Event } from './events.js';
import type { WorkItem } from './models.js';

import { diffWorkItems } from './diff.js';

export interface TickResult {
  adapterName: string;
  snapshot: ReadonlyMap<string, WorkItem>;
  events: Event[];
}

/**
 * Run one deterministic polling pass (poll → normalize → diff → events).
 *
 * This is the core, cron/webhook-friendly entrypoint.
 */
export async function tick(
  adapter: Adapter,
  previousSnapshot?: ReadonlyMap<string, WorkItem> | Readonly<Record<string, WorkItem>>,
): Promise<TickResult> {
  const prev = previousSnapshot ?? new Map<string, WorkItem>();

  const fetched = await adapter.fetchSnapshot();
  const snapshot = fetched instanceof Map ? new Map(fetched) : new Map(Object.entries(fetched));

  const events = diffWorkItems(prev, snapshot);

  return {
    adapterName: adapter.name(),
    snapshot,
    events,
  };
}
