/**
 * Simple Funding Rate Dashboard
 * No SDK dependencies, pure HTTP
 */

import express from 'express';
import { HttpAggregator } from '../core/http-aggregator';

const app = express();
const PORT = process.env.PORT || 3456;
const aggregator = new HttpAggregator();

// Cache with 30 second TTL
let cache: { data: any; timestamp: number } | null = null;
const CACHE_TTL = 30000;

async function getLatestData() {
  if (cache && Date.now() - cache.timestamp < CACHE_TTL) {
    return cache.data;
  }
  
  const [driftRates, binanceRates] = await Promise.all([
    aggregator.getDriftFunding(),
    aggregator.getBinanceFunding(),
  ]);
  
  const opportunities = await aggregator.findArbitrageOpportunities(0);
  
  cache = {
    data: { driftRates, binanceRates, opportunities, lastUpdate: new Date().toISOString() },
    timestamp: Date.now(),
  };
  
  return cache.data;
}

// API endpoint
app.get('/api/rates', async (req, res) => {
  try {
    const data = await getLatestData();
    res.json(data);
  } catch (e) {
    res.status(500).json({ error: String(e) });
  }
});

// HTML Dashboard
app.get('/', async (req, res) => {
  try {
    const data = await getLatestData();
    
    const html = `
<!DOCTYPE html>
<html>
<head>
  <title>⚡ Solana Funding Arbitrage</title>
  <meta http-equiv="refresh" content="30">
  <style>
    * { box-sizing: border-box; }
    body { 
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #0d1117; color: #c9d1d9;
      margin: 0; padding: 20px;
    }
    h1 { color: #58a6ff; }
    .card { 
      background: #161b22; border-radius: 8px; 
      padding: 20px; margin: 10px 0;
      border: 1px solid #30363d;
    }
    .positive { color: #3fb950; }
    .negative { color: #f85149; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #30363d; }
    th { color: #8b949e; font-weight: 500; }
    .opportunity { 
      background: linear-gradient(135deg, #238636 0%, #1f6f2c 100%);
      border-color: #238636;
    }
    .small { font-size: 0.85em; color: #8b949e; }
    .highlight { color: #f0883e; font-weight: 600; }
  </style>
</head>
<body>
  <h1>⚡ Solana Funding Rate Arbitrage</h1>
  <p class="small">Last update: ${data.lastUpdate} (auto-refresh: 30s)</p>
  
  <div class="card">
    <h2>📊 Funding Rate Comparison</h2>
    <table>
      <thead>
        <tr>
          <th>Symbol</th>
          <th>Drift APY</th>
          <th>Binance APY</th>
          <th>Spread</th>
          <th>Best Strategy</th>
        </tr>
      </thead>
      <tbody>
        ${data.opportunities.map((opp: any) => {
          const spreadClass = opp.spreadApy > 10 ? 'highlight' : '';
          const driftClass = opp.dexRate.fundingRateApy > 0 ? 'positive' : 'negative';
          const binanceClass = opp.cexRate.fundingRateApy > 0 ? 'positive' : 'negative';
          return `
            <tr>
              <td><strong>${opp.symbol}</strong></td>
              <td class="${driftClass}">${opp.dexRate.fundingRateApy.toFixed(2)}%</td>
              <td class="${binanceClass}">${opp.cexRate.fundingRateApy.toFixed(2)}%</td>
              <td class="${spreadClass}">${opp.spreadApy.toFixed(2)}%</td>
              <td>${opp.direction.replace(/_/g, ' ')}</td>
            </tr>
          `;
        }).join('')}
      </tbody>
    </table>
  </div>
  
  ${data.opportunities.filter((o: any) => o.spreadApy > 10).map((opp: any) => `
    <div class="card opportunity">
      <h2>🎯 ${opp.symbol} Opportunity: ${opp.spreadApy.toFixed(2)}% APY</h2>
      <p>
        <strong>Strategy:</strong> ${opp.direction === 'long_cex_short_dex' 
          ? `Long on Binance @ ${opp.cexRate.fundingRateApy.toFixed(2)}%, Short on Drift @ ${opp.dexRate.fundingRateApy.toFixed(2)}%`
          : `Long on Drift @ ${opp.dexRate.fundingRateApy.toFixed(2)}%, Short on Binance @ ${opp.cexRate.fundingRateApy.toFixed(2)}%`
        }
      </p>
      <p>
        <strong>Estimated Net APY:</strong> ${opp.estimatedApy.toFixed(2)}%
      </p>
      <p class="small">
        Prices: Drift $${opp.dexRate.price.toFixed(2)} | Binance $${opp.cexRate.price.toFixed(2)}
      </p>
    </div>
  `).join('')}
  
  <div class="card">
    <h2>ℹ️ How It Works</h2>
    <ul>
      <li><strong>Positive Rate (🔴):</strong> Longs pay shorts</li>
      <li><strong>Negative Rate (🟢):</strong> Shorts pay longs</li>
      <li><strong>Strategy:</strong> Go long where you receive funding, short where you pay less</li>
      <li><strong>Risk:</strong> Price divergence between venues, liquidation, execution</li>
    </ul>
  </div>
</body>
</html>
    `;
    
    res.send(html);
  } catch (e) {
    res.status(500).send(`Error: ${e}`);
  }
});

app.listen(PORT, () => {
  console.log(`\n🚀 Dashboard running at http://localhost:${PORT}`);
  console.log('📊 API endpoint: http://localhost:' + PORT + '/api/rates');
  console.log('\nPress Ctrl+C to stop\n');
});
