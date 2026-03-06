/**
 * Raydium DEX Integration
 * 
 * Raydium is one of Solana's largest AMM DEXes.
 */

import { Connection, PublicKey, Transaction } from '@solana/web3.js';
import axios from 'axios';
import { DexInterface, PriceQuote, getTokenMint, getTokenDecimals } from '../types';
import { logger } from '../utils/logger';

const RAYDIUM_API = 'https://api-v3.raydium.io';

export class RaydiumDex implements DexInterface {
  name = 'raydium';
  private connection: Connection;

  constructor(connection: Connection) {
    this.connection = connection;
  }

  async getQuote(baseToken: string, quoteToken: string, amountUsd: number): Promise<PriceQuote | null> {
    try {
      const inputMint = getTokenMint(quoteToken);
      const outputMint = getTokenMint(baseToken);
      const inputDecimals = getTokenDecimals(quoteToken);
      
      // Get pool info
      const poolResponse = await axios.get(`${RAYDIUM_API}/pools/info/mint`, {
        params: {
          mint1: inputMint,
          mint2: outputMint,
          poolType: 'all',
          poolSortField: 'liquidity',
          sortType: 'desc',
          pageSize: 1
        }
      });

      const pool = poolResponse.data?.data?.data?.[0];
      if (!pool) return null;

      // Calculate price from pool reserves
      const reserve1 = parseFloat(pool.mintAmountA);
      const reserve2 = parseFloat(pool.mintAmountB);
      
      const isToken1Input = pool.mintA === inputMint;
      const inputReserve = isToken1Input ? reserve1 : reserve2;
      const outputReserve = isToken1Input ? reserve2 : reserve1;
      
      // AMM price calculation with 0.25% fee
      const fee = 0.0025;
      const inputAmount = amountUsd; // Simplified
      const outputAmount = (outputReserve * inputAmount * (1 - fee)) / (inputReserve + inputAmount);
      
      const buyPrice = inputAmount / outputAmount;
      const sellPrice = buyPrice * (1 - fee * 2); // Approximate sell price with fees

      return {
        dex: this.name,
        baseToken,
        quoteToken,
        buyPrice,
        sellPrice,
        liquidity: parseFloat(pool.tvl) || amountUsd * 10,
        timestamp: Date.now()
      };
    } catch (error: any) {
      logger.debug(`Raydium quote error: ${error.message}`);
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
    
    // Get swap quote
    const quoteResponse = await axios.get(`${RAYDIUM_API}/compute/swap-base-in`, {
      params: {
        inputMint,
        outputMint,
        amount: Math.floor(amountUsd * Math.pow(10, inputDecimals)),
        slippageBps: maxSlippageBps,
        txVersion: 'V0'
      }
    });

    if (!quoteResponse.data?.data) {
      throw new Error('Failed to get Raydium quote');
    }

    // Get swap transaction
    const swapResponse = await axios.post(`${RAYDIUM_API}/transaction/swap-base-in`, {
      computeBudgetConfig: {
        units: 300000,
        microLamports: 50000
      },
      swapResponse: quoteResponse.data.data,
      wallet: userPubkey.toBase58(),
      wrapSol: true,
      unwrapSol: true
    });

    if (!swapResponse.data?.data?.[0]?.transaction) {
      throw new Error('Failed to get Raydium swap transaction');
    }

    const txBuf = Buffer.from(swapResponse.data.data[0].transaction, 'base64');
    return Transaction.from(txBuf);
  }
}
