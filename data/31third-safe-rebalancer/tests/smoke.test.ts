import { describe, expect, it, vi } from 'vitest';
import type { PublicClient } from 'viem';

import { runSmoke, type SmokeIO } from '../scripts/smoke.js';
import type { RuntimeConfig } from '../index.js';

function makeIo() {
  const log = vi.fn();
  const error = vi.fn();
  const io: SmokeIO = { log, error };
  return { io, log, error };
}

function makeConfig(): RuntimeConfig {
  return {
    safeAddress: '0x1000000000000000000000000000000000000001',
    chainId: 8453,
    rpcUrl: 'https://mainnet.base.org',
    executorModuleAddress: '0x2000000000000000000000000000000000000002'
  };
}

describe('smoke', () => {
  it('returns non-zero when config load fails', async () => {
    const { io, log } = makeIo();
    const code = await runSmoke([], io, {
      readConfigFromEnv: () => {
        throw new Error('bad env');
      },
      createViemClients: vi.fn() as any,
      readPolicySnapshot: vi.fn() as any,
      check_drift: vi.fn() as any,
      plan_rebalance: vi.fn() as any,
      simulateExecuteTradeNow: vi.fn() as any
    });

    expect(code).toBe(1);
    expect(String(log.mock.calls[0][0])).toContain('"ok": false');
  });

  it('passes happy-path checks and warns for skipped optional preflights', async () => {
    const { io, log } = makeIo();
    const publicClient = { getChainId: vi.fn(async () => 8453) } as unknown as PublicClient;

    const code = await runSmoke([], io, {
      readConfigFromEnv: () => makeConfig(),
      createViemClients: () => ({ publicClient }),
      readPolicySnapshot: vi.fn(async () => ({
        assetUniverseTokens: [],
        targetAllocations: []
      })),
      check_drift: vi.fn(async () => ({
        shouldRebalance: false,
        thresholdBps: 0,
        maxDriftBps: 0,
        explanation: 'ok',
        why: 'ok',
        tokens: []
      })),
      plan_rebalance: vi.fn() as any,
      simulateExecuteTradeNow: vi.fn() as any
    });

    expect(code).toBe(0);
    const output = String(log.mock.calls[0][0]);
    expect(output).toContain('"ok": true');
    expect(output).toContain('"status": "warn"');
  });
});
