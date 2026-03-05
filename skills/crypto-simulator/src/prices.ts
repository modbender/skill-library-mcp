import { getCachedPriceCount, getCachedPrices, getLatestCachedPrice, upsertPrices } from './db';
import { CoinId, CoinPriceRow, PricePoint, SUPPORTED_COINS } from './types';

const COIN_ALIASES: Record<string, CoinId> = {
  btc: 'bitcoin',
  bitcoin: 'bitcoin',
  eth: 'ethereum',
  ethereum: 'ethereum',
  sol: 'solana',
  solana: 'solana',
  doge: 'dogecoin',
  dogecoin: 'dogecoin',
  ada: 'cardano',
  cardano: 'cardano',
  dot: 'polkadot',
  polkadot: 'polkadot',
  avax: 'avalanche-2',
  avalanche: 'avalanche-2',
  'avalanche-2': 'avalanche-2',
  link: 'chainlink',
  chainlink: 'chainlink',
  matic: 'matic-network',
  polygon: 'matic-network',
  'matic-network': 'matic-network',
  xrp: 'ripple',
  ripple: 'ripple',
};

const API_BASE = 'https://api.coingecko.com/api/v3';

function toDateString(timestampMs: number): string {
  return new Date(timestampMs).toISOString().slice(0, 10);
}

function parseIsoDate(input: string): Date {
  const value = new Date(input);
  if (Number.isNaN(value.getTime())) {
    throw new Error(`Invalid date: ${input}`);
  }
  return value;
}

function dayDiffInclusive(startDate: string, endDate: string): number {
  const start = parseIsoDate(startDate);
  const end = parseIsoDate(endDate);
  const ms = end.getTime() - start.getTime();
  if (ms < 0) {
    throw new Error('start_date must be <= end_date');
  }
  return Math.floor(ms / (24 * 60 * 60 * 1000)) + 1;
}

function makeDateRange(days: number): { startDate: string; endDate: string } {
  const end = new Date();
  const start = new Date(end.getTime() - (days - 1) * 24 * 60 * 60 * 1000);
  return {
    startDate: start.toISOString().slice(0, 10),
    endDate: end.toISOString().slice(0, 10),
  };
}

async function fetchJsonWithRetry<T>(url: string, retries = 3): Promise<T> {
  let lastError: unknown;

  for (let attempt = 1; attempt <= retries; attempt += 1) {
    try {
      const response = await fetch(url, {
        headers: {
          Accept: 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 429 || response.status >= 500) {
          throw new Error(`CoinGecko request failed with status ${response.status}`);
        }

        const text = await response.text();
        throw new Error(`CoinGecko request failed: ${response.status} ${text}`);
      }

      return (await response.json()) as T;
    } catch (error) {
      lastError = error;
      if (attempt === retries) {
        break;
      }
      await new Promise((resolve) => setTimeout(resolve, attempt * 600));
    }
  }

  throw lastError;
}

export function normalizeCoin(input: string): CoinId {
  const normalized = COIN_ALIASES[input.toLowerCase()];
  if (!normalized) {
    throw new Error(`Unsupported coin: ${input}. Supported: ${SUPPORTED_COINS.join(', ')}`);
  }
  return normalized;
}

function normalizeMarketChart(prices: Array<[number, number]>, coin: CoinId): CoinPriceRow[] {
  const byDate = new Map<string, number>();

  for (const [timestamp, price] of prices) {
    byDate.set(toDateString(timestamp), price);
  }

  return [...byDate.entries()]
    .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
    .map(([date, price]) => ({ coin, date, price }));
}

async function fetchCoinMarketChart(coin: CoinId, days: number): Promise<CoinPriceRow[]> {
  const url = `${API_BASE}/coins/${coin}/market_chart?vs_currency=jpy&days=${days}&interval=daily`;
  const payload = await fetchJsonWithRetry<{ prices: Array<[number, number]> }>(url);
  return normalizeMarketChart(payload.prices ?? [], coin);
}

export async function fetchAndCachePrices(coin: CoinId, days = 365): Promise<PricePoint[]> {
  if (!Number.isFinite(days) || days <= 0) {
    throw new Error('days must be a positive number');
  }

  const rows = await fetchCoinMarketChart(coin, Math.ceil(days));
  upsertPrices(coin, rows);
  return rows.map((row) => ({ date: row.date, price: row.price }));
}

export interface PriceQueryOptions {
  coin: CoinId;
  startDate?: string;
  endDate?: string;
  days?: number;
  refresh?: boolean;
}

export async function getPriceHistory(options: PriceQueryOptions): Promise<PricePoint[]> {
  const { coin, refresh = false } = options;
  const days = options.days ?? 365;

  let startDate = options.startDate;
  let endDate = options.endDate;

  if (!startDate || !endDate) {
    const defaultRange = makeDateRange(days);
    startDate = startDate ?? defaultRange.startDate;
    endDate = endDate ?? defaultRange.endDate;
  }

  const expectedCount = dayDiffInclusive(startDate, endDate);

  if (refresh) {
    await fetchAndCachePrices(coin, Math.max(expectedCount + 5, days));
  } else {
    const cachedCount = getCachedPriceCount(coin, startDate, endDate);
    if (cachedCount < Math.max(3, Math.floor(expectedCount * 0.9))) {
      await fetchAndCachePrices(coin, Math.max(expectedCount + 5, days));
    }
  }

  const cached = getCachedPrices(coin, startDate, endDate);
  if (cached.length === 0) {
    throw new Error(`No price data available for ${coin} in ${startDate} - ${endDate}`);
  }

  return cached.map((row) => ({ date: row.date, price: row.price }));
}

export async function fetchCurrentPrice(coin: CoinId): Promise<number> {
  const url = `${API_BASE}/simple/price?ids=${coin}&vs_currencies=jpy`;
  try {
    const payload = await fetchJsonWithRetry<Record<string, { jpy?: number }>>(url);
    const value = payload[coin]?.jpy;
    if (value && Number.isFinite(value)) {
      return value;
    }
  } catch (error) {
    const fallback = getLatestCachedPrice(coin);
    if (fallback) {
      return fallback.price;
    }
    throw error;
  }

  const fallback = getLatestCachedPrice(coin);
  if (fallback) {
    return fallback.price;
  }

  throw new Error(`Failed to fetch current price for ${coin}`);
}

export async function fetchCurrentPrices(coins: CoinId[]): Promise<Record<CoinId, number>> {
  if (coins.length === 0) {
    return {} as Record<CoinId, number>;
  }

  const uniqCoins = [...new Set(coins)];
  const ids = uniqCoins.join(',');
  const url = `${API_BASE}/simple/price?ids=${ids}&vs_currencies=jpy`;
  const result = {} as Record<CoinId, number>;
  try {
    const payload = await fetchJsonWithRetry<Record<string, { jpy?: number }>>(url);
    for (const coin of uniqCoins) {
      const price = payload[coin]?.jpy;
      if (price && Number.isFinite(price)) {
        result[coin] = price;
        continue;
      }

      const fallback = getLatestCachedPrice(coin);
      if (!fallback) {
        throw new Error(`Failed to fetch current price for ${coin}`);
      }
      result[coin] = fallback.price;
    }
    return result;
  } catch (error) {
    for (const coin of uniqCoins) {
      const fallback = getLatestCachedPrice(coin);
      if (!fallback) {
        throw error;
      }
      result[coin] = fallback.price;
    }
  }
  return result;
}
