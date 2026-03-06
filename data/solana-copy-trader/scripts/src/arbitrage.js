/**
 * IRONMAN Solana Bot — Arbitrage Scanner
 * 
 * LESSON 4: Arbitrage — How it actually works
 * 
 * SIMPLE EXPLANATION:
 * ─────────────────
 * Maan le SOL = $100
 * 
 * Jupiter route 1 (via Raydium):
 *   0.1 SOL → 10.05 USDC → 0.1005 SOL back
 *   Profit: 0.0005 SOL = 0.5%
 * 
 * Jupiter route 2 (via Orca):
 *   0.1 SOL → 9.99 USDC → 0.0999 SOL back
 *   Loss: -0.01% ❌
 * 
 * Hum route 1 ko dhundh ke execute karte hain!
 * 
 * WHY IT EXISTS:
 * ─────────────
 * Different DEXes mein liquidity pools hote hain
 * Jab koi bada trade hota hai, price temporarily off ho jaata hai
 * Arbitrageurs yeh gap fill karte hain
 * Result: Market efficient rehta hai
 * Arbitrageur: Free profit!
 */

const { checkArbitrage, getMultiplePrices, getSolPrice } = require('./price_monitor');
const { config } = require('./config');
const axios = require('axios');

// Popular tokens for arbitrage scanning
// Yeh high-liquidity tokens hain jahan opportunities zyada hoti hain
const SCAN_TOKENS = [
  'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', // USDC
  'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',  // USDT
  'mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So',  // mSOL
  'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', // BONK
  'JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN',  // JUP
  '7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs', // ETH (Wormhole)
];

/**
 * Full arbitrage scan — sabhi tokens check karo
 * @param {number} solAmount - kitne SOL se scan karna hai
 * @param {number} minProfit - minimum profit % threshold
 */
async function scanArbitrageOpportunities(solAmount = 0.01, minProfit = 0.3) {
  console.log(`\n[Arb] Scanning ${SCAN_TOKENS.length} tokens for ${solAmount} SOL...`);
  
  const opportunities = [];
  const solPrice = await getSolPrice();
  console.log(`[Arb] SOL price: $${solPrice.toFixed(2)}`);
  
  // Parallel check — sab ek saath
  const results = await Promise.allSettled(
    SCAN_TOKENS.map(mint => checkArbitrage(mint, solAmount))
  );
  
  for (let i = 0; i < results.length; i++) {
    const result = results[i];
    if (result.status === 'fulfilled' && result.value) {
      const arb = result.value;
      
      if (arb.profitable && arb.profitPct >= minProfit) {
        const profitUSD = arb.profitSol * solPrice;
        opportunities.push({
          ...arb,
          profitUSD,
          token: SCAN_TOKENS[i],
        });
        
        console.log(`[Arb] ✅ OPPORTUNITY FOUND!`);
        console.log(`     Token: ${SCAN_TOKENS[i].slice(0,20)}...`);
        console.log(`     Profit: ${arb.profitPct.toFixed(3)}% = ${arb.profitSol.toFixed(6)} SOL ($${profitUSD.toFixed(4)})`);
        console.log(`     Route: SOL → [${arb.buyRoute}] → Token → [${arb.sellRoute}] → SOL`);
      } else if (arb.profitPct > -1) {
        // Close to profit — log for learning
        console.log(`[Arb] 📊 ${SCAN_TOKENS[i].slice(0,12)}... | ${arb.profitPct.toFixed(3)}% | ${arb.buyRoute} → ${arb.sellRoute}`);
      }
    }
  }
  
  // Best opportunity
  opportunities.sort((a, b) => b.profitPct - a.profitPct);
  
  return opportunities;
}

/**
 * Continuous arbitrage monitor
 * Every N seconds scan karo
 * 
 * @param {number} intervalMs - kitne ms baad scan karo
 * @param {Function} onOpportunity - callback when opportunity found
 */
async function startArbitrageMonitor(intervalMs = 5000, onOpportunity) {
  console.log(`[Arb Monitor] Starting... interval: ${intervalMs/1000}s`);
  
  let scanCount = 0;
  let totalOpportunities = 0;
  
  const scan = async () => {
    scanCount++;
    const startTime = Date.now();
    
    try {
      const opportunities = await scanArbitrageOpportunities(
        config.maxTradeSol,
        config.minProfitPct
      );
      
      const elapsed = Date.now() - startTime;
      console.log(`[Arb] Scan #${scanCount} done in ${elapsed}ms | Found: ${opportunities.length} opps`);
      
      if (opportunities.length > 0) {
        totalOpportunities += opportunities.length;
        
        for (const opp of opportunities) {
          if (onOpportunity) {
            await onOpportunity(opp);
          }
        }
      }
      
    } catch (e) {
      console.error('[Arb] Scan error:', e.message);
    }
  };
  
  // First scan immediately
  await scan();
  
  // Then repeat
  const interval = setInterval(scan, intervalMs);
  
  return {
    stop: () => clearInterval(interval),
    getStats: () => ({ scanCount, totalOpportunities }),
  };
}

/**
 * LESSON: Why arbitrage is hard in practice
 * 
 * Problems:
 * 1. By the time you see it, others execute it faster
 * 2. Transaction fees eat into profits (0.000005 SOL per tx)
 * 3. Slippage: Large trades move the price against you
 * 4. MEV bots front-run your transaction
 * 
 * Solutions (that whale uses):
 * 1. Private RPC (faster mempool access)
 * 2. Jito bundles (guaranteed execution order)
 * 3. Pre-signed transactions (ready to go)
 * 4. Multiple wallets (parallel execution)
 */
function explainArbitrage() {
  const explanation = `
═══════════════════════════════════════
ARBITRAGE — HOW IT REALLY WORKS
═══════════════════════════════════════

STEP 1: PRICE DISCOVERY
  - Jupiter API se quote lo (free)
  - SOL → USDC → SOL route test karo
  - Profit calculate karo

STEP 2: OPPORTUNITY CHECK
  - Profit > fees? (fees ~$0.0001 on Solana)
  - Profit > slippage? (usually 0.1-0.5%)
  - Execute within 1-2 blocks? (0.4 seconds)

STEP 3: EXECUTION (Advanced)
  - Jito bundle = multiple txs together
  - Private RPC = faster than public
  - Atomic = buy AND sell in same block

REAL NUMBERS:
  ✅ Opportunity: 0.5% on 1 SOL
  → Gross: 0.005 SOL ($0.40)
  → Network fee: 0.00001 SOL
  → Net: ~0.0049 SOL ($0.39)
  
  At 100 opportunities/day:
  → $39/day theoretical
  → Reality: ~30% hit rate = $12/day

WHALE REALITY (AgmLJBM...):
  → 172,000 txs/day
  → 0.3% average profit
  → ~500 SOL/day = $40,000/day
  → Using Jito MEV + private infra
═══════════════════════════════════════
`;
  console.log(explanation);
}

module.exports = {
  scanArbitrageOpportunities,
  startArbitrageMonitor,
  explainArbitrage,
  SCAN_TOKENS,
};
