// ============================================================================
// BIAS ENGINE — HTF & Intraday Directional Bias with Conviction Scoring
// ============================================================================
// Produces: HTF Bias, Intraday Bias, Conviction Score (0-100),
//           Alignment Score (Technical + Macro)
// Rules: Weekly > Daily > Intraday. Macro conflict reduces conviction.
//        Liquidity sweep resets bias.
// Emits: bias.update, bias.flip, bias.conflict
// Stores: data/bias-memory.json
// ============================================================================

const bus = require('../automation/event-bus');
const { EVENTS } = bus;
const fs = require('fs');
const path = require('path');

class BiasEngine {
  constructor(config = {}) {
    this.config = {
      biasMemoryFile: config.biasMemoryFile || path.join(__dirname, '../data/bias-memory.json'),
      convictionWeights: {
        weeklyStructure: 0.30,
        dailyStructure: 0.25,
        intradayStructure: 0.15,
        liquidityAlignment: 0.10,
        macroAlignment: 0.10,
        sessionAlignment: 0.05,
        fvgPresence: 0.05
      },
      conflictPenalty: 0.30, // Reduce conviction by 30% on macro conflict
      sweepResetCooldown: 3, // Candles before re-evaluating after sweep
      ...config
    };

    this.bias = {
      XAUUSD: this._defaultBias(),
      XAGUSD: this._defaultBias()
    };

    this.biasHistory = [];
    this._loadMemory();

    // Listen for sweep events to reset bias
    bus.on(EVENTS.LIQUIDITY_SWEEP, (data) => this._onSweep(data));
  }

  _defaultBias() {
    return {
      htfBias: 'neutral',       // bullish | bearish | neutral
      intradayBias: 'neutral',
      conviction: 0,            // 0-100
      alignmentScore: 0,        // 0-1
      technicalScore: 0,
      macroScore: 0,
      lastUpdate: null,
      components: {},
      cooldown: false
    };
  }

  // --- Main Bias Calculation ---
  calculate(symbol, inputs) {
    const {
      structureMTF,     // from StructureEngine.getMTFAlignment()
      liquidityState,   // from LiquidityEngine
      macroState,       // from MacroEngine
      sessionState,     // from SessionEngine
      volatilityState,  // from VolatilityEngine
      fvgs              // from StructureEngine
    } = inputs;

    const prev = { ...this.bias[symbol] };
    const weights = this.config.convictionWeights;

    // --- 1. Structure Scores by Timeframe ---
    const weeklyBias = structureMTF?.timeframes?.W1 || structureMTF?.timeframes?.D1 || 'neutral';
    const dailyBias = structureMTF?.timeframes?.D1 || 'neutral';
    const h4Bias = structureMTF?.timeframes?.H4 || 'neutral';
    const h1Bias = structureMTF?.timeframes?.H1 || 'neutral';
    const m15Bias = structureMTF?.timeframes?.M15 || 'neutral';

    // HTF Bias: Weekly overrides Daily
    let htfBias = 'neutral';
    if (weeklyBias !== 'neutral') htfBias = weeklyBias;
    else if (dailyBias !== 'neutral') htfBias = dailyBias;

    // Intraday Bias: H4 > H1 > M15
    let intradayBias = 'neutral';
    if (h4Bias !== 'neutral') intradayBias = h4Bias;
    else if (h1Bias !== 'neutral') intradayBias = h1Bias;
    else if (m15Bias !== 'neutral') intradayBias = m15Bias;

    // --- 2. Component Scores ---
    const components = {};

    // Weekly structure score
    components.weeklyStructure = this._biasToScore(weeklyBias, htfBias) * weights.weeklyStructure;
    components.dailyStructure = this._biasToScore(dailyBias, htfBias) * weights.dailyStructure;
    components.intradayStructure = this._biasToScore(intradayBias, htfBias) * weights.intradayStructure;

    // Liquidity alignment
    const liquidityAligned = this._checkLiquidityAlignment(liquidityState, htfBias);
    components.liquidityAlignment = (liquidityAligned ? 1 : 0) * weights.liquidityAlignment;

    // Macro alignment
    const macroAligned = this._checkMacroAlignment(macroState, htfBias);
    components.macroAlignment = (macroAligned ? 1 : 0.3) * weights.macroAlignment;

    // Session alignment
    const sessionAligned = sessionState?.isLondon || sessionState?.isNY || sessionState?.isLondonNYOverlap;
    components.sessionAlignment = (sessionAligned ? 1 : 0.5) * weights.sessionAlignment;

    // FVG presence
    const hasFVG = fvgs && fvgs.length > 0;
    const fvgAligned = hasFVG && fvgs.some(f =>
      (htfBias === 'bullish' && f.type === 'bullish_fvg') ||
      (htfBias === 'bearish' && f.type === 'bearish_fvg')
    );
    components.fvgPresence = (fvgAligned ? 1 : hasFVG ? 0.3 : 0) * weights.fvgPresence;

    // --- 3. Raw Conviction ---
    let rawConviction = Object.values(components).reduce((sum, v) => sum + v, 0) * 100;

    // --- 4. Apply Penalties ---
    // Macro conflict penalty
    if (!macroAligned && macroState?.macro_risk === 'high') {
      rawConviction *= (1 - this.config.conflictPenalty);
      bus.publish(EVENTS.BIAS_CONFLICT, {
        symbol,
        reason: 'macro_conflict',
        htfBias,
        macroBias: macroState.macro_bias
      });
    }

    // Cooldown after sweep
    if (this.bias[symbol].cooldown) {
      rawConviction *= 0.5;
    }

    // Clamp
    const conviction = Math.min(100, Math.max(0, Math.round(rawConviction)));

    // --- 5. Alignment Score ---
    const technicalScore = (components.weeklyStructure + components.dailyStructure + components.intradayStructure) /
      (weights.weeklyStructure + weights.dailyStructure + weights.intradayStructure);
    const macroScore = macroAligned ? 1 : 0;
    const alignmentScore = parseFloat(((technicalScore * 0.7 + macroScore * 0.3)).toFixed(2));

    // --- 6. Update State ---
    this.bias[symbol] = {
      htfBias,
      intradayBias,
      conviction,
      alignmentScore,
      technicalScore: parseFloat(technicalScore.toFixed(2)),
      macroScore,
      lastUpdate: new Date().toISOString(),
      components,
      cooldown: this.bias[symbol].cooldown
    };

    // --- 7. Detect Bias Flip ---
    if (prev.htfBias !== 'neutral' && htfBias !== 'neutral' && prev.htfBias !== htfBias) {
      bus.publish(EVENTS.BIAS_FLIP, {
        symbol,
        from: prev.htfBias,
        to: htfBias,
        conviction,
        reason: 'structure_shift'
      });
    }

    // --- 8. Emit Update ---
    bus.publish(EVENTS.BIAS_UPDATE, {
      symbol,
      ...this.bias[symbol]
    });

    // --- 9. Save Memory ---
    this._saveMemory();

    return this.bias[symbol];
  }

  // --- Helper: Bias to Score ---
  _biasToScore(tfBias, htfBias) {
    if (tfBias === htfBias) return 1;
    if (tfBias === 'neutral') return 0.5;
    return 0; // Opposing
  }

  // --- Check Liquidity Alignment ---
  _checkLiquidityAlignment(liquidityState, bias) {
    if (!liquidityState) return false;
    const sweeps = liquidityState.recentSweeps || [];
    if (sweeps.length === 0) return false;

    const lastSweep = sweeps[sweeps.length - 1];
    if (bias === 'bullish' && lastSweep.type === 'bullish_sweep') return true;
    if (bias === 'bearish' && lastSweep.type === 'bearish_sweep') return true;
    return false;
  }

  // --- Check Macro Alignment ---
  _checkMacroAlignment(macroState, bias) {
    if (!macroState) return true; // No data = assume neutral
    if (bias === 'bullish' && macroState.macro_bias === 'bullish_gold') return true;
    if (bias === 'bearish' && macroState.macro_bias === 'bearish_gold') return true;
    if (macroState.macro_bias === 'neutral') return true;
    return false;
  }

  // --- On Liquidity Sweep: Cooldown ---
  _onSweep(data) {
    const symbol = data.symbol;
    if (!symbol || !this.bias[symbol]) return;

    this.bias[symbol].cooldown = true;
    setTimeout(() => {
      if (this.bias[symbol]) this.bias[symbol].cooldown = false;
    }, this.config.sweepResetCooldown * 60000); // cooldown in minutes
  }

  // --- Get Bias ---
  getBias(symbol) {
    return this.bias[symbol] || this._defaultBias();
  }

  // --- Memory Persistence ---
  _saveMemory() {
    try {
      const memory = {
        timestamp: new Date().toISOString(),
        bias: this.bias,
        history: this.biasHistory.slice(-100)
      };
      fs.writeFileSync(this.config.biasMemoryFile, JSON.stringify(memory, null, 2));
    } catch (e) { /* silent */ }
  }

  _loadMemory() {
    try {
      if (fs.existsSync(this.config.biasMemoryFile)) {
        const data = JSON.parse(fs.readFileSync(this.config.biasMemoryFile, 'utf8'));
        if (data.bias) this.bias = { ...this.bias, ...data.bias };
        if (data.history) this.biasHistory = data.history;
      }
    } catch (e) { /* silent */ }
  }
}

module.exports = BiasEngine;
