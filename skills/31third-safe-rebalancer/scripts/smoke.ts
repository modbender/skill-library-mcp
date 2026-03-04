import { pathToFileURL } from 'node:url';

import {
  check_drift,
  createViemClients,
  plan_rebalance,
  readConfigFromEnv,
  type RuntimeConfig
} from '../index.js';
import { readPolicySnapshot, type PolicySnapshot } from '../src/policies.js';
import { simulateExecuteTradeNow, type BatchTrade, type BatchTradeConfig, type TokenApproval } from '../src/executor.js';

export interface SmokeIO {
  log: (...args: unknown[]) => void;
  error: (...args: unknown[]) => void;
}

type CheckStatus = 'pass' | 'fail' | 'warn';

interface SmokeCheck {
  name: string;
  status: CheckStatus;
  details: string;
}

interface SmokeReport {
  ok: boolean;
  checks: SmokeCheck[];
}

interface SmokeDeps {
  readConfigFromEnv: () => RuntimeConfig;
  createViemClients: typeof createViemClients;
  readPolicySnapshot: typeof readPolicySnapshot;
  check_drift: typeof check_drift;
  plan_rebalance: typeof plan_rebalance;
  simulateExecuteTradeNow: typeof simulateExecuteTradeNow;
}

const defaultDeps: SmokeDeps = {
  readConfigFromEnv,
  createViemClients,
  readPolicySnapshot,
  check_drift,
  plan_rebalance,
  simulateExecuteTradeNow
};

function readFlagValue(args: string[], flag: string): string | undefined {
  const index = args.indexOf(flag);
  if (index < 0 || index + 1 >= args.length) {
    return undefined;
  }
  return args[index + 1];
}

function parseJsonFlag<T>(args: string[], flag: string): T | undefined {
  const raw = readFlagValue(args, flag);
  if (!raw) {
    return undefined;
  }
  return JSON.parse(raw) as T;
}

function toBigInt(value: string | number | bigint): bigint {
  if (typeof value === 'bigint') {
    return value;
  }
  if (typeof value === 'number') {
    return BigInt(value);
  }
  return BigInt(value);
}

function normalizeTrades(raw: Array<{
  exchangeName: string;
  from: string;
  fromAmount: string | number | bigint;
  to: string;
  minToReceiveBeforeFees: string | number | bigint;
  data: `0x${string}`;
  signature: `0x${string}`;
}>): BatchTrade[] {
  return raw.map((trade) => ({
    exchangeName: trade.exchangeName,
    from: trade.from as `0x${string}`,
    fromAmount: toBigInt(trade.fromAmount),
    to: trade.to as `0x${string}`,
    minToReceiveBeforeFees: toBigInt(trade.minToReceiveBeforeFees),
    data: trade.data,
    signature: trade.signature
  }));
}

function normalizeApprovals(raw: Array<{ token: string; amount: string | number | bigint }>): TokenApproval[] {
  return raw.map((approval) => ({
    token: approval.token as `0x${string}`,
    amount: toBigInt(approval.amount)
  }));
}

function printUsage(io: SmokeIO): void {
  io.error('Usage:');
  io.error('  npm run smoke -- [--json] [--signer 0x...] [--min-trade-value 100]');
  io.error('  npm run smoke -- [--trades \'<json>\' --approvals \'<json>\']');
}

export async function runSmoke(args: string[], io: SmokeIO = console, deps: SmokeDeps = defaultDeps): Promise<number> {
  if (args.includes('--help')) {
    printUsage(io);
    return 0;
  }

  const checks: SmokeCheck[] = [];
  let config: RuntimeConfig;
  let policies: PolicySnapshot | undefined;

  try {
    config = deps.readConfigFromEnv();
    checks.push({ name: 'config', status: 'pass', details: `Loaded config for chain ${config.chainId}.` });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    checks.push({ name: 'config', status: 'fail', details: message });
    const report: SmokeReport = { ok: false, checks };
    io.log(JSON.stringify(report, null, 2));
    return 1;
  }

  const { publicClient } = deps.createViemClients(config);

  try {
    const actualChainId = await publicClient.getChainId();
    if (actualChainId !== config.chainId) {
      checks.push({
        name: 'rpc_chain',
        status: 'fail',
        details: `RPC chainId mismatch: configured ${config.chainId}, node ${actualChainId}.`
      });
    } else {
      checks.push({ name: 'rpc_chain', status: 'pass', details: `RPC chainId is ${actualChainId}.` });
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    checks.push({ name: 'rpc_chain', status: 'fail', details: `RPC/chain check failed: ${message}` });
  }

  try {
    policies = await deps.readPolicySnapshot(publicClient, config.executorModuleAddress);
    checks.push({
      name: 'policy_snapshot',
      status: 'pass',
      details: `Policies read. assetUniverse=${policies.assetUniverseTokens.length}, targets=${policies.targetAllocations.length}, slippage=${typeof policies.maxSlippageBps === 'number'}`
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    checks.push({ name: 'policy_snapshot', status: 'fail', details: `Failed reading policies: ${message}` });
  }

  if (policies) {
    try {
      const drift = await deps.check_drift({ config, publicClient, policies });
      checks.push({
        name: 'drift_read',
        status: 'pass',
        details: `Drift computed. shouldRebalance=${drift.shouldRebalance}, maxDriftBps=${drift.maxDriftBps}.`
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      checks.push({ name: 'drift_read', status: 'fail', details: `Drift check failed: ${message}` });
    }
  }

  const signer = readFlagValue(args, '--signer');
  const minTradeValue = readFlagValue(args, '--min-trade-value');
  if (config.totApiKey && signer) {
    try {
      await deps.plan_rebalance({
        config,
        publicClient,
        policies,
        signerAddress: signer as `0x${string}`,
        minTradeValue: minTradeValue ? Number(minTradeValue) : undefined
      });
      checks.push({ name: 'plan_rebalance', status: 'pass', details: 'Planner preflight succeeded.' });
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      checks.push({ name: 'plan_rebalance', status: 'fail', details: `Planner preflight failed: ${message}` });
    }
  } else {
    checks.push({
      name: 'plan_rebalance',
      status: 'warn',
      details: 'Skipped (provide TOT_API_KEY and --signer to enable planner preflight).'
    });
  }

  const tradesRaw = parseJsonFlag<Array<{
    exchangeName: string;
    from: string;
    fromAmount: string | number | bigint;
    to: string;
    minToReceiveBeforeFees: string | number | bigint;
    data: `0x${string}`;
    signature: `0x${string}`;
  }>>(args, '--trades');
  const approvalsRaw = parseJsonFlag<Array<{ token: string; amount: string | number | bigint }>>(args, '--approvals');

  if (tradesRaw && approvalsRaw) {
    const batchConfig: BatchTradeConfig = { checkFeelessWallets: true, revertOnError: true };
    try {
      await deps.simulateExecuteTradeNow({
        publicClient,
        executorModule: config.executorModuleAddress,
        approvals: normalizeApprovals(approvalsRaw),
        trades: normalizeTrades(tradesRaw),
        config: batchConfig
      });
      checks.push({ name: 'simulate_execute', status: 'pass', details: 'Simulation preflight succeeded.' });
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      checks.push({ name: 'simulate_execute', status: 'fail', details: `Simulation preflight failed: ${message}` });
    }
  } else if (tradesRaw || approvalsRaw) {
    checks.push({
      name: 'simulate_execute',
      status: 'fail',
      details: 'Provide both --trades and --approvals for simulation preflight.'
    });
  } else {
    checks.push({
      name: 'simulate_execute',
      status: 'warn',
      details: 'Skipped (provide --trades and --approvals to enable simulation preflight).'
    });
  }

  const ok = checks.every((check) => check.status !== 'fail');
  const report: SmokeReport = { ok, checks };
  io.log(JSON.stringify(report, null, 2));
  return ok ? 0 : 1;
}

async function main(): Promise<void> {
  process.exitCode = await runSmoke(process.argv.slice(2));
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  void main();
}
