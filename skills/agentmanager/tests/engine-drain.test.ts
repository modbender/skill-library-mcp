import { describe, expect, it } from 'vitest';
import { ExecutionEngine } from '../src/services/engine.js';
import { ToolRegistry } from '../src/services/tools.js';
import type { Plan, Run } from '../src/types.js';

const buildRun = (plan: Plan): Run => ({
  id: 'run-drain',
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

describe('engine in-flight drain on budget violation', () => {
  it('drains in-flight tasks without unhandled rejections', async () => {
    const plan: Plan = {
      mode: 'multi',
      rationale: 'drain regression',
      budget: { max_steps: 5, max_tool_calls: 0, max_latency_ms: 3000, max_cost_estimate: 10, max_model_upgrades: 1 },
      invariants: [],
      success_criteria: [],
      output_contract: { type: 'json' },
      tasks: [
        {
          name: 'executor_a',
          agent: 'executor',
          input: 'needs_tool:js_eval',
          depends_on: [],
          tools_allowed: ['js_eval'],
          model: 'gpt-lite',
          reasoning_level: 'low',
          max_output_tokens: 32
        },
        {
          name: 'executor_b',
          agent: 'executor',
          input: 'slow_ms_800 compute',
          depends_on: [],
          tools_allowed: [],
          model: 'gpt-lite',
          reasoning_level: 'low',
          max_output_tokens: 32
        }
      ]
    };

    const engine = new ExecutionEngine(new ToolRegistry());
    const pricing = { maxTierCap: 'premium' as const, tierPricePerToken: { cheap: 0.000001, standard: 0.000003, premium: 0.000008 } };

    let unhandled = 0;
    const onUnhandled = () => {
      unhandled += 1;
    };
    process.on('unhandledRejection', onUnhandled);

    try {
      const run = await engine.executeRun(buildRun(plan), { tokenOwner: 'owner', pricing, maxConcurrency: 2 });
      await new Promise<void>((resolve) => setImmediate(resolve));
      expect(unhandled).toBe(0);
      expect(run.status).toBe('failed');
      expect(run.error?.code).toBe('BUDGET_TOOL_CALLS');
    } finally {
      process.off('unhandledRejection', onUnhandled);
    }
  });
});
