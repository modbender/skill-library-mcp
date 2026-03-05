declare module 'yfinance' {
  export function ticker(symbol: string): Ticker;
  
  export interface Ticker {
    info: Promise<{
      currentPrice?: number;
      regularMarketPrice?: number;
      previousClose?: number;
      regularMarketPreviousClose?: number;
    }>;
  }
  
  const yfinance: {
    ticker: typeof ticker;
  };
  export default yfinance;
}
