/**
 * PRISM OS — Module 2: Market Data
 * Real-time and historical market intelligence.
 * Sources: CoinGecko, CMC, FMP, proprietary aggregation
 */

import { PrismHttpClient } from '../../core/client';
import { CanonicalResolver } from '../../core/canonical';
import {
  PriceData,
  OHLCVCandle,
  OrderBook,
  FundingRate,
  ChainId,
  VenueId,
} from '../../types/canonical';

type Interval = '1m' | '5m' | '15m' | '1h' | '4h' | '1d' | '1w';
type Window = '1h' | '24h' | '7d' | '30d';

export class MarketModule {
  constructor(
    private client: PrismHttpClient,
    private resolver: CanonicalResolver
  ) {}

  // ─────────────────────────────────────────────
  // SPOT PRICES
  // ─────────────────────────────────────────────

  async getPrice(query: string): Promise<PriceData> {
    const id = await this.resolver.resolve(query);
    return this.client.get<PriceData>('/market/price', {
      params: { id },
      cacheTtl: 10,
    });
  }

  async getPriceMulti(queries: string[]): Promise<PriceData[]> {
    const resolved = await this.resolver.batchResolve(queries);
    const ids = resolved.filter((r) => r.prismId).map((r) => r.prismId!);
    return this.client.get<PriceData[]>('/market/prices', {
      params: { ids: ids.join(',') },
      cacheTtl: 10,
    });
  }

  async getPriceByContract(address: string, chain: ChainId): Promise<PriceData> {
    const id = await this.resolver.resolve(address, { chain });
    return this.getPrice(id);
  }

  async getPriceHistory(
    query: string,
    from: number,
    to: number,
    interval: Interval = '1h'
  ): Promise<OHLCVCandle[]> {
    const id = await this.resolver.resolve(query);
    return this.client.get<OHLCVCandle[]>('/market/history', {
      params: { id, from, to, interval },
      cacheTtl: 60,
    });
  }

  // ─────────────────────────────────────────────
  // ORDER BOOK & DEPTH
  // ─────────────────────────────────────────────

  async getOrderBook(query: string, exchange: VenueId): Promise<OrderBook> {
    const id = await this.resolver.resolve(query);
    return this.client.get<OrderBook>('/market/orderbook', {
      params: { id, exchange },
      cacheTtl: 2,
    });
  }

  /**
   * Liquidity depth within X basis points of mid price
   * e.g. getDepth("ETH", "binance", 50) → $ available within 0.5%
   */
  async getDepth(query: string, exchange: VenueId, bps: number): Promise<{
    bidDepth: number;
    askDepth: number;
    totalDepth: number;
    midPrice: number;
  }> {
    const id = await this.resolver.resolve(query);
    return this.client.get('/market/depth', { params: { id, exchange, bps }, cacheTtl: 5 });
  }

  async getSpread(query: string, exchange: VenueId): Promise<{
    bid: number;
    ask: number;
    spreadBps: number;
    timestamp: number;
  }> {
    const id = await this.resolver.resolve(query);
    return this.client.get('/market/spread', { params: { id, exchange }, cacheTtl: 5 });
  }

  // ─────────────────────────────────────────────
  // VOLUME & FLOWS
  // ─────────────────────────────────────────────

  async getVolume(query: string, window: Window = '24h'): Promise<{
    total: number;
    byExchange: Record<string, number>;
    window: Window;
  }> {
    const id = await this.resolver.resolve(query);
    return this.client.get('/market/volume', { params: { id, window }, cacheTtl: 30 });
  }

  /** CEX vs DEX volume breakdown — key signal for DeFi agents */
  async getVolumeBreakdown(query: string): Promise<{
    cex: number;
    dex: number;
    cexPct: number;
    dexPct: number;
    topVenues: Array<{ venue: string; volume: number }>;
  }> {
    const id = await this.resolver.resolve(query);
    return this.client.get('/market/volume-breakdown', { params: { id }, cacheTtl: 60 });
  }

  /** Net buy/sell flow — directional pressure indicator */
  async getNetFlow(query: string, window: Window = '24h'): Promise<{
    netFlow: number;
    buyVolume: number;
    sellVolume: number;
    buyPressure: number;   // 0-100
  }> {
    const id = await this.resolver.resolve(query);
    return this.client.get('/market/flow', { params: { id, window }, cacheTtl: 30 });
  }

  // ─────────────────────────────────────────────
  // MARKET CAP & SUPPLY
  // ─────────────────────────────────────────────

  async getMarketCap(query: string): Promise<{ marketCap: number; rank: number }> {
    const id = await this.resolver.resolve(query);
    return this.client.get('/market/mcap', { params: { id }, cacheTtl: 60 });
  }

  async getFullyDilutedValuation(query: string): Promise<{ fdv: number; ratio: number }> {
    const id = await this.resolver.resolve(query);
    return this.client.get('/market/fdv', { params: { id }, cacheTtl: 300 });
  }

  async getCirculatingSupply(query: string): Promise<{
    circulating: string;
    total: string;
    max: string | null;
    supplyPct: number;
  }> {
    const id = await this.resolver.resolve(query);
    return this.client.get('/market/supply', { params: { id }, cacheTtl: 3600 });
  }

  async getUnlockSchedule(query: string): Promise<Array<{
    date: string;
    unlockAmount: number;
    unlockUsd: number;
    cumulativePct: number;
  }>> {
    const id = await this.resolver.resolve(query);
    return this.client.get('/market/unlocks', { params: { id }, cacheTtl: 3600 });
  }

  // ─────────────────────────────────────────────
  // DERIVATIVES
  // ─────────────────────────────────────────────

  async getFundingRate(
    query: string,
    exchange?: VenueId
  ): Promise<FundingRate | FundingRate[]> {
    const id = await this.resolver.resolve(query);
    return this.client.get('/market/funding', { params: { id, exchange }, cacheTtl: 30 });
  }

  async getOpenInterest(query: string, exchange?: VenueId): Promise<{
    total: number;
    byExchange: Record<string, number>;
    change24h: number;
  }> {
    const id = await this.resolver.resolve(query);
    return this.client.get('/market/oi', { params: { id, exchange }, cacheTtl: 30 });
  }

  /** Spot vs futures basis — contango/backwardation signal */
  async getBasisSpread(query: string): Promise<{
    spot: number;
    futures1m: number;
    futures3m: number;
    basis1m: number;
    basisPct1m: number;
    structure: 'contango' | 'backwardation' | 'flat';
  }> {
    const id = await this.resolver.resolve(query);
    return this.client.get('/market/basis', { params: { id }, cacheTtl: 60 });
  }

  async getOptionsChain(query: string, expiry?: string): Promise<Array<{
    strike: number;
    expiry: string;
    callBid: number;
    callAsk: number;
    putBid: number;
    putAsk: number;
    callOI: number;
    putOI: number;
    callIV: number;
    putIV: number;
  }>> {
    const id = await this.resolver.resolve(query);
    return this.client.get('/market/options', { params: { id, expiry }, cacheTtl: 60 });
  }

  // ─────────────────────────────────────────────
  // MACRO
  // ─────────────────────────────────────────────

  async getDominance(query: string): Promise<{
    marketSharePct: number;
    change24h: number;
  }> {
    const id = await this.resolver.resolve(query);
    return this.client.get('/market/dominance', { params: { id }, cacheTtl: 300 });
  }

  async getGlobalMetrics(): Promise<{
    totalMarketCap: number;
    totalVolume24h: number;
    btcDominance: number;
    ethDominance: number;
    defiTVL: number;
    fearGreed: number;
    activeCryptocurrencies: number;
  }> {
    return this.client.get('/market/global', { cacheTtl: 120 });
  }

  async getFearGreedIndex(): Promise<{
    value: number;
    label: 'Extreme Fear' | 'Fear' | 'Neutral' | 'Greed' | 'Extreme Greed';
    yesterday: number;
    lastWeek: number;
    lastMonth: number;
  }> {
    return this.client.get('/market/fear-greed', { cacheTtl: 3600 });
  }

  async getTrending(category?: string): Promise<Array<{
    prismId: string;
    name: string;
    symbol: string;
    price: number;
    change24h: number;
    trendScore: number;
  }>> {
    return this.client.get('/market/trending', { params: { category }, cacheTtl: 300 });
  }

  // ─────────────────────────────────────────────
  // EXPANSION TOOLS (AI/Agent-native signals)
  // ─────────────────────────────────────────────

  /**
   * [Expansion] AI predictive score — Kavout-style ML ranking
   * Combines momentum, volume anomaly, on-chain activity, sentiment
   */
  async getAIScore(query: string): Promise<{
    score: number;         // 0-100
    signal: 'strong_buy' | 'buy' | 'neutral' | 'sell' | 'strong_sell';
    factors: {
      momentum: number;
      volumeAnomaly: number;
      sentimentScore: number;
      onChainActivity: number;
      technicalScore: number;
    };
    confidence: number;
    updatedAt: string;
  }> {
    const id = await this.resolver.resolve(query);
    return this.client.get('/market/ai-score', { params: { id }, cacheTtl: 300 });
  }

  /**
   * [Expansion] Social score — AlphaSense-style sentiment
   */
  async getSocialScore(query: string): Promise<{
    score: number;
    volume: number;
    velocity: number;
    topInfluencers: string[];
    keyNarratives: string[];
  }> {
    const id = await this.resolver.resolve(query);
    return this.client.get('/market/social-score', { params: { id }, cacheTtl: 600 });
  }

  /**
   * [Expansion] Narrative momentum — what story is driving this asset?
   */
  async getNarrativeMomentum(query: string): Promise<{
    activeNarratives: Array<{
      narrative: string;
      strength: number;
      peaking: boolean;
    }>;
    emergingNarratives: string[];
    fadingNarratives: string[];
  }> {
    const id = await this.resolver.resolve(query);
    return this.client.get('/market/narratives', { params: { id }, cacheTtl: 1800 });
  }
}
