// Presage Market Analysis Tools
// Enhanced prediction market analysis for AI agents

const API_BASE = "https://presage.market/api";

/**
 * Fetch and analyze available prediction markets
 * Returns insights on trending markets, best prices, and opportunities
 */
async function analyzeMarkets(params) {
  const { limit = 20, category = "all" } = params || {};
  
  const response = await fetch(`${API_BASE}/events?limit=${limit}`);
  const data = await response.json();
  
  const markets = [];
  const analysis = [];
  
  for (const event of data.events || []) {
    for (const market of event.markets || []) {
      const price = market.yesBid || 0;
      const volume = market.volume || 0;
      
      // Find opportunities
      let recommendation = "HOLD";
      let reasoning = "";
      
      // High volume + extreme price = potential mispricing
      if (volume > 100000 && price > 0.8) {
        recommendation = "CONSIDER_NO";
        reasoning = `High volume (${volume}) but price very high (${price}). Market may be overconfident.`;
      } else if (volume > 100000 && price < 0.2) {
        recommendation = "CONSIDER_YES";
        reasoning = `High volume (${volume}) but price very low (${price}). Market may be undervaluing probability.`;
      } else if (price >= 0.45 && price <= 0.55) {
        recommendation = "WATCH";
        reasoning = "Price in uncertainty zone - good for research.";
      }
      
      markets.push({
        ticker: market.ticker,
        title: event.title,
        price: price,
        volume: volume,
        recommendation,
        reasoning
      });
    }
  }
  
  // Sort by volume
  markets.sort((a, b) => b.volume - a.volume);
  
  return {
    totalMarkets: markets.length,
    opportunities: markets.filter(m => m.recommendation !== "HOLD"),
    topMarkets: markets.slice(0, 10),
    summary: `Found ${markets.length} markets. ${markets.filter(m => m.recommendation !== "HOLD").length} have potential opportunities.`
  };
}

/**
 * Get detailed analysis of a specific market
 */
async function analyzeMarket(params) {
  const { ticker, includeNews = true } = params;
  
  // Fetch market data
  const [marketRes, orderbookRes, tradesRes] = await Promise.all([
    fetch(`${API_BASE}/markets/${ticker}`),
    fetch(`${API_BASE}/markets/${ticker}/orderbook`),
    fetch(`${API_BASE}/markets/${ticker}/trades?limit=10`)
  ]);
  
  const market = await marketRes.json();
  const orderbook = await orderbookRes.json();
  const trades = await tradesRes.json();
  
  const yesPrice = market.yesBid || 0;
  const noPrice = market.noBid || 0;
  
  // Calculate spread
  const spread = (market.yesAsk - market.yesBid) || 0;
  
  // Analyze orderbook pressure
  const yesBidVolume = orderbook.yes_bids?.reduce((sum, o) => sum + o.quantity, 0) || 0;
  const yesAskVolume = orderbook.yes_asks?.reduce((sum, o) => sum + o.quantity, 0) || 0;
  const pressure = yesBidVolume > yesAskVolume ? "BUY" : "SELL";
  
  // Recent trade sentiment
  const recentYes = trades.trades?.filter(t => t.side === "YES").length || 0;
  const recentNo = trades.trades?.filter(t => t.side === "NO").length || 0;
  const sentiment = recentYes > recentNo ? "BULLISH" : recentNo > recentYes ? "BEARISH" : "NEUTRAL";
  
  return {
    ticker: market.ticker,
    title: market.title,
    currentPrice: yesPrice,
    spread: spread.toFixed(4),
    orderbookPressure: pressure,
    recentSentiment: sentiment,
    volume: market.volume,
    status: market.status,
    recommendation: yesPrice > 0.7 ? "LEAN_NO" : yesPrice < 0.3 ? "LEAN_YES" : "RESEARCH_MORE"
  };
}

/**
 * Get my agent portfolio and performance
 */
async function getPortfolio(params) {
  const { agentId } = params;
  
  const response = await fetch(`${API_BASE}/agents/${agentId}`);
  const agent = await response.json();
  
  const positions = agent.positions || [];
  const trades = agent.trades || [];
  
  // Calculate metrics
  const totalInvested = positions.reduce((sum, p) => sum + p.quantity, 0);
  const currentValue = positions.reduce((sum, p) => {
    const value = p.side === "YES" ? p.yesPrice : p.noPrice;
    return sum + (p.quantity * value);
  }, 0);
  
  const pnl = currentValue - totalInvested;
  const pnlPercent = totalInvested > 0 ? (pnl / totalInvested) * 100 : 0;
  
  return {
    agentId: agent.id,
    name: agent.name,
    balance: agent.balance,
    totalPnL: pnl.toFixed(2),
    totalPnLPercent: pnlPercent.toFixed(2),
    openPositions: positions.length,
    recentTrades: trades.slice(0, 5).map(t => ({
      ticker: t.marketTicker,
      side: t.side,
      quantity: t.quantity,
      reasoning: t.reasoning?.substring(0, 100) + "..."
    }))
  };
}

/**
 * Find best trading opportunities across all markets
 */
async function findOpportunities(params) {
  const { minVolume = 50000 } = params || {};
  
  const response = await fetch(`${API_BASE}/events?limit=50`);
  const data = await response.json();
  
  const opportunities = [];
  
  for (const event of data.events || []) {
    for (const market of event.markets || []) {
      if (market.volume < minVolume) continue;
      if (market.status !== "open") continue;
      
      const price = market.yesBid || 0;
      const edge = Math.abs(0.5 - price);
      
      // Low edge = high confidence market (less opportunity)
      // High edge = more uncertainty (more opportunity if you have info)
      if (edge > 0.15 && market.volume > 100000) {
        opportunities.push({
          ticker: market.ticker,
          title: event.title,
          price: price,
          volume: market.volume,
          edge: edge.toFixed(3),
          recommendation: price < 0.35 ? "YES (undervalued)" : price > 0.65 ? "NO (overvalued)" : "RESEARCH"
        });
      }
    }
  }
  
  opportunities.sort((a, b) => b.volume - a.volume);
  
  return {
    count: opportunities.length,
    topOpportunities: opportunities.slice(0, 10),
    summary: `Found ${opportunities.length} high-volume markets with significant price edge.`
  };
}

module.exports = {
  analyzeMarkets,
  analyzeMarket,
  getPortfolio,
  findOpportunities
};
