/**
 * IRONMAN Solana Bot — Price Monitor
 * 
 * LESSON 2: Price Fetching
 * 
 * Jupiter API use karke kisi bhi token ka price milta hai
 * Jupiter = Solana ka best DEX aggregator
 * Woh automatically best route dhundta hai across all DEXes
 * 
 * ARBITRAGE CONCEPT:
 * Token X ka price:
 *   Raydium pe = $1.000
 *   Orca pe    = $1.005
 * 
 * Agar tu Raydium se buy kare aur Orca pe sell kare
 * → $0.005 profit per token (0.5%)
 * → Isse arbitrage kehte hain
 * → Risk-free profit (in theory)
 */

const axios = require('axios');
const { connection, TOKENS } = require('./config');

// Jupiter Price API — free, no auth needed
const JUPITER_PRICE_API = 'https://api.jup.ag/price/v2';
const JUPITER_QUOTE_API = 'https://quote-api.jup.ag/v6/quote';

/**
 * Kisi bhi token ka current price fetch karo (in USD)
 * @param {string} tokenMint - token ka mint address
 */
async function getTokenPrice(tokenMint) {
  try {
    const res = await axios.get(`${JUPITER_PRICE_API}?ids=${tokenMint}`, {
      timeout: 5000
    });
    const data = res.data.data[tokenMint];
    if (data) {
      return {
        price: parseFloat(data.price),
        mint: tokenMint,
        type: data.type,
      };
    }
  } catch (e) {
    // silent fail
  }
  return null;
}

/**
 * Multiple tokens ke prices ek saath fetch karo
 * @param {string[]} mints - array of token mint addresses
 */
async function getMultiplePrices(mints) {
  try {
    const ids = mints.join(',');
    const res = await axios.get(`${JUPITER_PRICE_API}?ids=${ids}`, {
      timeout: 8000
    });
    return res.data.data;
  } catch (e) {
    return {};
  }
}

/**
 * CORE FUNCTION: Jupiter se quote lo
 * 
 * Quote = "Agar main X token se Y token buy karun
 *          toh mujhe kitna milega?"
 * 
 * @param {string} inputMint  - jis token se pay karenge
 * @param {string} outputMint - jis token ko buy karenge  
 * @param {number} amountLamports - kitna (in lamports, 1 SOL = 1B lamports)
 * @param {number} slippage - max price slip allowed (50 = 0.5%)
 */
async function getJupiterQuote(inputMint, outputMint, amountLamports, slippage = 50) {
  try {
    const res = await axios.get(JUPITER_QUOTE_API, {
      params: {
        inputMint,
        outputMint,
        amount: amountLamports,
        slippageBps: slippage,
        onlyDirectRoutes: false,  // false = best route across all DEXes
      },
      timeout: 8000,
    });
    return res.data;
  } catch (e) {
    return null;
  }
}

/**
 * ARBITRAGE SCANNER
 * 
 * CONCEPT:
 * SOL → Token → SOL
 * Agar end mein zyada SOL mile toh profit!
 * 
 * Example:
 * 1 SOL se USDC buy karo (Jupiter best route)
 * Phir woh USDC se SOL buy karo (Jupiter best route)
 * Agar > 1 SOL mile = arbitrage opportunity!
 */
async function checkArbitrage(tokenMint, solAmount = 0.01) {
  const lamports = Math.floor(solAmount * 1e9); // SOL to lamports
  
  // Step 1: SOL → Token (kharidna)
  const buyQuote = await getJupiterQuote(
    TOKENS.SOL,
    tokenMint,
    lamports
  );
  
  if (!buyQuote) return null;
  
  const tokenReceived = parseInt(buyQuote.outAmount);
  const buyRoute = buyQuote.routePlan?.map(r => r.swapInfo?.label).join(' → ');
  
  // Step 2: Token → SOL (bechna)
  const sellQuote = await getJupiterQuote(
    tokenMint,
    TOKENS.SOL,
    tokenReceived
  );
  
  if (!sellQuote) return null;
  
  const solReceived = parseInt(sellQuote.outAmount);
  const sellRoute = sellQuote.routePlan?.map(r => r.swapInfo?.label).join(' → ');
  
  // Profit calculate karo
  const profitLamports = solReceived - lamports;
  const profitSol = profitLamports / 1e9;
  const profitPct = (profitLamports / lamports) * 100;
  
  return {
    token: tokenMint,
    inputSol: solAmount,
    outputSol: solReceived / 1e9,
    profitSol,
    profitPct,
    profitable: profitPct > 0,
    buyRoute,
    sellRoute,
    buyQuote,
    sellQuote,
  };
}

/**
 * SOL price in USD
 */
async function getSolPrice() {
  try {
    // CoinGecko free API - no auth needed
    const res = await axios.get(
      'https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd',
      { timeout: 8000 }
    );
    return res.data?.solana?.usd || 0;
  } catch (e) {
    const data = await getMultiplePrices([TOKENS.SOL]);
    return data[TOKENS.SOL]?.price || 0;
  }
}

/**
 * Token price ka history track karna
 * Price spike = potential opportunity
 */
class PriceTracker {
  constructor() {
    this.prices = new Map(); // mint => [price1, price2, ...]
    this.maxHistory = 60;    // last 60 readings
  }
  
  update(mint, price) {
    if (!this.prices.has(mint)) {
      this.prices.set(mint, []);
    }
    const history = this.prices.get(mint);
    history.push({ price, time: Date.now() });
    if (history.length > this.maxHistory) history.shift();
  }
  
  getChange(mint, windowMs = 60000) {
    const history = this.prices.get(mint);
    if (!history || history.length < 2) return 0;
    
    const now = Date.now();
    const old = history.find(h => now - h.time >= windowMs);
    const current = history[history.length - 1];
    
    if (!old) return 0;
    return ((current.price - old.price) / old.price) * 100;
  }
  
  isSpike(mint, threshold = 5) {
    return Math.abs(this.getChange(mint)) >= threshold;
  }
}

module.exports = {
  getTokenPrice,
  getMultiplePrices,
  getJupiterQuote,
  checkArbitrage,
  getSolPrice,
  PriceTracker,
};
