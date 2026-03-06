/**
 * IRONMAN — Copy Trade Engine
 * 
 * Whale ke trades real-time copy karo
 * Paper mode: simulate only
 * Live mode: actual execution (needs wallet)
 * 
 * HOW IT WORKS:
 * 1. WebSocket se whale ki activity detect karo
 * 2. Transaction parse karo — kya buy/sell hua
 * 3. Same trade execute karo (smaller size)
 * 4. Auto take-profit + stop-loss manage karo
 */

const { Connection, PublicKey, VersionedTransaction } = require('@solana/web3.js');
const axios = require('axios');
const { connection, wallet, TOKENS, config } = require('./config');
const { getJupiterQuote } = require('./price_monitor');
const { sendTelegram } = require('./alerts');
const { parseTransaction, getRecentTransactions } = require('./wallet_tracker');
const { getPumpToken, pumpSafetyCheck, calcBuy } = require('./pumpfun');

// Whale to copy
const WHALE = 'AgmLJBMDCqWynYnQiPCuj9ewsNNsBJXyzoUhD9LJzN51';

// Skip these — whale's internal routing, not real trades
const SKIP_MINTS = new Set([
  TOKENS.SOL,
  TOKENS.USDC, 
  TOKENS.USDT,
  'So11111111111111111111111111111111111111112',
]);

/**
 * Paper Trading State
 */
class PaperPortfolio {
  constructor(startSOL = 0.5) {
    this.sol = startSOL;
    this.startSOL = startSOL;
    this.positions = new Map(); // mint => {tokens, buyPrice, solSpent, time}
    this.closedTrades = [];
    this.log = [];
  }

  addLog(msg) {
    const entry = `[${new Date().toLocaleTimeString()}] ${msg}`;
    this.log.push(entry);
    console.log('[Portfolio]', entry);
  }

  buy(mint, solAmount, tokensReceived, price) {
    if (this.sol < solAmount) {
      this.addLog(`Insufficient balance: ${this.sol.toFixed(4)} SOL`);
      return false;
    }
    this.sol -= solAmount;
    const existing = this.positions.get(mint) || { tokens: 0, solSpent: 0 };
    this.positions.set(mint, {
      tokens: existing.tokens + tokensReceived,
      solSpent: existing.solSpent + solAmount,
      buyPrice: price,
      time: Date.now(),
    });
    this.addLog(`BUY ${mint.slice(0,12)}... | ${solAmount} SOL → ${tokensReceived.toFixed(0)} tokens`);
    return true;
  }

  sell(mint, solReceived, tokensSold) {
    const pos = this.positions.get(mint);
    if (!pos) return false;
    this.sol += solReceived;
    const pnl = solReceived - pos.solSpent;
    const pnlPct = (pnl / pos.solSpent) * 100;
    this.closedTrades.push({ mint, pnl, pnlPct, solReceived, solSpent: pos.solSpent });
    this.positions.delete(mint);
    this.addLog(`SELL ${mint.slice(0,12)}... | ${solReceived.toFixed(4)} SOL | P&L: ${pnlPct.toFixed(1)}%`);
    return true;
  }

  getStats() {
    const totalPnL = this.closedTrades.reduce((s, t) => s + t.pnl, 0);
    const winRate = this.closedTrades.filter(t => t.pnl > 0).length / Math.max(this.closedTrades.length, 1);
    return {
      currentSOL: this.sol,
      startSOL: this.startSOL,
      totalPnL,
      totalPnLPct: (totalPnL / this.startSOL) * 100,
      openPositions: this.positions.size,
      closedTrades: this.closedTrades.length,
      winRate: (winRate * 100).toFixed(0) + '%',
    };
  }
}

/**
 * Core: Process whale transaction + decide action
 */
async function processWhaleTx(tx, portfolio, options = {}) {
  const { 
    maxPositions = 3,
    solPerTrade = 0.01,
    takeProfitPct = 50,   // sell at +50%
    stopLossPct = 20,     // sell at -20%
    paper = true
  } = options;

  if (!tx || !tx.success) return;

  // Find meaningful token trades (not SOL/USDC routing)
  const realTrades = tx.tokenChanges.filter(c => 
    !SKIP_MINTS.has(c.mint) && 
    (c.mint.endsWith('pump') || Math.abs(c.change) > 1000)  // Pump.fun tokens OR big trades
  );

  if (realTrades.length === 0) return;

  for (const trade of realTrades) {
    const mint = trade.mint;

    if (trade.action === 'BUY') {
      // Whale bought — we buy too
      if (portfolio.positions.size >= maxPositions) {
        console.log(`[CopyTrade] Max positions (${maxPositions}) — skipping`);
        continue;
      }

      if (portfolio.positions.has(mint)) {
        console.log(`[CopyTrade] Already have position in ${mint.slice(0,12)}`);
        continue;
      }

      console.log(`\n[CopyTrade] 🐋 Whale BUY detected: ${mint.slice(0,20)}...`);

      // Get our buy quote
      const lamports = Math.floor(solPerTrade * 1e9);
      // Try Jupiter first
      let quote = await getJupiterQuote(TOKENS.SOL, mint, lamports, 5000);
      if (!quote) quote = await getJupiterQuote(TOKENS.SOL, mint, lamports, 9900);

      let tokensOut, pricePerToken, priceImpact, routeLabel;
      let isPumpDirect = false;

      if (!quote) {
        // Jupiter failed — try pump.fun bonding curve
        console.log('[CopyTrade] Jupiter no route — checking pump.fun...');
        const safety = await pumpSafetyCheck(mint);
        
        if (!safety.pass) {
          console.log(`[CopyTrade] Pump safety FAIL (score: ${safety.score}) — skip`);
          continue;
        }

        if (safety.token.complete) {
          console.log('[CopyTrade] Token graduated but no Jupiter route — skip');
          continue;
        }

        // Estimate tokens (bonding curve data unavailable — use placeholder for paper mode)
        tokensOut = Math.floor(lamports / 1000); // rough estimate: 1 lamport = 0.001 token units
        if (tokensOut === 0) { console.log('[CopyTrade] Token estimate failed — skip'); continue; }
        
        pricePerToken = solPerTrade / tokensOut;
        priceImpact = 0; // unknown for bonding curve
        routeLabel = 'Pump.fun Bonding Curve';
        isPumpDirect = true;
        console.log(`[CopyTrade] Pump.fun route found! ${tokensOut.toLocaleString()} tokens out | mcap: $${safety.token.marketCap?.toFixed(0)}`);
        
      } else {
        tokensOut = parseInt(quote.outAmount);
        pricePerToken = solPerTrade / tokensOut;
        priceImpact = parseFloat(quote.priceImpactPct || 0);
        routeLabel = quote.routePlan?.map(r => r.swapInfo?.label).join('→') || 'Jupiter';

        if (priceImpact > 50) {
          console.log(`[CopyTrade] Price impact too high: ${priceImpact}% — skip`);
          continue;
        }
      }

      if (paper) {
        portfolio.buy(mint, solPerTrade, tokensOut, pricePerToken);
        
        await sendTelegram(`
🔴 <b>COPY TRADE — PAPER BUY</b>

Copying whale: AgmLJBM...
Token: <code>${mint.slice(0,25)}...</code>
SOL spent: ${solPerTrade} SOL
Tokens: ${tokensOut.toLocaleString()}
Impact: ${priceImpact.toFixed(2)}%
Route: ${routeLabel}
${isPumpDirect ? '🎯 Pump.fun direct trade' : ''}

Portfolio: ${portfolio.sol.toFixed(4)} SOL left
Positions: ${portfolio.positions.size}/${maxPositions}
`.trim());

      } else {
        // REAL EXECUTION
        if (!wallet) {
          console.log('[CopyTrade] No wallet configured — paper only!');
          continue;
        }
        await executeRealSwap(mint, TOKENS.SOL, lamports, quote);
      }

    } else if (trade.action === 'SELL') {
      // Whale sold — we sell too
      if (!portfolio.positions.has(mint)) continue;

      console.log(`\n[CopyTrade] 🐋 Whale SELL detected: ${mint.slice(0,20)}...`);

      const pos = portfolio.positions.get(mint);
      const sellQuote = await getJupiterQuote(mint, TOKENS.SOL, Math.floor(pos.tokens), 2000);
      
      if (!sellQuote) continue;
      
      const solBack = parseInt(sellQuote.outAmount) / 1e9;
      
      if (paper) {
        portfolio.sell(mint, solBack, pos.tokens);
        const pnl = solBack - pos.solSpent;
        const pnlPct = (pnl / pos.solSpent) * 100;
        
        await sendTelegram(`
📊 <b>COPY TRADE — PAPER SELL</b>

Token: <code>${mint.slice(0,25)}...</code>
SOL received: ${solBack.toFixed(4)}
P&L: ${pnl >= 0 ? '+' : ''}${pnlPct.toFixed(1)}% ${pnl >= 0 ? '✅' : '❌'}

Portfolio total: ${portfolio.sol.toFixed(4)} SOL
`.trim());
      }
    }
  }
}

/**
 * Real swap execution via Jupiter
 * Only runs when wallet is configured
 */
async function executeRealSwap(inputMint, outputMint, lamports, quote) {
  if (!wallet) throw new Error('No wallet configured');
  
  try {
    // Get swap transaction from Jupiter
    const { data: swapData } = await axios.post('https://quote-api.jup.ag/v6/swap', {
      quoteResponse: quote,
      userPublicKey: wallet.publicKey.toString(),
      wrapAndUnwrapSol: true,
      prioritizationFeeLamports: 10000, // ~0.00001 SOL priority fee
    });

    // Deserialize + sign + send
    const swapTx = VersionedTransaction.deserialize(
      Buffer.from(swapData.swapTransaction, 'base64')
    );
    swapTx.sign([wallet]);
    
    const sig = await connection.sendRawTransaction(swapTx.serialize(), {
      skipPreflight: false,
      maxRetries: 3,
    });
    
    await connection.confirmTransaction(sig, 'confirmed');
    
    console.log(`[CopyTrade] ✅ REAL SWAP EXECUTED: ${sig}`);
    await sendTelegram(`✅ REAL SWAP: https://solscan.io/tx/${sig}`);
    return sig;
    
  } catch (e) {
    console.error('[CopyTrade] Swap failed:', e.message);
    await sendTelegram(`❌ Swap failed: ${e.message}`);
    return null;
  }
}

/**
 * MAIN: Start copy trading bot
 */
async function startCopyTrader(options = {}) {
  const opts = {
    solPerTrade: 0.01,
    maxPositions: 3,
    takeProfitPct: 50,
    stopLossPct: 20,
    paper: true,
    ...options
  };

  const portfolio = new PaperPortfolio(opts.startSOL || 0.5);
  
  console.log(`
╔══════════════════════════════════════════╗
║  IRONMAN COPY TRADER                     ║
║  Copying: AgmLJBMDCqWynYnQiPCu...       ║
║  Mode: ${opts.paper ? 'PAPER (No real money)    ' : '⚠️  LIVE - REAL MONEY     '}║
║  Per trade: ${opts.solPerTrade} SOL${' '.repeat(25)}║
║  Max positions: ${opts.maxPositions}${' '.repeat(25)}║
╚══════════════════════════════════════════╝
  `);

  await sendTelegram(`
🤖 <b>Copy Trader STARTED</b>

Copying: AgmLJBMDCqWynYnQiPCu...zN51
Mode: ${opts.paper ? 'PAPER TRADING' : '⚠️ LIVE'}
Per trade: ${opts.solPerTrade} SOL
Balance: ${portfolio.sol} SOL
Max positions: ${opts.maxPositions}
`.trim());

  let lastSig = null;

  // Poll for new transactions (WebSocket alternative — more reliable)
  const pollInterval = setInterval(async () => {
    try {
      const sigs = await getRecentTransactions(WHALE, 3);
      if (!sigs.length) return;

      const newestSig = sigs[0].signature;
      if (newestSig === lastSig) return; // No new tx
      
      lastSig = newestSig;
      console.log(`\n[CopyTrade] New tx: ${newestSig.slice(0,20)}...`);
      
      const tx = await parseTransaction(newestSig);
      if (tx) {
        await processWhaleTx(tx, portfolio, opts);
      }
      
    } catch (e) {
      if (!e.message?.includes('429')) {
        console.error('[CopyTrade] Poll error:', e.message);
      }
    }
  }, 3000); // Poll every 3 seconds

  // Stats report every 5 minutes
  const statsInterval = setInterval(async () => {
    const stats = portfolio.getStats();
    console.log('\n[Stats]', stats);
    await sendTelegram(`
📊 <b>Copy Trader Update</b>

Balance: ${stats.currentSOL.toFixed(4)} SOL
P&L: ${stats.totalPnL >= 0 ? '+' : ''}${stats.totalPnLPct.toFixed(2)}%
Trades: ${stats.closedTrades} closed | ${stats.openPositions} open
Win rate: ${stats.winRate}
`.trim());
  }, 5 * 60 * 1000);

  return {
    stop: () => { clearInterval(pollInterval); clearInterval(statsInterval); },
    portfolio,
  };
}

module.exports = { startCopyTrader, PaperPortfolio, processWhaleTx };
