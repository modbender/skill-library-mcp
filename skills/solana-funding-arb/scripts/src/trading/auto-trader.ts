/**
 * Funding Arbitrage Auto Trader
 * 
 * Fully automated trading bot for cross-DEX funding rate arbitrage
 * 
 * Strategy:
 * 1. Scan funding rates on Drift and Flash Trade
 * 2. Find pairs with significant spread (long where rate is negative, short where positive)
 * 3. Open delta-neutral positions to collect funding
 * 4. Monitor and rebalance when rates change
 * 5. Close when spread reverses or DD exceeds threshold
 */

import * as fs from 'fs';
import * as path from 'path';
import { DriftClient } from './drift-client';
import { FlashClient } from './flash-client';
import { PositionManager, ArbitragePosition } from './position-manager';
import { logger } from '../utils/logger';

// Config file location
const CONFIG_PATH = path.join(process.env.HOME || '~', '.secrets', 'funding-arb-config.json');
const STATE_PATH = path.join(process.env.HOME || '~', '.clawd', 'funding-arb', 'trader-state.json');

export interface TraderConfig {
  strategy: 'ultra_safe' | 'conservative' | 'moderate';
  max_position_pct: number;      // Max % of balance per position
  min_spread: number;            // Min APY spread to open (%)
  max_dd_pct: number;            // Max drawdown before closing (%)
  auto_execute: boolean;
  dry_run: boolean;
  leverage: number;
  check_interval_hours: number;
  min_apy_threshold: number;     // Min APY on either side
  max_position_usd: number;      // Max USD per position
  notification: {
    telegram: boolean;
    on_open: boolean;
    on_close: boolean;
    on_funding: boolean;
  };
  risk: {
    max_positions: number;
    stop_loss_pct: number;
    take_profit_pct: number | null;
    auto_rebalance: boolean;
    rebalance_threshold: number;  // Close if spread drops below this
  };
}

export interface ArbitrageOpportunity {
  symbol: string;
  driftRate: number;      // APY
  flashRate: number;      // APY
  spread: number;         // Absolute spread
  recommendation: {
    driftSide: 'long' | 'short';
    flashSide: 'long' | 'short';
  };
  driftPrice: number;
  flashPrice: number;
  confidence: number;     // 0-100
}

export interface TraderState {
  lastRun: number;
  lastCheck: number;
  totalTrades: number;
  totalFundingEarned: number;
  errors: string[];
}

export class AutoTrader {
  private config: TraderConfig;
  private driftClient: DriftClient;
  private flashClient: FlashClient;
  private positionManager: PositionManager;
  private state: TraderState;
  private isRunning: boolean = false;
  
  constructor(rpcUrl: string = 'https://api.mainnet-beta.solana.com') {
    this.config = this.loadConfig();
    this.driftClient = new DriftClient(rpcUrl, this.config.dry_run);
    this.flashClient = new FlashClient(rpcUrl, this.config.dry_run);
    this.positionManager = new PositionManager();
    this.state = this.loadState();
  }

  /**
   * Load configuration
   */
  private loadConfig(): TraderConfig {
    try {
      if (fs.existsSync(CONFIG_PATH)) {
        const data = fs.readFileSync(CONFIG_PATH, 'utf-8');
        const loaded = JSON.parse(data);
        logger.info(`Config loaded from ${CONFIG_PATH}`);
        return loaded;
      }
    } catch (error: any) {
      logger.warn(`Config load error: ${error.message}`);
    }

    // Default config
    return {
      strategy: 'ultra_safe',
      max_position_pct: 50,
      min_spread: 0.5,
      max_dd_pct: 2,
      auto_execute: true,
      dry_run: true,
      leverage: 1,
      check_interval_hours: 4,
      min_apy_threshold: 100,
      max_position_usd: 100,
      notification: {
        telegram: true,
        on_open: true,
        on_close: true,
        on_funding: true
      },
      risk: {
        max_positions: 2,
        stop_loss_pct: 2,
        take_profit_pct: null,
        auto_rebalance: true,
        rebalance_threshold: 0.3
      }
    };
  }

  /**
   * Load trader state
   */
  private loadState(): TraderState {
    try {
      if (fs.existsSync(STATE_PATH)) {
        return JSON.parse(fs.readFileSync(STATE_PATH, 'utf-8'));
      }
    } catch (error) {
      // Ignore
    }
    return {
      lastRun: 0,
      lastCheck: 0,
      totalTrades: 0,
      totalFundingEarned: 0,
      errors: []
    };
  }

  /**
   * Save trader state
   */
  private saveState(): void {
    try {
      const dir = path.dirname(STATE_PATH);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(STATE_PATH, JSON.stringify(this.state, null, 2));
    } catch (error) {
      // Ignore
    }
  }

  /**
   * Initialize clients
   */
  async initialize(): Promise<boolean> {
    logger.info('═══════════════════════════════════════════════════════');
    logger.info('  Funding Arbitrage Auto Trader');
    logger.info(`  Mode: ${this.config.dry_run ? 'DRY RUN 🧪' : 'LIVE TRADING 🔴'}`);
    logger.info(`  Strategy: ${this.config.strategy.toUpperCase()}`);
    logger.info(`  Leverage: ${this.config.leverage}x`);
    logger.info('═══════════════════════════════════════════════════════');

    const walletPath = process.env.SOLANA_WALLET_PATH;
    
    const driftInit = await this.driftClient.initializeWallet(walletPath);
    const flashInit = await this.flashClient.initializeWallet(walletPath);

    if (!driftInit || !flashInit) {
      logger.error('Failed to initialize one or more clients');
      return false;
    }

    // Show wallet info
    const driftWallet = this.driftClient.getWalletAddress();
    if (driftWallet) {
      logger.info(`Wallet: ${driftWallet.slice(0, 8)}...${driftWallet.slice(-4)}`);
      
      const balance = await this.driftClient.getBalance();
      logger.info(`Balance: $${balance.toFixed(2)}`);
    }

    return true;
  }

  /**
   * Scan for arbitrage opportunities
   */
  async scanOpportunities(): Promise<ArbitrageOpportunity[]> {
    logger.info('\n📡 Scanning funding rates...');

    const [driftMarkets, flashMarkets] = await Promise.all([
      this.driftClient.getMarkets(),
      this.flashClient.getMarkets()
    ]);

    logger.info(`  Drift: ${driftMarkets.length} markets`);
    logger.info(`  Flash: ${flashMarkets.length} markets`);

    const opportunities: ArbitrageOpportunity[] = [];

    // Match markets across exchanges
    for (const driftM of driftMarkets) {
      // Normalize symbol (SOL-PERP, SOL, etc)
      const baseSymbol = driftM.symbol.replace('-PERP', '').replace('-USD', '');
      
      const flashM = flashMarkets.find(f => {
        const flashBase = f.symbol.replace('-PERP', '').replace('-USD', '');
        return flashBase === baseSymbol;
      });

      if (!flashM) continue;

      const driftApy = driftM.fundingRateApy;
      const flashApy = flashM.fundingRateApy;
      const spread = Math.abs(driftApy - flashApy);

      // Skip if spread too low
      if (spread < this.config.min_spread * 100) continue;

      // Determine sides
      // If rate is negative, longs receive funding
      // If rate is positive, shorts receive funding
      let driftSide: 'long' | 'short';
      let flashSide: 'long' | 'short';

      if (driftApy < flashApy) {
        // Drift rate lower (more negative) = go long on Drift, short on Flash
        driftSide = 'long';
        flashSide = 'short';
      } else {
        // Flash rate lower = go long on Flash, short on Drift
        driftSide = 'short';
        flashSide = 'long';
      }

      // Calculate confidence based on spread and volume
      const avgVolume = (driftM.volume24h + flashM.volume24h) / 2;
      const volumeScore = Math.min(avgVolume / 10000000, 1) * 50; // Max 50 from volume
      const spreadScore = Math.min(spread / 500, 1) * 50; // Max 50 from spread
      const confidence = Math.round(volumeScore + spreadScore);

      opportunities.push({
        symbol: baseSymbol,
        driftRate: driftApy,
        flashRate: flashApy,
        spread,
        recommendation: { driftSide, flashSide },
        driftPrice: driftM.oraclePrice,
        flashPrice: flashM.oraclePrice,
        confidence
      });
    }

    // Sort by spread descending
    opportunities.sort((a, b) => b.spread - a.spread);

    // Log opportunities
    if (opportunities.length > 0) {
      logger.info('\n💰 Arbitrage Opportunities Found:');
      logger.info('─────────────────────────────────────────────────────');
      for (const opp of opportunities.slice(0, 5)) {
        const driftEmoji = opp.driftRate < 0 ? '🟢' : '🔴';
        const flashEmoji = opp.flashRate < 0 ? '🟢' : '🔴';
        logger.info(`${opp.symbol.padEnd(6)} | Drift: ${driftEmoji} ${opp.driftRate.toFixed(0).padStart(6)}% | Flash: ${flashEmoji} ${opp.flashRate.toFixed(0).padStart(6)}% | Spread: ${opp.spread.toFixed(0)}%`);
        logger.info(`        → ${opp.recommendation.driftSide.toUpperCase()} Drift, ${opp.recommendation.flashSide.toUpperCase()} Flash`);
      }
      logger.info('─────────────────────────────────────────────────────');
    } else {
      logger.info('  No opportunities above threshold');
    }

    return opportunities;
  }

  /**
   * Execute arbitrage trade
   */
  async executeArbitrage(opp: ArbitrageOpportunity): Promise<boolean> {
    if (!this.config.auto_execute) {
      logger.info(`Auto-execute disabled, skipping ${opp.symbol}`);
      return false;
    }

    // Check if we already have position for this symbol
    if (this.positionManager.hasPosition(opp.symbol)) {
      logger.info(`Already have position for ${opp.symbol}, skipping`);
      return false;
    }

    // Check max positions
    const openPositions = this.positionManager.getOpenPositions();
    if (openPositions.length >= this.config.risk.max_positions * 2) { // *2 because each arb = 2 positions
      logger.info('Max positions reached, skipping');
      return false;
    }

    // Calculate position size
    const balance = await this.driftClient.getBalance();
    const maxFromBalance = balance * (this.config.max_position_pct / 100);
    const positionSize = Math.min(maxFromBalance, this.config.max_position_usd);

    if (positionSize < 10) {
      logger.warn('Position size too small (<$10)');
      return false;
    }

    logger.info(`\n🚀 Executing arbitrage for ${opp.symbol}`);
    logger.info(`  Position size: $${positionSize.toFixed(2)}`);
    logger.info(`  Target spread: ${opp.spread.toFixed(0)}% APY`);

    // Open positions on both exchanges
    const driftResult = await this.driftClient.openPosition(
      `${opp.symbol}-PERP`,
      opp.recommendation.driftSide,
      positionSize / 2, // Half on each exchange
      this.config.leverage
    );

    if (!driftResult.success) {
      logger.error(`Drift position failed: ${driftResult.error}`);
      return false;
    }

    const flashResult = await this.flashClient.openPosition(
      `${opp.symbol}-PERP`,
      opp.recommendation.flashSide,
      positionSize / 2,
      this.config.leverage
    );

    if (!flashResult.success) {
      logger.error(`Flash position failed: ${flashResult.error}`);
      // Should close Drift position here in production
      return false;
    }

    // Record positions
    const driftPos = this.positionManager.addPosition(
      'drift',
      opp.symbol,
      opp.recommendation.driftSide,
      (positionSize / 2) / opp.driftPrice,
      opp.driftPrice,
      driftResult.txSignature!
    );

    const flashPos = this.positionManager.addPosition(
      'flash',
      opp.symbol,
      opp.recommendation.flashSide,
      (positionSize / 2) / opp.flashPrice,
      opp.flashPrice,
      flashResult.txSignature!
    );

    // Create arbitrage record
    this.positionManager.createArbitrage(driftPos, flashPos, opp.spread);

    this.state.totalTrades += 2;
    this.saveState();

    logger.info('✅ Arbitrage positions opened successfully!');
    
    return true;
  }

  /**
   * Check and rebalance existing positions
   */
  async checkAndRebalance(): Promise<void> {
    const arbitrages = this.positionManager.getArbitrages();
    if (arbitrages.length === 0) {
      logger.debug('No open arbitrages to check');
      return;
    }

    logger.info(`\n🔄 Checking ${arbitrages.length} open arbitrage(s)...`);

    for (const arb of arbitrages) {
      await this.checkArbitrage(arb);
    }
  }

  /**
   * Check a single arbitrage position
   */
  private async checkArbitrage(arb: ArbitragePosition): Promise<void> {
    const symbol = arb.pair.long.symbol;
    logger.debug(`Checking ${symbol} arbitrage (opened: ${new Date(arb.openTime).toISOString()})`);

    // Get current rates
    const [driftMarkets, flashMarkets] = await Promise.all([
      this.driftClient.getMarkets(),
      this.flashClient.getMarkets()
    ]);

    const driftM = driftMarkets.find(m => m.symbol.includes(symbol));
    const flashM = flashMarkets.find(m => m.symbol.includes(symbol));

    if (!driftM || !flashM) {
      logger.warn(`Cannot find current data for ${symbol}`);
      return;
    }

    // Calculate current spread
    const currentSpread = Math.abs(driftM.fundingRateApy - flashM.fundingRateApy);
    const spreadChange = currentSpread - arb.targetSpread;

    logger.info(`  ${symbol}: Spread ${arb.targetSpread.toFixed(0)}% → ${currentSpread.toFixed(0)}% (${spreadChange > 0 ? '+' : ''}${spreadChange.toFixed(0)}%)`);

    // Check if spread reversed or dropped below threshold
    if (currentSpread < this.config.risk.rebalance_threshold * 100) {
      logger.warn(`  ⚠️ Spread dropped below threshold (${(this.config.risk.rebalance_threshold * 100).toFixed(0)}%)`);
      
      if (this.config.risk.auto_rebalance) {
        logger.info(`  Closing arbitrage...`);
        await this.closeArbitrage(arb);
        return;
      }
    }

    // Check max drawdown
    const dd = this.positionManager.calculateMaxDrawdown();
    if (dd > this.config.max_dd_pct) {
      logger.warn(`  ⚠️ Max drawdown exceeded: ${dd.toFixed(2)}% > ${this.config.max_dd_pct}%`);
      
      if (this.config.auto_execute) {
        logger.info(`  Closing arbitrage...`);
        await this.closeArbitrage(arb);
      }
    }
  }

  /**
   * Close an arbitrage position
   */
  async closeArbitrage(arb: ArbitragePosition): Promise<boolean> {
    logger.info(`\n❌ Closing arbitrage: ${arb.pair.long.symbol}`);

    // Close both legs
    const driftResult = await this.driftClient.closePosition(`${arb.pair.long.symbol}-PERP`);
    const flashResult = await this.flashClient.closePosition(`${arb.pair.short.symbol}-PERP`);

    if (!driftResult.success || !flashResult.success) {
      logger.error('Failed to close one or more positions');
      return false;
    }

    // Get current prices for PnL calculation
    const driftMarkets = await this.driftClient.getMarkets();
    const driftM = driftMarkets.find(m => m.symbol.includes(arb.pair.long.symbol));
    const exitPrice = driftM?.oraclePrice || arb.pair.long.entryPrice;

    // Close positions in manager
    this.positionManager.closePosition(arb.pair.long.id, exitPrice, driftResult.txSignature!);
    this.positionManager.closePosition(arb.pair.short.id, exitPrice, flashResult.txSignature!);
    this.positionManager.closeArbitrage(arb.id);

    logger.info('✅ Arbitrage closed');
    return true;
  }

  /**
   * Main run loop
   */
  async run(): Promise<void> {
    const initialized = await this.initialize();
    if (!initialized) {
      logger.error('Initialization failed');
      return;
    }

    this.isRunning = true;
    this.state.lastRun = Date.now();

    try {
      // 1. Check existing positions
      await this.checkAndRebalance();

      // 2. Scan for new opportunities
      const opportunities = await this.scanOpportunities();

      // 3. Execute best opportunity if conditions met
      if (opportunities.length > 0) {
        const best = opportunities[0];
        
        if (best.spread >= this.config.min_spread * 100 && best.confidence >= 60) {
          await this.executeArbitrage(best);
        }
      }

      // 4. Print summary
      this.printSummary();

    } catch (error: any) {
      logger.error(`Run error: ${error.message}`);
      this.state.errors.push(`${new Date().toISOString()}: ${error.message}`);
      if (this.state.errors.length > 100) {
        this.state.errors = this.state.errors.slice(-100);
      }
    } finally {
      this.state.lastCheck = Date.now();
      this.saveState();
    }
  }

  /**
   * Print position summary
   */
  printSummary(): void {
    const summary = this.positionManager.getSummary();
    const stats = this.positionManager.getTotalStats();

    logger.info('\n📊 Portfolio Summary');
    logger.info('─────────────────────────────────────────────────────');
    logger.info(`  Open Positions: ${summary.totalPositions}`);
    logger.info(`  Total Notional: $${summary.totalNotional.toFixed(2)}`);
    logger.info(`  Unrealized PnL: $${summary.totalUnrealizedPnl.toFixed(2)}`);
    logger.info(`  Funding Collected: $${summary.totalFunding.toFixed(2)}`);
    logger.info(`  Lifetime PnL: $${stats.total.toFixed(2)}`);
    logger.info('─────────────────────────────────────────────────────');

    if (summary.totalPositions > 0) {
      const positions = this.positionManager.getOpenPositions();
      for (const pos of positions) {
        const pnlEmoji = (pos.unrealizedPnl || 0) >= 0 ? '🟢' : '🔴';
        logger.info(`  ${pos.exchange.padEnd(6)} ${pos.side.toUpperCase().padEnd(5)} ${pos.symbol.padEnd(8)} $${pos.notional.toFixed(0).padStart(6)} ${pnlEmoji} $${(pos.unrealizedPnl || 0).toFixed(2)}`);
      }
    }
  }

  /**
   * Stop the trader
   */
  stop(): void {
    this.isRunning = false;
    logger.info('Trader stopped');
  }

  /**
   * Get current config
   */
  getConfig(): TraderConfig {
    return this.config;
  }

  /**
   * Update config
   */
  updateConfig(updates: Partial<TraderConfig>): void {
    this.config = { ...this.config, ...updates };
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(this.config, null, 2));
    logger.info('Config updated');
  }
}

// Main entry point when run directly
async function main() {
  const args = process.argv.slice(2);
  const rpcUrl = process.env.SOLANA_RPC_URL || 'https://api.mainnet-beta.solana.com';
  
  const trader = new AutoTrader(rpcUrl);

  if (args.includes('--scan-only')) {
    // Just scan, don't trade
    await trader.initialize();
    await trader.scanOpportunities();
    return;
  }

  if (args.includes('--status')) {
    // Show current status
    await trader.initialize();
    trader.printSummary();
    return;
  }

  // Full run
  await trader.run();
}

main().catch(error => {
  logger.error(`Fatal error: ${error.message}`);
  process.exit(1);
});

export default AutoTrader;
