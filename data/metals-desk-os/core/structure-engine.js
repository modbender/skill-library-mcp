// ============================================================================
// STRUCTURE ENGINE — Market Structure Detection (ICT/SMC)
// ============================================================================
// Detects: HH, HL, LH, LL, BOS, CHoCH, Compression, Expansion
// Emits: structure.hh, structure.hl, structure.lh, structure.ll,
//        structure.bos, structure.choch, structure.shift,
//        structure.compression, structure.expansion
// ============================================================================

const bus = require('../automation/event-bus');
const { EVENTS } = bus;

class StructureEngine {
  constructor(config = {}) {
    this.config = {
      swingLookback: config.swingLookback || 5,
      minSwingSize: config.minSwingSize || { XAUUSD: 6.0, XAGUSD: 0.80 },
      confirmationCandles: config.confirmationCandles || 2,
      compressionThreshold: config.compressionThreshold || 0.4, // ATR ratio
      expansionThreshold: config.expansionThreshold || 1.8,      // ATR ratio
      timeframes: config.timeframes || ['M15', 'H1', 'H4', 'D1'],
      ...config
    };

    // State per symbol per timeframe
    this.state = {};
    this.fvgZones = {};  // Fair Value Gaps
    this.orderBlocks = {};

    this._initState('XAUUSD');
    this._initState('XAGUSD');
  }

  _initState(symbol) {
    this.state[symbol] = {};
    this.fvgZones[symbol] = {};
    this.orderBlocks[symbol] = {};

    this.config.timeframes.forEach(tf => {
      this.state[symbol][tf] = {
        swingHighs: [],
        swingLows: [],
        lastStructure: null, // 'bullish' | 'bearish' | null
        bos: [],
        choch: [],
        trend: 'neutral',
        lastHH: null,
        lastHL: null,
        lastLH: null,
        lastLL: null
      };
      this.fvgZones[symbol][tf] = [];
      this.orderBlocks[symbol][tf] = [];
    });
  }

  // --- Analyze Candles for Structure ---
  analyze(symbol, timeframe, candles) {
    if (!candles || candles.length < this.config.swingLookback * 2 + 1) return null;

    const state = this.state[symbol]?.[timeframe];
    if (!state) return null;

    const lookback = this.config.swingLookback;
    const minSize = this.config.minSwingSize[symbol] || 6.0;

    // 1. Detect Swing Points
    const swings = this._detectSwingPoints(candles, lookback, minSize);

    // 2. Classify Structure (HH/HL/LH/LL)
    const structurePoints = this._classifyStructure(symbol, timeframe, swings);

    // 3. Detect BOS and CHoCH
    const shifts = this._detectBOSandCHoCH(symbol, timeframe, candles, structurePoints);

    // 4. Detect FVGs (Fair Value Gaps)
    const fvgs = this._detectFVG(symbol, timeframe, candles);

    // 5. Detect Order Blocks
    const obs = this._detectOrderBlocks(symbol, timeframe, candles, shifts);

    // 6. Detect Compression / Expansion
    const volatilityState = this._detectCompressionExpansion(symbol, timeframe, candles);

    // Store state
    state.swingHighs = swings.highs;
    state.swingLows = swings.lows;
    this.fvgZones[symbol][timeframe] = fvgs;
    this.orderBlocks[symbol][timeframe] = obs;

    return {
      symbol,
      timeframe,
      trend: state.trend,
      lastStructure: state.lastStructure,
      swings,
      structurePoints,
      shifts,
      fvgs,
      orderBlocks: obs,
      volatilityState
    };
  }

  // --- Detect Swing Highs and Lows ---
  _detectSwingPoints(candles, lookback, minSize) {
    const highs = [];
    const lows = [];

    for (let i = lookback; i < candles.length - lookback; i++) {
      const current = candles[i];

      // Swing High
      let isSwingHigh = true;
      for (let j = 1; j <= lookback; j++) {
        if (candles[i - j].high >= current.high || candles[i + j].high >= current.high) {
          isSwingHigh = false;
          break;
        }
      }
      if (isSwingHigh) {
        highs.push({ index: i, price: current.high, time: current.time, type: 'swing_high' });
      }

      // Swing Low
      let isSwingLow = true;
      for (let j = 1; j <= lookback; j++) {
        if (candles[i - j].low <= current.low || candles[i + j].low <= current.low) {
          isSwingLow = false;
          break;
        }
      }
      if (isSwingLow) {
        lows.push({ index: i, price: current.low, time: current.time, type: 'swing_low' });
      }
    }

    return { highs, lows };
  }

  // --- Classify Structure Points ---
  _classifyStructure(symbol, timeframe, swings) {
    const state = this.state[symbol][timeframe];
    const points = [];

    // Classify swing highs
    for (let i = 1; i < swings.highs.length; i++) {
      const prev = swings.highs[i - 1];
      const curr = swings.highs[i];

      if (curr.price > prev.price) {
        points.push({ ...curr, label: 'HH' });
        state.lastHH = curr;
        bus.publish(EVENTS.STRUCTURE_HH, { symbol, timeframe, price: curr.price, time: curr.time });
      } else {
        points.push({ ...curr, label: 'LH' });
        state.lastLH = curr;
        bus.publish(EVENTS.STRUCTURE_LH, { symbol, timeframe, price: curr.price, time: curr.time });
      }
    }

    // Classify swing lows
    for (let i = 1; i < swings.lows.length; i++) {
      const prev = swings.lows[i - 1];
      const curr = swings.lows[i];

      if (curr.price > prev.price) {
        points.push({ ...curr, label: 'HL' });
        state.lastHL = curr;
        bus.publish(EVENTS.STRUCTURE_HL, { symbol, timeframe, price: curr.price, time: curr.time });
      } else {
        points.push({ ...curr, label: 'LL' });
        state.lastLL = curr;
        bus.publish(EVENTS.STRUCTURE_LL, { symbol, timeframe, price: curr.price, time: curr.time });
      }
    }

    return points.sort((a, b) => a.index - b.index);
  }

  // --- Detect BOS and CHoCH ---
  _detectBOSandCHoCH(symbol, timeframe, candles, structurePoints) {
    const state = this.state[symbol][timeframe];
    const shifts = [];
    const lastCandle = candles[candles.length - 1];

    // BOS Bullish: price breaks above last HH in uptrend
    if (state.lastHH && state.trend === 'bullish' && lastCandle.close > state.lastHH.price) {
      const bos = {
        type: 'BOS',
        direction: 'bullish',
        level: state.lastHH.price,
        time: lastCandle.time,
        symbol,
        timeframe
      };
      shifts.push(bos);
      state.bos.push(bos);
      bus.publish(EVENTS.STRUCTURE_BOS, bos);
    }

    // BOS Bearish: price breaks below last LL in downtrend
    if (state.lastLL && state.trend === 'bearish' && lastCandle.close < state.lastLL.price) {
      const bos = {
        type: 'BOS',
        direction: 'bearish',
        level: state.lastLL.price,
        time: lastCandle.time,
        symbol,
        timeframe
      };
      shifts.push(bos);
      state.bos.push(bos);
      bus.publish(EVENTS.STRUCTURE_BOS, bos);
    }

    // CHoCH Bullish: price breaks above last LH in downtrend → trend shift
    if (state.lastLH && state.trend === 'bearish' && lastCandle.close > state.lastLH.price) {
      state.trend = 'bullish';
      state.lastStructure = 'bullish';
      const choch = {
        type: 'CHoCH',
        direction: 'bullish',
        level: state.lastLH.price,
        time: lastCandle.time,
        symbol,
        timeframe
      };
      shifts.push(choch);
      state.choch.push(choch);
      bus.publish(EVENTS.STRUCTURE_CHOCH, choch);
      bus.publish(EVENTS.STRUCTURE_SHIFT, { ...choch, newTrend: 'bullish' });
    }

    // CHoCH Bearish: price breaks below last HL in uptrend → trend shift
    if (state.lastHL && state.trend === 'bullish' && lastCandle.close < state.lastHL.price) {
      state.trend = 'bearish';
      state.lastStructure = 'bearish';
      const choch = {
        type: 'CHoCH',
        direction: 'bearish',
        level: state.lastHL.price,
        time: lastCandle.time,
        symbol,
        timeframe
      };
      shifts.push(choch);
      state.choch.push(choch);
      bus.publish(EVENTS.STRUCTURE_CHOCH, choch);
      bus.publish(EVENTS.STRUCTURE_SHIFT, { ...choch, newTrend: 'bearish' });
    }

    // Detect initial trend from structure points
    if (state.trend === 'neutral' && structurePoints.length >= 4) {
      const recent = structurePoints.slice(-4);
      const hhCount = recent.filter(p => p.label === 'HH').length;
      const hlCount = recent.filter(p => p.label === 'HL').length;
      const lhCount = recent.filter(p => p.label === 'LH').length;
      const llCount = recent.filter(p => p.label === 'LL').length;

      if (hhCount + hlCount > lhCount + llCount) state.trend = 'bullish';
      else if (lhCount + llCount > hhCount + hlCount) state.trend = 'bearish';
    }

    return shifts;
  }

  // --- Detect Fair Value Gaps ---
  _detectFVG(symbol, timeframe, candles) {
    const fvgs = [];
    if (candles.length < 3) return fvgs;

    for (let i = 2; i < candles.length; i++) {
      const c1 = candles[i - 2]; // First candle
      const c2 = candles[i - 1]; // Middle candle (FVG body)
      const c3 = candles[i];     // Third candle

      // Bullish FVG: Gap between c1.high and c3.low
      if (c3.low > c1.high) {
        fvgs.push({
          type: 'bullish_fvg',
          top: c3.low,
          bottom: c1.high,
          mid: (c3.low + c1.high) / 2,
          time: c2.time,
          index: i - 1,
          filled: false
        });
      }

      // Bearish FVG: Gap between c3.high and c1.low
      if (c3.high < c1.low) {
        fvgs.push({
          type: 'bearish_fvg',
          top: c1.low,
          bottom: c3.high,
          mid: (c1.low + c3.high) / 2,
          time: c2.time,
          index: i - 1,
          filled: false
        });
      }
    }

    // Mark filled FVGs
    const lastPrice = candles[candles.length - 1].close;
    fvgs.forEach(fvg => {
      if (fvg.type === 'bullish_fvg' && lastPrice <= fvg.bottom) fvg.filled = true;
      if (fvg.type === 'bearish_fvg' && lastPrice >= fvg.top) fvg.filled = true;
    });

    return fvgs.filter(f => !f.filled).slice(-10); // Keep last 10 unfilled
  }

  // --- Detect Order Blocks ---
  _detectOrderBlocks(symbol, timeframe, candles, shifts) {
    const obs = [];
    if (candles.length < 5) return obs;

    // Find candles before BOS/CHoCH as potential OBs
    for (const shift of shifts) {
      const shiftIndex = candles.findIndex(c => c.time === shift.time);
      if (shiftIndex < 2) continue;

      // Look for last opposing candle before the shift
      for (let i = shiftIndex - 1; i >= Math.max(0, shiftIndex - 5); i--) {
        const candle = candles[i];

        if (shift.direction === 'bullish' && candle.close < candle.open) {
          // Bearish candle before bullish BOS = Bullish OB
          obs.push({
            type: 'bullish_ob',
            high: candle.high,
            low: candle.low,
            mid: (candle.high + candle.low) / 2,
            time: candle.time,
            shift: shift.type,
            tested: false
          });
          break;
        }

        if (shift.direction === 'bearish' && candle.close > candle.open) {
          // Bullish candle before bearish BOS = Bearish OB
          obs.push({
            type: 'bearish_ob',
            high: candle.high,
            low: candle.low,
            mid: (candle.high + candle.low) / 2,
            time: candle.time,
            shift: shift.type,
            tested: false
          });
          break;
        }
      }
    }

    return obs;
  }

  // --- Detect Compression / Expansion ---
  _detectCompressionExpansion(symbol, timeframe, candles) {
    if (candles.length < 20) return { state: 'unknown' };

    // Calculate ATR
    const ranges = candles.slice(-20).map(c => c.high - c.low);
    const atr = ranges.reduce((a, b) => a + b, 0) / ranges.length;
    const recentRange = ranges[ranges.length - 1];
    const ratio = recentRange / atr;

    let volState = 'normal';
    if (ratio < this.config.compressionThreshold) {
      volState = 'compression';
      bus.publish(EVENTS.STRUCTURE_COMPRESSION, { symbol, timeframe, ratio, atr });
    } else if (ratio > this.config.expansionThreshold) {
      volState = 'expansion';
      bus.publish(EVENTS.STRUCTURE_EXPANSION, { symbol, timeframe, ratio, atr });
    }

    return { state: volState, ratio: parseFloat(ratio.toFixed(2)), atr: parseFloat(atr.toFixed(2)) };
  }

  // --- Get Full State ---
  getState(symbol, timeframe) {
    return {
      structure: this.state[symbol]?.[timeframe] || null,
      fvgs: this.fvgZones[symbol]?.[timeframe] || [],
      orderBlocks: this.orderBlocks[symbol]?.[timeframe] || []
    };
  }

  // --- Get Multi-Timeframe Alignment ---
  getMTFAlignment(symbol) {
    const alignment = {};
    this.config.timeframes.forEach(tf => {
      const state = this.state[symbol]?.[tf];
      alignment[tf] = state ? state.trend : 'unknown';
    });

    const trends = Object.values(alignment);
    const bullish = trends.filter(t => t === 'bullish').length;
    const bearish = trends.filter(t => t === 'bearish').length;

    return {
      timeframes: alignment,
      dominant: bullish > bearish ? 'bullish' : bearish > bullish ? 'bearish' : 'mixed',
      alignmentScore: Math.max(bullish, bearish) / trends.length,
      aligned: bullish === trends.length || bearish === trends.length
    };
  }
}

module.exports = StructureEngine;
