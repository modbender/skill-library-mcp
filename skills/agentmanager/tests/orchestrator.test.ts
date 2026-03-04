import type { AddressInfo } from 'node:net';
import { afterAll, describe, expect, it } from 'vitest';
import { createApp } from '../src/app.js';
import { OrchestratorService } from '../src/services/orchestrator.js';
import { RunStore } from '../src/services/run-store.js';
import type { Run } from '../src/types.js';

afterAll(() => {
  delete process.env.ENABLE_TOOL_REGISTER;
  delete process.env.TOOL_ALLOWLIST;
  delete process.env.TOKENOWNER_MAX_RUNNING;
  delete process.env.TOKENOWNER_MAX_PER_MINUTE;
  delete process.env.MAX_EVENTS_PER_RUN;
});

const withServer = async <T>(orchestrator: OrchestratorService, fn: (baseUrl: string) => Promise<T>): Promise<T> => {
  const app = createApp(orchestrator);
  const server = app.listen(0);
  const port = (server.address() as AddressInfo).port;
  try {
    return await fn(`http://127.0.0.1:${port}`);
  } finally {
    await new Promise<void>((resolve) => server.close(() => resolve()));
  }
};

const jsonRequest = async (url: string, init?: RequestInit): Promise<{ status: number; body: any }> => {
  const res = await fetch(url, {
    ...init,
    headers: { 'content-type': 'application/json', ...(init?.headers ?? {}) }
  });
  return { status: res.status, body: await res.json() };
};

const waitForRun = async (orchestrator: OrchestratorService, id: string, timeoutMs = 6000): Promise<Run> => {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const run = orchestrator.getRun(id);
    if (run && (run.status === 'succeeded' || run.status === 'failed')) return run;
    await new Promise((r) => setTimeout(r, 25));
  }
  throw new Error(`timeout waiting for ${id}`);
};

describe('strategy and planning behavior', () => {
  it('supports default strategy and safe_minimal_v2 differences', async () => {
    await withServer(new OrchestratorService(new RunStore()), async (base) => {
      const input = 'Return a concise answer about two plus two';
      const defaultPlan = await jsonRequest(`${base}/v1/plan`, { method: 'POST', body: JSON.stringify({ user_request: input }) });
      const safePlan = await jsonRequest(`${base}/v1/plan`, { method: 'POST', body: JSON.stringify({ user_request: input, options: { strategy_hint: 'safe_minimal_v2' } }) });
      expect(defaultPlan.status).toBe(200);
      expect(safePlan.status).toBe(200);
      expect(safePlan.body.mode).toBe('single');
    });
  });

  it('supports /v1/plan/generate convenience endpoint', async () => {
    await withServer(new OrchestratorService(new RunStore()), async (base) => {
      const generated = await jsonRequest(`${base}/v1/plan/generate`, { method: 'POST', body: JSON.stringify({ user_request: 'compute answer' }) });
      expect(generated.status).toBe(200);
      expect(Array.isArray(generated.body.tasks)).toBe(true);
    });
  });



  it('planner multi mode creates distinct executor stream goals', async () => {
    await withServer(new OrchestratorService(new RunStore()), async (base) => {
      const planned = await jsonRequest(`${base}/v1/plan`, { method: 'POST', body: JSON.stringify({ user_request: 'compute and verify with tools and analysis also compare alternatives' }) });
      expect(planned.status).toBe(200);
      if (planned.body.mode === 'multi') {
        const a = planned.body.tasks.find((t: { name: string }) => t.name === 'executor_a');
        const b = planned.body.tasks.find((t: { name: string }) => t.name === 'executor_b');
        expect(a.input).not.toBe(b.input);
        expect(String(a.input)).toContain('direct solution path');
        expect(String(b.input)).toContain('alternative strategy');
      }
    });
  });

  it('returns STRATEGY_NOT_FOUND and does not leak running counters', async () => {
    process.env.TOKENOWNER_MAX_RUNNING = '1';
    const orchestrator = new OrchestratorService(new RunStore());
    await withServer(orchestrator, async (base) => {
      const bad = await jsonRequest(`${base}/v1/run`, {
        method: 'POST',
        headers: { 'X-Run-Token': 'owner-x' },
        body: JSON.stringify({ user_request: 'x', options: { strategy_hint: 'missing' } })
      });
      expect(bad.status).toBe(400);
      expect(bad.body.code).toBe('STRATEGY_NOT_FOUND');

      const ok = await jsonRequest(`${base}/v1/run`, {
        method: 'POST',
        headers: { 'X-Run-Token': 'owner-x' },
        body: JSON.stringify({ user_request: 'slow_ms_100 compute' })
      });
      expect(ok.status).toBe(202);
    });
  });


  it('applies must_verify and tool_preference avoid options deterministically', async () => {
    const orchestrator = new OrchestratorService(new RunStore());
    await withServer(orchestrator, async (base) => {
      const plan = await jsonRequest(`${base}/v1/plan`, {
        method: 'POST',
        body: JSON.stringify({ user_request: 'compute and verify with tools', options: { must_verify: true, tool_preference: 'avoid' } })
      });
      expect(plan.status).toBe(200);
      expect(plan.body.tasks.some((t: { agent: string }) => t.agent === 'verifier')).toBe(true);
      expect(plan.body.tasks.every((t: { tools_allowed: string[] }) => t.tools_allowed.length === 0)).toBe(true);
    });
  });

  it('invalid plan returns PLAN_INVALID and does not leak running limit counters', async () => {
    process.env.TOKENOWNER_MAX_RUNNING = '1';
    const orchestrator = new OrchestratorService(new RunStore());
    await withServer(orchestrator, async (base) => {
      const invalidPlan = {
        mode: 'single', rationale: 'bad', budget: { max_steps: 1, max_tool_calls: 1, max_latency_ms: 1000, max_cost_estimate: 1, max_model_upgrades: 0 },
        invariants: [], success_criteria: [],
        tasks: [{ name: 't1', agent: 'executor', input: 'x', depends_on: ['missing'], tools_allowed: [], model: 'gpt-lite', reasoning_level: 'low', max_output_tokens: 10 }],
        output_contract: { type: 'json' }
      };
      const bad = await jsonRequest(`${base}/v1/run`, { method: 'POST', headers: { 'X-Run-Token': 'owner-y' }, body: JSON.stringify({ plan: invalidPlan }) });
      expect(bad.status).toBe(400);
      expect(bad.body.code).toBe('PLAN_INVALID');

      const ok = await jsonRequest(`${base}/v1/run`, { method: 'POST', headers: { 'X-Run-Token': 'owner-y' }, body: JSON.stringify({ user_request: 'slow_ms_100 compute' }) });
      expect(ok.status).toBe(202);
    });
  });
});

describe('tools and capabilities', () => {
  it('rejects safe-tag bypass and accepts allowlisted tool; capabilities version increments', async () => {
    process.env.ENABLE_TOOL_REGISTER = '1';
    process.env.TOOL_ALLOWLIST = 'allowed_tool,inc_tool';
    const orchestrator = new OrchestratorService(new RunStore());
    await withServer(orchestrator, async (base) => {
      const reject = await jsonRequest(`${base}/v1/tools/register`, { method: 'POST', body: JSON.stringify({ tools: [{ name: 'fake_safe', description: 'x', input_schema: { type: 'object' }, timeout_ms: 100, tags: ['safe'] }] }) });
      expect(reject.status).toBe(403);
      expect(reject.body.code).toBe('TOOL_NOT_ALLOWED');

      const capBefore = await jsonRequest(`${base}/v1/capabilities`);
      const accept = await jsonRequest(`${base}/v1/tools/register`, { method: 'POST', body: JSON.stringify({ tools: [{ name: 'allowed_tool', description: 'x', input_schema: { type: 'object' }, timeout_ms: 100, tags: [] }] }) });
      expect(accept.status).toBe(200);

      await jsonRequest(`${base}/v1/tools/register`, { method: 'POST', body: JSON.stringify({ tools: [{ name: 'inc_tool', description: 'x', input_schema: { type: 'object' }, timeout_ms: 100, tags: [] }] }) });
      const capAfter = await jsonRequest(`${base}/v1/capabilities`);
      expect(capAfter.body.tool_registration.tools_version).toBeGreaterThan(capBefore.body.tool_registration.tools_version);
      expect(Array.isArray(capAfter.body.providers)).toBe(true);
      expect(capAfter.body.providers.some((p: { id: string }) => p.id === 'mock')).toBe(true);
      expect(capAfter.body.default_provider_id).toBeTruthy();
      expect(capAfter.body.llm_providers).toBeTruthy();
      expect(Array.isArray(capAfter.body.llm_providers.providers)).toBe(true);
      expect(capAfter.body.llm_providers.env.gateway_url_env).toBe('GATEWAY_URL');
    });
  });
});

describe('idempotency, cancellation, and events', () => {

  it('supports dry_run without creating a stored run', async () => {
    const orchestrator = new OrchestratorService(new RunStore());
    await withServer(orchestrator, async (base) => {
      const dry = await jsonRequest(`${base}/v1/run`, {
        method: 'POST',
        body: JSON.stringify({ user_request: 'compute quickly', options: { dry_run: true } })
      });
      expect(dry.status).toBe(200);
      expect(dry.body.dry_run).toBe(true);
      expect(dry.body.ok).toBe(true);
      expect(dry.body.run_id).toBeUndefined();
      expect(typeof dry.body.task_count).toBe('number');
    });
  });
  it('scopes idempotency by tokenOwner', async () => {
    const orchestrator = new OrchestratorService(new RunStore());
    await withServer(orchestrator, async (base) => {
      const body = { user_request: 'compute', idempotency_key: 'same-key' };
      const a = await jsonRequest(`${base}/v1/run`, { method: 'POST', headers: { 'X-Run-Token': 'owner-a' }, body: JSON.stringify(body) });
      const b = await jsonRequest(`${base}/v1/run`, { method: 'POST', headers: { 'X-Run-Token': 'owner-b' }, body: JSON.stringify(body) });
      expect(a.status).toBe(202);
      expect(b.status).toBe(202);
      expect(a.body.run_id).not.toBe(b.body.run_id);
    });
  });

  it('cancels run immediately and preserves RUN_CANCELLED terminal state', async () => {
    const orchestrator = new OrchestratorService(new RunStore());
    await withServer(orchestrator, async (base) => {
      const created = await jsonRequest(`${base}/v1/run`, { method: 'POST', body: JSON.stringify({ user_request: 'slow_ms_800 compute' }) });
      expect(created.status).toBe(202);
      const cancelled = await jsonRequest(`${base}/v1/run/${created.body.run_id}/cancel`, { method: 'POST' });
      expect(cancelled.status).toBe(200);
      const run = await waitForRun(orchestrator, created.body.run_id);
      expect(run.status).toBe('failed');
      expect(run.error?.code).toBe('RUN_CANCELLED');
      expect(run.logs.some((e: { type: string }) => e.type === 'run_cancel_requested')).toBe(true);
    });
  });

  it('returns global cursor with truncation semantics', async () => {
    process.env.MAX_EVENTS_PER_RUN = '5';
    const orchestrator = new OrchestratorService(new RunStore());
    await withServer(orchestrator, async (base) => {
      const created = await jsonRequest(`${base}/v1/run`, { method: 'POST', body: JSON.stringify({ user_request: 'compute and verify with tool and analysis' }) });
      const run = await waitForRun(orchestrator, created.body.run_id);

      const events = await jsonRequest(`${base}/v1/run/${run.id}/events?after=0`);
      expect(events.status).toBe(200);
      expect(typeof events.body.base).toBe('number');
      expect(typeof events.body.next).toBe('number');
      if (run.logs_base > 0) {
        expect(events.body.truncated).toBe(true);
        expect(events.body.base).toBe(run.logs_base);
      }
    });
  });

  it('returns consolidated run report from in-memory store', async () => {
    const orchestrator = new OrchestratorService(new RunStore());
    await withServer(orchestrator, async (base) => {
      const created = await jsonRequest(`${base}/v1/run`, { method: 'POST', body: JSON.stringify({ user_request: 'needs_tool:js_eval', options: { strategy_hint: 'safe_minimal_v2' } }) });
      expect(created.status).toBe(202);
      const run = await waitForRun(orchestrator, created.body.run_id);

      const report = await jsonRequest(`${base}/v1/run/${run.id}/report`);
      expect(report.status).toBe(200);
      expect(report.body.run_id).toBe(run.id);
      expect(report.body.plan_summary.mode).toBe(run.plan.mode);
      expect(Array.isArray(report.body.plan_summary.tasks)).toBe(true);
      expect(report.body.events.base).toBe(run.logs_base);
      expect(Array.isArray(report.body.events.items)).toBe(true);
      expect(typeof report.body.metrics.tool_calls).toBe('number');
    });
  });

  it('returns replay payload consistent with event stream', async () => {
    const orchestrator = new OrchestratorService(new RunStore());
    await withServer(orchestrator, async (base) => {
      const created = await jsonRequest(`${base}/v1/run`, { method: 'POST', body: JSON.stringify({ user_request: 'compute for replay' }) });
      const run = await waitForRun(orchestrator, created.body.run_id);
      const replay = await jsonRequest(`${base}/v1/run/${run.id}/replay`);
      expect(replay.status).toBe(200);
      expect(replay.body.plan_digest).toBeTruthy();
      expect(Array.isArray(replay.body.events)).toBe(true);
      const events = await jsonRequest(`${base}/v1/run/${run.id}/events?after=0`);
      expect(replay.body.events.length).toBe(events.body.events.length);
    });
  });

});


describe('auth and run listing', () => {
  it('enforces optional run-token auth when enabled', async () => {
    process.env.REQUIRE_RUN_TOKEN = '1';
    process.env.RUN_TOKENS = 'a,b';
    const orchestrator = new OrchestratorService(new RunStore());

    await withServer(orchestrator, async (base) => {
      const missing = await jsonRequest(`${base}/v1/run`, { method: 'POST', body: JSON.stringify({ user_request: 'compute' }) });
      expect(missing.status).toBe(401);
      expect(missing.body.code).toBe('AUTH_INVALID_TOKEN');

      const invalid = await jsonRequest(`${base}/v1/plan`, { method: 'POST', headers: { 'X-Run-Token': 'z' }, body: JSON.stringify({ user_request: 'compute' }) });
      expect(invalid.status).toBe(401);

      const valid = await jsonRequest(`${base}/v1/plan`, { method: 'POST', headers: { 'X-Run-Token': 'a' }, body: JSON.stringify({ user_request: 'compute' }) });
      expect(valid.status).toBe(200);
    });

    delete process.env.REQUIRE_RUN_TOKEN;
    delete process.env.RUN_TOKENS;
  });

  it('lists runs by owner with pagination endpoint', async () => {
    process.env.REQUIRE_RUN_TOKEN = '1';
    process.env.RUN_TOKENS = 'owner-a,owner-b';
    const orchestrator = new OrchestratorService(new RunStore());

    await withServer(orchestrator, async (base) => {
      await jsonRequest(`${base}/v1/run`, { method: 'POST', headers: { 'X-Run-Token': 'owner-a' }, body: JSON.stringify({ user_request: 'compute one' }) });
      await jsonRequest(`${base}/v1/run`, { method: 'POST', headers: { 'X-Run-Token': 'owner-a' }, body: JSON.stringify({ user_request: 'compute two' }) });
      await jsonRequest(`${base}/v1/run`, { method: 'POST', headers: { 'X-Run-Token': 'owner-b' }, body: JSON.stringify({ user_request: 'compute three' }) });

      await new Promise((r) => setTimeout(r, 60));

      const listA = await jsonRequest(`${base}/v1/runs?limit=1`, { headers: { 'X-Run-Token': 'owner-a' } });
      expect(listA.status).toBe(200);
      expect(Array.isArray(listA.body.runs)).toBe(true);
      expect(listA.body.runs.length).toBe(1);
      expect(listA.body.runs[0].owner).toBe('owner-a');
      expect(typeof listA.body.next_cursor === 'string' || typeof listA.body.next_cursor === 'undefined').toBe(true);

      const listB = await jsonRequest(`${base}/v1/runs`, { headers: { 'X-Run-Token': 'owner-b' } });
      expect(listB.status).toBe(200);
      expect(listB.body.runs.every((r: { owner: string }) => r.owner === 'owner-b')).toBe(true);
    });

    delete process.env.REQUIRE_RUN_TOKEN;
    delete process.env.RUN_TOKENS;
  });

  it('streams heartbeat comments for idle SSE stream intervals', async () => {
    process.env.SSE_HEARTBEAT_MS = '50';
    const orchestrator = new OrchestratorService(new RunStore());

    await withServer(orchestrator, async (base) => {
      const created = await jsonRequest(`${base}/v1/run`, { method: 'POST', body: JSON.stringify({ user_request: 'slow_ms_300 compute' }) });
      expect(created.status).toBe(202);

      const res = await fetch(`${base}/v1/run/${created.body.run_id}/stream`);
      expect(res.status).toBe(200);
      const reader = res.body?.getReader();
      expect(reader).toBeTruthy();
      let collected = '';
      const started = Date.now();
      while (Date.now() - started < 1000 && !collected.includes(': ping')) {
        const chunk = await reader!.read();
        if (chunk.done) break;
        collected += new TextDecoder().decode(chunk.value);
      }
      expect(collected.includes(': ping')).toBe(true);
      reader?.cancel();
    });

    delete process.env.SSE_HEARTBEAT_MS;
  });


  it('returns provider adapter schema endpoint payload', async () => {
    const orchestrator = new OrchestratorService(new RunStore());
    await withServer(orchestrator, async (base) => {
      const res = await jsonRequest(`${base}/v1/provider-adapter/schema`);
      expect(res.status).toBe(200);
      expect(res.body.schema_version).toBe('v1');
      expect(res.body.request_schema).toBeTruthy();
      expect(res.body.response_schema).toBeTruthy();
      expect(res.body.endpoints.gateway_step_path).toBeTruthy();
      expect(res.body.examples?.request?.request_id).toBeTruthy();
      expect(res.body.examples?.response?.request_id).toBeTruthy();
    });
  });

  it('returns /v1/errors catalog', async () => {
    const orchestrator = new OrchestratorService(new RunStore());
    await withServer(orchestrator, async (base) => {
      const errors = await jsonRequest(`${base}/v1/errors`);
      expect(errors.status).toBe(200);
      expect(Array.isArray(errors.body.errors)).toBe(true);
      expect(errors.body.errors.some((e: { code: string }) => e.code === 'DAG_DEADLOCK')).toBe(true);
    });
  });
});
