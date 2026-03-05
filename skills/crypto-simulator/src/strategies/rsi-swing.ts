import { CoinId, PricePoint, StrategyExecutionResult } from '../types';
import { buyAll, createState, createTradeBook, pushEquity, sellAll } from './common';

export interface RsiSwingParams {
  rsi_period?: number;
  buy_threshold?: number;
  sell_threshold?: number;
}

function computeRsi(values: number[], period: number): Array<number | null> {
  const result: Array<number | null> = new Array(values.length).fill(null);
  if (period <= 0 || values.length <= period) {
    return result;
  }

  let gains = 0;
  let losses = 0;

  for (let i = 1; i <= period; i += 1) {
    const change = values[i] - values[i - 1];
    if (change >= 0) {
      gains += change;
    } else {
      losses += Math.abs(change);
    }
  }

  let avgGain = gains / period;
  let avgLoss = losses / period;

  if (avgLoss === 0) {
    result[period] = 100;
  } else {
    const rs = avgGain / avgLoss;
    result[period] = 100 - 100 / (1 + rs);
  }

  for (let i = period + 1; i < values.length; i += 1) {
    const change = values[i] - values[i - 1];
    const gain = Math.max(change, 0);
    const loss = Math.max(-change, 0);

    avgGain = (avgGain * (period - 1) + gain) / period;
    avgLoss = (avgLoss * (period - 1) + loss) / period;

    if (avgLoss === 0) {
      result[i] = 100;
    } else {
      const rs = avgGain / avgLoss;
      result[i] = 100 - 100 / (1 + rs);
    }
  }

  return result;
}

export function runRsiSwingStrategy(
  coin: CoinId,
  prices: PricePoint[],
  initialCapital: number,
  params: RsiSwingParams = {},
): StrategyExecutionResult {
  const period = Math.max(2, Math.floor(params.rsi_period ?? 14));
  const buyThreshold = params.buy_threshold ?? 30;
  const sellThreshold = params.sell_threshold ?? 70;

  const state = createState(initialCapital);
  const tradeBook = createTradeBook();
  const equityCurve: StrategyExecutionResult['equityCurve'] = [];

  const rsiSeries = computeRsi(
    prices.map((point) => point.price),
    period,
  );

  for (let i = 0; i < prices.length; i += 1) {
    const point = prices[i];
    const rsi = rsiSeries[i];

    if (rsi !== null) {
      if (rsi <= buyThreshold && state.cash > 0) {
        buyAll(tradeBook, state, coin, point);
      } else if (rsi >= sellThreshold && state.quantity > 0) {
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
