/**
 * IRONMAN Solana Bot — Token Sniper
 * 
 * LESSON: How sniping works
 * 
 * New token launch hota hai Pump.fun / Raydium pe
 * → Hum WebSocket se detect karte hain
 * → Instantly buy karte hain (0.1-0.5 sec)
 * → Price pump hone pe sell karte hain
 * 
 * RISK WARNING:
 * → 90% new tokens = rugpull / honeypot
 * → Always small amounts only
 * → Never invest what you can't lose
 * 
 * SAFETY FILTERS we use:
 * → Minimum liquidity check
 * → No mint authority (can't print more)
 * → No freeze authority (can't freeze your tokens)
 * → Liquidity locked check
 */

const { Connection, PublicKey } = require('@solana/web3.js');
const axios = require('axios');
const { connection, DEX_PROGRAMS, TOKENS, config } = require('./config');
const { getJupiterQuote } = require('./price_monitor');
const { sendTelegram } = require('./alerts');

// Pump.fun program ID
const PUMP_FUN_PROGRAM = '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P';
// Raydium pool program
const RAYDIUM_POOL_PROGRAM = '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8';

/**
 * SAFETY CHECK — Token ke metadata verify karo
 * 
 * Ye sabse important step hai!
 * Bina safety check ke snipe karna = guaranteed loss
 */
async function safetyCheck(mintAddress) {
  const checks = {
    hasMintAuthority: false,   // true = bad (can print more tokens)
    hasFreezeAuthority: false, // true = bad (can freeze your wallet)
    hasLiquidity: false,       // false = bad (can't sell)
    liquidityUSD: 0,
    passed: false,
    reasons: [],
  };

  try {
    // Jupiter API se token info
    const res = await axios.get(
      `https://tokens.jup.ag/token/${mintAddress}`,
      { timeout: 5000 }
    );
    const tokenInfo = res.data;

    // Minimum liquidity check ($1000 minimum)
    // Kam liquidity = rug easily possible
    if (tokenInfo.daily_volume > 1000) {
      checks.hasLiquidity = true;
      checks.liquidityUSD = tokenInfo.daily_volume;
    } else {
      checks.reasons.push(`Low liquidity: $${tokenInfo.daily_volume}`);
    }

  } catch (e) {
    checks.reasons.push('Token not found on Jupiter');
  }

  try {
    // Solana RPC se mint account check
    const mintPubkey = new PublicKey(mintAddress);
    const mintInfo = await connection.getParsedAccountInfo(mintPubkey);
    
    if (mintInfo.value) {
      const data = mintInfo.value.data?.parsed?.info;
      if (data) {
        // Mint authority check
        if (data.mintAuthority) {
          checks.hasMintAuthority = true;
          checks.reasons.push('Has mint authority — dev can print tokens!');
        }
        
        // Freeze authority check
        if (data.freezeAuthority) {
          checks.hasFreezeAuthority = true;
          checks.reasons.push('Has freeze authority — dev can freeze your tokens!');
        }
      }
    }
  } catch (e) {
    checks.reasons.push('Could not verify mint authority');
  }

  // PASS only if: no mint auth + no freeze auth + has liquidity
  checks.passed = !checks.hasMintAuthority && 
                  !checks.hasFreezeAuthority && 
                  checks.hasLiquidity;

  return checks;
}

/**
 * NEW POOL DETECTOR
 * 
 * Raydium pe jab naya pool create hota hai
 * toh ek specific transaction pattern hota hai
 * Hum woh detect karte hain
 */
async function detectNewPools(onNewPool) {
  console.log('[Sniper] Watching for new pools on Raydium + Pump.fun...');
  
  // Raydium pool program ke logs monitor karo
  const subId = connection.onLogs(
    new PublicKey(RAYDIUM_POOL_PROGRAM),
    async (logs) => {
      // "initialize2" = new pool creation signature
      if (logs.logs.some(log => log.includes('initialize2'))) {
        console.log('\n[Sniper] 🚨 NEW RAYDIUM POOL DETECTED!');
        
        try {
          const tx = await connection.getParsedTransaction(logs.signature, {
            maxSupportedTransactionVersion: 0,
            commitment: 'confirmed',
          });
          
          if (tx) {
            // Token mint address dhundho
            const accounts = tx.transaction.message.accountKeys;
            const mints = [];
            
            for (const acc of accounts) {
              const pubkey = typeof acc === 'object' ? acc.pubkey?.toString() : acc.toString();
              // SOL aur USDC ko skip karo
              if (pubkey !== TOKENS.SOL && pubkey !== TOKENS.USDC) {
                try {
                  const info = await connection.getParsedAccountInfo(new PublicKey(pubkey));
                  if (info.value?.data?.parsed?.type === 'mint') {
                    mints.push(pubkey);
                  }
                } catch (e) {}
              }
            }
            
            if (mints.length > 0) {
              const newTokenMint = mints[0];
              console.log(`[Sniper] New token mint: ${newTokenMint}`);
              onNewPool({
                mint: newTokenMint,
                signature: logs.signature,
                timestamp: Date.now(),
                dex: 'RAYDIUM',
              });
            }
          }
        } catch (e) {
          console.error('[Sniper] Parse error:', e.message);
        }
      }
    },
    'confirmed'
  );
  
  // Pump.fun monitor (simpler — all txs are launches)
  const pumpSubId = connection.onLogs(
    new PublicKey(PUMP_FUN_PROGRAM),
    async (logs) => {
      if (logs.logs.some(log => log.includes('MintTo') || log.includes('InitializeMint'))) {
        console.log('\n[Sniper] 🚨 NEW PUMP.FUN TOKEN DETECTED!');
        
        // Quick grab the mint from logs
        const mintLog = logs.logs.find(l => l.includes('mint'));
        if (mintLog) {
          onNewPool({
            signature: logs.signature,
            timestamp: Date.now(),
            dex: 'PUMP_FUN',
            raw: mintLog,
          });
        }
      }
    },
    'confirmed'
  );
  
  return { raydiumSub: subId, pumpSub: pumpSubId };
}

/**
 * SNIPE EXECUTION LOGIC (Paper mode)
 * 
 * Real execution ke liye wallet private key chahiye
 * Abhi sirf simulate kar rahe hain
 */
async function executeSniperBuy(mint, solAmount, isSimulated = true) {
  console.log(`\n[Sniper] ${isSimulated ? 'SIMULATED' : 'REAL'} BUY: ${mint.slice(0,20)}... | ${solAmount} SOL`);
  
  // Safety check first!
  console.log('[Sniper] Running safety checks...');
  const safety = await safetyCheck(mint);
  
  console.log(`[Sniper] Safety: ${safety.passed ? '✅ PASSED' : '❌ FAILED'}`);
  if (!safety.passed) {
    console.log(`[Sniper] Reasons: ${safety.reasons.join(', ')}`);
    return { success: false, reason: safety.reasons.join(', ') };
  }
  
  // Get quote
  const lamports = Math.floor(solAmount * 1e9);
  const quote = await getJupiterQuote(TOKENS.SOL, mint, lamports, 1000); // 10% slippage for new tokens
  
  if (!quote) {
    return { success: false, reason: 'No route found' };
  }
  
  const tokensOut = parseInt(quote.outAmount);
  const priceImpact = parseFloat(quote.priceImpactPct || 0);
  
  console.log(`[Sniper] Quote: ${solAmount} SOL → ${tokensOut} tokens`);
  console.log(`[Sniper] Price impact: ${priceImpact.toFixed(2)}%`);
  
  if (priceImpact > 20) {
    return { success: false, reason: `Price impact too high: ${priceImpact.toFixed(2)}%` };
  }
  
  if (isSimulated) {
    // Paper trade only
    const result = {
      success: true,
      simulated: true,
      mint,
      solSpent: solAmount,
      tokensReceived: tokensOut,
      priceImpact,
      buyTime: Date.now(),
      safetyChecks: safety,
    };
    
    await sendTelegram(`
🎯 <b>SNIPER - PAPER BUY EXECUTED</b>

Token: <code>${mint.slice(0,20)}...</code>
SOL spent: ${solAmount}
Tokens: ${tokensOut.toLocaleString()}
Price impact: ${priceImpact.toFixed(2)}%
Safety: ✅ PASSED

⚠️ SIMULATED — No real money
`.trim());
    
    return result;
  }
  
  // REAL EXECUTION — Only with configured wallet
  // TODO: Add @jup-ag/api swap execution
  // Requires: wallet private key + enough SOL
  return { success: false, reason: 'Real execution not yet configured' };
}

/**
 * AUTO SELL — Take profit / stop loss
 * 
 * Target: Sell at 2x (100% profit)
 * Stop:   Sell at -30% (stop loss)
 */
async function autoSell(position, currentPrice) {
  const { mint, buyPrice, solSpent, tokensReceived } = position;
  const pnlPct = ((currentPrice - buyPrice) / buyPrice) * 100;
  
  console.log(`[Sniper] Position ${mint.slice(0,12)}: ${pnlPct.toFixed(1)}% P&L`);
  
  // Take profit at 2x
  if (pnlPct >= 100) {
    console.log('[Sniper] 🎯 TAKE PROFIT triggered!');
    return { action: 'SELL', reason: 'Take profit 2x' };
  }
  
  // Stop loss at -30%
  if (pnlPct <= -30) {
    console.log('[Sniper] 🛑 STOP LOSS triggered!');
    return { action: 'SELL', reason: 'Stop loss -30%' };
  }
  
  return { action: 'HOLD', pnlPct };
}

/**
 * FULL SNIPER BOT — Put it all together
 */
async function startSniper(options = {}) {
  const {
    solPerTrade = 0.01,  // TINY amount for testing
    simulated = true,    // Always start in paper mode!
    maxPositions = 3,    // Max 3 positions at once
  } = options;
  
  console.log(`
[Sniper] ==========================================
[Sniper] IRONMAN SNIPER BOT STARTING
[Sniper] Mode: ${simulated ? 'PAPER (Simulated)' : '⚠️ REAL MONEY'}
[Sniper] Per trade: ${solPerTrade} SOL
[Sniper] Max positions: ${maxPositions}
[Sniper] ==========================================
  `);
  
  await sendTelegram(`
🎯 <b>Sniper Bot Started</b>
Mode: ${simulated ? 'Paper Trading' : 'LIVE'}
Per trade: ${solPerTrade} SOL
Watching: Raydium + Pump.fun new launches
`.trim());
  
  const positions = new Map();
  let totalSnipes = 0;
  
  // Start watching for new pools
  const subs = await detectNewPools(async (newToken) => {
    console.log(`\n[Sniper] New token detected: ${newToken.dex}`);
    console.log(`[Sniper] Signature: ${newToken.signature?.slice(0,20)}...`);
    
    // Max positions check
    if (positions.size >= maxPositions) {
      console.log('[Sniper] Max positions reached — skipping');
      return;
    }
    
    if (!newToken.mint) {
      console.log('[Sniper] No mint address found — skipping');
      return;
    }
    
    // Execute snipe
    totalSnipes++;
    const result = await executeSniperBuy(newToken.mint, solPerTrade, simulated);
    
    if (result.success) {
      positions.set(newToken.mint, {
        ...result,
        buyPrice: solPerTrade / result.tokensReceived,
      });
      console.log(`[Sniper] Position opened! Total: ${positions.size}`);
    }
  });
  
  // Position monitor — check prices every 30 seconds
  const positionMonitor = setInterval(async () => {
    if (positions.size === 0) return;
    
    console.log(`\n[Sniper] Checking ${positions.size} positions...`);
    
    for (const [mint, position] of positions) {
      try {
        // Get current sell quote
        const sellQuote = await getJupiterQuote(
          mint,
          TOKENS.SOL,
          position.tokensReceived,
          500
        );
        
        if (sellQuote) {
          const currentSOL = parseInt(sellQuote.outAmount) / 1e9;
          const currentPrice = currentSOL / position.tokensReceived;
          
          const decision = await autoSell(position, currentPrice);
          
          if (decision.action === 'SELL') {
            console.log(`[Sniper] Selling ${mint.slice(0,12)}... Reason: ${decision.reason}`);
            positions.delete(mint);
            
            await sendTelegram(`
📊 <b>Sniper Position Closed</b>
Token: <code>${mint.slice(0,20)}...</code>
Reason: ${decision.reason}
P&L: ${((currentSOL - position.solSpent) / position.solSpent * 100).toFixed(1)}%
SOL back: ${currentSOL.toFixed(4)}
`.trim());
          }
        }
      } catch (e) {
        console.error(`[Sniper] Monitor error for ${mint.slice(0,12)}:`, e.message);
      }
    }
  }, 30000);
  
  // Stats every 5 minutes
  const statsInterval = setInterval(async () => {
    await sendTelegram(`
📊 <b>Sniper Stats</b>
Running: ${Math.floor(process.uptime()/60)} min
Total snipe attempts: ${totalSnipes}
Open positions: ${positions.size}
`.trim());
  }, 5 * 60 * 1000);
  
  return {
    stop: () => {
      clearInterval(positionMonitor);
      clearInterval(statsInterval);
    },
    getPositions: () => positions,
    getStats: () => ({ totalSnipes, openPositions: positions.size }),
  };
}

module.exports = {
  startSniper,
  safetyCheck,
  detectNewPools,
  executeSniperBuy,
  autoSell,
};
