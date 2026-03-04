import { z } from 'zod';

export const JsonSchemaZod = z.record(z.any());

export const ToolSpecSchema = z.object({
  name: z.string().min(1),
  description: z.string().min(1),
  input_schema: JsonSchemaZod,
  timeout_ms: z.number().int().positive(),
  tags: z.array(z.string()),
  callback_url: z.string().url().optional(),
  auth_ref: z.string().min(1).optional()
});

export const AgentRoleSchema = z.string().min(1);
export const ReasoningLevelSchema = z.enum(['low', 'medium', 'high']);

export const TaskSpecSchema = z.object({
  name: z.string().min(1),
  agent: AgentRoleSchema,
  input: z.union([
    z.string(),
    z.object({
      text: z.string().optional(),
      user_request_ref: z.string().optional(),
      refs: z.array(z.object({ task: z.string().min(1), path: z.string().optional(), as: z.string().optional() })).optional(),
      instructions: z.string().optional(),
      payload: z.any().optional()
    })
  ]),
  depends_on: z.array(z.string()),
  parallel_group: z.string().nullable().optional(),
  tools_allowed: z.array(z.string()),
  model: z.string().min(1),
  reasoning_level: ReasoningLevelSchema,
  max_output_tokens: z.number().int().positive(),
  timeout_ms: z.number().int().positive().optional(),
  system_prompt: z.string().optional(),
  provider_id: z.string().min(1).optional()
});

export const PlanSchema = z.object({
  mode: z.enum(['single', 'multi']),
  rationale: z.string(),
  budget: z.object({
    max_steps: z.number().int().positive(),
    max_tool_calls: z.number().int().nonnegative(),
    max_latency_ms: z.number().int().positive(),
    max_cost_estimate: z.number().nonnegative(),
    max_model_upgrades: z.number().int().nonnegative()
  }),
  invariants: z.array(z.string()),
  success_criteria: z.array(z.string()),
  tasks: z.array(TaskSpecSchema),
  output_contract: z.object({
    type: z.enum(['json', 'text']),
    schema: JsonSchemaZod.optional()
  })
});

export const RunErrorSchema = z.object({
  code: z.string(),
  message: z.string(),
  retryable: z.boolean(),
  suggested_action: z.enum(['retry', 'upgrade', 'downgrade', 'replan']).optional(),
  at: z.string().optional()
});

export const RunStatusSchema = z.enum(['queued', 'running', 'succeeded', 'failed']);

export const TaskResultSchema = z.object({
  payload: z.any().optional(),
  payload_ref: z.string().optional(),
  digest_text: z.string(),
  digest_hash: z.string(),
  digest: z.string().optional(),
  evidence: z.array(z.any()).optional(),
  meta: z.object({
    model: z.string(),
    tier: z.enum(['cheap', 'standard', 'premium']),
    tokens_est: z.number(),
    cost_est: z.number(),
    tool_calls: z.number().int().nonnegative()
  }).optional()
});

export const RunProgressSchema = z.object({
  total_tasks: z.number().int().nonnegative(),
  completed_tasks: z.number().int().nonnegative(),
  running_tasks: z.number().int().nonnegative(),
  queued_tasks: z.number().int().nonnegative()
});

export const RunEventSchema = z.object({
  seq: z.number().int().positive(),
  ts: z.number(),
  type: z.string(),
  run_id: z.string(),
  task_name: z.string().optional(),
  data: z.record(z.any()).optional()
});

export const RunSchema = z.object({
  id: z.string(),
  created_at: z.number(),
  status: RunStatusSchema,
  plan: PlanSchema,
  results_by_task: z.record(TaskResultSchema),
  final_output: z.any().optional(),
  output_digest: z.string().optional(),
  progress: RunProgressSchema,
  logs_base: z.number().int().nonnegative(),
  logs: z.array(RunEventSchema),
  token_owner: z.string().optional(),
  injected_tasks: z.record(z.object({ payload: z.any(), meta: z.any().optional() })).optional(),
  metrics: z.object({
    total_ms: z.number(),
    tasks_ms: z.record(z.number()),
    tool_calls: z.number(),
    retries: z.number(),
    fallback: z.boolean(),
    model_upgrades: z.number(),
    cost_estimate: z.number(),
    cost_estimate_committed: z.number(),
    cost_estimate_failed: z.number(),
    artifacts_bytes: z.number(),
    events_truncated: z.boolean(),
    steps_executed_total: z.number().int().nonnegative(),
    cost_breakdown: z.record(z.object({
      cost_est: z.number(),
      tier: z.string(),
      tool_calls: z.number()
    })).optional()
  }),
  error: RunErrorSchema.optional()
});

export const BudgetLevelSchema = z.enum(['cheap', 'normal', 'thorough']);
export const GoalTypeSchema = z.enum(['answer', 'code', 'analysis', 'tooling']);
export const RiskLevelSchema = z.enum(['low', 'medium', 'high']);
export const ToolPreferenceSchema = z.enum(['avoid', 'allow', 'prefer']);

export const PlanOptionsSchema = z.object({
  budget_level: BudgetLevelSchema.optional(),
  strategy_hint: z.string().min(1).optional(),
  goal_type: GoalTypeSchema.optional(),
  risk_level: RiskLevelSchema.optional(),
  must_verify: z.boolean().optional(),
  tool_preference: ToolPreferenceSchema.optional(),
  latency_hint_ms: z.number().int().positive().optional(),
  max_cost_override: z.number().positive().optional(),
  provider_id: z.string().min(1).optional()
});

export const PlanRequestSchema = z.object({
  user_request: z.string().min(1),
  options: PlanOptionsSchema.optional()
});

export const RunRequestSchema = z.object({
  user_request: z.string().min(1).optional(),
  plan: PlanSchema.optional(),
  idempotency_key: z.string().optional(),
  options: PlanOptionsSchema.extend({
    max_concurrency: z.number().int().positive().max(32).optional(),
    dry_run: z.boolean().optional()
  }).optional()
}).refine((value) => Boolean(value.user_request || value.plan), {
  message: 'either user_request or plan is required',
  path: ['user_request']
});

export type ToolSpec = z.infer<typeof ToolSpecSchema>;
export type TaskSpec = z.infer<typeof TaskSpecSchema>;
export type Plan = z.infer<typeof PlanSchema>;
export type Run = z.infer<typeof RunSchema>;
export type RunError = z.infer<typeof RunErrorSchema>;
export type BudgetLevel = z.infer<typeof BudgetLevelSchema>;
export type RunEvent = z.infer<typeof RunEventSchema>;
export type PlanOptions = z.infer<typeof PlanOptionsSchema>;
