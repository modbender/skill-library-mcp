import { CoinId, PricePoint, StrategyExecutionResult } from '../types';
import { buyAll, createState, createTradeBook, pushEquity, sellAll } from './common';

export interface MacdParams {
  fast_period?: number;
  slow_period?: number;
  signal_period?: number;
}

function computeEma(values: number[], period: number): Array<number | null> {
  const out: Array<number | null> = new Array(values.length).fill(null);
  if (period <= 0 || values.length < period) {
    return out;
  }

  let seed = 0;
  for (let i = 0; i < period; i += 1) {
    seed += values[i];
  }

  const alpha = 2 / (period + 1);
  let ema = seed / period;
  out[period - 1] = ema;

  for (let i = period; i < values.length; i += 1) {
    ema = values[i] * alpha + ema * (1 - alpha);
    out[i] = ema;
  }

  return out;
}

function computeSignal(macd: Array<number | null>, period: number): Array<number | null> {
  const compactValues: number[] = [];
  const compactIndices: number[] = [];

  for (let i = 0; i < macd.length; i += 1) {
    const value = macd[i];
    if (value !== null) {
      compactValues.push(value);
      compactIndices.push(i);
    }
  }

  const compactSignal = computeEma(compactValues, period);
  const signal = new Array(macd.length).fill(null) as Array<number | null>;

  for (let i = 0; i < compactSignal.length; i += 1) {
    if (compactSignal[i] !== null) {
      signal[compactIndices[i]] = compactSignal[i];
    }
  }

  return signal;
}

export function runMacdStrategy(
  coin: CoinId,
  prices: PricePoint[],
  initialCapital: number,
  params: MacdParams = {},
): StrategyExecutionResult {
  const fastPeriod = Math.max(2, Math.floor(params.fast_period ?? 12));
  const slowPeriod = Math.max(fastPeriod + 1, Math.floor(params.slow_period ?? 26));
  const signalPeriod = Math.max(2, Math.floor(params.signal_period ?? 9));

  const state = createState(initialCapital);
  const tradeBook = createTradeBook();
  const equityCurve: StrategyExecutionResult['equityCurve'] = [];

  const values = prices.map((point) => point.price);
  const fastEma = computeEma(values, fastPeriod);
  const slowEma = computeEma(values, slowPeriod);
  const macdLine = values.map((_, i) =>
    fastEma[i] !== null && slowEma[i] !== null ? fastEma[i] - slowEma[i] : null,
  );
  const signalLine = computeSignal(macdLine, signalPeriod);

  for (let i = 0; i < prices.length; i += 1) {
    if (i > 0) {
      const prevMacd = macdLine[i - 1];
      const prevSignal = signalLine[i - 1];
      const currMacd = macdLine[i];
      const currSignal = signalLine[i];

      if (
        prevMacd !== null &&
        prevSignal !== null &&
        currMacd !== null &&
        currSignal !== null
      ) {
        if (prevMacd <= prevSignal && currMacd > currSignal && state.cash > 0) {
          buyAll(tradeBook, state, coin, prices[i]);
        } else if (prevMacd >= prevSignal && currMacd < currSignal && state.quantity > 0) {
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
