import type { Adapter } from '../adapter.js';
import type { WorkItem } from '../models.js';

import { CliRunner } from './cli.js';

/**
 * Planka adapter (CLI-auth only).
 *
 * Planka doesn't have a universally standard CLI. This adapter is a scaffold that assumes
 * you have a `planka` (or custom) CLI that can output JSON.
 */
import { z } from 'zod';

import { Stage } from '../stage.js';

export class PlankaAdapter implements Adapter {
  private readonly cli: CliRunner;
  private readonly listArgs: readonly string[];
  private readonly stageMap: Readonly<Record<string, import('../stage.js').StageKey>>;
  private readonly boardId: string;
  private readonly backlogListId: string;

  constructor(opts: {
    stageMap: Readonly<Record<string, import('../stage.js').StageKey>>;
    boardId: string;
    backlogListId: string;
    bin?: string;
    listArgs?: readonly string[];
  }) {
    // Uses https://github.com/voydz/planka-cli
    this.cli = new CliRunner(opts?.bin ?? 'planka-cli');
    // NOTE: planka-cli output flags may differ by version. Override listArgs if needed.
    // Prefer scoping by board when supported; fall back to a global list otherwise.
    this.listArgs = opts?.listArgs ?? ['cards', 'list', '--json', '--boardId', opts.boardId];
    this.stageMap = opts.stageMap;
    this.boardId = opts.boardId;
    this.backlogListId = opts.backlogListId;
  }

  name(): string {
    return 'planka';
  }

  // ---- Verb-level (workflow) API (best-effort; depends on planka-cli surface) ----

  async whoami(): Promise<{ id?: string; username?: string; name?: string }> {
    const node = new CliRunner('node');
    const out = await node.run(['scripts/planka_whoami_json.mjs']);
    const parsed = out.trim().length > 0 ? JSON.parse(out) : {};
    return {
      name: parsed?.name ? String(parsed.name) : undefined,
    };
  }

  async listIdsByStage(stage: import('../stage.js').StageKey): Promise<string[]> {
    const snap = await this.fetchSnapshot();
    return [...snap.values()]
      .filter((i) => i.stage.key === stage)
      .map((i) => i.id);
  }

  async listBacklogIdsInOrder(): Promise<string[]> {
    const snap = await this.fetchSnapshot();
    const backlog = [...snap.values()].filter((i) => i.stage.key === 'stage:backlog');

    // Planka card position is the explicit order; assume CLI returns cards in that order.
    return backlog.map((i) => i.id);
  }

  async getWorkItem(id: string): Promise<{
    id: string;
    title: string;
    url?: string;
    stage: import('../stage.js').StageKey;
    body?: string;
    labels: string[];
    updatedAt?: Date;
  }> {
    const snap = await this.fetchSnapshot();
    const item = snap.get(id);
    if (!item) throw new Error(`Planka card not found: ${id}`);

    return {
      id: item.id,
      title: item.title,
      url: item.url,
      stage: item.stage.key,
      body: undefined,
      labels: item.labels,
      updatedAt: item.updatedAt,
    };
  }

  async listComments(
    _id: string,
    _opts: { limit: number; newestFirst: boolean; includeInternal: boolean },
  ): Promise<Array<{ id: string; body: string }>> {
    return [];
  }

  async listAttachments(_id: string): Promise<Array<{ filename: string; url: string }>> {
    return [];
  }

  async listLinkedWorkItems(_id: string): Promise<Array<{ id: string; title: string }>> {
    return [];
  }

  async setStage(_id: string, _stage: import('../stage.js').StageKey): Promise<void> {
    throw new Error('PlankaAdapter.setStage not implemented (requires planka-cli write support)');
  }

  async addComment(_id: string, _body: string): Promise<void> {
    throw new Error('PlankaAdapter.addComment not implemented (requires planka-cli write support)');
  }

  async createInBacklogAndAssignToSelf(_input: { title: string; body: string }): Promise<{ id: string; url?: string }> {
    throw new Error('PlankaAdapter.create not implemented (requires planka-cli write support)');
  }

  async fetchSnapshot(): Promise<ReadonlyMap<string, WorkItem>> {
    const out = await this.cli.run(this.listArgs);

    // Best-effort schema for planka-cli JSON output. Adjust once we lock down the exact fields.
    const CardSchema = z.object({
      id: z.union([z.string(), z.number()]).transform((v) => String(v)),
      name: z.string().default(''),
      url: z.string().optional(),
      updatedAt: z.string().optional(),
      labels: z
        .array(z.object({ name: z.string() }).passthrough())
        .optional()
        .default([])
        .transform((arr) => arr.map((x) => x.name)),
      list: z
        .object({
          id: z.union([z.string(), z.number()]).transform((v) => String(v)).optional(),
          name: z.string(),
        })
        .optional(),
    });

    const ParsedSchema = z.array(CardSchema);
    const cards = ParsedSchema.parse(JSON.parse(out || '[]'));

    const items = new Map<string, WorkItem>();

    for (const card of cards) {
      const stageLabel = card.labels.find((l) => this.stageMap[l] !== undefined);
      const stageSource = stageLabel ?? (card.list?.name ? this.stageMap[card.list.name] : undefined);
      if (!stageSource) continue;

      const stage = Stage.fromAny(stageSource);

      items.set(card.id, {
        id: card.id,
        title: card.name,
        stage,
        url: card.url,
        labels: card.labels,
        updatedAt: card.updatedAt ? new Date(card.updatedAt) : undefined,
        raw: card,
      });
    }

    return items;
  }
}
