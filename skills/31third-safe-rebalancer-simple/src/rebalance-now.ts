import { calculateRebalancing, executeRebalancing, type RebalancingResponse } from '@31third/sdk';
import { Contract, JsonRpcProvider, Wallet, isAddress } from 'ethers';

import {
  aggregatorV3Abi,
  assetUniversePolicyAbi,
  erc20Abi,
  executorModuleAbi,
  slippagePolicyAbi,
  staticAllocationPolicyAbi,
  tokenFeedRegistryAbi
} from './contracts.js';

export interface RuntimeConfig {
  safeAddress: string;
  executorModuleAddress: string;
  executorWalletPrivateKey: string;
  apiKey: string;
  rpcUrl: string;
  chainId: number;
  apiBaseUrl: string;
  maxSlippage: number;
  maxPriceImpact: number;
  minTradeValue: number;
  skipBalanceValidation: boolean;
}

export interface TargetEntryInput {
  tokenAddress: string;
  allocation: number;
}

export interface RebalanceNowResult {
  executed: boolean;
  skipped: boolean;
  txHash?: string;
  scheduler: string;
  registry: string;
  executorWallet: string;
  baseEntriesCount: number;
  targetEntriesCount: number;
  maxDriftBps?: number;
  driftThresholdBps?: number;
  effectiveMaxSlippage: number;
  effectiveMaxPriceImpact: number;
  message: string;
}

interface PolicyState {
  assetUniverseAddress?: string;
  staticAllocationAddress?: string;
  slippageAddress?: string;
}

interface PlanInputs {
  scheduler: string;
  registry: string;
  baseEntries: Array<{ tokenAddress: string; amount: string }>;
  targetEntries: Array<{ tokenAddress: string; allocation: number }>;
  driftThresholdBps?: number;
  feedRegistry?: string;
  effectiveMaxSlippage: number;
  effectiveMaxPriceImpact: number;
  notes: string[];
}

interface DriftResult {
  computable: boolean;
  maxDriftBps: number;
  thresholdBps: number;
  shouldRebalance: boolean;
  reason: string;
}

interface RebalanceDeps {
  calculateRebalancingFn?: typeof calculateRebalancing;
  executeRebalancingFn?: typeof executeRebalancing;
  loadPlanInputsFn?: (
    config: RuntimeConfig,
    provider: JsonRpcProvider,
    manualTargetEntries?: TargetEntryInput[]
  ) => Promise<PlanInputs>;
  createExecutorSignerFn?: (config: RuntimeConfig, provider: JsonRpcProvider) => Wallet;
  checkDriftFn?: (
    config: RuntimeConfig,
    provider: JsonRpcProvider,
    targetEntries: Array<{ tokenAddress: string; allocation: number }>,
    driftThresholdBps: number,
    feedRegistry: string
  ) => Promise<DriftResult>;
}

const ZERO_ADDRESS = '0x0000000000000000000000000000000000000000';

function required(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing ${name}`);
  }
  return value;
}

function readPositiveNumber(name: string, fallback: number): number {
  const raw = process.env[name];
  if (!raw) return fallback;
  const parsed = Number(raw);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    throw new Error(`Invalid ${name}`);
  }
  return parsed;
}

export function readConfigFromEnv(): RuntimeConfig {
  const safeAddress = required('SAFE_ADDRESS');
  const executorModuleAddress = required('EXECUTOR_MODULE_ADDRESS');
  const rpcUrl = process.env.RPC_URL ?? 'https://mainnet.base.org';
  const apiKey = required('TOT_API_KEY');
  const executorWalletPrivateKey = required('EXECUTOR_WALLET_PRIVATE_KEY');
  const chainId = Number(process.env.CHAIN_ID ?? '8453');

  if (!Number.isInteger(chainId) || chainId <= 0) {
    throw new Error('Invalid CHAIN_ID');
  }
  if (!isAddress(safeAddress)) {
    throw new Error('Invalid SAFE_ADDRESS');
  }
  if (!isAddress(executorModuleAddress)) {
    throw new Error('Invalid EXECUTOR_MODULE_ADDRESS');
  }

  return {
    safeAddress,
    executorModuleAddress,
    executorWalletPrivateKey,
    apiKey,
    rpcUrl,
    chainId,
    apiBaseUrl: process.env.API_BASE_URL ?? 'https://api.31third.com/1.3',
    maxSlippage: readPositiveNumber('MAX_SLIPPAGE', 0.01),
    maxPriceImpact: readPositiveNumber('MAX_PRICE_IMPACT', 0.05),
    minTradeValue: readPositiveNumber('MIN_TRADE_VALUE', 0.1),
    skipBalanceValidation: (process.env.SKIP_BALANCE_VALIDATION ?? 'false').toLowerCase() === 'true'
  };
}

function normalizePolicyState(entry: any): { policy: string; policyType: string } {
  const policy = entry?.policy ?? (Array.isArray(entry) ? entry[0] : undefined);
  const policyType = entry?.policyType ?? (Array.isArray(entry) ? entry[1] : undefined);
  return {
    policy: typeof policy === 'string' ? policy : '',
    policyType: typeof policyType === 'string' ? policyType : ''
  };
}

function readPolicyAddresses(policies: Array<{ policy: string; policyType: string }>): PolicyState {
  const find = (name: string) => policies.find((p) => p.policyType.toLowerCase() === name)?.policy;
  return {
    assetUniverseAddress: find('assetuniverse'),
    staticAllocationAddress: find('staticallocation'),
    slippageAddress: find('slippage')
  };
}

async function defaultLoadPlanInputs(
  config: RuntimeConfig,
  provider: JsonRpcProvider,
  manualTargetEntries?: TargetEntryInput[]
): Promise<PlanInputs> {
  const executor = new Contract(config.executorModuleAddress, executorModuleAbi, provider);
  const [scheduler, registry] = await Promise.all([
    executor.scheduler() as Promise<string>,
    executor.registry() as Promise<string>
  ]);

  const policiesRaw = await executor.getPoliciesWithTypes();
  const policies = (policiesRaw as any[]).map(normalizePolicyState);
  const policyAddresses = readPolicyAddresses(policies);

  const notes: string[] = [];

  let baseEntries: Array<{ tokenAddress: string; amount: string }> = [];
  if (policyAddresses.assetUniverseAddress) {
    const assetUniverse = new Contract(policyAddresses.assetUniverseAddress, assetUniversePolicyAbi, provider);
    const assetUniverseTokens = await assetUniverse.getTokens() as string[];

    const balances = await Promise.all(
      assetUniverseTokens.map(async (tokenAddress) => {
        const token = new Contract(tokenAddress, erc20Abi, provider);
        const amount = await token.balanceOf(config.safeAddress) as bigint;
        return { tokenAddress, amount };
      })
    );

    baseEntries = balances
      .filter((entry) => entry.amount > 0n)
      .map((entry) => ({ tokenAddress: entry.tokenAddress, amount: entry.amount.toString() }));
  } else {
    notes.push('AssetUniverse policy not deployed; baseEntries defaulted to empty array.');
  }

  let targetEntries: Array<{ tokenAddress: string; allocation: number }> = [];
  let driftThresholdBps: number | undefined;
  let feedRegistry: string | undefined;

  if (policyAddresses.staticAllocationAddress) {
    const staticAllocation = new Contract(policyAddresses.staticAllocationAddress, staticAllocationPolicyAbi, provider);
    const [rawTargets, rawDriftThresholdBps, staticFeedRegistry] = await Promise.all([
      staticAllocation.getAllTargets() as Promise<any[]>,
      staticAllocation.driftThresholdBps() as Promise<bigint>,
      staticAllocation.feedRegistry() as Promise<string>
    ]);

    targetEntries = rawTargets.map((target) => {
      const tokenAddress = target?.token ?? (Array.isArray(target) ? target[0] : undefined);
      const bps = target?.bps ?? (Array.isArray(target) ? target[1] : undefined);
      if (typeof tokenAddress !== 'string' || typeof bps === 'undefined') {
        throw new Error('Invalid target entry on StaticAllocation policy.');
      }
      return {
        tokenAddress,
        allocation: Number(bps) / 10_000
      };
    });

    driftThresholdBps = Number(rawDriftThresholdBps);
    feedRegistry = staticFeedRegistry;
  } else if (manualTargetEntries && manualTargetEntries.length > 0) {
    targetEntries = manualTargetEntries;
    notes.push('StaticAllocation policy not deployed; using manually provided target entries.');
  } else {
    throw new Error(
      'Missing StaticAllocation policy on ExecutorModule. Cannot auto fetch target allocation. Please pass targetEntries manually.'
    );
  }

  let effectiveMaxSlippage = config.maxSlippage;
  let effectiveMaxPriceImpact = config.maxPriceImpact;
  if (policyAddresses.slippageAddress) {
    const slippagePolicy = new Contract(policyAddresses.slippageAddress, slippagePolicyAbi, provider);
    const bps = Number(await slippagePolicy.maxSlippageBps() as bigint);
    const adjusted = Math.max(0, bps / 10_000 - 0.001);
    effectiveMaxSlippage = adjusted;
    effectiveMaxPriceImpact = adjusted;
  } else {
    notes.push('Slippage policy not deployed; using configured/default maxSlippage/maxPriceImpact.');
  }

  return {
    scheduler,
    registry,
    baseEntries,
    targetEntries,
    driftThresholdBps,
    feedRegistry,
    effectiveMaxSlippage,
    effectiveMaxPriceImpact,
    notes
  };
}

function tenPow(exp: number | bigint): bigint {
  const e = BigInt(exp);
  if (e <= 0n) return 1n;
  return 10n ** e;
}

function abs(n: bigint): bigint {
  return n >= 0n ? n : -n;
}

async function defaultCheckDrift(
  config: RuntimeConfig,
  provider: JsonRpcProvider,
  targetEntries: Array<{ tokenAddress: string; allocation: number }>,
  driftThresholdBps: number,
  feedRegistry: string
): Promise<DriftResult> {
  if (!targetEntries.length || !feedRegistry || !isAddress(feedRegistry)) {
    return {
      computable: false,
      maxDriftBps: 0,
      thresholdBps: driftThresholdBps,
      shouldRebalance: true,
      reason: 'Drift precheck skipped: missing target entries or feed registry.'
    };
  }

  const registry = new Contract(feedRegistry, tokenFeedRegistryAbi, provider);

  const values = await Promise.all(
    targetEntries.map(async (target) => {
      const token = new Contract(target.tokenAddress, erc20Abi, provider);
      const [balance, tokenDecimalsRaw, feedAddress] = await Promise.all([
        token.balanceOf(config.safeAddress) as Promise<bigint>,
        token.decimals() as Promise<bigint>,
        registry.getFeed(target.tokenAddress) as Promise<string>
      ]);
      const tokenDecimals = Number(tokenDecimalsRaw);

      if (!feedAddress || feedAddress.toLowerCase() === ZERO_ADDRESS) {
        return { target, usd18: null as bigint | null };
      }

      const feed = new Contract(feedAddress, aggregatorV3Abi, provider);
      const [feedDecimalsRaw, latestRoundData] = await Promise.all([
        feed.decimals() as Promise<bigint>,
        feed.latestRoundData() as Promise<[bigint, bigint, bigint, bigint, bigint]>
      ]);
      const feedDecimals = Number(feedDecimalsRaw);

      const price = latestRoundData[1];
      if (price <= 0n) {
        return { target, usd18: null as bigint | null };
      }

      let usd18 = (balance * price) / tenPow(tokenDecimals);
      if (feedDecimals < 18) {
        usd18 *= tenPow(18 - feedDecimals);
      } else if (feedDecimals > 18) {
        usd18 /= tenPow(feedDecimals - 18);
      }

      return { target, usd18 };
    })
  );

  if (values.some((v) => v.usd18 === null)) {
    return {
      computable: false,
      maxDriftBps: 0,
      thresholdBps: driftThresholdBps,
      shouldRebalance: true,
      reason: 'Drift precheck skipped: one or more target tokens have missing/invalid feeds.'
    };
  }

  const totalUsd18 = values.reduce((acc, v) => acc + (v.usd18 as bigint), 0n);
  if (totalUsd18 <= 0n) {
    return {
      computable: false,
      maxDriftBps: 0,
      thresholdBps: driftThresholdBps,
      shouldRebalance: true,
      reason: 'Drift precheck skipped: portfolio value is zero.'
    };
  }

  let maxDriftBps = 0;
  for (const entry of values) {
    const currentWeightBps = Number(((entry.usd18 as bigint) * 10_000n) / totalUsd18);
    const targetWeightBps = Math.round(entry.target.allocation * 10_000);
    const drift = Number(abs(BigInt(currentWeightBps - targetWeightBps)));
    if (drift > maxDriftBps) {
      maxDriftBps = drift;
    }
  }

  const shouldRebalance = maxDriftBps >= driftThresholdBps;
  return {
    computable: true,
    maxDriftBps,
    thresholdBps: driftThresholdBps,
    shouldRebalance,
    reason: shouldRebalance
      ? `Drift check passed for execution: max drift ${maxDriftBps} bps >= threshold ${driftThresholdBps} bps.`
      : `Skipped: max drift ${maxDriftBps} bps < threshold ${driftThresholdBps} bps.`
  };
}

export async function rebalance_now(params?: {
  config?: RuntimeConfig;
  targetEntries?: TargetEntryInput[];
  deps?: RebalanceDeps;
}): Promise<RebalanceNowResult> {
  const config = params?.config ?? readConfigFromEnv();
  const deps = params?.deps ?? {};

  const calculateRebalancingFn = deps.calculateRebalancingFn ?? calculateRebalancing;
  const executeRebalancingFn = deps.executeRebalancingFn ?? executeRebalancing;
  const loadPlanInputsFn = deps.loadPlanInputsFn ?? defaultLoadPlanInputs;
  const createExecutorSignerFn = deps.createExecutorSignerFn ?? ((cfg, provider) => new Wallet(cfg.executorWalletPrivateKey, provider));
  const checkDriftFn = deps.checkDriftFn ?? defaultCheckDrift;

  const provider = new JsonRpcProvider(config.rpcUrl);
  const executorSigner = createExecutorSignerFn(config, provider);
  const executorWallet = await executorSigner.getAddress();
  const {
    scheduler,
    registry,
    baseEntries,
    targetEntries,
    driftThresholdBps,
    feedRegistry,
    effectiveMaxSlippage,
    effectiveMaxPriceImpact,
    notes
  } = await loadPlanInputsFn(config, provider, params?.targetEntries);

  if (scheduler.toLowerCase() !== registry.toLowerCase()) {
    throw new Error(`SCHEDULER_REGISTRY_MISMATCH: scheduler=${scheduler} registry=${registry}`);
  }
  if (executorWallet.toLowerCase() === ZERO_ADDRESS) {
    throw new Error('EXECUTOR_WALLET_ZERO_ADDRESS: executor wallet cannot be zero address.');
  }
  if (executorWallet.toLowerCase() !== registry.toLowerCase()) {
    throw new Error(`EXECUTOR_WALLET_NOT_REGISTRY: wallet=${executorWallet} registry=${registry}`);
  }

  let maxDriftBps: number | undefined;
  if (typeof driftThresholdBps === 'number' && targetEntries.length > 0 && feedRegistry) {
    const drift = await checkDriftFn(config, provider, targetEntries, driftThresholdBps, feedRegistry);
    if (drift.computable) {
      maxDriftBps = drift.maxDriftBps;
    }
    if (!drift.shouldRebalance) {
      return {
        executed: false,
        skipped: true,
        scheduler,
        registry,
        executorWallet,
        baseEntriesCount: baseEntries.length,
        targetEntriesCount: targetEntries.length,
        maxDriftBps,
        driftThresholdBps: drift.thresholdBps,
        effectiveMaxSlippage,
        effectiveMaxPriceImpact,
        message: drift.reason
      };
    }
    if (!drift.computable) {
      notes.push(drift.reason);
    }
  }

  const rebalancing = await calculateRebalancingFn({
    apiBaseUrl: config.apiBaseUrl,
    apiKey: config.apiKey,
    chainId: config.chainId,
    payload: {
      wallet: config.safeAddress,
      signer: config.safeAddress,
      chainId: config.chainId,
      baseEntries,
      targetEntries,
      maxSlippage: effectiveMaxSlippage,
      maxPriceImpact: effectiveMaxPriceImpact,
      minTradeValue: config.minTradeValue,
      skipBalanceValidation: config.skipBalanceValidation
    }
  });

  const tx = await executeRebalancingFn({
    signer: executorSigner,
    executorModule: config.executorModuleAddress,
    rebalancing: rebalancing as RebalancingResponse
  });
  await tx.wait();

  return {
    executed: true,
    skipped: false,
    txHash: tx.hash,
    scheduler,
    registry,
    executorWallet,
    baseEntriesCount: baseEntries.length,
    targetEntriesCount: targetEntries.length,
    maxDriftBps,
    driftThresholdBps,
    effectiveMaxSlippage,
    effectiveMaxPriceImpact,
    message: [
      'Rebalance executed using deployed on-chain policies.',
      ...notes
    ].join(' ')
  };
}
