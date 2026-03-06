/**
 * Reputation System for Agent Marketplace
 * 
 * Features:
 * - Star ratings (0-5)
 * - Written reviews
 * - Trust levels based on history
 * - Verification badges
 * - Dispute history tracking
 * - Transaction-linked ratings
 */

const fs = require('fs');
const path = require('path');

class ReputationSystem {
  constructor(storePath = './reputation-state.json') {
    this.storePath = storePath;
    this.state = this.loadState();
  }

  loadState() {
    if (fs.existsSync(this.storePath)) {
      const data = fs.readFileSync(this.storePath, 'utf8');
      return JSON.parse(data);
    }
    return {
      agents: {}, // agentId -> profile
      ratings: [], // all ratings
      disputes: [] // dispute history
    };
  }

  saveState() {
    fs.writeFileSync(this.storePath, JSON.stringify(this.state, null, 2));
  }

  /**
   * Initialize agent profile
   */
  initProfile(agentId) {
    if (!this.state.agents[agentId]) {
      this.state.agents[agentId] = {
        agentId,
        created: Date.now(),
        totalRatings: 0,
        averageRating: 0,
        ratingBreakdown: { '5': 0, '4': 0, '3': 0, '2': 0, '1': 0 },
        totalTransactions: 0,
        successfulTransactions: 0,
        disputesAsProvider: 0,
        disputesAsClient: 0,
        disputesWon: 0,
        disputesLost: 0,
        trustLevel: 'new', // new, bronze, silver, gold, platinum
        verified: false,
        badges: [],
        metadata: {}
      };
      this.saveState();
    }
    return this.state.agents[agentId];
  }

  /**
   * Add rating for an agent
   */
  addRating({ agentId, raterId, rating, comment = '', transactionId = null, category = 'general' }) {
    // Validate rating
    if (rating < 0 || rating > 5) {
      throw new Error('Rating must be between 0 and 5');
    }

    // Initialize profile if needed
    this.initProfile(agentId);

    // Create rating record
    const ratingRecord = {
      id: 'rating_' + require('crypto').randomBytes(8).toString('hex'),
      agentId,
      raterId,
      rating,
      comment,
      category,
      transactionId,
      timestamp: Date.now(),
      helpful: 0, // Can be upvoted by others
      flagged: false
    };

    this.state.ratings.push(ratingRecord);

    // Update agent profile
    const profile = this.state.agents[agentId];
    profile.totalRatings++;
    
    // Update rating breakdown
    const ratingKey = Math.floor(rating).toString();
    profile.ratingBreakdown[ratingKey] = (profile.ratingBreakdown[ratingKey] || 0) + 1;

    // Recalculate average
    const allRatings = this.state.ratings.filter(r => r.agentId === agentId);
    profile.averageRating = allRatings.reduce((sum, r) => sum + r.rating, 0) / allRatings.length;

    // Update trust level
    this.updateTrustLevel(agentId);

    this.saveState();
    return ratingRecord;
  }

  /**
   * Record transaction completion
   */
  recordTransaction(agentId, success = true) {
    this.initProfile(agentId);
    const profile = this.state.agents[agentId];
    
    profile.totalTransactions++;
    if (success) {
      profile.successfulTransactions++;
    }

    this.updateTrustLevel(agentId);
    this.saveState();
  }

  /**
   * Record dispute
   */
  recordDispute({ agentId, role, reason, outcome = null, escrowId = null }) {
    this.initProfile(agentId);
    const profile = this.state.agents[agentId];

    const dispute = {
      id: 'dispute_' + require('crypto').randomBytes(8).toString('hex'),
      agentId,
      role, // 'provider' or 'client'
      reason,
      outcome, // 'won', 'lost', 'settled', null
      escrowId,
      timestamp: Date.now()
    };

    this.state.disputes.push(dispute);

    // Update profile
    if (role === 'provider') {
      profile.disputesAsProvider++;
    } else {
      profile.disputesAsClient++;
    }

    if (outcome === 'won') {
      profile.disputesWon++;
    } else if (outcome === 'lost') {
      profile.disputesLost++;
    }

    this.updateTrustLevel(agentId);
    this.saveState();

    return dispute;
  }

  /**
   * Calculate and update trust level
   */
  updateTrustLevel(agentId) {
    const profile = this.state.agents[agentId];
    
    const avgRating = profile.averageRating;
    const totalRatings = profile.totalRatings;
    const successRate = profile.totalTransactions > 0 
      ? profile.successfulTransactions / profile.totalTransactions 
      : 0;
    const disputeRate = profile.totalTransactions > 0
      ? (profile.disputesAsProvider + profile.disputesAsClient) / profile.totalTransactions
      : 0;

    // Calculate trust score (0-100)
    let trustScore = 0;

    // Rating component (40 points max)
    if (totalRatings >= 5) {
      trustScore += (avgRating / 5) * 40;
    } else {
      // Penalize for few ratings
      trustScore += (avgRating / 5) * 40 * (totalRatings / 5);
    }

    // Success rate component (30 points max)
    trustScore += successRate * 30;

    // Dispute penalty (up to -20 points)
    trustScore -= disputeRate * 20;

    // Volume bonus (10 points max)
    const volumeBonus = Math.min(profile.totalTransactions / 100, 1) * 10;
    trustScore += volumeBonus;

    // Verified bonus (20 points)
    if (profile.verified) {
      trustScore += 20;
    }

    // Determine trust level
    if (trustScore >= 80) {
      profile.trustLevel = 'platinum';
    } else if (trustScore >= 60) {
      profile.trustLevel = 'gold';
    } else if (trustScore >= 40) {
      profile.trustLevel = 'silver';
    } else if (trustScore >= 20) {
      profile.trustLevel = 'bronze';
    } else {
      profile.trustLevel = 'new';
    }

    profile.trustScore = Math.round(trustScore);

    // Award badges
    this.updateBadges(agentId);
  }

  /**
   * Award badges based on achievements
   */
  updateBadges(agentId) {
    const profile = this.state.agents[agentId];
    const badges = [];

    // Transaction milestones
    if (profile.totalTransactions >= 10) badges.push('10_transactions');
    if (profile.totalTransactions >= 50) badges.push('50_transactions');
    if (profile.totalTransactions >= 100) badges.push('100_transactions');

    // High ratings
    if (profile.averageRating >= 4.5 && profile.totalRatings >= 10) {
      badges.push('highly_rated');
    }
    if (profile.averageRating >= 4.8 && profile.totalRatings >= 25) {
      badges.push('top_rated');
    }

    // Reliability
    const successRate = profile.totalTransactions > 0
      ? profile.successfulTransactions / profile.totalTransactions
      : 0;
    if (successRate >= 0.95 && profile.totalTransactions >= 20) {
      badges.push('reliable');
    }

    // Low disputes
    const disputeRate = profile.totalTransactions > 0
      ? (profile.disputesAsProvider + profile.disputesAsClient) / profile.totalTransactions
      : 0;
    if (disputeRate <= 0.05 && profile.totalTransactions >= 20) {
      badges.push('trustworthy');
    }

    // Verified
    if (profile.verified) {
      badges.push('verified');
    }

    profile.badges = badges;
  }

  /**
   * Verify agent (manual or automated checks)
   */
  verifyAgent(agentId, verificationData = {}) {
    this.initProfile(agentId);
    const profile = this.state.agents[agentId];
    
    profile.verified = true;
    profile.verificationData = {
      timestamp: Date.now(),
      method: verificationData.method || 'manual',
      ...verificationData
    };

    this.updateTrustLevel(agentId);
    this.saveState();
  }

  /**
   * Get agent's reputation score
   */
  getScore(agentId) {
    const profile = this.state.agents[agentId];
    if (!profile) {
      return {
        agentId,
        average: 0,
        count: 0,
        exists: false
      };
    }

    return {
      agentId,
      average: profile.averageRating,
      count: profile.totalRatings,
      trustLevel: profile.trustLevel,
      trustScore: profile.trustScore,
      exists: true
    };
  }

  /**
   * Get full agent profile
   */
  getProfile(agentId) {
    return this.state.agents[agentId] || this.initProfile(agentId);
  }

  /**
   * Get ratings for an agent
   */
  getRatings(agentId, limit = 10) {
    return this.state.ratings
      .filter(r => r.agentId === agentId)
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, limit);
  }

  /**
   * Get top rated agents
   */
  getTopRated(limit = 10, minRatings = 5) {
    return Object.values(this.state.agents)
      .filter(a => a.totalRatings >= minRatings)
      .sort((a, b) => {
        // Sort by trust score, then average rating
        if (b.trustScore !== a.trustScore) {
          return b.trustScore - a.trustScore;
        }
        return b.averageRating - a.averageRating;
      })
      .slice(0, limit)
      .map(a => ({
        agentId: a.agentId,
        averageRating: a.averageRating,
        totalRatings: a.totalRatings,
        trustLevel: a.trustLevel,
        trustScore: a.trustScore,
        verified: a.verified,
        badges: a.badges
      }));
  }

  /**
   * Search agents by criteria
   */
  search({ minRating = 0, trustLevel = null, verified = null, minTransactions = 0 }) {
    let results = Object.values(this.state.agents);

    if (minRating > 0) {
      results = results.filter(a => a.averageRating >= minRating);
    }

    if (trustLevel) {
      results = results.filter(a => a.trustLevel === trustLevel);
    }

    if (verified !== null) {
      results = results.filter(a => a.verified === verified);
    }

    if (minTransactions > 0) {
      results = results.filter(a => a.totalTransactions >= minTransactions);
    }

    return results.map(a => ({
      agentId: a.agentId,
      averageRating: a.averageRating,
      totalRatings: a.totalRatings,
      trustLevel: a.trustLevel,
      verified: a.verified,
      totalTransactions: a.totalTransactions
    }));
  }

  /**
   * Get system statistics
   */
  getStats() {
    const agents = Object.values(this.state.agents);
    const totalRatings = this.state.ratings.length;
    const avgRating = this.state.ratings.reduce((sum, r) => sum + r.rating, 0) / totalRatings || 0;

    const byTrustLevel = agents.reduce((acc, a) => {
      acc[a.trustLevel] = (acc[a.trustLevel] || 0) + 1;
      return acc;
    }, {});

    return {
      totalAgents: agents.length,
      totalRatings,
      avgRating: avgRating.toFixed(2),
      verifiedAgents: agents.filter(a => a.verified).length,
      byTrustLevel,
      totalDisputes: this.state.disputes.length
    };
  }
}

module.exports = { ReputationSystem };
