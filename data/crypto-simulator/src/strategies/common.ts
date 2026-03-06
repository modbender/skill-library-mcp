import { CoinId, EquityPoint, ExecutedTrade, PricePoint, TradeAction } from '../types';

export interface TradingState {
  cash: number;
  quantity: number;
  avgEntryPrice: number;
}

export interface TradeBook {
  trades: ExecutedTrade[];
}

export function createState(initialCapital: number): TradingState {
  return {
    cash: initialCapital,
    quantity: 0,
    avgEntryPrice: 0,
  };
}

export function createTradeBook(): TradeBook {
  return { trades: [] };
}

function pushTrade(
  tradeBook: TradeBook,
  action: TradeAction,
  coin: CoinId,
  date: string,
  price: number,
  quantity: number,
  realizedPnl?: number,
): void {
  if (quantity <= 0) {
    return;
  }

  tradeBook.trades.push({
    action,
    coin,
    date,
    price,
    quantity,
    notional: quantity * price,
    ...(realizedPnl !== undefined ? { realizedPnl } : {}),
  });
}

export function buyByNotional(
  tradeBook: TradeBook,
  state: TradingState,
  coin: CoinId,
  point: PricePoint,
  notional: number,
): void {
  const spend = Math.min(state.cash, notional);
  if (spend <= 0) {
    return;
  }

  const qty = spend / point.price;
  const nextQty = state.quantity + qty;
  state.avgEntryPrice =
    nextQty > 0
      ? (state.avgEntryPrice * state.quantity + point.price * qty) / nextQty
      : state.avgEntryPrice;

  state.quantity = nextQty;
  state.cash -= spend;

  pushTrade(tradeBook, 'buy', coin, point.date, point.price, qty);
}

export function sellByQuantity(
  tradeBook: TradeBook,
  state: TradingState,
  coin: CoinId,
  point: PricePoint,
  qty: number,
): void {
  const sellQty = Math.min(state.quantity, qty);
  if (sellQty <= 0) {
    return;
  }

  const realizedPnl = (point.price - state.avgEntryPrice) * sellQty;
  state.cash += sellQty * point.price;
  state.quantity -= sellQty;

  if (state.quantity <= 1e-12) {
    state.quantity = 0;
    state.avgEntryPrice = 0;
  }

  pushTrade(tradeBook, 'sell', coin, point.date, point.price, sellQty, realizedPnl);
}

export function sellAll(
  tradeBook: TradeBook,
  state: TradingState,
  coin: CoinId,
  point: PricePoint,
): void {
  sellByQuantity(tradeBook, state, coin, point, state.quantity);
}

export function buyAll(
  tradeBook: TradeBook,
  state: TradingState,
  coin: CoinId,
  point: PricePoint,
): void {
  buyByNotional(tradeBook, state, coin, point, state.cash);
}

export function pushEquity(equityCurve: EquityPoint[], point: PricePoint, state: TradingState): void {
  equityCurve.push({
    date: point.date,
    equity: state.cash + state.quantity * point.price,
  });
}
