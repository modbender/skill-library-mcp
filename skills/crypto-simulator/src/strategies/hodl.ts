import { CoinId, PricePoint, StrategyExecutionResult } from '../types';
import { buyAll, createState, createTradeBook, pushEquity } from './common';

export function runHodlStrategy(
  coin: CoinId,
  prices: PricePoint[],
  initialCapital: number,
): StrategyExecutionResult {
  const state = createState(initialCapital);
  const tradeBook = createTradeBook();
  const equityCurve: StrategyExecutionResult['equityCurve'] = [];

  if (prices.length > 0) {
    buyAll(tradeBook, state, coin, prices[0]);
  }

  for (const point of prices) {
    pushEquity(equityCurve, point, state);
  }

  return {
    trades: tradeBook.trades,
    equityCurve,
    finalCash: state.cash,
    finalQuantity: state.quantity,
  };
}
