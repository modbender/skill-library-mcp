/**
 * PRISM OS — Module 6: Prediction Markets
 * Crowd intelligence from Polymarket, Kalshi, Manifold, Drift
 */

import { PrismHttpClient } from '../../core/client';
import { CanonicalResolver } from '../../core/canonical';
import { PredictionMarket } from '../../types/canonical';

export class PredictionsModule {
  constructor(
    private client: PrismHttpClient,
    private resolver: CanonicalResolver
  ) {}

  async getMarkets(filters?: {
    platform?: string;
    category?: string;
    minVolume?: number;
    status?: 'open' | 'closed' | 'resolved';
  }): Promise<PredictionMarket[]> {
    return this.client.get('/predictions/markets', { params: filters, cacheTtl: 60 });
  }

  async searchMarkets(query: string): Promise<PredictionMarket[]> {
    return this.client.get('/predictions/search', { params: { q: query }, cacheTtl: 120 });
  }

  async getTrendingMarkets(): Promise<PredictionMarket[]> {
    return this.client.get('/predictions/trending', { cacheTtl: 300 });
  }

  async getMarketsByCategory(category: string): Promise<PredictionMarket[]> {
    return this.client.get('/predictions/markets', { params: { category }, cacheTtl: 120 });
  }

  async getMarketsByAsset(query: string): Promise<PredictionMarket[]> {
    const id = await this.resolver.resolve(query);
    return this.client.get('/predictions/by-asset', { params: { id }, cacheTtl: 120 });
  }

  async getExpiringMarkets(withinHours: number): Promise<PredictionMarket[]> {
    return this.client.get('/predictions/expiring', { params: { withinHours }, cacheTtl: 60 });
  }

  async getMarket(marketId: string): Promise<PredictionMarket> {
    return this.client.get('/predictions/market', { params: { id: marketId }, cacheTtl: 30 });
  }

  async getOdds(marketId: string): Promise<{ yes: number; no: number; timestamp: number }> {
    return this.client.get('/predictions/odds', { params: { id: marketId }, cacheTtl: 15 });
  }

  async getOddsHistory(
    marketId: string,
    from?: number,
    to?: number
  ): Promise<Array<{ yes: number; no: number; timestamp: number }>> {
    return this.client.get('/predictions/odds-history', {
      params: { id: marketId, from, to },
      cacheTtl: 300,
    });
  }

  async getVolume(marketId: string, window = '24h'): Promise<{ volume: number; trades: number }> {
    return this.client.get('/predictions/volume', { params: { id: marketId, window }, cacheTtl: 60 });
  }

  async getLiquidity(marketId: string): Promise<{ total: number; yes: number; no: number }> {
    return this.client.get('/predictions/liquidity', { params: { id: marketId }, cacheTtl: 30 });
  }

  async getQuote(
    marketId: string,
    side: 'yes' | 'no',
    amount: number
  ): Promise<{ price: number; shares: number; cost: number; priceImpact: number }> {
    return this.client.get('/predictions/quote', { params: { id: marketId, side, amount }, cacheTtl: 10 });
  }

  async placeOrder(
    marketId: string,
    side: 'yes' | 'no',
    amount: number,
    params?: { maxPrice?: number; walletAddress?: string }
  ): Promise<{ orderId: string; shares: number; cost: number; txHash?: string }> {
    return this.client.post('/predictions/order', { marketId, side, amount, ...params });
  }

  async getMyPositions(walletAddress: string): Promise<Array<{
    marketId: string;
    title: string;
    side: 'yes' | 'no';
    shares: number;
    avgPrice: number;
    currentPrice: number;
    pnl: number;
  }>> {
    return this.client.get('/predictions/positions', { params: { wallet: walletAddress }, cacheTtl: 30 });
  }

  async resolveMarket(marketId: string): Promise<{
    resolved: boolean;
    outcome?: boolean;
    resolvedAt?: string;
  }> {
    return this.client.get('/predictions/resolve', { params: { id: marketId }, cacheTtl: 60 });
  }

  /** Correlation between prediction market and asset price — is the market leading or lagging? */
  async getCorrelation(
    marketId: string,
    assetQuery: string
  ): Promise<{ correlation: number; leadLagDays: number; significance: number }> {
    const assetId = await this.resolver.resolve(assetQuery);
    return this.client.get('/predictions/correlation', { params: { marketId, assetId }, cacheTtl: 3600 });
  }

  /** Smart money positioning — detect sharp bettor flow */
  async getSharpMoney(marketId: string): Promise<{
    sharpBias: 'yes' | 'no' | 'neutral';
    sharpVolumePct: number;
    recentSharpTrades: Array<{ side: string; amount: number; price: number }>;
  }> {
    return this.client.get('/predictions/sharp-money', { params: { id: marketId }, cacheTtl: 300 });
  }

  /** Find arb between Polymarket, Kalshi, Manifold for same event */
  async getArbitrageOpps(): Promise<Array<{
    event: string;
    venue1: string;
    venue2: string;
    price1: number;
    price2: number;
    arbPct: number;
    requiredCapital: number;
  }>> {
    return this.client.get('/predictions/arb', { cacheTtl: 60 });
  }

  /** What price move does prediction market imply for an asset? */
  async getImpliedMove(assetQuery: string): Promise<{
    impliedUpside: number;
    impliedDownside: number;
    confidence: number;
    keyMarkets: Array<{ marketId: string; title: string; correlation: number }>;
  }> {
    const id = await this.resolver.resolve(assetQuery);
    return this.client.get('/predictions/implied-move', { params: { id }, cacheTtl: 1800 });
  }

  /** [Expansion] Agent-native bet placement with strategy — CLAWSHI */
  async agentBet(
    marketId: string,
    strategy: 'contrarian' | 'momentum' | 'sharp_follow' | 'arb'
  ): Promise<{
    recommendedSide: 'yes' | 'no';
    recommendedSize: number;
    expectedValue: number;
    reasoning: string[];
  }> {
    return this.client.post('/predictions/agent-bet', { marketId, strategy });
  }

  /** [Expansion] Multi-agent consensus — aggregate views across agent fleet */
  async getMultiAgentConsensus(marketIds: string[]): Promise<Array<{
    marketId: string;
    consensusSide: 'yes' | 'no';
    confidence: number;
    agentCount: number;
  }>> {
    return this.client.post('/predictions/consensus', { marketIds });
  }
}
