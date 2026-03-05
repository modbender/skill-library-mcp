import {
  clearAllSimulationData,
  ensurePortfolio,
  getPortfolioCash,
  getPosition,
  insertSimulationTrade,
  listPositions,
  listSimulationTrades,
  setPortfolioCash,
  setPosition,
} from './db';
import { fetchCurrentPrice, fetchCurrentPrices } from './prices';
import {
  CoinId,
  PortfolioState,
  PositionState,
  SimulationTradeRequest,
  SimulationTradeResult,
} from './types';

const DEFAULT_INITIAL_CAPITAL = 10000;

function ensurePositive(value: number | undefined, fieldName: string): number {
  if (value === undefined || !Number.isFinite(value) || value <= 0) {
    throw new Error(`${fieldName} must be a positive number`);
  }
  return value;
}

function resolveBuyOrder(request: SimulationTradeRequest, price: number): { quantity: number; notional: number } {
  if (request.quantity !== undefined) {
    const quantity = ensurePositive(request.quantity, 'quantity');
    return { quantity, notional: quantity * price };
  }

  const amount = ensurePositive(request.amount, 'amount');
  return { quantity: amount / price, notional: amount };
}

function resolveSellOrder(request: SimulationTradeRequest, price: number): { quantity: number; notional: number } {
  if (request.quantity !== undefined) {
    const quantity = ensurePositive(request.quantity, 'quantity');
    return { quantity, notional: quantity * price };
  }

  const amount = ensurePositive(request.amount, 'amount');
  return { quantity: amount / price, notional: amount };
}

export async function executeSimulationTrade(
  request: SimulationTradeRequest,
  initialCapital = DEFAULT_INITIAL_CAPITAL,
): Promise<SimulationTradeResult> {
  ensurePortfolio(initialCapital);

  const price = await fetchCurrentPrice(request.coin);
  const cash = getPortfolioCash();
  const position = getPosition(request.coin);
  const now = new Date().toISOString();

  let nextCash = cash;
  let nextQuantity = position?.quantity ?? 0;
  let nextAvgPrice = position?.avg_price ?? 0;
  let tradeQuantity = 0;
  let tradeNotional = 0;

  if (request.action === 'buy') {
    const order = resolveBuyOrder(request, price);
    if (order.notional > cash) {
      throw new Error(`Insufficient cash. available=${cash.toFixed(2)} required=${order.notional.toFixed(2)}`);
    }

    tradeQuantity = order.quantity;
    tradeNotional = order.notional;

    nextCash = cash - tradeNotional;
    const totalCost = nextAvgPrice * nextQuantity + tradeNotional;
    nextQuantity += tradeQuantity;
    nextAvgPrice = nextQuantity > 0 ? totalCost / nextQuantity : 0;
  } else {
    const order = resolveSellOrder(request, price);
    if (!position || position.quantity <= 0) {
      throw new Error(`No position to sell for ${request.coin}`);
    }

    if (order.quantity > position.quantity) {
      throw new Error(
        `Insufficient quantity. available=${position.quantity.toFixed(8)} required=${order.quantity.toFixed(8)}`,
      );
    }

    tradeQuantity = order.quantity;
    tradeNotional = order.notional;
    nextCash = cash + tradeNotional;
    nextQuantity = position.quantity - tradeQuantity;
    nextAvgPrice = nextQuantity > 0 ? position.avg_price : 0;
  }

  setPortfolioCash(nextCash);
  setPosition(request.coin, nextQuantity, nextAvgPrice);

  const tradeId = insertSimulationTrade({
    action: request.action,
    coin: request.coin,
    price,
    quantity: tradeQuantity,
    notional: tradeNotional,
    createdAt: now,
  });

  const portfolio = await getPortfolioState(initialCapital);

  return {
    trade: {
      id: tradeId,
      action: request.action,
      coin: request.coin,
      price,
      quantity: tradeQuantity,
      notional: tradeNotional,
      created_at: now,
    },
    portfolio,
  };
}

export async function getPortfolioState(initialCapital = DEFAULT_INITIAL_CAPITAL): Promise<PortfolioState> {
  ensurePortfolio(initialCapital);

  const cash = getPortfolioCash();
  const rawPositions = listPositions();

  if (rawPositions.length === 0) {
    return {
      cash,
      positions: [],
      total_value: cash,
    };
  }

  const currentPrices = await fetchCurrentPrices(rawPositions.map((position) => position.coin));

  const positions: PositionState[] = rawPositions.map((position) => {
    const currentPrice = currentPrices[position.coin as CoinId];
    const marketValue = position.quantity * currentPrice;
    const unrealizedPnl = (currentPrice - position.avg_price) * position.quantity;

    return {
      coin: position.coin,
      quantity: position.quantity,
      avg_price: position.avg_price,
      current_price: currentPrice,
      market_value: marketValue,
      unrealized_pnl: unrealizedPnl,
    };
  });

  const totalValue = cash + positions.reduce((sum, position) => sum + position.market_value, 0);

  return {
    cash,
    positions,
    total_value: totalValue,
  };
}

export function getSimulationHistory(limit = 100): Array<{
  id: number;
  action: 'buy' | 'sell';
  coin: CoinId;
  price: number;
  quantity: number;
  notional: number;
  created_at: string;
}> {
  return listSimulationTrades(limit);
}

export function resetSimulationData(): void {
  clearAllSimulationData();
}
