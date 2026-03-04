/**
 * SolArb - Cross-DEX Arbitrage Engine
 * 
 * Finds and executes profitable arbitrage opportunities across Solana DEXes.
 */

import { Connection, PublicKey, Transaction, Keypair } from '@solana/web3.js';
import { JupiterDex } from '../dex/jupiter';
import { RaydiumDex } from '../dex/raydium';
import { OrcaDex } from '../dex/orca';
import { MeteoraDex } from '../dex/meteora';
import { PriceQuote, ArbitrageOpportunity, TradeResult, DexInterface } from '../types';
import { logger } from '../utils/logger';
import { PnLTracker } from './pnl-tracker';

export interface ArbitrageConfig {
  rpcUrl: string;
  wallet: Keypair;
  minProfitBps: number;      // Minimum profit in basis points (e.g., 10 = 0.1%)
  maxSlippageBps: number;    // Maximum allowed slippage
  maxPositionUsd: number;    // Maximum position size in USD
  pairs: string[];           // Trading pairs to monitor
  scanIntervalMs: number;    // How often to scan for opportunities
}

export class ArbitrageEngine {
  private connection: Connection;
  private config: ArbitrageConfig;
  private dexes: Map<string, DexInterface> = new Map();
  private pnlTracker: PnLTracker;
  private isRunning: boolean = false;

  constructor(config: ArbitrageConfig) {
    this.config = config;
    this.connection = new Connection(config.rpcUrl, 'confirmed');
    this.pnlTracker = new PnLTracker();
    
    // Initialize DEXes
    this.initializeDexes();
  }

  private initializeDexes(): void {
    this.dexes.set('jupiter', new JupiterDex(this.connection));
    this.dexes.set('raydium', new RaydiumDex(this.connection));
    this.dexes.set('orca', new OrcaDex(this.connection));
    this.dexes.set('meteora', new MeteoraDex(this.connection));
    
    logger.info(`Initialized ${this.dexes.size} DEXes`);
  }

  /**
   * Start the arbitrage scanner
   */
  async start(): Promise<void> {
    this.isRunning = true;
    logger.info('🚀 SolArb Arbitrage Engine started');
    logger.info(`Monitoring ${this.config.pairs.length} pairs across ${this.dexes.size} DEXes`);
    
    while (this.isRunning) {
      try {
        await this.scanAndExecute();
        await this.sleep(this.config.scanIntervalMs);
      } catch (error) {
        logger.error('Scan error:', error);
        await this.sleep(5000); // Wait before retry
      }
    }
  }

  /**
   * Stop the arbitrage scanner
   */
  stop(): void {
    this.isRunning = false;
    logger.info('SolArb stopped');
  }

  /**
   * Scan all pairs across all DEXes for arbitrage opportunities
   */
  async scanAndExecute(): Promise<void> {
    const opportunities: ArbitrageOpportunity[] = [];

    for (const pair of this.config.pairs) {
      const [baseToken, quoteToken] = pair.split('/');
      const quotes = await this.getAllQuotes(baseToken, quoteToken);
      
      // Find arbitrage opportunities
      const arb = this.findArbitrage(quotes, pair);
      if (arb) {
        opportunities.push(arb);
      }
    }

    // Sort by profit and execute best opportunity
    if (opportunities.length > 0) {
      opportunities.sort((a, b) => b.profitBps - a.profitBps);
      const best = opportunities[0];
      
      if (best.profitBps >= this.config.minProfitBps) {
        logger.info(`🎯 Found opportunity: ${best.pair} - ${best.profitBps} bps profit`);
        await this.executeArbitrage(best);
      }
    }
  }

  /**
   * Get quotes from all DEXes for a trading pair
   */
  private async getAllQuotes(baseToken: string, quoteToken: string): Promise<Map<string, PriceQuote>> {
    const quotes = new Map<string, PriceQuote>();
    
    const promises = Array.from(this.dexes.entries()).map(async ([name, dex]) => {
      try {
        const quote = await dex.getQuote(baseToken, quoteToken, this.config.maxPositionUsd);
        if (quote) {
          quotes.set(name, quote);
        }
      } catch (error) {
        logger.debug(`${name} quote failed for ${baseToken}/${quoteToken}`);
      }
    });
    
    await Promise.all(promises);
    return quotes;
  }

  /**
   * Find arbitrage opportunity from quotes
   */
  private findArbitrage(quotes: Map<string, PriceQuote>, pair: string): ArbitrageOpportunity | null {
    if (quotes.size < 2) return null;

    let bestBuy: { dex: string; quote: PriceQuote } | null = null;
    let bestSell: { dex: string; quote: PriceQuote } | null = null;

    // Find lowest buy price and highest sell price
    for (const [dex, quote] of quotes.entries()) {
      if (!bestBuy || quote.buyPrice < bestBuy.quote.buyPrice) {
        bestBuy = { dex, quote };
      }
      if (!bestSell || quote.sellPrice > bestSell.quote.sellPrice) {
        bestSell = { dex, quote };
      }
    }

    if (!bestBuy || !bestSell || bestBuy.dex === bestSell.dex) {
      return null;
    }

    // Calculate profit
    const profitBps = Math.floor(
      ((bestSell.quote.sellPrice - bestBuy.quote.buyPrice) / bestBuy.quote.buyPrice) * 10000
    );

    if (profitBps <= 0) return null;

    return {
      pair,
      buyDex: bestBuy.dex,
      sellDex: bestSell.dex,
      buyPrice: bestBuy.quote.buyPrice,
      sellPrice: bestSell.quote.sellPrice,
      profitBps,
      estimatedProfitUsd: (profitBps / 10000) * this.config.maxPositionUsd,
      timestamp: Date.now()
    };
  }

  /**
   * Execute an arbitrage trade
   */
  private async executeArbitrage(opportunity: ArbitrageOpportunity): Promise<TradeResult> {
    const startTime = Date.now();
    
    try {
      const buyDex = this.dexes.get(opportunity.buyDex)!;
      const sellDex = this.dexes.get(opportunity.sellDex)!;
      const [baseToken, quoteToken] = opportunity.pair.split('/');

      logger.info(`Executing: Buy on ${opportunity.buyDex}, Sell on ${opportunity.sellDex}`);

      // Build and execute buy transaction
      const buyTx = await buyDex.buildSwapTransaction(
        quoteToken,
        baseToken,
        this.config.maxPositionUsd,
        this.config.maxSlippageBps,
        this.config.wallet.publicKey
      );

      // Build and execute sell transaction
      const sellTx = await sellDex.buildSwapTransaction(
        baseToken,
        quoteToken,
        this.config.maxPositionUsd,
        this.config.maxSlippageBps,
        this.config.wallet.publicKey
      );

      // Execute atomically (in sequence for safety)
      const buyResult = await this.sendTransaction(buyTx);
      if (!buyResult.success) {
        throw new Error(`Buy failed: ${buyResult.error}`);
      }

      const sellResult = await this.sendTransaction(sellTx);
      if (!sellResult.success) {
        // TODO: Handle partial execution - may need to manually close position
        logger.error('CRITICAL: Sell failed after buy succeeded!');
        throw new Error(`Sell failed: ${sellResult.error}`);
      }

      const result: TradeResult = {
        success: true,
        opportunity,
        buyTxSignature: buyResult.signature!,
        sellTxSignature: sellResult.signature!,
        actualProfitUsd: opportunity.estimatedProfitUsd, // TODO: Calculate actual
        executionTimeMs: Date.now() - startTime
      };

      // Track P&L
      this.pnlTracker.recordTrade(result);
      logger.info(`✅ Arbitrage executed! Profit: $${result.actualProfitUsd.toFixed(2)}`);
      
      return result;
    } catch (error: any) {
      const result: TradeResult = {
        success: false,
        opportunity,
        error: error.message,
        executionTimeMs: Date.now() - startTime
      };
      
      this.pnlTracker.recordTrade(result);
      logger.error(`❌ Arbitrage failed: ${error.message}`);
      
      return result;
    }
  }

  /**
   * Send a transaction to the network
   */
  private async sendTransaction(transaction: Transaction): Promise<{ success: boolean; signature?: string; error?: string }> {
    try {
      transaction.recentBlockhash = (await this.connection.getLatestBlockhash()).blockhash;
      transaction.sign(this.config.wallet);
      
      const signature = await this.connection.sendRawTransaction(transaction.serialize(), {
        skipPreflight: true,
        maxRetries: 3
      });
      
      await this.connection.confirmTransaction(signature, 'confirmed');
      
      return { success: true, signature };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Get current P&L statistics
   */
  getPnLStats() {
    return this.pnlTracker.getStats();
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
