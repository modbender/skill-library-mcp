import { ethers } from 'ethers';
import { config } from '../config';

const provider = new ethers.JsonRpcProvider(config.baseRpcUrl);

// --- ERC-8004 Identity Registry on Base (ERC-721 based) ---
const ERC8004_REGISTRY = '0x8004A169FB4a3325136EB29fA0ceB6D2e539a432';
const ERC8004_ABI = [
  'function balanceOf(address owner) view returns (uint256)',
];
const registryContract = new ethers.Contract(ERC8004_REGISTRY, ERC8004_ABI, provider);

// --- Basenames (ENS on Base) reverse resolver ---
// Base uses standard ENS reverse resolution at the universal resolver
const BASE_REVERSE_REGISTRAR = '0xC6d566A56A1aFf6508b41f6c90ff131615583BCD';
const REVERSE_ABI = [
  'function node(address addr) view returns (bytes32)',
];

// Simple approach: try ENS reverse lookup on Base
async function hasBasename(address: string): Promise<boolean> {
  try {
    const name = await provider.lookupAddress(address);
    return name !== null && name.endsWith('.base.eth');
  } catch {
    // Reverse lookup not supported or failed — try direct registry check
    try {
      const reverseNode = ethers.namehash(
        address.slice(2).toLowerCase() + '.addr.reverse'
      );
      const resolver = new ethers.Contract(
        '0xC6d566A56A1aFf6508b41f6c90ff131615583BCD',
        ['function name(bytes32 node) view returns (string)'],
        provider
      );
      const name = await resolver.name(reverseNode);
      return typeof name === 'string' && name.length > 0;
    } catch {
      return false;
    }
  }
}

// --- Identity Tiers ---

export type IdentityTier = 'anonymous' | 'wallet' | 'basename' | 'erc8004';

export interface IdentityCheck {
  tier: IdentityTier;
  freeRequests: number;
  basename?: string;
  isRegisteredAgent?: boolean;
}

const TIER_FREE_REQUESTS: Record<IdentityTier, number> = {
  anonymous: 25,
  wallet: 50,
  basename: 100,
  erc8004: 100,
};

/**
 * Check onchain identity for a wallet address and determine the free request tier.
 * Checks ERC-8004 registry and Basenames in parallel.
 * Falls back gracefully if RPC calls fail.
 */
export async function checkIdentity(walletAddress?: string): Promise<IdentityCheck> {
  if (!walletAddress || !ethers.isAddress(walletAddress)) {
    return { tier: 'anonymous', freeRequests: TIER_FREE_REQUESTS.anonymous };
  }

  try {
    // Check ERC-8004 and Basename in parallel
    const [agentBalance, hasBn] = await Promise.allSettled([
      registryContract.balanceOf(walletAddress),
      hasBasename(walletAddress),
    ]);

    const agentRegistered = agentBalance.status === 'fulfilled' && BigInt(agentBalance.value) > 0n;
    const basenameFound = hasBn.status === 'fulfilled' && hasBn.value === true;

    if (agentRegistered) {
      return {
        tier: 'erc8004',
        freeRequests: TIER_FREE_REQUESTS.erc8004,
        isRegisteredAgent: true,
      };
    }

    if (basenameFound) {
      return {
        tier: 'basename',
        freeRequests: TIER_FREE_REQUESTS.basename,
      };
    }

    // Valid wallet but no onchain identity
    return { tier: 'wallet', freeRequests: TIER_FREE_REQUESTS.wallet };
  } catch (err) {
    console.error('[identity] Onchain check failed, falling back to wallet tier:', err);
    return { tier: 'wallet', freeRequests: TIER_FREE_REQUESTS.wallet };
  }
}

export { TIER_FREE_REQUESTS };
