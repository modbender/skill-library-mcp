import express, { NextFunction, Request, Response } from 'express';
import { runBacktest } from './backtest';
import { getPriceHistory, normalizeCoin } from './prices';
import { executeSimulationTrade, getPortfolioState, getSimulationHistory } from './simulator';
import { BacktestRequest, STRATEGIES, TradeAction } from './types';

const app = express();
const port = Number(process.env.PORT ?? 3002);

app.use(express.json());

app.get('/health', (_req, res) => {
  res.json({ ok: true, service: 'crypto-simulator' });
});

app.get('/api/prices/:coin', async (req, res, next) => {
  try {
    const coin = normalizeCoin(req.params.coin);
    const startDate = typeof req.query.start_date === 'string' ? req.query.start_date : undefined;
    const endDate = typeof req.query.end_date === 'string' ? req.query.end_date : undefined;
    const days = typeof req.query.days === 'string' ? Number(req.query.days) : undefined;
    const refresh = req.query.refresh === '1' || req.query.refresh === 'true';

    const prices = await getPriceHistory({
      coin,
      startDate,
      endDate,
      days: Number.isFinite(days) ? days : undefined,
      refresh,
    });

    res.json({
      coin,
      start_date: prices[0]?.date,
      end_date: prices[prices.length - 1]?.date,
      count: prices.length,
      prices,
    });
  } catch (error) {
    next(error);
  }
});

function parseBacktestRequest(body: unknown): BacktestRequest {
  if (!body || typeof body !== 'object') {
    throw new Error('Invalid request body');
  }

  const raw = body as Record<string, unknown>;
  if (typeof raw.strategy !== 'string' || !STRATEGIES.includes(raw.strategy as BacktestRequest['strategy'])) {
    throw new Error(`Invalid strategy. Supported: ${STRATEGIES.join(', ')}`);
  }
  if (typeof raw.coin !== 'string') {
    throw new Error('coin is required');
  }

  const initialCapital =
    typeof raw.initial_capital === 'number'
      ? raw.initial_capital
      : typeof raw.initial_capital === 'string'
        ? Number(raw.initial_capital)
        : 10000;

  const params = raw.params && typeof raw.params === 'object' ? (raw.params as Record<string, unknown>) : {};

  return {
    strategy: raw.strategy as BacktestRequest['strategy'],
    coin: normalizeCoin(raw.coin),
    initial_capital: initialCapital,
    start_date: typeof raw.start_date === 'string' ? raw.start_date : undefined,
    end_date: typeof raw.end_date === 'string' ? raw.end_date : undefined,
    params,
  };
}

app.post('/api/backtest', async (req, res, next) => {
  try {
    const request = parseBacktestRequest(req.body);
    const result = await runBacktest(request);
    res.json(result);
  } catch (error) {
    next(error);
  }
});

app.post('/api/simulate/trade', async (req, res, next) => {
  try {
    const body = req.body as Record<string, unknown>;
    const action = body.action;
    if (action !== 'buy' && action !== 'sell') {
      throw new Error('action must be "buy" or "sell"');
    }

    if (typeof body.coin !== 'string') {
      throw new Error('coin is required');
    }

    const amount =
      typeof body.amount === 'number'
        ? body.amount
        : typeof body.amount === 'string'
          ? Number(body.amount)
          : undefined;

    const quantity =
      typeof body.quantity === 'number'
        ? body.quantity
        : typeof body.quantity === 'string'
          ? Number(body.quantity)
          : undefined;

    const result = await executeSimulationTrade({
      action: action as TradeAction,
      coin: normalizeCoin(body.coin),
      amount: Number.isFinite(amount) ? amount : undefined,
      quantity: Number.isFinite(quantity) ? quantity : undefined,
    });

    res.json(result);
  } catch (error) {
    next(error);
  }
});

app.get('/api/simulate/portfolio', async (req, res, next) => {
  try {
    const initialCapital =
      typeof req.query.initial_capital === 'string'
        ? Number(req.query.initial_capital)
        : typeof req.query.initial_capital === 'number'
          ? req.query.initial_capital
          : 10000;

    const portfolio = await getPortfolioState(Number.isFinite(initialCapital) ? initialCapital : 10000);
    res.json(portfolio);
  } catch (error) {
    next(error);
  }
});

app.get('/api/simulate/history', (req, res, next) => {
  try {
    const limit = typeof req.query.limit === 'string' ? Number(req.query.limit) : 100;
    const history = getSimulationHistory(Number.isFinite(limit) ? limit : 100);
    res.json(history);
  } catch (error) {
    next(error);
  }
});

app.use((error: unknown, _req: Request, res: Response, _next: NextFunction) => {
  const message = error instanceof Error ? error.message : 'Unexpected error';
  res.status(400).json({ error: message });
});

app.listen(port, () => {
  console.log(`Crypto simulator API listening on http://localhost:${port}`);
});
