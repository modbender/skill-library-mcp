/**
 * PRISM OS — Types
 * Derived from api.prismapi.ai OpenAPI spec v4.0.0 (218 endpoints)
 * Every field name matches the actual API response shape.
 */

// ─── ASSET IDENTITY ────────────────────────────────────

export type AssetType = 'crypto' | 'stock' | 'etf' | 'forex' | 'commodity' | 'index' | 'prediction';

export interface ResolvedAsset {
  symbol:           string;
  name?:            string;
  asset_type?:      AssetType;
  family_id?:       string;
  canonical_id?:    string;
  chain?:           string;
  contract_address?:string;
  venues?:          Venue[];
  price?:           number;
  confidence?:      number;
  [k: string]:      unknown;
}

export interface Venue {
  name:       string;
  type?:      string;   // 'cex' | 'dex' | 'prediction' | 'sports'
  symbol?:    string;
  url?:       string;
  tradeable?: boolean;
  [k: string]:unknown;
}

export interface Family {
  family_id:   string;
  name:        string;
  symbol:      string;
  category?:   string;
  instances?:  FamilyInstance[];
  venues?:     Venue[];
  price?:      number;
  [k: string]: unknown;
}

export interface FamilyInstance {
  symbol:            string;
  chain?:            string;
  contract_address?: string;
  exchange?:         string;
  active?:           boolean;
  [k: string]:       unknown;
}

// ─── ASSET ANALYSIS ────────────────────────────────────

export interface AssetAnalysis {
  symbol:       string;
  asset_type?:  string;
  is_bridge?:   boolean;
  is_rebrand?:  boolean;
  is_fork?:     boolean;
  is_copycat?:  boolean;
  is_derivation?:boolean;
  original?:    string;
  risk_flags?:  string[];
  relationship?:string;
  confidence?:  number;
  [k: string]:  unknown;
}

// ─── CRYPTO PRICES ─────────────────────────────────────

export interface ConsensusPrice {
  symbol:      string;
  price:       number;
  price_usd?:  number;
  sources?:    PriceSource[];
  confidence?: number;
  timestamp?:  number;
  change_24h?: number;
  volume_24h?: number;
  market_cap?: number;
  [k: string]: unknown;
}

export interface PriceSource {
  source:     string;
  price:      number;
  weight?:    number;
  timestamp?: number;
}

export interface PriceHistoryPoint {
  timestamp: number;
  price:     number;
  volume?:   number;
  [k: string]:unknown;
}

// ─── MARKET ────────────────────────────────────────────

export interface GlobalMarket {
  total_market_cap?:    number;
  total_volume_24h?:    number;
  btc_dominance?:       number;
  eth_dominance?:       number;
  market_cap_change_24h?:number;
  active_cryptocurrencies?:number;
  [k: string]:          unknown;
}

export interface FearGreedIndex {
  value:           number;
  classification:  string;  // 'Extreme Fear'|'Fear'|'Neutral'|'Greed'|'Extreme Greed'
  timestamp?:      number;
  [k: string]:     unknown;
}

export interface MarketMover {
  symbol:          string;
  name?:           string;
  price?:          number;
  change_24h?:     number;
  change_pct_24h?: number;
  volume_24h?:     number;
  [k: string]:     unknown;
}

// ─── DEX ───────────────────────────────────────────────

export interface FundingRate {
  symbol:      string;
  dex:         string;
  rate:        number;
  annualized?: number;
  next_funding?:string;
  [k: string]: unknown;
}

export interface OpenInterest {
  symbol:     string;
  dex:        string;
  oi_usd:     number;
  oi_tokens?: number;
  change_24h?:number;
  [k: string]:unknown;
}

export interface DexPair {
  pair?:      string;
  base?:      string;
  quote?:     string;
  dex?:       string;
  chain?:     string;
  address?:   string;
  price?:     number;
  volume_24h?:number;
  liquidity?: number;
  [k: string]:unknown;
}

export interface PoolOHLCV {
  timestamp: number;
  open:      number;
  high:      number;
  low:       number;
  close:     number;
  volume?:   number;
}

// ─── ONCHAIN ───────────────────────────────────────────

export interface HolderEntry {
  address:     string;
  balance:     number;
  pct_supply?: number;
  label?:      string;
  [k: string]: unknown;
}

export interface HolderDistribution {
  total_holders:number;
  top_10_pct?:  number;
  top_50_pct?:  number;
  gini?:        number;
  distribution?:Record<string, number>;
  [k: string]:  unknown;
}

export interface WhaleMovement {
  tx_hash?:   string;
  from?:      string;
  to?:        string;
  value_usd:  number;
  token?:     string;
  chain?:     string;
  timestamp?: number;
  type?:      'buy'|'sell'|'transfer';
  [k: string]:unknown;
}

export interface ExchangeFlow {
  inflow:    number;
  outflow:   number;
  net_flow:  number;
  period?:   string;
  exchange?: string;
  [k: string]:unknown;
}

export interface OnchainSupply {
  total_supply?:        number;
  circulating_supply?:  number;
  burned?:              number;
  locked?:              number;
  [k: string]:          unknown;
}

// ─── DEFI ──────────────────────────────────────────────

export interface Protocol {
  name:        string;
  slug?:       string;
  symbol?:     string;
  category?:   string;
  chain?:      string;
  tvl?:        number;
  change_1d?:  number;
  change_7d?:  number;
  url?:        string;
  [k: string]: unknown;
}

export interface YieldPool {
  pool?:        string;
  protocol?:    string;
  chain?:       string;
  symbol?:      string;
  tvl_usd?:     number;
  apy?:         number;
  apy_base?:    number;
  apy_reward?:  number;
  stablecoin?:  boolean;
  risk_score?:  number;
  [k: string]:  unknown;
}

export interface Stablecoin {
  symbol:           string;
  name?:            string;
  peg?:             number;
  circulating?:     number;
  price?:           number;
  depeg_pct?:       number;
  collateral_type?: string;
  [k: string]:      unknown;
}

export interface Bridge {
  name:       string;
  tvl?:       number;
  volume_24h?:number;
  chains?:    string[];
  [k: string]:unknown;
}

export interface WalletBalance {
  token:      string;
  symbol?:    string;
  balance:    number;
  value_usd?: number;
  contract?:  string;
  chain?:     string;
  [k: string]:unknown;
}

export interface GasPrice {
  chain:     string;
  slow?:     number;
  standard?: number;
  fast?:     number;
  unit?:     string;
  [k: string]:unknown;
}

// ─── STOCKS ────────────────────────────────────────────

export interface StockQuote {
  symbol:        string;
  price:         number;
  open?:         number;
  high?:         number;
  low?:          number;
  previous_close?:number;
  change?:       number;
  change_pct?:   number;
  volume?:       number;
  market_cap?:   number;
  pe_ratio?:     number;
  timestamp?:    number;
  [k: string]:   unknown;
}

export interface StockProfile {
  symbol:      string;
  name?:       string;
  exchange?:   string;
  sector?:     string;
  industry?:   string;
  country?:    string;
  description?:string;
  employees?:  number;
  ceo?:        string;
  website?:    string;
  [k: string]: unknown;
}

export interface StockFundamentals {
  symbol:          string;
  pe?:             number;
  forward_pe?:     number;
  pb?:             number;
  ps?:             number;
  ev_ebitda?:      number;
  eps?:            number;
  revenue?:        number;
  net_income?:     number;
  gross_margin?:   number;
  net_margin?:     number;
  roe?:            number;
  roa?:            number;
  debt_to_equity?: number;
  current_ratio?:  number;
  dividend_yield?: number;
  beta?:           number;
  [k: string]:     unknown;
}

export interface FinancialStatement {
  symbol:     string;
  statement:  'income'|'balance'|'cash_flow';
  period:     'annual'|'quarterly';
  data?:      Array<Record<string, unknown>>;
  [k: string]:unknown;
}

export interface EarningsData {
  symbol:            string;
  report_date?:      string;
  period?:           string;
  eps_estimate?:     number;
  eps_actual?:       number;
  eps_surprise?:     number;
  revenue_estimate?: number;
  revenue_actual?:   number;
  [k: string]:       unknown;
}

export interface InsiderTrade {
  name?:   string;
  title?:  string;
  type?:   'buy'|'sell'|'award';
  shares?: number;
  price?:  number;
  value?:  number;
  date?:   string;
  [k: string]:unknown;
}

export interface InstitutionalHolder {
  institution?:string;
  shares?:     number;
  value?:      number;
  pct?:        number;
  change?:     number;
  quarter?:    string;
  [k: string]: unknown;
}

export interface AnalystRating {
  firm?:            string;
  analyst?:         string;
  rating?:          string;
  price_target?:    number;
  previous_rating?: string;
  previous_target?: number;
  date?:            string;
  [k: string]:      unknown;
}

export interface ValuationRatios {
  symbol:       string;
  pe?:          number;
  forward_pe?:  number;
  peg?:         number;
  pb?:          number;
  ps?:          number;
  ev_ebitda?:   number;
  ev_revenue?:  number;
  [k: string]:  unknown;
}

export interface DCFValuation {
  symbol:          string;
  intrinsic_value?: number;
  current_price?:  number;
  upside_pct?:     number;
  growth_rate?:    number;
  discount_rate?:  number;
  terminal_growth?:number;
  [k: string]:     unknown;
}

export interface ETFHolding {
  symbol?: string;
  name?:   string;
  weight?: number;
  shares?: number;
  value?:  number;
  [k: string]:unknown;
}

export interface SectorWeight {
  sector: string;
  weight: number;
  [k: string]:unknown;
}

// ─── FOREX & COMMODITIES ───────────────────────────────

export interface ForexQuote {
  pair:            string;
  base?:           string;
  quote?:          string;
  rate:            number;
  change_24h?:     number;
  change_pct_24h?: number;
  bid?:            number;
  ask?:            number;
  [k: string]:     unknown;
}

export interface CommodityQuote {
  symbol:          string;
  name?:           string;
  price:           number;
  change_24h?:     number;
  change_pct_24h?: number;
  unit?:           string;
  [k: string]:     unknown;
}

export interface TradeableForm {
  symbol:     string;
  type?:      string;
  exchange?:  string;
  tradeable?: boolean;
  [k: string]:unknown;
}

// ─── MACRO ECONOMICS (FRED-backed) ─────────────────────

export interface MacroSeries {
  series_id:  string;
  title?:     string;
  value?:     number;
  previous?:  number;
  change?:    number;
  date?:      string;
  unit?:      string;
  frequency?: string;
  history?:   Array<{ date: string; value: number }>;
  [k: string]:unknown;
}

export interface TreasuryYields {
  date?:    string;
  '1m'?:    number;
  '3m'?:    number;
  '6m'?:    number;
  '1y'?:    number;
  '2y'?:    number;
  '5y'?:    number;
  '10y'?:   number;
  '20y'?:   number;
  '30y'?:   number;
  '2s10s'?: number;
  inverted?:boolean;
  [k: string]:unknown;
}

// ─── TECHNICALS & SIGNALS ──────────────────────────────

export interface TechnicalAnalysis {
  symbol:            string;
  timeframe?:        string;
  trend?:            'bullish'|'bearish'|'neutral';
  rsi?:              number;
  macd?:             { value: number; signal: number; histogram: number };
  moving_averages?:  Record<string, number>;
  volume_signal?:    'high'|'normal'|'low';
  summary?:          string;
  [k: string]:       unknown;
}

export interface SupportResistance {
  symbol:       string;
  supports:     Array<{ price: number; strength: number }>;
  resistances:  Array<{ price: number; strength: number }>;
  current_price?:number;
  [k: string]:  unknown;
}

export interface Signal {
  symbol:       string;
  signal_type:  'momentum'|'volume_spike'|'breakout'|'divergence';
  direction?:   'bullish'|'bearish';
  strength?:    number;
  details?:     string;
  [k: string]:  unknown;
}

export interface RiskMetrics {
  symbol:        string;
  volatility?:   number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  beta?:         number;
  var?:          number;
  [k: string]:   unknown;
}

export interface OrderBook {
  symbol:     string;
  bids:       [number, number][];
  asks:       [number, number][];
  spread?:    number;
  imbalance?: number;
  timestamp?: number;
  [k: string]:unknown;
}

export interface Trade {
  symbol:     string;
  price:      number;
  size:       number;
  side?:      'buy'|'sell';
  value_usd?: number;
  exchange?:  string;
  timestamp?: number;
  [k: string]:unknown;
}

export interface CorrelationMatrix {
  assets:       string[];
  matrix:       Record<string, Record<string, number>>;
  period_days?: number;
  [k: string]:  unknown;
}

// ─── SOCIAL ────────────────────────────────────────────

export interface SocialSentiment {
  symbol:        string;
  sentiment_score?:number;
  label?:        'positive'|'negative'|'neutral';
  bullish_pct?:  number;
  bearish_pct?:  number;
  volume?:       number;
  [k: string]:   unknown;
}

export interface GithubActivity {
  symbol:       string;
  commits_30d?: number;
  contributors?:number;
  stars?:       number;
  forks?:       number;
  last_commit?: string;
  [k: string]:  unknown;
}

// ─── PREDICTIONS & ODDS ────────────────────────────────

export interface PredictionMarket {
  market_id:  string;
  title:      string;
  category?:  string;
  source?:    string;
  status?:    'open'|'closed'|'resolved';
  yes_price?: number;
  no_price?:  number;
  volume?:    number;
  liquidity?: number;
  end_date?:  string;
  outcomes?:  PredictionOutcome[];
  [k: string]:unknown;
}

export interface PredictionOutcome {
  outcome_id?:  string;
  name:         string;
  price?:       number;
  probability?: number;
  [k: string]:  unknown;
}

export interface ArbitrageOpportunity {
  market_id?:       string;
  event_id?:        string;
  title?:           string;
  platform_a?:      string;
  platform_b?:      string;
  price_a?:         number;
  price_b?:         number;
  profit_pct?:      number;
  required_capital?:number;
  [k: string]:      unknown;
}

export interface SportsEvent {
  event_id:    string;
  sport?:      string;
  home_team?:  string;
  away_team?:  string;
  start_time?: string;
  status?:     string;
  [k: string]: unknown;
}

// ─── NEWS & CALENDAR ───────────────────────────────────

export interface NewsItem {
  title:        string;
  url?:         string;
  source?:      string;
  published_at?:string;
  sentiment?:   'positive'|'negative'|'neutral';
  symbols?:     string[];
  summary?:     string;
  [k: string]:  unknown;
}

export interface EarningsCalendarEntry {
  symbol:       string;
  company?:     string;
  report_date:  string;
  time_of_day?: 'BMO'|'AMC'|'DMH';
  eps_estimate?:number;
  [k: string]:  unknown;
}

export interface EconomicCalendarEntry {
  event:      string;
  country?:   string;
  date:       string;
  impact?:    'low'|'medium'|'high';
  actual?:    number;
  forecast?:  number;
  previous?:  number;
  [k: string]:unknown;
}

// ─── HISTORICAL ────────────────────────────────────────

export interface HistoricalPrice {
  date:    string;
  open?:   number;
  high?:   number;
  low?:    number;
  close:   number;
  volume?: number;
  [k: string]:unknown;
}

export interface HistoricalReturns {
  symbol:   string;
  periods?: Record<string, number>; // '1d'|'7d'|'30d'|'1y' → pct
  [k: string]:unknown;
}

// ─── PORTFOLIO ─────────────────────────────────────────

export interface PortfolioPosition {
  symbol:      string;
  weight:      number;   // 0–1
  asset_type?: AssetType;
}

export interface PortfolioRisk {
  total_var?:   number;
  volatility?:  number;
  sharpe?:      number;
  max_drawdown?:number;
  [k: string]:  unknown;
}

// ─── NVT (Crypto Valuation) ────────────────────────────

export interface NVTRatio {
  symbol:               string;
  nvt?:                 number;
  nvt_signal?:          number;
  network_value?:       number;
  transaction_volume?:  number;
  signal?:              'overvalued'|'fair'|'undervalued';
  [k: string]:          unknown;
}

// ─── DEVELOPER ─────────────────────────────────────────

export interface UsageStats {
  requests_today?:  number;
  requests_month?:  number;
  limit_day?:       number;
  limit_month?:     number;
  tier?:            string;
  [k: string]:      unknown;
}
