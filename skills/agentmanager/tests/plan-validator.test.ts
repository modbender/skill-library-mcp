import { describe, expect, it } from 'vitest';
import type { Plan } from '../src/types.js';
import { validatePlan } from '../src/services/plan-validator.js';
import { ToolRegistry } from '../src/services/tools.js';

const basePlan = (): Plan => ({
  mode: 'single',
  rationale: 'base',
  budget: { max_steps: 5, max_tool_calls: 5, max_latency_ms: 5000, max_cost_estimate: 1, max_model_upgrades: 1 },
  invariants: [],
  success_criteria: [],
  output_contract: { type: 'json' },
  tasks: [
    {
      name: 'single_executor',
      agent: 'executor',
      input: 'compute',
      depends_on: [],
      tools_allowed: ['js_eval'],
      model: 'gpt-lite',
      reasoning_level: 'low',
      max_output_tokens: 30
    }
  ]
});

describe('validatePlan', () => {
  it('rejects cycles deterministically', () => {
    const plan = basePlan();
    plan.mode = 'multi';
    plan.tasks = [
      { ...plan.tasks[0], name: 'a', depends_on: ['b'] },
      { ...plan.tasks[0], name: 'b', depends_on: ['a'] }
    ];

    expect(() => validatePlan(plan, new ToolRegistry())).toThrow('Cycle detected');
  });

  it('rejects unknown tools', () => {
    const plan = basePlan();
    plan.tasks[0].tools_allowed = ['unknown_tool'];
    expect(() => validatePlan(plan, new ToolRegistry())).toThrow('unknown tool');
  });

  it('rejects invalid output contract schema', () => {
    const plan = basePlan();
    plan.output_contract = {
      type: 'json',
      schema: {
        type: 'object',
        properties: { name: { type: 'string' } },
        required: 'name'
      } as unknown as Record<string, unknown>
    };

    expect(() => validatePlan(plan, new ToolRegistry())).toThrow('Invalid output_contract JSON Schema');
  });

});
