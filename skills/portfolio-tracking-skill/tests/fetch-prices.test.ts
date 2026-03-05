import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  fetchCryptoPrice,
  fetchStockPrice,
  fetchFXRates,
  fetchHistoricalData,
  searchSymbols,
  refreshAllPrices,
} from '../scripts/fetch-prices.js';
import type { Asset } from '../scripts/utils.js';

// Mock global fetch
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

beforeEach(() => {
  mockFetch.mockReset();
});

describe('fetchCryptoPrice', () => {
  it('should fetch price from Binance', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ symbol: 'BTCUSDT', price: '67500.00' }),
    });

    const price = await fetchCryptoPrice('BTC');
    expect(price).toBe(67500);
    expect(mockFetch).toHaveBeenCalledWith(
      'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT',
    );
  });

  it('should handle BTC-USD format symbols', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ price: '67500.00' }),
    });

    const price = await fetchCryptoPrice('BTC-USD');
    expect(price).toBe(67500);
    expect(mockFetch).toHaveBeenCalledWith(
      'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT',
    );
  });

  it('should fallback to CoinGecko when Binance fails', async () => {
    mockFetch
      .mockResolvedValueOnce({ ok: false }) // Binance fails
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ bitcoin: { usd: 67000 } }),
      });

    const price = await fetchCryptoPrice('BTC');
    expect(price).toBe(67000);
    expect(mockFetch).toHaveBeenCalledTimes(2);
  });

  it('should return null when both sources fail', async () => {
    mockFetch
      .mockResolvedValueOnce({ ok: false })
      .mockResolvedValueOnce({ ok: false });

    const price = await fetchCryptoPrice('BTC');
    expect(price).toBeNull();
  });

  it('should return null for unknown crypto with no CoinGecko mapping', async () => {
    mockFetch.mockResolvedValueOnce({ ok: false });

    const price = await fetchCryptoPrice('UNKNOWNCOIN');
    expect(price).toBeNull();
    // Should only call Binance, no CoinGecko fallback for unknown
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });
});

describe('fetchStockPrice', () => {
  it('should fetch stock price from Yahoo Finance', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        chart: { result: [{ meta: { regularMarketPrice: 175.50 } }] },
      }),
    });

    const price = await fetchStockPrice('AAPL');
    expect(price).toBe(175.50);
  });

  it('should return null when Yahoo returns 404', async () => {
    mockFetch.mockResolvedValueOnce({ ok: false });

    const price = await fetchStockPrice('INVALID');
    expect(price).toBeNull();
  });

  it('should return null when data structure is unexpected', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ chart: { result: [{ meta: {} }] } }),
    });

    const price = await fetchStockPrice('AAPL');
    expect(price).toBeNull();
  });

  it('should handle network errors gracefully', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    const price = await fetchStockPrice('AAPL');
    expect(price).toBeNull();
  });
});

describe('fetchFXRates', () => {
  it('should fetch FX rates from Yahoo Finance', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          chart: { result: [{ meta: { regularMarketPrice: 7.25 } }] },
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          chart: { result: [{ meta: { regularMarketPrice: 7.81 } }] },
        }),
      });

    const rates = await fetchFXRates();
    expect(rates.USD).toBe(1);
    expect(rates.CNY).toBe(7.25);
    expect(rates.HKD).toBe(7.81);
  });

  it('should use fallback rates when Yahoo fails', async () => {
    mockFetch
      .mockResolvedValueOnce({ ok: false })
      .mockResolvedValueOnce({ ok: false });

    const rates = await fetchFXRates();
    expect(rates.USD).toBe(1);
    expect(rates.CNY).toBe(7.24);
    expect(rates.HKD).toBe(7.8);
  });

  it('should use partial fallback', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          chart: { result: [{ meta: { regularMarketPrice: 7.3 } }] },
        }),
      })
      .mockResolvedValueOnce({ ok: false });

    const rates = await fetchFXRates();
    expect(rates.CNY).toBe(7.3);
    expect(rates.HKD).toBe(7.8); // fallback
  });
});

describe('fetchHistoricalData', () => {
  it('should fetch 3yr monthly data', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        chart: {
          result: [{
            indicators: {
              adjclose: [{ adjclose: [100, 110, null, 120, 130] }],
            },
          }],
        },
      }),
    });

    const result = await fetchHistoricalData('AAPL');
    expect(result).toEqual({ start: 100, end: 130, count: 4 });
  });

  it('should return null when less than 2 data points', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        chart: {
          result: [{
            indicators: { adjclose: [{ adjclose: [null, null, 100] }] },
          }],
        },
      }),
    });

    const result = await fetchHistoricalData('NEW');
    expect(result).toBeNull();
  });

  it('should return null on HTTP error', async () => {
    mockFetch.mockResolvedValueOnce({ ok: false });

    const result = await fetchHistoricalData('INVALID');
    expect(result).toBeNull();
  });
});

describe('searchSymbols', () => {
  it('should search and map results', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        quotes: [
          { symbol: 'AAPL', shortname: 'Apple Inc.', quoteType: 'EQUITY', exchange: 'NAS' },
          { symbol: 'BTC-USD', shortname: 'Bitcoin USD', quoteType: 'CRYPTOCURRENCY', exchange: 'CCC' },
          { symbol: 'EURUSD=X', shortname: 'EUR/USD', quoteType: 'CURRENCY', exchange: 'CCY' },
        ],
      }),
    });

    const results = await searchSymbols('apple');
    expect(results).toHaveLength(2); // CURRENCY filtered out
    expect(results[0]).toEqual({
      symbol: 'AAPL',
      shortname: 'Apple Inc.',
      quoteType: 'EQUITY',
      exchange: 'NAS',
      type: 'USSTOCK',
      currency: 'USD',
    });
    expect(results[1].type).toBe('CRYPTO');
  });

  it('should return empty array on error', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    const results = await searchSymbols('anything');
    expect(results).toEqual([]);
  });
});

describe('refreshAllPrices', () => {
  it('should skip CASH assets and deduplicate symbols', async () => {
    const assets: Asset[] = [
      { id: '1', type: 'CRYPTO', symbol: 'BTC', name: 'Bitcoin', quantity: 1, avgPrice: 60000, currentPrice: 60000, currency: 'USD', transactions: [] },
      { id: '2', type: 'CRYPTO', symbol: 'BTC', name: 'Bitcoin', quantity: 0.5, avgPrice: 65000, currentPrice: 60000, currency: 'USD', transactions: [] },
      { id: '3', type: 'CASH', symbol: 'USD', name: 'US Dollar', quantity: 10000, avgPrice: 1, currentPrice: 1, currency: 'USD', transactions: [] },
      { id: '4', type: 'USSTOCK', symbol: 'AAPL', name: 'Apple', quantity: 10, avgPrice: 150, currentPrice: 150, currency: 'USD', transactions: [] },
    ];

    mockFetch
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ price: '70000.00' }) }) // BTC
      .mockResolvedValueOnce({
        ok: true, json: () => Promise.resolve({ chart: { result: [{ meta: { regularMarketPrice: 180 } }] } }),
      }); // AAPL

    const prices = await refreshAllPrices(assets);
    expect(prices.get('BTC')).toBe(70000);
    expect(prices.get('AAPL')).toBe(180);
    expect(prices.has('USD')).toBe(false);
    // BTC should only be fetched once (dedup)
    expect(mockFetch).toHaveBeenCalledTimes(2);
  });

  it('should set stablecoin price to 1 instead of fetching', async () => {
    const assets: Asset[] = [
      { id: '1', type: 'CRYPTO', symbol: 'RWUSD', name: 'RWUSD', quantity: 1000, avgPrice: 1, currentPrice: 1, currency: 'USD', transactions: [] },
      { id: '2', type: 'CRYPTO', symbol: 'BFUSD', name: 'BFUSD', quantity: 5000, avgPrice: 1, currentPrice: 1, currency: 'USD', transactions: [] },
      { id: '3', type: 'CRYPTO', symbol: 'FDUSD', name: 'FDUSD', quantity: 2000, avgPrice: 1, currentPrice: 1, currency: 'USD', transactions: [] },
      { id: '4', type: 'CRYPTO', symbol: 'BTC', name: 'Bitcoin', quantity: 1, avgPrice: 60000, currentPrice: 60000, currency: 'USD', transactions: [] },
    ];

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ price: '70000.00' }),
    }); // only BTC should be fetched

    const prices = await refreshAllPrices(assets);
    expect(prices.get('RWUSD')).toBe(1);
    expect(prices.get('BFUSD')).toBe(1);
    expect(prices.get('FDUSD')).toBe(1);
    expect(prices.get('BTC')).toBe(70000);
    // stablecoins should not trigger any fetch
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  it('should handle partial failures gracefully', async () => {
    const assets: Asset[] = [
      { id: '1', type: 'CRYPTO', symbol: 'BTC', name: 'Bitcoin', quantity: 1, avgPrice: 60000, currentPrice: 60000, currency: 'USD', transactions: [] },
      { id: '2', type: 'USSTOCK', symbol: 'AAPL', name: 'Apple', quantity: 10, avgPrice: 150, currentPrice: 150, currency: 'USD', transactions: [] },
    ];

    // Both tasks run concurrently via Promise.allSettled, so mock by URL
    mockFetch.mockImplementation(async (url: string) => {
      if (url.includes('binance.com')) throw new Error('Network error');
      if (url.includes('coingecko.com')) throw new Error('Network error');
      if (url.includes('yahoo.com')) {
        return { ok: true, json: () => Promise.resolve({ chart: { result: [{ meta: { regularMarketPrice: 180 } }] } }) };
      }
      return { ok: false };
    });

    const prices = await refreshAllPrices(assets);
    expect(prices.has('BTC')).toBe(false); // failed
    expect(prices.get('AAPL')).toBe(180); // succeeded
  });
});
