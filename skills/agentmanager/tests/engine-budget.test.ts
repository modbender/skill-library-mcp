import { describe, expect, it } from 'vitest';
import type { Plan, Run } from '../src/types.js';
import { ExecutionEngine } from '../src/services/engine.js';
import { ToolRegistry } from '../src/services/tools.js';

const baseRun = (plan: Plan): Run => ({
  id: 'run-budget',
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

describe('engine step budget durability', () => {
  it('does not bypass max_steps via fallback reset', async () => {
    const plan: Plan = {
      mode: 'multi',
      rationale: 'force fallback with strict steps',
      budget: { max_steps: 1, max_tool_calls: 10, max_latency_ms: 10000, max_cost_estimate: 1, max_model_upgrades: 1 },
      invariants: [],
      success_criteria: [],
      output_contract: { type: 'json' },
      tasks: [
        { name: 'triage', agent: 'triage', input: 'a', depends_on: [], tools_allowed: [], model: 'gpt-lite', reasoning_level: 'low', max_output_tokens: 10 },
        { name: 'planner', agent: 'planner', input: 'b', depends_on: ['triage'], tools_allowed: [], model: 'gpt-standard', reasoning_level: 'low', max_output_tokens: 10 },
        { name: 'executor_a', agent: 'executor', input: 'c', depends_on: ['planner'], tools_allowed: [], model: 'gpt-lite', reasoning_level: 'low', max_output_tokens: 10 },
        { name: 'executor_b', agent: 'executor', input: 'd', depends_on: ['planner'], tools_allowed: [], model: 'gpt-lite', reasoning_level: 'low', max_output_tokens: 10 },
        { name: 'verifier', agent: 'verifier', input: 'e', depends_on: ['executor_a', 'executor_b'], tools_allowed: [], model: 'gpt-premium', reasoning_level: 'high', max_output_tokens: 10 }
      ]
    };

    const engine = new ExecutionEngine(new ToolRegistry());
    const run = await engine.executeRun(baseRun(plan), {
      tokenOwner: 'owner',
      pricing: { maxTierCap: 'premium', tierPricePerToken: { cheap: 0.000001, standard: 0.000003, premium: 0.000008 } }
    });

    expect(run.status).toBe('failed');
    expect(run.error?.code).toBe('BUDGET_STEPS');
    expect(run.metrics.steps_executed_total).toBe(1);
    expect(run.metrics.fallback).toBe(true);
  });
});
