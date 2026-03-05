import type { Event } from './events.js';
import type { WorkItem } from './models.js';

export function diffWorkItems(
  previous: ReadonlyMap<string, WorkItem> | Readonly<Record<string, WorkItem>>,
  current: ReadonlyMap<string, WorkItem> | Readonly<Record<string, WorkItem>>,
): Event[] {
  const prevMap = previous instanceof Map ? previous : new Map(Object.entries(previous));
  const currMap = current instanceof Map ? current : new Map(Object.entries(current));

  const events: Event[] = [];

  const prevIds = new Set(prevMap.keys());
  const currIds = new Set(currMap.keys());

  const deleted = [...prevIds].filter((id) => !currIds.has(id)).sort();
  for (const wid of deleted) {
    events.push({ type: 'WorkItemDeleted', workItemId: wid });
  }

  const created = [...currIds].filter((id) => !prevIds.has(id)).sort();
  for (const wid of created) {
    const workItem = currMap.get(wid);
    if (!workItem) continue;
    events.push({ type: 'WorkItemCreated', workItem });
  }

  const common = [...prevIds].filter((id) => currIds.has(id)).sort();
  for (const wid of common) {
    const prev = prevMap.get(wid);
    const curr = currMap.get(wid);
    if (!prev || !curr) continue;

    if (prev.stage.key !== curr.stage.key) {
      events.push({
        type: 'StageChanged',
        workItemId: wid,
        old: { key: prev.stage.key },
        new: { key: curr.stage.key },
      });
      continue;
    }

    const prevLabels = [...prev.labels];
    const currLabels = [...curr.labels];

    if (prev.title !== curr.title || prevLabels.join('\u0000') !== currLabels.join('\u0000')) {
      events.push({ type: 'WorkItemUpdated', workItemId: wid });
    }
  }

  return events;
}
