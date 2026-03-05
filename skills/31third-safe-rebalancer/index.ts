import { privateKeyToAccount } from 'viem/accounts';
import { createPublicClient, createWalletClient, formatUnits, http, isAddress, type Address, type Chain, type PublicClient, type WalletClient } from 'viem';

import { buildBaseEntriesFromAssetUniverse, checkDrift, planRebalancingWithSdk, validateTrade, type TradeCandidate } from './src/balancer.js';
import { HARDCODED_TOKEN_FEED_REGISTRY_ADDRESS } from './src/contracts.js';
import {
  checkPoliciesVerbose,
  decodeRebalancingTxData,
  executeTradeNow,
  normalizeRebalancingAllowances,
  simulateExecuteTradeNow,
  type BatchTrade,
  type BatchTradeConfig,
  type RebalancingExecutionInput,
  type TokenApproval
} from './src/executor.js';
import { readPolicySnapshot, type PolicySnapshot } from './src/policies.js';

export interface RuntimeConfig {
  safeAddress: Address;
  chainId: number;
  rpcUrl: string;
  executorModuleAddress: Address;
  oracleMaxAgeSeconds?: number;
  heartbeatIntervalSeconds?: number;
  totApiKey?: string;
  executorWalletPrivateKey?: `0x${string}`;
}

export interface AutomationState {
  lastHeartbeatAt?: number;
}

export interface DriftToolResult {
  shouldRebalance: boolean;
  thresholdBps: number;
  maxDriftBps: number;
  explanation: string;
  why: string;
  tokens: Array<{
    token: Address;
    symbol: string;
    currentWeightPct: string;
    targetWeightPct: string;
    driftBps: number;
  }>;
}

export interface ValidationToolResult {
  valid: boolean;
  reason: string;
  minAllowedToReceive?: string;
}

export interface AutomationResult {
  checked: boolean;
  nextHeartbeatInSeconds: number;
  notify: boolean;
  message: string;
}

export interface HelpToolResult {
  summary: string;
  capabilities: string[];
  requiredEnv: string[];
  setupSteps: string[];
}

export interface PlanRebalanceResult {
  why: string;
  response: RebalancingExecutionInput;
}

export interface RebalanceNowResult {
  executed: boolean;
  skipped: boolean;
  reason: string;
  txHash?: `0x${string}`;
}

const ZERO_ADDRESS = '0x0000000000000000000000000000000000000000';

function assertAddress(value: string | undefined, fieldName: string): Address {
  if (!value || !isAddress(value)) {
    throw new Error(`Invalid or missing ${fieldName}`);
  }
  return value;
}

function parseRequiredInteger(value: string | undefined, fieldName: string, fallback?: number): number {
  const raw = value ?? (typeof fallback === 'number' ? String(fallback) : undefined);
  const parsed = raw ? Number(raw) : Number.NaN;
  if (!Number.isInteger(parsed) || parsed <= 0) {
    throw new Error(`Invalid ${fieldName}: expected a positive integer`);
  }
  return parsed;
}

function parseOptionalInteger(value: string | undefined, fieldName: string, fallback: number): number {
  if (!value) {
    return fallback;
  }
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed <= 0) {
    throw new Error(`Invalid ${fieldName}: expected a positive integer`);
  }
  return parsed;
}

export function readConfigFromEnv(): RuntimeConfig {
  const oracleMaxAgeSecondsRaw = process.env.ORACLE_MAX_AGE_SECONDS;
  const heartbeatIntervalSecondsRaw = process.env.HEARTBEAT_INTERVAL_SECONDS;
  return {
    safeAddress: assertAddress(process.env.SAFE_ADDRESS, 'SAFE_ADDRESS'),
    chainId: parseRequiredInteger(process.env.CHAIN_ID, 'CHAIN_ID', 8453),
    rpcUrl: process.env.RPC_URL ?? 'https://mainnet.base.org',
    executorModuleAddress: assertAddress(process.env.EXECUTOR_MODULE_ADDRESS, 'EXECUTOR_MODULE_ADDRESS'),
    oracleMaxAgeSeconds: parseOptionalInteger(oracleMaxAgeSecondsRaw, 'ORACLE_MAX_AGE_SECONDS', 3600),
    heartbeatIntervalSeconds: parseOptionalInteger(heartbeatIntervalSecondsRaw, 'HEARTBEAT_INTERVAL_SECONDS', 6 * 60 * 60),
    totApiKey: process.env.TOT_API_KEY,
    executorWalletPrivateKey: process.env.EXECUTOR_WALLET_PRIVATE_KEY as `0x${string}` | undefined
  };
}

export function createViemClients(config: RuntimeConfig): { publicClient: PublicClient; walletClient?: WalletClient } {
  const chain = { id: config.chainId } as Chain;

  const publicClient = createPublicClient({
    chain,
    transport: http(config.rpcUrl)
  });

  if (!config.executorWalletPrivateKey) {
    return { publicClient };
  }

  const account = privateKeyToAccount(config.executorWalletPrivateKey);
  const walletClient = createWalletClient({
    account,
    chain,
    transport: http(config.rpcUrl)
  });

  return { publicClient, walletClient };
}

export async function check_drift(params: {
  config: RuntimeConfig;
  publicClient?: PublicClient;
  policies?: PolicySnapshot;
}): Promise<DriftToolResult> {
  const publicClient = params.publicClient ?? createViemClients(params.config).publicClient;
  const policies = params.policies ?? await readPolicySnapshot(publicClient, params.config.executorModuleAddress);
  const tokenFeedRegistry = policies.tokenFeedRegistry ?? HARDCODED_TOKEN_FEED_REGISTRY_ADDRESS;

  const drift = await checkDrift({
    publicClient,
    safeAddress: params.config.safeAddress,
    tokenFeedRegistry,
    policies,
    oracleMaxAgeSeconds: params.config.oracleMaxAgeSeconds
  });

  const why = drift.exceedsThreshold
    ? `${drift.explanation} Rebalancing is recommended because drift exceeds the ${drift.thresholdBps} bps threshold.`
    : `${drift.explanation} Drift is below the ${drift.thresholdBps} bps threshold.`;

  return {
    shouldRebalance: drift.exceedsThreshold,
    thresholdBps: drift.thresholdBps,
    maxDriftBps: drift.maxDriftBps,
    explanation: drift.explanation,
    why,
    tokens: drift.tokens.map((token) => ({
      token: token.token,
      symbol: token.symbol,
      currentWeightPct: (token.currentWeightBps / 100).toFixed(2),
      targetWeightPct: (token.targetWeightBps / 100).toFixed(2),
      driftBps: token.driftBps
    }))
  };
}

export async function validate_trade(params: {
  config: RuntimeConfig;
  trade: TradeCandidate;
  publicClient?: PublicClient;
  policies?: PolicySnapshot;
}): Promise<ValidationToolResult> {
  const publicClient = params.publicClient ?? createViemClients(params.config).publicClient;
  const policies = params.policies ?? await readPolicySnapshot(publicClient, params.config.executorModuleAddress);
  const tokenFeedRegistry = policies.tokenFeedRegistry ?? HARDCODED_TOKEN_FEED_REGISTRY_ADDRESS;

  const validation = await validateTrade({
    publicClient,
    tokenFeedRegistry,
    policies,
    trade: params.trade,
    oracleMaxAgeSeconds: params.config.oracleMaxAgeSeconds
  });

  return {
    valid: validation.ok,
    reason: validation.reason,
    minAllowedToReceive: validation.minAllowedToReceive ? validation.minAllowedToReceive.toString() : undefined
  };
}

export async function automation(params: {
  config: RuntimeConfig;
  state?: AutomationState;
  nowMs?: number;
  publicClient?: PublicClient;
  policies?: PolicySnapshot;
}): Promise<AutomationResult> {
  const heartbeatSeconds = params.config.heartbeatIntervalSeconds ?? 6 * 60 * 60;
  const HEARTBEAT_MS = heartbeatSeconds * 1000;
  const now = params.nowMs ?? Date.now();
  const lastHeartbeatAt = params.state?.lastHeartbeatAt ?? 0;

  const due = now - lastHeartbeatAt >= HEARTBEAT_MS;
  if (!due) {
    return {
      checked: false,
      nextHeartbeatInSeconds: Math.ceil((HEARTBEAT_MS - (now - lastHeartbeatAt)) / 1000),
      notify: false,
      message: 'Heartbeat not due yet.'
    };
  }

  const drift = await check_drift({
    config: params.config,
    publicClient: params.publicClient,
    policies: params.policies
  });

  if (drift.shouldRebalance) {
    return {
      checked: true,
      nextHeartbeatInSeconds: heartbeatSeconds,
      notify: true,
      message: `Drift alert: ${drift.why}`
    };
  }

  return {
    checked: true,
    nextHeartbeatInSeconds: heartbeatSeconds,
    notify: false,
    message: `Heartbeat complete. ${drift.why}`
  };
}

export async function execute_rebalance(params: {
  config: RuntimeConfig;
  trades?: BatchTrade[];
  approvals?: TokenApproval[];
  rebalancing?: RebalancingExecutionInput;
  batchConfig?: BatchTradeConfig;
  walletClient?: WalletClient;
  publicClient?: PublicClient;
  maxAttempts?: number;
  retryDelayMs?: number;
}): Promise<{ txHash: `0x${string}`; why: string }> {
  const { walletClient: providedWalletClient } = params;
  const { publicClient: configuredPublicClient, walletClient: configuredWalletClient } = createViemClients(params.config);
  const publicClient = params.publicClient ?? configuredPublicClient;
  const walletClient = providedWalletClient ?? configuredWalletClient;

  if (!walletClient) {
    throw new Error('EXECUTOR_WALLET_NOT_SET: set EXECUTOR_WALLET_PRIVATE_KEY or inject walletClient.');
  }

  const scheduler = (await (publicClient as any).readContract({
    address: params.config.executorModuleAddress,
    abi: [
      { type: 'function', name: 'scheduler', stateMutability: 'view', inputs: [], outputs: [{ type: 'address' }] },
      { type: 'function', name: 'registry', stateMutability: 'view', inputs: [], outputs: [{ type: 'address' }] }
    ],
    functionName: 'scheduler'
  })) as Address;
  const registry = (await (publicClient as any).readContract({
    address: params.config.executorModuleAddress,
    abi: [
      { type: 'function', name: 'scheduler', stateMutability: 'view', inputs: [], outputs: [{ type: 'address' }] },
      { type: 'function', name: 'registry', stateMutability: 'view', inputs: [], outputs: [{ type: 'address' }] }
    ],
    functionName: 'registry'
  })) as Address;
  if (scheduler.toLowerCase() !== registry.toLowerCase()) {
    throw new Error(`SCHEDULER_REGISTRY_MISMATCH: scheduler=${scheduler} registry=${registry}`);
  }
  const walletAddress = await resolveWalletAddress(walletClient);
  if (!walletAddress) {
    throw new Error('EXECUTOR_WALLET_NOT_SET: executor wallet address unavailable from wallet client.');
  }
  if (walletAddress.toLowerCase() === ZERO_ADDRESS) {
    throw new Error('EXECUTOR_WALLET_ZERO_ADDRESS: executor wallet cannot be zero address.');
  }
  if (walletAddress.toLowerCase() !== registry.toLowerCase()) {
    throw new Error(
      `EXECUTOR_WALLET_NOT_REGISTRY: wallet=${walletAddress} registry=${registry} scheduler=${scheduler}`
    );
  }

  const defaultBatchConfig: BatchTradeConfig = {
    checkFeelessWallets: true,
    revertOnError: true
  };
  const batchConfig: BatchTradeConfig = params.batchConfig ?? defaultBatchConfig;

  const executionArgs = resolveExecutionArgs({
    trades: params.trades,
    approvals: params.approvals,
    rebalancing: params.rebalancing,
    batchConfig
  });

  const policyCheck = await checkPoliciesVerbose({
    publicClient,
    executorModule: params.config.executorModuleAddress,
    trades: executionArgs.trades,
    config: executionArgs.config
  });
  if (!policyCheck.ok) {
    throw new Error(`FAILED_POLICY_CHECK: policy=${policyCheck.failedPolicy} reason=${policyCheck.reason || 'Unknown policy failure'}`);
  }

  const maxAttempts = params.maxAttempts ?? 2;
  const retryDelayMs = params.retryDelayMs ?? 2000;
  let txHash: `0x${string}` | undefined;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      await simulateExecuteTradeNow({
        publicClient,
        executorModule: params.config.executorModuleAddress,
        approvals: executionArgs.approvals,
        trades: executionArgs.trades,
        config: executionArgs.config,
        account: (walletClient as any).account ?? walletAddress
      });

      txHash = await executeTradeNow({
        walletClient,
        executorModule: params.config.executorModuleAddress,
        approvals: executionArgs.approvals,
        trades: executionArgs.trades,
        config: executionArgs.config,
        account: (walletClient as any).account ?? walletAddress
      });
      break;
    } catch (error) {
      const classified = classifyExecutionFailure(error);
      if (classified.kind === 'skip') {
        throw new Error(`SKIPPED_MIN_TRADE_VALUE: ${classified.reason}`);
      }
      if (classified.kind === 'fail') {
        throw new Error(`FAILED_TOKEN_NOT_TRADEABLE: ${classified.reason}`);
      }
      if (attempt >= maxAttempts) {
        throw new Error(`FAILED_EXECUTION_UNKNOWN: ${classified.reason}`);
      }
      if (retryDelayMs > 0) {
        await new Promise((resolve) => setTimeout(resolve, retryDelayMs));
      }
    }
  }

  if (!txHash) {
    throw new Error('FAILED_EXECUTION_UNKNOWN: execution did not produce a transaction hash');
  }

  const why = `Execution submitted via ExecutorModule ${params.config.executorModuleAddress}.`;
  return { txHash, why };
}

function resolveExecutionArgs(input: {
  trades?: BatchTrade[];
  approvals?: TokenApproval[];
  rebalancing?: RebalancingExecutionInput;
  batchConfig: BatchTradeConfig;
}): { trades: BatchTrade[]; approvals: TokenApproval[]; config: BatchTradeConfig } {
  if (input.rebalancing) {
    const decoded = decodeRebalancingTxData(input.rebalancing.txData);
    const approvals = normalizeRebalancingAllowances(input.rebalancing.requiredAllowances);
    return {
      trades: decoded.trades,
      approvals,
      config: decoded.config
    };
  }

  if (!input.trades || !input.approvals) {
    throw new Error('Provide either { rebalancing } or both { trades, approvals }.');
  }

  return {
    trades: input.trades,
    approvals: input.approvals,
    config: input.batchConfig
  };
}

async function resolveWalletAddress(walletClient: WalletClient): Promise<Address | undefined> {
  const accountAddress = (walletClient as any)?.account?.address as Address | undefined;
  if (accountAddress) {
    return accountAddress;
  }
  const getAddresses = (walletClient as any)?.getAddresses;
  if (typeof getAddresses === 'function') {
    const addresses = await getAddresses.call(walletClient);
    if (Array.isArray(addresses) && addresses[0]) {
      return addresses[0] as Address;
    }
  }
  return undefined;
}

export async function plan_rebalance(params: {
  config: RuntimeConfig;
  signerAddress: Address;
  minTradeValue?: number;
  publicClient?: PublicClient;
  policies?: PolicySnapshot;
}): Promise<PlanRebalanceResult> {
  if (!params.config.totApiKey) {
    throw new Error('Missing TOT_API_KEY for rebalancing plan.');
  }

  const publicClient = params.publicClient ?? createViemClients(params.config).publicClient;
  const policies = params.policies ?? await readPolicySnapshot(publicClient, params.config.executorModuleAddress);

  if (policies.targetAllocations.length === 0) {
    throw new Error('Cannot plan rebalance: no StaticAllocation policy / target allocations found.');
  }

  const baseEntries = policies.assetUniverseTokens.length > 0
    ? await buildBaseEntriesFromAssetUniverse({
      publicClient,
      safeAddress: params.config.safeAddress,
      assetUniverseTokens: policies.assetUniverseTokens
    })
    : [];

  const response = await planRebalancingWithSdk({
    apiKey: params.config.totApiKey,
    chainId: params.config.chainId,
    safeAddress: params.config.safeAddress,
    signerAddress: params.signerAddress,
    minTradeValue: params.minTradeValue,
    baseEntries,
    targetAllocations: policies.targetAllocations
  });

  return {
    why: 'Plan generated from deployed target allocations via 31Third SDK.',
    response
  };
}

export async function rebalance_now(params: {
  config: RuntimeConfig;
  signerAddress?: Address;
  minTradeValue?: number;
  force?: boolean;
  publicClient?: PublicClient;
  walletClient?: WalletClient;
  policies?: PolicySnapshot;
  maxAttempts?: number;
  retryDelayMs?: number;
}): Promise<RebalanceNowResult> {
  const { publicClient: configuredPublicClient, walletClient: configuredWalletClient } = createViemClients(params.config);
  const publicClient = params.publicClient ?? configuredPublicClient;
  const walletClient = params.walletClient ?? configuredWalletClient;

  if (!walletClient) {
    throw new Error('EXECUTOR_WALLET_NOT_SET: set EXECUTOR_WALLET_PRIVATE_KEY or inject walletClient.');
  }

  const policies = params.policies ?? await readPolicySnapshot(publicClient, params.config.executorModuleAddress);
  if (policies.targetAllocations.length === 0) {
    return {
      executed: false,
      skipped: true,
      reason: 'Skipped: no StaticAllocation policy / target allocations found on ExecutorModule.'
    };
  }

  if (!params.force) {
    const drift = await check_drift({
      config: params.config,
      publicClient,
      policies
    });
    if (!drift.shouldRebalance) {
      return {
        executed: false,
        skipped: true,
        reason: `Skipped: ${drift.why}`
      };
    }
  }

  const signerAddress = params.signerAddress
    ?? ((walletClient as any).account?.address as Address | undefined);
  if (!signerAddress) {
    throw new Error('Missing signer address: pass signerAddress or configure EXECUTOR_WALLET_PRIVATE_KEY.');
  }

  const plan = await plan_rebalance({
    config: params.config,
    signerAddress,
    minTradeValue: params.minTradeValue,
    publicClient,
    policies
  });

  const execution = await execute_rebalance({
    config: params.config,
    publicClient,
    walletClient,
    rebalancing: plan.response,
    maxAttempts: params.maxAttempts,
    retryDelayMs: params.retryDelayMs
  });

  return {
    executed: true,
    skipped: false,
    reason: execution.why,
    txHash: execution.txHash
  };
}

function classifyExecutionFailure(error: unknown): { kind: 'skip' | 'fail' | 'retryable'; reason: string } {
  const reason = extractErrorText(error).toLowerCase();
  if (reason.includes('mintradevalue') || reason.includes('minimum trade value')) {
    return { kind: 'skip', reason: extractErrorText(error) };
  }
  if (
    reason.includes('tokennotbuyable') ||
    reason.includes('tokennotsellable') ||
    reason.includes('not tradeable') ||
    reason.includes('not tradable')
  ) {
    return { kind: 'fail', reason: extractErrorText(error) };
  }
  return { kind: 'retryable', reason: extractErrorText(error) };
}

function extractErrorText(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  try {
    return JSON.stringify(error);
  } catch {
    return String(error);
  }
}

export function summarizeTradeReason(input: {
  symbol: string;
  currentWeightBps: number;
  targetWeightBps: number;
}): string {
  return `${input.symbol} is at ${formatUnits(BigInt(input.currentWeightBps), 2)}%, rebalancing to ${formatUnits(BigInt(input.targetWeightBps), 2)}%.`;
}

export function help(): HelpToolResult {
  return {
    summary: 'Policy-aware Safe rebalancing for 31Third ExecutorModule, with drift checks, trade validation, and execution.',
    capabilities: [
      'check_drift: read policies and compare current allocation vs target allocation',
      'validate_trade: enforce Asset Universe and Slippage policy boundaries',
      'automation: configurable heartbeat that emits alert payloads when drift exceeds threshold',
      'plan_rebalance: build a rebalance plan from Safe balances (asset-universe bounded) + deployed target allocations via 31Third SDK',
      'execute_rebalance: accepts SDK rebalancing response or explicit trades/approvals, verifies scheduler==registry, runs checkPoliciesVerbose + simulation, retries unknown failures once, then executes through ExecutorModule',
      'Execution authorization: the signing wallet must equal ExecutorModule.registry in execute-now mode, otherwise execution is rejected',
      'rebalance_now: one-step rebalance from on-chain policies (drift check -> plan -> execute) for single-wallet executor setups',
      'Execution contract: map requiredAllowances -> approvals, decode txData as batchTrade(trades,config), ABI re-encode trade tuple payload, run checkPoliciesVerbose, and only executeTradeNow if scheduler==registry',
      'smoke (CLI): read-only preflight for config, chain/policy access, drift, optional planning, and optional simulation'
    ],
    requiredEnv: [
      'SAFE_ADDRESS',
      'EXECUTOR_MODULE_ADDRESS',
      'TOT_API_KEY (required for plan_rebalance)',
      'CHAIN_ID (default 8453)',
      'RPC_URL (default https://mainnet.base.org)',
      'EXECUTOR_WALLET_PRIVATE_KEY (required for execute_rebalance)',
      'HEARTBEAT_INTERVAL_SECONDS (optional, default 21600)',
      'ORACLE_MAX_AGE_SECONDS (optional, default 3600)'
    ],
    setupSteps: [
      'Deploy policy stack with the 31Third Safe policy wizard: https://app.31third.com/safe-policy-deployer',
      'Use two wallets: (1) Safe owner wallet for ownership/governance actions, (2) executor wallet configured on ExecutorModule for trade execution.',
      'Never share the Safe owner private key. Only the executor wallet private key should be provided to this skill for execution.',
      'Attach policies to the ExecutorModule (partial policy stacks are allowed)',
      'Use the wizard final step summary: it lists the required environment variables to copy into this skill configuration.',
      'Request a TOT_API_KEY (31Third API key) via https://31third.com or dev@31third.com.',
      'Run smoke preflight before execution: npm run smoke -- --signer 0xYourSigner',
      'Set environment variables and test read-only tools first (check_drift, validate_trade, automation)',
      'For the smoothest path, run one command: npm run cli -- rebalance-now',
      'Only then enable execution with EXECUTOR_WALLET_PRIVATE_KEY and run execute_rebalance'
    ]
  };
}
