/**
 * Funding Rate Arbitrage Engine
 * 
 * Captures funding rate opportunities through delta-neutral positions.
 */

import { Connection, Keypair, PublicKey } from '@solana/web3.js';
import { DriftProtocol, FundingRate } from '../protocols/drift';
import { JupiterDex } from '../dex/jupiter';
import { PnLTracker } from './pnl-tracker';
import { logger } from '../utils/logger';

export interface FundingArbConfig {
  rpcUrl: string;
  wallet: Keypair;
  minFundingApy: number;      // Minimum APY to enter (e.g., 20 = 20%)
  maxPositionUsd: number;      // Max position size
  markets: string[];           // Markets to monitor
  checkIntervalMs: number;     // How often to check rates
  exitApyThreshold: number;    // Exit when APY drops below this
}

export interface OpenPosition {
  market: string;
  perpSide: 'long' | 'short';
  perpSize: number;           // USD value
  spotSize: number;           // USD value (hedge)
  entryFundingApy: number;
  entryTime: number;
  accumulatedFunding: number;
}

export class FundingArbitrageEngine {
  private connection: Connection;
  private config: FundingArbConfig;
  private drift: DriftProtocol;
  private jupiter: JupiterDex;
  private pnlTracker: PnLTracker;
  private positions: Map<string, OpenPosition> = new Map();
  private isRunning: boolean = false;

  constructor(config: FundingArbConfig) {
    this.config = config;
    this.connection = new Connection(config.rpcUrl, 'confirmed');
    this.drift = new DriftProtocol(this.connection, config.wallet);
    this.jupiter = new JupiterDex(this.connection);
    this.pnlTracker = new PnLTracker();
  }

  /**
   * Start the funding arbitrage bot
   */
  async start(): Promise<void> {
    this.isRunning = true;
    
    console.log(`
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   ███████╗ ██████╗ ██╗      █████╗ ██████╗ ██████╗   ║
║   ██╔════╝██╔═══██╗██║     ██╔══██╗██╔══██╗██╔══██╗  ║
║   ███████╗██║   ██║██║     ███████║██████╔╝██████╔╝  ║
║   ╚════██║██║   ██║██║     ██╔══██║██╔══██╗██╔══██╗  ║
║   ███████║╚██████╔╝███████╗██║  ██║██║  ██║██████╔╝  ║
║   ╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝   ║
║                                                       ║
║         Funding Rate Arbitrage Agent                  ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
    `);

    logger.info('🚀 Funding Arbitrage Engine started');
    logger.info(`Monitoring ${this.config.markets.length} markets`);
    logger.info(`Min APY: ${this.config.minFundingApy}%`);
    logger.info(`Max Position: $${this.config.maxPositionUsd}`);

    while (this.isRunning) {
      try {
        await this.checkAndExecute();
        await this.sleep(this.config.checkIntervalMs);
      } catch (error: any) {
        logger.error(`Engine error: ${error.message}`);
        await this.sleep(10000);
      }
    }
  }

  /**
   * Stop the engine
   */
  stop(): void {
    this.isRunning = false;
    logger.info('Funding Arbitrage Engine stopped');
  }

  /**
   * Main check and execute loop
   */
  private async checkAndExecute(): Promise<void> {
    // Get current funding rates
    const fundingRates = await this.drift.getFundingRates();
    
    // Filter for monitored markets
    const relevantRates = fundingRates.filter(r => 
      this.config.markets.includes(r.market)
    );

    // Check existing positions - should we exit?
    for (const [market, position] of this.positions.entries()) {
      const currentRate = relevantRates.find(r => r.market === market);
      
      if (currentRate) {
        // Update accumulated funding estimate
        const hoursSinceEntry = (Date.now() - position.entryTime) / (60 * 60 * 1000);
        position.accumulatedFunding = this.drift.calculateExpectedFunding(
          position.perpSize,
          currentRate.fundingRate,
          hoursSinceEntry
        );

        // Check exit condition
        if (Math.abs(currentRate.fundingRateApy) < this.config.exitApyThreshold) {
          logger.info(`📉 ${market} funding dropped to ${currentRate.fundingRateApy.toFixed(1)}% APY - exiting`);
          await this.closePosition(market);
        }
      }
    }

    // Look for new opportunities
    for (const rate of relevantRates) {
      // Skip if already have position
      if (this.positions.has(rate.market)) continue;

      // Skip if APY too low
      if (Math.abs(rate.fundingRateApy) < this.config.minFundingApy) continue;

      // Found opportunity!
      logger.info(`🎯 Found opportunity: ${rate.market} at ${rate.fundingRateApy.toFixed(1)}% APY`);
      await this.openPosition(rate);
    }
  }

  /**
   * Open a funding arbitrage position
   */
  private async openPosition(rate: FundingRate): Promise<void> {
    const market = rate.market;
    const baseAsset = market.replace('-PERP', '');

    // Determine direction: go opposite of funding payers
    // If longs pay shorts (positive funding), we SHORT perp and LONG spot
    // If shorts pay longs (negative funding), we LONG perp and SHORT spot
    const perpSide: 'long' | 'short' = rate.longPayShort ? 'short' : 'long';
    const sizeUsd = this.config.maxPositionUsd;

    logger.info(`Opening ${perpSide.toUpperCase()} ${market} perp + ${perpSide === 'short' ? 'LONG' : 'SHORT'} ${baseAsset} spot`);

    try {
      // 1. Open perp position
      const perpResult = await this.drift.openPosition(market, perpSide, sizeUsd);
      if (!perpResult.success) {
        logger.error(`Failed to open perp: ${perpResult.error}`);
        return;
      }
      logger.success(`Perp position opened: ${perpResult.txSignature}`);

      // 2. Open spot hedge (via Jupiter swap)
      // For SHORT perp, we buy spot (long)
      // For LONG perp, we sell spot (short) - need to borrow, skip for simplicity
      if (perpSide === 'short') {
        // Buy spot to hedge
        const spotTx = await this.jupiter.buildSwapTransaction(
          'USDC',
          baseAsset,
          sizeUsd,
          100, // 1% slippage
          this.config.wallet.publicKey
        );
        
        // Sign and send
        spotTx.recentBlockhash = (await this.connection.getLatestBlockhash()).blockhash;
        spotTx.sign(this.config.wallet);
        const spotSig = await this.connection.sendRawTransaction(spotTx.serialize());
        await this.connection.confirmTransaction(spotSig);
        logger.success(`Spot hedge opened: ${spotSig}`);
      }

      // Record position
      this.positions.set(market, {
        market,
        perpSide,
        perpSize: sizeUsd,
        spotSize: sizeUsd,
        entryFundingApy: rate.fundingRateApy,
        entryTime: Date.now(),
        accumulatedFunding: 0
      });

      logger.info(`✅ Position opened: ${market} | ${perpSide.toUpperCase()} perp + hedge`);
      logger.info(`   Expected APY: ${rate.fundingRateApy.toFixed(1)}%`);

    } catch (error: any) {
      logger.error(`Failed to open position: ${error.message}`);
    }
  }

  /**
   * Close a funding arbitrage position
   */
  private async closePosition(market: string): Promise<void> {
    const position = this.positions.get(market);
    if (!position) return;

    const baseAsset = market.replace('-PERP', '');

    try {
      // 1. Close perp position
      const perpResult = await this.drift.closePosition(market);
      if (!perpResult.success) {
        logger.error(`Failed to close perp: ${perpResult.error}`);
        return;
      }

      // 2. Close spot hedge
      if (position.perpSide === 'short') {
        // Sell spot back to USDC
        const spotTx = await this.jupiter.buildSwapTransaction(
          baseAsset,
          'USDC',
          position.spotSize,
          100,
          this.config.wallet.publicKey
        );
        
        spotTx.recentBlockhash = (await this.connection.getLatestBlockhash()).blockhash;
        spotTx.sign(this.config.wallet);
        const spotSig = await this.connection.sendRawTransaction(spotTx.serialize());
        await this.connection.confirmTransaction(spotSig);
      }

      // Calculate profit
      const holdingHours = (Date.now() - position.entryTime) / (60 * 60 * 1000);
      const estimatedProfit = position.accumulatedFunding;

      logger.success(`Position closed: ${market}`);
      logger.info(`   Held for: ${holdingHours.toFixed(1)} hours`);
      logger.info(`   Estimated funding earned: $${estimatedProfit.toFixed(2)}`);

      // Remove from tracking
      this.positions.delete(market);

    } catch (error: any) {
      logger.error(`Failed to close position: ${error.message}`);
    }
  }

  /**
   * Get current status
   */
  getStatus(): {
    isRunning: boolean;
    positions: OpenPosition[];
    totalValue: number;
    totalFundingEarned: number;
  } {
    const positionList = Array.from(this.positions.values());
    const totalValue = positionList.reduce((sum, p) => sum + p.perpSize, 0);
    const totalFunding = positionList.reduce((sum, p) => sum + p.accumulatedFunding, 0);

    return {
      isRunning: this.isRunning,
      positions: positionList,
      totalValue,
      totalFundingEarned: totalFunding
    };
  }

  /**
   * Scan and display opportunities (without executing)
   */
  async scanOpportunities(): Promise<void> {
    console.log('\n🔍 Scanning funding rate opportunities...\n');

    const summary = await this.drift.getFundingSummary();
    console.log(summary);

    const rates = await this.drift.getFundingRates();
    const opportunities = rates.filter(r => 
      this.config.markets.includes(r.market) &&
      Math.abs(r.fundingRateApy) >= this.config.minFundingApy
    );

    if (opportunities.length === 0) {
      console.log('\n❌ No opportunities above threshold');
      console.log(`   Min APY required: ${this.config.minFundingApy}%`);
    } else {
      console.log(`\n✅ Found ${opportunities.length} opportunities:\n`);
      
      for (const opp of opportunities) {
        const direction = opp.longPayShort ? 'SHORT perp + LONG spot' : 'LONG perp + SHORT spot';
        const dailyReturn = (opp.fundingRateApy / 365).toFixed(3);
        
        console.log(`   ${opp.market}`);
        console.log(`   Strategy: ${direction}`);
        console.log(`   APY: ${opp.fundingRateApy.toFixed(1)}% (~${dailyReturn}% daily)`);
        console.log(`   $1000 position → ~$${(1000 * parseFloat(dailyReturn) / 100).toFixed(2)}/day`);
        console.log('');
      }
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
