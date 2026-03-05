import type { Adapter } from '../adapter.js';
import type { WorkItem } from '../models.js';

import { Stage, type StageKey } from '../stage.js';

import { CliRunner } from './cli.js';

type LinearIssueNode = {
  id: string;
  title: string;
  url?: string;
  updatedAt?: string;
  state?: {
    id?: string;
    name?: string;
    type?: string;
  };
};

type LinearCliIssuesResponse = {
  data?: {
    issues?: {
      nodes?: LinearIssueNode[];
    };
  };
};

export type LinearAdapterOptions = {
  /** Optional view id to fetch issues in explicit (manual) view order. */
  viewId?: string;
  /**
   * Binary to execute.
   *
   * Default: `linear` (wrapper script from https://github.com/simonvanlaak/linear-cli)
   */
  bin?: string;

  /**
   * Optional arguments prepended to every command.
   *
   * Example (Api2Cli direct):
   *   ["--config", ".../linear-cli/a2c", "--workspace", "linear"]
   */
  baseArgs?: readonly string[];

  /** Provide either teamId OR projectId (exactly one). */
  teamId?: string;
  projectId?: string;

  /** Map Linear workflow state/list names -> canonical StageKey. Required for all 4 canonical stages. */
  stageMap: Readonly<Record<string, StageKey>>;
};

/**
 * Linear adapter (CLI-auth only).
 *
 * Expected CLI:
 * - https://github.com/simonvanlaak/linear-cli
 *
 * It should support:
 * - `issues-team <team_id>`
 * - `issues-project <project_id>`
 * and return JSON containing `data.issues.nodes[]`.
 */
export class LinearAdapter implements Adapter {
  private readonly cli: CliRunner;
  private readonly baseArgs: readonly string[];
  private readonly viewId?: string;
  private readonly teamId?: string;
  private readonly projectId?: string;
  private readonly stageMap: Readonly<Record<string, StageKey>>;

  constructor(opts: LinearAdapterOptions) {
    this.cli = new CliRunner(opts.bin ?? 'linear');
    this.baseArgs = opts.baseArgs ?? [];
    this.viewId = opts.viewId;
    this.teamId = opts.teamId;
    this.projectId = opts.projectId;
    this.stageMap = opts.stageMap;
  }

  name(): string {
    return 'linear';
  }

  // ---- Verb-level (workflow) API (best-effort; depends on linear-cli surface) ----

  async whoami(): Promise<{ id?: string; username?: string; name?: string }> {
    const out = await this.cli.run([...this.baseArgs, 'whoami']);
    const parsed = out.trim().length > 0 ? JSON.parse(out) : {};

    const viewer = parsed?.data?.viewer ?? parsed?.viewer ?? {};
    return {
      id: viewer.id ? String(viewer.id) : undefined,
      username: viewer.displayName ? String(viewer.displayName) : viewer.name ? String(viewer.name) : undefined,
      name: viewer.name ? String(viewer.name) : undefined,
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
    // Assume CLI provides an explicit order; fallback to updatedAt desc when missing.
    const hasAllUpdated = backlog.every((i) => i.updatedAt instanceof Date);

    const ordered = hasAllUpdated
      ? [...backlog].sort((a, b) => (b.updatedAt?.getTime() ?? 0) - (a.updatedAt?.getTime() ?? 0))
      : backlog;

    return ordered.map((i) => i.id);
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
    if (!item) throw new Error(`Linear work item not found: ${id}`);

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
    throw new Error('LinearAdapter.setStage not implemented (requires linear-cli write support)');
  }

  async addComment(_id: string, _body: string): Promise<void> {
    throw new Error('LinearAdapter.addComment not implemented (requires linear-cli write support)');
  }

  async createInBacklogAndAssignToSelf(_input: { title: string; body: string }): Promise<{ id: string; url?: string }> {
    throw new Error('LinearAdapter.create not implemented (requires linear-cli write support)');
  }

  async fetchSnapshot(): Promise<ReadonlyMap<string, WorkItem>> {
    if (this.viewId) {
      // Explicit ordering via view id.
      return this.fetchSnapshotFromView(this.viewId);
    }

    if ((this.teamId && this.projectId) || (!this.teamId && !this.projectId)) {
      throw new Error('LinearAdapter requires exactly one of: teamId, projectId (or provide viewId)');
    }

    const cmd = this.teamId
      ? (['issues-team', this.teamId] as const)
      : (['issues-project', this.projectId!] as const);

    const out = await this.cli.run([...this.baseArgs, ...cmd]);
    return this.parseIssuesJson(out);
  }

  private async fetchSnapshotFromView(viewId: string): Promise<ReadonlyMap<string, WorkItem>> {
    // Requirement: explicit ordering via view id. We assume linear-cli exposes a read-only
    // command that returns issues for a view in that view's manual order.
    //
    // Expected (by convention): `linear issues-view <view_id>`.
    const out = await this.cli.run([...this.baseArgs, 'issues-view', viewId]);
    return this.parseIssuesJson(out);
  }

  private parseIssuesJson(out: string): ReadonlyMap<string, WorkItem> {
    const parsed: LinearCliIssuesResponse = out.trim().length > 0 ? JSON.parse(out) : {};
    const nodes = parsed.data?.issues?.nodes ?? [];

    const items = new Map<string, WorkItem>();

    for (const node of nodes) {
      const stateId = node.state?.id;
      const stateName = node.state?.name;

      const mapped = (stateId && this.stageMap[stateId]) || (stateName && this.stageMap[stateName]);
      if (!mapped) {
        // Ignore states not mapped into the canonical set.
        continue;
      }

      const stage = Stage.fromAny(mapped);

      const updatedAt = node.updatedAt ? new Date(node.updatedAt) : undefined;
      if (updatedAt && Number.isNaN(updatedAt.getTime())) {
        throw new Error(`Invalid Linear updatedAt datetime: ${node.updatedAt}`);
      }

      items.set(node.id, {
        id: node.id,
        title: node.title,
        stage,
        url: node.url,
        labels: [],
        updatedAt,
        raw: node as unknown as Record<string, unknown>,
      });
    }

    return items;
  }
}
