import type { BudgetLevel, Plan, PlanOptions } from '../types.js';
import { PlannerService } from './planner.js';

const baseTimeoutByBudget = (budget: BudgetLevel): number => ({ cheap: 8_000, normal: 20_000, thorough: 45_000 })[budget];

export interface PlannerStrategy {
  id: string;
  description: string;
  createPlan(userRequest: string, budgetLevel: BudgetLevel, options?: PlanOptions): Plan;
}

class HeuristicStrategy implements PlannerStrategy {
  id = 'heuristic_v1';
  description = 'Default heuristic strategy balancing quality and cost by request complexity.';
  private readonly planner = new PlannerService();

  createPlan(userRequest: string, budgetLevel: BudgetLevel, options?: PlanOptions): Plan {
    let plan = this.planner.createPlan(userRequest, budgetLevel);

    if (options?.tool_preference === 'avoid') {
      plan = { ...plan, tasks: plan.tasks.map((t) => ({ ...t, tools_allowed: [] })) };
    }

    if (options?.must_verify && !plan.tasks.some((t) => t.agent === 'verifier')) {
      const executor = plan.tasks[0];
      plan = {
        ...plan,
        mode: 'multi',
        tasks: [
          { ...executor, name: 'single_executor', depends_on: [] },
          {
            name: 'verifier',
            agent: 'verifier',
            input: 'Validate single executor result',
            depends_on: ['single_executor'],
            tools_allowed: [],
            model: executor.model,
            reasoning_level: 'high',
            max_output_tokens: 220,
            timeout_ms: Math.min(executor.timeout_ms ?? 20_000, baseTimeoutByBudget(budgetLevel))
          }
        ]
      };
    }

    if (options?.max_cost_override) {
      plan = { ...plan, budget: { ...plan.budget, max_cost_estimate: options.max_cost_override } };
    }
    if (options?.latency_hint_ms) {
      plan = { ...plan, budget: { ...plan.budget, max_latency_ms: Math.min(plan.budget.max_latency_ms, options.latency_hint_ms) } };
    }

    return plan;
  }
}

class SafeMinimalV2Strategy implements PlannerStrategy {
  id = 'safe_minimal_v2';
  description = 'Safety-first strategy: prefers single mode, reduced token budgets, and avoids tools unless explicitly preferred.';
  private readonly planner = new PlannerService();

  createPlan(userRequest: string, budgetLevel: BudgetLevel, options?: PlanOptions): Plan {
    const highComplexity = userRequest.length > 420 || /(parallel|verify|analyze|complex|multi)/i.test(userRequest);
    const mustMulti = Boolean(options?.must_verify || highComplexity);

    if (!mustMulti) {
      return {
        mode: 'single',
        rationale: 'safe_minimal_v2 selected single execution path.',
        budget: this.planner.createPlan(userRequest, budgetLevel).budget,
        invariants: ['Stay under strict budget bounds'],
        success_criteria: ['Produce valid output'],
        tasks: [
          {
            name: 'single_executor',
            agent: 'executor',
            input: userRequest,
            depends_on: [],
            tools_allowed: options?.tool_preference === 'prefer' ? ['js_eval'] : [],
            model: 'gpt-lite',
            reasoning_level: 'low',
            max_output_tokens: 180,
            timeout_ms: baseTimeoutByBudget(budgetLevel)
          }
        ],
        output_contract: { type: 'json', schema: { type: 'object' } }
      };
    }

    const base = this.planner.createPlan(userRequest, budgetLevel);
    const toolsAllowed = options?.tool_preference === 'prefer' ? ['js_eval'] : [];

    return {
      ...base,
      mode: 'multi',
      tasks: base.tasks.map((task) => {
        if (task.agent === 'executor') {
          return { ...task, tools_allowed: toolsAllowed, max_output_tokens: Math.min(task.max_output_tokens, 220) };
        }
        return { ...task, max_output_tokens: Math.min(task.max_output_tokens, 220) };
      })
    };
  }
}

export class StrategyRegistry {
  private readonly strategies = new Map<string, PlannerStrategy>();
  readonly defaultStrategyId = 'heuristic_v1';

  constructor() {
    this.register(new HeuristicStrategy());
    this.register(new SafeMinimalV2Strategy());
  }

  register(strategy: PlannerStrategy): void {
    this.strategies.set(strategy.id, strategy);
  }

  get(id: string): PlannerStrategy | undefined {
    return this.strategies.get(id);
  }

  list(): Array<{ id: string; description: string }> {
    return [...this.strategies.values()].map((s) => ({ id: s.id, description: s.description }));
  }
}
