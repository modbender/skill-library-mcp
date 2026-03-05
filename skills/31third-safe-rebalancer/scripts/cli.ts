import { readConfigFromEnv, check_drift, validate_trade, automation, execute_rebalance, help, plan_rebalance, rebalance_now } from '../index.js';
import type { BatchTrade, RebalancingExecutionInput, TokenApproval } from '../src/executor.js';
import type { TradeCandidate } from '../src/balancer.js';
import { pathToFileURL } from 'node:url';

export interface CliIO {
  log: (...args: unknown[]) => void;
  error: (...args: unknown[]) => void;
}

function printUsage(io: CliIO): void {
  io.error('Usage:');
  io.error('  npm run cli -- help');
  io.error('  npm run cli -- check-drift');
  io.error('  npm run cli -- automation [--last-heartbeat-ms <number>] [--now-ms <number>]');
  io.error('  npm run cli -- plan-rebalance --signer <address> [--min-trade-value <number>] [--api-key <key>]');
  io.error('  npm run cli -- rebalance-now [--min-trade-value <number>] [--signer <address>] [--force]');
  io.error('  npm run cli -- validate-trade --trade \'<json>\'');
  io.error('  npm run cli -- execute-rebalance --trades \'<json>\' --approvals \'<json>\'');
  io.error('  npm run cli -- execute-rebalance --rebalancing \'<json>\'');
}

function readFlagValue(args: string[], flag: string): string | undefined {
  const index = args.indexOf(flag);
  if (index < 0 || index + 1 >= args.length) {
    return undefined;
  }
  return args[index + 1];
}

function parseJsonFlag<T>(args: string[], flag: string): T {
  const raw = readFlagValue(args, flag);
  if (!raw) {
    throw new Error(`Missing required flag ${flag}`);
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

function normalizeTradeCandidate(input: {
  from: string;
  to: string;
  fromAmount: string | number | bigint;
  minToReceiveBeforeFees: string | number | bigint;
}): TradeCandidate {
  return {
    from: input.from as `0x${string}`,
    to: input.to as `0x${string}`,
    fromAmount: toBigInt(input.fromAmount),
    minToReceiveBeforeFees: toBigInt(input.minToReceiveBeforeFees)
  };
}

function normalizeBatchTrades(input: Array<{
  exchangeName: string;
  from: string;
  fromAmount: string | number | bigint;
  to: string;
  minToReceiveBeforeFees: string | number | bigint;
  data: `0x${string}`;
  signature: `0x${string}`;
}>): BatchTrade[] {
  return input.map((trade) => ({
    exchangeName: trade.exchangeName,
    from: trade.from as `0x${string}`,
    fromAmount: toBigInt(trade.fromAmount),
    to: trade.to as `0x${string}`,
    minToReceiveBeforeFees: toBigInt(trade.minToReceiveBeforeFees),
    data: trade.data,
    signature: trade.signature
  }));
}

function normalizeApprovals(input: Array<{ token: string; amount: string | number | bigint }>): TokenApproval[] {
  return input.map((approval) => ({
    token: approval.token as `0x${string}`,
    amount: toBigInt(approval.amount)
  }));
}

export async function runCli(args: string[], io: CliIO = console): Promise<number> {
  try {
    const command = args[0];

    if (!command) {
      printUsage(io);
      return 1;
    }

    if (command === 'help') {
      io.log(JSON.stringify(help(), null, 2));
      return 0;
    }

    const config = readConfigFromEnv();

    if (command === 'check-drift') {
      const result = await check_drift({ config });
      io.log(JSON.stringify(result, null, 2));
      return 0;
    }

    if (command === 'automation') {
      const lastHeartbeatMsRaw = readFlagValue(args, '--last-heartbeat-ms');
      const nowMsRaw = readFlagValue(args, '--now-ms');
      const result = await automation({
        config,
        state: lastHeartbeatMsRaw ? { lastHeartbeatAt: Number(lastHeartbeatMsRaw) } : undefined,
        nowMs: nowMsRaw ? Number(nowMsRaw) : undefined
      });
      io.log(JSON.stringify(result, null, 2));
      return 0;
    }

    if (command === 'validate-trade') {
      const tradeRaw = parseJsonFlag<{
        from: string;
        to: string;
        fromAmount: string | number | bigint;
        minToReceiveBeforeFees: string | number | bigint;
      }>(args, '--trade');
      const trade = normalizeTradeCandidate(tradeRaw);
      const result = await validate_trade({ config, trade });
      io.log(JSON.stringify(result, null, 2));
      return 0;
    }

    if (command === 'plan-rebalance') {
      const signerRaw = readFlagValue(args, '--signer');
      if (!signerRaw) {
        throw new Error('Missing required flag --signer');
      }
      const minTradeValueRaw = readFlagValue(args, '--min-trade-value');
      const apiKeyOverride = readFlagValue(args, '--api-key');
      const configWithApiKey = apiKeyOverride ? { ...config, totApiKey: apiKeyOverride } : config;

      const result = await plan_rebalance({
        config: configWithApiKey,
        signerAddress: signerRaw as `0x${string}`,
        minTradeValue: minTradeValueRaw ? Number(minTradeValueRaw) : undefined
      });
      io.log(JSON.stringify(result, null, 2));
      return 0;
    }

    if (command === 'rebalance-now') {
      const signerRaw = readFlagValue(args, '--signer');
      const minTradeValueRaw = readFlagValue(args, '--min-trade-value');
      const force = args.includes('--force');
      const result = await rebalance_now({
        config,
        signerAddress: signerRaw as `0x${string}` | undefined,
        minTradeValue: minTradeValueRaw ? Number(minTradeValueRaw) : undefined,
        force
      });
      io.log(JSON.stringify(result, null, 2));
      return 0;
    }

    if (command === 'execute-rebalance') {
      const rebalancingJson = readFlagValue(args, '--rebalancing');
      if (rebalancingJson) {
        const rebalancingRaw = JSON.parse(rebalancingJson) as RebalancingExecutionInput;
        const result = await execute_rebalance({ config, rebalancing: rebalancingRaw });
        io.log(JSON.stringify(result, null, 2));
        return 0;
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
      const trades = normalizeBatchTrades(tradesRaw);
      const approvals = normalizeApprovals(approvalsRaw);
      const result = await execute_rebalance({ config, trades, approvals });
      io.log(JSON.stringify(result, null, 2));
      return 0;
    }

    throw new Error(`Unknown command "${command}"`);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    io.error(message);
    return 1;
  }
}

async function main(): Promise<void> {
  process.exitCode = await runCli(process.argv.slice(2));
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  void main();
}
