/**
 * Drift Funding Rate Dashboard
 * No SDK dependencies, pure HTTP
 */

import express from 'express';
import { DriftAggregator } from '../core/drift-aggregator';

const app = express();
const PORT = process.env.PORT || 3456;
const aggregator = new DriftAggregator();

// Cache with 30 second TTL
let cache: { data: any; timestamp: number } | null = null;
const CACHE_TTL = 30000;

async function getData() {
  if (cache && Date.now() - cache.timestamp < CACHE_TTL) {
    return cache.data;
  }
  
  const [opportunities, pairs] = await Promise.all([
    aggregator.getTopFundingOpportunities(20),
    aggregator.findDeltaNeutralPairs(),
  ]);
  
  cache = {
    data: { opportunities, pairs, lastUpdate: new Date().toISOString() },
    timestamp: Date.now(),
  };
  
  return cache.data;
}

app.get('/api/funding', async (req, res) => {
  try {
    res.json(await getData());
  } catch (e) {
    res.status(500).json({ error: String(e) });
  }
});

app.get('/', async (req, res) => {
  try {
    const data = await getData();
    
    const html = `
<!DOCTYPE html>
<html>
<head>
  <title>⚡ Drift Funding Scanner</title>
  <meta http-equiv="refresh" content="30">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { 
      font-family: 'JetBrains Mono', 'Fira Code', monospace;
      background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
      color: #e6edf3;
      min-height: 100vh;
      padding: 20px;
    }
    .header {
      text-align: center;
      margin-bottom: 30px;
    }
    h1 { color: #58a6ff; font-size: 2em; }
    .subtitle { color: #8b949e; margin-top: 5px; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    @media (max-width: 1200px) { .grid { grid-template-columns: 1fr; } }
    .card { 
      background: rgba(22, 27, 34, 0.8);
      border: 1px solid #30363d;
      border-radius: 12px;
      padding: 20px;
      backdrop-filter: blur(10px);
    }
    .card h2 { color: #58a6ff; margin-bottom: 15px; font-size: 1.1em; }
    table { width: 100%; border-collapse: collapse; font-size: 0.85em; }
    th { color: #8b949e; text-align: left; padding: 8px 4px; border-bottom: 1px solid #30363d; }
    td { padding: 8px 4px; border-bottom: 1px solid rgba(48, 54, 61, 0.5); }
    .positive { color: #3fb950; }
    .negative { color: #f85149; }
    .highlight { 
      background: linear-gradient(90deg, rgba(56, 139, 253, 0.1), transparent);
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.7; }
    }
    .mega { 
      font-size: 1.2em; 
      font-weight: bold;
      text-shadow: 0 0 10px currentColor;
    }
    .pair-card {
      background: linear-gradient(135deg, rgba(35, 134, 54, 0.2), rgba(22, 27, 34, 0.9));
      border-color: #238636;
      margin-bottom: 10px;
      padding: 15px;
      border-radius: 8px;
    }
    .pair-title { color: #3fb950; font-weight: bold; }
    .pair-apy { 
      font-size: 1.5em; 
      color: #3fb950;
      text-shadow: 0 0 20px rgba(63, 185, 80, 0.5);
    }
    .warning { 
      background: rgba(210, 153, 34, 0.1);
      border: 1px solid #d29922;
      border-radius: 8px;
      padding: 15px;
      margin-top: 20px;
      color: #d29922;
    }
    .footer { text-align: center; margin-top: 20px; color: #8b949e; font-size: 0.8em; }
  </style>
</head>
<body>
  <div class="header">
    <h1>⚡ DRIFT FUNDING SCANNER</h1>
    <div class="subtitle">Real-time funding rate arbitrage opportunities</div>
    <div class="subtitle">Last update: ${data.lastUpdate} (auto-refresh: 30s)</div>
  </div>
  
  <div class="grid">
    <div class="card">
      <h2>🔥 TOP FUNDING RATES</h2>
      <table>
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Price</th>
            <th>Hourly</th>
            <th>APY</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          ${data.opportunities.slice(0, 15).map((opp: any, i: number) => {
            const absApy = Math.abs(opp.fundingApy);
            const apyClass = absApy > 10000 ? 'mega' : '';
            const rowClass = i < 3 ? 'highlight' : '';
            const priceStr = opp.price < 1 ? opp.price.toFixed(6) : opp.price.toFixed(2);
            
            return `
              <tr class="${rowClass}">
                <td><strong>${opp.symbol.replace('-PERP', '')}</strong></td>
                <td>$${priceStr}</td>
                <td class="${opp.fundingRate > 0 ? 'positive' : 'negative'}">${opp.fundingRate.toFixed(2)}%</td>
                <td class="${apyClass} ${opp.fundingApy > 0 ? 'positive' : 'negative'}">${opp.fundingApy.toFixed(0)}%</td>
                <td>${opp.direction === 'long_pays' ? '🔴 SHORT' : '🟢 LONG'}</td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    </div>
    
    <div class="card">
      <h2>🎯 DELTA-NEUTRAL STRATEGIES</h2>
      ${data.pairs.slice(0, 5).map((pair: any) => `
        <div class="pair-card">
          <div class="pair-title">${pair.strategy}</div>
          <div style="display: flex; justify-content: space-between; margin-top: 10px;">
            <div>
              <div style="color: #8b949e; font-size: 0.8em;">Long APY</div>
              <div class="negative">${pair.longApy.toFixed(0)}%</div>
            </div>
            <div>
              <div style="color: #8b949e; font-size: 0.8em;">Short APY</div>
              <div class="positive">${pair.shortApy.toFixed(0)}%</div>
            </div>
            <div>
              <div style="color: #8b949e; font-size: 0.8em;">Net APY</div>
              <div class="pair-apy">${pair.netApy.toFixed(0)}%</div>
            </div>
          </div>
        </div>
      `).join('')}
    </div>
  </div>
  
  <div class="warning">
    ⚠️ <strong>DYOR!</strong> Extreme funding rates often indicate:
    <ul style="margin-left: 20px; margin-top: 10px;">
      <li>Low liquidity - hard to enter/exit positions</li>
      <li>High volatility - liquidation risk</li>
      <li>Market manipulation - rate can flip quickly</li>
    </ul>
    Always check open interest and volume before trading.
  </div>
  
  <div class="footer">
    Data from Drift Protocol | Solana Mainnet
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
  console.log(`
╔════════════════════════════════════════════════╗
║  ⚡ DRIFT FUNDING SCANNER                       ║
║                                                ║
║  Dashboard: http://localhost:${PORT}              ║
║  API:       http://localhost:${PORT}/api/funding  ║
║                                                ║
║  Press Ctrl+C to stop                          ║
╚════════════════════════════════════════════════╝
  `);
});
