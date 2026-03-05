import { describe, expect, it } from 'vitest';
import { runBacktest } from '../src/backtest';
import { PricePoint } from '../src/types';

function prices(values: number[]): PricePoint[] {
  return values.map((price, index) => {
    const date = new Date(Date.UTC(2025, 0, 1 + index)).toISOString().slice(0, 10);
    return { date, price };
  });
}

describe('runBacktest', () => {
  it('calculates hodl metrics on rising prices', async () => {
    const result = await runBacktest(
      {
        strategy: 'hodl',
        coin: 'bitcoin',
        initial_capital: 10000,
      },
      {
        prices: prices([100, 150, 200]),
        persist: false,
      },
    );

    expect(result.final_value).toBeCloseTo(20000, 6);
    expect(result.metrics.total_return_pct).toBeCloseTo(100, 6);
    expect(result.metrics.trade_count).toBe(1);
    expect(result.metrics.daily_returns).toHaveLength(3);
  });

  it('executes ma cross buy and sell signals', async () => {
    const result = await runBacktest(
      {
        strategy: 'ma_cross',
        coin: 'ethereum',
        initial_capital: 10000,
        params: {
          short_period: 2,
          long_period: 3,
        },
      },
      {
        prices: prices([10, 10, 10, 20, 30, 20, 10]),
        persist: false,
      },
    );

    expect(result.trades.some((trade) => trade.action === 'buy')).toBe(true);
    expect(result.trades.some((trade) => trade.action === 'sell')).toBe(true);
    expect(result.metrics.trade_count).toBeGreaterThanOrEqual(2);
  });

  it('executes bollinger band signals', async () => {
    const result = await runBacktest(
      {
        strategy: 'bollinger_bands',
        coin: 'cardano',
        initial_capital: 10000,
        params: {
          period: 3,
          std_dev: 1,
        },
      },
      {
        prices: prices([100, 102, 101, 80, 100, 130, 100]),
        persist: false,
      },
    );

    expect(result.trades.some((trade) => trade.action === 'buy')).toBe(true);
    expect(result.trades.some((trade) => trade.action === 'sell')).toBe(true);
  });

  it('executes macd crossover signals', async () => {
    const result = await runBacktest(
      {
        strategy: 'macd',
        coin: 'solana',
        initial_capital: 10000,
        params: {
          fast_period: 2,
          slow_period: 4,
          signal_period: 2,
        },
      },
      {
        prices: prices([10, 10, 10, 12, 14, 16, 14, 12, 10, 8, 10, 12, 14, 12, 10]),
        persist: false,
      },
    );

    expect(result.trades.some((trade) => trade.action === 'buy')).toBe(true);
    expect(result.trades.some((trade) => trade.action === 'sell')).toBe(true);
  });

  it('executes mean reversion buy and sell signals', async () => {
    const result = await runBacktest(
      {
        strategy: 'mean_reversion',
        coin: 'dogecoin',
        initial_capital: 10000,
        params: {
          period: 3,
          deviation_pct: 5,
        },
      },
      {
        prices: prices([100, 101, 99, 90, 100, 110, 100]),
        persist: false,
      },
    );

    expect(result.trades.some((trade) => trade.action === 'buy')).toBe(true);
    expect(result.trades.some((trade) => trade.action === 'sell')).toBe(true);
  });
});
