/**
 * IRONMAN Solana Bot — Wallet Tracker
 * 
 * LESSON 3: Whale Wallet Tracking
 * 
 * Smart money copy trading:
 * 1. Whale ka wallet WebSocket se monitor karo
 * 2. Jab whale koi token buy kare → hum bhi buy karo
 * 3. Jab whale sell kare → hum bhi sell karo
 * 
 * Risk: Whale dump kare toh tum bhi loss mein
 * Reward: Whale ke saath profit
 * 
 * EDUCATIONAL: Is wallet ko hum analyze kar rahe hain:
 * AgmLJBMDCqWynYnQiPCuj9ewsNNsBJXyzoUhD9LJzN51
 */

const { Connection, PublicKey } = require('@solana/web3.js');
const { connection, DEX_PROGRAMS } = require('./config');
const { getTokenPrice } = require('./price_monitor');
const axios = require('axios');

// Target whale wallet
const WHALE_WALLET = 'AgmLJBMDCqWynYnQiPCuj9ewsNNsBJXyzoUhD9LJzN51';

/**
 * Wallet ki recent transactions fetch karo
 * RPC call: getSignaturesForAddress
 */
async function getRecentTransactions(walletAddress, limit = 10) {
  try {
    const pubkey = new PublicKey(walletAddress);
    const sigs = await connection.getSignaturesForAddress(pubkey, { limit });
    return sigs;
  } catch (e) {
    console.error('[Tracker] Error:', e.message);
    return [];
  }
}

/**
 * Transaction detail parse karo
 * Kaunsa token buy/sell hua? Kitna?
 */
async function parseTransaction(signature) {
  try {
    const tx = await connection.getParsedTransaction(signature, {
      maxSupportedTransactionVersion: 0,
      commitment: 'confirmed',
    });
    
    if (!tx || !tx.meta) return null;
    
    // Token balance changes dhundho
    const preBalances = tx.meta.preTokenBalances || [];
    const postBalances = tx.meta.postTokenBalances || [];
    
    const changes = [];
    
    // Post balance mein kya aaya
    for (const post of postBalances) {
      const pre = preBalances.find(
        p => p.mint === post.mint && p.accountIndex === post.accountIndex
      );
      
      const preAmt = pre ? parseFloat(pre.uiTokenAmount.uiAmount || 0) : 0;
      const postAmt = parseFloat(post.uiTokenAmount.uiAmount || 0);
      const change = postAmt - preAmt;
      
      if (Math.abs(change) > 0.001) {
        changes.push({
          mint: post.mint,
          change,
          action: change > 0 ? 'BUY' : 'SELL',
          owner: post.owner,
        });
      }
    }
    
    // SOL change
    const solChange = (tx.meta.postBalances[0] - tx.meta.preBalances[0]) / 1e9;
    
    // Kaunsa DEX use hua
    const accountKeys = tx.transaction.message.accountKeys.map(
      k => typeof k === 'object' ? k.pubkey?.toString() : k.toString()
    );
    
    const dexUsed = Object.entries(DEX_PROGRAMS).find(
      ([name, addr]) => accountKeys.includes(addr)
    );
    
    return {
      signature,
      timestamp: tx.blockTime,
      solChange,
      tokenChanges: changes,
      dex: dexUsed ? dexUsed[0] : 'UNKNOWN',
      success: !tx.meta.err,
    };
    
  } catch (e) {
    return null;
  }
}

/**
 * CORE: Real-time wallet monitor via WebSocket
 * 
 * Solana WebSocket se kisi bhi wallet ki
 * activity instantly milti hai
 * Polling se 10x faster!
 */
function watchWallet(walletAddress, onTransaction) {
  console.log(`[Tracker] Watching wallet: ${walletAddress.slice(0,20)}...`);
  
  const pubkey = new PublicKey(walletAddress);
  
  // WebSocket subscription
  // Jab bhi is wallet mein koi transaction aaye
  // toh callback call hoga
  const subId = connection.onAccountChange(
    pubkey,
    async (accountInfo, context) => {
      console.log(`[Tracker] Activity detected! Slot: ${context.slot}`);
      
      // Latest transaction fetch karo
      const sigs = await getRecentTransactions(walletAddress, 3);
      if (sigs.length > 0) {
        const parsed = await parseTransaction(sigs[0].signature);
        if (parsed) {
          onTransaction(parsed);
        }
      }
    },
    'confirmed'
  );
  
  console.log(`[Tracker] WebSocket subscription ID: ${subId}`);
  return subId;
}

/**
 * Pattern Analysis
 * 
 * Whale ke last N transactions analyze karo
 * Trading pattern samjho
 */
async function analyzeWalletPattern(walletAddress, txCount = 20) {
  console.log(`\n[Analysis] Analyzing ${walletAddress.slice(0,20)}...`);
  
  const sigs = await getRecentTransactions(walletAddress, txCount);
  console.log(`[Analysis] Fetched ${sigs.length} transactions`);
  
  const parsed = [];
  for (const sig of sigs.slice(0, 10)) { // Parse first 10
    const tx = await parseTransaction(sig.signature);
    if (tx) parsed.push(tx);
    await new Promise(r => setTimeout(r, 200)); // Rate limit respect
  }
  
  // Stats
  const totalTxs = sigs.length;
  const times = sigs.map(s => s.blockTime).filter(Boolean).sort((a,b) => b-a);
  const gaps = [];
  for (let i = 0; i < times.length - 1; i++) {
    gaps.push(times[i] - times[i+1]);
  }
  
  const avgGap = gaps.length ? gaps.reduce((a,b) => a+b, 0) / gaps.length : 0;
  const minGap = gaps.length ? Math.min(...gaps) : 0;
  
  // Token frequency
  const tokenFreq = {};
  const dexFreq = {};
  
  for (const tx of parsed) {
    for (const change of tx.tokenChanges) {
      tokenFreq[change.mint] = (tokenFreq[change.mint] || 0) + 1;
    }
    dexFreq[tx.dex] = (dexFreq[tx.dex] || 0) + 1;
  }
  
  const topTokens = Object.entries(tokenFreq)
    .sort((a,b) => b[1]-a[1])
    .slice(0, 5);
  
  const report = {
    wallet: walletAddress,
    totalTxs,
    avgGapSec: avgGap.toFixed(1),
    minGapSec: minGap.toFixed(1),
    isBot: minGap < 2,
    dexUsage: dexFreq,
    topTokens,
    strategy: minGap < 2 ? 'BOT (Automated)' : 
               avgGap < 60 ? 'Active Trader' : 'Manual Trader',
  };
  
  console.log('\n=== WALLET PATTERN REPORT ===');
  console.log(`Strategy: ${report.strategy}`);
  console.log(`Avg gap between txs: ${report.avgGapSec}s`);
  console.log(`Min gap: ${report.minGapSec}s`);
  console.log(`DEX usage:`, report.dexUsage);
  console.log(`Top tokens:`, topTokens.map(([m,c]) => `${m.slice(0,8)}: ${c}x`));
  
  return report;
}

/**
 * Copy Trade Simulator (PAPER TRADING — NO REAL MONEY)
 * 
 * Whale ke trades ko simulate karo
 * Real paise mat lagao — pehle result dekho
 */
class CopyTradeSimulator {
  constructor(initialSOL = 1.0) {
    this.balance = initialSOL;
    this.initialBalance = initialSOL;
    this.holdings = new Map(); // token => amount
    this.trades = [];
    console.log(`[Simulator] Started with ${initialSOL} SOL (PAPER TRADING)`);
  }
  
  async onWhaleTrade(tx) {
    for (const change of tx.tokenChanges) {
      if (change.action === 'BUY' && this.balance > 0.01) {
        // Whale ne buy kiya — hum bhi buy karte hain (simulated)
        const tradeSOL = Math.min(this.balance * 0.1, 0.1); // 10% of balance
        const price = await getTokenPrice(change.mint);
        
        if (price) {
          const tokensReceived = (tradeSOL / price.price);
          this.balance -= tradeSOL;
          this.holdings.set(change.mint, 
            (this.holdings.get(change.mint) || 0) + tokensReceived
          );
          
          const trade = {
            action: 'BUY',
            mint: change.mint,
            solSpent: tradeSOL,
            tokensReceived,
            price: price.price,
            time: new Date().toISOString(),
            dex: tx.dex,
          };
          this.trades.push(trade);
          console.log(`[Simulator] PAPER BUY: ${tradeSOL} SOL → ${tokensReceived.toFixed(2)} tokens @ $${price.price}`);
        }
        
      } else if (change.action === 'SELL') {
        // Whale ne sell kiya — hum bhi sell karte hain
        const held = this.holdings.get(change.mint) || 0;
        if (held > 0) {
          const price = await getTokenPrice(change.mint);
          if (price) {
            const solReceived = held * price.price;
            this.balance += solReceived;
            this.holdings.delete(change.mint);
            
            const trade = {
              action: 'SELL',
              mint: change.mint,
              tokensSold: held,
              solReceived,
              price: price.price,
              time: new Date().toISOString(),
            };
            this.trades.push(trade);
            console.log(`[Simulator] PAPER SELL: ${held.toFixed(2)} tokens → ${solReceived.toFixed(4)} SOL`);
          }
        }
      }
    }
  }
  
  getPnL() {
    const pnl = this.balance - this.initialBalance;
    const pnlPct = (pnl / this.initialBalance) * 100;
    return {
      currentBalance: this.balance,
      pnl,
      pnlPct,
      trades: this.trades.length,
    };
  }
}

module.exports = {
  getRecentTransactions,
  parseTransaction,
  watchWallet,
  analyzeWalletPattern,
  CopyTradeSimulator,
  WHALE_WALLET,
};
