/**
 * Crypto Module
 *
 * Endpoints:
 *   GET /crypto/price/{symbol}
 *   GET /crypto/prices/batch
 *   GET /crypto/sources/status
 *   GET /crypto/trending
 *   GET /crypto/trending/pools
 *   GET /crypto/trending/evm
 *   GET /crypto/trending/solana/bonding
 *   GET /crypto/trending/solana/graduated
 *   GET /crypto/trending/all
 *   GET /crypto/global
 *   GET /batch/crypto/prices
 *   GET /batch/crypto/history
 *   GET /batch/crypto/sparklines
 *   GET /batch/crypto/sparklines/symbols
 *   POST /batch/crypto/sparklines/symbols
 *   GET /market/overview
 *   GET /market/fear-greed
 *   GET /market/crypto/gainers
 *   GET /market/crypto/losers
 *   GET /market/crypto/gainers/aggregated
 *   GET /market/crypto/losers/aggregated
 *   GET /market/correlations
 *   GET /indexes/crypto
 *   GET /indexes/defi
 *   GET /chains
 *   GET /valuation/crypto/{symbol}/nvt
 *   GET /assets/search
 *   GET /assets/all
 *   GET /assets/stats
 *   GET /assets/cache
 *   GET /assets/{identifier}
 *   GET /assets/{symbol}/prices
 */

import { PrismClient } from '../core/client';
import type {
  ConsensusPrice, PriceHistoryPoint, GlobalMarket, FearGreedIndex, MarketMover, NVTRatio,
} from '../types';

export class CryptoModule {
  constructor(private c: PrismClient) {}

  // ─── PRICES ────────────────────────────────────────────

  /**
   * Consensus price for a crypto asset.
   * PRISM aggregates across multiple sources and returns a single trusted price.
   */
  async getPrice(
    symbol: string,
    opts?: {
      asset_id?: string;
      q?: string;              // Free-text disambiguation
      include_sources?: boolean;
      exclude_sources?: string;
      force_refresh?: boolean;
    }
  ): Promise<ConsensusPrice> {
    return this.c.get(`/crypto/price/${encodeURIComponent(symbol)}`, {
      params: opts as Record<string, string | boolean | undefined>,
      cacheTtl: 10,
    });
  }

  /** Batch price fetch by comma-separated symbols */
  async getPrices(symbols: string[]): Promise<ConsensusPrice[]> {
    return this.c.get('/crypto/prices/batch', {
      params: { symbols: symbols.join(',') },
      cacheTtl: 10,
    });
  }

  /** Batch via /batch/crypto/prices using coin_ids */
  async getBatchPrices(coinIds: string[]): Promise<ConsensusPrice[]> {
    return this.c.get('/batch/crypto/prices', {
      params: { coin_ids: coinIds.join(',') },
      cacheTtl: 10,
    });
  }

  /** Batch historical OHLCV for multiple coins */
  async getBatchHistory(coinIds: string[], days = 30): Promise<Record<string, PriceHistoryPoint[]>> {
    return this.c.get('/batch/crypto/history', {
      params: { coin_ids: coinIds.join(','), days },
      cacheTtl: 300,
    });
  }

  /** Sparklines for multiple tokens (by contract address) */
  async getBatchSparklines(tokens: string[]): Promise<Record<string, number[]>> {
    return this.c.get('/batch/crypto/sparklines', {
      params: { tokens: tokens.join(',') },
      cacheTtl: 300,
    });
  }

  /** Sparklines by symbol */
  async getSparklinesBySymbol(symbols: string[], days = 7): Promise<Record<string, number[]>> {
    return this.c.get('/batch/crypto/sparklines/symbols', {
      params: { symbols: symbols.join(','), days },
      cacheTtl: 300,
    });
  }

  /** Price source health — which data sources are online */
  async getPriceSources(): Promise<Array<{ source: string; status: string; latency?: number; [k: string]: unknown }>> {
    return this.c.get('/crypto/sources/status', { cacheTtl: 60 });
  }

  // ─── ASSET REGISTRY ────────────────────────────────────

  /** Search PRISM asset registry */
  async searchAssets(
    query: string,
    opts?: {
      asset_type?: string;
      category?: string;
      chain?: string;
      local_only?: boolean;
      auto_register?: boolean;
      max_age?: number;
      limit?: number;
    }
  ): Promise<unknown[]> {
    return this.c.get('/assets/search', {
      params: { q: query, ...opts } as Record<string, string | number | boolean | undefined>,
      cacheTtl: 60,
    });
  }

  /** Get asset by identifier (symbol, address, CoinGecko ID…) */
  async getAsset(identifier: string): Promise<unknown> {
    return this.c.get(`/assets/${encodeURIComponent(identifier)}`, { cacheTtl: 300 });
  }

  /** List all tracked assets */
  async listAssets(opts?: {
    asset_type?: string;
    limit?: number;
    offset?: number;
    order_by?: string;
    include_sparklines?: boolean;
  }): Promise<unknown[]> {
    return this.c.get('/assets/all', {
      params: opts as Record<string, string | number | boolean | undefined>,
      cacheTtl: 3600,
    });
  }

  /** Price history for an asset */
  async getPriceHistory(
    symbol: string,
    opts?: { interval?: string; limit?: number; asset_type?: string }
  ): Promise<PriceHistoryPoint[]> {
    return this.c.get(`/assets/${encodeURIComponent(symbol)}/prices`, {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 60,
    });
  }

  /** Asset registry stats */
  async getRegistryStats(): Promise<{ total?: number; [k: string]: unknown }> {
    return this.c.get('/assets/stats', { cacheTtl: 3600 });
  }

  // ─── MARKET DATA ───────────────────────────────────────

  /** Global crypto market snapshot */
  async getGlobal(): Promise<GlobalMarket> {
    return this.c.get('/crypto/global', { cacheTtl: 60 });
  }

  /** Fear & Greed Index */
  async getFearGreed(): Promise<FearGreedIndex> {
    return this.c.get('/market/fear-greed', { cacheTtl: 3600 });
  }

  /**
   * Full market overview — trending + movers.
   * Great single call for a dashboard snapshot.
   */
  async getMarketOverview(opts?: {
    include_trending?: boolean;
    include_movers?: boolean;
    movers_limit?: number;
  }): Promise<{ trending?: unknown[]; gainers?: unknown[]; losers?: unknown[]; [k: string]: unknown }> {
    return this.c.get('/market/overview', { params: opts, cacheTtl: 60 });
  }

  /** Top gainers in the last 24h */
  async getGainers(limit = 20): Promise<MarketMover[]> {
    return this.c.get('/market/crypto/gainers', { params: { limit }, cacheTtl: 60 });
  }

  /** Top losers in the last 24h */
  async getLosers(limit = 20): Promise<MarketMover[]> {
    return this.c.get('/market/crypto/losers', { params: { limit }, cacheTtl: 60 });
  }

  /** Aggregated gainers (de-duplicated across sources) */
  async getAggregatedGainers(limit = 20): Promise<MarketMover[]> {
    return this.c.get('/market/crypto/gainers/aggregated', { params: { limit }, cacheTtl: 60 });
  }

  /** Aggregated losers */
  async getAggregatedLosers(limit = 20): Promise<MarketMover[]> {
    return this.c.get('/market/crypto/losers/aggregated', { params: { limit }, cacheTtl: 60 });
  }

  // ─── TRENDING ──────────────────────────────────────────

  /** Trending crypto tokens */
  async getTrending(): Promise<unknown[]> {
    return this.c.get('/crypto/trending', { cacheTtl: 300 });
  }

  /** Trending DEX pools */
  async getTrendingPools(opts?: { duration?: string; limit?: number }): Promise<unknown[]> {
    return this.c.get('/crypto/trending/pools', { params: opts, cacheTtl: 300 });
  }

  /** Trending EVM tokens (optional chain filter) */
  async getTrendingEVM(opts?: { chain?: string; limit?: number }): Promise<unknown[]> {
    return this.c.get('/crypto/trending/evm', { params: opts, cacheTtl: 300 });
  }

  /** Solana tokens still on bonding curve */
  async getSolanaBonding(limit = 50): Promise<unknown[]> {
    return this.c.get('/crypto/trending/solana/bonding', { params: { limit }, cacheTtl: 300 });
  }

  /** Solana tokens that have graduated from bonding curve */
  async getSolanaGraduated(limit = 50): Promise<unknown[]> {
    return this.c.get('/crypto/trending/solana/graduated', { params: { limit }, cacheTtl: 300 });
  }

  /** All trending sources in one call */
  async getAllTrending(opts?: {
    include_pools?: boolean;
    include_solana?: boolean;
    evm_chains?: string;
    limit_per_source?: number;
    enrich?: boolean;
    dedupe_by_family?: boolean;
  }): Promise<unknown> {
    return this.c.get('/crypto/trending/all', {
      params: opts as Record<string, string | number | boolean | undefined>,
      cacheTtl: 300,
    });
  }

  // ─── INDEXES ───────────────────────────────────────────

  /** Crypto market index (broad market) */
  async getCryptoIndex(): Promise<unknown> {
    return this.c.get('/indexes/crypto', { cacheTtl: 3600 });
  }

  /** DeFi sector index */
  async getDefiIndex(): Promise<unknown> {
    return this.c.get('/indexes/defi', { cacheTtl: 3600 });
  }

  /** All supported chains */
  async getChains(): Promise<Array<{ chain: string; chain_id?: number; [k: string]: unknown }>> {
    return this.c.get('/chains', { cacheTtl: 3600 });
  }

  // ─── VALUATION ─────────────────────────────────────────

  /**
   * NVT Ratio — Network Value to Transactions.
   * The "P/E ratio" for crypto: high NVT = overvalued relative to on-chain activity.
   */
  async getNVT(symbol: string): Promise<NVTRatio> {
    return this.c.get(`/valuation/crypto/${encodeURIComponent(symbol)}/nvt`, { cacheTtl: 3600 });
  }
}
