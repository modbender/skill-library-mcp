import { describe, expect, it, vi } from 'vitest';
import { encodeFunctionData, type Address, type PublicClient } from 'viem';

import { checkDrift, validateTrade } from '../src/balancer.js';
import { automation, check_drift, execute_rebalance, plan_rebalance, readConfigFromEnv, rebalance_now, type RuntimeConfig, validate_trade } from '../index.js';
import type { BatchTrade, BatchTradeConfig, TokenApproval } from '../src/executor.js';
import { batchTradeAbi } from '../src/contracts.js';
import type { PolicySnapshot } from '../src/policies.js';

const SAFE = '0x1000000000000000000000000000000000000001' as Address;
const REGISTRY = '0x1d4999242A24C8588c4f5dB7dFF1D74Df6bC746A' as Address;
const CUSTOM_REGISTRY = '0x2000000000000000000000000000000000000002' as Address;
const TOKEN_A = '0x3000000000000000000000000000000000000003' as Address;
const TOKEN_B = '0x4000000000000000000000000000000000000004' as Address;
const FEED_A = '0x5000000000000000000000000000000000000005' as Address;
const FEED_B = '0x6000000000000000000000000000000000000006' as Address;
const NOW_SEC = BigInt(Math.floor(Date.now() / 1000));
const EXECUTOR_MODULE = '0x7000000000000000000000000000000000000007' as Address;
const SAMPLE_TRADES: BatchTrade[] = [{
  exchangeName: 'mock',
  from: TOKEN_A,
  fromAmount: 100n,
  to: TOKEN_B,
  minToReceiveBeforeFees: 90n,
  data: '0x1234',
  signature: '0xabcd'
}];
const SAMPLE_APPROVALS: TokenApproval[] = [{ token: TOKEN_A, amount: 100n }];
const SAMPLE_CONFIG: BatchTradeConfig = { checkFeelessWallets: true, revertOnError: true };
const SAMPLE_REBALANCING = {
  txData: encodeFunctionData({
    abi: batchTradeAbi,
    functionName: 'batchTrade',
    args: [SAMPLE_TRADES, SAMPLE_CONFIG]
  }),
  requiredAllowances: [{ token: { address: TOKEN_A }, neededAllowance: '100' }]
};

function mockPublicClient(readContractImpl: (args: { address: Address; functionName: string; args?: unknown[] }) => unknown): PublicClient {
  return {
    readContract: vi.fn(async (args: { address: Address; functionName: string; args?: unknown[] }) => readContractImpl(args))
  } as unknown as PublicClient;
}

describe('31third-safe-rebalancer', () => {
  it('checkDrift flags drift over threshold', async () => {
    const policies: PolicySnapshot = {
      assetUniverseTokens: [TOKEN_A, TOKEN_B],
      targetAllocations: [
        { token: TOKEN_A, bps: 5_000 },
        { token: TOKEN_B, bps: 5_000 }
      ],
      driftThresholdBps: 300
    };

    const publicClient = mockPublicClient(({ address, functionName, args }) => {
      if (address === TOKEN_A && functionName === 'symbol') return 'BTC';
      if (address === TOKEN_B && functionName === 'symbol') return 'ETH';
      if ((address === TOKEN_A || address === TOKEN_B) && functionName === 'decimals') return 18;
      if (address === TOKEN_A && functionName === 'balanceOf' && args?.[0] === SAFE) return 54n * 10n ** 18n;
      if (address === TOKEN_B && functionName === 'balanceOf' && args?.[0] === SAFE) return 46n * 10n ** 18n;
      if (address === REGISTRY && functionName === 'getFeed' && args?.[0] === TOKEN_A) return FEED_A;
      if (address === REGISTRY && functionName === 'getFeed' && args?.[0] === TOKEN_B) return FEED_B;
      if ((address === FEED_A || address === FEED_B) && functionName === 'decimals') return 8;
      if (address === FEED_A && functionName === 'latestRoundData') return [1n, 1n * 10n ** 8n, 0n, NOW_SEC, 1n];
      if (address === FEED_B && functionName === 'latestRoundData') return [1n, 1n * 10n ** 8n, 0n, NOW_SEC, 1n];
      throw new Error(`Unhandled readContract ${address}:${functionName}`);
    });

    const result = await checkDrift({
      publicClient,
      safeAddress: SAFE,
      tokenFeedRegistry: REGISTRY,
      policies
    });

    expect(result.exceedsThreshold).toBe(true);
    expect(result.maxDriftBps).toBe(400);
    expect(result.explanation).toContain('BTC is at 54.00%');
  });

  it('validateTrade rejects token outside asset universe', async () => {
    const policies: PolicySnapshot = {
      assetUniverseTokens: [TOKEN_A],
      targetAllocations: [],
      maxSlippageBps: 100
    };

    const publicClient = mockPublicClient(() => {
      throw new Error('Unexpected chain call');
    });

    const result = await validateTrade({
      publicClient,
      tokenFeedRegistry: REGISTRY,
      policies,
      trade: {
        from: TOKEN_A,
        to: TOKEN_B,
        fromAmount: 10n,
        minToReceiveBeforeFees: 10n
      }
    });

    expect(result.ok).toBe(false);
    expect(result.reason).toContain('Asset Universe violation');
  });

  it('automation returns notification when 6-hour heartbeat is due and drift is high', async () => {
    const config: RuntimeConfig = {
      safeAddress: SAFE,
      chainId: 8453,
      rpcUrl: 'https://mainnet.base.org',
      executorModuleAddress: '0x7000000000000000000000000000000000000007'
    };

    const policies: PolicySnapshot = {
      assetUniverseTokens: [TOKEN_A, TOKEN_B],
      targetAllocations: [
        { token: TOKEN_A, bps: 5_000 },
        { token: TOKEN_B, bps: 5_000 }
      ],
      tokenFeedRegistry: REGISTRY,
      driftThresholdBps: 300
    };

    const publicClient = mockPublicClient(({ address, functionName, args }) => {
      if (address === TOKEN_A && functionName === 'symbol') return 'BTC';
      if (address === TOKEN_B && functionName === 'symbol') return 'ETH';
      if ((address === TOKEN_A || address === TOKEN_B) && functionName === 'decimals') return 18;
      if (address === TOKEN_A && functionName === 'balanceOf' && args?.[0] === SAFE) return 54n * 10n ** 18n;
      if (address === TOKEN_B && functionName === 'balanceOf' && args?.[0] === SAFE) return 46n * 10n ** 18n;
      if (address === REGISTRY && functionName === 'getFeed' && args?.[0] === TOKEN_A) return FEED_A;
      if (address === REGISTRY && functionName === 'getFeed' && args?.[0] === TOKEN_B) return FEED_B;
      if ((address === FEED_A || address === FEED_B) && functionName === 'decimals') return 8;
      if (address === FEED_A && functionName === 'latestRoundData') return [1n, 1n * 10n ** 8n, 0n, NOW_SEC, 1n];
      if (address === FEED_B && functionName === 'latestRoundData') return [1n, 1n * 10n ** 8n, 0n, NOW_SEC, 1n];
      throw new Error(`Unhandled readContract ${address}:${functionName}`);
    });

    const result = await automation({
      config,
      state: { lastHeartbeatAt: 0 },
      nowMs: 6 * 60 * 60 * 1000 + 1,
      publicClient,
      policies
    });

    expect(result.checked).toBe(true);
    expect(result.notify).toBe(true);
    expect(result.message).toContain('Drift alert');
  });

  it('check_drift uses tokenFeedRegistry from policy snapshot', async () => {
    const config: RuntimeConfig = {
      safeAddress: SAFE,
      chainId: 8453,
      rpcUrl: 'https://mainnet.base.org',
      executorModuleAddress: '0x7000000000000000000000000000000000000007'
    };

    const policies: PolicySnapshot = {
      assetUniverseTokens: [TOKEN_A, TOKEN_B],
      targetAllocations: [
        { token: TOKEN_A, bps: 5_000 },
        { token: TOKEN_B, bps: 5_000 }
      ],
      tokenFeedRegistry: CUSTOM_REGISTRY,
      driftThresholdBps: 300
    };

    const publicClient = mockPublicClient(({ address, functionName, args }) => {
      if (address === TOKEN_A && functionName === 'symbol') return 'BTC';
      if (address === TOKEN_B && functionName === 'symbol') return 'ETH';
      if ((address === TOKEN_A || address === TOKEN_B) && functionName === 'decimals') return 18;
      if (address === TOKEN_A && functionName === 'balanceOf' && args?.[0] === SAFE) return 54n * 10n ** 18n;
      if (address === TOKEN_B && functionName === 'balanceOf' && args?.[0] === SAFE) return 46n * 10n ** 18n;
      if (address === CUSTOM_REGISTRY && functionName === 'getFeed' && args?.[0] === TOKEN_A) return FEED_A;
      if (address === CUSTOM_REGISTRY && functionName === 'getFeed' && args?.[0] === TOKEN_B) return FEED_B;
      if ((address === FEED_A || address === FEED_B) && functionName === 'decimals') return 8;
      if (address === FEED_A && functionName === 'latestRoundData') return [1n, 1n * 10n ** 8n, 0n, NOW_SEC, 1n];
      if (address === FEED_B && functionName === 'latestRoundData') return [1n, 1n * 10n ** 8n, 0n, NOW_SEC, 1n];
      throw new Error(`Unhandled readContract ${address}:${functionName}`);
    });

    const result = await check_drift({
      config,
      publicClient,
      policies
    });

    expect(result.shouldRebalance).toBe(true);
    expect(result.maxDriftBps).toBe(400);
  });

  it('validate_trade uses tokenFeedRegistry from policy snapshot', async () => {
    const config: RuntimeConfig = {
      safeAddress: SAFE,
      chainId: 8453,
      rpcUrl: 'https://mainnet.base.org',
      executorModuleAddress: '0x7000000000000000000000000000000000000007'
    };

    const policies: PolicySnapshot = {
      assetUniverseTokens: [TOKEN_A, TOKEN_B],
      targetAllocations: [],
      tokenFeedRegistry: CUSTOM_REGISTRY,
      maxSlippageBps: 100
    };

    const publicClient = mockPublicClient(({ address, functionName, args }) => {
      if ((address === TOKEN_A || address === TOKEN_B) && functionName === 'decimals') return 18;
      if (address === CUSTOM_REGISTRY && functionName === 'getFeed' && args?.[0] === TOKEN_A) return FEED_A;
      if (address === CUSTOM_REGISTRY && functionName === 'getFeed' && args?.[0] === TOKEN_B) return FEED_B;
      if ((address === FEED_A || address === FEED_B) && functionName === 'decimals') return 8;
      if (address === FEED_A && functionName === 'latestRoundData') return [1n, 1n * 10n ** 8n, 0n, NOW_SEC, 1n];
      if (address === FEED_B && functionName === 'latestRoundData') return [1n, 1n * 10n ** 8n, 0n, NOW_SEC, 1n];
      throw new Error(`Unhandled readContract ${address}:${functionName}`);
    });

    const result = await validate_trade({
      config,
      publicClient,
      policies,
      trade: {
        from: TOKEN_A,
        to: TOKEN_B,
        fromAmount: 10n * 10n ** 18n,
        minToReceiveBeforeFees: 10n * 10n ** 18n
      }
    });

    expect(result.valid).toBe(true);
  });

  it('check_drift is non-alerting when StaticAllocation policy is absent', async () => {
    const config: RuntimeConfig = {
      safeAddress: SAFE,
      chainId: 8453,
      rpcUrl: 'https://mainnet.base.org',
      executorModuleAddress: '0x7000000000000000000000000000000000000007'
    };

    const policies: PolicySnapshot = {
      assetUniverseTokens: [TOKEN_A, TOKEN_B],
      targetAllocations: []
    };

    const publicClient = mockPublicClient(() => {
      throw new Error('Unexpected chain call');
    });

    const result = await check_drift({
      config,
      publicClient,
      policies
    });

    expect(result.shouldRebalance).toBe(false);
    expect(result.maxDriftBps).toBe(0);
    expect(result.explanation).toContain('No StaticAllocation policy');
  });

  it('validate_trade rejects stale oracle data when max age is exceeded', async () => {
    const config: RuntimeConfig = {
      safeAddress: SAFE,
      chainId: 8453,
      rpcUrl: 'https://mainnet.base.org',
      executorModuleAddress: '0x7000000000000000000000000000000000000007',
      oracleMaxAgeSeconds: 60
    };

    const policies: PolicySnapshot = {
      assetUniverseTokens: [TOKEN_A, TOKEN_B],
      targetAllocations: [],
      tokenFeedRegistry: CUSTOM_REGISTRY,
      maxSlippageBps: 100
    };

    const staleSec = NOW_SEC - 3600n;
    const publicClient = mockPublicClient(({ address, functionName, args }) => {
      if ((address === TOKEN_A || address === TOKEN_B) && functionName === 'decimals') return 18;
      if (address === CUSTOM_REGISTRY && functionName === 'getFeed' && args?.[0] === TOKEN_A) return FEED_A;
      if (address === CUSTOM_REGISTRY && functionName === 'getFeed' && args?.[0] === TOKEN_B) return FEED_B;
      if ((address === FEED_A || address === FEED_B) && functionName === 'decimals') return 8;
      if (address === FEED_A && functionName === 'latestRoundData') return [1n, 1n * 10n ** 8n, 0n, staleSec, 1n];
      if (address === FEED_B && functionName === 'latestRoundData') return [1n, 1n * 10n ** 8n, 0n, staleSec, 1n];
      throw new Error(`Unhandled readContract ${address}:${functionName}`);
    });

    const result = await validate_trade({
      config,
      publicClient,
      policies,
      trade: {
        from: TOKEN_A,
        to: TOKEN_B,
        fromAmount: 10n * 10n ** 18n,
        minToReceiveBeforeFees: 10n * 10n ** 18n
      }
    });

    expect(result.valid).toBe(false);
    expect(result.reason).toContain('stale');
  });

  it('plan_rebalance fails fast when TOT_API_KEY is missing', async () => {
    const config: RuntimeConfig = {
      safeAddress: SAFE,
      chainId: 8453,
      rpcUrl: 'https://mainnet.base.org',
      executorModuleAddress: '0x7000000000000000000000000000000000000007'
    };

    await expect(plan_rebalance({
      config,
      signerAddress: SAFE,
      policies: {
        assetUniverseTokens: [TOKEN_A],
        targetAllocations: [{ token: TOKEN_A, bps: 10_000 }]
      }
    })).rejects.toThrow('TOT_API_KEY');
  });

  it('plan_rebalance fails fast when StaticAllocation targets are missing', async () => {
    const config: RuntimeConfig = {
      safeAddress: SAFE,
      chainId: 8453,
      rpcUrl: 'https://mainnet.base.org',
      executorModuleAddress: '0x7000000000000000000000000000000000000007',
      totApiKey: 'test-key'
    };

    await expect(plan_rebalance({
      config,
      signerAddress: SAFE,
      policies: {
        assetUniverseTokens: [TOKEN_A],
        targetAllocations: []
      }
    })).rejects.toThrow('no StaticAllocation policy');
  });

  it('automation uses configured heartbeat interval', async () => {
    const config: RuntimeConfig = {
      safeAddress: SAFE,
      chainId: 8453,
      rpcUrl: 'https://mainnet.base.org',
      executorModuleAddress: '0x7000000000000000000000000000000000000007',
      heartbeatIntervalSeconds: 60
    };

    const policies: PolicySnapshot = {
      assetUniverseTokens: [TOKEN_A],
      targetAllocations: []
    };

    const publicClient = mockPublicClient(() => {
      throw new Error('Unexpected chain call');
    });

    const result = await automation({
      config,
      state: { lastHeartbeatAt: 0 },
      nowMs: 60_001,
      publicClient,
      policies
    });

    expect(result.checked).toBe(true);
    expect(result.notify).toBe(false);
    expect(result.nextHeartbeatInSeconds).toBe(60);
  });

  it('readConfigFromEnv rejects malformed numeric env vars', () => {
    const originalEnv = { ...process.env };
    process.env.SAFE_ADDRESS = SAFE;
    process.env.EXECUTOR_MODULE_ADDRESS = '0x7000000000000000000000000000000000000007';
    process.env.CHAIN_ID = 'not-a-number';
    process.env.ORACLE_MAX_AGE_SECONDS = '3600';
    process.env.HEARTBEAT_INTERVAL_SECONDS = '21600';

    expect(() => readConfigFromEnv()).toThrow('CHAIN_ID');
    process.env = originalEnv;
  });

  it('execute_rebalance fails early on checkPoliciesVerbose violation', async () => {
    const config: RuntimeConfig = {
      safeAddress: SAFE,
      chainId: 8453,
      rpcUrl: 'https://mainnet.base.org',
      executorModuleAddress: EXECUTOR_MODULE
    };

    const publicClient = {
      readContract: vi.fn(async (args: { functionName: string }) => {
        if (args.functionName === 'scheduler') return EXECUTOR_MODULE;
        if (args.functionName === 'registry') return EXECUTOR_MODULE;
        return [false, TOKEN_A, 'Policy failed'];
      })
    } as unknown as PublicClient;
    const walletClient = {
      account: { address: EXECUTOR_MODULE },
      writeContract: vi.fn(async () => '0xabc')
    } as any;

    await expect(execute_rebalance({
      config,
      publicClient,
      walletClient,
      trades: SAMPLE_TRADES,
      approvals: SAMPLE_APPROVALS,
      batchConfig: SAMPLE_CONFIG
    })).rejects.toThrow('FAILED_POLICY_CHECK');
  });

  it('execute_rebalance retries once for unknown failures and then succeeds', async () => {
    const config: RuntimeConfig = {
      safeAddress: SAFE,
      chainId: 8453,
      rpcUrl: 'https://mainnet.base.org',
      executorModuleAddress: EXECUTOR_MODULE
    };

    const simulateContract = vi.fn(async () => ({}));
    const publicClient = {
      readContract: vi.fn(async (args: { functionName: string }) => {
        if (args.functionName === 'scheduler') return EXECUTOR_MODULE;
        if (args.functionName === 'registry') return EXECUTOR_MODULE;
        return [true, TOKEN_A, 'ok'];
      }),
      simulateContract
    } as unknown as PublicClient;
    const writeContract = vi.fn()
      .mockRejectedValueOnce(new Error('temporary rpc issue'))
      .mockResolvedValueOnce('0xabc');
    const walletClient = { account: { address: EXECUTOR_MODULE }, writeContract } as any;

    const result = await execute_rebalance({
      config,
      publicClient,
      walletClient,
      trades: SAMPLE_TRADES,
      approvals: SAMPLE_APPROVALS,
      batchConfig: SAMPLE_CONFIG,
      retryDelayMs: 0
    });

    expect(result.txHash).toBe('0xabc');
    expect(writeContract).toHaveBeenCalledTimes(2);
  });

  it('execute_rebalance passes resolved wallet address when walletClient.account is missing', async () => {
    const config: RuntimeConfig = {
      safeAddress: SAFE,
      chainId: 8453,
      rpcUrl: 'https://mainnet.base.org',
      executorModuleAddress: EXECUTOR_MODULE
    };

    const simulateContract = vi.fn(async () => ({}));
    const publicClient = {
      readContract: vi.fn(async (args: { functionName: string }) => {
        if (args.functionName === 'scheduler') return EXECUTOR_MODULE;
        if (args.functionName === 'registry') return EXECUTOR_MODULE;
        return [true, TOKEN_A, 'ok'];
      }),
      simulateContract
    } as unknown as PublicClient;
    const writeContract = vi.fn(async () => '0xabc');
    const walletClient = {
      getAddresses: vi.fn(async () => [EXECUTOR_MODULE]),
      writeContract
    } as any;

    const result = await execute_rebalance({
      config,
      publicClient,
      walletClient,
      trades: SAMPLE_TRADES,
      approvals: SAMPLE_APPROVALS,
      batchConfig: SAMPLE_CONFIG,
      retryDelayMs: 0
    });

    expect(result.txHash).toBe('0xabc');
    expect(simulateContract).toHaveBeenCalledTimes(1);
    expect(writeContract).toHaveBeenCalledTimes(1);
    expect((simulateContract as any).mock.calls[0][0].account).toBe(EXECUTOR_MODULE);
    expect((writeContract as any).mock.calls[0][0].account).toBe(EXECUTOR_MODULE);
  });

  it('execute_rebalance classifies min-trade-value as skipped', async () => {
    const config: RuntimeConfig = {
      safeAddress: SAFE,
      chainId: 8453,
      rpcUrl: 'https://mainnet.base.org',
      executorModuleAddress: EXECUTOR_MODULE
    };

    const publicClient = {
      readContract: vi.fn(async (args: { functionName: string }) => {
        if (args.functionName === 'scheduler') return EXECUTOR_MODULE;
        if (args.functionName === 'registry') return EXECUTOR_MODULE;
        return [true, TOKEN_A, 'ok'];
      }),
      simulateContract: vi.fn(async () => ({}))
    } as unknown as PublicClient;
    const walletClient = {
      account: { address: EXECUTOR_MODULE },
      writeContract: vi.fn(async () => {
        throw new Error('minimum trade value threshold not reached');
      })
    } as any;

    await expect(execute_rebalance({
      config,
      publicClient,
      walletClient,
      trades: SAMPLE_TRADES,
      approvals: SAMPLE_APPROVALS,
      batchConfig: SAMPLE_CONFIG,
      retryDelayMs: 0
    })).rejects.toThrow('SKIPPED_MIN_TRADE_VALUE');
  });

  it('execute_rebalance classifies token-not-tradeable as failed', async () => {
    const config: RuntimeConfig = {
      safeAddress: SAFE,
      chainId: 8453,
      rpcUrl: 'https://mainnet.base.org',
      executorModuleAddress: EXECUTOR_MODULE
    };

    const publicClient = {
      readContract: vi.fn(async (args: { functionName: string }) => {
        if (args.functionName === 'scheduler') return EXECUTOR_MODULE;
        if (args.functionName === 'registry') return EXECUTOR_MODULE;
        return [true, TOKEN_A, 'ok'];
      }),
      simulateContract: vi.fn(async () => ({}))
    } as unknown as PublicClient;
    const walletClient = {
      account: { address: EXECUTOR_MODULE },
      writeContract: vi.fn(async () => {
        throw new Error('tokenNotSellable');
      })
    } as any;

    await expect(execute_rebalance({
      config,
      publicClient,
      walletClient,
      trades: SAMPLE_TRADES,
      approvals: SAMPLE_APPROVALS,
      batchConfig: SAMPLE_CONFIG,
      retryDelayMs: 0
    })).rejects.toThrow('FAILED_TOKEN_NOT_TRADEABLE');
  });

  it('execute_rebalance fast-fails when scheduler and registry differ', async () => {
    const config: RuntimeConfig = {
      safeAddress: SAFE,
      chainId: 8453,
      rpcUrl: 'https://mainnet.base.org',
      executorModuleAddress: EXECUTOR_MODULE
    };

    const publicClient = {
      readContract: vi.fn(async (args: { functionName: string }) => {
        if (args.functionName === 'scheduler') return TOKEN_A;
        if (args.functionName === 'registry') return TOKEN_B;
        return [true, TOKEN_A, 'ok'];
      })
    } as unknown as PublicClient;
    const walletClient = { account: { address: EXECUTOR_MODULE }, writeContract: vi.fn(async () => '0xabc') } as any;

    await expect(execute_rebalance({
      config,
      publicClient,
      walletClient,
      trades: SAMPLE_TRADES,
      approvals: SAMPLE_APPROVALS,
      batchConfig: SAMPLE_CONFIG
    })).rejects.toThrow(`SCHEDULER_REGISTRY_MISMATCH: scheduler=${TOKEN_A} registry=${TOKEN_B}`);
  });

  it('execute_rebalance fast-fails when signer wallet is not registry', async () => {
    const config: RuntimeConfig = {
      safeAddress: SAFE,
      chainId: 8453,
      rpcUrl: 'https://mainnet.base.org',
      executorModuleAddress: EXECUTOR_MODULE
    };

    const publicClient = {
      readContract: vi.fn(async (args: { functionName: string }) => {
        if (args.functionName === 'scheduler') return TOKEN_A;
        if (args.functionName === 'registry') return TOKEN_A;
        return [true, TOKEN_A, 'ok'];
      })
    } as unknown as PublicClient;
    const walletClient = {
      account: { address: TOKEN_B },
      writeContract: vi.fn(async () => '0xabc')
    } as any;

    await expect(execute_rebalance({
      config,
      publicClient,
      walletClient,
      trades: SAMPLE_TRADES,
      approvals: SAMPLE_APPROVALS,
      batchConfig: SAMPLE_CONFIG
    })).rejects.toThrow(`EXECUTOR_WALLET_NOT_REGISTRY: wallet=${TOKEN_B} registry=${TOKEN_A} scheduler=${TOKEN_A}`);
  });

  it('execute_rebalance fails when executor wallet address is zero', async () => {
    const config: RuntimeConfig = {
      safeAddress: SAFE,
      chainId: 8453,
      rpcUrl: 'https://mainnet.base.org',
      executorModuleAddress: EXECUTOR_MODULE
    };

    const publicClient = {
      readContract: vi.fn(async (args: { functionName: string }) => {
        if (args.functionName === 'scheduler') return TOKEN_A;
        if (args.functionName === 'registry') return TOKEN_A;
        return [true, TOKEN_A, 'ok'];
      })
    } as unknown as PublicClient;
    const walletClient = {
      account: { address: '0x0000000000000000000000000000000000000000' as Address },
      writeContract: vi.fn(async () => '0xabc')
    } as any;

    await expect(execute_rebalance({
      config,
      publicClient,
      walletClient,
      trades: SAMPLE_TRADES,
      approvals: SAMPLE_APPROVALS,
      batchConfig: SAMPLE_CONFIG
    })).rejects.toThrow('EXECUTOR_WALLET_ZERO_ADDRESS');
  });

  it('rebalance_now fails when executor wallet is not set', async () => {
    const config: RuntimeConfig = {
      safeAddress: SAFE,
      chainId: 8453,
      rpcUrl: 'https://mainnet.base.org',
      executorModuleAddress: EXECUTOR_MODULE
    };

    await expect(rebalance_now({
      config,
      publicClient: { readContract: vi.fn(async () => [true, TOKEN_A, 'ok']) } as unknown as PublicClient,
      walletClient: undefined
    })).rejects.toThrow('EXECUTOR_WALLET_NOT_SET');
  });

  it('execute_rebalance accepts sdk rebalancing payload directly', async () => {
    const config: RuntimeConfig = {
      safeAddress: SAFE,
      chainId: 8453,
      rpcUrl: 'https://mainnet.base.org',
      executorModuleAddress: EXECUTOR_MODULE
    };

    const simulateContract = vi.fn(async () => ({}));
    const publicClient = {
      readContract: vi.fn(async (args: { functionName: string }) => {
        if (args.functionName === 'scheduler') return EXECUTOR_MODULE;
        if (args.functionName === 'registry') return EXECUTOR_MODULE;
        return [true, TOKEN_A, 'ok'];
      }),
      simulateContract
    } as unknown as PublicClient;
    const walletClient = {
      account: { address: EXECUTOR_MODULE },
      writeContract: vi.fn(async () => '0xabc')
    } as any;

    const result = await execute_rebalance({
      config,
      publicClient,
      walletClient,
      rebalancing: SAMPLE_REBALANCING
    });

    expect(result.txHash).toBe('0xabc');
    expect(simulateContract).toHaveBeenCalledTimes(1);
  });

  it('rebalance_now skips when no target allocation policy is present', async () => {
    const config: RuntimeConfig = {
      safeAddress: SAFE,
      chainId: 8453,
      rpcUrl: 'https://mainnet.base.org',
      executorModuleAddress: EXECUTOR_MODULE
    };

    const walletClient = {
      account: { address: SAFE },
      writeContract: vi.fn(async () => '0xabc')
    } as any;
    const publicClient = {
      readContract: vi.fn(async () => [true, TOKEN_A, 'ok']),
      simulateContract: vi.fn(async () => ({}))
    } as unknown as PublicClient;

    const result = await rebalance_now({
      config,
      publicClient,
      walletClient,
      policies: {
        assetUniverseTokens: [TOKEN_A],
        targetAllocations: []
      }
    });

    expect(result.executed).toBe(false);
    expect(result.skipped).toBe(true);
  });

  it('rebalance_now executes in one step when forced', async () => {
    const config: RuntimeConfig = {
      safeAddress: SAFE,
      chainId: 8453,
      rpcUrl: 'https://mainnet.base.org',
      executorModuleAddress: EXECUTOR_MODULE,
      totApiKey: 'test-key'
    };

    const originalFetch = globalThis.fetch;
    try {
      const txData = encodeFunctionData({
        abi: batchTradeAbi,
        functionName: 'batchTrade',
        args: [SAMPLE_TRADES, SAMPLE_CONFIG]
      });
      globalThis.fetch = vi.fn(async () => ({
        ok: true,
        json: async () => ({
          txData,
          requiredAllowances: [{ token: { address: TOKEN_A }, neededAllowance: '100' }]
        })
      })) as unknown as typeof fetch;

      const walletClient = {
        account: { address: EXECUTOR_MODULE },
        writeContract: vi.fn(async () => '0xabc')
      } as any;
      const publicClient = {
        readContract: vi.fn(async (args: { functionName: string }) => {
          if (args.functionName === 'scheduler') return EXECUTOR_MODULE;
          if (args.functionName === 'registry') return EXECUTOR_MODULE;
          if (args.functionName === 'checkPoliciesVerbose') return [true, TOKEN_A, 'ok'];
          return 0n;
        }),
        simulateContract: vi.fn(async () => ({}))
      } as unknown as PublicClient;

      const result = await rebalance_now({
        config,
        publicClient,
        walletClient,
        policies: {
          assetUniverseTokens: [],
          targetAllocations: [{ token: TOKEN_A, bps: 10_000 }]
        },
        force: true
      });

      expect(result.executed).toBe(true);
      expect(result.skipped).toBe(false);
      expect(result.txHash).toBe('0xabc');
    } finally {
      globalThis.fetch = originalFetch;
    }
  });
});
