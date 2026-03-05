/**
 * TradFi Module — Stocks, ETFs, Forex, Commodities, Indexes
 *
 * Stocks:
 *   GET /stocks/{symbol}/quote
 *   GET /stocks/{symbol}/profile
 *   GET /stocks/{symbol}/profile (detail)
 *   GET /stocks/{symbol}/fundamentals
 *   GET /stocks/{symbol}/financials
 *   GET /stocks/{symbol}/earnings
 *   GET /stocks/{symbol}/dividends
 *   GET /stocks/{symbol}/splits
 *   GET /stocks/{symbol}/insiders
 *   GET /stocks/{symbol}/institutional
 *   GET /stocks/{symbol}/filings
 *   GET /stocks/{symbol}/peers
 *   GET /stocks/{symbol}/analyst-ratings
 *   GET /stocks/{symbol}/sparkline
 *   GET /stocks/gainers | losers | active | multi-day-movers
 *   POST /stocks/batch/quotes
 *   POST /stocks/batch/sparklines
 *   GET /batch/quotes
 *   GET /batch/stocks/sparklines
 *   GET /valuation/{symbol}/ratios
 *   GET /valuation/{symbol}/dcf
 *
 * ETFs:
 *   GET /etfs/popular
 *   GET /etfs/{symbol}/holdings
 *   GET /etfs/{symbol}/sector-weights
 *
 * Indexes:
 *   GET /indexes
 *   GET /indexes/sp500
 *   GET /indexes/nasdaq100
 *   GET /indexes/dow30
 *   GET /sectors
 *
 * Forex:
 *   GET /forex
 *   GET /forex/{currency}/tradeable
 *
 * Commodities:
 *   GET /commodities
 *   GET /commodities/{commodity}/tradeable
 */

import { PrismClient } from '../core/client';
import type {
  StockQuote, StockProfile, StockFundamentals, FinancialStatement,
  EarningsData, InsiderTrade, InstitutionalHolder, AnalystRating,
  ValuationRatios, DCFValuation, ETFHolding, SectorWeight,
  ForexQuote, CommodityQuote, TradeableForm,
} from '../types';

export class StocksModule {
  constructor(private c: PrismClient) {}

  // ─── QUOTES ────────────────────────────────────────────

  /** Real-time quote for a stock */
  async getQuote(symbol: string): Promise<StockQuote> {
    return this.c.get(`/stocks/${symbol.toUpperCase()}/quote`, { cacheTtl: 15 });
  }

  /** Batch quotes via POST */
  async getBatchQuotes(symbols: string[]): Promise<StockQuote[]> {
    return this.c.post('/stocks/batch/quotes', { symbols: symbols.map(s => s.toUpperCase()) });
  }

  /** Batch quotes via GET (comma-separated) */
  async getQuotes(symbols: string[]): Promise<StockQuote[]> {
    return this.c.get('/batch/quotes', {
      params: { symbols: symbols.join(',') },
      cacheTtl: 15,
    });
  }

  /** Sparkline (mini price chart, last N days) */
  async getSparkline(symbol: string, days = 30): Promise<{ prices: number[]; [k: string]: unknown }> {
    return this.c.get(`/stocks/${symbol.toUpperCase()}/sparkline`, { params: { days }, cacheTtl: 300 });
  }

  /** Batch sparklines via GET */
  async getBatchSparklines(symbols: string[]): Promise<Record<string, number[]>> {
    return this.c.get('/batch/stocks/sparklines', {
      params: { symbols: symbols.join(',') },
      cacheTtl: 300,
    });
  }

  // ─── COMPANY DATA ──────────────────────────────────────

  /** Company profile (name, sector, exchange, description) */
  async getProfile(symbol: string): Promise<StockProfile> {
    return this.c.get(`/stocks/${symbol.toUpperCase()}/profile`, { cacheTtl: 86400 });
  }

  /** Detailed profile (more fields) */
  async getProfileDetail(symbol: string): Promise<StockProfile> {
    return this.c.get(`/stocks/${symbol.toUpperCase()}/profile`, { cacheTtl: 86400 });
  }

  /** Key financial ratios and metrics */
  async getFundamentals(symbol: string): Promise<StockFundamentals> {
    return this.c.get(`/stocks/${symbol.toUpperCase()}/fundamentals`, { cacheTtl: 3600 });
  }

  /**
   * Financial statements: income, balance sheet, or cash flow.
   * statement: 'income' | 'balance' | 'cash_flow'
   * period: 'annual' | 'quarterly'
   */
  async getFinancials(
    symbol: string,
    opts?: {
      statement?: 'income' | 'balance' | 'cash_flow';
      period?: 'annual' | 'quarterly';
      limit?: number;
    }
  ): Promise<FinancialStatement> {
    return this.c.get(`/stocks/${symbol.toUpperCase()}/financials`, {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 3600,
    });
  }

  /** Peer companies (similar sector/size) */
  async getPeers(symbol: string): Promise<string[]> {
    return this.c.get(`/stocks/${symbol.toUpperCase()}/peers`, { cacheTtl: 86400 });
  }

  // ─── EARNINGS & CORPORATE ACTIONS ──────────────────────

  /** Historical earnings: EPS actuals vs estimates, surprises */
  async getEarnings(symbol: string, limit = 8): Promise<EarningsData[]> {
    return this.c.get(`/stocks/${symbol.toUpperCase()}/earnings`, { params: { limit }, cacheTtl: 3600 });
  }

  /** Dividend history */
  async getDividends(symbol: string, limit = 20): Promise<Array<{
    amount: number; ex_date: string; pay_date?: string; yield?: number; [k: string]: unknown;
  }>> {
    return this.c.get(`/stocks/${symbol.toUpperCase()}/dividends`, { params: { limit }, cacheTtl: 3600 });
  }

  /** Stock split history */
  async getSplits(symbol: string, limit = 10): Promise<Array<{
    date: string; ratio: string; from?: number; to?: number; [k: string]: unknown;
  }>> {
    return this.c.get(`/stocks/${symbol.toUpperCase()}/splits`, { params: { limit }, cacheTtl: 86400 });
  }

  /** SEC filings (10-K, 10-Q, 8-K, proxy…) */
  async getFilings(
    symbol: string,
    opts?: { filing_type?: string; limit?: number }
  ): Promise<Array<{
    type: string; date: string; url?: string; description?: string; [k: string]: unknown;
  }>> {
    return this.c.get(`/stocks/${symbol.toUpperCase()}/filings`, {
      params: opts as Record<string, string | number | undefined>,
      cacheTtl: 3600,
    });
  }

  // ─── OWNERSHIP ─────────────────────────────────────────

  /** Insider transactions (Form 4 filings) */
  async getInsiders(symbol: string, limit = 20): Promise<InsiderTrade[]> {
    return this.c.get(`/stocks/${symbol.toUpperCase()}/insiders`, { params: { limit }, cacheTtl: 3600 });
  }

  /** Institutional 13F ownership */
  async getInstitutional(symbol: string, limit = 20): Promise<InstitutionalHolder[]> {
    return this.c.get(`/stocks/${symbol.toUpperCase()}/institutional`, { params: { limit }, cacheTtl: 86400 });
  }

  /** Analyst buy/hold/sell ratings + price targets */
  async getAnalystRatings(symbol: string, limit = 20): Promise<{
    consensus?: string;
    avg_target?: number;
    ratings: AnalystRating[];
    [k: string]: unknown;
  }> {
    return this.c.get(`/stocks/${symbol.toUpperCase()}/analyst-ratings`, { params: { limit }, cacheTtl: 3600 });
  }

  // ─── VALUATION ─────────────────────────────────────────

  /**
   * Valuation multiples: P/E, P/B, EV/EBITDA, PEG, P/S.
   * Works for TradFi-style equity analysis.
   */
  async getValuationRatios(symbol: string): Promise<ValuationRatios> {
    return this.c.get(`/valuation/${symbol.toUpperCase()}/ratios`, { cacheTtl: 3600 });
  }

  /**
   * Simple DCF intrinsic value estimate.
   * Pass your own growth/discount assumptions or use PRISM defaults.
   */
  async getDCF(
    symbol: string,
    opts?: {
      growth_rate?: number;
      discount_rate?: number;
      terminal_growth?: number;
    }
  ): Promise<DCFValuation> {
    return this.c.get(`/valuation/${symbol.toUpperCase()}/dcf`, {
      params: opts as Record<string, number | undefined>,
      cacheTtl: 3600,
    });
  }

  // ─── MARKET MOVERS ─────────────────────────────────────

  /** Top gaining stocks today */
  async getGainers(limit = 20): Promise<StockQuote[]> {
    return this.c.get('/stocks/gainers', { params: { limit }, cacheTtl: 60 });
  }

  /** Top losing stocks today */
  async getLosers(limit = 20): Promise<StockQuote[]> {
    return this.c.get('/stocks/losers', { params: { limit }, cacheTtl: 60 });
  }

  /** Most active by volume */
  async getMostActive(limit = 20): Promise<StockQuote[]> {
    return this.c.get('/stocks/active', { params: { limit }, cacheTtl: 60 });
  }

  /** Multi-day movers (sustained momentum) */
  async getMultiDayMovers(opts?: { days?: number; limit?: number }): Promise<StockQuote[]> {
    return this.c.get('/stocks/multi-day-movers', { params: opts, cacheTtl: 3600 });
  }

  // ─── INDEXES ───────────────────────────────────────────

  /** All major market indexes (SPX, DJIA, NDX, VIX, etc.) */
  async getIndexes(): Promise<Array<{ symbol: string; name: string; value: number; change?: number; [k: string]: unknown }>> {
    return this.c.get('/indexes', { cacheTtl: 60 });
  }

  /** S&P 500 constituents */
  async getSP500(): Promise<Array<{ symbol: string; name: string; weight?: number; [k: string]: unknown }>> {
    return this.c.get('/indexes/sp500', { cacheTtl: 86400 });
  }

  /** NASDAQ-100 constituents */
  async getNASDAQ100(): Promise<Array<{ symbol: string; name: string; weight?: number; [k: string]: unknown }>> {
    return this.c.get('/indexes/nasdaq100', { cacheTtl: 86400 });
  }

  /** Dow Jones 30 constituents */
  async getDOW30(): Promise<Array<{ symbol: string; name: string; weight?: number; [k: string]: unknown }>> {
    return this.c.get('/indexes/dow30', { cacheTtl: 86400 });
  }

  /** Sector performance (GICS sectors) */
  async getSectors(): Promise<Array<{ sector: string; performance?: number; [k: string]: unknown }>> {
    return this.c.get('/sectors', { cacheTtl: 3600 });
  }
}

export class ETFModule {
  constructor(private c: PrismClient) {}

  /** Most popular ETFs by volume */
  async getPopular(limit = 20): Promise<Array<{ symbol: string; name?: string; [k: string]: unknown }>> {
    return this.c.get('/etfs/popular', { params: { limit }, cacheTtl: 3600 });
  }

  /** Full holdings breakdown for an ETF */
  async getHoldings(symbol: string): Promise<ETFHolding[]> {
    return this.c.get(`/etfs/${symbol.toUpperCase()}/holdings`, { cacheTtl: 86400 });
  }

  /** Sector weight allocation for an ETF */
  async getSectorWeights(symbol: string): Promise<SectorWeight[]> {
    return this.c.get(`/etfs/${symbol.toUpperCase()}/sector-weights`, { cacheTtl: 86400 });
  }
}

export class ForexModule {
  constructor(private c: PrismClient) {}

  /** All tracked forex pairs with live rates */
  async getAll(): Promise<ForexQuote[]> {
    return this.c.get('/forex', { cacheTtl: 30 });
  }

  /** Tradeable forms of a currency (spot, CFD, ETF, futures…) */
  async getTradeableForms(currency: string): Promise<TradeableForm[]> {
    return this.c.get(`/forex/${encodeURIComponent(currency.toUpperCase())}/tradeable`, { cacheTtl: 3600 });
  }
}

export class CommoditiesModule {
  constructor(private c: PrismClient) {}

  /** All tracked commodities with live prices (gold, oil, natural gas, corn…) */
  async getAll(): Promise<CommodityQuote[]> {
    return this.c.get('/commodities', { cacheTtl: 60 });
  }

  /** Tradeable forms of a commodity (futures, ETF, CFD…) */
  async getTradeableForms(commodity: string): Promise<TradeableForm[]> {
    return this.c.get(`/commodities/${encodeURIComponent(commodity.toUpperCase())}/tradeable`, { cacheTtl: 3600 });
  }
}
