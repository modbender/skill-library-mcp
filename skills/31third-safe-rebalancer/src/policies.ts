import type { Address, PublicClient } from 'viem';

import { HARDCODED_TOKEN_FEED_REGISTRY_ADDRESS } from './contracts.js';
import {
  assetUniversePolicyAbi,
  executorModuleAbi,
  slippagePolicyAbi,
  staticAllocationPolicyAbi
} from './contracts.js';

export interface TargetAllocation {
  token: Address;
  bps: number;
}

export interface PolicySnapshot {
  assetUniverseTokens: Address[];
  targetAllocations: TargetAllocation[];
  tokenFeedRegistry?: Address;
  driftThresholdBps?: number;
  toleranceThresholdBps?: number;
  maxSlippageBps?: number;
}

interface PolicyState {
  policy: Address;
  policyType: string;
}

export async function getExecutorPolicies(
  publicClient: PublicClient,
  executorModule: Address
): Promise<PolicyState[]> {
  const withTypes = (await publicClient.readContract({
    address: executorModule,
    abi: executorModuleAbi,
    functionName: 'getPoliciesWithTypes'
  })) as Array<{ policy: Address; policyType: string }>;

  if (withTypes.length > 0) {
    return withTypes;
  }

  const policies = (await publicClient.readContract({
    address: executorModule,
    abi: executorModuleAbi,
    functionName: 'getPolicies'
  })) as Address[];

  const resolved = await Promise.all(
    policies.map(async (policy): Promise<PolicyState> => {
      const policyType = (await publicClient.readContract({
        address: policy,
        abi: assetUniversePolicyAbi,
        functionName: 'policyType'
      })) as string;
      return { policy, policyType };
    })
  );

  return resolved;
}

export async function readPolicySnapshot(
  publicClient: PublicClient,
  executorModule: Address
): Promise<PolicySnapshot> {
  const policyStates = await getExecutorPolicies(publicClient, executorModule);

  const snapshot: PolicySnapshot = {
    assetUniverseTokens: [],
    targetAllocations: []
  };

  for (const policyState of policyStates) {
    const kind = policyState.policyType.toLowerCase();

    if (kind === 'assetuniverse') {
      snapshot.assetUniverseTokens = (await publicClient.readContract({
        address: policyState.policy,
        abi: assetUniversePolicyAbi,
        functionName: 'getTokens'
      })) as Address[];
      continue;
    }

    if (kind === 'staticallocation') {
      const feedRegistry = (await publicClient.readContract({
        address: policyState.policy,
        abi: staticAllocationPolicyAbi,
        functionName: 'feedRegistry'
      })) as Address;

      const driftThresholdBps = (await publicClient.readContract({
        address: policyState.policy,
        abi: staticAllocationPolicyAbi,
        functionName: 'driftThresholdBps'
      })) as bigint;

      const toleranceThresholdBps = (await publicClient.readContract({
        address: policyState.policy,
        abi: staticAllocationPolicyAbi,
        functionName: 'toleranceThresholdBps'
      })) as bigint;

      const targets = (await publicClient.readContract({
        address: policyState.policy,
        abi: staticAllocationPolicyAbi,
        functionName: 'getAllTargets'
      })) as Array<{ token: Address; bps: number }>;

      snapshot.driftThresholdBps = Number(driftThresholdBps);
      snapshot.toleranceThresholdBps = Number(toleranceThresholdBps);
      snapshot.tokenFeedRegistry = feedRegistry;
      snapshot.targetAllocations = targets.map((item) => ({
        token: item.token,
        bps: Number(item.bps)
      }));
      continue;
    }

    if (kind === 'slippage') {
      const feedRegistry = (await publicClient.readContract({
        address: policyState.policy,
        abi: slippagePolicyAbi,
        functionName: 'feedRegistry'
      })) as Address;

      const maxSlippageBps = (await publicClient.readContract({
        address: policyState.policy,
        abi: slippagePolicyAbi,
        functionName: 'maxSlippageBps'
      })) as bigint;

      snapshot.tokenFeedRegistry = snapshot.tokenFeedRegistry ?? feedRegistry;
      snapshot.maxSlippageBps = Number(maxSlippageBps);
    }
  }

  snapshot.tokenFeedRegistry = snapshot.tokenFeedRegistry ?? HARDCODED_TOKEN_FEED_REGISTRY_ADDRESS;
  return snapshot;
}
