import * as fs from 'node:fs/promises';
import * as path from 'node:path';

import type { Adapter } from '../adapter.js';
import type { WorkItem } from '../models.js';
import { Stage } from '../stage.js';

import { CliRunner } from './cli.js';

export type GitHubIssue = {
  number: number;
  title: string;
  url: string;
  state: string;
  updatedAt: Date;
  labels: string[];
};

export type GitHubIssueEvent = {
  kind: 'created' | 'updated' | 'labels_changed';
  issueNumber: number;
  updatedAt: Date;
  details: Record<string, unknown>;
};

type GhIssueListJson = {
  number: number;
  title?: string;
  url?: string;
  state?: string;
  updatedAt: string;
  labels?: Array<{ name: string }>;
};

function parseGitHubDate(value: string): Date {
  const dt = new Date(value);
  if (Number.isNaN(dt.getTime())) {
    throw new Error(`Invalid GitHub datetime: ${value}`);
  }
  return dt;
}

function toIsoZ(dt: Date): string {
  return dt.toISOString();
}

function pickStageLabel(labels: readonly string[]): string | undefined {
  const stageLabels = labels.filter((l) => l.toLowerCase().startsWith('stage:')).sort();
  return stageLabels[0];
}

/* pickFirst removed */

export class GhCli extends CliRunner {
  constructor() {
    super('gh');
  }
}

type SnapshotIssue = {
  updatedAt: string;
  labels: string[];
  title: string;
  url: string;
  state: string;
};

type Snapshot = Record<string, SnapshotIssue> & {
  _meta?: {
    repo: string;
    lastPolledAt: string;
  };
};

export class GitHubAdapter implements Adapter {
  private readonly repo: string;
  private readonly snapshotPath: string;
  private readonly gh: GhCli;
  private readonly project?: { owner: string; number: number };
  /** Platform stage label -> canonical stage key. */
  private readonly stageMap: Readonly<Record<string, import('../stage.js').StageKey>>;

  constructor(opts: {
    repo: string;
    snapshotPath: string;
    stageMap: Readonly<Record<string, import('../stage.js').StageKey>>;
    gh?: GhCli;
    project?: { owner: string; number: number };
  }) {
    this.repo = opts.repo;
    this.snapshotPath = opts.snapshotPath;
    this.stageMap = opts.stageMap;
    this.gh = opts.gh ?? new GhCli();
    this.project = opts.project;
  }

  name(): string {
    return `github:${this.repo}`;
  }

  // (stage mapping helpers live below under pickPlatformStage/platformStagesFor)

  async fetchSnapshot(): Promise<ReadonlyMap<string, WorkItem>> {
    const issues = await this.listOpenIssuesWithStageLabels({ limit: 200 });
    const items = new Map<string, WorkItem>();

    for (const issue of issues) {
      const stageLabel = this.pickPlatformStage(issue.labels);
      if (!stageLabel) continue;

      const mapped = this.stageMap[stageLabel];
      if (!mapped) continue;

      items.set(String(issue.number), {
        id: String(issue.number),
        title: issue.title,
        stage: Stage.fromAny(mapped),
        url: issue.url,
        labels: issue.labels,
        updatedAt: issue.updatedAt,
        raw: {
          number: issue.number,
          state: issue.state,
          updatedAt: issue.updatedAt.toISOString(),
        },
      });
    }

    return items;
  }

  async listOpenIssuesWithStageLabels(opts?: { limit?: number }): Promise<GitHubIssue[]> {
    const limit = opts?.limit ?? 200;
    const issues = await this.listIssues({ state: 'open', limit });

    return issues
      .filter((i) => i.labels.some((l) => l.startsWith('stage:')))
      .map((i) => {
        const stageLabels = [...i.labels].filter((l) => l.startsWith('stage:')).sort();
        const otherLabels = [...i.labels].filter((l) => !l.startsWith('stage:')).sort();
        return {
          ...i,
          labels: [...stageLabels, ...otherLabels]
        };
      });
  }

  async addComment(id: string, body: string): Promise<void> {
    await this.gh.run([
      'issue',
      'comment',
      String(id),
      '--repo',
      this.repo,
      '--body',
      body,
    ]);
  }

  private async addLabelsToIssue(issueNumber: number, labels: Iterable<string>): Promise<void> {
    const arr = Array.from(labels);
    if (arr.length === 0) return;

    await this.gh.run([
      'issue',
      'edit',
      String(issueNumber),
      '--repo',
      this.repo,
      '--add-label',
      arr.join(','),
    ]);
  }

  private async removeLabelsFromIssue(issueNumber: number, labels: Iterable<string>): Promise<void> {
    const arr = Array.from(labels);
    if (arr.length === 0) return;

    await this.gh.run([
      'issue',
      'edit',
      String(issueNumber),
      '--repo',
      this.repo,
      '--remove-label',
      arr.join(','),
    ]);
  }

  // ---- Verb-level (workflow) API ----

  private pickPlatformStage(labels: readonly string[]): string | undefined {
    // Prefer the first stage label that exists in the configured stageMap.
    const mapped = labels.filter((l) => this.stageMap[l] !== undefined).sort();
    if (mapped.length > 0) return mapped[0];

    // Back-compat: fall back to any stage:* label.
    return pickStageLabel(labels);
  }

  private platformStagesFor(stage: import('../stage.js').StageKey): string[] {
    return Object.entries(this.stageMap)
      .filter(([, canonical]) => canonical === stage)
      .map(([platform]) => platform)
      .sort();
  }

  async whoami(): Promise<{ username: string }> {
    const out = await this.gh.run(['api', 'user', '--jq', '.login']);
    const login = out.trim().replaceAll('"', '');
    if (!login) throw new Error('gh api user did not return login');
    return { username: login };
  }

  async listIdsByStage(stage: import('../stage.js').StageKey): Promise<string[]> {
    const platformStages = this.platformStagesFor(stage);
    if (platformStages.length === 0) {
      throw new Error(`No platform stage mapped for canonical ${stage}`);
    }

    // GH search doesn't support OR across labels easily; merge results.
    const ids: string[] = [];
    for (const platform of platformStages) {
      const issues = await this.listIssues({ state: 'open', limit: 200, search: `label:${platform}` });
      ids.push(...issues.map((i) => String(i.number)));
    }

    return [...new Set(ids)];
  }

  async listBacklogIdsInOrder(): Promise<string[]> {
    const all = await this.listOpenIssuesWithStageLabels({ limit: 200 });
    const backlog = all.filter((i) => {
      const platform = this.pickPlatformStage(i.labels);
      return platform ? this.stageMap[platform] === 'stage:backlog' : false;
    });

    const byUpdatedDesc = [...backlog].sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime());
    if (!this.project) {
      return byUpdatedDesc.map((i) => String(i.number));
    }

    const projectOrdered = await this.listProjectIssueNumbersInOrder({
      owner: this.project.owner,
      number: this.project.number,
    });

    const backlogByNumber = new Map(backlog.map((i) => [i.number, i] as const));
    const picked: number[] = [];

    for (const n of projectOrdered) {
      if (backlogByNumber.has(n)) picked.push(n);
    }

    const pickedSet = new Set(picked);
    for (const i of byUpdatedDesc) {
      if (!pickedSet.has(i.number)) picked.push(i.number);
    }

    return picked.map(String);
  }

  async getWorkItem(id: string): Promise<{
    id: string;
    title: string;
    url?: string;
    stage: import('../stage.js').StageKey;
    body?: string;
    labels: string[];
    assignees?: Array<{ username?: string; name?: string; id?: string }>;
    updatedAt?: Date;
  }> {
    const out = await this.gh.run([
      'issue',
      'view',
      String(id),
      '--repo',
      this.repo,
      '--json',
      'number,title,url,body,updatedAt,labels,assignees'
    ]);

    const parsed = out.trim().length > 0 ? JSON.parse(out) : {};
    const labels = (parsed.labels ?? []).map((l: any) => String(l.name)).sort();
    const stageLabel = this.pickPlatformStage(labels);
    if (!stageLabel) throw new Error(`Issue ${id} missing mapped stage label`);

    const mapped = this.stageMap[stageLabel];
    if (!mapped) throw new Error(`Issue ${id} stage label ${stageLabel} is not mapped in config`);

    const assignees = (parsed.assignees ?? []).map((a: any) => ({ username: a?.login, name: a?.name }));

    return {
      id: String(parsed.number ?? id),
      title: String(parsed.title ?? ''),
      url: parsed.url ? String(parsed.url) : undefined,
      stage: Stage.fromAny(mapped).key,
      body: parsed.body ? String(parsed.body) : undefined,
      labels,
      assignees,
      updatedAt: parsed.updatedAt ? parseGitHubDate(String(parsed.updatedAt)) : undefined,
    };
  }

  async listComments(
    id: string,
    opts: { limit: number; newestFirst: boolean; includeInternal: boolean },
  ): Promise<Array<{ id: string; body: string; createdAt?: Date; author?: { username?: string; name?: string } }>> {
    void opts.includeInternal; // GitHub issue comments have no "internal" concept.

    const out = await this.gh.run([
      'issue',
      'view',
      String(id),
      '--repo',
      this.repo,
      '--json',
      'comments'
    ]);

    const parsed = out.trim().length > 0 ? JSON.parse(out) : {};
    const comments = (parsed.comments ?? []).map((c: any) => ({
      id: String(c.id ?? ''),
      body: String(c.body ?? ''),
      createdAt: c.createdAt ? parseGitHubDate(String(c.createdAt)) : undefined,
      author: c.author ? { username: String(c.author.login ?? ''), name: c.author.name ? String(c.author.name) : undefined } : undefined,
    }));

    const sorted = [...comments].sort((a: any, b: any) => {
      const at = a.createdAt ? a.createdAt.getTime() : 0;
      const bt = b.createdAt ? b.createdAt.getTime() : 0;
      return opts.newestFirst ? bt - at : at - bt;
    });

    return sorted.slice(0, opts.limit);
  }

  async listAttachments(id: string): Promise<Array<{ filename: string; url: string }>> {
    // GitHub doesn't expose structured attachments, but uploaded issue attachments
    // commonly appear as `github.com/user-attachments/...` URLs in the body.
    const out = await this.gh.run([
      'issue',
      'view',
      String(id),
      '--repo',
      this.repo,
      '--json',
      'body',
    ]);

    const parsed = out.trim().length > 0 ? JSON.parse(out) : {};
    const body = typeof parsed.body === 'string' ? parsed.body : '';

    const urls = (body.match(/https:\/\/github\.com\/user-attachments\/[\w\-./?%#=]+/g) ?? [])
      .map((u) => u.replace(/[)"'>\]]+$/, ''));

    const uniq = Array.from(new Set(urls));

    return uniq.map((url) => {
      const clean = url.split('?')[0];
      const parts = clean.split('/').filter(Boolean);
      const last = parts[parts.length - 1] ?? 'attachment';
      return { filename: last, url };
    });
  }

  async listLinkedWorkItems(_id: string): Promise<Array<{ id: string; title: string }>> {
    // TODO: GitHub linked/related issues require GraphQL or parsing timeline items.
    return [];
  }

  async setStage(id: string, stage: import('../stage.js').StageKey): Promise<void> {
    const details = await this.getWorkItem(id);

    const desiredPlatform = this.platformStagesFor(stage)[0];
    if (!desiredPlatform) {
      throw new Error(`No platform stage mapped for canonical ${stage}`);
    }

    const knownStageLabels = details.labels.filter((l) => this.stageMap[l] !== undefined);
    const toRemove = knownStageLabels.filter((l) => l !== desiredPlatform);

    if (toRemove.length > 0) {
      await this.removeLabelsFromIssue(Number(id), toRemove);
    }
    if (!details.labels.includes(desiredPlatform)) {
      await this.addLabelsToIssue(Number(id), [desiredPlatform]);
    }
  }

  async createInBacklogAndAssignToSelf(input: { title: string; body: string }): Promise<{ id: string; url?: string }> {
    const self = await this.whoami();
    if (!self.username) {
      throw new Error('Unable to self-assign: gh whoami did not return username');
    }

    const backlogLabel = this.platformStagesFor('stage:backlog')[0];
    if (!backlogLabel) {
      throw new Error('Unable to create in backlog: no platform stage mapped to stage:backlog');
    }

    const out = await this.gh.run([
      'issue',
      'create',
      '--repo',
      this.repo,
      '--title',
      input.title,
      '--body',
      input.body,
      '--assignee',
      self.username,
      '--label',
      backlogLabel
    ]);

    const url = out.trim();
    const m = url.match(/\/issues\/(\d+)(?:\b|\/|$)/);
    const id = m?.[1];
    if (!id) {
      throw new Error(`Unable to parse created issue number from gh output: ${JSON.stringify(out)}`);
    }

    return { id, url };
  }

  private async listProjectIssueNumbersInOrder(opts: { owner: string; number: number }): Promise<number[]> {
    const out = await this.gh.run([
      'project',
      'item-list',
      String(opts.number),
      '--owner',
      opts.owner,
      '--limit',
      '200',
      '--format',
      'json'
    ]);

    const parsed = out.trim().length > 0 ? JSON.parse(out) : {};
    const items = Array.isArray(parsed.items) ? parsed.items : Array.isArray(parsed) ? parsed : [];

    const numbers: number[] = [];
    for (const item of items) {
      const n = item?.content?.number;
      if (typeof n === 'number') numbers.push(n);
    }
    return numbers;
  }

  async pollEventsSince(opts: { since: Date }): Promise<GitHubIssueEvent[]> {
    const since = opts.since;
    const snapshot = await this.loadSnapshot();

    const day = since.toISOString().slice(0, 10);
    const search = `is:issue updated:>=${day}`;
    const updated = await this.listIssues({ state: 'open', limit: 200, search });

    const events: GitHubIssueEvent[] = [];

    for (const issue of updated) {
      if (issue.updatedAt.getTime() < since.getTime()) continue;

      const prev = snapshot[String(issue.number)];
      if (!prev) {
        events.push({
          kind: 'created',
          issueNumber: issue.number,
          updatedAt: issue.updatedAt,
          details: { title: issue.title, labels: [...issue.labels] }
        });
      } else {
        const prevUpdatedAt = parseGitHubDate(prev.updatedAt);
        const prevLabels = new Set(prev.labels ?? []);
        const currLabels = new Set(issue.labels);

        const added = [...currLabels].filter((l) => !prevLabels.has(l)).sort();
        const removed = [...prevLabels].filter((l) => !currLabels.has(l)).sort();

        if (added.length > 0 || removed.length > 0) {
          events.push({
            kind: 'labels_changed',
            issueNumber: issue.number,
            updatedAt: issue.updatedAt,
            details: { added, removed }
          });
        } else if (issue.updatedAt.getTime() > prevUpdatedAt.getTime()) {
          events.push({
            kind: 'updated',
            issueNumber: issue.number,
            updatedAt: issue.updatedAt,
            details: {}
          });
        }
      }

      snapshot[String(issue.number)] = {
        updatedAt: toIsoZ(issue.updatedAt),
        labels: [...issue.labels],
        title: issue.title,
        url: issue.url,
        state: issue.state
      };
    }

    snapshot._meta = {
      repo: this.repo,
      lastPolledAt: toIsoZ(new Date())
    };

    await this.saveSnapshot(snapshot);
    return events;
  }

  private async listIssues(opts: {
    state: 'open' | 'closed' | 'all';
    limit: number;
    search?: string;
  }): Promise<GitHubIssue[]> {
    const args = [
      'issue',
      'list',
      '--repo',
      this.repo,
      '--state',
      opts.state,
      '--limit',
      String(opts.limit),
      '--json',
      'number,title,url,state,updatedAt,labels'
    ];
    if (opts.search) {
      args.push('--search', opts.search);
    }

    const out = await this.gh.run(args);
    const raw: GhIssueListJson[] = out.trim().length > 0 ? JSON.parse(out) : [];

    return raw.map((obj) => {
      const labels = (obj.labels ?? []).map((l) => l.name).sort();
      return {
        number: Number(obj.number),
        title: String(obj.title ?? ''),
        url: String(obj.url ?? ''),
        state: String(obj.state ?? ''),
        updatedAt: parseGitHubDate(String(obj.updatedAt)),
        labels
      };
    });
  }

  private async loadSnapshot(): Promise<Snapshot> {
    try {
      const text = await fs.readFile(this.snapshotPath, 'utf-8');
      return JSON.parse(text) as Snapshot;
    } catch (err: any) {
      if (err?.code === 'ENOENT') return {};
      throw err;
    }
  }

  private async saveSnapshot(snapshot: Snapshot): Promise<void> {
    await fs.mkdir(path.dirname(this.snapshotPath), { recursive: true });
    await fs.writeFile(this.snapshotPath, `${JSON.stringify(snapshot, null, 2)}\n`, 'utf-8');
  }
}
