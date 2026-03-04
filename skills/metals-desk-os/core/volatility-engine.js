// ============================================================================
// VOLATILITY ENGINE — ATR, Spike Detection, Regime Classification
// ============================================================================
// Monitors volatility across timeframes. Detects spikes and low-vol regimes.
// Used by Risk Engine to adjust position sizing.
// Emits: volatility.update, volatility.spike, volatility.low
// ============================================================================

const bus = require('../automation/event-bus');
const { EVENTS } = bus;

class VolatilityEngine {
  constructor(config = {}) {
    this.config = {
      atrPeriod: config.atrPeriod || 14,
      spikeMultiplier: config.spikeMultiplier || 2.5,
      lowVolMultiplier: config.lowVolMultiplier || 0.5,
      extremeSpikeMultiplier: config.extremeSpikeMultiplier || 4.0,
      timeframes: config.timeframes || ['M15', 'H1', 'H4', 'D1'],
      ...config
    };

    this.state = {};
    ['XAUUSD', 'XAGUSD'].forEach(symbol => {
      this.state[symbol] = {};
      this.config.timeframes.forEach(tf => {
        this.state[symbol][tf] = {
          atr: 0,
          atrPercent: 0,
          currentRange: 0,
          avgRange: 0,
          regime: 'normal', // low | normal | high | extreme
          spikeDetected: false,
          history: []
        };
      });
    });
  }

  // --- Calculate ATR and Volatility Metrics ---
  analyze(symbol, timeframe, candles) {
    if (!candles || candles.length < this.config.atrPeriod + 1) return null;

    const state = this.state[symbol]?.[timeframe];
    if (!state) return null;

    // Calculate True Range
    const trueRanges = [];
    for (let i = 1; i < candles.length; i++) {
      const high = candles[i].high;
      const low = candles[i].low;
      const prevClose = candles[i - 1].close;
      const tr = Math.max(high - low, Math.abs(high - prevClose), Math.abs(low - prevClose));
      trueRanges.push(tr);
    }

    // ATR (Simple Moving Average of True Range)
    const recentTRs = trueRanges.slice(-this.config.atrPeriod);
    const atr = recentTRs.reduce((a, b) => a + b, 0) / recentTRs.length;

    // Current candle range
    const lastCandle = candles[candles.length - 1];
    const currentRange = lastCandle.high - lastCandle.low;

    // Average range (last 20)
    const ranges = candles.slice(-20).map(c => c.high - c.low);
    const avgRange = ranges.reduce((a, b) => a + b, 0) / ranges.length;

    // ATR as percentage of price
    const atrPercent = (atr / lastCandle.close) * 100;

    // Volatility regime
    const rangeRatio = currentRange / atr;
    let regime = 'normal';
    let spikeDetected = false;

    if (rangeRatio >= this.config.extremeSpikeMultiplier) {
      regime = 'extreme';
      spikeDetected = true;
      bus.publish(EVENTS.VOLATILITY_SPIKE, {
        symbol, timeframe, rangeRatio: parseFloat(rangeRatio.toFixed(2)),
        atr: parseFloat(atr.toFixed(2)), currentRange: parseFloat(currentRange.toFixed(2)),
        severity: 'extreme'
      });
    } else if (rangeRatio >= this.config.spikeMultiplier) {
      regime = 'high';
      spikeDetected = true;
      bus.publish(EVENTS.VOLATILITY_SPIKE, {
        symbol, timeframe, rangeRatio: parseFloat(rangeRatio.toFixed(2)),
        atr: parseFloat(atr.toFixed(2)), currentRange: parseFloat(currentRange.toFixed(2)),
        severity: 'high'
      });
    } else if (rangeRatio <= this.config.lowVolMultiplier) {
      regime = 'low';
      bus.publish(EVENTS.VOLATILITY_LOW, {
        symbol, timeframe, rangeRatio: parseFloat(rangeRatio.toFixed(2)),
        atr: parseFloat(atr.toFixed(2))
      });
    }

    // Bollinger Band Width (volatility gauge)
    const closes = candles.slice(-20).map(c => c.close);
    const sma = closes.reduce((a, b) => a + b, 0) / closes.length;
    const stdDev = Math.sqrt(closes.reduce((s, v) => s + Math.pow(v - sma, 2), 0) / closes.length);
    const bbWidth = (stdDev * 2) / sma * 100;

    // Update state
    Object.assign(state, {
      atr: parseFloat(atr.toFixed(2)),
      atrPercent: parseFloat(atrPercent.toFixed(4)),
      currentRange: parseFloat(currentRange.toFixed(2)),
      avgRange: parseFloat(avgRange.toFixed(2)),
      regime,
      spikeDetected,
      rangeRatio: parseFloat(rangeRatio.toFixed(2)),
      bbWidth: parseFloat(bbWidth.toFixed(4)),
      stdDev: parseFloat(stdDev.toFixed(2))
    });

    // History for trend analysis
    state.history.push({ time: lastCandle.time, atr: state.atr, regime });
    if (state.history.length > 100) state.history = state.history.slice(-50);

    bus.publish(EVENTS.VOLATILITY_UPDATE, { symbol, timeframe, ...state });

    return state;
  }

  // --- Get ATR for Stop Loss Calculation ---
  getATR(symbol, timeframe = 'H1') {
    return this.state[symbol]?.[timeframe]?.atr || 0;
  }

  // --- Get Volatility Regime ---
  getRegime(symbol, timeframe = 'H1') {
    return this.state[symbol]?.[timeframe]?.regime || 'unknown';
  }

  // --- Is Spike Active ---
  isSpikeActive(symbol) {
    return this.config.timeframes.some(tf =>
      this.state[symbol]?.[tf]?.spikeDetected === true
    );
  }

  // --- Get Position Size Multiplier Based on Volatility ---
  getSizeMultiplier(symbol) {
    const h1Regime = this.getRegime(symbol, 'H1');
    switch (h1Regime) {
      case 'extreme': return 0.25;  // Quarter size
      case 'high': return 0.5;      // Half size
      case 'low': return 1.0;       // Normal (could increase in trending)
      default: return 1.0;          // Normal
    }
  }

  // --- Get Full State ---
  getState(symbol) {
    return this.state[symbol] || {};
  }
}

module.exports = VolatilityEngine;
