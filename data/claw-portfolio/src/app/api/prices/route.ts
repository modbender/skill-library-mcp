import { NextResponse } from 'next/server';
import { PriceData } from '@/lib/types';

const COINGECKO_API = 'https://api.coingecko.com/api/v3';

async function fetchStockPrice(symbol: string): Promise<PriceData | null> {
  try {
    const response = await fetch(
      `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?interval=1d&range=1d`
    );
    
    if (!response.ok) return null;
    
    const data = await response.json();
    const result = data.chart?.result?.[0];
    
    if (!result) return null;
    
    const meta = result.meta;
    const price = meta.regularMarketPrice || meta.previousClose;
    const previousClose = meta.chartPreviousClose || meta.previousClose;
    
    if (!price) return null;
    
    const change = price - (previousClose || price);
    const changePercent = previousClose ? (change / previousClose) * 100 : 0;
    
    return {
      symbol,
      price,
      change,
      changePercent,
      lastUpdated: new Date().toISOString(),
    };
  } catch (error) {
    console.error(`Error fetching stock price for ${symbol}:`, error);
    return null;
  }
}

async function fetchCryptoPrice(symbol: string): Promise<PriceData | null> {
  try {
    const coinId = symbol.toLowerCase().replace('-usdt', '').replace('-usd', '');
    
    const response = await fetch(
      `${COINGECKO_API}/simple/price?ids=${coinId}&vs_currencies=usd&include_24hr_change=true`
    );
    
    if (!response.ok) return null;
    
    const data = await response.json();
    const coinData = data[coinId];
    
    if (!coinData) return null;
    
    const price = coinData.usd;
    const changePercent = coinData.usd_24h_change || 0;
    const change = price * (changePercent / 100);
    
    return {
      symbol,
      price,
      change,
      changePercent,
      lastUpdated: new Date().toISOString(),
    };
  } catch (error) {
    console.error(`Error fetching crypto price for ${symbol}:`, error);
    return null;
  }
}

export async function POST(request: Request) {
  try {
    const { symbols, types } = await request.json();
    
    const results: Record<string, PriceData> = {};
    
    for (let i = 0; i < symbols.length; i++) {
      const symbol = symbols[i];
      const type = types[i];
      
      const priceData = type === 'crypto' 
        ? await fetchCryptoPrice(symbol)
        : await fetchStockPrice(symbol);
      
      if (priceData) {
        results[symbol] = priceData;
      }
    }
    
    return NextResponse.json(results);
  } catch (error) {
    console.error('Error fetching prices:', error);
    return NextResponse.json({ error: 'Failed to fetch prices' }, { status: 500 });
  }
}
