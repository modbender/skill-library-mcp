import { describe, expect, it, vi } from 'vitest';
import { writeFile, unlink } from 'node:fs/promises';

vi.mock('../index.js', () => ({
  rebalance_now: vi.fn(async () => ({ txHash: '0xabc' })),
  verify_deployment_config: vi.fn(async () => ({ ok: true })),
  help: vi.fn(() => ({ summary: 'help' }))
}));

import { runCli } from '../scripts/cli.js';
import { rebalance_now, verify_deployment_config } from '../index.js';
import { beforeEach } from 'vitest';

describe('cli', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('runs rebalance-now', async () => {
    const io = { log: vi.fn(), error: vi.fn() };
    const code = await runCli(['rebalance-now'], io as any);
    expect(code).toBe(0);
    expect(rebalance_now).toHaveBeenCalledTimes(1);
  });

  it('prints usage for unknown command', async () => {
    const io = { log: vi.fn(), error: vi.fn() };
    const code = await runCli(['wat'], io as any);
    expect(code).toBe(1);
    expect(io.error).toHaveBeenCalled();
  });

  it('passes --target-entries fallback payload to rebalance_now', async () => {
    const io = { log: vi.fn(), error: vi.fn() };
    const code = await runCli([
      'rebalance-now',
      '--target-entries',
      '[{\"tokenAddress\":\"0x3000000000000000000000000000000000000003\",\"allocation\":1}]'
    ], io as any);
    expect(code).toBe(0);
    expect(rebalance_now).toHaveBeenCalledTimes(1);
    const params = (rebalance_now as any).mock.calls[0][0];
    expect(params.targetEntries).toEqual([
      { tokenAddress: '0x3000000000000000000000000000000000000003', allocation: 1 }
    ]);
  });

  it('runs verify-deployment with inline summary', async () => {
    const io = { log: vi.fn(), error: vi.fn() };
    const code = await runCli([
      'verify-deployment',
      '--troubleshooting-summary',
      'Safe=0x1000000000000000000000000000000000000001'
    ], io as any);
    expect(code).toBe(0);
    expect(verify_deployment_config).toHaveBeenCalledTimes(1);
    const params = (verify_deployment_config as any).mock.calls[0][0];
    expect(params.troubleshootingSummary).toContain('Safe=');
  });

  it('rejects traversal in --troubleshooting-file', async () => {
    const io = { log: vi.fn(), error: vi.fn() };
    const code = await runCli([
      'verify-deployment',
      '--troubleshooting-file',
      '../package.json'
    ], io as any);
    expect(code).toBe(1);
    expect(verify_deployment_config).toHaveBeenCalledTimes(0);
    expect(io.error).toHaveBeenCalled();
  });

  it('reads --troubleshooting-file inside cwd', async () => {
    const io = { log: vi.fn(), error: vi.fn() };
    const file = '.tmp-troubleshooting-summary.txt';
    await writeFile(file, 'Safe=0x1000000000000000000000000000000000000001', 'utf8');
    try {
      const code = await runCli([
        'verify-deployment',
        '--troubleshooting-file',
        file
      ], io as any);
      expect(code).toBe(0);
      expect(verify_deployment_config).toHaveBeenCalledTimes(1);
    } finally {
      await unlink(file);
    }
  });

  it('rejects unsafe target entries payload', async () => {
    const io = { log: vi.fn(), error: vi.fn() };
    const code = await runCli([
      'rebalance-now',
      '--target-entries',
      '[{\"tokenAddress\":\"0x3000000000000000000000000000000000000003\",\"allocation\":1,\"__proto__\":{}}]'
    ], io as any);
    expect(code).toBe(1);
    expect(rebalance_now).toHaveBeenCalledTimes(0);
    expect(io.error).toHaveBeenCalled();
  });
});
