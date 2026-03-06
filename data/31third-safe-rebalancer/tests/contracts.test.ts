import { describe, expect, it } from 'vitest';
import type { Address } from 'viem';

import {
  HARDCODED_BATCH_TRADE_ADDRESS,
  HARDCODED_TOKEN_FEED_REGISTRY_ADDRESS,
  batchTradeAbi,
  createContractRefs,
  executorModuleAbi,
  tokenFeedRegistryAbi
} from '../src/contracts.js';

describe('contracts', () => {
  it('createContractRefs wires executor and hardcoded shared contracts', () => {
    const refs = createContractRefs({
      executorModule: '0x1000000000000000000000000000000000000001' as Address,
      batchTrade: '0x2000000000000000000000000000000000000002' as Address,
      tokenFeedRegistry: '0x3000000000000000000000000000000000000003' as Address
    });

    expect(refs.executorModule.address).toBe('0x1000000000000000000000000000000000000001');
    expect(refs.executorModule.abi).toBe(executorModuleAbi);
    expect(refs.batchTrade.address).toBe(HARDCODED_BATCH_TRADE_ADDRESS);
    expect(refs.batchTrade.abi).toBe(batchTradeAbi);
    expect(refs.tokenFeedRegistry.address).toBe(HARDCODED_TOKEN_FEED_REGISTRY_ADDRESS);
    expect(refs.tokenFeedRegistry.abi).toBe(tokenFeedRegistryAbi);
  });
});
