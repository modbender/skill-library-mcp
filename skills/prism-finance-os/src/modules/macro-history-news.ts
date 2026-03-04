/**
 * Macro Economics + Historical Data + News + Calendar
 *
 * Macro (all FRED-backed):
 *   GET /macro/fed-rate
 *   GET /macro/inflation
 *   GET /macro/treasury-yields
 *   GET /macro/unemployment
 *   GET /macro/gdp
 *   GET /macro/m2-supply
 *   GET /macro/housing
 *   GET /macro/consumer
 *   GET /macro/market
 *   GET /macro/jobless-claims
 *   GET /macro/industrial
 *   GET /macro/summary
 *   GET /macro/series/{series_id}
 *   GET /macro/available-series
 *
 * Historical:
 *   GET /historical/{symbol}/prices
 *   GET /historical/{symbol}/volume
 *   GET /historical/{symbol}/metrics
 *   GET /historical/{symbol}/returns
 *   GET /historical/{symbol}/volatility
 *   GET /historical/compare
 *
 * News:
 *   GET /news/crypto
 *   GET /news/stocks
 *   GET /news/stocks/batch
 *
 * Calendar:
 *   GET /calendar/earnings
 *   GET /calendar/earnings/week
 *   GET /calendar/economic
 */

import { PrismClient } from '../core/client';
import type {
  MacroSeries, TreasuryYields,
  NewsItem, EarningsCalendarEntry, EconomicCalendarEntry,
  HistoricalPrice, HistoricalReturns,
} from '../types';

export class MacroModule {
  constructor(private c: PrismClient) {}

  // ─── MACRO INDICATORS ──────────────────────────────────

  /** Federal Funds Rate (current + history) */
  async getFedRate(): Promise<MacroSeries> {
    return this.c.get('/macro/fed-rate', { cacheTtl: 3600 });
  }

  /** CPI inflation (current + history) */
  async getInflation(): Promise<MacroSeries> {
    return this.c.get('/macro/inflation', { cacheTtl: 3600 });
  }

  /**
   * Full Treasury yield curve (1m through 30y).
   * Includes 2s10s spread and inversion flag — critical recession signal.
   */
  async getTreasuryYields(): Promise<TreasuryYields> {
    return this.c.get('/macro/treasury-yields', { cacheTtl: 3600 });
  }

  /** Unemployment rate (current + history) */
  async getUnemployment(): Promise<MacroSeries> {
    return this.c.get('/macro/unemployment', { cacheTtl: 3600 });
  }

  /** GDP growth rate (current + history) */
  async getGDP(): Promise<MacroSeries> {
    return this.c.get('/macro/gdp', { cacheTtl: 3600 });
  }

  /** M2 money supply */
  async getM2Supply(): Promise<MacroSeries> {
    return this.c.get('/macro/m2-supply', { cacheTtl: 3600 });
  }

  /** Housing data (starts, permits, prices) */
  async getHousing(): Promise<MacroSeries> {
    return this.c.get('/macro/housing', { cacheTtl: 3600 });
  }

  /** Consumer data (confidence, spending, retail sales) */
  async getConsumer(): Promise<MacroSeries> {
    return this.c.get('/macro/consumer', { cacheTtl: 3600 });
  }

  /** Financial market indicators (VIX, yield spreads, etc.) */
  async getMarketIndicators(): Promise<MacroSeries> {
    return this.c.get('/macro/market', { cacheTtl: 3600 });
  }

  /** Weekly jobless claims */
  async getJoblessClaims(): Promise<MacroSeries> {
    return this.c.get('/macro/jobless-claims', { cacheTtl: 3600 });
  }

  /** Industrial production index */
  async getIndustrial(): Promise<MacroSeries> {
    return this.c.get('/macro/industrial', { cacheTtl: 3600 });
  }

  /**
   * All-in-one macro dashboard snapshot.
   * Great for agent context injection — one call to understand the macro environment.
   */
  async getSummary(): Promise<{
    fed_rate?: number;
    inflation?: number;
    unemployment?: number;
    gdp_growth?: number;
    treasury_10y?: number;
    yield_curve_inverted?: boolean;
    [k: string]: unknown;
  }> {
    return this.c.get('/macro/summary', { cacheTtl: 3600 });
  }

  /**
   * Fetch any FRED series by ID.
   * Unlocks thousands of additional series: SOFR, PCE, consumer credit, etc.
   * See /macro/available-series for the full list.
   * Examples: 'SOFR', 'PCEPI', 'WALCL' (Fed balance sheet), 'T10YIE' (10y breakeven inflation)
   */
  async getSeries(seriesId: string, limit = 100): Promise<MacroSeries> {
    return this.c.get(`/macro/series/${encodeURIComponent(seriesId)}`, {
      params: { limit },
      cacheTtl: 3600,
    });
  }

  /** List all available FRED series IDs that PRISM supports */
  async getAvailableSeries(): Promise<Array<{ series_id: string; title: string; frequency?: string; [k: string]: unknown }>> {
    return this.c.get('/macro/available-series', { cacheTtl: 86400 });
  }
}

export class HistoricalModule {
  constructor(private c: PrismClient) {}

  /**
   * OHLCV price history — works for crypto, stocks, ETFs, forex, commodities.
   * This is the universal historical data endpoint.
   */
  async getPrices(
    symbol: string,
    opts?: {
      from_date?: string;   // ISO date
      to_date?: string;
      days?: number;        // Alternative to from/to
      interval?: '1d' | '1h' | '5m' | '15m';
    }
  ): Promise<HistoricalPrice[]> {
    return this.c.get(`/historical/${symbol}/prices`, {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 300,
    });
  }

  /** Volume history */
  async getVolume(symbol: string, days = 30): Promise<Array<{ date: string; volume: number; [k: string]: unknown }>> {
    return this.c.get(`/historical/${symbol}/volume`, { params: { days }, cacheTtl: 300 });
  }

  /** Multiple metrics over time (market cap, volume, price combined) */
  async getMetrics(symbol: string, days = 30): Promise<unknown[]> {
    return this.c.get(`/historical/${symbol}/metrics`, { params: { days }, cacheTtl: 300 });
  }

  /** Period returns: 1d, 7d, 30d, 1y, etc. */
  async getReturns(symbol: string, periods?: string): Promise<HistoricalReturns> {
    return this.c.get(`/historical/${symbol}/returns`, { params: { periods }, cacheTtl: 300 });
  }

  /** Historical volatility (rolling window) */
  async getVolatility(symbol: string, window = 30): Promise<{
    symbol: string; volatility: number; window: number; annualized?: number; [k: string]: unknown;
  }> {
    return this.c.get(`/historical/${symbol}/volatility`, { params: { window }, cacheTtl: 300 });
  }

  /**
   * Compare multiple assets over time.
   * Normalizes all series to 100 at start — perfect for relative performance charts.
   */
  async compare(symbols: string[], days = 30, metric = 'price'): Promise<unknown> {
    return this.c.get('/historical/compare', {
      params: { symbols: symbols.join(','), days, metric },
      cacheTtl: 300,
    });
  }
}

export class NewsModule {
  constructor(private c: PrismClient) {}

  /** Latest crypto news with sentiment tags */
  async getCryptoNews(limit = 20): Promise<NewsItem[]> {
    return this.c.get('/news/crypto', { params: { limit }, cacheTtl: 300 });
  }

  /** Stock news — pass symbol for company-specific, or leave blank for market news */
  async getStockNews(symbol?: string, limit = 20): Promise<NewsItem[]> {
    return this.c.get('/news/stocks', { params: { symbol, limit }, cacheTtl: 300 });
  }

  /** News for multiple stocks in one call */
  async getStockNewsBatch(
    symbols: string[],
    limitPerSymbol = 5
  ): Promise<Record<string, NewsItem[]>> {
    return this.c.get('/news/stocks/batch', {
      params: { symbols: symbols.join(','), limit_per_symbol: limitPerSymbol },
      cacheTtl: 300,
    });
  }
}

export class CalendarModule {
  constructor(private c: PrismClient) {}

  /**
   * Earnings calendar — all upcoming reports in a date range.
   * from_date / to_date: ISO date strings (YYYY-MM-DD)
   */
  async getEarnings(from_date?: string, to_date?: string): Promise<EarningsCalendarEntry[]> {
    return this.c.get('/calendar/earnings', { params: { from_date, to_date }, cacheTtl: 3600 });
  }

  /** Earnings reports this week — no date params needed */
  async getEarningsThisWeek(limit = 50): Promise<EarningsCalendarEntry[]> {
    return this.c.get('/calendar/earnings/week', { params: { limit }, cacheTtl: 3600 });
  }

  /**
   * Economic events calendar (FOMC, CPI, GDP, jobs reports…).
   * Includes forecast vs actual vs previous — essential for macro agents.
   */
  async getEconomic(from_date?: string, to_date?: string): Promise<EconomicCalendarEntry[]> {
    return this.c.get('/calendar/economic', { params: { from_date, to_date }, cacheTtl: 3600 });
  }
}
