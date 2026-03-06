/**
 * IRONMAN Solana Bot — Main Entry Point
 * 
 * EDUCATIONAL PURPOSE — Learn how bots work
 * 
 * Modes:
 *   node index.js analyze   → Wallet analysis only
 *   node index.js scan      → Arbitrage scanner (no trades)
 *   node index.js watch     → Watch whale wallet
 *   node index.js paper     → Paper trading simulation
 *   node index.js learn     → Full explanation mode
 */

const { analyzeWalletPattern, watchWallet, CopyTradeSimulator, WHALE_WALLET } = require('./src/wallet_tracker');
const { scanArbitrageOpportunities, startArbitrageMonitor, explainArbitrage } = require('./src/arbitrage');
const { sendTelegram, formatArbitrageAlert, formatWhaleTrade } = require('./src/alerts');
const { getSolPrice } = require('./src/price_monitor');
const { startSniper, safetyCheck } = require('./src/sniper');
const { startCopyTrader } = require('./src/copy_trade');
const { wallet, config } = require('./src/config');

const MODE = process.argv[2] || 'learn';
const TRADE_AMOUNT = parseFloat(process.argv[3] || '0.01'); // SOL amount

console.log(`
╔═══════════════════════════════════════╗
║   IRONMAN SOLANA BOT — Educational    ║
║   Mode: ${MODE.padEnd(30)}║
╚═══════════════════════════════════════╝
`);

async function main() {
  // Current SOL price
  const solPrice = await getSolPrice();
  console.log(`[Main] SOL Price: $${solPrice.toFixed(2)}\n`);

  switch (MODE) {
    
    // ═══════════════════════════════════════
    case 'analyze':
    // Whale wallet ka full analysis
    // LEARN: Transaction patterns, bot detection
    // ═══════════════════════════════════════
      console.log('[Mode] WALLET ANALYSIS\n');
      const report = await analyzeWalletPattern(WHALE_WALLET, 20);
      
      await sendTelegram(`
<b>Whale Wallet Analysis Complete</b>

Strategy: ${report.strategy}
Avg tx gap: ${report.avgGapSec}s
Min tx gap: ${report.minGapSec}s
Is Bot: ${report.isBot ? 'YES' : 'NO'}
Total txs analyzed: ${report.totalTxs}

Top DEXes: ${JSON.stringify(report.dexUsage)}
`.trim());
      break;

    // ═══════════════════════════════════════
    case 'scan':
    // Arbitrage opportunities scan karo
    // LEARN: Price differences across DEXes
    // ═══════════════════════════════════════
      console.log('[Mode] ARBITRAGE SCANNER (Watch Only)\n');
      explainArbitrage();
      
      console.log('Starting continuous scan... Press Ctrl+C to stop\n');
      
      const monitor = await startArbitrageMonitor(8000, async (opp) => {
        console.log(`\n🔥 OPPORTUNITY: ${opp.profitPct.toFixed(3)}% profit!`);
        await sendTelegram(formatArbitrageAlert(opp));
      });
      
      // Run for 5 minutes then report
      setTimeout(async () => {
        const stats = monitor.getStats();
        console.log(`\n[Stats] Scans: ${stats.scanCount} | Opportunities found: ${stats.totalOpportunities}`);
        await sendTelegram(`Bot ran ${stats.scanCount} scans, found ${stats.totalOpportunities} opportunities`);
        monitor.stop();
        process.exit(0);
      }, 5 * 60 * 1000);
      
      // Keep alive
      await new Promise(() => {});
      break;

    // ═══════════════════════════════════════
    case 'watch':
    // Whale wallet real-time watch
    // LEARN: WebSocket monitoring, copy trading logic
    // ═══════════════════════════════════════
      console.log(`[Mode] WHALE WATCHER — ${WHALE_WALLET.slice(0,20)}...\n`);
      console.log('Watching for transactions... Press Ctrl+C to stop\n');
      
      await sendTelegram(`🐋 Whale Watch STARTED\nWatching: ${WHALE_WALLET.slice(0,20)}...`);
      
      watchWallet(WHALE_WALLET, async (tx) => {
        console.log('\n🚨 WHALE TRANSACTION DETECTED!');
        console.log(JSON.stringify(tx, null, 2));
        await sendTelegram(formatWhaleTrade(tx));
      });
      
      // Keep alive
      await new Promise(() => {});
      break;

    // ═══════════════════════════════════════
    case 'paper':
    // Paper trading — ZERO real money
    // LEARN: Copy trading logic, P&L tracking
    // ═══════════════════════════════════════
      console.log('[Mode] PAPER TRADING SIMULATION\n');
      console.log('⚠️  NO REAL MONEY — Simulation only\n');
      
      const sim = new CopyTradeSimulator(1.0); // Start with 1 SOL (fake)
      
      await sendTelegram('📊 Paper Trading Started\nSimulating copy trades with 1 SOL (fake)');
      
      // Watch whale and simulate copy trades
      watchWallet(WHALE_WALLET, async (tx) => {
        if (tx.tokenChanges.length > 0) {
          await sim.onWhaleTrade(tx);
          
          const pnl = sim.getPnL();
          console.log(`\n[PnL] Balance: ${pnl.currentBalance.toFixed(4)} SOL | P&L: ${pnl.pnlPct.toFixed(2)}%`);
          
          // Report every 10 trades
          if (pnl.trades % 10 === 0 && pnl.trades > 0) {
            await sendTelegram(`
<b>Paper Trading Update</b>
Trades: ${pnl.trades}
Balance: ${pnl.currentBalance.toFixed(4)} SOL
P&L: ${pnl.pnl >= 0 ? '+' : ''}${pnl.pnlPct.toFixed(2)}%
${pnl.pnl >= 0 ? '✅ Profitable' : '❌ Losing'}
`.trim());
          }
        }
      });
      
      // Keep alive
      await new Promise(() => {});
      break;

    // ═══════════════════════════════════════
    case 'copy':
    // Copy trade whale wallet in paper mode
    // ═══════════════════════════════════════
      console.log('[Mode] COPY TRADER — Paper Mode\n');
      
      const copyBot = await startCopyTrader({
        solPerTrade: TRADE_AMOUNT,  // e.g. 0.01 SOL
        maxPositions: 3,
        takeProfitPct: 50,
        stopLossPct: 20,
        paper: true,              // change to false for real
        startSOL: 0.5,
      });
      
      console.log('Copying whale... Press Ctrl+C to stop\n');
      await new Promise(() => {});
      break;

    // ═══════════════════════════════════════
    case 'snipe':
    // Token Sniper — new launches detect + buy
    // LEARN: WebSocket monitoring, safety checks, auto sell
    // ═══════════════════════════════════════
      console.log('[Mode] SNIPER BOT (Paper Trading)\n');
      console.log(`Trade amount: ${TRADE_AMOUNT} SOL per snipe\n`);
      console.log('⚠️  Running in PAPER mode — no real money\n');
      
      await sendTelegram(`
🎯 <b>IRONMAN Sniper Bot</b>
Mode: Paper Trading
Per snipe: ${TRADE_AMOUNT} SOL (simulated)
Watching: Raydium + Pump.fun
Safety filters: ON
`.trim());

      const sniper = await startSniper({
        solPerTrade: TRADE_AMOUNT,
        simulated: true,  // Always paper first!
        maxPositions: 3,
      });
      
      // Keep alive
      await new Promise(() => {});
      break;

    // ═══════════════════════════════════════
    case 'safety':
    // Safety check a specific token
    // LEARN: How to detect rugs before buying
    // ═══════════════════════════════════════
      const tokenToCheck = process.argv[3];
      if (!tokenToCheck) {
        console.log('Usage: node index.js safety <TOKEN_MINT_ADDRESS>');
        break;
      }
      console.log(`[Mode] SAFETY CHECK: ${tokenToCheck}\n`);
      const safety = await safetyCheck(tokenToCheck);
      console.log('\n=== SAFETY REPORT ===');
      console.log(JSON.stringify(safety, null, 2));
      if (safety.passed) {
        console.log('\n✅ Token passed safety checks');
      } else {
        console.log('\n❌ Token FAILED — DO NOT BUY');
        console.log('Reasons:', safety.reasons.join('\n - '));
      }
      break;

    // ═══════════════════════════════════════
    case 'learn':
    default:
    // Learning mode — sab explain karo
    // ═══════════════════════════════════════
      console.log('[Mode] LEARNING MODE\n');
      
      explainArbitrage();
      
      console.log('\n[Learning] Quick arbitrage scan (1 round)...\n');
      const opps = await scanArbitrageOpportunities(0.01, 0.1);
      
      console.log(`\n[Learning] Found ${opps.length} opportunities above 0.1% threshold`);
      
      if (opps.length > 0) {
        console.log('\nBest opportunity:');
        console.log(JSON.stringify(opps[0], null, 2));
      }
      
      console.log('\n[Learning] Quick whale analysis...\n');
      await analyzeWalletPattern(WHALE_WALLET, 10);
      
      console.log(`
═══════════════════════════════════════
NEXT STEPS TO LEARN:
═══════════════════════════════════════
1. node index.js scan    → Live arbitrage scanning
2. node index.js watch   → Watch whale in real-time  
3. node index.js analyze → Deep wallet analysis
4. node index.js paper   → Simulate copy trading

ADD YOUR WALLET to .env to enable:
→ Real execution (start with tiny amounts!)
→ Actual P&L tracking
═══════════════════════════════════════
`);

      await sendTelegram(`
<b>IRONMAN Bot Learning Session Complete!</b>

SOL Price: $${solPrice.toFixed(2)}
Arb opportunities (>0.1%): ${opps.length}
Whale strategy: Confirmed BOT

Bot is ready. Add private key to .env for real trading.
`.trim());
      break;
  }
}

main().catch(console.error);
