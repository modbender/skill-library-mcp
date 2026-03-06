/**
 * Resolution & Families — PRISM's Canonical Identity Layer
 *
 * Endpoints:
 *   GET  /resolve/{symbol}
 *   POST /resolve/batch
 *   GET  /resolve/family/{family_id}
 *   GET  /resolve/venues/{symbol}
 *   GET  /families
 *   GET  /families/{family_id}
 *   GET  /families/{family_id}/price
 *   GET  /families/{family_id}/instances
 *   GET  /families/{family_id}/venues
 *   GET  /search
 *   GET  /universe/search
 *   GET  /universe/crypto | /stocks | /etfs | /indexes
 *   GET  /universe/stats
 *   GET  /contracts/{chain}/{address}
 *   POST /agent/resolve
 */

import { PrismClient } from '../core/client';
import type { ResolvedAsset, Family, FamilyInstance, Venue, AssetType } from '../types';

export class ResolutionModule {
  constructor(private c: PrismClient) {}

  /**
   * Resolve ANY identifier → canonical asset.
   * Pass a ticker, contract address, CoinGecko ID, full name — PRISM figures it out.
   * Most important endpoint in the whole API.
   */
  async resolve(
    symbol: string,
    opts?: {
      context?: string;        // "This is a DeFi yield token on Arbitrum"
      chain?: string;
      venue?: string;
      expand?: boolean;        // Include venues, instances
      use_llm?: boolean;       // Use LLM disambiguation
      live_price?: boolean;    // Attach live price to response
    }
  ): Promise<ResolvedAsset> {
    return this.c.get(`/resolve/${encodeURIComponent(symbol)}`, {
      params: opts as Record<string, string | number | boolean | undefined>,
      cacheTtl: 300,
    });
  }

  /**
   * Resolve many symbols at once.
   * Body: { symbols: string[], context?: string, expand?: boolean }
   */
  async resolveBatch(
    symbols: string[],
    opts?: { context?: string; expand?: boolean }
  ): Promise<ResolvedAsset[]> {
    return this.c.post('/resolve/batch', { symbols, ...opts });
  }

  /**
   * Get venues (exchanges / DEXes) where a symbol trades.
   * Useful for routing: "where can I buy PEPE?"
   */
  async getVenues(
    symbol: string,
    opts?: { asset_type?: AssetType; chain?: string; contract_address?: string }
  ): Promise<Venue[]> {
    return this.c.get(`/resolve/venues/${encodeURIComponent(symbol)}`, {
      params: opts as Record<string, string | undefined>,
      cacheTtl: 300,
    });
  }

  /**
   * Get a Family by ID.
   * Families = "same asset, many forms" (e.g. BTC on all CEXes + WBTC on Ethereum)
   */
  async getFamily(familyId: string, expand?: boolean): Promise<Family> {
    return this.c.get(`/resolve/family/${encodeURIComponent(familyId)}`, {
      params: { expand },
      cacheTtl: 300,
    });
  }

  /** List all families (paginated by category) */
  async listFamilies(opts?: { category?: string; limit?: number }): Promise<Family[]> {
    return this.c.get('/families', { params: opts, cacheTtl: 300 });
  }

  /** Get full family details */
  async getFamilyDetail(familyId: string): Promise<Family> {
    return this.c.get(`/families/${encodeURIComponent(familyId)}`, { cacheTtl: 300 });
  }

  /** Get consensus price for a family (all instances aggregated) */
  async getFamilyPrice(familyId: string): Promise<{ family_id: string; price: number; [k: string]: unknown }> {
    return this.c.get(`/families/${encodeURIComponent(familyId)}/price`, { cacheTtl: 30 });
  }

  /** Get all instances of a family (by chain, exchange, etc.) */
  async getFamilyInstances(
    familyId: string,
    opts?: { chain?: string; include_inactive?: boolean }
  ): Promise<FamilyInstance[]> {
    return this.c.get(`/families/${encodeURIComponent(familyId)}/instances`, {
      params: opts as Record<string, string | boolean | undefined>,
      cacheTtl: 300,
    });
  }

  /** Get venues where this family's assets trade */
  async getFamilyVenues(familyId: string): Promise<Venue[]> {
    return this.c.get(`/families/${encodeURIComponent(familyId)}/venues`, { cacheTtl: 300 });
  }

  /**
   * Universal search across stocks, crypto, ETFs, indexes, forex.
   * The broadest search endpoint — good for UI search bars.
   */
  async search(
    query: string,
    opts?: {
      type?: AssetType;
      category?: string;
      chain?: string;
      include?: string;    // comma-separated: 'price,market_cap'
      limit?: number;
      cursor?: string;
    }
  ): Promise<ResolvedAsset[]> {
    return this.c.get('/search', {
      params: { q: query, ...opts } as Record<string, string | number | undefined>,
      cacheTtl: 60,
    });
  }

  /** Universe search — verified assets only, sorted by market cap */
  async universeSearch(
    query: string,
    opts?: {
      type?: 'crypto' | 'stock' | 'etf' | 'index' | 'forex';
      chain?: string;
      verified?: boolean;
      limit?: number;
      offset?: number;
    }
  ): Promise<ResolvedAsset[]> {
    return this.c.get('/universe/search', {
      params: { q: query, ...opts } as Record<string, string | number | boolean | undefined>,
      cacheTtl: 60,
    });
  }

  /** Full crypto universe — all tracked tokens */
  async cryptoUniverse(opts?: {
    chain?: string;
    verified?: boolean;
    limit?: number;
    offset?: number;
    order_by?: 'market_cap' | 'volume' | 'symbol' | 'lookup_count' | 'created_at';
  }): Promise<ResolvedAsset[]> {
    return this.c.get('/universe/crypto', {
      params: opts as Record<string, string | number | boolean | undefined>,
      cacheTtl: 3600,
    });
  }

  /** Full stocks universe */
  async stocksUniverse(opts?: {
    exchange?: string;
    verified?: boolean;
    limit?: number;
    offset?: number;
    order_by?: 'market_cap' | 'volume' | 'symbol' | 'lookup_count' | 'created_at';
  }): Promise<ResolvedAsset[]> {
    return this.c.get('/universe/stocks', {
      params: opts as Record<string, string | number | boolean | undefined>,
      cacheTtl: 3600,
    });
  }

  /** ETF universe */
  async etfUniverse(opts?: {
    exchange?: string;
    verified?: boolean;
    limit?: number;
    offset?: number;
  }): Promise<ResolvedAsset[]> {
    return this.c.get('/universe/etfs', {
      params: opts as Record<string, string | number | boolean | undefined>,
      cacheTtl: 3600,
    });
  }

  /** Index universe */
  async indexUniverse(opts?: { limit?: number; offset?: number }): Promise<ResolvedAsset[]> {
    return this.c.get('/universe/indexes', { params: opts, cacheTtl: 3600 });
  }

  /** Stats on how many assets PRISM tracks */
  async universeStats(): Promise<{ crypto?: number; stocks?: number; etfs?: number; indexes?: number; [k: string]: unknown }> {
    return this.c.get('/universe/stats', { cacheTtl: 3600 });
  }

  /** Look up a contract address on a specific chain */
  async getContract(chain: string, address: string): Promise<ResolvedAsset> {
    return this.c.get(`/contracts/${encodeURIComponent(chain)}/${encodeURIComponent(address)}`, {
      cacheTtl: 300,
    });
  }

  /**
   * Agent-optimised batch resolve.
   * POST /agent/resolve — same as /resolve/batch but with richer context options.
   */
  async agentResolve(
    queries: string[],
    opts?: { include?: string; context?: string }
  ): Promise<ResolvedAsset[]> {
    return this.c.post('/agent/resolve', { queries, ...opts });
  }
}
