import { describe, expect, it } from 'vitest';
import { buildParameterGrid, optimizeCoin } from '../src/optimizer';
import { PricePoint } from '../src/types';

function prices(values: number[]): PricePoint[] {
  return values.map((price, index) => {
    const date = new Date(Date.UTC(2025, 0, 1 + index)).toISOString().slice(0, 10);
    return { date, price };
  });
}

describe('optimizer', () => {
  it('builds parameter grids for core strategies', () => {
    expect(buildParameterGrid('rsi_swing')).toHaveLength(80);
    expect(buildParameterGrid('ma_cross')).toHaveLength(24);
    expect(buildParameterGrid('grid')).toHaveLength(36);
    expect(buildParameterGrid('dca')).toHaveLength(4);
  });

  it('optimizes selected strategies using injected prices', async () => {
    const result = await optimizeCoin({
      coin: 'bitcoin',
      initial_capital: 10000,
      strategies: ['hodl', 'dca'],
      prices: prices([100, 105, 110, 120, 115, 125, 130, 140]),
      persist: false,
      top: 3,
    });

    expect(result.evaluated_count).toBe(5);
    expect(result.rankings).toHaveLength(3);
    expect(result.best.score).toBeGreaterThanOrEqual(result.rankings[result.rankings.length - 1].score);
    expect(result.start_date).toBe('2025-01-01');
    expect(result.end_date).toBe('2025-01-08');
  });
});
