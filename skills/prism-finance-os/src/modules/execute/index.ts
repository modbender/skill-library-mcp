/**
 * PRISM OS — Module 10: Agent Execution Primitives
 * Higher-order composable actions for autonomous agents
 * This is where See → Think → ACT
 */

import { PrismHttpClient } from '../../core/client';
import { CanonicalResolver } from '../../core/canonical';
import { RiskModule } from '../risk';
import { DexModule } from '../dex';
import { OrderParams, OrderResult, BatchOperation, ChainId, VenueId } from '../../types/canonical';

export class ExecuteModule {
  constructor(
    private client: PrismHttpClient,
    private resolver: CanonicalResolver,
    private risk: RiskModule,
    private dex: DexModule
  ) {}

  // ─────────────────────────────────────────────
  // ORDER MANAGEMENT
  // ─────────────────────────────────────────────

  async marketBuy(
    query: string,
    amount: string,
    chain: ChainId,
    venue: VenueId
  ): Promise<OrderResult> {
    const id = await this.resolver.resolve(query);

    // Auto risk check
    const risk = await this.risk.getTokenScore(id);
    if (risk.overallScore > 75) {
      throw new Error(
        `Risk check failed for ${query}: score ${risk.overallScore}/100. Flags: ${risk.flags.join(', ')}`
      );
    }

    return this.client.post('/execute/market-buy', { id, amount, chain, venue });
  }

  async marketSell(
    query: string,
    amount: string,
    chain: ChainId,
    venue: VenueId
  ): Promise<OrderResult> {
    const id = await this.resolver.resolve(query);
    return this.client.post('/execute/market-sell', { id, amount, chain, venue });
  }

  async limitOrder(params: OrderParams): Promise<{ orderId: string; status: 'pending' }> {
    const id = await this.resolver.resolve(params.prismId);
    return this.client.post('/execute/limit', { ...params, prismId: id });
  }

  async stopLoss(
    query: string,
    triggerPrice: number,
    amount: string,
    chain: ChainId,
    venue: VenueId
  ): Promise<{ orderId: string; triggerPrice: number }> {
    const id = await this.resolver.resolve(query);
    return this.client.post('/execute/stop-loss', { id, triggerPrice, amount, chain, venue });
  }

  async takeProfit(
    query: string,
    triggerPrice: number,
    amount: string,
    chain: ChainId,
    venue: VenueId
  ): Promise<{ orderId: string; triggerPrice: number }> {
    const id = await this.resolver.resolve(query);
    return this.client.post('/execute/take-profit', { id, triggerPrice, amount, chain, venue });
  }

  /** Time-weighted average price — breaks large orders to minimize impact */
  async twap(params: {
    query: string;
    side: 'buy' | 'sell';
    totalAmount: string;
    durationMinutes: number;
    intervals: number;
    chain: ChainId;
    venue: VenueId;
  }): Promise<{ twapId: string; estimatedFillTime: string; sliceSize: string }> {
    const id = await this.resolver.resolve(params.query);
    return this.client.post('/execute/twap', { ...params, prismId: id });
  }

  /** Dollar-cost averaging — recurring buy schedule */
  async dca(params: {
    query: string;
    amount: string;
    frequencyHours: number;
    totalOccurrences: number;
    chain: ChainId;
    venue: VenueId;
  }): Promise<{ dcaId: string; nextExecution: string; schedule: string[] }> {
    const id = await this.resolver.resolve(params.query);
    return this.client.post('/execute/dca', { ...params, prismId: id });
  }

  // ─────────────────────────────────────────────
  // STRATEGY EXECUTION
  // ─────────────────────────────────────────────

  /**
   * Cross-venue arbitrage — detect and execute
   * Checks: price delta > fees + gas before executing
   */
  async arbitrage(
    query: string,
    fromVenue: VenueId,
    toVenue: VenueId,
    amount: string
  ): Promise<{
    profitable: boolean;
    expectedProfit: number;
    fees: number;
    netProfit: number;
    txHashes?: string[];
  }> {
    const id = await this.resolver.resolve(query);
    return this.client.post('/execute/arbitrage', { id, fromVenue, toVenue, amount });
  }

  /**
   * Portfolio rebalance — move allocations to targets
   * e.g. rebalance to { ETH: 0.4, SOL: 0.3, USDC: 0.3 }
   */
  async rebalance(
    walletAddress: string,
    targetAllocations: Record<string, number>,  // prismId → pct (0-1)
    options?: { slippage?: number; maxGas?: number; venue?: VenueId }
  ): Promise<{
    tradesRequired: Array<{ from: string; to: string; amount: string }>;
    estimatedFees: number;
    preview?: OrderResult[];
  }> {
    // Resolve all target asset IDs
    const resolvedTargets: Record<string, number> = {};
    await Promise.all(
      Object.entries(targetAllocations).map(async ([query, pct]) => {
        const id = await this.resolver.resolve(query);
        resolvedTargets[id] = pct;
      })
    );

    return this.client.post('/execute/rebalance', {
      wallet: walletAddress,
      targets: resolvedTargets,
      ...options,
    });
  }

  /**
   * Yield migration — move position from lower to higher yield
   */
  async yieldMigrate(
    fromProtocol: string,
    toProtocol: string,
    query: string,
    amount?: string
  ): Promise<{
    steps: Array<{ action: string; protocol: string; txHash?: string }>;
    expectedYieldDelta: number;
    totalGasCost: number;
  }> {
    const id = await this.resolver.resolve(query);
    return this.client.post('/execute/yield-migrate', { fromProtocol, toProtocol, id, amount });
  }

  // ─────────────────────────────────────────────
  // BATCH & CONDITIONAL
  // ─────────────────────────────────────────────

  /**
   * Atomic batch execution — all or nothing
   * Dependencies are respected, operations run in DAG order
   *
   * Example:
   * batch([
   *   { id: 'swap1', module: 'dex', method: 'executeSwap', params: {...} },
   *   { id: 'lp1', module: 'dex', method: 'agentLPEnter', params: {...}, dependsOn: ['swap1'] }
   * ])
   */
  async batch(operations: BatchOperation[]): Promise<Array<{
    id: string;
    status: 'success' | 'failed' | 'skipped';
    result?: unknown;
    error?: string;
  }>> {
    // Topological sort by dependencies
    const sorted = this.topologicalSort(operations);
    return this.client.post('/execute/batch', { operations: sorted });
  }

  /**
   * Conditional execution — if X then Y
   *
   * Example:
   * conditional(
   *   { type: 'price_below', asset: 'ETH', threshold: 3000 },
   *   { module: 'execute', method: 'marketBuy', params: { query: 'ETH', amount: '1000' } }
   * )
   */
  async conditional(
    condition: {
      type: 'price_above' | 'price_below' | 'volume_spike' | 'time' | 'prediction_odds';
      asset?: string;
      threshold?: number;
      timestamp?: number;
      marketId?: string;
    },
    action: BatchOperation
  ): Promise<{ conditionId: string; status: 'watching'; expiresAt?: string }> {
    return this.client.post('/execute/conditional', { condition, action });
  }

  // ─────────────────────────────────────────────
  // EXPANSION
  // ─────────────────────────────────────────────

  /**
   * [Expansion] Multi-agent coordination — orchestrate a fleet
   * Virtual Agent Commerce Protocol style
   */
  async multiAgentCoord(
    agents: string[],
    task: {
      type: 'split_order' | 'consensus_trade' | 'liquidity_provision' | 'arb_hunt';
      params: Record<string, unknown>;
    }
  ): Promise<{
    coordinationId: string;
    agentAssignments: Record<string, string>;
    expectedCompletion: string;
  }> {
    return this.client.post('/execute/multi-agent', { agents, task });
  }

  /**
   * [Expansion] x402 payment integration for agent fee-for-service
   * Bankr-style: agent pays for services via HTTP 402 + micropayments
   */
  async integrateX402(paymentParams: {
    service: string;
    amount: string;
    currency: string;
    walletAddress: string;
    chain: ChainId;
  }): Promise<{ paymentId: string; status: 'paid' | 'pending'; txHash?: string }> {
    return this.client.post('/execute/x402-pay', paymentParams);
  }

  /**
   * [Expansion] Agent treasury management
   * Juno/Bankr-style: manage an agent's own capital autonomously
   */
  async agentTreasuryManage(
    walletAddress: string,
    strategy: 'conservative' | 'balanced' | 'aggressive'
  ): Promise<{
    currentAllocations: Record<string, number>;
    recommendedChanges: Array<{ action: string; asset: string; amount: string }>;
    projectedYield: number;
  }> {
    return this.client.post('/execute/treasury', { wallet: walletAddress, strategy });
  }

  // ─────────────────────────────────────────────
  // Private
  // ─────────────────────────────────────────────

  private topologicalSort(operations: BatchOperation[]): BatchOperation[] {
    const sorted: BatchOperation[] = [];
    const visited = new Set<string>();
    const visiting = new Set<string>();

    const opMap = new Map(operations.map((op) => [op.id, op]));

    function visit(op: BatchOperation): void {
      if (visiting.has(op.id)) throw new Error(`Circular dependency in batch: ${op.id}`);
      if (visited.has(op.id)) return;

      visiting.add(op.id);
      for (const depId of op.dependsOn ?? []) {
        const dep = opMap.get(depId);
        if (dep) visit(dep);
      }
      visiting.delete(op.id);
      visited.add(op.id);
      sorted.push(op);
    }

    for (const op of operations) visit(op);
    return sorted;
  }
}
