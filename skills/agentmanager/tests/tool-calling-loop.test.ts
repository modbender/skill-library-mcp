import { describe, expect, it } from 'vitest';
import { ExecutionEngine } from '../src/services/engine.js';
import { ToolRegistry } from '../src/services/tools.js';
import type { Plan, Run } from '../src/types.js';

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

const pricing = { maxTierCap: 'premium' as const, tierPricePerToken: { cheap: 0.000001, standard: 0.000003, premium: 0.000008 } };

describe('provider-driven tool-calling loop', () => {
  it('executes tool call loop and emits llm/tool events', async () => {
    const plan: Plan = {
      mode: 'single',
      rationale: 'tool loop',
      budget: { max_steps: 3, max_tool_calls: 2, max_latency_ms: 3000, max_cost_estimate: 1, max_model_upgrades: 1 },
      invariants: [],
      success_criteria: [],
      output_contract: { type: 'json' },
      tasks: [
        {
          name: 'single_executor',
          agent: 'executor',
          input: 'needs_tool:js_eval',
          depends_on: [],
          tools_allowed: ['js_eval'],
          model: 'gpt-lite',
          reasoning_level: 'low',
          max_output_tokens: 64
        }
      ]
    };

    const run = await new ExecutionEngine(new ToolRegistry()).executeRun(buildRun('run-tool-loop', plan), { tokenOwner: 'owner', pricing });
    expect(run.status).toBe('succeeded');
    expect(run.metrics.tool_calls).toBe(1);
    expect(run.results_by_task.single_executor.meta?.tool_calls).toBe(1);
    const eventTypes = run.logs.map((e) => e.type);
    expect(eventTypes).toContain('llm_step_start');
    expect(eventTypes).toContain('llm_step_tool_calls');
    expect(eventTypes).toContain('tool_call_start');
    expect(eventTypes).toContain('tool_call_end');
    expect(eventTypes).toContain('llm_step_final');
    expect(eventTypes).toContain('llm_round_start');
    expect(eventTypes).toContain('llm_round_final');
    const llmStart = run.logs.find((e) => e.type === 'llm_step_start');
    expect(typeof llmStart?.data?.request_id).toBe('string');
  });

  it('stops on max_tool_calls budget during tool loop', async () => {
    const plan: Plan = {
      mode: 'single',
      rationale: 'tool budget',
      budget: { max_steps: 3, max_tool_calls: 0, max_latency_ms: 3000, max_cost_estimate: 1, max_model_upgrades: 1 },
      invariants: [],
      success_criteria: [],
      output_contract: { type: 'json' },
      tasks: [
        {
          name: 'single_executor',
          agent: 'executor',
          input: 'needs_tool:js_eval',
          depends_on: [],
          tools_allowed: ['js_eval'],
          model: 'gpt-lite',
          reasoning_level: 'low',
          max_output_tokens: 64
        }
      ]
    };

    const run = await new ExecutionEngine(new ToolRegistry()).executeRun(buildRun('run-tool-budget', plan), { tokenOwner: 'owner', pricing });
    expect(run.status).toBe('failed');
    expect(run.error?.code).toBe('BUDGET_TOOL_CALLS');
    expect(run.logs.some((e) => e.type === 'budget_violation')).toBe(true);
  });

  it('appends exactly one tool result per tool_call_id before next round', async () => {
    const plan: Plan = {
      mode: 'single',
      rationale: 'tool pair protocol',
      budget: { max_steps: 3, max_tool_calls: 4, max_latency_ms: 3000, max_cost_estimate: 1, max_model_upgrades: 1 },
      invariants: [],
      success_criteria: [],
      output_contract: { type: 'json' },
      tasks: [
        {
          name: 'single_executor',
          agent: 'executor',
          input: 'needs_tool_pair',
          depends_on: [],
          tools_allowed: ['js_eval'],
          model: 'gpt-lite',
          reasoning_level: 'low',
          max_output_tokens: 64
        }
      ]
    };

    const run = await new ExecutionEngine(new ToolRegistry()).executeRun(buildRun('run-tool-pair', plan), { tokenOwner: 'owner', pricing });
    expect(run.status).toBe('succeeded');
    const starts = run.logs.filter((e) => e.type === 'tool_call_start').map((e) => String(e.data?.tool_call_id));
    const ends = run.logs.filter((e) => e.type === 'tool_call_end').map((e) => String(e.data?.tool_call_id));
    expect(starts.sort()).toEqual(['single_executor-pair-1', 'single_executor-pair-2']);
    expect(ends.sort()).toEqual(['single_executor-pair-1', 'single_executor-pair-2']);
  });
});
