import { getPriceHistory } from './prices';
import { saveBacktestResult } from './db';
import {
  BacktestRequest,
  BacktestResult,
  DailyReturnPoint,
  ExecutedTrade,
  PricePoint,
  StrategyExecutionResult,
} from './types';
import { runDcaStrategy } from './strategies/dca';
import { runGridStrategy } from './strategies/grid';
import { runHodlStrategy } from './strategies/hodl';
import { runMaCrossStrategy } from './strategies/ma-cross';
import { runRsiSwingStrategy } from './strategies/rsi-swing';
import { runBollingerBandsStrategy } from './strategies/bollinger-bands';
import { runMacdStrategy } from './strategies/macd';
import { runMeanReversionStrategy } from './strategies/mean-reversion';

export interface RunBacktestOptions {
  prices?: PricePoint[];
  persist?: boolean;
  refreshPrices?: boolean;
}

function numberParam(
  params: Record<string, unknown> | undefined,
  key: string,
): number | undefined {
  if (!params) {
    return undefined;
  }
  const raw = params[key];
  if (typeof raw === 'number' && Number.isFinite(raw)) {
    return raw;
  }
  if (typeof raw === 'string' && raw.trim() !== '' && Number.isFinite(Number(raw))) {
    return Number(raw);
  }
  return undefined;
}

function stringParam(
  params: Record<string, unknown> | undefined,
  key: string,
): string | undefined {
  if (!params) {
    return undefined;
  }
  const raw = params[key];
  return typeof raw === 'string' ? raw : undefined;
}

function calculateMaxDrawdown(equityCurve: StrategyExecutionResult['equityCurve']): number {
  if (equityCurve.length === 0) {
    return 0;
  }

  let peak = equityCurve[0].equity;
  let maxDrawdown = 0;

  for (const point of equityCurve) {
    if (point.equity > peak) {
      peak = point.equity;
    }

    if (peak > 0) {
      const drawdown = (point.equity - peak) / peak;
      if (drawdown < maxDrawdown) {
        maxDrawdown = drawdown;
      }
    }
  }

  return Math.abs(maxDrawdown) * 100;
}

function calculateDailyReturns(equityCurve: StrategyExecutionResult['equityCurve']): DailyReturnPoint[] {
  if (equityCurve.length === 0) {
    return [];
  }

  const daily: DailyReturnPoint[] = [];
  for (let i = 0; i < equityCurve.length; i += 1) {
    if (i === 0) {
      daily.push({ date: equityCurve[i].date, daily_return_pct: 0, equity: equityCurve[i].equity });
      continue;
    }

    const prev = equityCurve[i - 1].equity;
    const current = equityCurve[i].equity;
    const ret = prev > 0 ? ((current - prev) / prev) * 100 : 0;

    daily.push({ date: equityCurve[i].date, daily_return_pct: ret, equity: current });
  }

  return daily;
}

function calculateSharpeRatio(equityCurve: StrategyExecutionResult['equityCurve']): number {
  if (equityCurve.length < 3) {
    return 0;
  }

  const returns: number[] = [];
  for (let i = 1; i < equityCurve.length; i += 1) {
    const prev = equityCurve[i - 1].equity;
    const current = equityCurve[i].equity;
    if (prev <= 0) {
      continue;
    }
    returns.push((current - prev) / prev);
  }

  if (returns.length < 2) {
    return 0;
  }

  const mean = returns.reduce((sum, value) => sum + value, 0) / returns.length;
  const variance =
    returns.reduce((sum, value) => sum + (value - mean) ** 2, 0) / (returns.length - 1);
  const stdDev = Math.sqrt(variance);

  if (stdDev === 0) {
    return 0;
  }

  return (mean / stdDev) * Math.sqrt(365);
}

function calculateWinRate(trades: ExecutedTrade[]): number {
  const closes = trades.filter((trade) => trade.action === 'sell' && trade.realizedPnl !== undefined);
  if (closes.length === 0) {
    return 0;
  }

  const wins = closes.filter((trade) => (trade.realizedPnl ?? 0) > 0).length;
  return (wins / closes.length) * 100;
}

function runStrategy(request: BacktestRequest, prices: PricePoint[]): StrategyExecutionResult {
  const { strategy, coin, initial_capital: initialCapital, params } = request;

  if (strategy === 'dca') {
    return runDcaStrategy(coin, prices, initialCapital, {
      interval:
        (stringParam(params, 'interval') as
          | 'daily'
          | 'weekly'
          | 'biweekly'
          | 'monthly'
          | undefined) ?? 'weekly',
      amount_per_buy: numberParam(params, 'amount_per_buy'),
    });
  }

  if (strategy === 'rsi_swing') {
    return runRsiSwingStrategy(coin, prices, initialCapital, {
      rsi_period: numberParam(params, 'rsi_period'),
      buy_threshold: numberParam(params, 'buy_threshold'),
      sell_threshold: numberParam(params, 'sell_threshold'),
    });
  }

  if (strategy === 'ma_cross') {
    return runMaCrossStrategy(coin, prices, initialCapital, {
      short_period: numberParam(params, 'short_period'),
      long_period: numberParam(params, 'long_period'),
    });
  }

  if (strategy === 'grid') {
    const gridWidth = numberParam(params, 'grid_width_pct') ?? numberParam(params, 'grid_pct');
    return runGridStrategy(coin, prices, initialCapital, {
      grid_width_pct: gridWidth,
      grid_count: numberParam(params, 'grid_count'),
    });
  }

  if (strategy === 'bollinger_bands') {
    return runBollingerBandsStrategy(coin, prices, initialCapital, {
      period: numberParam(params, 'period'),
      std_dev: numberParam(params, 'std_dev'),
    });
  }

  if (strategy === 'macd') {
    return runMacdStrategy(coin, prices, initialCapital, {
      fast_period: numberParam(params, 'fast_period'),
      slow_period: numberParam(params, 'slow_period'),
      signal_period: numberParam(params, 'signal_period'),
    });
  }

  if (strategy === 'mean_reversion') {
    return runMeanReversionStrategy(coin, prices, initialCapital, {
      period: numberParam(params, 'period'),
      deviation_pct: numberParam(params, 'deviation_pct'),
    });
  }

  return runHodlStrategy(coin, prices, initialCapital);
}

export async function runBacktest(
  request: BacktestRequest,
  options: RunBacktestOptions = {},
): Promise<BacktestResult> {
  if (request.initial_capital <= 0) {
    throw new Error('initial_capital must be > 0');
  }

  const prices =
    options.prices ??
    (await getPriceHistory({
      coin: request.coin,
      startDate: request.start_date,
      endDate: request.end_date,
      refresh: options.refreshPrices,
    }));

  if (prices.length < 2) {
    throw new Error('Not enough price data to run backtest');
  }

  const execution = runStrategy(request, prices);
  const finalValue = execution.equityCurve[execution.equityCurve.length - 1]?.equity ?? request.initial_capital;

  const result: BacktestResult = {
    strategy: request.strategy,
    coin: request.coin,
    initial_capital: request.initial_capital,
    start_date: prices[0].date,
    end_date: prices[prices.length - 1].date,
    final_value: finalValue,
    metrics: {
      total_return_pct: ((finalValue - request.initial_capital) / request.initial_capital) * 100,
      max_drawdown_pct: calculateMaxDrawdown(execution.equityCurve),
      sharpe_ratio: calculateSharpeRatio(execution.equityCurve),
      win_rate_pct: calculateWinRate(execution.trades),
      trade_count: execution.trades.length,
      daily_returns: calculateDailyReturns(execution.equityCurve),
    },
    trades: execution.trades,
  };

  if (options.persist !== false) {
    saveBacktestResult(
      request.strategy,
      request.coin,
      request.initial_capital,
      result.start_date,
      result.end_date,
      JSON.stringify(result),
    );
  }

  return result;
}
