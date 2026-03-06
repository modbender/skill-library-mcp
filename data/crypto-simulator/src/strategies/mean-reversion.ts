import { CoinId, PricePoint, StrategyExecutionResult } from '../types';
import { buyAll, createState, createTradeBook, pushEquity, sellAll } from './common';

export interface MeanReversionParams {
  period?: number;
  deviation_pct?: number;
}

function computeSma(values: number[], period: number): Array<number | null> {
  const out: Array<number | null> = new Array(values.length).fill(null);
  if (period <= 0 || values.length < period) {
    return out;
  }

  let sum = 0;
  for (let i = 0; i < values.length; i += 1) {
    sum += values[i];
    if (i >= period) {
      sum -= values[i - period];
    }
    if (i >= period - 1) {
      out[i] = sum / period;
    }
  }

  return out;
}

export function runMeanReversionStrategy(
  coin: CoinId,
  prices: PricePoint[],
  initialCapital: number,
  params: MeanReversionParams = {},
): StrategyExecutionResult {
  const period = Math.max(2, Math.floor(params.period ?? 20));
  const deviationPct = Math.max(0.1, params.deviation_pct ?? 5);

  const state = createState(initialCapital);
  const tradeBook = createTradeBook();
  const equityCurve: StrategyExecutionResult['equityCurve'] = [];

  const sma = computeSma(
    prices.map((point) => point.price),
    period,
  );

  for (let i = 0; i < prices.length; i += 1) {
    const point = prices[i];
    const avg = sma[i];

    if (avg !== null && avg > 0) {
      const deviation = ((point.price - avg) / avg) * 100;
      if (deviation <= -deviationPct && state.cash > 0) {
        buyAll(tradeBook, state, coin, point);
      } else if (deviation >= deviationPct && state.quantity > 0) {
        sellAll(tradeBook, state, coin, point);
      }
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
