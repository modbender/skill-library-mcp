/**
 * DeFi + Onchain Module
 *
 * DeFi Endpoints:
 *   GET /defi/tvl/total
 *   GET /defi/tvl/chains
 *   GET /defi/tvl/protocol/{protocol}
 *   GET /defi/yields
 *   GET /defi/stablecoins
 *   GET /defi/bridges
 *   GET /defi/protocols
 *   GET /defi/protocol/{symbol}/info
 *   GET /gas
 *   GET /gas/{chain}
 *   GET /convert
 *   GET /wallets/{address}/balances
 *   GET /wallets/{address}/native
 *   GET /dex/pairs
 *   GET /dex/{dex}/pairs
 *   GET /dex/{dex}/{symbol}/funding
 *   GET /dex/{dex}/{symbol}/oi
 *   GET /dex/{symbol}/funding/all
 *   GET /dex/{symbol}/oi/all
 *   GET /dex/info
 *   GET /pools/{address}/pairs
 *   GET /pools/{address}/ohlcv
 *
 * Onchain Endpoints:
 *   GET /onchain/holders/{address}/top
 *   GET /onchain/holders/{address}/distribution
 *   GET /onchain/supply/{symbol}
 *   GET /onchain/active-addresses/{symbol}
 *   GET /onchain/transaction-count/{symbol}
 *   GET /onchain/whale-movements
 *   GET /onchain/exchange-flows/{symbol}
 *   GET /analytics/holders/{address}
 *   GET /analytics/bonding/{address}
 *   GET /analytics/price/onchain/{address}
 */

import { PrismClient } from '../core/client';
import type {
  Protocol, YieldPool, Stablecoin, Bridge, WalletBalance, GasPrice,
  FundingRate, OpenInterest, DexPair, PoolOHLCV,
  HolderEntry, HolderDistribution, WhaleMovement, ExchangeFlow, OnchainSupply,
} from '../types';

export class DeFiModule {
  constructor(private c: PrismClient) {}

  // ─── TVL ───────────────────────────────────────────────

  /** Total value locked across all DeFi protocols */
  async getTotalTVL(): Promise<{ tvl: number; change_1d?: number; change_7d?: number; [k: string]: unknown }> {
    return this.c.get('/defi/tvl/total', { cacheTtl: 300 });
  }

  /** TVL broken down by chain */
  async getChainTVLs(limit = 20): Promise<Array<{ chain: string; tvl: number; [k: string]: unknown }>> {
    return this.c.get('/defi/tvl/chains', { params: { limit }, cacheTtl: 300 });
  }

  /** TVL for a specific protocol (e.g. "uniswap", "aave", "lido") */
  async getProtocolTVL(protocol: string): Promise<{ protocol: string; tvl: number; history?: unknown[]; [k: string]: unknown }> {
    return this.c.get(`/defi/tvl/protocol/${encodeURIComponent(protocol)}`, { cacheTtl: 300 });
  }

  // ─── PROTOCOLS ─────────────────────────────────────────

  /** Search/list DeFi protocols */
  async getProtocols(opts?: {
    category?: string;
    chain?: string;
    min_tvl?: number;
    limit?: number;
  }): Promise<Protocol[]> {
    return this.c.get('/defi/protocols', {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 300,
    });
  }

  /** Look up a specific protocol by symbol */
  async getProtocolInfo(symbol: string): Promise<Protocol> {
    return this.c.get(`/defi/protocol/${encodeURIComponent(symbol)}/info`, { cacheTtl: 300 });
  }

  // ─── YIELDS ────────────────────────────────────────────

  /**
   * Yield farming opportunities across DeFi.
   * Filter by chain, APY, TVL, stablecoin-only.
   * Key tool for yield-optimizer agents.
   */
  async getYields(opts?: {
    chain?: string;
    min_tvl?: number;
    min_apy?: number;
    stablecoin?: boolean;
    limit?: number;
  }): Promise<YieldPool[]> {
    return this.c.get('/defi/yields', {
      params: opts as Record<string, string | number | boolean | undefined>,
      cacheTtl: 300,
    });
  }

  // ─── STABLECOINS ───────────────────────────────────────

  /**
   * All tracked stablecoins with peg health.
   * Shows USDT, USDC, DAI, FRAX, USDE — critical for depeg risk monitoring.
   */
  async getStablecoins(limit = 50): Promise<Stablecoin[]> {
    return this.c.get('/defi/stablecoins', { params: { limit }, cacheTtl: 300 });
  }

  // ─── BRIDGES ───────────────────────────────────────────

  /** Cross-chain bridge data (TVL, volume) */
  async getBridges(limit = 20): Promise<Bridge[]> {
    return this.c.get('/defi/bridges', { params: { limit }, cacheTtl: 300 });
  }

  // ─── GAS ───────────────────────────────────────────────

  /** Gas prices across all tracked chains */
  async getAllGas(): Promise<GasPrice[]> {
    return this.c.get('/gas', { cacheTtl: 15 });
  }

  /** Gas price for a specific chain */
  async getChainGas(chain: string): Promise<GasPrice> {
    return this.c.get(`/gas/${encodeURIComponent(chain)}`, { cacheTtl: 15 });
  }

  // ─── CONVERSION ────────────────────────────────────────

  /** Convert between any two assets using live rates */
  async convert(from: string, to: string, amount?: number): Promise<{
    from: string; to: string; rate: number; converted?: number; [k: string]: unknown;
  }> {
    return this.c.get('/convert', { params: { from, to, amount }, cacheTtl: 10 });
  }

  // ─── WALLETS ───────────────────────────────────────────

  /** All token balances in a wallet */
  async getWalletBalances(
    address: string,
    opts?: {
      chain?: string;
      min_value_usd?: number;
      exclude_spam?: boolean;
      limit?: number;
    }
  ): Promise<WalletBalance[]> {
    return this.c.get(`/wallets/${address}/balances`, {
      params: opts as Record<string, string | number | boolean | undefined>,
      cacheTtl: 60,
    });
  }

  /** Native token balance only (ETH, SOL, BNB…) */
  async getNativeBalance(address: string, chain?: string): Promise<{ balance: number; value_usd?: number; [k: string]: unknown }> {
    return this.c.get(`/wallets/${address}/native`, { params: { chain }, cacheTtl: 30 });
  }

  // ─── DEX ───────────────────────────────────────────────

  /** All DEX trading pairs across all venues */
  async getAllDexPairs(): Promise<DexPair[]> {
    return this.c.get('/dex/pairs', { cacheTtl: 300 });
  }

  /** Pairs for a specific DEX */
  async getDexPairs(dex: string): Promise<DexPair[]> {
    return this.c.get(`/dex/${encodeURIComponent(dex)}/pairs`, { cacheTtl: 300 });
  }

  /** Funding rate for a perp on a specific DEX */
  async getFundingRate(dex: string, symbol: string): Promise<FundingRate> {
    return this.c.get(`/dex/${encodeURIComponent(dex)}/${encodeURIComponent(symbol)}/funding`, { cacheTtl: 60 });
  }

  /** Open interest for a perp on a specific DEX */
  async getOpenInterest(dex: string, symbol: string): Promise<OpenInterest> {
    return this.c.get(`/dex/${encodeURIComponent(dex)}/${encodeURIComponent(symbol)}/oi`, { cacheTtl: 60 });
  }

  /** Funding rates across ALL DEXes for a symbol */
  async getAllFundingRates(symbol: string): Promise<FundingRate[]> {
    return this.c.get(`/dex/${encodeURIComponent(symbol)}/funding/all`, { cacheTtl: 60 });
  }

  /** Open interest across ALL DEXes for a symbol */
  async getAllOpenInterest(symbol: string): Promise<OpenInterest[]> {
    return this.c.get(`/dex/${encodeURIComponent(symbol)}/oi/all`, { cacheTtl: 60 });
  }

  /** DEX metadata (supported venues, chains) */
  async getDexInfo(): Promise<unknown> {
    return this.c.get('/dex/info', { cacheTtl: 3600 });
  }

  // ─── POOLS ─────────────────────────────────────────────

  /** Token pairs for a pool address */
  async getPoolPairs(address: string, opts?: { chain?: string; limit?: number }): Promise<DexPair[]> {
    return this.c.get(`/pools/${address}/pairs`, {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 300,
    });
  }

  /** OHLCV candlestick data for a pool */
  async getPoolOHLCV(
    address: string,
    opts?: { chain?: string; timeframe?: string; limit?: number }
  ): Promise<PoolOHLCV[]> {
    return this.c.get(`/pools/${address}/ohlcv`, {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 60,
    });
  }
}

export class OnchainModule {
  constructor(private c: PrismClient) {}

  // ─── HOLDERS ───────────────────────────────────────────

  /** Top token holders for a contract address */
  async getTopHolders(address: string, opts?: { chain?: string; limit?: number }): Promise<HolderEntry[]> {
    return this.c.get(`/onchain/holders/${address}/top`, {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 3600,
    });
  }

  /** Holder distribution (concentration, gini, brackets) */
  async getHolderDistribution(address: string, chain?: string): Promise<HolderDistribution> {
    return this.c.get(`/onchain/holders/${address}/distribution`, {
      params: { chain },
      cacheTtl: 3600,
    });
  }

  /** Aggregate holder analytics for a contract */
  async getHolderStats(address: string, chain?: string): Promise<unknown> {
    return this.c.get(`/analytics/holders/${address}`, { params: { chain }, cacheTtl: 3600 });
  }

  // ─── SUPPLY ────────────────────────────────────────────

  /** Circulating, total, burned, locked supply */
  async getSupply(symbol: string, opts?: { chain?: string; address?: string }): Promise<OnchainSupply> {
    return this.c.get(`/onchain/supply/${encodeURIComponent(symbol)}`, {
      params: opts as Record<string, string | undefined>,
      cacheTtl: 3600,
    });
  }

  // ─── ACTIVITY ──────────────────────────────────────────

  /** Daily active addresses — network health indicator */
  async getActiveAddresses(
    symbol: string,
    opts?: { chain?: string; address?: string }
  ): Promise<{ active_addresses?: number; history?: unknown[]; [k: string]: unknown }> {
    return this.c.get(`/onchain/active-addresses/${encodeURIComponent(symbol)}`, {
      params: opts as Record<string, string | undefined>,
      cacheTtl: 3600,
    });
  }

  /** Daily transaction count */
  async getTransactionCount(
    symbol: string,
    opts?: { chain?: string; address?: string }
  ): Promise<{ tx_count?: number; history?: unknown[]; [k: string]: unknown }> {
    return this.c.get(`/onchain/transaction-count/${encodeURIComponent(symbol)}`, {
      params: opts as Record<string, string | undefined>,
      cacheTtl: 3600,
    });
  }

  // ─── WHALE & FLOW ──────────────────────────────────────

  /**
   * Whale movements — large transfers in/out of tracked addresses.
   * Essential for "smart money" tracking agents.
   */
  async getWhaleMovements(
    address: string,
    opts?: { chain?: string; min_value_usd?: number; limit?: number }
  ): Promise<WhaleMovement[]> {
    return this.c.get('/onchain/whale-movements', {
      params: { address, ...opts } as Record<string, string | number | undefined>,
      cacheTtl: 60,
    });
  }

  /** Exchange inflows/outflows — key signal for buy/sell pressure */
  async getExchangeFlows(
    symbol: string,
    address: string,
    opts?: { chain?: string; period?: string }
  ): Promise<ExchangeFlow> {
    return this.c.get(`/onchain/exchange-flows/${encodeURIComponent(symbol)}`, {
      params: { address, ...opts } as Record<string, string | undefined>,
      cacheTtl: 300,
    });
  }

  // ─── TOKEN ANALYTICS ───────────────────────────────────

  /** Bonding curve status for a token (Pump.fun style) */
  async getBondingStatus(address: string): Promise<{
    on_bonding_curve: boolean;
    progress_pct?: number;
    graduated?: boolean;
    [k: string]: unknown;
  }> {
    return this.c.get(`/analytics/bonding/${address}`, { cacheTtl: 60 });
  }

  /** On-chain price from DEX pool data (as opposed to CEX price) */
  async getOnchainPrice(address: string, chain?: string): Promise<{
    price: number;
    source?: string;
    [k: string]: unknown;
  }> {
    return this.c.get(`/analytics/price/onchain/${address}`, {
      params: { chain },
      cacheTtl: 30,
    });
  }
}
