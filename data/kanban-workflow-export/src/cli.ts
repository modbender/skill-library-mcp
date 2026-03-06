import * as fs from 'node:fs/promises';

import { execa } from 'execa';

import { loadConfigFromFile } from './config.js';
import { runSetup } from './setup.js';
import { GitHubAdapter } from './adapters/github.js';
import { LinearAdapter } from './adapters/linear.js';
import { PlaneAdapter } from './adapters/plane.js';
import { PlankaAdapter } from './adapters/planka.js';
import { runAutopilotTick } from './automation/autopilot_tick.js';
import { lockfile } from './automation/lockfile.js';
import { ask, complete, create, next, show, start, update } from './verbs/verbs.js';

export type CliIo = {
  stdout: { write(chunk: string): void };
  stderr: { write(chunk: string): void };
};

function whatNextTipForCommand(cmd: string): string {
  switch (cmd) {
    case 'setup':
      return 'run `kanban-workflow next`';
    case 'next':
      return 'run `kanban-workflow start --id <id>`';
    case 'start':
      return 'run the actual execution in a subagent; then `kanban-workflow ask --id <id> --text "..."` or `kanban-workflow update --id <id> --text "..."`';
    case 'ask':
      return 'run `kanban-workflow next`';
    case 'update':
      return 'run `kanban-workflow complete --id <id> --summary "..."`';
    case 'complete':
      return 'run `kanban-workflow next`';
    case 'autopilot-tick':
      return 'if a ticket was started, your autopilot agent should `kanban-workflow show --id <id>` and begin work; otherwise wait and retry';
    case 'show':
    case 'create':
      return 'run `kanban-workflow next`';
    default:
      return 'run `kanban-workflow next`';
  }
}

function writeWhatNext(io: CliIo, cmd: string): void {
  io.stdout.write(`What next: ${whatNextTipForCommand(cmd)}\n`);
}

function writeSetupRequiredError(io: CliIo): void {
  io.stderr.write('Setup not completed: missing or invalid config/kanban-workflow.json\n');
  io.stderr.write('What next: run `kanban-workflow setup`\n');
}

function parseArgs(argv: string[]): { cmd: string; flags: Record<string, string | boolean | string[]> } {
  const [cmd = 'help', ...rest] = argv;
  const flags: Record<string, string | boolean | string[]> = {};

  for (let i = 0; i < rest.length; i++) {
    const tok = rest[i];
    if (!tok.startsWith('--')) continue;

    const key = tok.slice(2);
    const next = rest[i + 1];

    const value: string | boolean = next && !next.startsWith('--') ? next : true;
    if (value !== true) i++;

    const prev = flags[key];
    if (prev === undefined) {
      flags[key] = value;
    } else if (typeof prev === 'string') {
      flags[key] = [prev, String(value)];
    } else if (Array.isArray(prev)) {
      prev.push(String(value));
      flags[key] = prev;
    } else {
      // prev was boolean true; promote to array of strings
      flags[key] = [String(value)];
    }
  }

  return { cmd, flags };
}

export async function runCli(rawArgv: string[], io: CliIo = { stdout: process.stdout, stderr: process.stderr }): Promise<number> {
  const { cmd, flags } = parseArgs(rawArgv);
  const configPath = 'config/kanban-workflow.json';

  try {
    if (flags.config) {
      throw new Error('Only a single config file is supported: config/kanban-workflow.json (no --config override)');
    }

    if (cmd === 'setup') {
      const force = Boolean(flags.force);

      const adapterKind = String(flags.adapter ?? '').trim();
      if (!adapterKind) throw new Error('setup requires --adapter <github|plane|linear|planka>');

      const mapBacklog = String(flags['map-backlog'] ?? '').trim();
      const mapBlocked = String(flags['map-blocked'] ?? '').trim();
      const mapInProgress = String(flags['map-in-progress'] ?? '').trim();
      const mapInReview = String(flags['map-in-review'] ?? '').trim();

      if (!mapBacklog || !mapBlocked || !mapInProgress || !mapInReview) {
        throw new Error('setup requires all stage mappings: --map-backlog, --map-blocked, --map-in-progress, --map-in-review');
      }

      const stageMap: Record<string, string> = {
        [mapBacklog]: 'stage:backlog',
        [mapBlocked]: 'stage:blocked',
        [mapInProgress]: 'stage:in-progress',
        [mapInReview]: 'stage:in-review',
      };

      // Detect accidental duplicates (which would silently drop a mapping).
      if (new Set([mapBacklog, mapBlocked, mapInProgress, mapInReview]).size !== 4) {
        throw new Error('setup stage mapping values must be unique (a platform stage/list/status can only map to one canonical stage)');
      }

      let adapterCfg: any;

      if (adapterKind === 'github') {
        const repo = String(flags['github-repo'] ?? '').trim();
        if (!repo) throw new Error('setup --adapter github requires --github-repo <owner/repo>');

        const number = flags['github-project-number'] ? Number(flags['github-project-number']) : undefined;
        const owner = repo.includes('/') ? repo.split('/')[0] : undefined;

        adapterCfg = {
          kind: 'github',
          repo,
          project: owner && number ? { owner, number } : undefined,
          stageMap,
        };
      } else if (adapterKind === 'linear') {
        const teamId = flags['linear-team-id'] ? String(flags['linear-team-id']) : undefined;
        const projectId = flags['linear-project-id'] ? String(flags['linear-project-id']) : undefined;

        if ((teamId ? 1 : 0) + (projectId ? 1 : 0) !== 1) {
          throw new Error('setup --adapter linear requires exactly one scope: --linear-team-id <id> OR --linear-project-id <id>');
        }

        adapterCfg = {
          kind: 'linear',
          viewId: flags['linear-view-id'] ? String(flags['linear-view-id']) : undefined,
          teamId,
          projectId,
          stageMap,
        };
      } else if (adapterKind === 'plane') {
        const workspaceSlug = String(flags['plane-workspace-slug'] ?? '').trim();
        const scope = String(flags['plane-scope'] ?? 'project').trim();
        const projectId = String(flags['plane-project-id'] ?? '').trim();
        if (!workspaceSlug) throw new Error('setup --adapter plane requires --plane-workspace-slug <slug>');

        if (scope !== 'project' && scope !== 'all-projects') {
          throw new Error('setup --adapter plane: --plane-scope must be project|all-projects');
        }

        if (scope === 'project' && !projectId) {
          throw new Error('setup --adapter plane --plane-scope project requires --plane-project-id <uuid>');
        }

        const adapterTmp = new PlaneAdapter({
          workspaceSlug,
          projectId: scope === 'project' ? projectId : undefined,
          stageMap,
          orderField: flags['plane-order-field'] ? String(flags['plane-order-field']) : undefined,
        });

        let projectIds: string[] | undefined;
        if (scope === 'all-projects') {
          const out = await (adapterTmp as any).cli.run(['projects', 'list', '-f', 'json']);
          const parsed = out.trim().length > 0 ? JSON.parse(out) : [];
          const arr: any[] = Array.isArray(parsed)
            ? parsed
            : parsed?.results && Array.isArray(parsed.results)
              ? parsed.results
              : [];
          projectIds = arr.map((p: any) => String(p?.id)).filter((x) => x && x !== 'undefined');
          if (projectIds.length === 0) {
            throw new Error('plane --plane-scope all-projects: no projects discovered');
          }

          // Validate state name consistency: all mapped keys must exist in every project.
          const requiredNames = Object.keys(stageMap);
          for (const pid of projectIds) {
            const statesOut = await (adapterTmp as any).cli.run(['states', 'list', '-p', pid, '-f', 'json']);
            const statesParsed = statesOut.trim().length > 0 ? JSON.parse(statesOut) : [];
            const statesArr: any[] = Array.isArray(statesParsed)
              ? statesParsed
              : statesParsed?.results && Array.isArray(statesParsed.results)
                ? statesParsed.results
                : [];
            const names = new Set(statesArr.map((s: any) => String(s?.name)).filter(Boolean));
            const missing = requiredNames.filter((n) => !names.has(n));
            if (missing.length > 0) {
              throw new Error(`Plane state names mismatch for project ${pid}: missing ${missing.join(', ')}`);
            }
          }
        }

        adapterCfg = {
          kind: 'plane',
          workspaceSlug,
          projectId: scope === 'project' ? projectId : undefined,
          projectIds: scope === 'all-projects' ? projectIds : undefined,
          orderField: flags['plane-order-field'] ? String(flags['plane-order-field']) : undefined,
          stageMap,
        };
      } else if (adapterKind === 'planka') {
        const boardId = String(flags['planka-board-id'] ?? '').trim();
        const backlogListId = String(flags['planka-backlog-list-id'] ?? '').trim();
        if (!boardId) throw new Error('setup --adapter planka requires --planka-board-id <id>');
        if (!backlogListId) throw new Error('setup --adapter planka requires --planka-backlog-list-id <id>');

        adapterCfg = { kind: 'planka', boardId, backlogListId, stageMap };
      } else {
        throw new Error(`Unknown adapter kind: ${adapterKind}`);
      }

      const autopilotCronExpr = String(flags['autopilot-cron-expr'] ?? '*/5 * * * *').trim();
      const autopilotTz = flags['autopilot-cron-tz'] ? String(flags['autopilot-cron-tz']).trim() : undefined;
      const autopilotInstallCron = Boolean(flags['autopilot-install-cron']);

      await runSetup({
        fs,
        configPath,
        force,
        config: { version: 1, autopilot: { cronExpr: autopilotCronExpr, tz: autopilotTz || undefined }, adapter: adapterCfg },
        validate: async () => {
          // Validate ALL read-only verb prerequisites.
          const adapter = await adapterFromConfig(adapterCfg);
          await adapter.whoami();

          // next prerequisites
          await adapter.listBacklogIdsInOrder();
          await adapter.listIdsByStage('stage:backlog');
          await adapter.listIdsByStage('stage:blocked');
          await adapter.listIdsByStage('stage:in-progress');
          await adapter.listIdsByStage('stage:in-review');

          // show prerequisites (best-effort: validate on at least one work item if any exist)
          const candidates = [
            ...(await adapter.listIdsByStage('stage:backlog')),
            ...(await adapter.listIdsByStage('stage:blocked')),
            ...(await adapter.listIdsByStage('stage:in-progress')),
            ...(await adapter.listIdsByStage('stage:in-review')),
          ];

          const id = candidates[0];
          if (id) {
            await adapter.getWorkItem(id);
            await adapter.listComments(id, { limit: 1, newestFirst: true, includeInternal: true });
            await adapter.listAttachments(id);
            await adapter.listLinkedWorkItems(id);
          }
        },
      });

      io.stdout.write(`Wrote ${configPath}\n`);
      io.stdout.write(
        `Autopilot suggestion: schedule an OpenClaw cron job (expr: ${autopilotCronExpr}${autopilotTz ? `, tz: ${autopilotTz}` : ''}) to run \`kanban-workflow autopilot-tick\`.\n`,
      );

      if (autopilotInstallCron) {
        const tz = autopilotTz ?? '';
        const message = [
          'Autopilot tick (kanban-workflow):',
          '',
          '- Run: kanban-workflow autopilot-tick',
          '- If it starts a ticket, a separate always-on agent should do the actual work (read `show`, implement, `update`/`ask`, then `complete`).',
          '',
          'This job was created by `kanban-workflow setup --autopilot-install-cron`.',
        ].join('\n');

        const args = [
          'cron',
          'add',
          '--name',
          'kanban-workflow autopilot tick',
          '--session',
          'isolated',
          '--cron',
          autopilotCronExpr,
          '--exact',
          '--message',
          message,
          '--no-deliver',
          '--json',
        ];

        if (tz) {
          args.push('--tz', tz);
        }

        const out = await execa('openclaw', args);
        io.stdout.write(`Installed OpenClaw cron job: ${out.stdout.trim()}\n`);
      }

      writeWhatNext(io, cmd);
      return 0;
    }

    let config: any;
    try {
      config = await loadConfigFromFile({ fs, path: configPath });
    } catch {
      writeSetupRequiredError(io);
      return 1;
    }

    const adapter = await adapterFromConfig(config.adapter);

    if (cmd === 'show') {
      const id = String(flags.id ?? '');
      if (!id) throw new Error('show requires --id');
      io.stdout.write(`${JSON.stringify(await show(adapter, id), null, 2)}\n`);
      writeWhatNext(io, cmd);
      return 0;
    }

    if (cmd === 'autopilot-tick') {
      const res = await runAutopilotTick({ adapter, lock: lockfile, now: new Date() });
      io.stdout.write(`${JSON.stringify(res, null, 2)}\n`);
      writeWhatNext(io, cmd);
      return 0;
    }

    if (cmd === 'next') {
      io.stdout.write(`${JSON.stringify(await next(adapter), null, 2)}\n`);
      writeWhatNext(io, cmd);
      return 0;
    }

    if (cmd === 'start') {
      const id = String(flags.id ?? '');
      if (!id) throw new Error('start requires --id');
      await start(adapter, id);
      writeWhatNext(io, cmd);
      return 0;
    }

    if (cmd === 'update') {
      const id = String(flags.id ?? '');
      const text = String(flags.text ?? '');
      if (!id) throw new Error('update requires --id');
      if (!text) throw new Error('update requires --text');
      await update(adapter, id, text);
      writeWhatNext(io, cmd);
      return 0;
    }

    if (cmd === 'ask') {
      const id = String(flags.id ?? '');
      const text = String(flags.text ?? '');
      if (!id) throw new Error('ask requires --id');
      if (!text) throw new Error('ask requires --text');
      await ask(adapter, id, text);
      writeWhatNext(io, cmd);
      return 0;
    }

    if (cmd === 'complete') {
      const id = String(flags.id ?? '');
      const summary = String(flags.summary ?? '');
      if (!id) throw new Error('complete requires --id');
      if (!summary) throw new Error('complete requires --summary');
      await complete(adapter, id, summary);
      writeWhatNext(io, cmd);
      return 0;
    }

    if (cmd === 'create') {
      const title = String(flags.title ?? '');
      const body = String(flags.body ?? '');
      if (!title) throw new Error('create requires --title');
      io.stdout.write(`${JSON.stringify(await create(adapter, { title, body }), null, 2)}\n`);
      writeWhatNext(io, cmd);
      return 0;
    }

    io.stderr.write(`Unknown command: ${cmd}\n`);
    return 2;
  } catch (err: any) {
    io.stderr.write(`${err?.message ?? String(err)}\n`);
    return 1;
  }
}

async function adapterFromConfig(cfg: any): Promise<any> {
  switch (cfg.kind) {
    case 'github':
      return new GitHubAdapter({
        repo: cfg.repo,
        snapshotPath: 'data/github_snapshot.json',
        project: cfg.project,
        stageMap: cfg.stageMap,
      });
    case 'linear':
      return new LinearAdapter({ viewId: cfg.viewId, teamId: cfg.teamId, projectId: cfg.projectId, stageMap: cfg.stageMap });
    case 'plane':
      return new PlaneAdapter({
        workspaceSlug: cfg.workspaceSlug,
        projectId: cfg.projectId,
        projectIds: cfg.projectIds,
        orderField: cfg.orderField,
        stageMap: cfg.stageMap,
      });
    case 'planka':
      return new PlankaAdapter({ stageMap: cfg.stageMap, boardId: cfg.boardId, backlogListId: cfg.backlogListId, bin: cfg.bin });
    default:
      throw new Error(`Unknown adapter kind: ${cfg.kind}`);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  runCli(process.argv.slice(2)).then((code) => {
    process.exitCode = code;
  });
}
