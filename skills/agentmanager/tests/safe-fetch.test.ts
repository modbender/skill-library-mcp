import { createServer } from 'node:http';
import { describe, expect, it } from 'vitest';
import { safeFetch } from '../src/lib/safe-fetch.js';

const withServer = async (handler: Parameters<typeof createServer>[0], run: (base: string) => Promise<void>): Promise<void> => {
  const server = createServer(handler);
  await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', () => resolve()));
  const addr = server.address();
  if (!addr || typeof addr === 'string') throw new Error('bad addr');
  const base = `http://127.0.0.1:${addr.port}`;
  try { await run(base); } finally { await new Promise<void>((resolve) => server.close(() => resolve())); }
};

describe('safeFetch', () => {
  it('allows allowlisted host with resolver override', async () => {
    process.env.OUTBOUND_HOST_ALLOWLIST = 'api.example.com';
    process.env.OUTBOUND_ALLOW_ALL = '0';
    const original = global.fetch;
    global.fetch = (async () => new Response('{"ok":true}', { status: 200, headers: { 'content-type': 'application/json' } })) as typeof fetch;
    try {
      const res = await safeFetch('https://api.example.com/v1', { resolver: async () => [{ address: '93.184.216.34' }] });
      expect(res.status).toBe(200);
    } finally {
      global.fetch = original;
    }
  });

  it('blocks private ip literals and dns private resolutions', async () => {
    process.env.OUTBOUND_ALLOW_ALL = '1';
    await expect(safeFetch('https://127.0.0.1/x', {})).rejects.toThrow('OUTBOUND_IP_LITERAL_FORBIDDEN');
    await expect(safeFetch('https://api.example.com/x', { resolver: async () => [{ address: '10.0.0.1' }] })).rejects.toThrow('OUTBOUND_PRIVATE_ADDRESS_BLOCKED');
  });

  it('blocks redirects and enforces size cap', async () => {
    process.env.OUTBOUND_ALLOW_ALL = '1';
    const original = global.fetch;
    global.fetch = (async (_url, init) => {
      if (init?.redirect === 'error') {
        return new Response('x'.repeat(5000), { status: 200, headers: { 'content-type': 'text/plain' } });
      }
      return new Response('', { status: 302, headers: { location: 'https://api.example.com/next' } });
    }) as typeof fetch;
    try {
      await expect(safeFetch('https://api.example.com/ok', { maxBytes: 100, resolver: async () => [{ address: '93.184.216.34' }] })).rejects.toThrow('OUTBOUND_RESPONSE_TOO_LARGE');
    } finally {
      global.fetch = original;
    }
  });
});
