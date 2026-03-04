import { describe, expect, it, vi } from 'vitest';

vi.mock('../src/security/outbound-policy.js', () => ({
  checkOutboundUrl: async () => undefined
}));

describe('GatewayLLMProvider', () => {
  it('validates adapter schema and returns tool calls', async () => {
    process.env.GATEWAY_URL = 'https://api.example.com';
    process.env.OUTBOUND_ALLOW_ALL = '1';
    process.env.OUTBOUND_HOST_ALLOWLIST = 'api.example.com';
    process.env.OUTBOUND_ALLOWLIST = 'api.example.com';

    const { GatewayLLMProvider } = await import('../src/providers/gateway.js');
    const provider = new GatewayLLMProvider();
    const original = global.fetch;
    global.fetch = (async () => new Response(JSON.stringify({
      request_id: 'r1:t1:a1:s1',
      output_text: 'done',
      tool_calls: [{ call_id: 'c1', name: 'js_eval', arguments: { expression: '1+1' } }],
      usage: { input_tokens: 1, output_tokens: 2 },
      model: 'gw-model'
    }), { status: 200, headers: { 'content-type': 'application/json' } })) as typeof fetch;

    try {
      const res = await provider.executeRound({
        run_id: 'r1',
        runId: 'r1',
        task: { name: 't1', agent: 'executor', input: 'x', depends_on: [], tools_allowed: ['js_eval'], model: 'm', reasoning_level: 'low', max_output_tokens: 10 },
        taskName: 't1',
        step: 1,
        attempt: 1,
        requestId: 'r1:t1:a1:s1',
        tier: 'cheap',
        tokenOwner: 'o1',
        dependencyDigests: [],
        messages: [{ role: 'user', content: 'x' }],
        tools: [{ name: 'js_eval', description: 'd', input_schema: { type: 'object' }, timeout_ms: 1000, tags: [] }]
      });
      expect(res.model).toBe('gw-model');
      expect(res.tool_calls?.[0].name).toBe('js_eval');
    } finally {
      global.fetch = original;
      delete process.env.GATEWAY_URL;
      delete process.env.OUTBOUND_ALLOW_ALL;
      delete process.env.OUTBOUND_HOST_ALLOWLIST;
      delete process.env.OUTBOUND_ALLOWLIST;
    }
  });
});
