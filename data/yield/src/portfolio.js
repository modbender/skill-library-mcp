/**
 * YIELD Portfolio Manager
 *
 * Tracks the five psychological asset classes across a conversation
 * and computes compound yield scores. This is the "investment portfolio"
 * of every conversation.
 *
 * Asset Classes:
 *   trust       — Compounds slowly, like government bonds
 *   commitment  — Stacks and locks, like real estate equity
 *   urgency     — Decays rapidly, like options contracts
 *   curiosity   — Pulls forward, like futures contracts
 *   authority   — Grows with proof, like blue-chip stocks
 */

// ─── Configuration ───────────────────────────────────────────────────────────

const DEFAULT_CONFIG = {
  // Compounding multiplier for positive trust signals
  trustCompoundRate: 1.12,

  // Urgency decay per message without reinforcement
  urgencyDecayRate: 0.85,

  // Curiosity decay when loops are closed
  curiosityClosureDecay: 0.12,

  // Weights for total yield calculation (must sum to 1.0)
  weights: {
    trust: 0.35,
    commitment: 0.25,
    urgency: 0.15,
    curiosity: 0.15,
    authority: 0.10,
  },

  // Asset floor and ceiling
  minValue: 0.0,
  maxValue: 1.0,

  // Starting values (slightly above zero — benefit of the doubt)
  initialValues: {
    trust: 0.10,
    commitment: 0.05,
    urgency: 0.05,
    curiosity: 0.15,
    authority: 0.10,
  },
};

// ─── Portfolio Class ─────────────────────────────────────────────────────────

export class Portfolio {
  constructor(config = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.assets = { ...this.config.initialValues };
    this.history = [];          // yield score history for trend detection
    this.messageCount = 0;
    this.lastSignalTypes = new Set();
    this.peakYield = 0;
    this.createdAt = Date.now();
  }

  /**
   * Apply detected signals to the portfolio.
   * This is where compounding happens.
   *
   * @param {Array<{type: string, assets: Object, confidence: number}>} signals
   * @returns {Object} Updated portfolio state
   */
  applySignals(signals) {
    this.messageCount++;
    this.lastSignalTypes.clear();

    // Track which asset classes received reinforcement this turn
    const reinforced = new Set();

    for (const signal of signals) {
      this.lastSignalTypes.add(signal.type);
      const confidence = signal.confidence || 0.8;

      for (const [asset, delta] of Object.entries(signal.assets)) {
        if (this.assets[asset] === undefined) continue;

        let effectiveDelta = delta * confidence;

        // ── COMPOUNDING LOGIC ──
        // Positive trust signals compound on existing trust
        if (asset === 'trust' && delta > 0) {
          effectiveDelta *= (1 + this.assets.trust * (this.config.trustCompoundRate - 1));
        }

        // Commitment stacks harder when trust is high (trust unlocks commitment)
        if (asset === 'commitment' && delta > 0 && this.assets.trust > 0.4) {
          effectiveDelta *= 1.25;
        }

        // Authority gains are amplified when curiosity is high (they asked, you delivered)
        if (asset === 'authority' && delta > 0 && this.assets.curiosity > 0.3) {
          effectiveDelta *= 1.3;
        }

        this.assets[asset] = this._clamp(this.assets[asset] + effectiveDelta);
        if (delta > 0) reinforced.add(asset);
      }
    }

    // ── DECAY: Urgency decays every turn it's not reinforced ──
    if (!reinforced.has('urgency')) {
      this.assets.urgency *= this.config.urgencyDecayRate;
      this.assets.urgency = this._clamp(this.assets.urgency);
    }

    // ── DECAY: Curiosity slowly decays if not fed ──
    if (!reinforced.has('curiosity') && this.messageCount > 3) {
      this.assets.curiosity *= 0.95;
      this.assets.curiosity = this._clamp(this.assets.curiosity);
    }

    // Record yield history
    const totalYield = this.calculateTotalYield();
    this.history.push({
      messageIndex: this.messageCount,
      yield: totalYield,
      assets: { ...this.assets },
      timestamp: Date.now(),
    });

    if (totalYield > this.peakYield) {
      this.peakYield = totalYield;
    }

    return this.getState();
  }

  /**
   * Calculate the total compound yield using weighted geometric mean.
   * This models true compounding — weak assets drag down the whole portfolio.
   *
   * @returns {number} Total yield between 0.0 and 1.0
   */
  calculateTotalYield() {
    const w = this.config.weights;
    const a = this.assets;

    // Weighted geometric mean (product of assets raised to their weights)
    // This naturally penalizes portfolios with one zero — just like real investing.
    const yield_ =
      Math.pow(Math.max(a.trust, 0.001), w.trust) *
      Math.pow(Math.max(a.commitment, 0.001), w.commitment) *
      Math.pow(Math.max(a.urgency, 0.001), w.urgency) *
      Math.pow(Math.max(a.curiosity, 0.001), w.curiosity) *
      Math.pow(Math.max(a.authority, 0.001), w.authority);

    return Math.round(yield_ * 1000) / 1000;
  }

  /**
   * Detect yield inversion: when the trajectory flips negative.
   * Like an inverted yield curve predicting recession — this predicts abandonment.
   *
   * @returns {{ inverted: boolean, severity: number, turnsUntilAbandon: number | null }}
   */
  detectInversion() {
    if (this.history.length < 3) {
      return { inverted: false, severity: 0, turnsUntilAbandon: null };
    }

    const recent = this.history.slice(-5);
    const yields = recent.map(h => h.yield);

    // Calculate velocity (rate of change)
    let velocity = 0;
    for (let i = 1; i < yields.length; i++) {
      velocity += (yields[i] - yields[i - 1]);
    }
    velocity /= (yields.length - 1);

    // Calculate acceleration (rate of velocity change)
    let acceleration = 0;
    if (yields.length >= 3) {
      const firstHalf = yields.slice(0, Math.ceil(yields.length / 2));
      const secondHalf = yields.slice(Math.floor(yields.length / 2));
      const v1 = (firstHalf[firstHalf.length - 1] - firstHalf[0]) / firstHalf.length;
      const v2 = (secondHalf[secondHalf.length - 1] - secondHalf[0]) / secondHalf.length;
      acceleration = v2 - v1;
    }

    const inverted = velocity < -0.02 && acceleration <= 0;
    const severity = inverted ? Math.min(Math.abs(velocity) * 10, 1.0) : 0;

    // Estimate turns until abandon (yield hits near-zero)
    let turnsUntilAbandon = null;
    if (inverted && velocity < 0) {
      const currentYield = yields[yields.length - 1];
      turnsUntilAbandon = Math.max(1, Math.ceil(currentYield / Math.abs(velocity)));
    }

    return {
      inverted,
      severity: Math.round(severity * 100) / 100,
      turnsUntilAbandon,
      velocity: Math.round(velocity * 1000) / 1000,
      acceleration: Math.round(acceleration * 1000) / 1000,
    };
  }

  /**
   * Detect if we're in a conversion window — the optimal moment to present an offer.
   *
   * Conditions:
   * - Trust above threshold (foundation is solid)
   * - Commitment above threshold (they've invested)
   * - Yield is near peak or rising
   * - No active inversion
   *
   * @returns {{ open: boolean, strength: number, reason: string }}
   */
  detectConversionWindow() {
    const a = this.assets;
    const totalYield = this.calculateTotalYield();
    const inversion = this.detectInversion();

    if (inversion.inverted) {
      return { open: false, strength: 0, reason: 'yield_inverted' };
    }

    if (a.trust < 0.45) {
      return { open: false, strength: 0, reason: 'insufficient_trust' };
    }

    if (a.commitment < 0.35) {
      return { open: false, strength: 0, reason: 'insufficient_commitment' };
    }

    // Check if yield is near peak
    const nearPeak = totalYield >= this.peakYield * 0.85;

    // Check if multiple asset classes are strong
    const strongAssets = Object.values(a).filter(v => v > 0.4).length;

    if (strongAssets >= 3 && nearPeak) {
      const strength = Math.min(
        (a.trust + a.commitment + a.urgency) / 3,
        1.0
      );
      return {
        open: true,
        strength: Math.round(strength * 100) / 100,
        reason: 'portfolio_aligned',
      };
    }

    // Special case: high urgency + high trust = window even if other assets are moderate
    if (a.trust > 0.6 && a.urgency > 0.5 && a.commitment > 0.3) {
      return {
        open: true,
        strength: Math.round(((a.trust + a.urgency) / 2) * 100) / 100,
        reason: 'urgency_trust_convergence',
      };
    }

    return { open: false, strength: 0, reason: 'not_ready' };
  }

  /**
   * Get the current portfolio state snapshot.
   */
  getState() {
    return {
      assets: { ...this.assets },
      totalYield: this.calculateTotalYield(),
      messageCount: this.messageCount,
      peakYield: this.peakYield,
      inversion: this.detectInversion(),
      conversionWindow: this.detectConversionWindow(),
    };
  }

  /**
   * Export portfolio as a serializable object (for persistence).
   */
  toJSON() {
    return {
      assets: { ...this.assets },
      history: this.history,
      messageCount: this.messageCount,
      peakYield: this.peakYield,
      createdAt: this.createdAt,
    };
  }

  /**
   * Restore portfolio from serialized state.
   */
  static fromJSON(data, config = {}) {
    const portfolio = new Portfolio(config);
    portfolio.assets = { ...data.assets };
    portfolio.history = data.history || [];
    portfolio.messageCount = data.messageCount || 0;
    portfolio.peakYield = data.peakYield || 0;
    portfolio.createdAt = data.createdAt || Date.now();
    return portfolio;
  }

  /** @private */
  _clamp(value) {
    return Math.max(this.config.minValue, Math.min(this.config.maxValue, value));
  }
}
