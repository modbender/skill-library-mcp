import { z } from 'zod'

export const TaskRecordSchema = z.object({
  task_id: z.string().regex(/^tsk_[a-zA-Z0-9]{12,}$/),
  parent_task_id: z.string().nullable().default(null),
  started_at: z.string().datetime(),
  completed_at: z.string().datetime().nullable().default(null),
  status: z.enum(['in_progress', 'completed', 'failed', 'abandoned']),
  complexity_score: z.number().int().min(0).max(100).default(0),
  complexity_level: z.enum(['L1', 'L2', 'L3', 'L4']).default('L1'),
  quality_score: z.number().min(0).max(1).default(0),
  total_tokens: z.number().int().nonnegative().default(0),
  total_cost_usd: z.number().nonnegative().default(0),
  tes: z.number().nullable().default(null),
  models_used: z.array(z.string()).default([]),
  sessions: z.array(z.string()).default([]),
  sub_agents: z.number().int().nonnegative().default(0),
  cron_id: z.string().nullable().default(null),
  cron_triggered: z.boolean().default(false),
  tools_called: z.number().int().nonnegative().default(0),
  tool_names: z.array(z.string()).default([]),
  external_api_calls: z.number().int().nonnegative().default(0),
  user_turns: z.number().int().nonnegative().default(0),
  intent_summary: z.string().default(''),
  outcome_summary: z.string().default(''),
})

/**
 * Factory function to create a TaskRecord with defaults.
 * @param {Partial<z.infer<typeof TaskRecordSchema>>} partial
 */
export function createTaskRecord(partial) {
  return TaskRecordSchema.parse({
    task_id: partial.task_id ?? `tsk_${randomId()}`,
    started_at: partial.started_at ?? new Date().toISOString(),
    status: partial.status ?? 'in_progress',
    ...partial,
  })
}

function randomId(len = 16) {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
  return Array.from({ length: len }, () => chars[Math.floor(Math.random() * chars.length)]).join('')
}
