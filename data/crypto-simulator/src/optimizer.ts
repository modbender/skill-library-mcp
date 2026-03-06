import { runBacktest } from './backtest';
import {
  listOptimizationResults,
  OptimizationResultQuery,
  saveOptimizationResult,
} from './db';
import { getPriceHistory } from './prices';
import { BacktestResult, CoinId, PricePoint, STRATEGIES, StrategyName, SUPPORTED_COINS } from './types';

const DEFAULT_TOP = 10;

export interface OptimizationRanking {
  coin: CoinId;
  strategy: StrategyName;
  initial_capital: number;
  start_date: string;
  end_date: string;
  params: Record<string, unknown>;
  final_value: number;
  total_return_pct: number;
  max_drawdown_pct: number;
  sharpe_ratio: number;
  win_rate_pct: number;
  trade_count: number;
  score: number;
  created_at?: string;
  id?: number;
}

export interface OptimizeCoinRequest {
  coin: CoinId;
  initial_capital: number;
  start_date?: string;
  end_date?: string;
  top?: number;
  persist?: boolean;
  refresh_prices?: boolean;
  strategies?: StrategyName[];
  prices?: PricePoint[];
}

export interface OptimizeCoinResult {
  coin: CoinId;
  initial_capital: number;
  start_date: string;
  end_date: string;
  evaluated_count: number;
  best: OptimizationRanking;
  rankings: OptimizationRanking[];
}

export interface OptimizeAllRequest {
  initial_capital: number;
  start_date?: string;
  end_date?: string;
  top?: number;
  persist?: boolean;
  refresh_prices?: boolean;
  strategies?: StrategyName[];
  coins?: CoinId[];
}

export interface OptimizeAllResult {
  initial_capital: number;
  evaluated_count: number;
  coin_count: number;
  coins: OptimizeCoinResult[];
  overall_rankings: OptimizationRanking[];
}

function validateCapital(initialCapital: number): void {
  if (!Number.isFinite(initialCapital) || initialCapital <= 0) {
    throw new Error('initial_capital must be > 0');
  }
}

function resolveStrategies(strategies?: StrategyName[]): StrategyName[] {
  if (!strategies || strategies.length === 0) {
    return [...STRATEGIES];
  }

  const uniq = [...new Set(strategies)];
  for (const strategy of uniq) {
    if (!STRATEGIES.includes(strategy)) {
      throw new Error(`Unsupported strategy: ${strategy}`);
    }
  }
  return uniq;
}

function resolveCoins(coins?: CoinId[]): CoinId[] {
  if (!coins || coins.length === 0) {
    return [...SUPPORTED_COINS];
  }

  const uniq = [...new Set(coins)];
  for (const coin of uniq) {
    if (!SUPPORTED_COINS.includes(coin)) {
      throw new Error(`Unsupported coin: ${coin}`);
    }
  }
  return uniq;
}

function rankingComparator(a: OptimizationRanking, b: OptimizationRanking): number {
  if (b.score !== a.score) {
    return b.score - a.score;
  }
  if (b.total_return_pct !== a.total_return_pct) {
    return b.total_return_pct - a.total_return_pct;
  }
  if (b.sharpe_ratio !== a.sharpe_ratio) {
    return b.sharpe_ratio - a.sharpe_ratio;
  }
  return b.final_value - a.final_value;
}

function computeScore(result: BacktestResult): number {
  return (
    result.metrics.total_return_pct +
    result.metrics.sharpe_ratio * 10 +
    result.metrics.win_rate_pct * 0.05 -
    result.metrics.max_drawdown_pct * 0.5
  );
}

function toRanking(
  coin: CoinId,
  strategy: StrategyName,
  initialCapital: number,
  params: Record<string, unknown>,
  result: BacktestResult,
): OptimizationRanking {
  return {
    coin,
    strategy,
    initial_capital: initialCapital,
    start_date: result.start_date,
    end_date: result.end_date,
    params,
    final_value: result.final_value,
    total_return_pct: result.metrics.total_return_pct,
    max_drawdown_pct: result.metrics.max_drawdown_pct,
    sharpe_ratio: result.metrics.sharpe_ratio,
    win_rate_pct: result.metrics.win_rate_pct,
    trade_count: result.metrics.trade_count,
    score: computeScore(result),
  };
}

function topLimit(top: number | undefined): number {
  if (top === undefined) {
    return DEFAULT_TOP;
  }
  return Math.max(1, Math.floor(top));
}

export function buildParameterGrid(strategy: StrategyName): Record<string, unknown>[] {
  if (strategy === 'rsi_swing') {
    const params: Record<string, unknown>[] = [];
    const periods = [7, 10, 14, 18, 21];
    const buyThresholds = [20, 25, 30, 35];
    const sellThresholds = [65, 70, 75, 80];

    for (const rsiPeriod of periods) {
      for (const buyThreshold of buyThresholds) {
        for (const sellThreshold of sellThresholds) {
          if (buyThreshold >= sellThreshold) {
            continue;
          }
          params.push({
            rsi_period: rsiPeriod,
            buy_threshold: buyThreshold,
            sell_threshold: sellThreshold,
          });
        }
      }
    }

    return params;
  }

  if (strategy === 'ma_cross') {
    const params: Record<string, unknown>[] = [];
    const shortPeriods = [20, 40, 60, 80, 100];
    const longPeriods = [100, 150, 200, 250, 300];

    for (const shortPeriod of shortPeriods) {
      for (const longPeriod of longPeriods) {
        if (shortPeriod >= longPeriod) {
          continue;
        }
        params.push({
          short_period: shortPeriod,
          long_period: longPeriod,
        });
      }
    }
    return params;
  }

  if (strategy === 'grid') {
    const params: Record<string, unknown>[] = [];
    const widths = [1, 2, 3, 5, 7, 10];
    const counts = [5, 10, 15, 20, 25, 30];

    for (const width of widths) {
      for (const count of counts) {
        params.push({
          grid_width_pct: width,
          grid_count: count,
        });
      }
    }

    return params;
  }

  if (strategy === 'dca') {
    return [
      { interval: 'daily' },
      { interval: 'weekly' },
      { interval: 'biweekly' },
      { interval: 'monthly' },
    ];
  }

  if (strategy === 'bollinger_bands') {
    const params: Record<string, unknown>[] = [];
    const periods = [14, 20, 30];
    const stdDevs = [1.5, 2, 2.5];

    for (const period of periods) {
      for (const stdDev of stdDevs) {
        params.push({
          period,
          std_dev: stdDev,
        });
      }
    }

    return params;
  }

  if (strategy === 'macd') {
    const params: Record<string, unknown>[] = [];
    const fastPeriods = [8, 12, 16];
    const slowPeriods = [21, 26, 35];
    const signalPeriods = [6, 9, 12];

    for (const fastPeriod of fastPeriods) {
      for (const slowPeriod of slowPeriods) {
        if (fastPeriod >= slowPeriod) {
          continue;
        }
        for (const signalPeriod of signalPeriods) {
          params.push({
            fast_period: fastPeriod,
            slow_period: slowPeriod,
            signal_period: signalPeriod,
          });
        }
      }
    }

    return params;
  }

  if (strategy === 'mean_reversion') {
    const params: Record<string, unknown>[] = [];
    const periods = [10, 20, 30];
    const deviations = [3, 5, 7, 10];

    for (const period of periods) {
      for (const deviation of deviations) {
        params.push({
          period,
          deviation_pct: deviation,
        });
      }
    }

    return params;
  }

  return [{}];
}

async function evaluateCoin(request: OptimizeCoinRequest): Promise<{
  rankings: OptimizationRanking[];
  start_date: string;
  end_date: string;
}> {
  validateCapital(request.initial_capital);
  const strategies = resolveStrategies(request.strategies);

  const prices =
    request.prices ??
    (await getPriceHistory({
      coin: request.coin,
      startDate: request.start_date,
      endDate: request.end_date,
      refresh: request.refresh_prices,
    }));

  if (prices.length < 2) {
    throw new Error('Not enough price data to run optimization');
  }

  const rankings: OptimizationRanking[] = [];

  for (const strategy of strategies) {
    const parameterGrid = buildParameterGrid(strategy);

    for (const params of parameterGrid) {
      const backtest = await runBacktest(
        {
          strategy,
          coin: request.coin,
          initial_capital: request.initial_capital,
          params,
        },
        {
          prices,
          persist: false,
        },
      );

      const ranking = toRanking(request.coin, strategy, request.initial_capital, params, backtest);
      rankings.push(ranking);

      if (request.persist !== false) {
        saveOptimizationResult({
          coin: ranking.coin,
          strategy: ranking.strategy,
          initial_capital: ranking.initial_capital,
          start_date: ranking.start_date,
          end_date: ranking.end_date,
          params_json: JSON.stringify(ranking.params),
          final_value: ranking.final_value,
          total_return_pct: ranking.total_return_pct,
          max_drawdown_pct: ranking.max_drawdown_pct,
          sharpe_ratio: ranking.sharpe_ratio,
          win_rate_pct: ranking.win_rate_pct,
          trade_count: ranking.trade_count,
          score: ranking.score,
        });
      }
    }
  }

  rankings.sort(rankingComparator);

  return {
    rankings,
    start_date: prices[0].date,
    end_date: prices[prices.length - 1].date,
  };
}

export async function optimizeCoin(request: OptimizeCoinRequest): Promise<OptimizeCoinResult> {
  const evaluation = await evaluateCoin(request);
  if (evaluation.rankings.length === 0) {
    throw new Error('No optimization result generated');
  }

  const top = topLimit(request.top);

  return {
    coin: request.coin,
    initial_capital: request.initial_capital,
    start_date: evaluation.start_date,
    end_date: evaluation.end_date,
    evaluated_count: evaluation.rankings.length,
    best: evaluation.rankings[0],
    rankings: evaluation.rankings.slice(0, top),
  };
}

export async function optimizeAllCoins(request: OptimizeAllRequest): Promise<OptimizeAllResult> {
  validateCapital(request.initial_capital);

  const coins = resolveCoins(request.coins);
  const strategies = resolveStrategies(request.strategies);
  const top = topLimit(request.top);

  const coinResults: OptimizeCoinResult[] = [];
  const overallRankings: OptimizationRanking[] = [];

  for (const coin of coins) {
    const evaluation = await evaluateCoin({
      coin,
      initial_capital: request.initial_capital,
      start_date: request.start_date,
      end_date: request.end_date,
      persist: request.persist,
      refresh_prices: request.refresh_prices,
      strategies,
    });

    if (evaluation.rankings.length === 0) {
      continue;
    }

    coinResults.push({
      coin,
      initial_capital: request.initial_capital,
      start_date: evaluation.start_date,
      end_date: evaluation.end_date,
      evaluated_count: evaluation.rankings.length,
      best: evaluation.rankings[0],
      rankings: evaluation.rankings.slice(0, top),
    });

    overallRankings.push(...evaluation.rankings);
  }

  overallRankings.sort(rankingComparator);

  return {
    initial_capital: request.initial_capital,
    evaluated_count: overallRankings.length,
    coin_count: coinResults.length,
    coins: coinResults,
    overall_rankings: overallRankings.slice(0, top),
  };
}

export function getOptimizationRankings(query: OptimizationResultQuery = {}): OptimizationRanking[] {
  const rows = listOptimizationResults(query);
  return rows.map((row) => {
    let params: Record<string, unknown> = {};
    try {
      const parsed = JSON.parse(row.params_json) as unknown;
      if (parsed && typeof parsed === 'object') {
        params = parsed as Record<string, unknown>;
      }
    } catch (_error) {
      params = {};
    }

    return {
      id: row.id,
      created_at: row.created_at,
      coin: row.coin,
      strategy: row.strategy,
      initial_capital: row.initial_capital,
      start_date: row.start_date,
      end_date: row.end_date,
      params,
      final_value: row.final_value,
      total_return_pct: row.total_return_pct,
      max_drawdown_pct: row.max_drawdown_pct,
      sharpe_ratio: row.sharpe_ratio,
      win_rate_pct: row.win_rate_pct,
      trade_count: row.trade_count,
      score: row.score,
    };
  });
}
