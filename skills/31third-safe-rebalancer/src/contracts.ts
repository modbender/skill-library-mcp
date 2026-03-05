import type { Abi, Address } from 'viem';

import executorArtifact from '../abi/ExecutorModule.json' with { type: 'json' };
import assetUniverseArtifact from '../abi/AssetUniversePolicy.json' with { type: 'json' };
import staticAllocationArtifact from '../abi/StaticAllocationPolicy.json' with { type: 'json' };
import slippageArtifact from '../abi/SlippagePolicy.json' with { type: 'json' };
import tokenFeedRegistryArtifact from '../abi/TokenFeedRegistry.json' with { type: 'json' };
import batchTradeArtifact from '../abi/IBatchTrade.json' with { type: 'json' };

export const executorModuleAbi = executorArtifact.abi as Abi;
export const assetUniversePolicyAbi = assetUniverseArtifact.abi as Abi;
export const staticAllocationPolicyAbi = staticAllocationArtifact.abi as Abi;
export const slippagePolicyAbi = slippageArtifact.abi as Abi;
export const tokenFeedRegistryAbi = tokenFeedRegistryArtifact.abi as Abi;
export const batchTradeAbi = batchTradeArtifact.abi as Abi;
export const HARDCODED_BATCH_TRADE_ADDRESS = '0xD20c024560ccA40288C05BAB650ac087ae9b0f6e' as Address;
export const HARDCODED_TOKEN_FEED_REGISTRY_ADDRESS = '0x1d4999242A24C8588c4f5dB7dFF1D74Df6bC746A' as Address;

export interface ContractAddresses {
  executorModule: Address;
  batchTrade: Address;
  tokenFeedRegistry: Address;
}

export interface ContractRefs {
  executorModule: { address: Address; abi: Abi };
  batchTrade: { address: Address; abi: Abi };
  tokenFeedRegistry: { address: Address; abi: Abi };
}

export function createContractRefs(addresses: ContractAddresses): ContractRefs {
  return {
    executorModule: {
      address: addresses.executorModule,
      abi: executorModuleAbi
    },
    batchTrade: {
      address: HARDCODED_BATCH_TRADE_ADDRESS,
      abi: batchTradeAbi
    },
    tokenFeedRegistry: {
      address: HARDCODED_TOKEN_FEED_REGISTRY_ADDRESS,
      abi: tokenFeedRegistryAbi
    }
  };
}
