// ============================================================================
// PERFORMANCE ENGINE — Institutional Performance Metrics
// ============================================================================
// Calculates: Expectancy, Risk-Adjusted Return, Consecutive Loss Tracking,
//             Max Equity Drawdown, Monthly Performance, Sharpe-like Metric
// Auto-adjusts risk if drawdown > threshold
// Emits: performance.update, performance.report
// ============================================================================

const bus = require('../automation/event-bus');
const { EVENTS } = bus;
const fs = require('fs');
const path = require('path');

class PerformanceEngine {
  constructor(config = {}) {
    this.config = {
      performanceFile: config.performanceFile || path.join(__dirname, '../data/performance.json'),
      tradeLogFile: config.tradeLogFile || path.join(__dirname, '../data/trade-log.json'),
      riskReductionDrawdown: config.riskReductionDrawdown || 0.06, // 6% drawdown triggers risk reduction
      riskReductionFactor: config.riskReductionFactor || 0.5,
      targetRiskFreeRate: config.targetRiskFreeRate || 0.05, // 5% annual for Sharpe calc
      ...config
    };

    this.trades = [];
    this.metrics = this._defaultMetrics();
    this._load();
  }

  _defaultMetrics() {
    return {
      totalTrades: 0,
      wins: 0,
      losses: 0,
      breakeven: 0,
      winRate: 0,
      avgWin: 0,
      avgLoss: 0,
      avgRR: 0,
      expectancy: 0,            // Expected $ per trade
      expectancyR: 0,           // Expected R per trade
      profitFactor: 0,
      maxConsecutiveWins: 0,
      maxConsecutiveLosses: 0,
      currentStreak: 0,         // Positive = wins, negative = losses
      peakEquity: 0,
      maxDrawdown: 0,           // % from peak
      maxDrawdownAmount: 0,
      sharpeRatio: 0,
      totalPnL: 0,
      totalRMultiple: 0,
      monthly: {},              // { '2025-01': { pnl: 500, trades: 12, ... } }
      weekly: {},
      bySymbol: {},
      bySession: {},
      lastUpdate: null
    };
  }

  // --- Record a Completed Trade ---
  recordTrade(trade) {
    const {
      symbol, direction, entryPrice, exitPrice, stopLoss,
      lots, pnl, rMultiple, session, openTime, closeTime,
      closeReason // 'tp1' | 'tp2' | 'tp3' | 'sl' | 'be' | 'manual' | 'trail'
    } = trade;

    const tradeRecord = {
      id: `T${Date.now()}`,
      symbol,
      direction,
      entryPrice,
      exitPrice,
      stopLoss,
      lots,
      pnl: parseFloat(pnl.toFixed(2)),
      rMultiple: parseFloat((rMultiple || 0).toFixed(2)),
      session: session || 'unknown',
      openTime,
      closeTime: closeTime || new Date().toISOString(),
      closeReason: closeReason || 'unknown',
      isWin: pnl > 0,
      isLoss: pnl < 0,
      duration: openTime ? (new Date(closeTime || Date.now()) - new Date(openTime)) / 60000 : 0 // minutes
    };

    this.trades.push(tradeRecord);
    this._recalculate();
    this._save();

    bus.publish(EVENTS.PERFORMANCE_UPDATE, {
      trade: tradeRecord,
      metrics: this.getMetricsSummary()
    });

    return tradeRecord;
  }

  // --- Recalculate All Metrics ---
  _recalculate() {
    const m = this._defaultMetrics();
    const trades = this.trades;
    if (trades.length === 0) { this.metrics = m; return; }

    m.totalTrades = trades.length;
    m.wins = trades.filter(t => t.isWin).length;
    m.losses = trades.filter(t => t.isLoss).length;
    m.breakeven = trades.filter(t => t.pnl === 0).length;
    m.winRate = parseFloat(((m.wins / m.totalTrades) * 100).toFixed(1));

    // Average win/loss
    const winPnLs = trades.filter(t => t.isWin).map(t => t.pnl);
    const lossPnLs = trades.filter(t => t.isLoss).map(t => Math.abs(t.pnl));
    m.avgWin = winPnLs.length > 0 ? parseFloat((winPnLs.reduce((a, b) => a + b, 0) / winPnLs.length).toFixed(2)) : 0;
    m.avgLoss = lossPnLs.length > 0 ? parseFloat((lossPnLs.reduce((a, b) => a + b, 0) / lossPnLs.length).toFixed(2)) : 0;

    // Average R:R
    const rMultiples = trades.map(t => t.rMultiple).filter(r => r !== 0);
    m.avgRR = rMultiples.length > 0 ? parseFloat((rMultiples.reduce((a, b) => a + b, 0) / rMultiples.length).toFixed(2)) : 0;

    // Expectancy: (WinRate × AvgWin) - (LossRate × AvgLoss)
    const winRate = m.wins / m.totalTrades;
    const lossRate = m.losses / m.totalTrades;
    m.expectancy = parseFloat(((winRate * m.avgWin) - (lossRate * m.avgLoss)).toFixed(2));

    // Expectancy in R
    const winRs = trades.filter(t => t.isWin).map(t => t.rMultiple);
    const lossRs = trades.filter(t => t.isLoss).map(t => t.rMultiple);
    const avgWinR = winRs.length > 0 ? winRs.reduce((a, b) => a + b, 0) / winRs.length : 0;
    const avgLossR = lossRs.length > 0 ? Math.abs(lossRs.reduce((a, b) => a + b, 0) / lossRs.length) : 0;
    m.expectancyR = parseFloat(((winRate * avgWinR) - (lossRate * avgLossR)).toFixed(3));

    // Profit Factor
    const grossProfit = winPnLs.reduce((a, b) => a + b, 0);
    const grossLoss = lossPnLs.reduce((a, b) => a + b, 0);
    m.profitFactor = grossLoss > 0 ? parseFloat((grossProfit / grossLoss).toFixed(2)) : grossProfit > 0 ? Infinity : 0;

    // Consecutive streaks
    let currentStreak = 0;
    let maxWinStreak = 0;
    let maxLossStreak = 0;
    for (const t of trades) {
      if (t.isWin) {
        currentStreak = currentStreak > 0 ? currentStreak + 1 : 1;
        maxWinStreak = Math.max(maxWinStreak, currentStreak);
      } else if (t.isLoss) {
        currentStreak = currentStreak < 0 ? currentStreak - 1 : -1;
        maxLossStreak = Math.max(maxLossStreak, Math.abs(currentStreak));
      }
    }
    m.maxConsecutiveWins = maxWinStreak;
    m.maxConsecutiveLosses = maxLossStreak;
    m.currentStreak = currentStreak;

    // Equity curve and max drawdown
    let equity = 0;
    let peak = 0;
    let maxDD = 0;
    let maxDDAmount = 0;
    for (const t of trades) {
      equity += t.pnl;
      if (equity > peak) peak = equity;
      const dd = peak > 0 ? (peak - equity) / peak : 0;
      if (dd > maxDD) { maxDD = dd; maxDDAmount = peak - equity; }
    }
    m.peakEquity = parseFloat(peak.toFixed(2));
    m.maxDrawdown = parseFloat((maxDD * 100).toFixed(2));
    m.maxDrawdownAmount = parseFloat(maxDDAmount.toFixed(2));
    m.totalPnL = parseFloat(equity.toFixed(2));
    m.totalRMultiple = parseFloat(trades.reduce((s, t) => s + t.rMultiple, 0).toFixed(2));

    // Sharpe-like ratio (simplified)
    const returns = trades.map(t => t.pnl);
    const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
    const stdDev = Math.sqrt(returns.reduce((s, v) => s + Math.pow(v - avgReturn, 2), 0) / returns.length);
    m.sharpeRatio = stdDev > 0 ? parseFloat((avgReturn / stdDev).toFixed(3)) : 0;

    // Monthly breakdown
    m.monthly = {};
    for (const t of trades) {
      const month = t.closeTime.substring(0, 7); // '2025-01'
      if (!m.monthly[month]) m.monthly[month] = { pnl: 0, trades: 0, wins: 0, losses: 0 };
      m.monthly[month].pnl += t.pnl;
      m.monthly[month].trades++;
      if (t.isWin) m.monthly[month].wins++;
      if (t.isLoss) m.monthly[month].losses++;
    }

    // By symbol
    m.bySymbol = {};
    for (const t of trades) {
      if (!m.bySymbol[t.symbol]) m.bySymbol[t.symbol] = { pnl: 0, trades: 0, winRate: 0, wins: 0 };
      m.bySymbol[t.symbol].pnl += t.pnl;
      m.bySymbol[t.symbol].trades++;
      if (t.isWin) m.bySymbol[t.symbol].wins++;
      m.bySymbol[t.symbol].winRate = parseFloat(((m.bySymbol[t.symbol].wins / m.bySymbol[t.symbol].trades) * 100).toFixed(1));
    }

    // By session
    m.bySession = {};
    for (const t of trades) {
      const sess = t.session;
      if (!m.bySession[sess]) m.bySession[sess] = { pnl: 0, trades: 0, wins: 0 };
      m.bySession[sess].pnl += t.pnl;
      m.bySession[sess].trades++;
      if (t.isWin) m.bySession[sess].wins++;
    }

    m.lastUpdate = new Date().toISOString();
    this.metrics = m;
  }

  // --- Get Summary ---
  getMetricsSummary() {
    const m = this.metrics;
    return {
      winRate: m.winRate,
      avgRR: m.avgRR,
      expectancy: m.expectancy,
      expectancyR: m.expectancyR,
      profitFactor: m.profitFactor,
      maxDrawdown: m.maxDrawdown,
      sharpeRatio: m.sharpeRatio,
      totalPnL: m.totalPnL,
      totalTrades: m.totalTrades,
      currentStreak: m.currentStreak
    };
  }

  // --- Should Reduce Risk? ---
  shouldReduceRisk() {
    return this.metrics.maxDrawdown > (this.config.riskReductionDrawdown * 100);
  }

  getRiskMultiplier() {
    if (this.shouldReduceRisk()) return this.config.riskReductionFactor;
    return 1.0;
  }

  // --- Persistence ---
  _save() {
    try {
      fs.writeFileSync(this.config.performanceFile, JSON.stringify(this.metrics, null, 2));
      fs.writeFileSync(this.config.tradeLogFile, JSON.stringify(this.trades.slice(-500), null, 2));
    } catch (e) { /* silent */ }
  }

  _load() {
    try {
      if (fs.existsSync(this.config.tradeLogFile)) {
        this.trades = JSON.parse(fs.readFileSync(this.config.tradeLogFile, 'utf8'));
        this._recalculate();
      }
    } catch (e) { /* silent */ }
  }

  getFullMetrics() { return this.metrics; }
  getTrades(count = 50) { return this.trades.slice(-count); }
}

module.exports = PerformanceEngine;
