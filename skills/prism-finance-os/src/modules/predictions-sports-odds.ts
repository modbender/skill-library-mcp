/**
 * Predictions + Sports + Odds
 *
 * Prediction Markets:
 *   GET /predictions/markets
 *   GET /predictions/markets/{market_id}
 *   GET /predictions/markets/{market_id}/odds
 *   GET /predictions/markets/{market_id}/orderbook
 *   GET /predictions/markets/{market_id}/price
 *   GET /predictions/markets/{market_id}/history
 *   GET /predictions/markets/{market_id}/candlesticks
 *   GET /predictions/markets/{market_id}/linked
 *   GET /predictions/trade-history
 *   GET /predictions/resolve
 *   GET /predictions/search
 *   GET /predictions/categories
 *   GET /predictions/events
 *   GET /predictions/trending
 *   GET /predictions/arbitrage
 *
 * Sports:
 *   GET /sports/list
 *   GET /sports/{sport}/events
 *   GET /sports/events/{event_id}
 *   GET /sports/events/{event_id}/odds
 *   GET /sports/resolve
 *   GET /sports/search
 *   GET /sports/sportsbooks
 *
 * Odds:
 *   GET /odds/arbitrage
 *   GET /odds/arbitrage/{event_id}
 *   GET /odds/compare/{event_id}
 *   GET /odds/history/{market_id}
 *   GET /odds/best
 *   GET /odds/platforms
 */

import { PrismClient } from '../core/client';
import type { PredictionMarket, ArbitrageOpportunity, SportsEvent } from '../types';

export class PredictionsModule {
  constructor(private c: PrismClient) {}

  // ─── MARKET DISCOVERY ──────────────────────────────────

  /** List prediction markets with filters */
  async getMarkets(opts?: {
    category?: string;
    status?: 'open' | 'closed' | 'resolved';
    source?: string;           // 'polymarket' | 'kalshi' | 'manifold'
    sort?: string;
    limit?: number;
    cursor?: string;
    min_volume?: number;
    tags?: string;
  }): Promise<PredictionMarket[]> {
    return this.c.get('/predictions/markets', {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 60,
    });
  }

  /** Get a specific market by ID */
  async getMarket(marketId: string): Promise<PredictionMarket> {
    return this.c.get(`/predictions/markets/${encodeURIComponent(marketId)}`, { cacheTtl: 30 });
  }

  /** Search prediction markets by text */
  async searchMarkets(query: string, opts?: { category?: string; source?: string; limit?: number }): Promise<PredictionMarket[]> {
    return this.c.get('/predictions/search', {
      params: { q: query, ...opts } as Record<string, string | number | undefined>,
      cacheTtl: 60,
    });
  }

  /** Natural language resolution: "Will BTC hit 100k in 2025?" → matching market */
  async resolve(query: string): Promise<{ market?: PredictionMarket; confidence?: number; [k: string]: unknown }> {
    return this.c.get('/predictions/resolve', { params: { q: query }, cacheTtl: 60 });
  }

  /** Trending prediction markets */
  async getTrending(limit = 20): Promise<PredictionMarket[]> {
    return this.c.get('/predictions/trending', { params: { limit }, cacheTtl: 300 });
  }

  /** Browse market categories */
  async getCategories(): Promise<Array<{ category: string; count?: number; [k: string]: unknown }>> {
    return this.c.get('/predictions/categories', { cacheTtl: 3600 });
  }

  /** Browse prediction events (parent groupings of markets) */
  async getEvents(opts?: {
    category?: string;
    subcategory?: string;
    status?: string;
    limit?: number;
    cursor?: string;
    expand?: boolean;
  }): Promise<unknown[]> {
    return this.c.get('/predictions/events', {
      params: opts as Record<string, string | number | boolean | undefined>,
      cacheTtl: 300,
    });
  }

  // ─── MARKET DATA ───────────────────────────────────────

  /** Current odds for a market (yes/no prices, multi-outcome) */
  async getOdds(marketId: string, include_history = false): Promise<unknown> {
    return this.c.get(`/predictions/markets/${encodeURIComponent(marketId)}/odds`, {
      params: { include_history },
      cacheTtl: 30,
    });
  }

  /** Order book for a prediction market */
  async getOrderBook(marketId: string, opts?: { source?: string; outcome_id?: string }): Promise<unknown> {
    return this.c.get(`/predictions/markets/${encodeURIComponent(marketId)}/orderbook`, {
      params: opts,
      cacheTtl: 10,
    });
  }

  /** Current price for a market (or at a specific timestamp) */
  async getPrice(marketId: string, at_time?: string): Promise<{ price: number; [k: string]: unknown }> {
    return this.c.get(`/predictions/markets/${encodeURIComponent(marketId)}/price`, {
      params: { at_time },
      cacheTtl: 10,
    });
  }

  /** Price history for a market */
  async getPriceHistory(marketId: string, opts?: {
    start_time?: string;
    end_time?: string;
    interval?: string;
    limit?: number;
  }): Promise<unknown[]> {
    return this.c.get(`/predictions/markets/${encodeURIComponent(marketId)}/history`, {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 300,
    });
  }

  /** Candlestick OHLCV data for a prediction market */
  async getCandlesticks(marketId: string, opts?: {
    start_time?: string;
    end_time?: string;
    interval?: string;
    outcome?: string;
    outcome_id?: string;
    limit?: number;
  }): Promise<unknown[]> {
    return this.c.get(`/predictions/markets/${encodeURIComponent(marketId)}/candlesticks`, {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 300,
    });
  }

  /** Markets linked to this one (correlated or opposite) */
  async getLinkedMarkets(marketId: string): Promise<PredictionMarket[]> {
    return this.c.get(`/predictions/markets/${encodeURIComponent(marketId)}/linked`, { cacheTtl: 300 });
  }

  /** Trade history for a market */
  async getTradeHistory(marketId: string, opts?: {
    source?: string;
    outcome_id?: string;
    start_time?: string;
    end_time?: string;
    limit?: number;
    cursor?: string;
  }): Promise<unknown[]> {
    return this.c.get('/predictions/trade-history', {
      params: { market_id: marketId, ...opts } as Record<string, string | number | undefined>,
      cacheTtl: 60,
    });
  }

  // ─── ARBITRAGE ─────────────────────────────────────────

  /**
   * Prediction market arbitrage opportunities.
   * Finds markets where YES + NO < 100% (or equivalent), yielding risk-free profit.
   */
  async getArbitrage(opts?: {
    category?: string;
    min_profit?: number;
    limit?: number;
  }): Promise<ArbitrageOpportunity[]> {
    return this.c.get('/predictions/arbitrage', {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 60,
    });
  }
}

export class SportsModule {
  constructor(private c: PrismClient) {}

  /** List all supported sports */
  async listSports(opts?: { active_only?: boolean; region?: string }): Promise<Array<{
    sport: string; name?: string; active?: boolean; [k: string]: unknown;
  }>> {
    return this.c.get('/sports/list', {
      params: opts as Record<string, string | boolean | undefined>,
      cacheTtl: 3600,
    });
  }

  /** Upcoming/live events for a sport */
  async getEvents(sport: string, opts?: {
    status?: string;
    days_ahead?: number;
    limit?: number;
  }): Promise<SportsEvent[]> {
    return this.c.get(`/sports/${encodeURIComponent(sport)}/events`, {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 300,
    });
  }

  /** Event details */
  async getEvent(eventId: string): Promise<SportsEvent> {
    return this.c.get(`/sports/events/${encodeURIComponent(eventId)}`, { cacheTtl: 300 });
  }

  /** Odds for a sports event across bookmakers */
  async getEventOdds(eventId: string, opts?: {
    market?: string;
    bookmakers?: string;
    region?: string;
  }): Promise<unknown> {
    return this.c.get(`/sports/events/${encodeURIComponent(eventId)}/odds`, {
      params: opts,
      cacheTtl: 60,
    });
  }

  /** Natural language sports resolution: "Lakers vs Warriors tonight" → event */
  async resolve(query: string): Promise<{ event?: SportsEvent; [k: string]: unknown }> {
    return this.c.get('/sports/resolve', { params: { q: query }, cacheTtl: 60 });
  }

  /** Search sports events */
  async search(query: string, opts?: { sport?: string; status?: string; limit?: number }): Promise<SportsEvent[]> {
    return this.c.get('/sports/search', {
      params: { q: query, ...opts } as Record<string, string | number | undefined>,
      cacheTtl: 60,
    });
  }

  /** List sportsbooks */
  async getSportsbooks(region?: string): Promise<Array<{ name: string; [k: string]: unknown }>> {
    return this.c.get('/sports/sportsbooks', { params: { region }, cacheTtl: 3600 });
  }
}

export class OddsModule {
  constructor(private c: PrismClient) {}

  /**
   * Cross-platform arbitrage across sportsbooks.
   * Finds events where odds across different books sum to < 100%.
   */
  async findArbitrage(opts?: {
    category?: string;
    min_profit_pct?: number;
    max_stake?: number;
    include_expired?: boolean;
    limit?: number;
  }): Promise<ArbitrageOpportunity[]> {
    return this.c.get('/odds/arbitrage', {
      params: opts as Record<string, string | number | boolean | undefined>,
      cacheTtl: 60,
    });
  }

  /** Arbitrage opportunities for a specific event */
  async getEventArbitrage(eventId: string): Promise<ArbitrageOpportunity> {
    return this.c.get(`/odds/arbitrage/${encodeURIComponent(eventId)}`, { cacheTtl: 60 });
  }

  /** Side-by-side odds comparison across all bookmakers for an event */
  async compareOdds(eventId: string, opts?: { market?: string; format?: string }): Promise<unknown> {
    return this.c.get(`/odds/compare/${encodeURIComponent(eventId)}`, {
      params: opts,
      cacheTtl: 60,
    });
  }

  /** Historical odds movement for a market */
  async getOddsHistory(marketId: string, opts?: {
    outcome?: string;
    platform?: string;
    interval?: string;
    days?: number;
  }): Promise<unknown[]> {
    return this.c.get(`/odds/history/${encodeURIComponent(marketId)}`, {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 300,
    });
  }

  /** Best available odds across all platforms */
  async getBestOdds(opts?: {
    category?: string;
    sport?: string;
    sort?: string;
    limit?: number;
  }): Promise<unknown[]> {
    return this.c.get('/odds/best', {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 60,
    });
  }

  /** All supported odds platforms */
  async getPlatforms(category?: string): Promise<Array<{ name: string; type?: string; [k: string]: unknown }>> {
    return this.c.get('/odds/platforms', { params: { category }, cacheTtl: 3600 });
  }
}
