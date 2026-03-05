import { describe, expect, it, vi } from 'vitest';

import { rebalance_now, type RuntimeConfig } from '../index.js';

const config: RuntimeConfig = {
  safeAddress: '0x1000000000000000000000000000000000000001',
  executorModuleAddress: '0x2000000000000000000000000000000000000002',
  executorWalletPrivateKey: '0xabc',
  apiKey: 'key',
  rpcUrl: 'https://mainnet.base.org',
  chainId: 8453,
  apiBaseUrl: 'https://api.31third.com/1.3',
  maxSlippage: 0.01,
  maxPriceImpact: 0.05,
  minTradeValue: 0.1,
  skipBalanceValidation: false
};

describe('rebalance_now', () => {
  it('executes one-step flow with policy-derived entries', async () => {
    const calculateRebalancingFn = vi.fn(async () => ({ txData: '0x1234', requiredAllowances: [] }));
    const wait = vi.fn(async () => ({}));
    const executeRebalancingFn = vi.fn(async () => ({ hash: '0xdead', wait }));

    const result = await rebalance_now({
      config,
      deps: {
        calculateRebalancingFn: calculateRebalancingFn as any,
        executeRebalancingFn: executeRebalancingFn as any,
        createExecutorSignerFn: () => ({ getAddress: async () => '0x3000000000000000000000000000000000000003' } as any),
        loadPlanInputsFn: async () => ({
          scheduler: '0x3000000000000000000000000000000000000003',
          registry: '0x3000000000000000000000000000000000000003',
          baseEntries: [{ tokenAddress: '0xaaa', amount: '1' }],
          targetEntries: [{ tokenAddress: '0xbbb', allocation: 1 }],
          effectiveMaxSlippage: 0.01,
          effectiveMaxPriceImpact: 0.01,
          notes: []
        })
      }
    });

    expect(result.txHash).toBe('0xdead');
    expect(calculateRebalancingFn).toHaveBeenCalledTimes(1);
    expect(executeRebalancingFn).toHaveBeenCalledTimes(1);
    expect(wait).toHaveBeenCalledTimes(1);
  });

  it('fails when scheduler and registry differ', async () => {
    await expect(rebalance_now({
      config,
      deps: {
        calculateRebalancingFn: vi.fn() as any,
        executeRebalancingFn: vi.fn() as any,
        createExecutorSignerFn: () => ({ getAddress: async () => '0x3000000000000000000000000000000000000003' } as any),
        loadPlanInputsFn: async () => ({
          scheduler: '0x3000000000000000000000000000000000000003',
          registry: '0x4000000000000000000000000000000000000004',
          baseEntries: [],
          targetEntries: [],
          effectiveMaxSlippage: 0.01,
          effectiveMaxPriceImpact: 0.01,
          notes: []
        })
      }
    })).rejects.toThrow('SCHEDULER_REGISTRY_MISMATCH');
  });

  it('fails when executor wallet is not registry', async () => {
    await expect(rebalance_now({
      config,
      deps: {
        calculateRebalancingFn: vi.fn() as any,
        executeRebalancingFn: vi.fn() as any,
        createExecutorSignerFn: () => ({ getAddress: async () => '0x5000000000000000000000000000000000000005' } as any),
        loadPlanInputsFn: async () => ({
          scheduler: '0x3000000000000000000000000000000000000003',
          registry: '0x3000000000000000000000000000000000000003',
          baseEntries: [],
          targetEntries: [],
          effectiveMaxSlippage: 0.01,
          effectiveMaxPriceImpact: 0.01,
          notes: []
        })
      }
    })).rejects.toThrow('EXECUTOR_WALLET_NOT_REGISTRY');
  });

  it('skips when drift is below threshold', async () => {
    const calculateRebalancingFn = vi.fn(async () => ({ txData: '0x1234', requiredAllowances: [] }));

    const result = await rebalance_now({
      config,
      deps: {
        calculateRebalancingFn: calculateRebalancingFn as any,
        executeRebalancingFn: vi.fn() as any,
        createExecutorSignerFn: () => ({ getAddress: async () => '0x3000000000000000000000000000000000000003' } as any),
        loadPlanInputsFn: async () => ({
          scheduler: '0x3000000000000000000000000000000000000003',
          registry: '0x3000000000000000000000000000000000000003',
          baseEntries: [{ tokenAddress: '0xaaa', amount: '1' }],
          targetEntries: [{ tokenAddress: '0xbbb', allocation: 1 }],
          driftThresholdBps: 300,
          feedRegistry: '0x9000000000000000000000000000000000000009',
          effectiveMaxSlippage: 0.01,
          effectiveMaxPriceImpact: 0.01,
          notes: []
        }),
        checkDriftFn: async () => ({
          computable: true,
          maxDriftBps: 100,
          thresholdBps: 300,
          shouldRebalance: false,
          reason: 'Skipped: max drift 100 bps < threshold 300 bps.'
        })
      }
    });

    expect(result.executed).toBe(false);
    expect(result.skipped).toBe(true);
    expect(calculateRebalancingFn).toHaveBeenCalledTimes(0);
  });
});
