/**
 * Meteora DEX Integration
 * 
 * Meteora DLMM (Dynamic Liquidity Market Maker) pools.
 */

import { Connection, PublicKey, Transaction } from '@solana/web3.js';
import axios from 'axios';
import { DexInterface, PriceQuote, getTokenMint, getTokenDecimals } from '../types';
import { logger } from '../utils/logger';

const METEORA_API = 'https://dlmm-api.meteora.ag';

export class MeteoraDex implements DexInterface {
  name = 'meteora';
  private connection: Connection;

  constructor(connection: Connection) {
    this.connection = connection;
  }

  async getQuote(baseToken: string, quoteToken: string, amountUsd: number): Promise<PriceQuote | null> {
    try {
      const inputMint = getTokenMint(quoteToken);
      const outputMint = getTokenMint(baseToken);
      const inputDecimals = getTokenDecimals(quoteToken);
      
      // Get all DLMM pairs
      const pairsResponse = await axios.get(`${METEORA_API}/pair/all_by_groups`);
      const allPairs = pairsResponse.data?.groups?.flatMap((g: any) => g.pairs) || [];
      
      // Find matching pair
      const pair = allPairs.find((p: any) => 
        (p.mint_x === inputMint && p.mint_y === outputMint) ||
        (p.mint_y === inputMint && p.mint_x === outputMint)
      );

      if (!pair) return null;

      // Get quote
      const isXInput = pair.mint_x === inputMint;
      const inputAmount = Math.floor(amountUsd * Math.pow(10, inputDecimals));
      
      const quoteResponse = await axios.get(`${METEORA_API}/pair/${pair.address}/quote`, {
        params: {
          amount: inputAmount,
          swapForY: isXInput
        }
      });

      if (!quoteResponse.data) return null;

      const outputAmount = parseInt(quoteResponse.data.outAmount || '0');
      const outputDecimals = getTokenDecimals(baseToken);
      
      const buyPrice = (inputAmount / Math.pow(10, inputDecimals)) / 
                       (outputAmount / Math.pow(10, outputDecimals));
      
      const sellPrice = buyPrice * 0.995; // Estimate with fees

      return {
        dex: this.name,
        baseToken,
        quoteToken,
        buyPrice,
        sellPrice,
        liquidity: parseFloat(pair.liquidity) || amountUsd * 20,
        timestamp: Date.now()
      };
    } catch (error: any) {
      logger.debug(`Meteora quote error: ${error.message}`);
      return null;
    }
  }

  async buildSwapTransaction(
    inputToken: string,
    outputToken: string,
    amountUsd: number,
    maxSlippageBps: number,
    userPubkey: PublicKey
  ): Promise<Transaction> {
    // Meteora swap via their SDK
    // For hackathon, we'll use Jupiter as fallback for Meteora routes
    throw new Error('Meteora direct swap not implemented - use Jupiter aggregator');
  }
}
