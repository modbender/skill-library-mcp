import type { AddressInfo } from 'node:net';
import { describe, expect, it } from 'vitest';
import { sleep } from '../src/lib/utils.js';
import { ToolRegistry } from '../src/services/tools.js';

describe('ToolRegistry builtins hardening', () => {
  it('rejects file_store path traversal and absolute path', async () => {
    const registry = new ToolRegistry();

    const traversal = await registry.call('file_store', { path: '../x.txt', content: 'x' }, { runId: 'r1', tokenOwner: 'o1' });
    expect(traversal.ok).toBe(false);
    expect((traversal.output as { error: string }).error).toBe('PATH_NOT_ALLOWED');

    const absolute = await registry.call('file_store', { path: '/tmp/x.txt', content: 'x' }, { runId: 'r1', tokenOwner: 'o1' });
    expect(absolute.ok).toBe(false);
    expect((absolute.output as { error: string }).error).toBe('PATH_NOT_ALLOWED');

    const windowsSlash = await registry.call('file_store', { path: 'a\\b.txt', content: 'x' }, { runId: 'r1', tokenOwner: 'o1' });
    expect(windowsSlash.ok).toBe(false);
    expect((windowsSlash.output as { error: string }).error).toBe('PATH_NOT_ALLOWED');
  });

  it('enforces artifact cap atomically under concurrency', async () => {
    const registry = new ToolRegistry();
    let bytes = 0;

    const ctx = {
      runId: 'r2',
      tokenOwner: 'o2',
      getArtifactsBytes: () => bytes,
      tryReserveArtifactsBytes: (delta: number) => {
        if (bytes + delta > 10) return false;
        bytes += delta;
        return true;
      },
      rollbackArtifactsBytes: (delta: number) => {
        bytes = Math.max(0, bytes - delta);
      }
    };

    const [a, b] = await Promise.all([
      registry.call('file_store', { path: 'a.txt', content: '1234567890' }, ctx),
      registry.call('file_store', { path: 'b.txt', content: '1234567890' }, ctx)
    ]);

    const okCount = [a, b].filter((v) => v.ok).length;
    const limitCount = [a, b].filter((v) => (v.output as { error?: string }).error === 'ARTIFACT_LIMIT').length;
    expect(okCount).toBe(1);
    expect(limitCount).toBe(1);
    expect(bytes).toBeLessThanOrEqual(10);
  });

  it('supports arithmetic-only js_eval and rejects unsafe expressions', async () => {
    const registry = new ToolRegistry();

    const ok = await registry.call('js_eval', { expression: '1+2*3' }, { runId: 'r3', tokenOwner: 'o3' });
    expect(ok.ok).toBe(true);
    expect(ok.output).toBe(7);

    const disallowed = await registry.call('js_eval', { expression: 'process.exit()' }, { runId: 'r3', tokenOwner: 'o3' });
    expect(disallowed.ok).toBe(false);
    expect((disallowed.output as { error: string }).error).toBe('EXPRESSION_NOT_ALLOWED');

    const semicolon = await registry.call('js_eval', { expression: '1;2' }, { runId: 'r3', tokenOwner: 'o3' });
    expect(semicolon.ok).toBe(false);
    expect((semicolon.output as { error: string }).error).toBe('EXPRESSION_NOT_ALLOWED');
  });



  it('supports HTTP callback tools', async () => {
    process.env.TOOL_ALLOWLIST = 'callback_tool';
    process.env.ALLOW_INSECURE_HTTP_TOOLS = '1';
    process.env.TOOL_CALLBACK_ALLOW_LOCAL_TEST = '1';
    const registry = new ToolRegistry();
    const http = await import('node:http');
    const callbackServer = http.createServer((req, res) => {
      if (req.method !== 'POST') {
        res.statusCode = 405;
        res.end();
        return;
      }
      const chunks: Buffer[] = [];
      req.on('data', (chunk) => chunks.push(Buffer.from(chunk)));
      req.on('end', () => {
        const body = JSON.parse(Buffer.concat(chunks).toString('utf8')) as { input: { value: number }; run_id: string; token_owner: string };
        res.setHeader('content-type', 'application/json');
        res.end(JSON.stringify({ echoed: body.input.value, run_id: body.run_id, owner: body.token_owner, tokens_used: 7 }));
      });
    });

    await new Promise<void>((resolve) => callbackServer.listen(0, () => resolve()));
    const port = (callbackServer.address() as AddressInfo).port;

    try {
      registry.register([
        {
          name: 'callback_tool',
          description: 'calls callback',
          input_schema: { type: 'object', properties: { value: { type: 'number' } }, required: ['value'] },
          timeout_ms: 100,
          tags: [],
          callback_url: `http://127.0.0.1:${port}/tool`
        }
      ]);

      const result = await registry.call('callback_tool', { value: 42 }, { runId: 'run-http', tokenOwner: 'owner-http' });
      expect(result.ok).toBe(true);
      expect(result.tokens_used).toBe(7);
      expect(result.output).toMatchObject({ echoed: 42, run_id: 'run-http', owner: 'owner-http' });
    } finally {
      await new Promise<void>((resolve) => callbackServer.close(() => resolve()));
      delete process.env.ALLOW_INSECURE_HTTP_TOOLS;
      delete process.env.TOOL_CALLBACK_ALLOW_LOCAL_TEST;
    }
  });

  it('blocks localhost callback by default', () => {
    process.env.TOOL_ALLOWLIST = 'blocked_callback_tool';
    const registry = new ToolRegistry();
    expect(() => registry.register([
      {
        name: 'blocked_callback_tool',
        description: 'blocked',
        input_schema: { type: 'object' },
        timeout_ms: 100,
        tags: [],
        callback_url: 'http://127.0.0.1:9999/tool'
      }
    ])).toThrow();
  });



  it('enforces callback tool timeout', async () => {
    process.env.TOOL_ALLOWLIST = 'callback_timeout_tool';
    process.env.ALLOW_INSECURE_HTTP_TOOLS = '1';
    process.env.TOOL_CALLBACK_ALLOW_LOCAL_TEST = '1';
    const registry = new ToolRegistry();
    const http = await import('node:http');
    const callbackServer = http.createServer((_req, res) => {
      setTimeout(() => {
        res.setHeader('content-type', 'application/json');
        res.end(JSON.stringify({ ok: true }));
      }, 80);
    });

    await new Promise<void>((resolve) => callbackServer.listen(0, () => resolve()));
    const port = (callbackServer.address() as AddressInfo).port;

    try {
      registry.register([
        {
          name: 'callback_timeout_tool',
          description: 'callback timeout',
          input_schema: { type: 'object' },
          timeout_ms: 10,
          tags: [],
          callback_url: `http://127.0.0.1:${port}/slow`
        }
      ]);

      const result = await registry.call('callback_timeout_tool', {}, { runId: 'run-timeout', tokenOwner: 'owner-timeout' });
      expect(result.ok).toBe(false);
      expect((result.output as { error: string }).error).toBe('TOOL_TIMEOUT');
    } finally {
      await new Promise<void>((resolve) => callbackServer.close(() => resolve()));
      delete process.env.ALLOW_INSECURE_HTTP_TOOLS;
      delete process.env.TOOL_CALLBACK_ALLOW_LOCAL_TEST;
    }
  });

  it('enforces timeout_ms for registered tools', async () => {
    process.env.TOOL_ALLOWLIST = 'slow_tool';
    const registry = new ToolRegistry();
    registry.register([
      {
        name: 'slow_tool',
        description: 'slow',
        input_schema: { type: 'object' },
        timeout_ms: 5,
        tags: []
      }
    ]);

    registry.setHandler('slow_tool', async () => {
      await sleep(20);
      return { ok: true, output: { done: true }, tokens_used: 5 };
    });

    const timedOut = await registry.call('slow_tool', {}, { runId: 'r4', tokenOwner: 'o4' });
    expect(timedOut.ok).toBe(false);
    expect((timedOut.output as { error: string }).error).toBe('TOOL_TIMEOUT');
  });
});
