// ============================================================================
// LIQUIDITY ENGINE — Liquidity Pool & Sweep Detection (ICT/SMC)
// ============================================================================
// Detects: Equal highs/lows, stop clusters, session liquidity,
//          PDH/PDL/PWH/PWL, external liquidity, sweeps
// Emits: liquidity.sweep, liquidity.pool.detected,
//        liquidity.equal.highs, liquidity.equal.lows
// ============================================================================

const bus = require('../automation/event-bus');
const { EVENTS } = bus;

class LiquidityEngine {
  constructor(config = {}) {
    this.config = {
      equalLevelTolerance: config.equalLevelTolerance || { XAUUSD: 3.0, XAGUSD: 0.25 },
      minTouchesForPool: config.minTouchesForPool || 2,
      sweepConfirmationPips: config.sweepConfirmationPips || { XAUUSD: 4.0, XAGUSD: 0.40 },
      maxPoolAge: config.maxPoolAge || 100, // candles
      ...config
    };

    this.pools = {};       // { XAUUSD: { H1: [...] } }
    this.sweeps = {};      // Recent sweep events
    this.externalLevels = {}; // PDH, PDL, PWH, PWL, session levels

    this._initSymbol('XAUUSD');
    this._initSymbol('XAGUSD');
  }

  _initSymbol(symbol) {
    this.pools[symbol] = {};
    this.sweeps[symbol] = [];
    this.externalLevels[symbol] = [];
  }

  // --- Main Analysis ---
  analyze(symbol, timeframe, candles, sessionLevels = []) {
    if (!candles || candles.length < 20) return null;

    const tolerance = this.config.equalLevelTolerance[symbol] || 1.5;
    const sweepPips = this.config.sweepConfirmationPips[symbol] || 2.0;

    // Store external levels
    this.externalLevels[symbol] = sessionLevels;

    // 1. Detect Equal Highs
    const equalHighs = this._detectEqualLevels(candles, 'high', tolerance);

    // 2. Detect Equal Lows
    const equalLows = this._detectEqualLevels(candles, 'low', tolerance);

    // 3. Build Liquidity Pools
    const highPools = equalHighs.map(eh => ({
      type: 'equal_highs',
      level: eh.level,
      touches: eh.touches,
      firstTouch: eh.firstIndex,
      lastTouch: eh.lastIndex,
      strength: eh.touches.length
    }));

    const lowPools = equalLows.map(el => ({
      type: 'equal_lows',
      level: el.level,
      touches: el.touches,
      firstTouch: el.firstIndex,
      lastTouch: el.lastIndex,
      strength: el.touches.length
    }));

    // 4. Add session/external levels as pools
    const externalPools = sessionLevels.map(sl => ({
      type: `external_${sl.type.toLowerCase()}`,
      level: sl.price,
      touches: [{ index: candles.length - 1 }],
      strength: sl.type.includes('W') ? 3 : 2  // Weekly levels are stronger
    }));

    // Combine all pools
    const allPools = [...highPools, ...lowPools, ...externalPools];
    this.pools[symbol][timeframe] = allPools;

    // 5. Detect Sweeps
    const newSweeps = this._detectSweeps(symbol, timeframe, candles, allPools, sweepPips);

    // 6. Emit events
    equalHighs.forEach(eh => {
      bus.publish(EVENTS.LIQUIDITY_EQH, {
        symbol, timeframe, level: eh.level, touches: eh.touches.length
      });
    });

    equalLows.forEach(el => {
      bus.publish(EVENTS.LIQUIDITY_EQL, {
        symbol, timeframe, level: el.level, touches: el.touches.length
      });
    });

    allPools.forEach(pool => {
      bus.publish(EVENTS.LIQUIDITY_POOL, {
        symbol, timeframe, type: pool.type, level: pool.level, strength: pool.strength
      });
    });

    return {
      symbol,
      timeframe,
      pools: allPools,
      equalHighs,
      equalLows,
      recentSweeps: newSweeps,
      externalLevels: sessionLevels,
      nearestHighPool: this._findNearest(candles[candles.length - 1].close, highPools, 'above'),
      nearestLowPool: this._findNearest(candles[candles.length - 1].close, lowPools, 'below')
    };
  }

  // --- Detect Equal Levels ---
  _detectEqualLevels(candles, priceType, tolerance) {
    const levels = [];
    const used = new Set();

    for (let i = 0; i < candles.length; i++) {
      if (used.has(i)) continue;

      const basePrice = candles[i][priceType];
      const touches = [{ index: i, price: basePrice }];

      for (let j = i + 1; j < candles.length; j++) {
        if (used.has(j)) continue;
        const comparePrice = candles[j][priceType];

        if (Math.abs(comparePrice - basePrice) <= tolerance) {
          touches.push({ index: j, price: comparePrice });
          used.add(j);
        }
      }

      if (touches.length >= this.config.minTouchesForPool) {
        const avgLevel = touches.reduce((sum, t) => sum + t.price, 0) / touches.length;
        levels.push({
          level: parseFloat(avgLevel.toFixed(2)),
          touches,
          firstIndex: touches[0].index,
          lastIndex: touches[touches.length - 1].index
        });
      }
    }

    return levels;
  }

  // --- Detect Sweeps ---
  _detectSweeps(symbol, timeframe, candles, pools, sweepPips) {
    const newSweeps = [];
    if (candles.length < 3) return newSweeps;

    const lastCandle = candles[candles.length - 1];
    const prevCandle = candles[candles.length - 2];

    for (const pool of pools) {
      // Bullish Sweep (price dips below pool then closes above)
      if (pool.type.includes('low') || pool.type.includes('pdl') || pool.type.includes('pwl')) {
        if (lastCandle.low < pool.level && lastCandle.close > pool.level + sweepPips) {
          const sweep = {
            type: 'bullish_sweep',
            pool: pool.type,
            level: pool.level,
            sweepLow: lastCandle.low,
            recovery: lastCandle.close,
            symbol,
            timeframe,
            time: lastCandle.time,
            strength: pool.strength,
            displacement: lastCandle.close - lastCandle.low
          };
          newSweeps.push(sweep);
          this.sweeps[symbol].push(sweep);
          bus.publish(EVENTS.LIQUIDITY_SWEEP, sweep);
        }
      }

      // Bearish Sweep (price spikes above pool then closes below)
      if (pool.type.includes('high') || pool.type.includes('pdh') || pool.type.includes('pwh')) {
        if (lastCandle.high > pool.level && lastCandle.close < pool.level - sweepPips) {
          const sweep = {
            type: 'bearish_sweep',
            pool: pool.type,
            level: pool.level,
            sweepHigh: lastCandle.high,
            recovery: lastCandle.close,
            symbol,
            timeframe,
            time: lastCandle.time,
            strength: pool.strength,
            displacement: lastCandle.high - lastCandle.close
          };
          newSweeps.push(sweep);
          this.sweeps[symbol].push(sweep);
          bus.publish(EVENTS.LIQUIDITY_SWEEP, sweep);
        }
      }
    }

    // Trim old sweeps
    if (this.sweeps[symbol].length > 50) {
      this.sweeps[symbol] = this.sweeps[symbol].slice(-25);
    }

    return newSweeps;
  }

  // --- Find Nearest Pool ---
  _findNearest(currentPrice, pools, direction) {
    if (pools.length === 0) return null;

    const filtered = direction === 'above'
      ? pools.filter(p => p.level > currentPrice)
      : pools.filter(p => p.level < currentPrice);

    if (filtered.length === 0) return null;

    filtered.sort((a, b) => {
      const distA = Math.abs(a.level - currentPrice);
      const distB = Math.abs(b.level - currentPrice);
      return distA - distB;
    });

    return {
      level: filtered[0].level,
      distance: parseFloat(Math.abs(filtered[0].level - currentPrice).toFixed(2)),
      type: filtered[0].type,
      strength: filtered[0].strength
    };
  }

  // --- Get Recent Sweeps ---
  getRecentSweeps(symbol, count = 5) {
    return (this.sweeps[symbol] || []).slice(-count);
  }

  // --- Get All Pools ---
  getPools(symbol, timeframe) {
    return this.pools[symbol]?.[timeframe] || [];
  }

  // --- Get Liquidity Map (for dashboard) ---
  getLiquidityMap(symbol) {
    return {
      pools: this.pools[symbol] || {},
      recentSweeps: this.sweeps[symbol]?.slice(-10) || [],
      externalLevels: this.externalLevels[symbol] || []
    };
  }
}

module.exports = LiquidityEngine;
