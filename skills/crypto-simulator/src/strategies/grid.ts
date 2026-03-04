import { CoinId, PricePoint, StrategyExecutionResult } from '../types';
import {
  buyByNotional,
  createState,
  createTradeBook,
  pushEquity,
  sellByQuantity,
} from './common';

export interface GridParams {
  grid_width_pct?: number;
  grid_count?: number;
}

export function runGridStrategy(
  coin: CoinId,
  prices: PricePoint[],
  initialCapital: number,
  params: GridParams = {},
): StrategyExecutionResult {
  const width = Math.max(0.001, (params.grid_width_pct ?? 2) / 100);
  const gridCount = Math.max(1, Math.floor(params.grid_count ?? 5));

  const state = createState(initialCapital);
  const tradeBook = createTradeBook();
  const equityCurve: StrategyExecutionResult['equityCurve'] = [];

  if (prices.length === 0) {
    return {
      trades: [],
      equityCurve,
      finalCash: state.cash,
      finalQuantity: state.quantity,
    };
  }

  const first = prices[0];
  buyByNotional(tradeBook, state, coin, first, initialCapital / 2);

  let lastGridPrice = first.price;
  const unitQty = state.quantity / gridCount;

  for (let i = 0; i < prices.length; i += 1) {
    const point = prices[i];

    if (i > 0 && unitQty > 0) {
      let guard = 0;
      while (point.price <= lastGridPrice * (1 - width) && guard < gridCount * 3) {
        const requiredNotional = unitQty * point.price;
        if (state.cash < requiredNotional) {
          break;
        }
        buyByNotional(tradeBook, state, coin, point, requiredNotional);
        lastGridPrice *= 1 - width;
        guard += 1;
      }

      guard = 0;
      while (point.price >= lastGridPrice * (1 + width) && guard < gridCount * 3) {
        if (state.quantity < unitQty) {
          break;
        }
        sellByQuantity(tradeBook, state, coin, point, unitQty);
        lastGridPrice *= 1 + width;
        guard += 1;
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
