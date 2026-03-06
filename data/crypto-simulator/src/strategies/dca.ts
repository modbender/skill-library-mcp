import { PricePoint, StrategyExecutionResult, CoinId } from '../types';
import { buyByNotional, createState, createTradeBook, pushEquity } from './common';

export interface DcaParams {
  interval?: 'daily' | 'weekly' | 'biweekly' | 'monthly';
  amount_per_buy?: number;
}

function intervalDays(interval: DcaParams['interval']): number {
  if (interval === 'weekly') {
    return 7;
  }
  if (interval === 'biweekly') {
    return 14;
  }
  if (interval === 'monthly') {
    return 30;
  }
  return 1;
}

function estimatePurchaseCount(length: number, everyDays: number): number {
  return Math.max(1, Math.ceil(length / everyDays));
}

export function runDcaStrategy(
  coin: CoinId,
  prices: PricePoint[],
  initialCapital: number,
  params: DcaParams = {},
): StrategyExecutionResult {
  const interval = params.interval ?? 'weekly';
  const everyDays = intervalDays(interval);
  const amountPerBuy =
    params.amount_per_buy && params.amount_per_buy > 0
      ? params.amount_per_buy
      : initialCapital / estimatePurchaseCount(prices.length, everyDays);

  const state = createState(initialCapital);
  const tradeBook = createTradeBook();
  const equityCurve: StrategyExecutionResult['equityCurve'] = [];

  let nextBuyDate = prices[0] ? new Date(prices[0].date) : new Date();

  for (const point of prices) {
    const currentDate = new Date(point.date);
    if (currentDate.getTime() >= nextBuyDate.getTime()) {
      buyByNotional(tradeBook, state, coin, point, amountPerBuy);
      nextBuyDate = new Date(currentDate.getTime() + everyDays * 24 * 60 * 60 * 1000);
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
