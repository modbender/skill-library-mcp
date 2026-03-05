/**
 * SolArb Type Definitions
 */

import { Transaction, PublicKey } from '@solana/web3.js';

export interface PriceQuote {
  dex: string;
  baseToken: string;
  quoteToken: string;
  buyPrice: number;      // Price to buy base token in quote token
  sellPrice: number;     // Price to sell base token for quote token
  liquidity: number;     // Available liquidity in USD
  timestamp: number;
}

export interface ArbitrageOpportunity {
  pair: string;
  buyDex: string;
  sellDex: string;
  buyPrice: number;
  sellPrice: number;
  profitBps: number;           // Profit in basis points
  estimatedProfitUsd: number;
  timestamp: number;
}

export interface TradeResult {
  success: boolean;
  opportunity: ArbitrageOpportunity;
  buyTxSignature?: string;
  sellTxSignature?: string;
  actualProfitUsd?: number;
  error?: string;
  executionTimeMs: number;
}

export interface DexInterface {
  name: string;
  
  /**
   * Get price quote for a trading pair
   */
  getQuote(baseToken: string, quoteToken: string, amountUsd: number): Promise<PriceQuote | null>;
  
  /**
   * Build a swap transaction
   */
  buildSwapTransaction(
    inputToken: string,
    outputToken: string,
    amountUsd: number,
    maxSlippageBps: number,
    userPubkey: PublicKey
  ): Promise<Transaction>;
}

export interface PnLStats {
  daily: PnLPeriod;
  weekly: PnLPeriod;
  monthly: PnLPeriod;
  allTime: PnLPeriod;
}

export interface PnLPeriod {
  profitUsd: number;
  trades: number;
  winRate: number;
  avgProfitPerTrade: number;
  bestTrade: number;
  worstTrade: number;
}

export interface TokenInfo {
  symbol: string;
  name: string;
  mint: string;
  decimals: number;
  price: number;
}

// Common Solana tokens
export const TOKENS: Record<string, TokenInfo> = {
  SOL: {
    symbol: 'SOL',
    name: 'Solana',
    mint: 'So11111111111111111111111111111111111111112',
    decimals: 9,
    price: 0
  },
  USDC: {
    symbol: 'USDC',
    name: 'USD Coin',
    mint: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    decimals: 6,
    price: 1
  },
  USDT: {
    symbol: 'USDT',
    name: 'Tether USD',
    mint: 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',
    decimals: 6,
    price: 1
  },
  RAY: {
    symbol: 'RAY',
    name: 'Raydium',
    mint: '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R',
    decimals: 6,
    price: 0
  },
  ORCA: {
    symbol: 'ORCA',
    name: 'Orca',
    mint: 'orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE',
    decimals: 6,
    price: 0
  },
  JUP: {
    symbol: 'JUP',
    name: 'Jupiter',
    mint: 'JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN',
    decimals: 6,
    price: 0
  }
};

export function getTokenMint(symbol: string): string {
  const token = TOKENS[symbol.toUpperCase()];
  if (!token) {
    throw new Error(`Unknown token: ${symbol}`);
  }
  return token.mint;
}

export function getTokenDecimals(symbol: string): number {
  const token = TOKENS[symbol.toUpperCase()];
  if (!token) {
    throw new Error(`Unknown token: ${symbol}`);
  }
  return token.decimals;
}
