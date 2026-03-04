import { describe, expect, it } from 'vitest';
import { RunStore } from '../src/services/run-store.js';
import type { Plan, Run } from '../src/types.js';

const plan: Plan = {
  mode: 'single',
  rationale: 'test',
  budget: { max_steps: 1, max_tool_calls: 1, max_latency_ms: 1000, max_cost_estimate: 1, max_model_upgrades: 0 },
  invariants: [],
  success_criteria: [],
  tasks: [{ name: 'single_executor', agent: 'executor', input: 'x', depends_on: [], tools_allowed: [], model: 'gpt-lite', reasoning_level: 'low', max_output_tokens: 10, timeout_ms: 1000 }],
  output_contract: { type: 'json' }
};

const run = (id: string, createdAt: number, status: Run['status']): Run => ({
  id,
  created_at: createdAt,
  status,
  plan,
  results_by_task: {},
  progress: { total_tasks: 1, completed_tasks: 0, running_tasks: 0, queued_tasks: 1 },
  logs_base: 0,
  logs: [],
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

describe('RunStore TTL and completion wait', () => {
  it('evicts expired runs and idempotency mappings', async () => {
    const store = new RunStore(false);
    const old = run('old-run', Date.now() - 2 * 60 * 60 * 1000, 'failed');
    store.set(old);
    store.putIdempotency('owner', 'key', old.id);
    (store as unknown as { cleanup: () => void }).cleanup();

    expect(store.get(old.id)).toBeUndefined();
    expect(store.getByIdempotency('owner', 'key')).toBeUndefined();
  });



  it('getByIdempotency does not trigger cleanup traversal', () => {
    const store = new RunStore(false);
    store.putIdempotency('owner', 'key', 'run-x');
    const before = store.getCleanupCount();
    for (let i = 0; i < 100; i += 1) {
      expect(store.getByIdempotency('owner', 'key')).toBe('run-x');
    }
    const after = store.getCleanupCount();
    expect(after).toBe(before);
  });

  it('capacity eviction clears idempotency entries', () => {
    process.env.MAX_RUNS_IN_MEMORY = '2';
    const store = new RunStore(false);
    const a = run('a', Date.now() - 3, 'succeeded');
    const b = run('b', Date.now() - 2, 'succeeded');
    const c = run('c', Date.now() - 1, 'succeeded');
    store.set(a, 'owner');
    store.putIdempotency('owner', 'a', 'a');
    store.set(b, 'owner');
    store.putIdempotency('owner', 'b', 'b');
    store.set(c, 'owner');
    store.putIdempotency('owner', 'c', 'c');
    expect(store.get('a')).toBeUndefined();
    expect(store.getByIdempotency('owner', 'a')).toBeUndefined();
    delete process.env.MAX_RUNS_IN_MEMORY;
  });

  it('waits for completion without polling', async () => {
    const store = new RunStore(false);
    const running = run('wait-run', Date.now(), 'running');
    store.set(running);

    const waiter = store.waitForCompletion('wait-run', { timeoutMs: 1000 });
    setTimeout(() => {
      store.set({ ...running, status: 'succeeded' });
    }, 20);

    const done = await waiter;
    expect(done.status).toBe('succeeded');
  });
});
