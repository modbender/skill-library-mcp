/**
 * PRISM OS SDK
 * Unified interface to api.prismapi.ai (218 endpoints, v4.0.0)
 *
 * Every method maps 1:1 to a real endpoint.
 * No fabricated routes.
 */

import { PrismClient } from './core/client';

// Modules
import { ResolutionModule }                          from './modules/resolution';
import { CryptoModule }                              from './modules/crypto';
import { DeFiModule, OnchainModule }                 from './modules/defi-onchain';
import { StocksModule, ETFModule, ForexModule, CommoditiesModule } from './modules/tradfi';
import { MacroModule, HistoricalModule, NewsModule, CalendarModule } from './modules/macro-history-news';
import {
  TechnicalsModule, SignalsModule, RiskModule,
  OrderBookModule, TradesModule, SocialModule, AnalysisModule,
} from './modules/signals-risk-social';
import { PredictionsModule, SportsModule, OddsModule } from './modules/predictions-sports-odds';
import { DeveloperModule, AgentModule }              from './modules/developer-agent';

export interface PrismConfig {
  apiKey:   string;
  baseUrl?: string;
  timeout?: number;
}

export class PrismOS {
  /** Canonical identity resolution — the core of PRISM */
  readonly resolve:     ResolutionModule;

  /** Crypto prices, trending, market data, NVT valuation */
  readonly crypto:      CryptoModule;

  /** DeFi protocols, TVL, yields, stablecoins, bridges, wallets, DEX, gas */
  readonly defi:        DeFiModule;

  /** Onchain holder data, supply, whale movements, exchange flows */
  readonly onchain:     OnchainModule;

  /** Stocks: quotes, fundamentals, financials, earnings, insider/institutional, ratings, DCF */
  readonly stocks:      StocksModule;

  /** ETFs: popular, holdings, sector weights */
  readonly etfs:        ETFModule;

  /** Forex: live quotes, tradeable forms */
  readonly forex:       ForexModule;

  /** Commodities: live prices, tradeable forms */
  readonly commodities: CommoditiesModule;

  /** Macro economics: FRED-backed — Fed rate, inflation, GDP, treasury yields, M2 */
  readonly macro:       MacroModule;

  /** Historical OHLCV, volume, metrics, returns, volatility — cross-asset */
  readonly historical:  HistoricalModule;

  /** News: crypto and stock news with sentiment */
  readonly news:        NewsModule;

  /** Earnings calendar, economic events calendar */
  readonly calendar:    CalendarModule;

  /** Technical analysis: RSI, MACD, MAs, trend, support/resistance — cross-asset */
  readonly technicals:  TechnicalsModule;

  /** Market signals: momentum, volume spikes, breakouts, divergence */
  readonly signals:     SignalsModule;

  /** Risk metrics: volatility, VaR, Sharpe, portfolio risk */
  readonly risk:        RiskModule;

  /** Order book: depth, spread, imbalance */
  readonly orderbook:   OrderBookModule;

  /** Recent and large trades */
  readonly trades:      TradesModule;

  /** Social sentiment, mentions, trending score, GitHub activity */
  readonly social:      SocialModule;

  /** Asset intelligence: fork/bridge/copycat/rebrand/derivation detection */
  readonly analysis:    AnalysisModule;

  /** Prediction markets: Polymarket, Kalshi, Manifold */
  readonly predictions: PredictionsModule;

  /** Sports events, live scores, event details */
  readonly sports:      SportsModule;

  /** Odds comparison, arbitrage finder, odds history */
  readonly odds:        OddsModule;

  /** API key management, usage stats, health checks */
  readonly developer:   DeveloperModule;

  /** Agent-optimised context injection, endpoint discovery, schemas */
  readonly agent:       AgentModule;

  constructor(config: PrismConfig) {
    const client = new PrismClient({
      apiKey:  config.apiKey,
      baseUrl: config.baseUrl ?? 'https://api.prismapi.ai',
      timeout: config.timeout ?? 10_000,
    });

    this.resolve     = new ResolutionModule(client);
    this.crypto      = new CryptoModule(client);
    this.defi        = new DeFiModule(client);
    this.onchain     = new OnchainModule(client);
    this.stocks      = new StocksModule(client);
    this.etfs        = new ETFModule(client);
    this.forex       = new ForexModule(client);
    this.commodities = new CommoditiesModule(client);
    this.macro       = new MacroModule(client);
    this.historical  = new HistoricalModule(client);
    this.news        = new NewsModule(client);
    this.calendar    = new CalendarModule(client);
    this.technicals  = new TechnicalsModule(client);
    this.signals     = new SignalsModule(client);
    this.risk        = new RiskModule(client);
    this.orderbook   = new OrderBookModule(client);
    this.trades      = new TradesModule(client);
    this.social      = new SocialModule(client);
    this.analysis    = new AnalysisModule(client);
    this.predictions = new PredictionsModule(client);
    this.sports      = new SportsModule(client);
    this.odds        = new OddsModule(client);
    this.developer   = new DeveloperModule(client);
    this.agent       = new AgentModule(client);
  }
}

export default PrismOS;

// Re-export all types
export * from './types';

// Re-export modules for direct use
export { ResolutionModule, CryptoModule, DeFiModule, OnchainModule };
export { StocksModule, ETFModule, ForexModule, CommoditiesModule };
export { MacroModule, HistoricalModule, NewsModule, CalendarModule };
export { TechnicalsModule, SignalsModule, RiskModule, OrderBookModule, TradesModule };
export { SocialModule, AnalysisModule };
export { PredictionsModule, SportsModule, OddsModule };
export { DeveloperModule, AgentModule };
