/**
 * Position Manager
 * 
 * Tracks all open positions, calculates PnL, monitors funding collected
 */

import * as fs from 'fs';
import * as path from 'path';
import { logger } from '../utils/logger';

// State file location
const STATE_DIR = path.join(process.env.HOME || '~', '.clawd', 'funding-arb');
const STATE_FILE = path.join(STATE_DIR, 'positions.json');
const HISTORY_FILE = path.join(STATE_DIR, 'history.json');

export interface Position {
  id: string;
  exchange: 'drift' | 'flash';
  symbol: string;
  side: 'long' | 'short';
  size: number;           // Base amount
  notional: number;       // USD value
  entryPrice: number;
  openTime: number;       // Unix timestamp
  txSignature: string;
  
  // Live data (updated on sync)
  currentPrice?: number;
  unrealizedPnl?: number;
  fundingCollected?: number;
  lastUpdate?: number;
}

export interface ArbitragePosition {
  id: string;
  pair: {
    long: Position;   // Platform where we go long (receive funding when rate negative)
    short: Position;  // Platform where we go short (receive funding when rate positive)
  };
  openTime: number;
  totalNotional: number;
  targetSpread: number;   // APY spread when opened
  
  // Live PnL tracking
  totalPnl?: number;
  totalFunding?: number;
  status: 'open' | 'closing' | 'closed';
}

export interface PositionState {
  positions: Position[];
  arbitrages: ArbitragePosition[];
  lastUpdate: number;
  totalFundingCollected: number;
  totalRealizedPnl: number;
}

export interface TradeHistory {
  id: string;
  type: 'open' | 'close';
  exchange: 'drift' | 'flash';
  symbol: string;
  side: 'long' | 'short';
  size: number;
  price: number;
  time: number;
  txSignature: string;
  pnl?: number;
  funding?: number;
}

export class PositionManager {
  private state: PositionState;
  private history: TradeHistory[];
  
  constructor() {
    this.ensureStateDir();
    this.state = this.loadState();
    this.history = this.loadHistory();
  }

  /**
   * Ensure state directory exists
   */
  private ensureStateDir(): void {
    if (!fs.existsSync(STATE_DIR)) {
      fs.mkdirSync(STATE_DIR, { recursive: true });
      logger.info(`Created state directory: ${STATE_DIR}`);
    }
  }

  /**
   * Load position state from file
   */
  private loadState(): PositionState {
    try {
      if (fs.existsSync(STATE_FILE)) {
        const data = fs.readFileSync(STATE_FILE, 'utf-8');
        return JSON.parse(data);
      }
    } catch (error: any) {
      logger.warn(`Failed to load state: ${error.message}`);
    }

    return {
      positions: [],
      arbitrages: [],
      lastUpdate: Date.now(),
      totalFundingCollected: 0,
      totalRealizedPnl: 0
    };
  }

  /**
   * Save position state to file
   */
  private saveState(): void {
    try {
      this.state.lastUpdate = Date.now();
      fs.writeFileSync(STATE_FILE, JSON.stringify(this.state, null, 2));
    } catch (error: any) {
      logger.error(`Failed to save state: ${error.message}`);
    }
  }

  /**
   * Load trade history
   */
  private loadHistory(): TradeHistory[] {
    try {
      if (fs.existsSync(HISTORY_FILE)) {
        const data = fs.readFileSync(HISTORY_FILE, 'utf-8');
        return JSON.parse(data);
      }
    } catch (error: any) {
      logger.warn(`Failed to load history: ${error.message}`);
    }
    return [];
  }

  /**
   * Save trade history
   */
  private saveHistory(): void {
    try {
      // Keep last 1000 trades
      if (this.history.length > 1000) {
        this.history = this.history.slice(-1000);
      }
      fs.writeFileSync(HISTORY_FILE, JSON.stringify(this.history, null, 2));
    } catch (error: any) {
      logger.error(`Failed to save history: ${error.message}`);
    }
  }

  /**
   * Generate unique position ID
   */
  private generateId(): string {
    return `pos_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;
  }

  /**
   * Add a new position
   */
  addPosition(
    exchange: 'drift' | 'flash',
    symbol: string,
    side: 'long' | 'short',
    size: number,
    entryPrice: number,
    txSignature: string
  ): Position {
    const position: Position = {
      id: this.generateId(),
      exchange,
      symbol,
      side,
      size,
      notional: size * entryPrice,
      entryPrice,
      openTime: Date.now(),
      txSignature,
      fundingCollected: 0,
      unrealizedPnl: 0,
      lastUpdate: Date.now()
    };

    this.state.positions.push(position);
    this.saveState();

    // Add to history
    this.history.push({
      id: position.id,
      type: 'open',
      exchange,
      symbol,
      side,
      size,
      price: entryPrice,
      time: Date.now(),
      txSignature
    });
    this.saveHistory();

    logger.info(`Position added: ${position.id} - ${side.toUpperCase()} ${symbol} on ${exchange}`);
    return position;
  }

  /**
   * Create an arbitrage pair
   */
  createArbitrage(
    longPosition: Position,
    shortPosition: Position,
    targetSpread: number
  ): ArbitragePosition {
    const arb: ArbitragePosition = {
      id: this.generateId(),
      pair: { long: longPosition, short: shortPosition },
      openTime: Date.now(),
      totalNotional: longPosition.notional + shortPosition.notional,
      targetSpread,
      totalPnl: 0,
      totalFunding: 0,
      status: 'open'
    };

    this.state.arbitrages.push(arb);
    this.saveState();

    logger.info(`Arbitrage created: ${arb.id}`);
    logger.info(`  Long: ${longPosition.symbol} on ${longPosition.exchange}`);
    logger.info(`  Short: ${shortPosition.symbol} on ${shortPosition.exchange}`);
    logger.info(`  Target spread: ${targetSpread.toFixed(2)}% APY`);

    return arb;
  }

  /**
   * Close a position
   */
  closePosition(positionId: string, exitPrice: number, txSignature: string): boolean {
    const index = this.state.positions.findIndex(p => p.id === positionId);
    if (index === -1) {
      logger.error(`Position not found: ${positionId}`);
      return false;
    }

    const position = this.state.positions[index];
    
    // Calculate PnL
    const priceDiff = position.side === 'long'
      ? exitPrice - position.entryPrice
      : position.entryPrice - exitPrice;
    const realizedPnl = priceDiff * position.size;
    const totalPnl = realizedPnl + (position.fundingCollected || 0);

    // Update totals
    this.state.totalRealizedPnl += realizedPnl;
    this.state.totalFundingCollected += position.fundingCollected || 0;

    // Remove from active positions
    this.state.positions.splice(index, 1);
    this.saveState();

    // Add to history
    this.history.push({
      id: position.id,
      type: 'close',
      exchange: position.exchange,
      symbol: position.symbol,
      side: position.side,
      size: position.size,
      price: exitPrice,
      time: Date.now(),
      txSignature,
      pnl: realizedPnl,
      funding: position.fundingCollected
    });
    this.saveHistory();

    logger.info(`Position closed: ${position.id}`);
    logger.info(`  PnL: $${realizedPnl.toFixed(2)} + $${(position.fundingCollected || 0).toFixed(2)} funding`);
    logger.info(`  Total: $${totalPnl.toFixed(2)}`);

    return true;
  }

  /**
   * Update position with live data
   */
  updatePosition(positionId: string, currentPrice: number, fundingDelta: number = 0): void {
    const position = this.state.positions.find(p => p.id === positionId);
    if (!position) return;

    position.currentPrice = currentPrice;
    
    // Calculate unrealized PnL
    const priceDiff = position.side === 'long'
      ? currentPrice - position.entryPrice
      : position.entryPrice - currentPrice;
    position.unrealizedPnl = priceDiff * position.size;
    
    // Update funding collected
    position.fundingCollected = (position.fundingCollected || 0) + fundingDelta;
    position.lastUpdate = Date.now();

    this.saveState();
  }

  /**
   * Get all open positions
   */
  getOpenPositions(): Position[] {
    return this.state.positions;
  }

  /**
   * Get positions by exchange
   */
  getPositionsByExchange(exchange: 'drift' | 'flash'): Position[] {
    return this.state.positions.filter(p => p.exchange === exchange);
  }

  /**
   * Get all arbitrage positions
   */
  getArbitrages(): ArbitragePosition[] {
    return this.state.arbitrages.filter(a => a.status === 'open');
  }

  /**
   * Close an arbitrage (both legs)
   */
  closeArbitrage(arbId: string): void {
    const arb = this.state.arbitrages.find(a => a.id === arbId);
    if (!arb) return;

    arb.status = 'closed';
    this.saveState();
  }

  /**
   * Get position summary
   */
  getSummary(): {
    totalPositions: number;
    totalNotional: number;
    totalUnrealizedPnl: number;
    totalFunding: number;
    byExchange: Record<string, number>;
  } {
    const positions = this.state.positions;
    
    return {
      totalPositions: positions.length,
      totalNotional: positions.reduce((sum, p) => sum + p.notional, 0),
      totalUnrealizedPnl: positions.reduce((sum, p) => sum + (p.unrealizedPnl || 0), 0),
      totalFunding: positions.reduce((sum, p) => sum + (p.fundingCollected || 0), 0),
      byExchange: {
        drift: positions.filter(p => p.exchange === 'drift').reduce((sum, p) => sum + p.notional, 0),
        flash: positions.filter(p => p.exchange === 'flash').reduce((sum, p) => sum + p.notional, 0)
      }
    };
  }

  /**
   * Check if we have position for a symbol
   */
  hasPosition(symbol: string, exchange?: 'drift' | 'flash'): boolean {
    return this.state.positions.some(p => 
      p.symbol === symbol && (!exchange || p.exchange === exchange)
    );
  }

  /**
   * Get total stats
   */
  getTotalStats(): { realized: number; funding: number; total: number } {
    return {
      realized: this.state.totalRealizedPnl,
      funding: this.state.totalFundingCollected,
      total: this.state.totalRealizedPnl + this.state.totalFundingCollected
    };
  }

  /**
   * Get recent history
   */
  getRecentHistory(count: number = 10): TradeHistory[] {
    return this.history.slice(-count);
  }

  /**
   * Calculate max drawdown
   */
  calculateMaxDrawdown(): number {
    const positions = this.state.positions;
    if (positions.length === 0) return 0;

    const totalNotional = positions.reduce((sum, p) => sum + p.notional, 0);
    const totalUnrealizedPnl = positions.reduce((sum, p) => sum + (p.unrealizedPnl || 0), 0);
    
    if (totalNotional === 0) return 0;
    
    return Math.abs(Math.min(0, totalUnrealizedPnl)) / totalNotional * 100;
  }

  /**
   * Clear all positions (for testing)
   */
  clearAll(): void {
    this.state = {
      positions: [],
      arbitrages: [],
      lastUpdate: Date.now(),
      totalFundingCollected: 0,
      totalRealizedPnl: 0
    };
    this.saveState();
    logger.warn('All positions cleared');
  }
}
