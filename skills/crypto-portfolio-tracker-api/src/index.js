/**
 * @strykr/portfolio-tracker
 * Real-time crypto portfolio tracking powered by Strykr Prism API
 */

const PRISM_BASE = 'https://api.prismapi.ai';

class PortfolioTracker {
  constructor(options = {}) {
    this.apiKey = options.apiKey || process.env.PRISM_API_KEY || null;
    this.baseUrl = options.baseUrl || PRISM_BASE;
    this.holdings = new Map();
  }

  /**
   * Add a holding to the portfolio
   * @param {string} symbol - Token symbol (BTC, ETH, SOL, etc.)
   * @param {number} amount - Amount held
   * @param {number} [costBasis] - Optional cost basis per unit
   */
  addHolding(symbol, amount, costBasis = null) {
    const existing = this.holdings.get(symbol.toUpperCase()) || { amount: 0, costBasis: null };
    this.holdings.set(symbol.toUpperCase(), {
      amount: existing.amount + amount,
      costBasis: costBasis || existing.costBasis
    });
    return this;
  }

  /**
   * Remove a holding from the portfolio
   * @param {string} symbol - Token symbol
   * @param {number} [amount] - Amount to remove (all if not specified)
   */
  removeHolding(symbol, amount = null) {
    const key = symbol.toUpperCase();
    if (amount === null) {
      this.holdings.delete(key);
    } else {
      const existing = this.holdings.get(key);
      if (existing) {
        existing.amount -= amount;
        if (existing.amount <= 0) {
          this.holdings.delete(key);
        }
      }
    }
    return this;
  }

  /**
   * Fetch current prices for all holdings
   * @returns {Promise<Object>} Price data for each symbol
   */
  async fetchPrices() {
    const symbols = Array.from(this.holdings.keys());
    if (symbols.length === 0) return { prices: [] };

    const url = `${this.baseUrl}/crypto/prices/batch?symbols=${symbols.join(',')}`;
    const headers = this.apiKey ? { 'X-API-Key': this.apiKey } : {};
    
    const response = await fetch(url, { headers });
    if (!response.ok) {
      throw new Error(`Prism API error: ${response.status}`);
    }
    
    return response.json();
  }

  /**
   * Get full portfolio valuation with P&L
   * @returns {Promise<Object>} Portfolio summary
   */
  async getValuation() {
    const result = await this.fetchPrices();
    const priceMap = {};
    
    // Build lookup map from array response
    for (const p of (result.prices || [])) {
      priceMap[p.symbol] = p;
    }
    
    const items = [];
    let totalValue = 0;
    let totalCost = 0;

    for (const [symbol, holding] of this.holdings) {
      const priceData = priceMap[symbol] || {};
      const price = priceData.price_usd || priceData.price || 0;
      const value = holding.amount * price;
      const cost = holding.costBasis ? holding.amount * holding.costBasis : null;
      const pnl = cost !== null ? value - cost : null;
      const pnlPercent = cost !== null && cost > 0 ? ((value - cost) / cost) * 100 : null;

      totalValue += value;
      if (cost !== null) totalCost += cost;

      items.push({
        symbol,
        amount: holding.amount,
        price,
        value,
        costBasis: holding.costBasis,
        pnl,
        pnlPercent,
        change24h: priceData?.change_24h_pct || priceData?.change_24h || null
      });
    }

    // Sort by value descending
    items.sort((a, b) => b.value - a.value);

    // Calculate allocation percentages
    for (const item of items) {
      item.allocation = totalValue > 0 ? (item.value / totalValue) * 100 : 0;
    }

    return {
      totalValue,
      totalCost: totalCost > 0 ? totalCost : null,
      totalPnl: totalCost > 0 ? totalValue - totalCost : null,
      totalPnlPercent: totalCost > 0 ? ((totalValue - totalCost) / totalCost) * 100 : null,
      holdings: items,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Get portfolio as simple object
   */
  toJSON() {
    const obj = {};
    for (const [symbol, holding] of this.holdings) {
      obj[symbol] = holding;
    }
    return obj;
  }

  /**
   * Load portfolio from JSON
   */
  static fromJSON(data) {
    const tracker = new PortfolioTracker();
    for (const [symbol, holding] of Object.entries(data)) {
      tracker.holdings.set(symbol, holding);
    }
    return tracker;
  }
}

/**
 * Quick price lookup for a single symbol
 * @param {string} symbol - Token symbol
 * @returns {Promise<Object>} Price data
 */
async function getPrice(symbol) {
  const response = await fetch(`${PRISM_BASE}/crypto/price/${symbol.toUpperCase()}`);
  if (!response.ok) {
    throw new Error(`Prism API error: ${response.status}`);
  }
  return response.json();
}

/**
 * Batch price lookup
 * @param {string[]} symbols - Array of symbols
 * @returns {Promise<Object>} Prices keyed by symbol
 */
async function getPrices(symbols) {
  const url = `${PRISM_BASE}/crypto/prices/batch?symbols=${symbols.map(s => s.toUpperCase()).join(',')}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Prism API error: ${response.status}`);
  }
  return response.json();
}

module.exports = {
  PortfolioTracker,
  getPrice,
  getPrices
};
