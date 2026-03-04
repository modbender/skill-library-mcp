/**
 * Vouching System with Stake-at-Risk
 * 
 * Allows established agents to vouch for newcomers.
 * Voucher's reputation is partially bound to vouchee's behavior.
 * 
 * Reference: Tang et al. 2010, "Hybrid Transitive-Trust Mechanisms"
 * Transitive trust: Trust(A->C) = Trust(A->B) * Trust(B->C) * 0.8
 * 
 * Features:
 * - Vouching with stake (voucher risks reputation)
 * - Transitive trust propagation (2 hops max)
 * - Vouch limits per agent (prevents vouch spam)
 * - Slashing for voucher when vouchee misbehaves
 * - Time-weighted decay of vouches
 */

class VouchingSystem {
  constructor(opts = {}) {
    this.maxVouchesPerAgent = opts.maxVouches || 5;
    this.transitiveDecay = opts.transitiveDecay || 0.8;
    this.vouchHalfLifeDays = opts.vouchHalfLife || 30;
    
    // In-memory store (would be on-chain or DB in production)
    this.vouches = [];  // { voucher, vouchee, stake, timestamp, active }
    this.slashes = [];  // { voucher, vouchee, reason, amount, timestamp }
  }

  /**
   * Create a vouch
   * @param {string} voucher - Agent providing the vouch
   * @param {string} vouchee - Agent being vouched for
   * @param {number} voucherScore - Current trust score of voucher
   * @param {number} stake - Reputation stake (0-100, portion of score at risk)
   * @returns {Object} - Vouch result
   */
  vouch(voucher, vouchee, voucherScore, stake = 10) {
    // Validate
    if (voucher === vouchee) {
      return { success: false, error: 'Cannot vouch for yourself' };
    }

    if (voucherScore < 40) {
      return { success: false, error: 'Voucher trust too low (minimum 40)' };
    }

    if (stake > voucherScore * 0.25) {
      return { success: false, error: `Stake too high (max ${Math.round(voucherScore * 0.25)}% of your score)` };
    }

    // Check vouch limit
    const activeVouches = this.vouches.filter(v => 
      v.voucher === voucher && v.active
    );
    if (activeVouches.length >= this.maxVouchesPerAgent) {
      return { success: false, error: `Max ${this.maxVouchesPerAgent} active vouches reached` };
    }

    // Check if already vouching for this agent
    const existing = this.vouches.find(v => 
      v.voucher === voucher && v.vouchee === vouchee && v.active
    );
    if (existing) {
      return { success: false, error: 'Already vouching for this agent' };
    }

    const vouchRecord = {
      id: `vouch_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
      voucher,
      vouchee,
      stake,
      voucherScoreAtTime: voucherScore,
      timestamp: Date.now(),
      active: true,
    };

    this.vouches.push(vouchRecord);

    // Calculate trust boost for vouchee
    const trustBoost = this._calculateBoost(voucherScore, stake);

    return {
      success: true,
      vouchId: vouchRecord.id,
      trustBoost,
      stakeAtRisk: stake,
      message: `${voucher} vouched for ${vouchee} with ${stake} stake. Trust boost: +${trustBoost}`,
    };
  }

  /**
   * Slash a voucher when their vouchee misbehaves
   * @param {string} vouchee - The agent that misbehaved
   * @param {string} reason - Why they're being slashed
   * @param {number} severity - 0-1 (0.1 = minor, 0.5 = moderate, 1.0 = severe)
   * @returns {Array} - Affected vouchers and penalties
   */
  slash(vouchee, reason, severity = 0.5) {
    const affectedVouches = this.vouches.filter(v => 
      v.vouchee === vouchee && v.active
    );

    const penalties = [];

    for (const vouch of affectedVouches) {
      const penalty = Math.round(vouch.stake * severity);

      this.slashes.push({
        voucher: vouch.voucher,
        vouchee,
        reason,
        amount: penalty,
        severity,
        timestamp: Date.now(),
      });

      penalties.push({
        voucher: vouch.voucher,
        penalty,
        originalStake: vouch.stake,
        reason,
      });

      // Deactivate vouch on severe violations
      if (severity >= 0.5) {
        vouch.active = false;
      }
    }

    return penalties;
  }

  /**
   * Get trust boost for an agent from all active vouches
   * Includes time decay and transitive trust
   */
  getTrustBoost(agentName) {
    const now = Date.now();
    let totalBoost = 0;
    const activeVouches = [];

    for (const vouch of this.vouches) {
      if (vouch.vouchee !== agentName || !vouch.active) continue;

      // Time decay
      const ageDays = (now - vouch.timestamp) / (1000 * 60 * 60 * 24);
      const decay = Math.pow(0.5, ageDays / this.vouchHalfLifeDays);

      const boost = this._calculateBoost(vouch.voucherScoreAtTime, vouch.stake) * decay;
      totalBoost += boost;

      activeVouches.push({
        voucher: vouch.voucher,
        boost: Math.round(boost * 10) / 10,
        stake: vouch.stake,
        ageDays: Math.round(ageDays),
        decay: Math.round(decay * 100),
      });
    }

    // Check for transitive vouches (2 hops)
    // If A vouches for B, and B vouches for C, C gets transitive trust from A
    const directVouchers = activeVouches.map(v => v.voucher);
    for (const vouch of this.vouches) {
      if (!vouch.active) continue;
      if (!directVouchers.includes(vouch.vouchee)) continue;
      if (vouch.voucher === agentName) continue;

      const ageDays = (now - vouch.timestamp) / (1000 * 60 * 60 * 24);
      const decay = Math.pow(0.5, ageDays / this.vouchHalfLifeDays);
      const transitiveBoost = this._calculateBoost(vouch.voucherScoreAtTime, vouch.stake)
        * decay * this.transitiveDecay;

      if (transitiveBoost > 0.5) {
        totalBoost += transitiveBoost;
        activeVouches.push({
          voucher: `${vouch.voucher} (via ${vouch.vouchee})`,
          boost: Math.round(transitiveBoost * 10) / 10,
          transitive: true,
        });
      }
    }

    // Cap total boost
    totalBoost = Math.min(25, totalBoost);

    return {
      totalBoost: Math.round(totalBoost * 10) / 10,
      vouches: activeVouches,
      count: activeVouches.length,
    };
  }

  /**
   * Get slash history for an agent (as voucher)
   */
  getSlashHistory(voucher) {
    return this.slashes.filter(s => s.voucher === voucher);
  }

  _calculateBoost(voucherScore, stake) {
    // Boost = sqrt(voucherScore * stake) / 10
    // Higher voucher score = more meaningful vouch
    // Higher stake = more skin in the game
    return Math.round(Math.sqrt(voucherScore * stake) / 10 * 10) / 10;
  }

  /**
   * Export state for persistence
   */
  toJSON() {
    return {
      vouches: this.vouches,
      slashes: this.slashes,
    };
  }

  /**
   * Import state
   */
  fromJSON(data) {
    this.vouches = data.vouches || [];
    this.slashes = data.slashes || [];
  }
}

module.exports = { VouchingSystem };
