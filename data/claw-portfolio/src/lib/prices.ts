import { AssetType } from './types';

export interface PriceResult {
  price: number;
  change: number;
}

export async function fetchPrice(symbol: string, type: AssetType): Promise<PriceResult | null> {
  try {
    if (type === 'crypto') {
      const coinId = symbol.toLowerCase().replace('-usdt', '').replace('-usd', '');
      const response = await fetch(
        `https://api.coingecko.com/api/v3/simple/price?ids=${encodeURIComponent(coinId)}&vs_currencies=usd&include_24hr_change=true`,
      );

      if (!response.ok) {
        return null;
      }

      const data = (await response.json()) as Record<string, { usd?: number; usd_24h_change?: number }>;
      const coinData = data[coinId];
      if (coinData && typeof coinData.usd === 'number') {
        return {
          price: coinData.usd,
          change: coinData.usd_24h_change ?? 0,
        };
      }
      return null;
    }

    const response = await fetch(
      `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}?interval=1d&range=1d`,
    );
    if (!response.ok) {
      return null;
    }

    const data = (await response.json()) as {
      chart?: {
        result?: Array<{
          meta?: {
            regularMarketPrice?: number;
            chartPreviousClose?: number;
            previousClose?: number;
          };
        }>;
      };
    };

    const result = data.chart?.result?.[0];
    const price = result?.meta?.regularMarketPrice;
    if (typeof price !== 'number') {
      return null;
    }

    const previous = result?.meta?.chartPreviousClose ?? result?.meta?.previousClose;
    const change = typeof previous === 'number' && previous !== 0 ? ((price - previous) / previous) * 100 : 0;

    return { price, change };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    console.error(`Error fetching ${symbol}:`, message);
    return null;
  }
}
