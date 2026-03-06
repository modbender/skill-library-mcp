/**
 * PRISM OS — Canonical Asset Resolver
 * The core of the OS. Everything starts here.
 *
 * Resolves any human input → PRISM-ID → canonical asset object
 * Sources: internal registry → CoinGecko → CMC → on-chain fallback
 */

import { CanonicalAsset, ChainId, PrismConfig } from '../types/canonical';

// ─────────────────────────────────────────────
// MOCK REGISTRY (replace with API calls in prod)
// ─────────────────────────────────────────────

const REGISTRY: Record<string, CanonicalAsset> = {
  'prism:ethereum:eth': {
    prismId: 'prism:ethereum:eth',
    name: 'Ethereum',
    symbol: 'ETH',
    category: 'L1',
    tags: ['store-of-value', 'pos', 'evm', 'gas-token'],
    primaryChain: 'ethereum',
    chains: ['ethereum', 'arbitrum', 'optimism', 'base', 'polygon'],
    contracts: {
      ethereum: { address: '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', decimals: 18, verified: true },
      arbitrum: { address: '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1', decimals: 18, verified: true },
      optimism: { address: '0x4200000000000000000000000000000000000006', decimals: 18, verified: true },
      base: { address: '0x4200000000000000000000000000000000000006', decimals: 18, verified: true },
    },
    wrappedVersions: ['prism:ethereum:weth'],
    syntheticVersions: ['prism:synthetix:seth'],
    bridgedVersions: [],
    relatedAssets: ['prism:ethereum:steth', 'prism:ethereum:reth'],
    cexListings: ['binance', 'bybit', 'okx', 'coinbase', 'kraken'],
    dexListings: [
      { venue: 'uniswap', chain: 'ethereum', pool: '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640' },
      { venue: 'aerodrome', chain: 'base', pool: '0x...' },
    ],
    coingeckoId: 'ethereum',
    coinmarketcapId: '1027',
    defilllamaSlug: 'ethereum',
    logoUrl: 'https://assets.coingecko.com/coins/images/279/large/ethereum.png',
    auditStatus: 'audited',
    rugScore: 0,
    createdAt: '2015-07-30T00:00:00Z',
    updatedAt: new Date().toISOString(),
  },
  'prism:solana:sol': {
    prismId: 'prism:solana:sol',
    name: 'Solana',
    symbol: 'SOL',
    category: 'L1',
    tags: ['high-throughput', 'pos', 'gas-token'],
    primaryChain: 'solana',
    chains: ['solana', 'ethereum'],
    contracts: {
      solana: { address: 'So11111111111111111111111111111111111111112', decimals: 9, verified: true },
      ethereum: { address: '0xD31a59c85aE9D8edefec411D448f90841571b89c', decimals: 9, verified: true },
    },
    wrappedVersions: ['prism:solana:wsol'],
    syntheticVersions: [],
    bridgedVersions: ['prism:ethereum:sol-bridged'],
    relatedAssets: ['prism:solana:jitoSOL', 'prism:solana:mSOL'],
    cexListings: ['binance', 'bybit', 'okx', 'coinbase', 'kraken'],
    dexListings: [
      { venue: 'jupiter', chain: 'solana', pool: '...' },
      { venue: 'orca', chain: 'solana', pool: '...' },
    ],
    coingeckoId: 'solana',
    coinmarketcapId: '5426',
    defilllamaSlug: 'solana',
    auditStatus: 'audited',
    rugScore: 0,
    createdAt: '2020-03-20T00:00:00Z',
    updatedAt: new Date().toISOString(),
  },
  'prism:ethereum:usdc': {
    prismId: 'prism:ethereum:usdc',
    name: 'USD Coin',
    symbol: 'USDC',
    category: 'Stablecoin',
    tags: ['stablecoin', 'regulated', 'fiat-backed', 'circle'],
    primaryChain: 'ethereum',
    chains: ['ethereum', 'solana', 'arbitrum', 'optimism', 'base', 'polygon', 'avalanche'],
    contracts: {
      ethereum: { address: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', decimals: 6, verified: true },
      solana: { address: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', decimals: 6, verified: true },
      base: { address: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913', decimals: 6, verified: true },
    },
    wrappedVersions: [],
    syntheticVersions: [],
    bridgedVersions: [],
    relatedAssets: ['prism:ethereum:usdt', 'prism:ethereum:dai'],
    cexListings: ['binance', 'bybit', 'okx', 'coinbase', 'kraken'],
    dexListings: [],
    coingeckoId: 'usd-coin',
    coinmarketcapId: '3408',
    auditStatus: 'audited',
    rugScore: 2,
    createdAt: '2018-09-26T00:00:00Z',
    updatedAt: new Date().toISOString(),
  },
};

// Alias maps — "WETH" → "prism:ethereum:weth", contract → ID, etc.
const ALIAS_MAP: Record<string, string> = {
  'eth': 'prism:ethereum:eth',
  'ethereum': 'prism:ethereum:eth',
  'sol': 'prism:solana:sol',
  'solana': 'prism:solana:sol',
  'usdc': 'prism:ethereum:usdc',
  'usd-coin': 'prism:ethereum:usdc',
  // Contract aliases
  '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48': 'prism:ethereum:usdc',
  '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 'prism:ethereum:weth',
  'So11111111111111111111111111111111111111112': 'prism:solana:sol',
};

// ─────────────────────────────────────────────
// CANONICAL RESOLVER CLASS
// ─────────────────────────────────────────────

export class CanonicalResolver {
  private config: PrismConfig;
  private cache: Map<string, { asset: CanonicalAsset; expiresAt: number }> = new Map();

  constructor(config: PrismConfig) {
    this.config = config;
  }

  /**
   * Resolve any query string to a PRISM canonical ID
   * Handles: symbol, name, contract address, CoinGecko ID, CMC ID
   */
  async resolve(query: string, hint?: { chain?: ChainId }): Promise<string> {
    const normalized = query.toLowerCase().trim();

    // 1. Already a PRISM-ID
    if (normalized.startsWith('prism:')) {
      if (REGISTRY[normalized]) return normalized;
      throw new Error(`Unknown PRISM-ID: ${normalized}`);
    }

    // 2. Alias map lookup (fast path)
    if (ALIAS_MAP[normalized]) return ALIAS_MAP[normalized];

    // 3. Contract address lookup
    if (this.isContractAddress(query)) {
      const fromContract = this.resolveFromContract(query, hint?.chain);
      if (fromContract) return fromContract;
    }

    // 4. Fuzzy match against registry
    const fuzzyMatch = this.fuzzyResolve(normalized, hint?.chain);
    if (fuzzyMatch) return fuzzyMatch;

    // 5. External API fallback (CoinGecko)
    if (this.config.environment !== 'mock') {
      const external = await this.resolveExternal(query);
      if (external) return external;
    }

    throw new Error(`Cannot resolve asset: "${query}". Try a contract address or CoinGecko ID.`);
  }

  /**
   * Get the full canonical asset object
   */
  async getAsset(prismId: string): Promise<CanonicalAsset> {
    // Check cache
    const cached = this.cache.get(prismId);
    if (cached && cached.expiresAt > Date.now()) {
      return cached.asset;
    }

    const asset = REGISTRY[prismId];
    if (!asset) {
      throw new Error(`Asset not found: ${prismId}`);
    }

    // Cache with TTL
    const ttl = this.config.cache?.ttl ?? 300;
    this.cache.set(prismId, { asset, expiresAt: Date.now() + ttl * 1000 });

    return asset;
  }

  /**
   * Check if two queries refer to the same underlying asset
   * Key for preventing wrong-asset trades (e.g. ETH vs WETH vs stETH)
   */
  async isSameAsset(query1: string, query2: string): Promise<boolean> {
    try {
      const [id1, id2] = await Promise.all([this.resolve(query1), this.resolve(query2)]);

      if (id1 === id2) return true;

      // Check wrapped/synthetic relationships
      const asset1 = await this.getAsset(id1);
      return (
        asset1.wrappedVersions.includes(id2) ||
        asset1.syntheticVersions.includes(id2) ||
        asset1.bridgedVersions.includes(id2)
      );
    } catch {
      return false;
    }
  }

  /**
   * Batch resolve — for portfolio operations, multiple assets at once
   */
  async batchResolve(
    queries: string[],
    hint?: { chain?: ChainId }
  ): Promise<Array<{ query: string; prismId: string | null; error?: string }>> {
    const results = await Promise.allSettled(
      queries.map((q) => this.resolve(q, hint))
    );

    return results.map((result, i) => ({
      query: queries[i],
      prismId: result.status === 'fulfilled' ? result.value : null,
      error: result.status === 'rejected' ? result.reason.message : undefined,
    }));
  }

  /**
   * Search assets by name/symbol/tag
   */
  async search(query: string, limit = 10): Promise<CanonicalAsset[]> {
    const normalized = query.toLowerCase();
    const results: Array<{ asset: CanonicalAsset; score: number }> = [];

    for (const asset of Object.values(REGISTRY)) {
      let score = 0;

      // Exact symbol match → highest score
      if (asset.symbol.toLowerCase() === normalized) score += 100;
      // Symbol prefix match
      else if (asset.symbol.toLowerCase().startsWith(normalized)) score += 70;
      // Name contains query
      else if (asset.name.toLowerCase().includes(normalized)) score += 50;
      // Tag match
      else if (asset.tags.some((t) => t.includes(normalized))) score += 30;

      if (score > 0) results.push({ asset, score });
    }

    return results
      .sort((a, b) => b.score - a.score)
      .slice(0, limit)
      .map((r) => r.asset);
  }

  // ─────────────────────────────────────────────
  // Private helpers
  // ─────────────────────────────────────────────

  private isContractAddress(query: string): boolean {
    // Ethereum-style
    if (/^0x[a-fA-F0-9]{40}$/.test(query)) return true;
    // Solana-style
    if (/^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(query)) return true;
    return false;
  }

  private resolveFromContract(address: string, chain?: ChainId): string | null {
    // Check alias map first
    if (ALIAS_MAP[address]) return ALIAS_MAP[address];

    // Scan registry contracts
    for (const asset of Object.values(REGISTRY)) {
      for (const [assetChain, info] of Object.entries(asset.contracts)) {
        if (
          info.address.toLowerCase() === address.toLowerCase() &&
          (!chain || assetChain === chain)
        ) {
          return asset.prismId;
        }
      }
    }
    return null;
  }

  private fuzzyResolve(query: string, chain?: ChainId): string | null {
    for (const asset of Object.values(REGISTRY)) {
      if (
        asset.symbol.toLowerCase() === query ||
        asset.coingeckoId === query ||
        asset.coinmarketcapId === query
      ) {
        // If chain hint provided, prefer matching chain
        if (chain && asset.primaryChain !== chain) {
          const chainVariant = `prism:${chain}:${asset.symbol.toLowerCase()}`;
          if (REGISTRY[chainVariant]) return chainVariant;
        }
        return asset.prismId;
      }
    }
    return null;
  }

  private async resolveExternal(query: string): Promise<string | null> {
    // In production: hit Prism API → CoinGecko → CMC
    // For now returns null to signal "not in registry"
    console.warn(`[PRISM] External resolution for "${query}" - not in local registry`);
    return null;
  }
}
