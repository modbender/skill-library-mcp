/**
 * P&L (Profit & Loss) Tracker
 * 
 * Tracks trading performance with daily, weekly, monthly statistics.
 */

import { TradeResult, PnLStats, PnLPeriod } from '../types';
import * as fs from 'fs';
import * as path from 'path';

const DATA_DIR = path.join(process.env.HOME || '.', '.solarb');
const TRADES_FILE = path.join(DATA_DIR, 'trades.json');

interface StoredTrade {
  timestamp: number;
  pair: string;
  buyDex: string;
  sellDex: string;
  profitUsd: number;
  success: boolean;
  executionTimeMs: number;
}

export class PnLTracker {
  private trades: StoredTrade[] = [];

  constructor() {
    this.loadTrades();
  }

  /**
   * Record a completed trade
   */
  recordTrade(result: TradeResult): void {
    const trade: StoredTrade = {
      timestamp: Date.now(),
      pair: result.opportunity.pair,
      buyDex: result.opportunity.buyDex,
      sellDex: result.opportunity.sellDex,
      profitUsd: result.success ? (result.actualProfitUsd || 0) : 0,
      success: result.success,
      executionTimeMs: result.executionTimeMs
    };

    this.trades.push(trade);
    this.saveTrades();
  }

  /**
   * Get P&L statistics
   */
  getStats(): PnLStats {
    const now = Date.now();
    const dayAgo = now - 24 * 60 * 60 * 1000;
    const weekAgo = now - 7 * 24 * 60 * 60 * 1000;
    const monthAgo = now - 30 * 24 * 60 * 60 * 1000;

    return {
      daily: this.calculatePeriod(this.trades.filter(t => t.timestamp > dayAgo)),
      weekly: this.calculatePeriod(this.trades.filter(t => t.timestamp > weekAgo)),
      monthly: this.calculatePeriod(this.trades.filter(t => t.timestamp > monthAgo)),
      allTime: this.calculatePeriod(this.trades)
    };
  }

  /**
   * Get recent trades
   */
  getRecentTrades(limit: number = 50): StoredTrade[] {
    return this.trades.slice(-limit).reverse();
  }

  /**
   * Get trade history for a specific period
   */
  getTradeHistory(startTime: number, endTime: number): StoredTrade[] {
    return this.trades.filter(t => t.timestamp >= startTime && t.timestamp <= endTime);
  }

  /**
   * Calculate P&L for a period
   */
  private calculatePeriod(trades: StoredTrade[]): PnLPeriod {
    if (trades.length === 0) {
      return {
        profitUsd: 0,
        trades: 0,
        winRate: 0,
        avgProfitPerTrade: 0,
        bestTrade: 0,
        worstTrade: 0
      };
    }

    const profits = trades.map(t => t.profitUsd);
    const successfulTrades = trades.filter(t => t.success && t.profitUsd > 0);

    return {
      profitUsd: profits.reduce((a, b) => a + b, 0),
      trades: trades.length,
      winRate: (successfulTrades.length / trades.length) * 100,
      avgProfitPerTrade: profits.reduce((a, b) => a + b, 0) / trades.length,
      bestTrade: Math.max(...profits),
      worstTrade: Math.min(...profits)
    };
  }

  /**
   * Load trades from file
   */
  private loadTrades(): void {
    try {
      if (!fs.existsSync(DATA_DIR)) {
        fs.mkdirSync(DATA_DIR, { recursive: true });
      }

      if (fs.existsSync(TRADES_FILE)) {
        const data = fs.readFileSync(TRADES_FILE, 'utf-8');
        this.trades = JSON.parse(data);
      }
    } catch (error) {
      console.error('Failed to load trades:', error);
      this.trades = [];
    }
  }

  /**
   * Save trades to file
   */
  private saveTrades(): void {
    try {
      if (!fs.existsSync(DATA_DIR)) {
        fs.mkdirSync(DATA_DIR, { recursive: true });
      }
      
      fs.writeFileSync(TRADES_FILE, JSON.stringify(this.trades, null, 2));
    } catch (error) {
      console.error('Failed to save trades:', error);
    }
  }

  /**
   * Get summary string for display
   */
  getSummaryString(): string {
    const stats = this.getStats();
    
    return `
╔══════════════════════════════════════════════════╗
║              SolArb P&L Summary                  ║
╠══════════════════════════════════════════════════╣
║  Daily:   ${this.formatProfit(stats.daily.profitUsd).padEnd(12)} (${stats.daily.trades} trades, ${stats.daily.winRate.toFixed(0)}% win)
║  Weekly:  ${this.formatProfit(stats.weekly.profitUsd).padEnd(12)} (${stats.weekly.trades} trades, ${stats.weekly.winRate.toFixed(0)}% win)
║  Monthly: ${this.formatProfit(stats.monthly.profitUsd).padEnd(12)} (${stats.monthly.trades} trades, ${stats.monthly.winRate.toFixed(0)}% win)
║  AllTime: ${this.formatProfit(stats.allTime.profitUsd).padEnd(12)} (${stats.allTime.trades} trades, ${stats.allTime.winRate.toFixed(0)}% win)
╚══════════════════════════════════════════════════╝`;
  }

  private formatProfit(amount: number): string {
    const sign = amount >= 0 ? '+' : '';
    return `${sign}$${amount.toFixed(2)}`;
  }
}
