import type { Asset, ExchangeRates, AssetType, Currency } from './utils.js';
import { COINGECKO_MAP, DEFAULT_FX_RATES, STABLECOINS, detectAssetDetails } from './utils.js';

// ─── Crypto Price (Binance → CoinGecko fallback) ───────────────────

export async function fetchCryptoPrice(symbol: string): Promise<number | null> {
  const baseSymbol = symbol.split('-')[0].toUpperCase();

  // Attempt 1: Binance
  try {
    const url = `https://api.binance.com/api/v3/ticker/price?symbol=${baseSymbol}USDT`;
    const response = await fetch(url);
    if (response.ok) {
      const data = await response.json();
      if (data.price) return parseFloat(data.price);
    }
  } catch { /* fallback */ }

  // Attempt 2: CoinGecko
  const cgId = COINGECKO_MAP[baseSymbol];
  if (cgId) {
    try {
      const url = `https://api.coingecko.com/api/v3/simple/price?ids=${cgId}&vs_currencies=usd`;
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        if (data[cgId]?.usd) return data[cgId].usd;
      }
    } catch { /* give up */ }
  }

  return null;
}

// ─── Stock Price (Yahoo Finance) ────────────────────────────────────

export async function fetchStockPrice(symbol: string): Promise<number | null> {
  try {
    const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}?interval=1d&range=1d`;
    const response = await fetch(url);
    if (!response.ok) return null;

    const data = await response.json();
    const result = data.chart?.result?.[0];
    return result?.meta?.regularMarketPrice ?? null;
  } catch {
    return null;
  }
}

// ─── FX Rates ───────────────────────────────────────────────────────

export async function fetchFXRates(): Promise<ExchangeRates> {
  const rates: ExchangeRates = { USD: 1, CNY: 0, HKD: 0 };
  const symbols = ['CNY=X', 'HKD=X'] as const;

  await Promise.all(symbols.map(async (symbol) => {
    try {
      const url = `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?interval=1d&range=1d`;
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        const price = data.chart?.result?.[0]?.meta?.regularMarketPrice;
        if (price) {
          if (symbol === 'CNY=X') rates.CNY = price;
          if (symbol === 'HKD=X') rates.HKD = price;
        }
      }
    } catch { /* fallback */ }
  }));

  // Fallback values
  if (!rates.CNY) rates.CNY = DEFAULT_FX_RATES.CNY;
  if (!rates.HKD) rates.HKD = DEFAULT_FX_RATES.HKD;

  return rates;
}

// ─── Historical Data (3yr monthly) ──────────────────────────────────

export async function fetchHistoricalData(symbol: string): Promise<{ start: number; end: number; count: number } | null> {
  try {
    const threeYearsAgo = Math.floor(Date.now() / 1000) - (3 * 365 * 24 * 60 * 60);
    const now = Math.floor(Date.now() / 1000);
    const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}?period1=${threeYearsAgo}&period2=${now}&interval=1mo`;

    const response = await fetch(url);
    if (!response.ok) return null;

    const data = await response.json();
    const result = data.chart?.result?.[0];
    const adjCloses = result?.indicators?.adjclose?.[0]?.adjclose as (number | null)[] | undefined;
    if (!adjCloses) return null;

    const valid = adjCloses.filter((c): c is number => c !== null);
    if (valid.length < 2) return null;

    return { start: valid[0], end: valid[valid.length - 1], count: valid.length };
  } catch {
    return null;
  }
}

// ─── Symbol Search ──────────────────────────────────────────────────

export interface SearchResult {
  symbol: string;
  shortname: string;
  quoteType: string;
  exchange: string;
  type: AssetType;
  currency: Currency;
}

export async function searchSymbols(query: string): Promise<SearchResult[]> {
  try {
    const url = `https://query2.finance.yahoo.com/v1/finance/search?q=${encodeURIComponent(query)}&quotesCount=10`;
    const response = await fetch(url);
    if (!response.ok) return [];

    const data = await response.json();
    return (data.quotes || [])
      .map((q: any) => {
        const details = detectAssetDetails(q.quoteType, q.exchange, q.symbol);
        if (!details) return null;
        return {
          symbol: q.symbol,
          shortname: q.shortname || q.longname || q.symbol,
          quoteType: q.quoteType,
          exchange: q.exchange,
          ...details,
        };
      })
      .filter((q: any): q is SearchResult => q !== null);
  } catch {
    return [];
  }
}

// ─── Batch Price Refresh ────────────────────────────────────────────

export async function refreshAllPrices(assets: Asset[]): Promise<Map<string, number>> {
  const prices = new Map<string, number>();
  const seen = new Set<string>();

  const tasks = assets
    .filter(a => {
      if (a.type === 'CASH' || seen.has(a.symbol)) return false;
      seen.add(a.symbol);
      return true;
    })
    .map(async (a) => {
      if (STABLECOINS.has(a.symbol)) {
        prices.set(a.symbol, 1);
        return;
      }
      let price: number | null = null;
      if (a.type === 'CRYPTO') {
        price = await fetchCryptoPrice(a.symbol);
      } else {
        price = await fetchStockPrice(a.symbol);
      }
      if (price !== null) {
        prices.set(a.symbol, price);
      }
    });

  await Promise.allSettled(tasks);
  return prices;
}

// ─── CLI Entry Point ────────────────────────────────────────────────

const command = process.argv[2];

if (command) {
  try {
    let result: unknown;

    switch (command) {
      case 'crypto': {
        const symbol = process.argv[3];
        if (!symbol) throw new Error('Symbol required');
        const price = await fetchCryptoPrice(symbol);
        result = price !== null ? { price } : { error: 'Price not found' };
        break;
      }
      case 'stock': {
        const symbol = process.argv[3];
        if (!symbol) throw new Error('Symbol required');
        const price = await fetchStockPrice(symbol);
        result = price !== null ? { price } : { error: 'Price not found' };
        break;
      }
      case 'fx': {
        result = await fetchFXRates();
        break;
      }
      case 'historical': {
        const symbol = process.argv[3];
        if (!symbol) throw new Error('Symbol required');
        result = await fetchHistoricalData(symbol);
        if (!result) result = { error: 'Historical data not found' };
        break;
      }
      case 'search': {
        const query = process.argv[3];
        if (!query) throw new Error('Query required');
        result = await searchSymbols(query);
        break;
      }
      case 'refresh': {
        // Read assets from stdin
        const input = await new Promise<string>((resolve) => {
          let data = '';
          process.stdin.on('data', chunk => data += chunk);
          process.stdin.on('end', () => resolve(data));
        });
        const assets = JSON.parse(input) as Asset[];
        const prices = await refreshAllPrices(assets);
        result = Object.fromEntries(prices);
        break;
      }
      default:
        result = { error: `Unknown command: ${command}` };
    }

    console.log(JSON.stringify(result));
  } catch (err: any) {
    console.log(JSON.stringify({ error: err.message }));
    process.exit(1);
  }
}
