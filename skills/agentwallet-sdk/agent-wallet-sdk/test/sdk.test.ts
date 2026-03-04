import { describe, it, expect, vi, beforeEach } from 'vitest';
import { zeroAddress, type Address } from 'viem';

// ─── Mock state ───
const mockReadFns: Record<string, any> = {};
const mockWriteFns: Record<string, any> = {};
const mockWaitForReceipt = vi.fn().mockResolvedValue({ logs: [] });
const mockWatchEvent = vi.fn().mockReturnValue(() => {});
const mockGetContractEvents = vi.fn().mockResolvedValue([]);

vi.mock('viem', async () => {
  const actual = await vi.importActual('viem');
  return {
    ...actual,
    createPublicClient: () => ({
      waitForTransactionReceipt: (...args: any[]) => mockWaitForReceipt(...args),
      watchContractEvent: (...args: any[]) => mockWatchEvent(...args),
      getContractEvents: (...args: any[]) => mockGetContractEvents(...args),
    }),
    createWalletClient: () => ({}),
    getContract: () => ({
      read: new Proxy({}, { get: (_, p: string) => (...a: any[]) => mockReadFns[p]?.(...a) }),
      write: new Proxy({}, { get: (_, p: string) => (...a: any[]) => mockWriteFns[p]?.(...a) }),
    }),
  };
});

// ─── Imports (after mock) ───
const {
  createWallet,
  setSpendPolicy,
  agentExecute,
  checkBudget,
  getPendingApprovals,
  approveTransaction,
  cancelTransaction,
  setOperator,
  agentTransferToken,
  deployWallet,
  getWalletAddress,
  getBudgetForecast,
  getWalletHealth,
  batchAgentTransfer,
  getActivityHistory,
  NATIVE_TOKEN,
} = await import('../src/index.js');

// ─── Constants ───
const ACCOUNT: Address = '0x1234567890abcdef1234567890abcdef12345678';
const OPERATOR: Address = '0xBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB';
const TOKEN: Address = '0xCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC';
const FACTORY: Address = '0xDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD';
const TX_HASH = '0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' as `0x${string}`;

function makeWallet() {
  return createWallet({
    accountAddress: ACCOUNT,
    chain: 'base',
    rpcUrl: 'https://rpc.example.com',
    walletClient: {} as any,
  });
}

describe('createWallet', () => {
  it('creates a wallet with correct address', () => {
    const w = makeWallet();
    expect(w.address).toBe(ACCOUNT);
    expect(w.chain).toBeDefined();
  });

  it('throws on unsupported chain', () => {
    expect(() =>
      createWallet({ accountAddress: ACCOUNT, chain: 'solana' as any, walletClient: {} as any })
    ).toThrow('Unsupported chain');
  });

  it('supports all valid chains', () => {
    for (const chain of ['base', 'base-sepolia', 'ethereum', 'arbitrum', 'polygon'] as const) {
      expect(createWallet({ accountAddress: ACCOUNT, chain, walletClient: {} as any }).address).toBe(ACCOUNT);
    }
  });
});

describe('NATIVE_TOKEN', () => {
  it('is the zero address', () => {
    expect(NATIVE_TOKEN).toBe(zeroAddress);
  });
});

describe('setSpendPolicy', () => {
  it('calls contract with correct params', async () => {
    mockWriteFns.setSpendPolicy = vi.fn().mockResolvedValue(TX_HASH);
    const hash = await setSpendPolicy(makeWallet(), {
      token: NATIVE_TOKEN,
      perTxLimit: 100000000000000000n,
      periodLimit: 1000000000000000000n,
      periodLength: 86400,
    });
    expect(hash).toBe(TX_HASH);
    expect(mockWriteFns.setSpendPolicy).toHaveBeenCalledWith([
      NATIVE_TOKEN, 100000000000000000n, 1000000000000000000n, 86400n,
    ], expect.objectContaining({ chain: expect.objectContaining({ id: 8453 }) }));
  });

  it('defaults periodLength to 86400 when falsy', async () => {
    mockWriteFns.setSpendPolicy = vi.fn().mockResolvedValue(TX_HASH);
    await setSpendPolicy(makeWallet(), { token: NATIVE_TOKEN, perTxLimit: 0n, periodLimit: 0n, periodLength: 0 });
    expect(mockWriteFns.setSpendPolicy).toHaveBeenCalledWith([NATIVE_TOKEN, 0n, 0n, 86400n], expect.objectContaining({ chain: expect.objectContaining({ id: 8453 }) }));
  });

  it('handles zero limits (all queued)', async () => {
    mockWriteFns.setSpendPolicy = vi.fn().mockResolvedValue(TX_HASH);
    const hash = await setSpendPolicy(makeWallet(), { token: TOKEN, perTxLimit: 0n, periodLimit: 0n, periodLength: 3600 });
    expect(hash).toBe(TX_HASH);
  });

  it('handles max uint256 limits', async () => {
    mockWriteFns.setSpendPolicy = vi.fn().mockResolvedValue(TX_HASH);
    const max = 2n ** 256n - 1n;
    await setSpendPolicy(makeWallet(), { token: TOKEN, perTxLimit: max, periodLimit: max, periodLength: 86400 });
    expect(mockWriteFns.setSpendPolicy).toHaveBeenCalledWith([TOKEN, max, max, 86400n], expect.objectContaining({ chain: expect.objectContaining({ id: 8453 }) }));
  });
});

describe('setOperator', () => {
  it('adds an operator', async () => {
    mockWriteFns.setOperator = vi.fn().mockResolvedValue(TX_HASH);
    expect(await setOperator(makeWallet(), OPERATOR, true)).toBe(TX_HASH);
    expect(mockWriteFns.setOperator).toHaveBeenCalledWith([OPERATOR, true], expect.objectContaining({ chain: expect.objectContaining({ id: 8453 }) }));
  });

  it('removes an operator', async () => {
    mockWriteFns.setOperator = vi.fn().mockResolvedValue(TX_HASH);
    expect(await setOperator(makeWallet(), OPERATOR, false)).toBe(TX_HASH);
    expect(mockWriteFns.setOperator).toHaveBeenCalledWith([OPERATOR, false], expect.objectContaining({ chain: expect.objectContaining({ id: 8453 }) }));
  });
});

describe('agentExecute', () => {
  beforeEach(() => {
    mockReadFns.pendingNonce = vi.fn().mockResolvedValue(0n);
    mockWaitForReceipt.mockResolvedValue({ logs: [] });
  });

  it('executes a transaction', async () => {
    mockWriteFns.agentExecute = vi.fn().mockResolvedValue(TX_HASH);
    const result = await agentExecute(makeWallet(), { to: OPERATOR, value: 50000000000000000n });
    expect(result.txHash).toBe(TX_HASH);
    expect(result.executed).toBe(true);
  });

  it('defaults value to 0 and data to 0x', async () => {
    mockWriteFns.agentExecute = vi.fn().mockResolvedValue(TX_HASH);
    await agentExecute(makeWallet(), { to: OPERATOR });
    expect(mockWriteFns.agentExecute).toHaveBeenCalledWith([OPERATOR, 0n, '0x'], expect.objectContaining({ value: 0n, chain: expect.objectContaining({ id: 8453 }) }));
  });

  it('passes custom data', async () => {
    mockWriteFns.agentExecute = vi.fn().mockResolvedValue(TX_HASH);
    await agentExecute(makeWallet(), { to: TOKEN, value: 0n, data: '0xdeadbeef' });
    expect(mockWriteFns.agentExecute).toHaveBeenCalledWith([TOKEN, 0n, '0xdeadbeef'], expect.objectContaining({ value: 0n, chain: expect.objectContaining({ id: 8453 }) }));
  });
});

describe('checkBudget', () => {
  it('returns budget status', async () => {
    mockReadFns.remainingBudget = vi.fn().mockResolvedValue([100000000000000000n, 500000000000000000n]);
    const budget = await checkBudget(makeWallet(), NATIVE_TOKEN);
    expect(budget.token).toBe(NATIVE_TOKEN);
    expect(budget.perTxLimit).toBe(100000000000000000n);
    expect(budget.remainingInPeriod).toBe(500000000000000000n);
  });

  it('defaults to NATIVE_TOKEN', async () => {
    mockReadFns.remainingBudget = vi.fn().mockResolvedValue([0n, 0n]);
    await checkBudget(makeWallet());
    expect(mockReadFns.remainingBudget).toHaveBeenCalledWith([NATIVE_TOKEN]);
  });
});

describe('getPendingApprovals', () => {
  it('returns pending txs', async () => {
    mockReadFns.pendingNonce = vi.fn().mockResolvedValue(2n);
    mockReadFns.getPending = vi.fn()
      .mockResolvedValueOnce([OPERATOR, 1n, NATIVE_TOKEN, 1n, 100n, false, false])
      .mockResolvedValueOnce([OPERATOR, 2n, NATIVE_TOKEN, 2n, 101n, false, false]);
    const pending = await getPendingApprovals(makeWallet());
    expect(pending).toHaveLength(2);
    expect(pending[0].txId).toBe(0n);
    expect(pending[1].txId).toBe(1n);
  });

  it('filters out executed and cancelled txs', async () => {
    mockReadFns.pendingNonce = vi.fn().mockResolvedValue(3n);
    mockReadFns.getPending = vi.fn()
      .mockResolvedValueOnce([OPERATOR, 1n, NATIVE_TOKEN, 1n, 1n, true, false])
      .mockResolvedValueOnce([OPERATOR, 1n, NATIVE_TOKEN, 1n, 1n, false, true])
      .mockResolvedValueOnce([OPERATOR, 1n, NATIVE_TOKEN, 1n, 1n, false, false]);
    const pending = await getPendingApprovals(makeWallet());
    expect(pending).toHaveLength(1);
    expect(pending[0].txId).toBe(2n);
  });

  it('returns empty when no pending', async () => {
    mockReadFns.pendingNonce = vi.fn().mockResolvedValue(0n);
    expect(await getPendingApprovals(makeWallet())).toHaveLength(0);
  });
});

describe('approveTransaction', () => {
  it('approves a pending tx', async () => {
    mockWriteFns.approvePending = vi.fn().mockResolvedValue(TX_HASH);
    expect(await approveTransaction(makeWallet(), 0n)).toBe(TX_HASH);
    expect(mockWriteFns.approvePending).toHaveBeenCalledWith([0n], expect.objectContaining({ chain: expect.objectContaining({ id: 8453 }) }));
  });
});

describe('cancelTransaction', () => {
  it('cancels a pending tx', async () => {
    mockWriteFns.cancelPending = vi.fn().mockResolvedValue(TX_HASH);
    expect(await cancelTransaction(makeWallet(), 1n)).toBe(TX_HASH);
    expect(mockWriteFns.cancelPending).toHaveBeenCalledWith([1n], expect.objectContaining({ chain: expect.objectContaining({ id: 8453 }) }));
  });
});

describe('agentTransferToken', () => {
  it('transfers tokens', async () => {
    mockWriteFns.agentTransferToken = vi.fn().mockResolvedValue(TX_HASH);
    const hash = await agentTransferToken(makeWallet(), { token: TOKEN, to: OPERATOR, amount: 500n });
    expect(hash).toBe(TX_HASH);
    expect(mockWriteFns.agentTransferToken).toHaveBeenCalledWith([TOKEN, OPERATOR, 500n], expect.objectContaining({ chain: expect.objectContaining({ id: 8453 }) }));
  });
});

describe('deployWallet', () => {
  it('throws on unsupported chain', async () => {
    await expect(
      deployWallet({ factoryAddress: FACTORY, tokenContract: TOKEN, tokenId: 1n, chain: 'solana' as any, walletClient: {} as any })
    ).rejects.toThrow('Unsupported chain');
  });

  it('deploys and returns address + hash', async () => {
    // getContract is mocked globally, so read/write proxies work
    mockReadFns.getAddress = vi.fn().mockResolvedValue(ACCOUNT);
    mockWriteFns.createAccount = vi.fn().mockResolvedValue(TX_HASH);
    const result = await deployWallet({
      factoryAddress: FACTORY, tokenContract: TOKEN, tokenId: 1n,
      chain: 'base', rpcUrl: 'https://rpc.example.com', walletClient: {} as any,
    });
    expect(result.walletAddress).toBe(ACCOUNT);
    expect(result.txHash).toBe(TX_HASH);
  });
});

describe('getWalletAddress', () => {
  it('computes deterministic address', async () => {
    mockReadFns.getAddress = vi.fn().mockResolvedValue(ACCOUNT);
    const addr = await getWalletAddress({
      factoryAddress: FACTORY, tokenContract: TOKEN, tokenId: 1n, chain: 'base',
    });
    expect(addr).toBe(ACCOUNT);
  });

  it('throws on unsupported chain', async () => {
    await expect(
      getWalletAddress({ factoryAddress: FACTORY, tokenContract: TOKEN, tokenId: 1n, chain: 'invalid' })
    ).rejects.toThrow('Unsupported chain');
  });
});

// ─── [MAX-ADDED] Tests for value-add features ───

describe('getBudgetForecast', () => {
  it('returns forecast with utilization and reset time', async () => {
    mockReadFns.remainingBudget = vi.fn().mockResolvedValue([100n, 700n]);
    mockReadFns.spendPolicies = vi.fn().mockResolvedValue([100n, 1000n, 86400n, 300n, 1000n]);

    const forecast = await getBudgetForecast(makeWallet(), NATIVE_TOKEN, 50000);
    expect(forecast.token).toBe(NATIVE_TOKEN);
    expect(forecast.perTxLimit).toBe(100n);
    expect(forecast.remainingInPeriod).toBe(700n);
    expect(forecast.periodLimit).toBe(1000n);
    expect(forecast.periodSpent).toBe(300n);
    expect(forecast.utilizationPercent).toBe(30);
    expect(forecast.secondsUntilReset).toBe(87400 - 50000); // 1000 + 86400 - 50000
  });

  it('handles zero period limit (no autonomous spending)', async () => {
    mockReadFns.remainingBudget = vi.fn().mockResolvedValue([0n, 0n]);
    mockReadFns.spendPolicies = vi.fn().mockResolvedValue([0n, 0n, 86400n, 0n, 0n]);

    const forecast = await getBudgetForecast(makeWallet(), TOKEN, 100);
    expect(forecast.utilizationPercent).toBe(0);
  });

  it('clamps secondsUntilReset to zero when period expired', async () => {
    mockReadFns.remainingBudget = vi.fn().mockResolvedValue([100n, 1000n]);
    mockReadFns.spendPolicies = vi.fn().mockResolvedValue([100n, 1000n, 86400n, 0n, 1000n]);

    const forecast = await getBudgetForecast(makeWallet(), NATIVE_TOKEN, 999999);
    expect(forecast.secondsUntilReset).toBe(0);
  });
});

describe('getWalletHealth', () => {
  it('returns full diagnostic snapshot', async () => {
    mockReadFns.tokenContract = vi.fn().mockResolvedValue(TOKEN);
    mockReadFns.tokenId = vi.fn().mockResolvedValue(42n);
    mockReadFns.operatorEpoch = vi.fn().mockResolvedValue(1n);
    mockReadFns.isOperatorActive = vi.fn().mockResolvedValue(true);
    mockReadFns.pendingNonce = vi.fn().mockResolvedValue(1n);
    mockReadFns.getPending = vi.fn().mockResolvedValue([OPERATOR, 1n, NATIVE_TOKEN, 1n, 100n, false, false]);
    mockReadFns.remainingBudget = vi.fn().mockResolvedValue([100n, 500n]);
    mockReadFns.spendPolicies = vi.fn().mockResolvedValue([100n, 1000n, 86400n, 500n, 1000n]);

    const health = await getWalletHealth(makeWallet(), [OPERATOR], [NATIVE_TOKEN], 50000);
    expect(health.address).toBe(ACCOUNT);
    expect(health.tokenContract).toBe(TOKEN);
    expect(health.tokenId).toBe(42n);
    expect(health.operatorEpoch).toBe(1n);
    expect(health.activeOperators).toHaveLength(1);
    expect(health.activeOperators[0].active).toBe(true);
    expect(health.pendingQueueDepth).toBe(1);
    expect(health.budgets).toHaveLength(1);
    expect(health.budgets[0].token).toBe(NATIVE_TOKEN);
  });

  it('returns zero queue depth when no pending', async () => {
    mockReadFns.tokenContract = vi.fn().mockResolvedValue(TOKEN);
    mockReadFns.tokenId = vi.fn().mockResolvedValue(1n);
    mockReadFns.operatorEpoch = vi.fn().mockResolvedValue(0n);
    mockReadFns.pendingNonce = vi.fn().mockResolvedValue(0n);
    mockReadFns.remainingBudget = vi.fn().mockResolvedValue([0n, 0n]);
    mockReadFns.spendPolicies = vi.fn().mockResolvedValue([0n, 0n, 86400n, 0n, 0n]);

    const health = await getWalletHealth(makeWallet(), [], [NATIVE_TOKEN], 100);
    expect(health.pendingQueueDepth).toBe(0);
    expect(health.activeOperators).toHaveLength(0);
  });
});

describe('batchAgentTransfer', () => {
  it('executes multiple transfers and returns all hashes', async () => {
    const hash2 = '0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb' as `0x${string}`;
    mockWriteFns.agentTransferToken = vi.fn()
      .mockResolvedValueOnce(TX_HASH)
      .mockResolvedValueOnce(hash2);

    const hashes = await batchAgentTransfer(makeWallet(), [
      { token: TOKEN, to: OPERATOR, amount: 100n },
      { token: TOKEN, to: ACCOUNT, amount: 200n },
    ]);
    expect(hashes).toHaveLength(2);
    expect(hashes[0]).toBe(TX_HASH);
    expect(hashes[1]).toBe(hash2);
    expect(mockWriteFns.agentTransferToken).toHaveBeenCalledTimes(2);
  });

  it('returns empty array for empty batch', async () => {
    const hashes = await batchAgentTransfer(makeWallet(), []);
    expect(hashes).toHaveLength(0);
  });
});

describe('getActivityHistory', () => {
  it('returns sorted activity entries', async () => {
    mockGetContractEvents
      .mockResolvedValueOnce([{ // TransactionExecuted
        blockNumber: 200n,
        transactionHash: TX_HASH,
        args: { target: OPERATOR, value: 1n },
      }])
      .mockResolvedValueOnce([]) // TransactionQueued
      .mockResolvedValueOnce([]) // TransactionApproved
      .mockResolvedValueOnce([]) // TransactionCancelled
      .mockResolvedValueOnce([{ // SpendPolicyUpdated
        blockNumber: 100n,
        transactionHash: TX_HASH,
        args: { token: NATIVE_TOKEN, perTxLimit: 100n },
      }])
      .mockResolvedValueOnce([]); // OperatorUpdated

    const history = await getActivityHistory(makeWallet());
    expect(history).toHaveLength(2);
    // Should be sorted by block number ascending
    expect(history[0].type).toBe('policy_update');
    expect(history[0].blockNumber).toBe(100n);
    expect(history[1].type).toBe('execution');
    expect(history[1].blockNumber).toBe(200n);
  });

  it('returns empty array when no events', async () => {
    mockGetContractEvents.mockResolvedValue([]);
    const history = await getActivityHistory(makeWallet());
    expect(history).toHaveLength(0);
  });
});
