import { describe, expect, it, vi } from 'vitest';
import type { Address, PublicClient } from 'viem';

vi.mock('@31third/sdk', () => ({
  calculateRebalancing: vi.fn(async (payload) => payload)
}));

import { calculateRebalancing } from '@31third/sdk';
import { buildBaseEntriesFromAssetUniverse, planRebalancingWithSdk } from '../src/balancer.js';

const SAFE = '0x1000000000000000000000000000000000000001' as Address;
const SIGNER = '0x2000000000000000000000000000000000000002' as Address;
const TOKEN_A = '0x3000000000000000000000000000000000000003' as Address;
const TOKEN_B = '0x4000000000000000000000000000000000000004' as Address;

describe('planRebalancingWithSdk', () => {
  it('populates baseEntries from asset universe tokens', async () => {
    const calculateRebalancingMock = vi.mocked(calculateRebalancing);
    await planRebalancingWithSdk({
      apiKey: 'key',
      chainId: 8453,
      safeAddress: SAFE,
      signerAddress: SIGNER,
      baseEntries: [
        { tokenAddress: TOKEN_A, amount: '100' },
        { tokenAddress: TOKEN_B, amount: '200' }
      ],
      targetAllocations: [{ token: TOKEN_A, bps: 10_000 }]
    });

    expect(calculateRebalancingMock).toHaveBeenCalledTimes(1);
    const call = calculateRebalancingMock.mock.calls[0][0];
    expect(call.payload.baseEntries).toEqual([
      { tokenAddress: TOKEN_A, amount: '100' },
      { tokenAddress: TOKEN_B, amount: '200' }
    ]);
  });

  it('keeps baseEntries empty when no asset universe tokens are provided', async () => {
    const calculateRebalancingMock = vi.mocked(calculateRebalancing);
    await planRebalancingWithSdk({
      apiKey: 'key',
      chainId: 8453,
      safeAddress: SAFE,
      signerAddress: SIGNER,
      targetAllocations: [{ token: TOKEN_A, bps: 10_000 }]
    });

    const call = calculateRebalancingMock.mock.calls[1][0];
    expect(call.payload.baseEntries).toEqual([]);
  });

  it('builds base entries from Safe balances and filters zero balances', async () => {
    const publicClient = {
      readContract: vi.fn(async ({ address }: { address: Address }) => {
        if (address === TOKEN_A) return 1_000n;
        if (address === TOKEN_B) return 0n;
        throw new Error('Unexpected token');
      })
    } as unknown as PublicClient;

    const entries = await buildBaseEntriesFromAssetUniverse({
      publicClient,
      safeAddress: SAFE,
      assetUniverseTokens: [TOKEN_A, TOKEN_B]
    });

    expect(entries).toEqual([{ tokenAddress: TOKEN_A, amount: '1000' }]);
  });
});
