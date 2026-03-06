/**
 * Jupiter DEX Integration
 * 
 * Jupiter is Solana's leading DEX aggregator, providing best prices across all DEXes.
 */

import { Connection, PublicKey, Transaction, VersionedTransaction } from '@solana/web3.js';
import axios from 'axios';
import { DexInterface, PriceQuote, getTokenMint, getTokenDecimals } from '../types';
import { logger } from '../utils/logger';

const JUPITER_API = 'https://quote-api.jup.ag/v6';
const JUPITER_PRICE_API = 'https://price.jup.ag/v6';

export class JupiterDex implements DexInterface {
  name = 'jupiter';
  private connection: Connection;

  constructor(connection: Connection) {
    this.connection = connection;
  }

  /**
   * Get price quote from Jupiter
   */
  async getQuote(baseToken: string, quoteToken: string, amountUsd: number): Promise<PriceQuote | null> {
    try {
      const inputMint = getTokenMint(quoteToken);  // We're buying base with quote
      const outputMint = getTokenMint(baseToken);
      const inputDecimals = getTokenDecimals(quoteToken);
      
      // Get quote token price to convert USD to token amount
      const quotePrice = await this.getTokenPrice(quoteToken);
      const inputAmount = Math.floor((amountUsd / quotePrice) * Math.pow(10, inputDecimals));

      // Get buy quote (quote -> base)
      const buyResponse = await axios.get(`${JUPITER_API}/quote`, {
        params: {
          inputMint,
          outputMint,
          amount: inputAmount.toString(),
          slippageBps: 50
        }
      });

      if (!buyResponse.data) return null;

      const buyQuote = buyResponse.data;
      const outputAmount = parseInt(buyQuote.outAmount);
      const outputDecimals = getTokenDecimals(baseToken);
      
      // Calculate buy price (how much quote for 1 base)
      const buyPrice = (inputAmount / Math.pow(10, inputDecimals)) / 
                       (outputAmount / Math.pow(10, outputDecimals));

      // Get sell quote (base -> quote) for sell price
      const sellInputAmount = outputAmount; // Use what we'd get from buying
      const sellResponse = await axios.get(`${JUPITER_API}/quote`, {
        params: {
          inputMint: outputMint,
          outputMint: inputMint,
          amount: sellInputAmount.toString(),
          slippageBps: 50
        }
      });

      if (!sellResponse.data) return null;

      const sellQuote = sellResponse.data;
      const sellOutputAmount = parseInt(sellQuote.outAmount);
      
      // Calculate sell price (how much quote for 1 base)
      const sellPrice = (sellOutputAmount / Math.pow(10, inputDecimals)) /
                        (sellInputAmount / Math.pow(10, outputDecimals));

      return {
        dex: this.name,
        baseToken,
        quoteToken,
        buyPrice,
        sellPrice,
        liquidity: amountUsd * 100, // Jupiter has deep liquidity
        timestamp: Date.now()
      };
    } catch (error: any) {
      logger.debug(`Jupiter quote error: ${error.message}`);
      return null;
    }
  }

  /**
   * Build swap transaction using Jupiter
   */
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
    
    // Get token price
    const inputPrice = await this.getTokenPrice(inputToken);
    const inputAmount = Math.floor((amountUsd / inputPrice) * Math.pow(10, inputDecimals));

    // Get quote
    const quoteResponse = await axios.get(`${JUPITER_API}/quote`, {
      params: {
        inputMint,
        outputMint,
        amount: inputAmount.toString(),
        slippageBps: maxSlippageBps
      }
    });

    if (!quoteResponse.data) {
      throw new Error('Failed to get Jupiter quote');
    }

    // Get swap transaction
    const swapResponse = await axios.post(`${JUPITER_API}/swap`, {
      quoteResponse: quoteResponse.data,
      userPublicKey: userPubkey.toBase58(),
      wrapAndUnwrapSol: true,
      dynamicComputeUnitLimit: true,
      prioritizationFeeLamports: 'auto'
    });

    if (!swapResponse.data?.swapTransaction) {
      throw new Error('Failed to get Jupiter swap transaction');
    }

    // Deserialize transaction
    const swapTransactionBuf = Buffer.from(swapResponse.data.swapTransaction, 'base64');
    const transaction = VersionedTransaction.deserialize(swapTransactionBuf);
    
    // Convert to legacy Transaction for signing
    // Note: In production, you'd want to handle versioned transactions properly
    return Transaction.from(transaction.serialize());
  }

  /**
   * Get token price in USD
   */
  async getTokenPrice(symbol: string): Promise<number> {
    try {
      if (symbol === 'USDC' || symbol === 'USDT') return 1;
      
      const mint = getTokenMint(symbol);
      const response = await axios.get(`${JUPITER_PRICE_API}/price`, {
        params: { ids: mint }
      });
      
      return response.data?.data?.[mint]?.price || 0;
    } catch {
      return 0;
    }
  }

  /**
   * Get prices for multiple tokens
   */
  async getMultiplePrices(symbols: string[]): Promise<Record<string, number>> {
    const mints = symbols.map(s => getTokenMint(s));
    
    try {
      const response = await axios.get(`${JUPITER_PRICE_API}/price`, {
        params: { ids: mints.join(',') }
      });
      
      const prices: Record<string, number> = {};
      for (let i = 0; i < symbols.length; i++) {
        prices[symbols[i]] = response.data?.data?.[mints[i]]?.price || 0;
      }
      
      return prices;
    } catch {
      return {};
    }
  }
}
