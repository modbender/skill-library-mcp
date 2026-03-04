/**
 * Signals & Technicals + Risk + Orderbook + Social + Analysis
 *
 * Technicals (cross-asset: stocks, crypto, forex, commodities):
 *   GET /technicals/{symbol}
 *   GET /technicals/{symbol}/indicators
 *   GET /technicals/{symbol}/support-resistance
 *   GET /technicals/{symbol}/trend
 *   POST /technicals/batch
 *   GET /forex/technicals/{pair}
 *   GET /commodities/technicals/{symbol}
 *   GET /benchmarks/compare
 *   GET /market/correlations
 *
 * Signals:
 *   GET /signals/momentum
 *   GET /signals/volume-spike
 *   GET /signals/breakout
 *   GET /signals/divergence
 *   GET /signals/summary
 *
 * Risk:
 *   GET /risk/{symbol}/metrics
 *   GET /risk/{symbol}/var
 *   POST /risk/portfolio
 *
 * Order Book & Trades:
 *   GET /orderbook/{symbol}
 *   GET /orderbook/{symbol}/depth
 *   GET /orderbook/{symbol}/spread
 *   GET /orderbook/{symbol}/imbalance
 *   GET /trades/{symbol}/recent
 *   GET /trades/{symbol}/large
 *
 * Social (crypto-focused):
 *   GET /social/{symbol}/sentiment
 *   GET /social/{symbol}/mentions
 *   GET /social/{symbol}/trending-score
 *   GET /social/{symbol}/github
 *   GET /social/trending
 *
 * Asset Analysis (relationship intelligence):
 *   GET /analyze/{symbol}
 *   GET /analyze/derivation/{symbol}
 *   GET /analyze/bridge/{symbol}
 *   GET /analyze/rebrand/{symbol}
 *   GET /analyze/fork/{symbol}
 *   GET /analyze/copycat/{symbol}
 *   GET /analyze/batch
 */

import { PrismClient } from '../core/client';
import type {
  TechnicalAnalysis, SupportResistance, Signal, RiskMetrics, OrderBook, Trade,
  SocialSentiment, GithubActivity, CorrelationMatrix, AssetAnalysis, PortfolioPosition, PortfolioRisk,
} from '../types';

export class TechnicalsModule {
  constructor(private c: PrismClient) {}

  /**
   * Full technical analysis for any symbol (crypto, stock, forex, commodity).
   * Returns trend, RSI, MACD, MAs, volume signal, and a plain-language summary.
   */
  async analyze(symbol: string, timeframe = '1d'): Promise<TechnicalAnalysis> {
    return this.c.get(`/technicals/${encodeURIComponent(symbol)}`, {
      params: { timeframe },
      cacheTtl: 60,
    });
  }

  /**
   * Specific indicators for a symbol.
   * indicators: comma-separated e.g. 'RSI,MACD,EMA20'
   */
  async getIndicators(
    symbol: string,
    opts?: { indicators?: string; timeframe?: string; period?: number }
  ): Promise<Record<string, unknown>> {
    return this.c.get(`/technicals/${encodeURIComponent(symbol)}/indicators`, {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 60,
    });
  }

  /** Key support and resistance price levels */
  async getSupportResistance(symbol: string, timeframe = '1d'): Promise<SupportResistance> {
    return this.c.get(`/technicals/${encodeURIComponent(symbol)}/support-resistance`, {
      params: { timeframe },
      cacheTtl: 300,
    });
  }

  /** Trend direction and strength */
  async getTrend(symbol: string, timeframe = '1d'): Promise<{
    symbol: string;
    trend: 'bullish' | 'bearish' | 'neutral';
    strength?: number;
    [k: string]: unknown;
  }> {
    return this.c.get(`/technicals/${encodeURIComponent(symbol)}/trend`, {
      params: { timeframe },
      cacheTtl: 60,
    });
  }

  /** Batch technical analysis for multiple symbols */
  async batch(symbols: string[], timeframe = '1d', indicators?: string[]): Promise<TechnicalAnalysis[]> {
    return this.c.post('/technicals/batch', {
      symbols,
      timeframe,
      indicators,
    });
  }

  /** Technical analysis for a forex pair (EUR/USD, GBP/JPY…) */
  async analyzeFX(pair: string, timeframe = '1d'): Promise<TechnicalAnalysis> {
    return this.c.get(`/forex/technicals/${encodeURIComponent(pair)}`, {
      params: { timeframe },
      cacheTtl: 60,
    });
  }

  /** Technical analysis for a commodity (GOLD, OIL, NATGAS…) */
  async analyzeCommodity(symbol: string, timeframe = '1d'): Promise<TechnicalAnalysis> {
    return this.c.get(`/commodities/technicals/${encodeURIComponent(symbol)}`, {
      params: { timeframe },
      cacheTtl: 60,
    });
  }

  /** Compare an asset's performance vs a benchmark (SPY, BTC, etc.) */
  async compareVsBenchmark(asset: string, benchmark = 'SPY', days = 30): Promise<unknown> {
    return this.c.get('/benchmarks/compare', {
      params: { asset, benchmark, days },
      cacheTtl: 3600,
    });
  }

  /**
   * Cross-asset correlation matrix.
   * Pass any mix of stocks, crypto, ETFs — PRISM normalises the data.
   */
  async getCorrelations(assets?: string[], days = 30): Promise<CorrelationMatrix> {
    return this.c.get('/market/correlations', {
      params: { assets: assets?.join(','), days },
      cacheTtl: 3600,
    });
  }
}

export class SignalsModule {
  constructor(private c: PrismClient) {}

  /**
   * Momentum signals — RSI oversold/overbought across a universe.
   * Defaults work across all PRISM-tracked assets.
   */
  async getMomentum(opts?: {
    symbols?: string;          // comma-separated, or omit for all
    rsi_oversold?: number;     // default 30
    rsi_overbought?: number;   // default 70
  }): Promise<Signal[]> {
    return this.c.get('/signals/momentum', {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 300,
    });
  }

  /** Volume spike signals — unusual volume surge vs average */
  async getVolumeSpikes(opts?: {
    symbols?: string;
    spike_threshold?: number;  // default 2.0 = 2× avg volume
    lookback_periods?: number;
  }): Promise<Signal[]> {
    return this.c.get('/signals/volume-spike', {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 300,
    });
  }

  /** Price breakout signals above resistance or below support */
  async getBreakouts(opts?: {
    symbols?: string;
    lookback_periods?: number;
    breakout_threshold?: number;
  }): Promise<Signal[]> {
    return this.c.get('/signals/breakout', {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 300,
    });
  }

  /** Divergence signals (price vs indicator divergence) */
  async getDivergence(opts?: {
    symbols?: string;
    lookback_periods?: number;
  }): Promise<Signal[]> {
    return this.c.get('/signals/divergence', {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 300,
    });
  }

  /**
   * Unified signal summary for a symbol or universe.
   * Aggregates all signal types — great for a one-liner agent scan.
   */
  async getSummary(symbols?: string): Promise<Record<string, Signal[]>> {
    return this.c.get('/signals/summary', {
      params: { symbols },
      cacheTtl: 300,
    });
  }
}

export class RiskModule {
  constructor(private c: PrismClient) {}

  /**
   * Risk metrics for a single asset.
   * Returns volatility, Sharpe ratio, max drawdown, beta.
   * Works for crypto and stocks.
   */
  async getMetrics(
    symbol: string,
    opts?: { asset_type?: string; period?: number }
  ): Promise<RiskMetrics> {
    return this.c.get(`/risk/${encodeURIComponent(symbol)}/metrics`, {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 3600,
    });
  }

  /**
   * Value at Risk (VaR) for a position.
   * confidence: 0.95 = 95% VaR (default)
   * period: lookback in days
   */
  async getVaR(
    symbol: string,
    opts?: {
      asset_type?: string;
      confidence?: number;
      period?: number;
      position_size?: number;
    }
  ): Promise<{ symbol: string; var: number; confidence?: number; [k: string]: unknown }> {
    return this.c.get(`/risk/${encodeURIComponent(symbol)}/var`, {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 3600,
    });
  }

  /**
   * Portfolio-level risk analysis.
   * Pass a list of positions with weights — PRISM calculates aggregate risk.
   * Supports mixed portfolios: stocks + crypto + ETFs together.
   */
  async analyzePortfolio(
    positions: PortfolioPosition[],
    period_days = 30
  ): Promise<PortfolioRisk> {
    return this.c.post('/risk/portfolio', { positions, period_days });
  }
}

export class OrderBookModule {
  constructor(private c: PrismClient) {}

  /**
   * Aggregated order book (consolidated across exchanges).
   * levels: number of price levels to return (default 10)
   */
  async get(symbol: string, opts?: { levels?: number; exchanges?: string }): Promise<OrderBook> {
    return this.c.get(`/orderbook/${encodeURIComponent(symbol)}`, {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 5,
    });
  }

  /** Full depth data */
  async getDepth(symbol: string, opts?: { levels?: number; exchange?: string }): Promise<OrderBook> {
    return this.c.get(`/orderbook/${encodeURIComponent(symbol)}/depth`, {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 5,
    });
  }

  /** Bid-ask spread */
  async getSpread(symbol: string): Promise<{ symbol: string; spread: number; spread_pct?: number; [k: string]: unknown }> {
    return this.c.get(`/orderbook/${encodeURIComponent(symbol)}/spread`, { cacheTtl: 5 });
  }

  /**
   * Order book imbalance — ratio of bid vs ask pressure.
   * Positive = more bids (bullish pressure). Negative = more asks (selling pressure).
   */
  async getImbalance(symbol: string, depth = 10): Promise<{
    symbol: string; imbalance: number; bid_volume?: number; ask_volume?: number; [k: string]: unknown;
  }> {
    return this.c.get(`/orderbook/${encodeURIComponent(symbol)}/imbalance`, {
      params: { depth },
      cacheTtl: 5,
    });
  }
}

export class TradesModule {
  constructor(private c: PrismClient) {}

  /** Recent trades for a symbol */
  async getRecent(symbol: string, opts?: { limit?: number; exchange?: string }): Promise<Trade[]> {
    return this.c.get(`/trades/${encodeURIComponent(symbol)}/recent`, {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 5,
    });
  }

  /**
   * Large trades / block trades — institutional-size prints.
   * min_value: USD threshold (e.g. 100000 for $100k+ trades)
   */
  async getLarge(symbol: string, opts?: { min_value?: number; limit?: number }): Promise<Trade[]> {
    return this.c.get(`/trades/${encodeURIComponent(symbol)}/large`, {
      params: opts as Record<string, number | undefined>,
      cacheTtl: 30,
    });
  }
}

export class SocialModule {
  constructor(private c: PrismClient) {}

  /** Social sentiment score for a crypto asset */
  async getSentiment(symbol: string): Promise<SocialSentiment> {
    return this.c.get(`/social/${encodeURIComponent(symbol)}/sentiment`, { cacheTtl: 300 });
  }

  /** Social mention count and trending posts */
  async getMentions(symbol: string): Promise<{ symbol: string; total?: number; change_24h?: number; [k: string]: unknown }> {
    return this.c.get(`/social/${encodeURIComponent(symbol)}/mentions`, { cacheTtl: 300 });
  }

  /** Trending score (composite of social velocity) */
  async getTrendingScore(symbol: string): Promise<{ symbol: string; score: number; rank?: number; [k: string]: unknown }> {
    return this.c.get(`/social/${encodeURIComponent(symbol)}/trending-score`, { cacheTtl: 300 });
  }

  /** GitHub development activity (commits, contributors, stars) */
  async getGithub(symbol: string): Promise<GithubActivity> {
    return this.c.get(`/social/${encodeURIComponent(symbol)}/github`, { cacheTtl: 3600 });
  }

  /** Trending tokens by social velocity */
  async getTrending(limit = 20): Promise<Array<{ symbol: string; score?: number; [k: string]: unknown }>> {
    return this.c.get('/social/trending', { params: { limit }, cacheTtl: 300 });
  }
}

export class AnalysisModule {
  constructor(private c: PrismClient) {}

  /**
   * Full asset analysis — detects if an asset is a bridge, fork, copycat, rebrand, or derivation.
   * Essential for token due diligence agents.
   */
  async analyze(
    symbol: string,
    opts?: {
      asset_type?: string;
      chain?: string;
      contract_address?: string;
      market_cap?: number;
      deployer_address?: string;
    }
  ): Promise<AssetAnalysis> {
    return this.c.get(`/analyze/${encodeURIComponent(symbol)}`, {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 3600,
    });
  }

  /** Detect if a token is a derivation of another (wrapped, synthetic, etc.) */
  async checkDerivation(symbol: string): Promise<AssetAnalysis> {
    return this.c.get(`/analyze/derivation/${encodeURIComponent(symbol)}`, { cacheTtl: 3600 });
  }

  /** Detect if a token is a bridge asset (cross-chain bridged version) */
  async checkBridge(symbol: string, opts?: { chain?: string; contract_address?: string }): Promise<AssetAnalysis> {
    return this.c.get(`/analyze/bridge/${encodeURIComponent(symbol)}`, {
      params: opts,
      cacheTtl: 3600,
    });
  }

  /** Detect if a token has been rebranded from another */
  async checkRebrand(symbol: string): Promise<AssetAnalysis> {
    return this.c.get(`/analyze/rebrand/${encodeURIComponent(symbol)}`, { cacheTtl: 3600 });
  }

  /** Detect if a token is a fork of another protocol */
  async checkFork(symbol: string): Promise<AssetAnalysis> {
    return this.c.get(`/analyze/fork/${encodeURIComponent(symbol)}`, { cacheTtl: 3600 });
  }

  /** Detect if a token is a copycat / scam clone */
  async checkCopycat(
    symbol: string,
    opts?: { chain?: string; contract_address?: string; market_cap?: number; deployer_address?: string }
  ): Promise<AssetAnalysis> {
    return this.c.get(`/analyze/copycat/${encodeURIComponent(symbol)}`, {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 3600,
    });
  }

  /** Batch analysis for multiple symbols */
  async batchAnalyze(symbols: string[], asset_type?: string): Promise<AssetAnalysis[]> {
    return this.c.get('/analyze/batch', {
      params: { symbols: symbols.join(','), asset_type },
      cacheTtl: 3600,
    });
  }
}
