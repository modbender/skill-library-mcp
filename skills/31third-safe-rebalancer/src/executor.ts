import type { AbiParameter, Account, Address, PublicClient, WalletClient } from 'viem';
import { decodeFunctionData, encodeAbiParameters, encodeFunctionData } from 'viem';

import { batchTradeAbi, executorModuleAbi } from './contracts.js';

export interface BatchTrade {
  exchangeName: string;
  from: Address;
  fromAmount: bigint;
  to: Address;
  minToReceiveBeforeFees: bigint;
  data: `0x${string}`;
  signature: `0x${string}`;
}

export interface BatchTradeConfig {
  checkFeelessWallets: boolean;
  revertOnError: boolean;
}

export interface TokenApproval {
  token: Address;
  amount: bigint;
}

export interface RebalancingAllowanceInput {
  token: string | { address?: string };
  neededAllowance: string | number | bigint;
}

export interface RebalancingExecutionInput {
  txData: string;
  requiredAllowances?: RebalancingAllowanceInput[];
}

export interface PolicyCheckResult {
  ok: boolean;
  failedPolicy: Address;
  reason: string;
}

const tradeArrayParam: AbiParameter = {
  type: 'tuple[]',
  components: [
    { name: 'exchangeName', type: 'string' },
    { name: 'from', type: 'address' },
    { name: 'fromAmount', type: 'uint256' },
    { name: 'to', type: 'address' },
    { name: 'minToReceiveBeforeFees', type: 'uint256' },
    { name: 'data', type: 'bytes' },
    { name: 'signature', type: 'bytes' }
  ]
};

const configParam: AbiParameter = {
  type: 'tuple',
  components: [
    { name: 'checkFeelessWallets', type: 'bool' },
    { name: 'revertOnError', type: 'bool' }
  ]
};

export function encodeTradeData(trades: BatchTrade[], config: BatchTradeConfig): `0x${string}` {
  return encodeAbiParameters([tradeArrayParam, configParam], [trades, config]);
}

export function encodeScheduleTradeCall(args: {
  approvals: TokenApproval[];
  trades: BatchTrade[];
  config: BatchTradeConfig;
  validForSeconds: number;
}): `0x${string}` {
  const tradeData = encodeTradeData(args.trades, args.config);

  return encodeFunctionData({
    abi: executorModuleAbi,
    functionName: 'scheduleTrade',
    args: [args.approvals, tradeData, BigInt(args.validForSeconds)]
  });
}

export function encodeExecuteTradeNowCall(args: {
  approvals: TokenApproval[];
  trades: BatchTrade[];
  config: BatchTradeConfig;
}): `0x${string}` {
  const tradeData = encodeTradeData(args.trades, args.config);

  return encodeFunctionData({
    abi: executorModuleAbi,
    functionName: 'executeTradeNow',
    args: [args.approvals, tradeData]
  });
}

export async function simulateExecuteTradeNow(params: {
  publicClient: PublicClient;
  executorModule: Address;
  approvals: TokenApproval[];
  trades: BatchTrade[];
  config: BatchTradeConfig;
  account?: Account | Address;
}): Promise<void> {
  const data = encodeTradeData(params.trades, params.config);

  const request: Record<string, unknown> = {
    address: params.executorModule,
    abi: executorModuleAbi,
    functionName: 'executeTradeNow',
    args: [params.approvals, data]
  };
  if (params.account) {
    request.account = params.account;
  }

  await (params.publicClient as any).simulateContract(request);
}

export async function checkPoliciesVerbose(params: {
  publicClient: PublicClient;
  executorModule: Address;
  trades: BatchTrade[];
  config: BatchTradeConfig;
}): Promise<PolicyCheckResult> {
  const result = (await (params.publicClient as any).readContract({
    address: params.executorModule,
    abi: executorModuleAbi,
    functionName: 'checkPoliciesVerbose',
    args: [params.trades, params.config]
  })) as [boolean, Address, string];

  return {
    ok: Boolean(result[0]),
    failedPolicy: result[1],
    reason: result[2]
  };
}

export async function executeTradeNow(params: {
  walletClient: WalletClient;
  executorModule: Address;
  approvals: TokenApproval[];
  trades: BatchTrade[];
  config: BatchTradeConfig;
  account?: Account | Address;
}): Promise<`0x${string}`> {
  const data = encodeTradeData(params.trades, params.config);

  const request: Record<string, unknown> = {
    address: params.executorModule,
    abi: executorModuleAbi,
    functionName: 'executeTradeNow',
    args: [params.approvals, data]
  };
  if (params.account) {
    request.account = params.account;
  }

  return (params.walletClient as any).writeContract(request);
}

export function decodeRebalancingTxData(txData: string): { trades: BatchTrade[]; config: BatchTradeConfig } {
  if (!txData || !txData.startsWith('0x')) {
    throw new Error('Invalid rebalancing txData: expected 0x-prefixed calldata');
  }
  const decoded = decodeFunctionData({
    abi: batchTradeAbi,
    data: txData as `0x${string}`
  });
  if (decoded.functionName !== 'batchTrade') {
    throw new Error(`Unsupported txData selector: expected batchTrade, received ${decoded.functionName}`);
  }
  const args = decoded.args as [BatchTrade[], BatchTradeConfig] | undefined;
  if (!args || args.length < 2) {
    throw new Error('Invalid rebalancing txData: missing trade arguments');
  }
  return { trades: args[0], config: args[1] };
}

export function normalizeRebalancingAllowances(
  allowances: RebalancingAllowanceInput[] | undefined
): TokenApproval[] {
  if (!allowances?.length) {
    return [];
  }

  return allowances.map((allowance) => {
    const tokenAddress = typeof allowance.token === 'string' ? allowance.token : allowance.token?.address;
    if (!tokenAddress || !tokenAddress.startsWith('0x')) {
      throw new Error('Invalid requiredAllowances entry: missing token address');
    }
    return {
      token: tokenAddress as Address,
      amount: BigInt(allowance.neededAllowance)
    };
  });
}
