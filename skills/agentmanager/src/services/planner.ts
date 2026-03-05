import type { BudgetLevel, Plan, TaskSpec } from '../types.js';
import { PlanSchema } from '../types.js';

const budgetByLevel: Record<BudgetLevel, Plan['budget']> = {
  cheap: { max_steps: 4, max_tool_calls: 2, max_latency_ms: 15_000, max_cost_estimate: 0.02, max_model_upgrades: 1 },
  normal: { max_steps: 8, max_tool_calls: 6, max_latency_ms: 35_000, max_cost_estimate: 0.08, max_model_upgrades: 2 },
  thorough: { max_steps: 12, max_tool_calls: 12, max_latency_ms: 60_000, max_cost_estimate: 0.2, max_model_upgrades: 4 }
};

const taskTimeoutByBudget: Record<BudgetLevel, number> = {
  cheap: 8_000,
  normal: 20_000,
  thorough: 45_000
};

const kCompute = /(calculate|compute|analy[sz]e|algorithm|derive|optimi[sz]e)/i;
const kVerify = /(verify|validate|proof|test|assert|check)/i;
const kExternal = /(file|tool|api|web|search|database|js|script|store)/i;
const kMultiGoal = /( and |also|;|\n-)/i;

export class PlannerService {
  createPlan(userRequest: string, budgetLevel: BudgetLevel): Plan {
    const complexity = this.complexity(userRequest);
    const mode = complexity >= 3 ? 'multi' : 'single';
    const plan = mode === 'multi' ? this.multiPlan(userRequest, budgetLevel, complexity) : this.singlePlan(userRequest, budgetLevel, complexity);
    return PlanSchema.parse(plan);
  }

  private complexity(input: string): number {
    let score = input.length > 240 ? 1 : 0;
    if (kMultiGoal.test(input)) score += 1;
    if (kCompute.test(input)) score += 1;
    if (kVerify.test(input)) score += 1;
    if (kExternal.test(input)) score += 1;
    return score;
  }

  private singlePlan(userRequest: string, budgetLevel: BudgetLevel, complexity: number): Plan {
    const tasks: TaskSpec[] = [{
      name: 'single_executor',
      agent: 'executor',
      input: userRequest,
      depends_on: [],
      tools_allowed: kExternal.test(userRequest) ? ['file_store', 'js_eval'] : ['js_eval'],
      model: 'gpt-lite',
      reasoning_level: complexity >= 2 ? 'medium' : 'low',
      max_output_tokens: 500,
      timeout_ms: taskTimeoutByBudget[budgetLevel]
    }];

    return {
      mode: 'single',
      rationale: `Low complexity (${complexity}) request selected single executor flow.`,
      budget: budgetByLevel[budgetLevel],
      invariants: ['Never exceed budget hard limits', 'Must produce digest for output'],
      success_criteria: ['Output contract validates', 'No budget violation'],
      tasks,
      output_contract: { type: 'json', schema: { type: 'object' } }
    };
  }

  private multiPlan(userRequest: string, budgetLevel: BudgetLevel, complexity: number): Plan {
    const tools = kExternal.test(userRequest) ? ['file_store', 'js_eval'] : ['js_eval'];
    const timeout = taskTimeoutByBudget[budgetLevel];
    const tasks: TaskSpec[] = [
      {
        name: 'triage',
        agent: 'triage',
        input: userRequest,
        depends_on: [],
        tools_allowed: [],
        model: 'gpt-lite',
        reasoning_level: 'low',
        max_output_tokens: 250,
        timeout_ms: timeout
      },
      {
        name: 'planner',
        agent: 'planner',
        input: 'Use triage digest to produce a concrete execution outline, expected JSON fields, and distinct executor stream goals.',
        depends_on: ['triage'],
        tools_allowed: [],
        model: 'gpt-standard',
        reasoning_level: 'medium',
        max_output_tokens: 350,
        timeout_ms: timeout
      },
      {
        name: 'executor_a',
        agent: 'executor',
        input: `Execute stream A for: ${userRequest}. Focus on a direct solution path and primary constraints.`,
        depends_on: ['planner'],
        parallel_group: 'execute',
        tools_allowed: tools,
        model: 'gpt-lite',
        reasoning_level: 'medium',
        max_output_tokens: 500,
        timeout_ms: timeout
      },
      {
        name: 'executor_b',
        agent: 'executor',
        input: `Execute stream B for: ${userRequest}. Focus on alternative strategy, edge-cases, and risk checks.`,
        depends_on: ['planner'],
        parallel_group: 'execute',
        tools_allowed: tools,
        model: 'gpt-lite',
        reasoning_level: complexity > 3 ? 'high' : 'medium',
        max_output_tokens: 500,
        timeout_ms: timeout
      },
      {
        name: 'verifier',
        agent: 'verifier',
        input: 'Validate all executor digests and ensure criteria',
        depends_on: ['executor_a', 'executor_b'],
        tools_allowed: [],
        model: 'gpt-premium',
        reasoning_level: 'high',
        max_output_tokens: 300,
        timeout_ms: timeout
      }
    ];

    return {
      mode: 'multi',
      rationale: `Complexity score ${complexity} triggered multi-agent route.`,
      budget: budgetByLevel[budgetLevel],
      invariants: ['Planner must run after triage', 'Verifier must run after all executors', 'Budget constraints are hard limits'],
      success_criteria: ['Verifier passes', 'Output contract validates'],
      tasks,
      output_contract: { type: 'json', schema: { type: 'object', properties: { summary: { type: 'string' } } } }
    };
  }
}
