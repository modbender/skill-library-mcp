export type StrategyName =
  | 'dca'
  | 'rsi_swing'
  | 'ma_cross'
  | 'grid'
  | 'hodl'
  | 'bollinger_bands'
  | 'macd'
  | 'mean_reversion';

export type CoinId =
  | 'bitcoin'
  | 'ethereum'
  | 'solana'
  | 'dogecoin'
  | 'cardano'
  | 'polkadot'
  | 'avalanche-2'
  | 'chainlink'
  | 'matic-network'
  | 'ripple';

export type TradeAction = 'buy' | 'sell';

export interface PricePoint {
  date: string; // YYYY-MM-DD
  price: number;
}

export interface ExecutedTrade {
  date: string;
  action: TradeAction;
  coin: CoinId;
  price: number;
  quantity: number;
  notional: number;
  realizedPnl?: number;
}

export interface EquityPoint {
  date: string;
  equity: number;
}

export interface StrategyExecutionResult {
  trades: ExecutedTrade[];
  equityCurve: EquityPoint[];
  finalCash: number;
  finalQuantity: number;
}

export interface BacktestRequest {
  strategy: StrategyName;
  coin: CoinId;
  initial_capital: number;
  start_date?: string;
  end_date?: string;
  params?: Record<string, unknown>;
}

export interface DailyReturnPoint {
  date: string;
  daily_return_pct: number;
  equity: number;
}

export interface BacktestMetrics {
  total_return_pct: number;
  max_drawdown_pct: number;
  sharpe_ratio: number;
  win_rate_pct: number;
  trade_count: number;
  daily_returns: DailyReturnPoint[];
}

export interface BacktestResult {
  strategy: StrategyName;
  coin: CoinId;
  initial_capital: number;
  start_date: string;
  end_date: string;
  final_value: number;
  metrics: BacktestMetrics;
  trades: ExecutedTrade[];
}

export interface SimulationTradeRequest {
  action: TradeAction;
  coin: CoinId;
  amount?: number; // JPY notionals
  quantity?: number;
}

export interface PositionState {
  coin: CoinId;
  quantity: number;
  avg_price: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
}

export interface PortfolioState {
  cash: number;
  positions: PositionState[];
  total_value: number;
}

export interface SimulationTradeResult {
  trade: {
    id: number;
    action: TradeAction;
    coin: CoinId;
    price: number;
    quantity: number;
    notional: number;
    created_at: string;
  };
  portfolio: PortfolioState;
}

export interface CoinPriceRow {
  coin: CoinId;
  date: string;
  price: number;
}

export const SUPPORTED_COINS: CoinId[] = [
  'bitcoin',
  'ethereum',
  'solana',
  'dogecoin',
  'cardano',
  'polkadot',
  'avalanche-2',
  'chainlink',
  'matic-network',
  'ripple',
];

export const STRATEGIES: StrategyName[] = [
  'dca',
  'rsi_swing',
  'ma_cross',
  'grid',
  'hodl',
  'bollinger_bands',
  'macd',
  'mean_reversion',
];
