import type { StageKey } from '../stage.js';

import { selectNextFromStages } from './next_selection.js';
import type { CreateInput, ShowPayload, VerbAdapter } from './types.js';

export async function show(adapter: VerbAdapter, id: string): Promise<ShowPayload> {
  const item = await adapter.getWorkItem(id);
  const [linked, comments, attachments] = await Promise.all([
    adapter.listLinkedWorkItems(id),
    adapter.listComments(id, {
      limit: 10,
      newestFirst: true,
      includeInternal: true,
    }),
    adapter.listAttachments(id),
  ]);

  return {
    adapter: adapter.name(),
    item: {
      ...item,
      attachments,
      linked,
    },
    comments,
  };
}

export type NextResult = { kind: 'none' } | ({ kind: 'item' } & ShowPayload);

export async function next(adapter: VerbAdapter): Promise<NextResult> {
  const inProgressIds = await adapter.listIdsByStage('stage:in-progress');
  const backlogOrderedIds = await adapter.listBacklogIdsInOrder();

  const sel = selectNextFromStages({ inProgressIds, backlogOrderedIds });
  if (sel.kind === 'none') return { kind: 'none' };

  const payload = await show(adapter, sel.id);
  return {
    kind: 'item',
    ...payload,
  };
}

export async function start(adapter: VerbAdapter, id: string): Promise<void> {
  await adapter.setStage(id, 'stage:in-progress');
}

export async function update(adapter: VerbAdapter, id: string, text: string): Promise<void> {
  await adapter.addComment(id, text);
}

export async function ask(adapter: VerbAdapter, id: string, text: string): Promise<void> {
  if (!text.trim()) throw new Error('ask requires non-empty text');
  await adapter.addComment(id, text);
  await adapter.setStage(id, 'stage:blocked');
}

export async function complete(adapter: VerbAdapter, id: string, summary: string): Promise<void> {
  if (!summary.trim()) throw new Error('complete requires non-empty summary');
  await adapter.addComment(id, `Completed: ${summary}`);
  await adapter.setStage(id, 'stage:in-review');
}

export async function create(adapter: VerbAdapter, input: CreateInput): Promise<{ id: string; url?: string }> {
  if (!input.title.trim()) throw new Error('create requires title');
  // body can be empty but should be provided as markdown
  return adapter.createInBacklogAndAssignToSelf({ title: input.title, body: input.body ?? '' });
}

export async function setStage(adapter: VerbAdapter, id: string, stage: StageKey): Promise<void> {
  await adapter.setStage(id, stage);
}
