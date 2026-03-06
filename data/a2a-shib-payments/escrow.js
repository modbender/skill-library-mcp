/**
 * Escrow System for Trustless Agent-to-Agent Payments
 * 
 * Features:
 * - Time-locked payments
 * - Conditional releases
 * - Dispute resolution
 * - Multi-party approvals
 * - Automatic refunds
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

class EscrowSystem {
  constructor(storePath = './escrow-state.json') {
    this.storePath = storePath;
    this.escrows = this.loadState();
  }

  loadState() {
    if (fs.existsSync(this.storePath)) {
      const data = fs.readFileSync(this.storePath, 'utf8');
      return JSON.parse(data);
    }
    return {};
  }

  saveState() {
    fs.writeFileSync(this.storePath, JSON.stringify(this.escrows, null, 2));
  }

  /**
   * Create new escrow
   * 
   * @param {object} params
   * @param {string} params.payer - Agent ID of payer
   * @param {string} params.payee - Agent ID or address of recipient
   * @param {number} params.amount - Amount in SHIB
   * @param {string} params.purpose - Description of escrow purpose
   * @param {object} params.conditions - Release conditions
   * @param {number} params.timeoutMinutes - Auto-refund after timeout (optional)
   */
  create({ payer, payee, amount, purpose, conditions = {}, timeoutMinutes = null }) {
    const escrowId = 'esc_' + crypto.randomBytes(16).toString('hex');
    
    const now = Date.now();
    const escrow = {
      id: escrowId,
      payer,
      payee,
      amount,
      purpose,
      conditions: {
        requiresApproval: conditions.requiresApproval !== false, // Default true
        requiresDelivery: conditions.requiresDelivery || false,
        requiresArbiter: conditions.requiresArbiter || false,
        customConditions: conditions.customConditions || [],
        ...conditions
      },
      state: 'pending', // pending → funded → locked → released/refunded/disputed
      timeline: {
        created: now,
        funded: null,
        locked: null,
        released: null,
        refunded: null,
        disputed: null
      },
      timeout: timeoutMinutes ? now + (timeoutMinutes * 60 * 1000) : null,
      approvals: [],
      deliveryProof: null,
      disputeReason: null,
      txHash: null,
      metadata: {}
    };

    this.escrows[escrowId] = escrow;
    this.saveState();

    return escrow;
  }

  /**
   * Fund escrow (mark as funded - actual payment happens separately)
   */
  fund(escrowId, txHash) {
    const escrow = this.escrows[escrowId];
    if (!escrow) throw new Error('Escrow not found');
    if (escrow.state !== 'pending') throw new Error(`Cannot fund escrow in state: ${escrow.state}`);

    escrow.state = 'funded';
    escrow.timeline.funded = Date.now();
    escrow.txHash = txHash;

    // Auto-lock if no approval required
    if (!escrow.conditions.requiresApproval) {
      escrow.state = 'locked';
      escrow.timeline.locked = Date.now();
    }

    this.saveState();
    return escrow;
  }

  /**
   * Approve escrow (move to locked state)
   */
  approve(escrowId, approverId) {
    const escrow = this.escrows[escrowId];
    if (!escrow) throw new Error('Escrow not found');
    if (escrow.state !== 'funded') throw new Error(`Cannot approve escrow in state: ${escrow.state}`);

    if (!escrow.approvals.includes(approverId)) {
      escrow.approvals.push(approverId);
    }

    // Check if all required approvals met
    const requiredApprovers = [escrow.payer, escrow.payee];
    const allApproved = requiredApprovers.every(id => escrow.approvals.includes(id));

    if (allApproved) {
      escrow.state = 'locked';
      escrow.timeline.locked = Date.now();
    }

    this.saveState();
    return escrow;
  }

  /**
   * Submit delivery proof
   */
  submitDelivery(escrowId, proof) {
    const escrow = this.escrows[escrowId];
    if (!escrow) throw new Error('Escrow not found');
    if (escrow.state !== 'locked') throw new Error(`Cannot submit delivery for escrow in state: ${escrow.state}`);

    escrow.deliveryProof = {
      submittedBy: proof.submittedBy || escrow.payee,
      timestamp: Date.now(),
      data: proof.data,
      signature: proof.signature || null
    };

    // Auto-release if delivery was the only condition (and no arbiter required)
    if (escrow.conditions.requiresDelivery && !escrow.conditions.requiresArbiter && !escrow.conditions.requiresClientConfirmation) {
      this.release(escrowId, 'automatic - delivery confirmed');
    }

    this.saveState();
    return escrow;
  }

  /**
   * Release funds to payee
   */
  release(escrowId, reason = 'manual release') {
    const escrow = this.escrows[escrowId];
    if (!escrow) throw new Error('Escrow not found');
    if (escrow.state !== 'locked') throw new Error(`Cannot release escrow in state: ${escrow.state}`);

    // Check conditions
    if (escrow.conditions.requiresDelivery && !escrow.deliveryProof) {
      throw new Error('Delivery proof required before release');
    }

    escrow.state = 'released';
    escrow.timeline.released = Date.now();
    escrow.metadata.releaseReason = reason;

    this.saveState();
    return escrow;
  }

  /**
   * Refund to payer
   */
  refund(escrowId, reason = 'manual refund') {
    const escrow = this.escrows[escrowId];
    if (!escrow) throw new Error('Escrow not found');
    if (!['funded', 'locked', 'disputed'].includes(escrow.state)) {
      throw new Error(`Cannot refund escrow in state: ${escrow.state}`);
    }

    escrow.state = 'refunded';
    escrow.timeline.refunded = Date.now();
    escrow.metadata.refundReason = reason;

    this.saveState();
    return escrow;
  }

  /**
   * Open dispute
   */
  dispute(escrowId, disputerId, reason) {
    const escrow = this.escrows[escrowId];
    if (!escrow) throw new Error('Escrow not found');
    if (escrow.state !== 'locked') throw new Error(`Cannot dispute escrow in state: ${escrow.state}`);

    escrow.state = 'disputed';
    escrow.timeline.disputed = Date.now();
    escrow.disputeReason = {
      disputerId,
      reason,
      timestamp: Date.now()
    };

    this.saveState();
    return escrow;
  }

  /**
   * Resolve dispute (arbiter decision)
   */
  resolveDispute(escrowId, decision, arbiter) {
    const escrow = this.escrows[escrowId];
    if (!escrow) throw new Error('Escrow not found');
    if (escrow.state !== 'disputed') throw new Error(`Escrow not in disputed state`);

    if (decision === 'release') {
      this.release(escrowId, `arbiter decision by ${arbiter}`);
    } else if (decision === 'refund') {
      this.refund(escrowId, `arbiter decision by ${arbiter}`);
    } else {
      throw new Error(`Invalid dispute resolution: ${decision}`);
    }

    escrow.metadata.arbiter = arbiter;
    this.saveState();
    return escrow;
  }

  /**
   * Check for expired escrows and auto-refund
   */
  processTimeouts() {
    const now = Date.now();
    const expired = [];

    for (const [id, escrow] of Object.entries(this.escrows)) {
      if (escrow.timeout && escrow.timeout < now && ['funded', 'locked'].includes(escrow.state)) {
        this.refund(id, 'automatic timeout');
        expired.push(id);
      }
    }

    return expired;
  }

  /**
   * Get escrow by ID
   */
  get(escrowId) {
    return this.escrows[escrowId] || null;
  }

  /**
   * List escrows with filters
   */
  list(filters = {}) {
    let results = Object.values(this.escrows);

    if (filters.payer) {
      results = results.filter(e => e.payer === filters.payer);
    }

    if (filters.payee) {
      results = results.filter(e => e.payee === filters.payee);
    }

    if (filters.state) {
      results = results.filter(e => e.state === filters.state);
    }

    if (filters.minAmount) {
      results = results.filter(e => e.amount >= filters.minAmount);
    }

    return results;
  }

  /**
   * Get escrow stats
   */
  getStats() {
    const all = Object.values(this.escrows);
    const byState = all.reduce((acc, e) => {
      acc[e.state] = (acc[e.state] || 0) + 1;
      return acc;
    }, {});

    const totalLocked = all
      .filter(e => e.state === 'locked')
      .reduce((sum, e) => sum + e.amount, 0);

    return {
      total: all.length,
      byState,
      totalLocked,
      activeEscrows: all.filter(e => ['funded', 'locked'].includes(e.state)).length
    };
  }
}

module.exports = { EscrowSystem };
