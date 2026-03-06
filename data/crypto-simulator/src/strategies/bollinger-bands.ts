import { CoinId, PricePoint, StrategyExecutionResult } from '../types';
import { buyAll, createState, createTradeBook, pushEquity, sellAll } from './common';

export interface BollingerBandsParams {
  period?: number;
  std_dev?: number;
}

function computeBollingerBands(
  values: number[],
  period: number,
  stdDevMultiplier: number,
): Array<{ upper: number | null; lower: number | null }> {
  const out: Array<{ upper: number | null; lower: number | null }> = new Array(values.length)
    .fill(null)
    .map(() => ({ upper: null, lower: null }));

  if (period <= 1 || values.length < period) {
    return out;
  }

  let sum = 0;
  let sumSquares = 0;

  for (let i = 0; i < values.length; i += 1) {
    const value = values[i];
    sum += value;
    sumSquares += value * value;

    if (i >= period) {
      const removed = values[i - period];
      sum -= removed;
      sumSquares -= removed * removed;
    }

    if (i >= period - 1) {
      const mean = sum / period;
      const variance = Math.max(sumSquares / period - mean * mean, 0);
      const stdDev = Math.sqrt(variance);

      out[i] = {
        upper: mean + stdDev * stdDevMultiplier,
        lower: mean - stdDev * stdDevMultiplier,
      };
    }
  }

  return out;
}

export function runBollingerBandsStrategy(
  coin: CoinId,
  prices: PricePoint[],
  initialCapital: number,
  params: BollingerBandsParams = {},
): StrategyExecutionResult {
  const period = Math.max(2, Math.floor(params.period ?? 20));
  const stdDev = Math.max(0.1, params.std_dev ?? 2);

  const state = createState(initialCapital);
  const tradeBook = createTradeBook();
  const equityCurve: StrategyExecutionResult['equityCurve'] = [];

  const bands = computeBollingerBands(
    prices.map((point) => point.price),
    period,
    stdDev,
  );

  for (let i = 0; i < prices.length; i += 1) {
    const point = prices[i];
    const band = bands[i];

    if (band.lower !== null && point.price <= band.lower && state.cash > 0) {
      buyAll(tradeBook, state, coin, point);
    } else if (band.upper !== null && point.price >= band.upper && state.quantity > 0) {
      sellAll(tradeBook, state, coin, point);
    }

    pushEquity(equityCurve, point, state);
  }

  return {
    trades: tradeBook.trades,
    equityCurve,
    finalCash: state.cash,
    finalQuantity: state.quantity,
  };
}
