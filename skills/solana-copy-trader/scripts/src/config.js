/**
 * IRONMAN Solana Bot — Config Module
 * 
 * LESSON 1: Environment variables se sensitive data store karte hain
 * Code mein kabhi private key mat likho
 */

require('dotenv').config();
const { Connection, PublicKey, Keypair } = require('@solana/web3.js');
const bs58 = require('bs58');

// ============================================
// CONNECTION SETUP
// ============================================
// Solana network se connect karna
// mainnet-beta = real money, devnet = test money
const connection = new Connection(
  process.env.RPC_URL || 'https://api.mainnet-beta.solana.com',
  {
    commitment: 'confirmed',  // transaction confirm hone ka level
    wsEndpoint: process.env.RPC_WS,
  }
);

// ============================================
// WALLET SETUP  
// ============================================
// Private key se Keypair banate hain
// Keypair = public key (wallet address) + private key (signing)
let wallet = null;
if (process.env.PRIVATE_KEY && process.env.PRIVATE_KEY !== 'your_private_key_here') {
  try {
    const secretKey = bs58.default.decode(process.env.PRIVATE_KEY);
    wallet = Keypair.fromSecretKey(secretKey);
    console.log(`[Config] Wallet loaded: ${wallet.publicKey.toString()}`);
  } catch (e) {
    console.log('[Config] No wallet configured — running in WATCH ONLY mode');
  }
} else {
  console.log('[Config] No wallet configured — running in WATCH ONLY mode');
}

// ============================================
// KNOWN DEX PROGRAM IDs
// ============================================
// Yeh Solana pe DEX protocols ke addresses hain
// Jab koi in addresses ke saath transaction karta hai
// toh hum samajh jaate hain kaunsa DEX use hua
const DEX_PROGRAMS = {
  JUPITER:    'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4',
  RAYDIUM:    '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8',
  ORCA:       'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc',
  PUMP_FUN:   '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P',
  METEORA:    'Eo7WjKq67rjJQDd81bBQXXZMCFNiPQWASbcYxKBF3Rn',
};

// ============================================
// IMPORTANT TOKEN ADDRESSES
// ============================================
const TOKENS = {
  SOL:  'So11111111111111111111111111111111111111112',
  USDC: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
  USDT: 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',
};

module.exports = {
  connection,
  wallet,
  DEX_PROGRAMS,
  TOKENS,
  config: {
    maxTradeSol: parseFloat(process.env.MAX_TRADE_SOL || '0.1'),
    minProfitPct: parseFloat(process.env.MIN_PROFIT_PCT || '0.5'),
    jitoTip: parseFloat(process.env.JITO_TIP || '0.001'),
    botToken: process.env.BOT_TOKEN,
    chatId: process.env.CHAT_ID,
  }
};
