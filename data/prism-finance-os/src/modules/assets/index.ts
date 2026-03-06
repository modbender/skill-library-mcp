/**
 * PRISM OS — Module 1: Asset Intelligence
 * Know what an asset is before you do anything with it.
 */

import { PrismHttpClient } from '../../core/client';
import { CanonicalResolver } from '../../core/canonical';
import { CanonicalAsset, AssetCategory, ChainId } from '../../types/canonical';

export class AssetsModule {
  constructor(
    private client: PrismHttpClient,
    private resolver: CanonicalResolver
  ) {}

  /**
   * Resolve any identifier to a canonical PRISM-ID
   * Input: "ETH", "0xA0b...", "ethereum", "bitcoin", etc.
   */
  async resolve(query: string, hint?: { chain?: ChainId }): Promise<string> {
    return this.resolver.resolve(query, hint);
  }

  /**
   * Fuzzy search — returns ranked canonical assets
   */
  async search(query: string, limit = 10): Promise<CanonicalAsset[]> {
    return this.resolver.search(query, limit);
  }

  /**
   * Full canonical asset metadata
   */
  async getMetadata(prismId: string): Promise<CanonicalAsset> {
    const id = await this.resolver.resolve(prismId);
    return this.resolver.getAsset(id);
  }

  /**
   * All verified contract addresses for an asset across chains
   */
  async getContractAddresses(
    prismId: string
  ): Promise<Record<ChainId, { address: string; decimals: number; verified: boolean }>> {
    const asset = await this.resolver.getAsset(prismId);
    return asset.contracts;
  }

  /**
   * Dedup check — critical before executing trades
   * e.g. isSameAsset("WETH", "ETH") → true (same underlying)
   */
  async isSameAsset(query1: string, query2: string): Promise<boolean> {
    return this.resolver.isSameAsset(query1, query2);
  }

  /**
   * Get all related assets (wrapped, synthetic, bridged)
   */
  async getRelated(prismId: string): Promise<{
    wrapped: string[];
    synthetic: string[];
    bridged: string[];
    correlated: string[];
  }> {
    const asset = await this.resolver.getAsset(prismId);
    return {
      wrapped: asset.wrappedVersions,
      synthetic: asset.syntheticVersions,
      bridged: asset.bridgedVersions,
      correlated: asset.relatedAssets,
    };
  }

  /**
   * Get asset category (L1, DeFi, Meme, RWA, etc.)
   */
  async getCategory(prismId: string): Promise<AssetCategory> {
    const asset = await this.resolver.getAsset(prismId);
    return asset.category;
  }

  /**
   * Get ecosystem tags
   */
  async getTags(prismId: string): Promise<string[]> {
    const asset = await this.resolver.getAsset(prismId);
    return asset.tags;
  }

  /**
   * Which chains is this asset available on?
   */
  async getChainAvailability(prismId: string): Promise<ChainId[]> {
    const asset = await this.resolver.getAsset(prismId);
    return asset.chains;
  }

  /**
   * Batch resolve — for portfolio-level operations
   */
  async batchResolve(
    queries: string[],
    hint?: { chain?: ChainId }
  ): Promise<Array<{ query: string; prismId: string | null; error?: string }>> {
    return this.resolver.batchResolve(queries, hint);
  }

  /**
   * [Expansion] Token unlock schedule — for AntiHunter audits / timing trades
   */
  async getUnlockSchedule(prismId: string): Promise<Array<{
    date: string;
    amount: string;
    amountUsd: number;
    recipient: string;
    type: 'team' | 'investor' | 'ecosystem' | 'public';
  }>> {
    const id = await this.resolver.resolve(prismId);
    return this.client.get(`/assets/${id}/unlocks`, { cacheTtl: 3600 });
  }

  /**
   * [Expansion] All yield opportunities for this asset — for YieldClaw
   */
  async getRelatedYields(prismId: string): Promise<Array<{
    protocol: string;
    chain: ChainId;
    apy: number;
    tvl: number;
    risk: 'low' | 'medium' | 'high';
    type: 'lending' | 'lp' | 'staking' | 'restaking';
  }>> {
    const id = await this.resolver.resolve(prismId);
    return this.client.get(`/assets/${id}/yields`, { cacheTtl: 300 });
  }
}
