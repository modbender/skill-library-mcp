import { z } from 'zod';

import { WorkItemSchema } from './models.js';
import { StageKeySchema } from './stage.js';

export const WorkItemCreatedSchema = z.object({
  type: z.literal('WorkItemCreated'),
  workItem: WorkItemSchema,
});
export type WorkItemCreated = z.infer<typeof WorkItemCreatedSchema>;

export const WorkItemDeletedSchema = z.object({
  type: z.literal('WorkItemDeleted'),
  workItemId: z.string().min(1),
});
export type WorkItemDeleted = z.infer<typeof WorkItemDeletedSchema>;

export const StageChangedSchema = z.object({
  type: z.literal('StageChanged'),
  workItemId: z.string().min(1),
  old: z.object({ key: StageKeySchema }),
  new: z.object({ key: StageKeySchema }),
});
export type StageChanged = z.infer<typeof StageChangedSchema>;

export const WorkItemUpdatedSchema = z.object({
  type: z.literal('WorkItemUpdated'),
  workItemId: z.string().min(1),
});
export type WorkItemUpdated = z.infer<typeof WorkItemUpdatedSchema>;

export const EventSchema = z.discriminatedUnion('type', [
  WorkItemCreatedSchema,
  WorkItemDeletedSchema,
  StageChangedSchema,
  WorkItemUpdatedSchema,
]);

export type Event = z.infer<typeof EventSchema>;
