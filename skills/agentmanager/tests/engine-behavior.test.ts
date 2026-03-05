import { describe, expect, it } from 'vitest';
import { ExecutionEngine } from '../src/services/engine.js';
import { ToolRegistry } from '../src/services/tools.js';
import type { LLMProvider, LLMTaskContext, LLMTaskStepResult } from '../src/providers/llm-provider.js';
import type { Plan, Run, TaskSpec } from '../src/types.js';

const pricing = { maxTierCap: 'premium' as const, tierPricePerToken: { cheap: 0.000001, standard: 0.000003, premium: 0.000008 } };

const buildRun = (id: string, plan: Plan): Run => ({
  id,
  created_at: Date.now(),
  status: 'queued',
  plan,
  results_by_task: {},
  logs_base: 0,
  logs: [],
  progress: { total_tasks: plan.tasks.length, completed_tasks: 0, running_tasks: 0, queued_tasks: plan.tasks.length },
  metrics: {
    total_ms: 0,
    tasks_ms: {},
    tool_calls: 0,
    retries: 0,
    fallback: false,
    model_upgrades: 0,
    cost_estimate: 0,
    cost_estimate_committed: 0,
    cost_estimate_failed: 0,
    artifacts_bytes: 0,
    events_truncated: false,
    steps_executed_total: 0
  }
});

const singleTaskPlan = (task: TaskSpec): Plan => ({
  mode: 'single',
  rationale: 'single task',
  budget: { max_steps: 3, max_tool_calls: 5, max_latency_ms: 5000, max_cost_estimate: 5, max_model_upgrades: 0 },
  invariants: [],
  success_criteria: [],
  output_contract: { type: 'json' },
  tasks: [{ ...task, depends_on: [] }]
});

class CaptureProvider implements LLMProvider {
  readonly id = 'capture';
  public systemContent = '';

  async step(_task: TaskSpec, context: LLMTaskContext): Promise<LLMTaskStepResult> {
    this.systemContent = context.messages[0]?.content ?? '';
    return { type: 'final', payload: { ok: true } };
  }
}

class RetryProvider implements LLMProvider {
  readonly id = 'retry';

  async step(): Promise<LLMTaskStepResult> {
    throw { code: 'TEMP_FAIL', message: 'temporary failure', retryable: true, suggested_action: 'retry', at: 'provider' };
  }
}

describe('engine behavior', () => {
  it('uses task.system_prompt as the system message', async () => {
    const provider = new CaptureProvider();
    const task: TaskSpec = {
      name: 'single_executor',
      agent: 'executor',
      input: 'hello',
      depends_on: [],
      tools_allowed: [],
      model: 'gpt-lite',
      reasoning_level: 'low',
      max_output_tokens: 64,
      system_prompt: 'System prompt override'
    };

    const run = await new ExecutionEngine(new ToolRegistry(), provider).executeRun(buildRun('run-system-prompt', singleTaskPlan(task)), { tokenOwner: 'owner', pricing });
    expect(run.status).toBe('succeeded');
    expect(provider.systemContent).toBe('System prompt override');
  });

  it('uses exponential retry backoff delays', async () => {
    const provider = new RetryProvider();
    const task: TaskSpec = {
      name: 'single_executor',
      agent: 'executor',
      input: 'hello',
      depends_on: [],
      tools_allowed: [],
      model: 'gpt-lite',
      reasoning_level: 'low',
      max_output_tokens: 64
    };

    const started = Date.now();
    const run = await new ExecutionEngine(new ToolRegistry(), provider).executeRun(buildRun('run-retry-backoff', singleTaskPlan(task)), { tokenOwner: 'owner', pricing });
    const elapsed = Date.now() - started;

    expect(run.status).toBe('failed');
    expect(run.metrics.retries).toBeGreaterThanOrEqual(3);
    expect(elapsed).toBeGreaterThanOrEqual(55);
  });
});
