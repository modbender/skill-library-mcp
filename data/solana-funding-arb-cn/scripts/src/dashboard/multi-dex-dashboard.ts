/**
 * Multi-DEX Funding Rate Dashboard
 * Compares Drift vs Flash Trade
 */

import express from 'express';
import { MultiDexAggregator } from '../core/multi-dex-aggregator';

const app = express();
const PORT = process.env.PORT || 3456;
const aggregator = new MultiDexAggregator();

let cache: { data: any; timestamp: number } | null = null;
const CACHE_TTL = 30000;

async function getData() {
  if (cache && Date.now() - cache.timestamp < CACHE_TTL) {
    return cache.data;
  }
  
  const [driftRates, flashRates, opportunities] = await Promise.all([
    aggregator.getDriftRates(),
    aggregator.getFlashTradeRates(),
    aggregator.findCrossExchangeArbitrage(5),
  ]);
  
  // Build comparison table
  const driftMap = new Map(driftRates.map(r => [r.symbol, r]));
  const flashMap = new Map(flashRates.map(r => [r.symbol, r]));
  const allSymbols = new Set([...driftMap.keys(), ...flashMap.keys()]);
  
  const comparison = Array.from(allSymbols).map(symbol => {
    const drift = driftMap.get(symbol);
    const flash = flashMap.get(symbol);
    const spread = drift && flash ? Math.abs(drift.fundingRateApy - flash.fundingRateApy) : 0;
    
    return {
      symbol,
      drift: drift || null,
      flash: flash || null,
      spread,
      hasArb: spread > 50,
    };
  }).filter(c => c.drift || c.flash)
    .sort((a, b) => b.spread - a.spread);
  
  cache = {
    data: { 
      driftRates, 
      flashRates, 
      opportunities, 
      comparison,
      stats: {
        driftCount: driftRates.length,
        flashCount: flashRates.length,
        commonCount: comparison.filter(c => c.drift && c.flash).length,
        arbCount: opportunities.length,
      },
      lastUpdate: new Date().toISOString() 
    },
    timestamp: Date.now(),
  };
  
  return cache.data;
}

app.get('/api/rates', async (req, res) => {
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
  <title>⚡ Solana DEX Arb Scanner</title>
  <meta http-equiv="refresh" content="30">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { 
      font-family: 'JetBrains Mono', monospace;
      background: #0d1117;
      color: #e6edf3;
      padding: 20px;
    }
    .header { text-align: center; margin-bottom: 20px; }
    h1 { color: #58a6ff; }
    .stats { 
      display: flex; gap: 20px; justify-content: center; 
      margin: 15px 0;
    }
    .stat { 
      background: #161b22; 
      padding: 10px 20px; 
      border-radius: 8px;
      border: 1px solid #30363d;
    }
    .stat-value { font-size: 1.5em; color: #3fb950; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    @media (max-width: 1200px) { .grid { grid-template-columns: 1fr; } }
    .card { 
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 12px;
      padding: 15px;
    }
    .card h2 { color: #58a6ff; margin-bottom: 10px; font-size: 1em; }
    table { width: 100%; border-collapse: collapse; font-size: 0.8em; }
    th { color: #8b949e; text-align: left; padding: 8px 4px; }
    td { padding: 6px 4px; border-bottom: 1px solid #21262d; }
    .positive { color: #3fb950; }
    .negative { color: #f85149; }
    .neutral { color: #8b949e; }
    .arb-card {
      background: linear-gradient(135deg, rgba(35, 134, 54, 0.2), rgba(22, 27, 34, 0.9));
      border-color: #238636;
      padding: 12px;
      margin-bottom: 8px;
      border-radius: 8px;
    }
    .arb-title { color: #3fb950; font-weight: bold; }
    .arb-spread { font-size: 1.3em; color: #f0883e; }
    .small { font-size: 0.75em; color: #8b949e; }
    .badge {
      display: inline-block;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 0.7em;
    }
    .drift { background: #1f6feb; }
    .flash { background: #a371f7; }
  </style>
</head>
<body>
  <div class="header">
    <h1>⚡ SOLANA DEX ARBITRAGE SCANNER</h1>
    <p class="small">Drift Protocol vs Flash Trade | Auto-refresh: 30s</p>
  </div>
  
  <div class="stats">
    <div class="stat">
      <div class="small">Drift Markets</div>
      <div class="stat-value">${data.stats.driftCount}</div>
    </div>
    <div class="stat">
      <div class="small">Flash Markets</div>
      <div class="stat-value">${data.stats.flashCount}</div>
    </div>
    <div class="stat">
      <div class="small">Common</div>
      <div class="stat-value">${data.stats.commonCount}</div>
    </div>
    <div class="stat">
      <div class="small">Arb Opps</div>
      <div class="stat-value">${data.stats.arbCount}</div>
    </div>
  </div>
  
  <div class="grid">
    <div class="card">
      <h2>🎯 TOP ARBITRAGE OPPORTUNITIES</h2>
      ${data.opportunities.length === 0 ? '<p class="neutral">No significant opportunities found</p>' : ''}
      ${data.opportunities.slice(0, 6).map((opp: any) => `
        <div class="arb-card">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="arb-title">${opp.symbol}</span>
            <span class="arb-spread">${opp.spreadApy.toFixed(0)}% spread</span>
          </div>
          <div style="margin-top: 8px; font-size: 0.85em;">
            <div class="positive">📈 Long <span class="badge ${opp.longExchange.toLowerCase()}">${opp.longExchange}</span> @ ${opp.longRate.fundingRateApy.toFixed(0)}%</div>
            <div class="negative">📉 Short <span class="badge ${opp.shortExchange.toLowerCase()}">${opp.shortExchange}</span> @ ${opp.shortRate.fundingRateApy.toFixed(0)}%</div>
          </div>
          <div class="small" style="margin-top: 5px;">Est. Net APY: ${opp.netApy.toFixed(0)}%</div>
        </div>
      `).join('')}
    </div>
    
    <div class="card">
      <h2>📊 FUNDING RATE COMPARISON</h2>
      <table>
        <thead>
          <tr>
            <th>Symbol</th>
            <th><span class="badge drift">Drift</span></th>
            <th><span class="badge flash">Flash</span></th>
            <th>Spread</th>
          </tr>
        </thead>
        <tbody>
          ${data.comparison.filter((c: any) => c.drift && c.flash).slice(0, 15).map((c: any) => {
            const driftClass = c.drift?.fundingRateApy > 0 ? 'positive' : 'negative';
            const flashClass = c.flash?.fundingRateApy > 0 ? 'positive' : 'negative';
            return `
              <tr>
                <td><strong>${c.symbol}</strong></td>
                <td class="${driftClass}">${c.drift ? c.drift.fundingRateApy.toFixed(0) + '%' : '-'}</td>
                <td class="${flashClass}">${c.flash ? c.flash.fundingRateApy.toFixed(0) + '%' : '-'}</td>
                <td style="color: ${c.spread > 100 ? '#f0883e' : '#8b949e'}">${c.spread.toFixed(0)}%</td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    </div>
  </div>
  
  <div class="card" style="margin-top: 20px;">
    <h2>ℹ️ How It Works</h2>
    <ul style="margin-left: 20px; font-size: 0.85em; color: #8b949e;">
      <li><strong>Positive Rate (🔴):</strong> Longs pay shorts - SHORT to receive funding</li>
      <li><strong>Negative Rate (🟢):</strong> Shorts pay longs - LONG to receive funding</li>
      <li><strong>Strategy:</strong> Long where rate is negative/low, Short where rate is positive/high</li>
      <li><strong>Risk:</strong> Price divergence, execution, liquidation, funding rate changes</li>
    </ul>
  </div>
  
  <p class="small" style="text-align: center; margin-top: 15px;">
    ${data.lastUpdate} | Data from Drift Protocol & Flash Trade (CoinGecko)
  </p>
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
╔═══════════════════════════════════════════════════════╗
║  ⚡ SOLANA DEX ARBITRAGE SCANNER                       ║
║                                                       ║
║  Comparing: Drift Protocol vs Flash Trade             ║
║                                                       ║
║  Dashboard: http://localhost:${PORT}                      ║
║  API:       http://localhost:${PORT}/api/rates            ║
║                                                       ║
║  Press Ctrl+C to stop                                 ║
╚═══════════════════════════════════════════════════════╝
  `);
});
