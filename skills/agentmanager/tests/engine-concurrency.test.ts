import { existsSync } from 'node:fs';
import { rm } from 'node:fs/promises';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { sleep } from '../src/lib/utils.js';
import { ExecutionEngine } from '../src/services/engine.js';
import { ToolRegistry } from '../src/services/tools.js';
import type { LLMProvider } from '../src/providers/llm-provider.js';
import type { Plan, Run, TaskSpec } from '../src/types.js';

const pricing = { maxTierCap: 'premium' as const, tierPricePerToken: { cheap: 0.000001, standard: 0.000003, premium: 0.000008 } };

const baseRun = (id: string, plan: Plan): Run => ({
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

describe('engine structured concurrency', () => {
  it('aborts in-flight sibling work and prevents late file_store side effects after failure', async () => {
    const runId = 'run-structured-concurrency';
    await rm(join(process.cwd(), 'runs', 'artifacts', runId), { recursive: true, force: true });

    const provider: LLMProvider = {
      id: 'test-provider',
      async step(task: TaskSpec, context) {
        if (task.name === 'fail_now') {
          const error = new Error('fail now') as Error & { code: string; retryable: boolean; at: string };
          error.code = 'INTERNAL';
          error.retryable = false;
          error.at = task.name;
          throw error;
        }
        if (task.name === 'write_late') {
          await sleep(200, context.signal);
        }
        return {
          type: 'final',
          payload: {
            task: task.name,
            agent: task.agent,
            input: task.input,
            dependency_digests: context.dependencyDigests,
            verified: true,
            owner: context.tokenOwner
          }
        };
      }
    };

    const tools = new ToolRegistry();
    const engine = new ExecutionEngine(tools, provider);
    const plan: Plan = {
      mode: 'multi',
      rationale: 'parallel failure test',
      budget: { max_steps: 4, max_tool_calls: 5, max_latency_ms: 5000, max_cost_estimate: 10, max_model_upgrades: 1 },
      invariants: [],
      success_criteria: [],
      output_contract: { type: 'json' },
      tasks: [
        { name: 'fail_now', agent: 'executor', input: 'tool compute', depends_on: [], tools_allowed: [], model: 'gpt-lite', reasoning_level: 'low', max_output_tokens: 32 },
        { name: 'write_late', agent: 'executor', input: 'tool slow_ms_200 store', depends_on: [], tools_allowed: ['file_store'], model: 'gpt-lite', reasoning_level: 'low', max_output_tokens: 32 }
      ]
    };

    let unhandled = 0;
    const onUnhandled = () => {
      unhandled += 1;
    };
    process.on('unhandledRejection', onUnhandled);

    try {
      const run = await engine.executeRun(baseRun(runId, plan), { tokenOwner: 'owner', pricing, maxConcurrency: 2 });
      expect(['failed', 'succeeded']).toContain(run.status);
      expect(run.metrics.fallback).toBe(true);
      await sleep(50);
      expect(unhandled).toBe(0);
      const expectedPath = join(process.cwd(), 'runs', 'artifacts', runId, 'write_late.txt');
      expect(existsSync(expectedPath)).toBe(false);
    } finally {
      process.off('unhandledRejection', onUnhandled);
      await rm(join(process.cwd(), 'runs', 'artifacts', runId), { recursive: true, force: true });
    }
  });
});
