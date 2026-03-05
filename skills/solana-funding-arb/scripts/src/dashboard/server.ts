/**
 * SolArb Dashboard Server
 * 
 * Real-time web dashboard for monitoring funding rates and positions.
 */

import express from 'express';
import { createServer } from 'http';
import { WebSocket, WebSocketServer } from 'ws';
import { Connection } from '@solana/web3.js';
import { DriftProtocol } from '../protocols/drift';
import { JupiterPerps } from '../protocols/jupiter-perps';
import { ZetaMarkets } from '../protocols/zeta';
import { FlashTrade } from '../protocols/flash';
import { MangoMarkets } from '../protocols/mango';
import { GooseFX } from '../protocols/goosefx';
import { ParclProtocol } from '../protocols/parcl';
import { PnLTracker } from '../core/pnl-tracker';
import { findArbOpportunities, formatOpportunity } from '../core/cross-protocol-arb';
import path from 'path';

const PORT = process.env.PORT || 3000;
const IS_DEVNET = process.env.DRIFT_NETWORK !== 'mainnet';
const RPC_URL = process.env.SOLANA_RPC || (IS_DEVNET 
  ? 'https://api.devnet.solana.com'
  : 'https://api.mainnet-beta.solana.com');

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server });

// Initialize services
const connection = new Connection(RPC_URL, 'confirmed');
const drift = new DriftProtocol(connection);
const jupiterPerps = new JupiterPerps(connection);
const zeta = new ZetaMarkets(connection);
const flash = new FlashTrade(connection);
const mango = new MangoMarkets(connection);
const goose = new GooseFX(connection);
const parcl = new ParclProtocol(connection);
const pnlTracker = new PnLTracker();

// All protocols
const protocols = [
  { name: 'Drift', instance: drift },
  { name: 'Jupiter', instance: jupiterPerps },
  { name: 'Zeta', instance: zeta },
  { name: 'Flash', instance: flash },
  { name: 'Mango', instance: mango },
  { name: 'GooseFX', instance: goose },
  { name: 'Parcl', instance: parcl },
];

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// API Routes
app.get('/api/funding-rates', async (req, res) => {
  try {
    // Fetch from all protocols in parallel
    const [driftRates, jupRates, zetaRates, flashRates, mangoRates, gooseRates, parclRates] = 
      await Promise.all([
        drift.getFundingRates(),
        jupiterPerps.getFundingRates(),
        zeta.getFundingRates(),
        flash.getFundingRates(),
        mango.getFundingRates(),
        goose.getFundingRates(),
        parcl.getFundingRates(),
      ]);
    
    // Combine and add protocol label
    const allRates = [
      ...driftRates.map(r => ({ ...r, protocol: 'Drift', market: `DRIFT:${r.market}` })),
      ...jupRates.map(r => ({ ...r, protocol: 'Jupiter' })),
      ...zetaRates.map(r => ({ ...r, protocol: 'Zeta' })),
      ...flashRates.map(r => ({ ...r, protocol: 'Flash' })),
      ...mangoRates.map(r => ({ ...r, protocol: 'Mango' })),
      ...gooseRates.map(r => ({ ...r, protocol: 'GooseFX' })),
      ...parclRates.map(r => ({ ...r, protocol: 'Parcl' })),
    ];
    
    // Sort by APY (highest first)
    allRates.sort((a, b) => Math.abs(b.fundingRateApy) - Math.abs(a.fundingRateApy));
    
    res.json({ 
      success: true, 
      rates: allRates,
      protocols: protocols.length,
      totalMarkets: allRates.length
    });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.get('/api/arb-opportunities', async (req, res) => {
  try {
    // Fetch from all protocols
    const [driftRates, jupRates, zetaRates, flashRates, mangoRates, gooseRates, parclRates] = 
      await Promise.all([
        drift.getFundingRates(),
        jupiterPerps.getFundingRates(),
        zeta.getFundingRates(),
        flash.getFundingRates(),
        mango.getFundingRates(),
        goose.getFundingRates(),
        parcl.getFundingRates(),
      ]);
    
    const allRates = [
      ...driftRates.map(r => ({ ...r, protocol: 'Drift', market: `DRIFT:${r.market}` })),
      ...jupRates.map(r => ({ ...r, protocol: 'Jupiter' })),
      ...zetaRates.map(r => ({ ...r, protocol: 'Zeta' })),
      ...flashRates.map(r => ({ ...r, protocol: 'Flash' })),
      ...mangoRates.map(r => ({ ...r, protocol: 'Mango' })),
      ...gooseRates.map(r => ({ ...r, protocol: 'GooseFX' })),
      ...parclRates.map(r => ({ ...r, protocol: 'Parcl' })),
    ];
    
    // Find arbitrage opportunities
    const opportunities = findArbOpportunities(allRates as any);
    
    res.json({ 
      success: true, 
      opportunities,
      formatted: opportunities.map(formatOpportunity),
      count: opportunities.length
    });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.get('/api/markets', async (req, res) => {
  try {
    const markets = await drift.getMarkets();
    res.json({ success: true, markets });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.get('/api/pnl', (req, res) => {
  try {
    const stats = pnlTracker.getStats();
    const recent = pnlTracker.getRecentTrades(20);
    res.json({ success: true, stats, recentTrades: recent });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.get('/api/status', (req, res) => {
  res.json({
    success: true,
    status: {
      uptime: process.uptime(),
      rpc: RPC_URL.slice(0, 30) + '...',
      timestamp: Date.now()
    }
  });
});

// Serve main dashboard
app.get('/', (req, res) => {
  res.send(getDashboardHTML());
});

// WebSocket for real-time updates
wss.on('connection', (ws) => {
  console.log('Dashboard client connected');
  
  // Send initial data
  sendUpdate(ws);
  
  // Send updates every 30 seconds
  const interval = setInterval(() => sendUpdate(ws), 30000);
  
  ws.on('close', () => {
    clearInterval(interval);
    console.log('Dashboard client disconnected');
  });
});

async function sendUpdate(ws: WebSocket) {
  try {
    // Fetch from all protocols
    const [driftRates, jupRates, zetaRates, flashRates, mangoRates, gooseRates, parclRates] = 
      await Promise.all([
        drift.getFundingRates(),
        jupiterPerps.getFundingRates(),
        zeta.getFundingRates(),
        flash.getFundingRates(),
        mango.getFundingRates(),
        goose.getFundingRates(),
        parcl.getFundingRates(),
      ]);
    
    const allRates = [
      ...driftRates.map(r => ({ ...r, protocol: 'Drift', market: `DRIFT:${r.market}` })),
      ...jupRates.map(r => ({ ...r, protocol: 'Jupiter' })),
      ...zetaRates.map(r => ({ ...r, protocol: 'Zeta' })),
      ...flashRates.map(r => ({ ...r, protocol: 'Flash' })),
      ...mangoRates.map(r => ({ ...r, protocol: 'Mango' })),
      ...gooseRates.map(r => ({ ...r, protocol: 'GooseFX' })),
      ...parclRates.map(r => ({ ...r, protocol: 'Parcl' })),
    ];
    
    allRates.sort((a, b) => Math.abs(b.fundingRateApy) - Math.abs(a.fundingRateApy));
    
    const stats = pnlTracker.getStats();
    
    ws.send(JSON.stringify({
      type: 'update',
      data: { 
        rates: allRates.slice(0, 30), 
        stats,
        protocols: protocols.length,
        totalMarkets: allRates.length
      }
    }));
  } catch (error) {
    // Ignore errors
  }
}

function getDashboardHTML(): string {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SolArb - Funding Rate Arbitrage</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Segoe UI', system-ui, sans-serif;
      background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 100%);
      color: #e0e0e0;
      min-height: 100vh;
    }
    .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
    
    header {
      text-align: center;
      padding: 40px 20px;
      border-bottom: 1px solid #333;
    }
    header h1 {
      font-size: 2.5rem;
      background: linear-gradient(90deg, #00d4ff, #7b2cbf);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 10px;
    }
    header p { color: #888; }
    
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin: 30px 0;
    }
    .stat-card {
      background: rgba(255,255,255,0.05);
      border: 1px solid #333;
      border-radius: 12px;
      padding: 20px;
      text-align: center;
    }
    .stat-card h3 { color: #888; font-size: 0.9rem; margin-bottom: 10px; }
    .stat-card .value { font-size: 2rem; font-weight: bold; }
    .stat-card .value.positive { color: #00ff88; }
    .stat-card .value.negative { color: #ff4444; }
    
    .section { margin: 40px 0; }
    .section h2 {
      font-size: 1.5rem;
      margin-bottom: 20px;
      padding-bottom: 10px;
      border-bottom: 2px solid #7b2cbf;
    }
    
    table {
      width: 100%;
      border-collapse: collapse;
      background: rgba(255,255,255,0.02);
      border-radius: 12px;
      overflow: hidden;
    }
    th, td {
      padding: 15px;
      text-align: left;
      border-bottom: 1px solid #333;
    }
    th { background: rgba(123, 44, 191, 0.2); color: #7b2cbf; }
    tr:hover { background: rgba(255,255,255,0.05); }
    
    .positive { color: #00ff88; }
    .negative { color: #ff4444; }
    .neutral { color: #888; }
    
    .badge {
      display: inline-block;
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: bold;
    }
    .badge.long { background: rgba(0, 255, 136, 0.2); color: #00ff88; }
    .badge.short { background: rgba(255, 68, 68, 0.2); color: #ff4444; }
    
    .opportunity {
      background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(123, 44, 191, 0.1));
      border: 1px solid #7b2cbf;
    }
    
    .arb-card {
      background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(123, 44, 191, 0.1));
      border: 1px solid #7b2cbf;
      border-radius: 12px;
      padding: 20px;
    }
    .arb-card.low { border-color: #00ff88; }
    .arb-card.medium { border-color: #ffaa00; }
    .arb-card.high { border-color: #ff4444; }
    .arb-card h3 { 
      font-size: 1.3rem; 
      margin-bottom: 15px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .arb-card .apy { color: #00ff88; font-size: 1.5rem; }
    .arb-card .leg {
      padding: 10px;
      background: rgba(0,0,0,0.3);
      border-radius: 8px;
      margin: 8px 0;
    }
    .arb-card .leg.long { border-left: 3px solid #00ff88; }
    .arb-card .leg.short { border-left: 3px solid #ff4444; }
    .arb-card .risk { 
      font-size: 0.8rem; 
      padding: 4px 10px; 
      border-radius: 12px;
    }
    .arb-card .risk.low { background: rgba(0,255,136,0.2); color: #00ff88; }
    .arb-card .risk.medium { background: rgba(255,170,0,0.2); color: #ffaa00; }
    .arb-card .risk.high { background: rgba(255,68,68,0.2); color: #ff4444; }
    
    .execute-btn {
      width: 100%;
      padding: 12px;
      margin-top: 15px;
      background: linear-gradient(90deg, #00d4ff, #7b2cbf);
      border: none;
      border-radius: 8px;
      color: white;
      font-weight: bold;
      cursor: pointer;
      font-size: 1rem;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .execute-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 20px rgba(123, 44, 191, 0.4);
    }
    .execute-btn:disabled {
      background: #444;
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }
    
    .wallet-modal {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.8);
      z-index: 1000;
      justify-content: center;
      align-items: center;
    }
    .wallet-modal.show { display: flex; }
    .wallet-modal-content {
      background: #1a1a2e;
      border: 1px solid #333;
      border-radius: 16px;
      padding: 30px;
      max-width: 400px;
      text-align: center;
    }
    .wallet-option {
      display: flex;
      align-items: center;
      gap: 15px;
      padding: 15px;
      margin: 10px 0;
      background: rgba(255,255,255,0.05);
      border: 1px solid #333;
      border-radius: 12px;
      cursor: pointer;
      transition: border-color 0.2s;
    }
    .wallet-option:hover { border-color: #7b2cbf; }
    
    #loading {
      text-align: center;
      padding: 40px;
      color: #888;
    }
    
    .refresh-indicator {
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 10px 20px;
      background: rgba(0,0,0,0.8);
      border-radius: 20px;
      font-size: 0.8rem;
    }
    .refresh-indicator.connected { color: #00ff88; }
    .refresh-indicator.disconnected { color: #ff4444; }
    
    footer {
      text-align: center;
      padding: 40px;
      color: #666;
      border-top: 1px solid #333;
      margin-top: 40px;
    }
  </style>
</head>
<body>
  <div class="refresh-indicator" id="status">Connecting...</div>
  
  <header>
    <h1>⚡ SolArb</h1>
    <p>Funding Rate Arbitrage Agent for Solana</p>
  </header>
  
  <!-- Mock Data Banner -->
  <div id="mock-banner" style="
    background: linear-gradient(90deg, #ff6b35, #f7931a);
    padding: 15px 20px;
    text-align: center;
    font-weight: bold;
  ">
    ⚠️ DEMO MODE - Mock Data | 
    <span style="font-weight:normal">Connect wallet for live trading →</span>
    <button id="connect-wallet" style="
      background: #fff;
      color: #000;
      border: none;
      padding: 8px 20px;
      border-radius: 20px;
      margin-left: 15px;
      cursor: pointer;
      font-weight: bold;
    ">🔗 Connect Wallet</button>
  </div>
  
  <div class="container">
    <div class="stats-grid" id="stats">
      <div class="stat-card">
        <h3>Daily P&L</h3>
        <div class="value" id="daily-pnl">$0.00</div>
      </div>
      <div class="stat-card">
        <h3>Weekly P&L</h3>
        <div class="value" id="weekly-pnl">$0.00</div>
      </div>
      <div class="stat-card">
        <h3>Monthly P&L</h3>
        <div class="value" id="monthly-pnl">$0.00</div>
      </div>
      <div class="stat-card">
        <h3>Total Trades</h3>
        <div class="value" id="total-trades">0</div>
      </div>
    </div>
    
    <div class="section">
      <h2>🔥 Cross-Protocol Arbitrage</h2>
      <div id="arb-loading">Finding arbitrage opportunities...</div>
      <div id="arb-cards" style="display:none; display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;"></div>
    </div>

    <div class="section">
      <h2>🎯 Funding Rate Opportunities</h2>
      <div id="loading">Loading funding rates...</div>
      <table id="rates-table" style="display:none;">
        <thead>
          <tr>
            <th>Protocol</th>
            <th>Market</th>
            <th>Funding Rate</th>
            <th>APY</th>
            <th>Direction</th>
            <th>Strategy</th>
          </tr>
        </thead>
        <tbody id="rates-body"></tbody>
      </table>
    </div>
  </div>
  
  <footer>
    <p>Built for Colosseum Agent Hackathon 2026</p>
    <p style="margin-top: 10px;">
      <a href="https://github.com/Zedit42/solarb" style="color: #7b2cbf;">GitHub</a> •
      <a href="https://drift.trade" style="color: #7b2cbf;">Drift Protocol</a>
    </p>
  </footer>
  
  <script>
    const ws = new WebSocket(\`ws://\${window.location.host}\`);
    const statusEl = document.getElementById('status');
    
    ws.onopen = () => {
      statusEl.textContent = '🟢 Live';
      statusEl.className = 'refresh-indicator connected';
    };
    
    ws.onclose = () => {
      statusEl.textContent = '🔴 Disconnected';
      statusEl.className = 'refresh-indicator disconnected';
    };
    
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === 'update') {
        updateDashboard(msg.data);
      }
    };
    
    function updateDashboard(data) {
      // Update stats
      if (data.stats) {
        updateStat('daily-pnl', data.stats.daily.profitUsd);
        updateStat('weekly-pnl', data.stats.weekly.profitUsd);
        updateStat('monthly-pnl', data.stats.monthly.profitUsd);
        document.getElementById('total-trades').textContent = data.stats.allTime.trades;
      }
      
      // Update rates table
      if (data.rates && data.rates.length > 0) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('rates-table').style.display = 'table';
        
        const tbody = document.getElementById('rates-body');
        tbody.innerHTML = data.rates.map(rate => {
          const isOpportunity = Math.abs(rate.fundingRateApy) >= 100;
          const strategy = rate.longPayShort ? 'SHORT' : 'LONG';
          
          return \`
            <tr class="\${isOpportunity ? 'opportunity' : ''}">
              <td><span style="color:#7b2cbf">\${rate.protocol || 'Drift'}</span></td>
              <td><strong>\${rate.market}</strong></td>
              <td>\${(rate.fundingRate * 100).toFixed(4)}%/hr</td>
              <td class="\${rate.fundingRateApy > 0 ? 'positive' : 'negative'}">
                \${rate.fundingRateApy > 0 ? '+' : ''}\${rate.fundingRateApy.toFixed(1)}%
              </td>
              <td>
                <span class="badge \${rate.longPayShort ? 'short' : 'long'}">
                  \${rate.longPayShort ? 'L→S' : 'S→L'}
                </span>
              </td>
              <td>\${strategy}</td>
            </tr>
          \`;
        }).join('');
      }
    }
    
    function updateStat(id, value) {
      const el = document.getElementById(id);
      const formatted = value >= 0 ? '+$' + value.toFixed(2) : '-$' + Math.abs(value).toFixed(2);
      el.textContent = formatted;
      el.className = 'value ' + (value >= 0 ? 'positive' : 'negative');
    }
    
    // Fetch arb opportunities
    function loadArbOpportunities() {
      fetch('/api/arb-opportunities')
        .then(r => r.json())
        .then(data => {
          if (data.success && data.opportunities.length > 0) {
            document.getElementById('arb-loading').style.display = 'none';
            const container = document.getElementById('arb-cards');
            container.style.display = 'grid';
            
            container.innerHTML = data.opportunities.slice(0, 6).map((opp, i) => \`
              <div class="arb-card \${opp.riskLevel}">
                <h3>
                  <span>\${opp.asset}</span>
                  <span class="apy">\${opp.netApy.toFixed(0)}% APY</span>
                </h3>
                <div class="leg long">
                  <strong>📈 LONG</strong> on \${opp.longProtocol}<br>
                  <small>\${opp.longMarket} @ \${(opp.longRate * 100).toFixed(4)}%/hr</small>
                </div>
                <div class="leg short">
                  <strong>📉 SHORT</strong> on \${opp.shortProtocol}<br>
                  <small>\${opp.shortMarket} @ \${(opp.shortRate * 100).toFixed(4)}%/hr</small>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:15px;">
                  <span>Spread: \${opp.spreadApy.toFixed(0)}%</span>
                  <span class="risk \${opp.riskLevel}">\${opp.riskLevel.toUpperCase()}</span>
                </div>
                <button class="execute-btn" onclick="executeArb('\${opp.asset}', '\${opp.longProtocol}', '\${opp.shortProtocol}')" \${!window.walletConnected ? 'disabled' : ''}>
                  \${window.walletConnected ? '⚡ Execute Trade' : '🔒 Connect Wallet First'}
                </button>
              </div>
            \`).join('');
          }
        });
    }
    
    // Initial fetch
    fetch('/api/funding-rates')
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          updateDashboard({ rates: data.rates, stats: { daily: {profitUsd: 0}, weekly: {profitUsd: 0}, monthly: {profitUsd: 0}, allTime: {trades: 0} } });
        }
      });
    
    loadArbOpportunities();
    setInterval(loadArbOpportunities, 30000);
    
    // Wallet connection
    window.walletConnected = false;
    
    document.getElementById('connect-wallet').addEventListener('click', () => {
      document.getElementById('wallet-modal').classList.add('show');
    });
    
    function closeModal() {
      document.getElementById('wallet-modal').classList.remove('show');
    }
    
    async function connectWallet(type) {
      try {
        if (type === 'phantom' && window.solana) {
          await window.solana.connect();
          window.walletConnected = true;
          window.walletAddress = window.solana.publicKey.toString();
        } else if (type === 'solflare' && window.solflare) {
          await window.solflare.connect();
          window.walletConnected = true;
          window.walletAddress = window.solflare.publicKey.toString();
        } else {
          alert('Please install ' + type.charAt(0).toUpperCase() + type.slice(1) + ' wallet extension');
          return;
        }
        
        closeModal();
        document.getElementById('mock-banner').innerHTML = \`
          ✅ Connected: \${window.walletAddress.slice(0,4)}...\${window.walletAddress.slice(-4)} | 
          <span style="color:#00ff88">Live Trading Enabled</span>
          <button onclick="disconnectWallet()" style="
            background: #ff4444;
            color: #fff;
            border: none;
            padding: 8px 15px;
            border-radius: 20px;
            margin-left: 15px;
            cursor: pointer;
          ">Disconnect</button>
        \`;
        document.getElementById('mock-banner').style.background = 'linear-gradient(90deg, #00ff88, #00d4ff)';
        document.getElementById('mock-banner').style.color = '#000';
        
        // Refresh arb cards to enable buttons
        loadArbOpportunities();
      } catch (err) {
        alert('Connection failed: ' + err.message);
      }
    }
    
    function disconnectWallet() {
      window.walletConnected = false;
      window.walletAddress = null;
      location.reload();
    }
    
    async function executeArb(asset, longProtocol, shortProtocol) {
      if (!window.walletConnected) {
        document.getElementById('wallet-modal').classList.add('show');
        return;
      }
      
      const confirmed = confirm(\`Execute \${asset} arbitrage?\\n\\nLONG on \${longProtocol}\\nSHORT on \${shortProtocol}\\n\\nThis will open positions on both protocols.\`);
      
      if (confirmed) {
        // TODO: Integrate with actual protocol SDKs
        alert(\`🚧 Coming Soon!\\n\\nThis will:\\n1. Open LONG \${asset} on \${longProtocol}\\n2. Open SHORT \${asset} on \${shortProtocol}\\n\\nSDK integration in progress...\`);
      }
    }
  </script>
  
  <!-- Wallet Modal -->
  <div id="wallet-modal" class="wallet-modal" onclick="if(event.target === this) closeModal()">
    <div class="wallet-modal-content">
      <h2 style="margin-bottom:20px">Connect Wallet</h2>
      <p style="color:#888; margin-bottom:20px">Select a wallet to enable live trading</p>
      
      <div class="wallet-option" onclick="connectWallet('phantom')">
        <img src="https://phantom.app/img/phantom-icon-purple.svg" width="40" height="40" alt="Phantom">
        <span>Phantom</span>
      </div>
      
      <div class="wallet-option" onclick="connectWallet('solflare')">
        <img src="https://solflare.com/assets/logo.svg" width="40" height="40" alt="Solflare">
        <span>Solflare</span>
      </div>
      
      <button onclick="closeModal()" style="
        margin-top: 20px;
        padding: 10px 30px;
        background: transparent;
        border: 1px solid #666;
        color: #888;
        border-radius: 8px;
        cursor: pointer;
      ">Cancel</button>
    </div>
  </div>
</body>
</html>
  `;
}

// Start server
server.listen(PORT, () => {
  console.log(`
==========================================================
           SolArb Dashboard Server                        
==========================================================
  Dashboard: http://localhost:${PORT}
  WebSocket: ws://localhost:${PORT}
  API: http://localhost:${PORT}/api/funding-rates
==========================================================
  `);
});
