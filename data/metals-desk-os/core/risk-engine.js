// ============================================================================
// RISK ENGINE — Institutional Risk Management
// ============================================================================
// Hard Rules: Max 2% per trade, Max 5% daily exposure, Max 3 losses → halt
// Volatility spike → reduce size 50%, Spread widening → block entry
// Position sizing: (Balance × Risk%) / StopDistance, ATR-adjusted
// Emits: risk.check.pass, risk.check.fail, risk.halt, risk.resume
// ============================================================================

const bus = require('../automation/event-bus');
const { EVENTS } = bus;
const fs = require('fs');
const path = require('path');

class RiskEngine {
  constructor(config = {}) {
    this.config = {
      maxRiskPerTrade: config.maxRiskPerTrade || 0.02,       // 2%
      maxDailyExposure: config.maxDailyExposure || 0.05,     // 5%
      maxConsecutiveLosses: config.maxConsecutiveLosses || 3,
      maxDailyLoss: config.maxDailyLoss || 0.05,             // 5%
      volatilitySpikeReduction: config.volatilitySpikeReduction || 0.5,
      spreadThreshold: config.spreadThreshold || { XAUUSD: 5.0, XAGUSD: 0.50 },
      maxOpenPositions: config.maxOpenPositions || 3,
      drawdownHaltThreshold: config.drawdownHaltThreshold || 0.08, // 8% equity drawdown
      minRR: config.minRR || 1.5,                            // Minimum Risk:Reward
      pipValues: config.pipValues || { XAUUSD: 1.0, XAGUSD: 50.0 }, // $ per pip per lot
      ...config
    };

    this.state = {
      accountBalance: 0,
      equity: 0,
      peakEquity: 0,
      dailyPnL: 0,
      dailyStartBalance: 0,
      openPositions: 0,
      currentExposure: 0,      // Total risk in open trades as % of balance
      consecutiveLosses: 0,
      totalTradesToday: 0,
      halted: false,
      haltReason: null,
      haltUntil: null,
      lastCheck: null
    };
  }

  // --- Update Account Info ---
  updateAccount(balance, equity) {
    this.state.accountBalance = balance;
    this.state.equity = equity;

    if (equity > this.state.peakEquity) this.state.peakEquity = equity;

    // Check drawdown
    if (this.state.peakEquity > 0) {
      const drawdown = (this.state.peakEquity - equity) / this.state.peakEquity;
      if (drawdown > this.config.drawdownHaltThreshold) {
        this._halt(`Equity drawdown ${(drawdown * 100).toFixed(1)}% exceeds ${this.config.drawdownHaltThreshold * 100}% threshold`);
        bus.publish(EVENTS.RISK_DRAWDOWN_WARN, { drawdown: parseFloat((drawdown * 100).toFixed(2)), peak: this.state.peakEquity, current: equity });
      }
    }

    // Initialize daily balance if not set
    if (this.state.dailyStartBalance === 0) this.state.dailyStartBalance = balance;
  }

  // --- Daily Reset ---
  resetDaily() {
    this.state.dailyPnL = 0;
    this.state.dailyStartBalance = this.state.accountBalance;
    this.state.totalTradesToday = 0;
    this.state.consecutiveLosses = 0;
    if (this.state.halted && this.state.haltReason?.includes('session')) {
      this.state.halted = false;
      this.state.haltReason = null;
      bus.publish(EVENTS.RISK_RESUME, { reason: 'daily_reset' });
    }
  }

  // --- Record Trade Result ---
  recordResult(pnl) {
    this.state.dailyPnL += pnl;
    this.state.totalTradesToday++;

    if (pnl < 0) {
      this.state.consecutiveLosses++;
      if (this.state.consecutiveLosses >= this.config.maxConsecutiveLosses) {
        this._halt(`${this.state.consecutiveLosses} consecutive losses — trading halted for session`);
      }
    } else {
      this.state.consecutiveLosses = 0;
    }

    // Check daily loss limit
    const dailyLossPercent = Math.abs(this.state.dailyPnL) / this.state.dailyStartBalance;
    if (this.state.dailyPnL < 0 && dailyLossPercent > this.config.maxDailyLoss) {
      this._halt(`Daily loss ${(dailyLossPercent * 100).toFixed(1)}% exceeds ${this.config.maxDailyLoss * 100}% limit`);
      bus.publish(EVENTS.RISK_DAILY_LIMIT, { dailyPnL: this.state.dailyPnL, percent: dailyLossPercent });
    }
  }

  // --- Pre-Trade Risk Check ---
  checkEntry(params) {
    const { symbol, direction, entryPrice, stopLoss, takeProfit, spreadInfo, volatilityState, sessionState } = params;

    const checks = [];
    let passed = true;

    // 1. Halt check
    if (this.state.halted) {
      checks.push({ check: 'halt_status', passed: false, reason: this.state.haltReason });
      passed = false;
    }

    // 2. Max open positions
    if (this.state.openPositions >= this.config.maxOpenPositions) {
      checks.push({ check: 'max_positions', passed: false, reason: `${this.state.openPositions}/${this.config.maxOpenPositions} positions open` });
      passed = false;
    }

    // 3. Stop distance
    const stopDistance = Math.abs(entryPrice - stopLoss);
    if (stopDistance <= 0) {
      checks.push({ check: 'stop_distance', passed: false, reason: 'Invalid stop distance' });
      passed = false;
    }

    // 4. Risk:Reward ratio
    const tpDistance = Math.abs(takeProfit - entryPrice);
    const rr = tpDistance / stopDistance;
    if (rr < this.config.minRR) {
      checks.push({ check: 'risk_reward', passed: false, reason: `R:R ${rr.toFixed(2)} below minimum ${this.config.minRR}` });
      passed = false;
    } else {
      checks.push({ check: 'risk_reward', passed: true, value: parseFloat(rr.toFixed(2)) });
    }

    // 5. Spread check
    const spreadLimit = this.config.spreadThreshold[symbol] || 5.0;
    if (spreadInfo && spreadInfo.current > spreadLimit) {
      checks.push({ check: 'spread', passed: false, reason: `Spread ${spreadInfo.current} exceeds ${spreadLimit}` });
      passed = false;
    } else {
      checks.push({ check: 'spread', passed: true });
    }

    // 6. Volatility check
    if (volatilityState && volatilityState.regime === 'extreme') {
      checks.push({ check: 'volatility', passed: false, reason: 'Extreme volatility detected' });
      passed = false;
    } else {
      checks.push({ check: 'volatility', passed: true });
    }

    // 7. Session check
    if (sessionState && !sessionState.isLondon && !sessionState.isNY) {
      checks.push({ check: 'session', passed: false, reason: `Invalid session: ${sessionState.currentSession || 'none'}` });
      passed = false;
    } else {
      checks.push({ check: 'session', passed: true });
    }

    // 8. Daily loss check
    if (this.state.dailyStartBalance > 0) {
      const dailyLossPercent = Math.abs(Math.min(0, this.state.dailyPnL)) / this.state.dailyStartBalance;
      if (dailyLossPercent > this.config.maxDailyExposure * 0.8) {
        checks.push({ check: 'daily_exposure', passed: false, reason: `Near daily limit: ${(dailyLossPercent * 100).toFixed(1)}%` });
        passed = false;
      } else {
        checks.push({ check: 'daily_exposure', passed: true });
      }
    }

    // Calculate position size
    let positionSize = null;
    if (passed && this.state.accountBalance > 0 && stopDistance > 0) {
      positionSize = this.calculatePositionSize(symbol, stopDistance, volatilityState);
    }

    const result = {
      passed,
      checks,
      positionSize,
      riskReward: parseFloat(rr.toFixed(2)),
      stopDistance: parseFloat(stopDistance.toFixed(2)),
      timestamp: new Date().toISOString()
    };

    if (passed) {
      bus.publish(EVENTS.RISK_CHECK_PASS, result);
    } else {
      bus.publish(EVENTS.RISK_CHECK_FAIL, result);
    }

    this.state.lastCheck = result;
    return result;
  }

  // --- Position Size Calculation ---
  calculatePositionSize(symbol, stopDistance, volatilityState = null) {
    const balance = this.state.accountBalance;
    const riskAmount = balance * this.config.maxRiskPerTrade;
    const pipValue = this.config.pipValues[symbol] || 1.0;

    // Base size
    let lots = riskAmount / (stopDistance * pipValue);

    // Volatility adjustment
    if (volatilityState) {
      if (volatilityState.regime === 'high') lots *= this.config.volatilitySpikeReduction;
      if (volatilityState.regime === 'extreme') lots *= 0.25;
    }

    // Round to 2 decimals (0.01 lot minimum)
    lots = Math.max(0.01, parseFloat(lots.toFixed(2)));

    const riskPercent = ((lots * stopDistance * pipValue) / balance) * 100;

    return {
      lots,
      riskAmount: parseFloat((lots * stopDistance * pipValue).toFixed(2)),
      riskPercent: parseFloat(riskPercent.toFixed(2)),
      stopDistance: parseFloat(stopDistance.toFixed(2)),
      pipValue
    };
  }

  // --- Halt Trading ---
  _halt(reason) {
    this.state.halted = true;
    this.state.haltReason = reason;
    this.state.haltUntil = new Date(Date.now() + 4 * 3600000).toISOString(); // 4 hours

    bus.publish(EVENTS.RISK_HALT, {
      reason,
      haltUntil: this.state.haltUntil,
      dailyPnL: this.state.dailyPnL,
      consecutiveLosses: this.state.consecutiveLosses
    });

    bus.publish(EVENTS.ALERT_RISK, {
      type: 'RISK_HALT',
      message: `RISK HALT ACTIVATED\nReason: ${reason}\nTrading paused`
    });
  }

  // --- Manual Resume ---
  resume() {
    this.state.halted = false;
    this.state.haltReason = null;
    this.state.haltUntil = null;
    bus.publish(EVENTS.RISK_RESUME, { reason: 'manual_resume' });
  }

  // --- Update Open Positions Count ---
  setOpenPositions(count) {
    this.state.openPositions = count;
  }

  // --- Getters ---
  isHalted() { return this.state.halted; }
  getState() { return { ...this.state }; }
  getMaxRisk() { return this.config.maxRiskPerTrade; }
}

module.exports = RiskEngine;
