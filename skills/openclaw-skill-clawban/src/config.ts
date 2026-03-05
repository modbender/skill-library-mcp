import { z } from 'zod';

import { CANONICAL_STAGE_KEYS, StageKeySchema } from './stage.js';

const StageMapSchema = z
  .record(z.string().min(1), StageKeySchema)
  .superRefine((map, ctx) => {
    const values = new Set(Object.values(map));
    for (const key of CANONICAL_STAGE_KEYS) {
      if (!values.has(key)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: `stageMap must include a mapping for canonical stage ${key}`,
        });
      }
    }
  });

export const ClawbanConfigV1Schema = z.object({
  version: z.literal(1),
  autopilot: z
    .object({
      /** Cron expression for triggering a single autopilot tick. */
      cronExpr: z.string().min(1).default('*/5 * * * *'),
      /** Optional timezone for cron evaluation (e.g. Europe/Berlin). */
      tz: z.string().min(1).optional(),
    })
    .optional(),
  adapter: z.discriminatedUnion('kind', [
    z.object({
      kind: z.literal('github'),
      repo: z.string().min(1),
      /** Explicit ordering source: GitHub Project number (optional). */
      project: z
        .object({
          number: z.number().int().positive(),
          owner: z.string().min(1),
        })
        .optional(),
      stageMap: StageMapSchema,
    }),
    z.object({
      kind: z.literal('linear'),
      /** Explicit ordering via Linear view id (manual view order). */
      viewId: z.string().optional(),
      /** Provide either teamId OR projectId when viewId is not provided (exactly one). */
      teamId: z.string().optional(),
      projectId: z.string().optional(),
      stageMap: StageMapSchema,
    }),
    z.object({
      kind: z.literal('plane'),
      workspaceSlug: z.string().min(1),
      /** Single project scope (legacy). */
      projectId: z.string().min(1).optional(),
      /** Multi-project scope (preferred for autopilot). */
      projectIds: z.array(z.string().min(1)).optional(),
      /** Explicit ordering field name when UI order can't be discovered. */
      orderField: z.string().min(1).optional(),
      stageMap: StageMapSchema,
    }),
    z.object({
      kind: z.literal('planka'),
      /** Board scope for listing cards. */
      boardId: z.string().min(1),
      /** Needed for explicit backlog ordering by card position. */
      backlogListId: z.string().min(1),
      bin: z.string().optional(),
      stageMap: StageMapSchema,
    }),
  ]),
});

export type ClawbanConfigV1 = z.infer<typeof ClawbanConfigV1Schema>;

export type ClawbanConfig = ClawbanConfigV1;
export const ClawbanConfigSchema = ClawbanConfigV1Schema;

export type FsLike = {
  readFile(path: string, encoding: 'utf-8'): Promise<string>;
  writeFile(path: string, content: string, encoding: 'utf-8'): Promise<void>;
  mkdir(path: string, opts: { recursive: boolean }): Promise<void>;
};

export async function loadConfigFromFile(opts: {
  fs: FsLike;
  path: string;
}): Promise<ClawbanConfig> {
  const text = await opts.fs.readFile(opts.path, 'utf-8');
  const parsed = JSON.parse(text);
  return ClawbanConfigSchema.parse(parsed);
}

export async function writeConfigToFile(opts: {
  fs: FsLike;
  path: string;
  config: ClawbanConfig;
}): Promise<void> {
  const dir = opts.path.split('/').slice(0, -1).join('/') || '.';
  await opts.fs.mkdir(dir, { recursive: true });
  await opts.fs.writeFile(opts.path, `${JSON.stringify(opts.config, null, 2)}\n`, 'utf-8');
}
