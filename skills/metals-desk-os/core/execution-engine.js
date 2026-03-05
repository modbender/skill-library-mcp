// ============================================================================
// EXECUTION ENGINE — Trade Signal Generation & Entry Logic
// ============================================================================
// Conditions for auto-trade:
//   1. Bias aligned
//   2. Liquidity sweep confirmed
//   3. BOS confirmed
//   4. Session = London or NY
//   5. Macro risk = low
//   6. Risk within limits
// Then: Calculate entry, SL, TP (multi-target), send to broker
// Emits: execution.signal, execution.entry, execution.rejected
// ============================================================================

const bus = require('../automation/event-bus');
const { EVENTS } = bus;

class ExecutionEngine {
  constructor(config = {}) {
    this.config = {
      minConviction: config.minConviction || 65,       // Minimum bias conviction
      minAlignmentScore: config.minAlignmentScore || 0.6,
      tpMultipliers: config.tpMultipliers || [1.5, 2.5, 4.0], // R:R for TP1, TP2, TP3
      partialClosePercent: config.partialClosePercent || [0.40, 0.30, 0.30], // Close % at each TP
      moveToBreakevenAtTP: config.moveToBreakevenAtTP || 1,  // Move SL to BE at TP1
      trailAfterTP: config.trailAfterTP || 1,
      slBuffer: config.slBuffer || { XAUUSD: 3.0, XAGUSD: 0.25 }, // Pips below/above structure
      useFVGForEntry: config.useFVGForEntry || true,
      useOBForEntry: config.useOBForEntry || true,
      ...config
    };

    this.pendingSignals = [];
    this.executedSignals = [];
    this.rejectedSignals = [];
  }

  // --- Evaluate for Trade Entry ---
  evaluate(params) {
    const {
      symbol,
      currentPrice,  // { bid, ask, mid, spread }
      bias,          // from BiasEngine
      structure,     // from StructureEngine for execution TF
      liquidity,     // from LiquidityEngine
      macro,         // from MacroEngine
      volatility,    // from VolatilityEngine
      session,       // from SessionEngine
      risk,          // from RiskEngine
      fvgs,          // Fair Value Gaps
      orderBlocks    // Order Blocks
    } = params;

    const signal = {
      symbol,
      timestamp: new Date().toISOString(),
      checks: {},
      passed: true,
      direction: null,
      entry: null,
      sl: null,
      tp: [],
      conviction: 0,
      reason: []
    };

    // --- CHECK 1: Bias Aligned ---
    const biasOk = bias && bias.htfBias !== 'neutral' && bias.conviction >= this.config.minConviction;
    signal.checks.bias = {
      passed: biasOk,
      htfBias: bias?.htfBias,
      intradayBias: bias?.intradayBias,
      conviction: bias?.conviction,
      required: this.config.minConviction
    };
    if (!biasOk) { signal.passed = false; signal.reason.push('Insufficient bias conviction'); }

    // Determine direction from bias
    signal.direction = bias?.htfBias === 'bullish' ? 'long' : bias?.htfBias === 'bearish' ? 'short' : null;
    if (!signal.direction) { signal.passed = false; signal.reason.push('No directional bias'); }

    // --- CHECK 2: Alignment Score ---
    const alignOk = bias && bias.alignmentScore >= this.config.minAlignmentScore;
    signal.checks.alignment = {
      passed: alignOk,
      score: bias?.alignmentScore,
      required: this.config.minAlignmentScore
    };
    if (!alignOk) { signal.passed = false; signal.reason.push('Low alignment score'); }

    // --- CHECK 3: Liquidity Sweep ---
    const recentSweeps = liquidity?.recentSweeps || [];
    const sweepAligned = recentSweeps.some(s =>
      (signal.direction === 'long' && s.type === 'bullish_sweep') ||
      (signal.direction === 'short' && s.type === 'bearish_sweep')
    );
    signal.checks.liquiditySweep = { passed: sweepAligned, recentSweeps: recentSweeps.length };
    if (!sweepAligned) { signal.passed = false; signal.reason.push('No aligned liquidity sweep'); }

    // --- CHECK 4: BOS Confirmed ---
    const structureState = structure?.structure;
    const bosConfirmed = structureState && structureState.bos && structureState.bos.length > 0 &&
      structureState.bos[structureState.bos.length - 1].direction === (signal.direction === 'long' ? 'bullish' : 'bearish');
    signal.checks.bos = { passed: bosConfirmed };
    if (!bosConfirmed) { signal.passed = false; signal.reason.push('No BOS confirmation'); }

    // --- CHECK 5: Session ---
    const sessionOk = session && (session.isLondon || session.isNY);
    signal.checks.session = {
      passed: sessionOk,
      current: session?.currentSession,
      isKillZone: session?.isKillZone
    };
    if (!sessionOk) { signal.passed = false; signal.reason.push('Outside London/NY session'); }

    // --- CHECK 6: Macro ---
    const macroOk = macro && macro.macro_risk !== 'high' && !macro.newsBlockActive;
    signal.checks.macro = {
      passed: macroOk,
      bias: macro?.macro_bias,
      risk: macro?.macro_risk,
      newsBlock: macro?.newsBlockActive
    };
    if (!macroOk) { signal.passed = false; signal.reason.push('Macro risk too high or news block'); }

    // --- CHECK 7: Risk Engine ---
    // (Full risk check happens when we calculate entry/SL/TP)

    // --- CALCULATE ENTRY, SL, TP ---
    if (signal.passed && currentPrice) {
      const entryCalc = this._calculateEntry(symbol, signal.direction, currentPrice, fvgs, orderBlocks, volatility, structure);
      signal.entry = entryCalc.entry;
      signal.sl = entryCalc.sl;
      signal.tp = entryCalc.tp;
      signal.entryType = entryCalc.entryType;

      // Risk check with calculated levels
      if (risk) {
        const riskCheck = risk.checkEntry({
          symbol,
          direction: signal.direction,
          entryPrice: signal.entry,
          stopLoss: signal.sl,
          takeProfit: signal.tp[0], // TP1 for R:R calc
          spreadInfo: { current: currentPrice.spread },
          volatilityState: volatility,
          sessionState: session
        });

        signal.checks.risk = riskCheck;
        signal.positionSize = riskCheck.positionSize;

        if (!riskCheck.passed) {
          signal.passed = false;
          signal.reason.push('Risk check failed');
        }
      }
    }

    // --- Final conviction ---
    signal.conviction = bias?.conviction || 0;

    // --- Emit ---
    if (signal.passed) {
      bus.publish(EVENTS.EXECUTION_SIGNAL, signal);

      // In full-auto mode, trigger entry
      if (bus.isAutoMode()) {
        bus.publish(EVENTS.EXECUTION_ENTRY, signal);
      }

      this.pendingSignals.push(signal);
    } else {
      bus.publish(EVENTS.EXECUTION_REJECTED, signal);
      this.rejectedSignals.push(signal);
      if (this.rejectedSignals.length > 100) this.rejectedSignals = this.rejectedSignals.slice(-50);
    }

    return signal;
  }

  // --- Calculate Entry, SL, TP ---
  _calculateEntry(symbol, direction, price, fvgs, orderBlocks, volatility, structure) {
    const atr = volatility?.atr || (symbol === 'XAUUSD' ? 30 : 2.50);
    const buffer = this.config.slBuffer[symbol] || 1.5;
    let entry, sl;

    // --- Entry Point ---
    let entryType = 'market';

    // Try FVG entry (optimal)
    if (this.config.useFVGForEntry && fvgs && fvgs.length > 0) {
      const alignedFVG = fvgs.find(f =>
        (direction === 'long' && f.type === 'bullish_fvg' && f.mid < price.mid) ||
        (direction === 'short' && f.type === 'bearish_fvg' && f.mid > price.mid)
      );
      if (alignedFVG) {
        entry = parseFloat(alignedFVG.mid.toFixed(2));
        entryType = 'fvg_limit';
      }
    }

    // Try Order Block entry
    if (!entry && this.config.useOBForEntry && orderBlocks && orderBlocks.length > 0) {
      const alignedOB = orderBlocks.find(ob =>
        (direction === 'long' && ob.type === 'bullish_ob' && ob.mid < price.mid) ||
        (direction === 'short' && ob.type === 'bearish_ob' && ob.mid > price.mid)
      );
      if (alignedOB) {
        entry = parseFloat(alignedOB.mid.toFixed(2));
        entryType = 'ob_limit';
      }
    }

    // Fallback: Market entry
    if (!entry) {
      entry = direction === 'long' ? price.ask : price.bid;
      entryType = 'market';
    }

    // --- Stop Loss (ATR-adjusted, below/above structure) ---
    if (direction === 'long') {
      // SL below recent swing low + buffer
      const structureLow = structure?.structure?.swingLows?.slice(-1)[0]?.price;
      sl = structureLow ? structureLow - buffer : entry - atr * 1.5;
    } else {
      // SL above recent swing high + buffer
      const structureHigh = structure?.structure?.swingHighs?.slice(-1)[0]?.price;
      sl = structureHigh ? structureHigh + buffer : entry + atr * 1.5;
    }
    sl = parseFloat(sl.toFixed(2));

    // --- Take Profits (multi-target) ---
    const stopDistance = Math.abs(entry - sl);
    const tp = this.config.tpMultipliers.map((mult, i) => {
      const tpPrice = direction === 'long'
        ? entry + stopDistance * mult
        : entry - stopDistance * mult;
      return {
        level: i + 1,
        price: parseFloat(tpPrice.toFixed(2)),
        rr: mult,
        closePercent: this.config.partialClosePercent[i] || 0.33
      };
    });

    return { entry: parseFloat(entry.toFixed(2)), sl, tp, entryType, stopDistance: parseFloat(stopDistance.toFixed(2)), atr };
  }

  // --- Get Active Signals ---
  getPendingSignals() { return this.pendingSignals; }
  getRecentRejections(count = 10) { return this.rejectedSignals.slice(-count); }
}

module.exports = ExecutionEngine;
