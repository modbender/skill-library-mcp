/**
 * Detect drift between database state and interchange .md files.
 *
 * @param {Record<string, any>} dbState - Map of entity ID → { hash, updated, ... }
 * @param {{ id: string, content_hash: string, updated: string }[]} files - Parsed interchange files
 * @returns {{ added: string[], removed: string[], changed: string[], unchanged: string[] }}
 */
export function reconcileDbToInterchange(dbState, files) {
  const fileMap = new Map(files.map(f => [f.id, f]));
  const dbIds = new Set(Object.keys(dbState));
  const fileIds = new Set(files.map(f => f.id));

  const added = [...dbIds].filter(id => !fileIds.has(id)).sort();
  const removed = [...fileIds].filter(id => !dbIds.has(id)).sort();
  const changed = [];
  const unchanged = [];

  for (const id of dbIds) {
    if (!fileIds.has(id)) continue;
    const file = fileMap.get(id);
    if (file.content_hash !== dbState[id].hash) {
      changed.push(id);
    } else {
      unchanged.push(id);
    }
  }

  return { added, removed, changed: changed.sort(), unchanged: unchanged.sort() };
}
