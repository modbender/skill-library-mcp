import type { StageKey } from '../stage.js';

export type ProgressUpdateComment = {
  /** Human-friendly description of what is currently being worked on. */
  current: string;
  /** Human-friendly description of the next step. */
  next: string;
};

export type ProgressUpdateState = {
  /** workItemId -> ISO timestamp of the last automatic progress comment we posted */
  lastAutoCommentAt: Record<string, string>;
};

export type ProgressUpdatePort = {
  listIdsByStage(stage: StageKey): Promise<string[]>;
  addComment(id: string, body: string): Promise<void>;
};

export async function runProgressAutoUpdates(opts: {
  adapter: ProgressUpdatePort;
  now: Date;
  state?: ProgressUpdateState;
  intervalMs?: number;
  /**
   * Allows the caller (e.g., the agent) to provide a better message.
   * If omitted, a generic best-effort message is used.
   */
  getMessage?: (workItemId: string) => Promise<ProgressUpdateComment> | ProgressUpdateComment;
}): Promise<{ state: ProgressUpdateState; postedIds: string[] }> {
  const intervalMs = opts.intervalMs ?? 5 * 60 * 1000;
  const state: ProgressUpdateState = opts.state ?? { lastAutoCommentAt: {} };

  const inProgressIds = await opts.adapter.listIdsByStage('stage:in-progress');
  const inProgressSet = new Set(inProgressIds);

  // Stop tracking work items that are no longer in progress.
  for (const id of Object.keys(state.lastAutoCommentAt)) {
    if (!inProgressSet.has(id)) delete state.lastAutoCommentAt[id];
  }

  const postedIds: string[] = [];

  for (const id of inProgressIds) {
    const lastIso = state.lastAutoCommentAt[id];
    const lastMs = lastIso ? Date.parse(lastIso) : undefined;

    if (lastMs !== undefined && Number.isFinite(lastMs)) {
      if (opts.now.getTime() - lastMs < intervalMs) continue;
    }

    const msg = opts.getMessage
      ? await opts.getMessage(id)
      : {
          current: 'working on this task',
          next: 'continue implementation/testing',
        };

    await opts.adapter.addComment(id, `Progress update (auto):\n\n- Currently: ${msg.current}\n- Next: ${msg.next}`);
    state.lastAutoCommentAt[id] = opts.now.toISOString();
    postedIds.push(id);
  }

  return { state, postedIds };
}
