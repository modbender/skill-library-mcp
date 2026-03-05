import { z } from 'zod';

import { Stage, StageKeySchema } from './stage.js';

export type JsonObject = Record<string, unknown>;

export interface WorkItem {
  id: string;
  title: string;
  stage: Stage;
  url?: string;
  labels: readonly string[];
  updatedAt?: Date;
  raw: JsonObject;
}

export const WorkItemSchema = z.object({
  id: z.string().min(1),
  title: z.string().min(1),
  stage: z
    .object({
      key: StageKeySchema,
    })
    .transform((s) => Stage.fromAny(s.key)),
  url: z.string().url().optional(),
  labels: z.array(z.string()).default([]),
  updatedAt: z.coerce.date().optional(),
  raw: z.record(z.unknown()).default({}),
});
