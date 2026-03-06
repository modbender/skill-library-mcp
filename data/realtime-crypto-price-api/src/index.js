/**
 * realtime-crypto-price-api
 * Real-time cryptocurrency price data for 10,000+ tokens
 * Powered by PRISM API - https://prismapi.ai
 */

const PRISM_BASE = process.env.PRISM_API_URL || 'https://api.prismapi.ai';

class CryptoPrice {
  constructor(apiKey) {
    this.apiKey = apiKey || process.env.PRISM_API_KEY;
    this.baseUrl = PRISM_BASE;
  }

  async _fetch(endpoint, params = {}) {
    const url = new URL(this.baseUrl + endpoint);
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined) url.searchParams.set(k, v);
    });

    const headers = {};
    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    const res = await fetch(url, { headers });
    
    if (!res.ok) {
      throw new Error(`API error: ${res.status} ${res.statusText}`);
    }
    
    return res.json();
  }

  /**
   * Get current price for a single cryptocurrency
   * @param {string} symbol - Token symbol (BTC, ETH, SOL, etc.)
   * @param {string} currency - Quote currency (default: USD)
   * @returns {Promise<{symbol, price, change24h, volume24h, marketCap, timestamp}>}
   */
  async getPrice(symbol, currency = 'USD') {
    const data = await this._fetch(`/crypto/price/${symbol.toUpperCase()}`, { currency });
    return {
      symbol: symbol.toUpperCase(),
      price: data.price,
      change24h: data.change_24h,
      changePercent24h: data.change_percent_24h,
      volume24h: data.volume_24h,
      marketCap: data.market_cap,
      timestamp: data.timestamp || Date.now()
    };
  }

  /**
   * Get prices for multiple cryptocurrencies in one call
   * @param {string[]} symbols - Array of token symbols
   * @param {string} currency - Quote currency (default: USD)
   * @returns {Promise<Object.<string, {price, change24h, volume24h}>>}
   */
  async getPrices(symbols, currency = 'USD') {
    const symbolList = symbols.map(s => s.toUpperCase()).join(',');
    const data = await this._fetch('/crypto/prices/batch', { symbols: symbolList, currency });
    return data;
  }

  /**
   * Get top cryptocurrencies by market cap
   * @param {number} limit - Number of results (default: 100)
   * @param {string} currency - Quote currency (default: USD)
   * @returns {Promise<Array<{rank, symbol, name, price, marketCap, volume24h, change24h}>>}
   */
  async getTopCoins(limit = 100, currency = 'USD') {
    return this._fetch('/crypto/top', { limit, currency });
  }

  /**
   * Get trending cryptocurrencies (biggest movers)
   * @param {string} direction - 'gainers' or 'losers'
   * @param {number} limit - Number of results (default: 20)
   * @returns {Promise<Array<{symbol, name, price, change24h}>>}
   */
  async getTrending(direction = 'gainers', limit = 20) {
    return this._fetch('/crypto/trending', { direction, limit });
  }

  /**
   * Get historical price data
   * @param {string} symbol - Token symbol
   * @param {string} interval - '1h', '4h', '1d', '1w'
   * @param {number} limit - Number of candles
   * @returns {Promise<Array<{timestamp, open, high, low, close, volume}>>}
   */
  async getHistory(symbol, interval = '1d', limit = 30) {
    return this._fetch(`/crypto/history/${symbol.toUpperCase()}`, { interval, limit });
  }

  /**
   * Search for cryptocurrencies by name or symbol
   * @param {string} query - Search query
   * @returns {Promise<Array<{symbol, name, logo}>>}
   */
  async search(query) {
    return this._fetch('/crypto/search', { q: query });
  }
}

module.exports = { CryptoPrice };
