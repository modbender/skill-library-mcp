import { createServer } from 'node:http';
import { afterEach, describe, expect, it } from 'vitest';
import { createApp } from '../src/app.js';
import { OrchestratorService } from '../src/services/orchestrator.js';
import { RunStore } from '../src/services/run-store.js';
import { checkOutboundUrl, parseAllowlist } from '../src/security/outbound-policy.js';
import { ToolRegistry } from '../src/services/tools.js';

const withServer = async (handler: Parameters<typeof createServer>[0], run: (base: string) => Promise<void>): Promise<void> => {
  const server = createServer(handler);
  await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', () => resolve()));
  const addr = server.address();
  if (!addr || typeof addr === 'string') throw new Error('bad addr');
  const base = `http://127.0.0.1:${addr.port}`;
  try {
    await run(base);
  } finally {
    await new Promise<void>((resolve, reject) => server.close((err) => err ? reject(err) : resolve()));
  }
};

const withApi = async (run: (base: string, orchestrator: OrchestratorService) => Promise<void>): Promise<void> => {
  const orchestrator = new OrchestratorService(new RunStore());
  const app = createApp(orchestrator);
  const server = createServer(app);
  await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', () => resolve()));
  const addr = server.address();
  if (!addr || typeof addr === 'string') throw new Error('bad addr');
  const base = `http://127.0.0.1:${addr.port}`;
  try {
    await run(base, orchestrator);
  } finally {
    await new Promise<void>((resolve, reject) => server.close((err) => err ? reject(err) : resolve()));
  }
};

const jsonReq = async (url: string, init?: RequestInit): Promise<{ status: number; body: any }> => {
  const res = await fetch(url, { headers: { 'content-type': 'application/json', ...(init?.headers ?? {}) }, ...init });
  const body = await res.json();
  return { status: res.status, body };
};

afterEach(() => {
  delete process.env.REDACT_TELEMETRY;
  delete process.env.REDACT_TELEMETRY_MODE;
  delete process.env.OUTBOUND_ALLOWLIST;
  delete process.env.TOOL_CALLBACK_ALLOWLIST;
  delete process.env.ALLOW_INSECURE_HTTP_TOOLS;
  delete process.env.TOOL_CALLBACK_ALLOW_LOCAL_TEST;
  delete process.env.ENABLE_TOOL_REGISTER;
  delete process.env.TOOL_ALLOWLIST;
});

describe('outbound allowlist policy', () => {
  it('matches exact and wildcard rules with optional port', async () => {
    const rules = parseAllowlist('api.example.com:443,*.example.com:8443');
    expect(rules).toHaveLength(2);

    await expect(checkOutboundUrl('https://api.example.com', {
      allowlistRaw: 'api.example.com:443',
      allowHttp: false,
      resolver: async () => [{ address: '93.184.216.34' }]
    })).resolves.toBeUndefined();

    await expect(checkOutboundUrl('https://a.example.com:8443/x', {
      allowlistRaw: '*.example.com:8443',
      allowHttp: false,
      resolver: async () => [{ address: '93.184.216.34' }]
    })).resolves.toBeUndefined();
  });

  it('rejects ip literals and private dns results', async () => {
    await expect(checkOutboundUrl('https://127.0.0.1/x', { allowlistRaw: '127.0.0.1', allowHttp: false })).rejects.toThrow('OUTBOUND_IP_LITERAL_FORBIDDEN');
    await expect(checkOutboundUrl('https://safe.example.com/x', {
      allowlistRaw: 'safe.example.com',
      allowHttp: false,
      resolver: async () => [{ address: '127.0.0.1' }]
    })).rejects.toThrow('OUTBOUND_PRIVATE_ADDRESS_BLOCKED');
  });
});

describe('callback tools outbound hardening', () => {
  it('uses redirect:error and blocks redirect responses', async () => {
    process.env.ENABLE_TOOL_REGISTER = '1';
    process.env.TOOL_ALLOWLIST = 'cb';
    process.env.ALLOW_INSECURE_HTTP_TOOLS = '1';
    process.env.TOOL_CALLBACK_ALLOW_LOCAL_TEST = '1';

    const registry = new ToolRegistry();
    registry.register([{ name: 'cb', description: 'cb', input_schema: { type: 'object' }, timeout_ms: 1000, tags: [], callback_url: 'http://127.0.0.1:9999/cb' }]);

    const original = global.fetch;
    let redirectMode: string | undefined;
    global.fetch = (async (_input: any, init?: RequestInit) => {
      redirectMode = String(init?.redirect);
      return new Response('', { status: 302, headers: { location: 'http://other' } });
    }) as typeof fetch;
    try {
      const result = await registry.call('cb', {}, { runId: 'r1', tokenOwner: 'o1' });
      expect(redirectMode).toBe('error');
      expect(result.ok).toBe(false);
    } finally {
      global.fetch = original;
    }
  });
});

describe('telemetry redaction mode', () => {
  it('redacts replay/report/events payload fields', async () => {
    process.env.REDACT_TELEMETRY = '1';
    process.env.REDACT_TELEMETRY_MODE = 'hash';

    await withApi(async (base, orchestrator) => {
      const created = await jsonReq(`${base}/v1/run`, { method: 'POST', body: JSON.stringify({ user_request: 'compute secret_payload_value' }) });
      expect(created.status).toBe(202);
      const runId = created.body.run_id as string;

      const wait = async (): Promise<void> => {
        for (let i = 0; i < 60; i += 1) {
          const run = orchestrator.getRun(runId);
          if (run && (run.status === 'succeeded' || run.status === 'failed')) return;
          await new Promise((r) => setTimeout(r, 20));
        }
        throw new Error('timeout');
      };
      await wait();

      const replay = await jsonReq(`${base}/v1/run/${runId}/replay`);
      expect(replay.status).toBe(200);
      const payload = replay.body.results_index.single_executor.payload;
      expect(payload.redacted || payload.input?.redacted).toBeTruthy();

      const report = await jsonReq(`${base}/v1/run/${runId}/report`);
      expect(report.status).toBe(200);
      expect(report.body.results_by_task.single_executor.payload.redacted || report.body.results_by_task.single_executor.payload.input?.redacted).toBeTruthy();

      const events = await jsonReq(`${base}/v1/run/${runId}/events?after=0`);
      expect(events.status).toBe(200);
      expect(events.body.events[0].seq).toBeGreaterThan(0);
    });
  });
});
