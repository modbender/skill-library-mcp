/**
 * Orca DEX Integration
 * 
 * Orca Whirlpools - concentrated liquidity pools on Solana.
 */

import { Connection, PublicKey, Transaction } from '@solana/web3.js';
import axios from 'axios';
import { DexInterface, PriceQuote, getTokenMint, getTokenDecimals } from '../types';
import { logger } from '../utils/logger';

const ORCA_API = 'https://api.mainnet.orca.so';

export class OrcaDex implements DexInterface {
  name = 'orca';
  private connection: Connection;

  constructor(connection: Connection) {
    this.connection = connection;
  }

  async getQuote(baseToken: string, quoteToken: string, amountUsd: number): Promise<PriceQuote | null> {
    try {
      const inputMint = getTokenMint(quoteToken);
      const outputMint = getTokenMint(baseToken);
      const inputDecimals = getTokenDecimals(quoteToken);
      
      // Get quote from Orca
      const response = await axios.get(`${ORCA_API}/v1/quote`, {
        params: {
          inputMint,
          outputMint,
          amount: Math.floor(amountUsd * Math.pow(10, inputDecimals)),
          slippageBps: 50,
          swapMode: 'ExactIn'
        }
      });

      if (!response.data) return null;

      const quote = response.data;
      const outputAmount = parseInt(quote.outAmount || quote.outputAmount || '0');
      const outputDecimals = getTokenDecimals(baseToken);
      
      const inputAmount = amountUsd * Math.pow(10, inputDecimals);
      const buyPrice = inputAmount / outputAmount * Math.pow(10, outputDecimals - inputDecimals);
      
      // Estimate sell price (reverse direction with fees)
      const sellPrice = buyPrice * 0.994; // ~0.6% spread for safety

      return {
        dex: this.name,
        baseToken,
        quoteToken,
        buyPrice,
        sellPrice,
        liquidity: amountUsd * 50,
        timestamp: Date.now()
      };
    } catch (error: any) {
      logger.debug(`Orca quote error: ${error.message}`);
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
    const inputMint = getTokenMint(inputToken);
    const outputMint = getTokenMint(outputToken);
    const inputDecimals = getTokenDecimals(inputToken);
    
    const response = await axios.post(`${ORCA_API}/v1/swap`, {
      inputMint,
      outputMint,
      amount: Math.floor(amountUsd * Math.pow(10, inputDecimals)),
      slippageBps: maxSlippageBps,
      swapMode: 'ExactIn',
      userPublicKey: userPubkey.toBase58()
    });

    if (!response.data?.transaction) {
      throw new Error('Failed to get Orca swap transaction');
    }

    const txBuf = Buffer.from(response.data.transaction, 'base64');
    return Transaction.from(txBuf);
  }
}
