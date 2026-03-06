import ExecutorModuleArtifact from '../abi/ExecutorModule.json' with { type: 'json' };
import AssetUniversePolicyArtifact from '../abi/AssetUniversePolicy.json' with { type: 'json' };
import StaticAllocationPolicyArtifact from '../abi/StaticAllocationPolicy.json' with { type: 'json' };
import SlippagePolicyArtifact from '../abi/SlippagePolicy.json' with { type: 'json' };

export const executorModuleAbi = ExecutorModuleArtifact.abi;
export const assetUniversePolicyAbi = AssetUniversePolicyArtifact.abi;
export const staticAllocationPolicyAbi = StaticAllocationPolicyArtifact.abi;
export const slippagePolicyAbi = SlippagePolicyArtifact.abi;

export const erc20Abi = [
  {
    type: 'function',
    name: 'balanceOf',
    stateMutability: 'view',
    inputs: [{ name: 'account', type: 'address' }],
    outputs: [{ name: '', type: 'uint256' }]
  },
  {
    type: 'function',
    name: 'decimals',
    stateMutability: 'view',
    inputs: [],
    outputs: [{ name: '', type: 'uint8' }]
  }
] as const;

export const tokenFeedRegistryAbi = [
  {
    type: 'function',
    name: 'getFeed',
    stateMutability: 'view',
    inputs: [{ name: 'token', type: 'address' }],
    outputs: [{ name: '', type: 'address' }]
  }
] as const;

export const aggregatorV3Abi = [
  {
    type: 'function',
    name: 'decimals',
    stateMutability: 'view',
    inputs: [],
    outputs: [{ name: '', type: 'uint8' }]
  },
  {
    type: 'function',
    name: 'latestRoundData',
    stateMutability: 'view',
    inputs: [],
    outputs: [
      { name: 'roundId', type: 'uint80' },
      { name: 'answer', type: 'int256' },
      { name: 'startedAt', type: 'uint256' },
      { name: 'updatedAt', type: 'uint256' },
      { name: 'answeredInRound', type: 'uint80' }
    ]
  }
] as const;
