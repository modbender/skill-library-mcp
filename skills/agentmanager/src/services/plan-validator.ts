import AjvModule from 'ajv';
import type { Plan } from '../types.js';
import { ToolRegistry } from './tools.js';

const Ajv = (AjvModule as unknown as { new (opts: { strict: boolean }): any });
const ajv = new Ajv({ strict: false });

export class PlanValidationError extends Error {
  readonly code = 'PLAN_INVALID';
  readonly retryable = false;
  readonly at = 'plan';

  constructor(message: string) {
    super(message);
  }
}

export const validatePlan = (plan: Plan, toolRegistry: ToolRegistry): void => {
  if (plan.output_contract.type === 'json' && plan.output_contract.schema) {
    try {
      ajv.compile(plan.output_contract.schema);
    } catch {
      throw new PlanValidationError('Invalid output_contract JSON Schema');
    }
  }

  const taskNames = new Set<string>();

  for (const task of plan.tasks) {
    if (taskNames.has(task.name)) {
      throw new PlanValidationError(`Duplicate task name: ${task.name}`);
    }
    taskNames.add(task.name);
  }

  if (plan.tasks.length > plan.budget.max_steps) {
    throw new PlanValidationError('Task count exceeds budget.max_steps');
  }

  for (const task of plan.tasks) {
    if (task.timeout_ms && task.timeout_ms > plan.budget.max_latency_ms) {
      throw new PlanValidationError(`Task ${task.name} timeout_ms exceeds plan.budget.max_latency_ms`);
    }

    for (const dep of task.depends_on) {
      if (!taskNames.has(dep)) {
        throw new PlanValidationError(`Task ${task.name} depends on unknown task ${dep}`);
      }
    }

    for (const tool of task.tools_allowed) {
      if (!toolRegistry.has(tool)) {
        throw new PlanValidationError(`Task ${task.name} references unknown tool ${tool}`);
      }
      if (!toolRegistry.isToolAllowed(tool)) {
        throw new PlanValidationError(`Task ${task.name} references disallowed tool ${tool}`);
      }
    }
  }

  const byName = new Map(plan.tasks.map((task) => [task.name, task]));
  const visiting = new Set<string>();
  const visited = new Set<string>();

  const visit = (name: string): void => {
    if (visited.has(name)) return;
    if (visiting.has(name)) {
      throw new PlanValidationError(`Cycle detected at task ${name}`);
    }

    visiting.add(name);
    const task = byName.get(name);
    if (!task) {
      throw new PlanValidationError(`Unknown task in graph traversal: ${name}`);
    }

    for (const dep of task.depends_on) {
      visit(dep);
    }
    visiting.delete(name);
    visited.add(name);
  };

  for (const task of plan.tasks) {
    visit(task.name);
  }

  const groups = new Map<string, Set<string>>();
  for (const task of plan.tasks) {
    if (!task.parallel_group) continue;
    const set = groups.get(task.parallel_group) ?? new Set<string>();
    set.add(task.name);
    groups.set(task.parallel_group, set);
  }

  for (const [groupName, members] of groups) {
    for (const member of members) {
      const task = byName.get(member);
      if (!task) continue;
      for (const dep of task.depends_on) {
        if (members.has(dep)) {
          throw new PlanValidationError(`Tasks in parallel_group ${groupName} cannot depend on each other (${member} -> ${dep})`);
        }
      }
    }
  }
};
