/**
 * PRISM OS — Module 3: DEX & Liquidity
 * On-chain trading: quote, route, execute, analyze pools
 * Venues: Uniswap, Jupiter, Orca, Raydium, Curve, Balancer, Aerodrome, etc.
 */

import { PrismHttpClient } from '../../core/client';
import { CanonicalResolver } from '../../core/canonical';
import { SwapQuote, PoolData, ChainId, VenueId } from '../../types/canonical';

export interface SwapParams {
  fromQuery: string;
  toQuery: string;
  amount: string;           // in wei/lamports (smallest unit) or human-readable
  amountIsHuman?: boolean;
  chain: ChainId;
  slippageTolerance?: number;  // e.g. 0.005 = 0.5%
  deadline?: number;           // unix timestamp
  recipient?: string;
}

export class DexModule {
  constructor(
    private client: PrismHttpClient,
    private resolver: CanonicalResolver
  ) {}

  // ─────────────────────────────────────────────
  // QUOTING & ROUTING
  // ─────────────────────────────────────────────

  /**
   * Best quote across all DEXes on a given chain
   */
  async getQuote(params: SwapParams): Promise<SwapQuote> {
    const [fromId, toId] = await Promise.all([
      this.resolver.resolve(params.fromQuery, { chain: params.chain }),
      this.resolver.resolve(params.toQuery, { chain: params.chain }),
    ]);

    // Safety check: prevent swapping an asset for itself
    if (fromId === toId) {
      throw new Error(`Cannot swap ${params.fromQuery} for itself (same PRISM-ID: ${fromId})`);
    }

    return this.client.get<SwapQuote>('/dex/quote', {
      params: {
        fromId,
        toId,
        amount: params.amount,
        amountIsHuman: params.amountIsHuman,
        chain: params.chain,
        slippage: params.slippageTolerance ?? 0.005,
      },
      cacheTtl: 15,
    });
  }

  /**
   * Compare quotes across all chains — find cheapest execution
   */
  async getQuoteMultiChain(
    fromQuery: string,
    toQuery: string,
    amount: string
  ): Promise<Array<SwapQuote & { totalCostUsd: number; chain: ChainId }>> {
    const chains: ChainId[] = ['ethereum', 'arbitrum', 'base', 'solana', 'polygon'];
    const results = await Promise.allSettled(
      chains.map((chain) => this.getQuote({ fromQuery, toQuery, amount, chain }))
    );

    return results
      .filter((r) => r.status === 'fulfilled')
      .map((r) => (r as PromiseFulfilledResult<SwapQuote>).value)
      .map((q) => ({ ...q, totalCostUsd: q.gasUsd }))
      .sort((a, b) => parseFloat(b.expectedOutput) - parseFloat(a.expectedOutput));
  }

  /**
   * All available routes — agent can pick based on strategy
   */
  async getRoutes(
    fromQuery: string,
    toQuery: string,
    amount: string,
    chain: ChainId
  ): Promise<Array<{
    route: SwapQuote;
    protocol: string;
    outputAmount: string;
    priceImpact: number;
    isAggregated: boolean;
  }>> {
    const [fromId, toId] = await Promise.all([
      this.resolver.resolve(fromQuery, { chain }),
      this.resolver.resolve(toQuery, { chain }),
    ]);
    return this.client.get('/dex/routes', { params: { fromId, toId, amount, chain } });
  }

  async estimateSlippage(params: SwapParams): Promise<{
    estimatedSlippage: number;
    priceImpact: number;
    recommendation: 'safe' | 'caution' | 'high_impact';
  }> {
    const quote = await this.getQuote(params);
    const impact = quote.priceImpact;
    return {
      estimatedSlippage: quote.slippage,
      priceImpact: impact,
      recommendation: impact < 0.005 ? 'safe' : impact < 0.02 ? 'caution' : 'high_impact',
    };
  }

  async getMinOutput(
    params: SwapParams,
    slippageTolerance: number
  ): Promise<{ minOutput: string; minOutputUsd: number }> {
    const quote = await this.getQuote({ ...params, slippageTolerance });
    return { minOutput: quote.minimumOutput, minOutputUsd: 0 };
  }

  // ─────────────────────────────────────────────
  // EXECUTION
  // ─────────────────────────────────────────────

  /**
   * Build unsigned transaction — agent submits with its own signer
   */
  async buildSwapTx(params: SwapParams): Promise<{
    to: string;
    data: string;
    value: string;
    gasLimit: string;
    chain: ChainId;
    quoteId: string;
    expiresAt: number;
  }> {
    const quote = await this.getQuote(params);
    return this.client.post('/dex/build-tx', { quoteId: quote.quoteId, ...params });
  }

  /**
   * Dry run — preview exactly what will happen without executing
   */
  async simulateSwap(params: SwapParams): Promise<{
    willSucceed: boolean;
    expectedOutput: string;
    priceImpact: number;
    gasEstimate: string;
    warnings: string[];
  }> {
    const quote = await this.getQuote(params);
    return this.client.post('/dex/simulate', { quoteId: quote.quoteId });
  }

  /**
   * Full execution — requires a signer function or private key (handled externally)
   * Agent passes signed transaction back for broadcasting
   */
  async executeSwap(
    params: SwapParams,
    signTransaction: (txData: unknown) => Promise<string>
  ): Promise<{
    txHash: string;
    status: 'success' | 'failed' | 'pending';
    inputAmount: string;
    outputAmount: string;
    gasUsed: string;
    timestamp: number;
  }> {
    // 1. Get quote
    const quote = await this.getQuote(params);

    // 2. Build unsigned tx
    const txData = await this.buildSwapTx(params);

    // 3. Sign (externally — agent's wallet handles this)
    const signedTx = await signTransaction(txData);

    // 4. Broadcast
    return this.client.post('/dex/broadcast', {
      signedTx,
      quoteId: quote.quoteId,
      chain: params.chain,
    });
  }

  // ─────────────────────────────────────────────
  // POOL DATA
  // ─────────────────────────────────────────────

  /**
   * All pools for a given asset
   */
  async getPools(query: string, chain?: ChainId): Promise<PoolData[]> {
    const id = await this.resolver.resolve(query);
    return this.client.get('/dex/pools', { params: { id, chain }, cacheTtl: 120 });
  }

  async getPoolData(poolAddress: string, chain: ChainId): Promise<PoolData> {
    return this.client.get('/dex/pool', { params: { address: poolAddress, chain }, cacheTtl: 60 });
  }

  async getPoolsByTVL(chain: ChainId, limit = 20): Promise<PoolData[]> {
    return this.client.get('/dex/pools/top', { params: { chain, limit }, cacheTtl: 300 });
  }

  /** New pools — alpha hunting for new launches */
  async getNewPools(chain: ChainId, since?: number): Promise<Array<PoolData & {
    ageMinutes: number;
    honeypotRisk: boolean;
    initialLiquidity: number;
  }>> {
    return this.client.get('/dex/pools/new', {
      params: { chain, since: since ?? Date.now() - 86400000 },
      cacheTtl: 30,
    });
  }

  async getPoolHistory(poolAddress: string, from: number, to: number): Promise<Array<{
    timestamp: number;
    tvl: number;
    volume: number;
    fees: number;
  }>> {
    return this.client.get('/dex/pool/history', { params: { address: poolAddress, from, to } });
  }

  // ─────────────────────────────────────────────
  // LP ANALYTICS
  // ─────────────────────────────────────────────

  async getLPPosition(walletAddress: string, chain?: ChainId): Promise<Array<{
    pool: string;
    protocol: VenueId;
    token0: string;
    token1: string;
    liquidity: string;
    valueUsd: number;
    feesEarned: number;
    il: number;
  }>> {
    return this.client.get('/dex/lp-positions', {
      params: { wallet: walletAddress, chain },
      cacheTtl: 60,
    });
  }

  async getImpermanentLoss(
    poolAddress: string,
    chain: ChainId,
    entryPrices: { token0: number; token1: number }
  ): Promise<{
    ilPct: number;
    ilUsd: number;
    breakEvenDays: number;
    recommendation: 'hold' | 'exit';
  }> {
    return this.client.post('/dex/il-calc', { poolAddress, chain, entryPrices });
  }

  async getPoolFeeAPY(poolAddress: string, chain: ChainId): Promise<{
    feeApy: number;
    rewardApy: number;
    totalApy: number;
    window: string;
  }> {
    return this.client.get('/dex/pool/apy', { params: { address: poolAddress, chain }, cacheTtl: 300 });
  }

  // ─────────────────────────────────────────────
  // DEX-SPECIFIC
  // ─────────────────────────────────────────────

  async getSupportedDEXes(chain: ChainId): Promise<Array<{
    id: VenueId;
    name: string;
    tvl: number;
    volume24h: number;
  }>> {
    return this.client.get('/dex/supported', { params: { chain }, cacheTtl: 3600 });
  }

  async getDEXVolume(dex: VenueId, window: string = '24h'): Promise<{
    volume: number;
    change: number;
    txCount: number;
  }> {
    return this.client.get('/dex/venue-volume', { params: { dex, window }, cacheTtl: 300 });
  }

  /** Aggregator quote — 1inch/Paraswap/Li.fi style routing */
  async getAggregatorQuote(
    fromQuery: string,
    toQuery: string,
    amount: string,
    chain: ChainId
  ): Promise<{
    bestRoute: SwapQuote;
    alternatives: SwapQuote[];
    savings: number;
  }> {
    const [fromId, toId] = await Promise.all([
      this.resolver.resolve(fromQuery, { chain }),
      this.resolver.resolve(toQuery, { chain }),
    ]);
    return this.client.get('/dex/aggregator', { params: { fromId, toId, amount, chain }, cacheTtl: 10 });
  }

  // ─────────────────────────────────────────────
  // EXPANSION TOOLS
  // ─────────────────────────────────────────────

  /**
   * [Expansion] Yield-optimized LP entry — Zignaly-style auto-compounder selection
   */
  async yieldOptimize(
    fromQuery: string,
    targetChain: ChainId,
    strategy: 'max_yield' | 'min_il' | 'balanced'
  ): Promise<{
    recommendedPool: PoolData;
    expectedApy: number;
    ilRisk: 'low' | 'medium' | 'high';
    steps: Array<{ action: string; details: string }>;
  }> {
    const id = await this.resolver.resolve(fromQuery);
    return this.client.post('/dex/yield-optimize', { id, targetChain, strategy });
  }

  /**
   * [Expansion] Automated LP entry — TradeBoba style one-click LP
   */
  async agentLPEnter(params: {
    poolAddress: string;
    chain: ChainId;
    amount0: string;
    amount1: string;
    slippage?: number;
  }): Promise<{
    txHash: string;
    lpTokens: string;
    valueUsd: number;
  }> {
    return this.client.post('/dex/lp-enter', params);
  }
}
