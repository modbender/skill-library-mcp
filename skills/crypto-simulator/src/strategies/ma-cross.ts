import { CoinId, PricePoint, StrategyExecutionResult } from '../types';
import { buyAll, createState, createTradeBook, pushEquity, sellAll } from './common';

export interface MaCrossParams {
  short_period?: number;
  long_period?: number;
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

export function runMaCrossStrategy(
  coin: CoinId,
  prices: PricePoint[],
  initialCapital: number,
  params: MaCrossParams = {},
): StrategyExecutionResult {
  const shortPeriod = Math.max(2, Math.floor(params.short_period ?? 50));
  const longPeriod = Math.max(shortPeriod + 1, Math.floor(params.long_period ?? 200));

  const state = createState(initialCapital);
  const tradeBook = createTradeBook();
  const equityCurve: StrategyExecutionResult['equityCurve'] = [];

  const values = prices.map((p) => p.price);
  const shortSma = computeSma(values, shortPeriod);
  const longSma = computeSma(values, longPeriod);

  for (let i = 0; i < prices.length; i += 1) {
    if (i > 0) {
      const prevShort = shortSma[i - 1];
      const prevLong = longSma[i - 1];
      const currShort = shortSma[i];
      const currLong = longSma[i];

      if (
        prevShort !== null &&
        prevLong !== null &&
        currShort !== null &&
        currLong !== null
      ) {
        if (prevShort <= prevLong && currShort > currLong && state.cash > 0) {
          buyAll(tradeBook, state, coin, prices[i]);
        } else if (prevShort >= prevLong && currShort < currLong && state.quantity > 0) {
          sellAll(tradeBook, state, coin, prices[i]);
        }
      }
    }

    pushEquity(equityCurve, prices[i], state);
  }

  return {
    trades: tradeBook.trades,
    equityCurve,
    finalCash: state.cash,
    finalQuantity: state.quantity,
  };
}
