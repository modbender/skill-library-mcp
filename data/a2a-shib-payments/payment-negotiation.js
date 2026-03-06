/**
 * Payment Negotiation System (x402-inspired)
 * 
 * Enables agent-to-agent service negotiation and payment
 * 
 * Flow:
 * 1. Client requests service → Server quotes price
 * 2. Client accepts/rejects/counters
 * 3. Agreement reached → Escrow created
 * 4. Service delivered → Payment released
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

class PaymentNegotiationSystem {
  constructor(escrowSystem, storePath = './negotiation-state.json') {
    this.escrowSystem = escrowSystem;
    this.storePath = storePath;
    this.negotiations = this.loadState();
  }

  loadState() {
    if (fs.existsSync(this.storePath)) {
      const data = fs.readFileSync(this.storePath, 'utf8');
      return JSON.parse(data);
    }
    return {};
  }

  saveState() {
    fs.writeFileSync(this.storePath, JSON.stringify(this.negotiations, null, 2));
  }

  /**
   * Service provider creates a price quote
   * 
   * @param {object} params
   * @param {string} params.providerId - Agent ID of service provider
   * @param {string} params.clientId - Agent ID of client
   * @param {string} params.service - Service description
   * @param {number} params.price - Price in SHIB
   * @param {object} params.terms - Service terms
   * @param {number} params.validForMinutes - Quote validity period
   */
  createQuote({ providerId, clientId, service, price, terms = {}, validForMinutes = 60 }) {
    const quoteId = 'quote_' + crypto.randomBytes(16).toString('hex');
    
    const now = Date.now();
    const quote = {
      id: quoteId,
      providerId,
      clientId,
      service,
      price,
      terms: {
        deliveryTimeMinutes: terms.deliveryTimeMinutes || null,
        qualityGuarantee: terms.qualityGuarantee || null,
        refundPolicy: terms.refundPolicy || 'none',
        escrowRequired: terms.escrowRequired !== false, // Default true
        customTerms: terms.customTerms || [],
        ...terms
      },
      state: 'pending', // pending → accepted → rejected → countered → expired
      timeline: {
        created: now,
        responded: null,
        agreed: null,
        expired: now + (validForMinutes * 60 * 1000)
      },
      counterOffers: [],
      agreedPrice: null,
      escrowId: null,
      metadata: {}
    };

    this.negotiations[quoteId] = quote;
    this.saveState();

    return quote;
  }

  /**
   * Client accepts quote
   */
  accept(quoteId, clientId) {
    const quote = this.negotiations[quoteId];
    if (!quote) throw new Error('Quote not found');
    if (quote.clientId !== clientId) throw new Error('Not authorized');
    if (quote.state !== 'pending') throw new Error(`Cannot accept quote in state: ${quote.state}`);
    if (Date.now() > quote.timeline.expired) throw new Error('Quote expired');

    quote.state = 'accepted';
    quote.timeline.responded = Date.now();
    quote.timeline.agreed = Date.now();
    quote.agreedPrice = quote.price;

    // Create escrow if required
    if (quote.terms.escrowRequired && this.escrowSystem) {
      const escrow = this.escrowSystem.create({
        payer: clientId,
        payee: quote.providerId,
        amount: quote.agreedPrice,
        purpose: `Payment for: ${quote.service}`,
        conditions: {
          requiresApproval: true,
          requiresDelivery: true,
          requiresArbiter: quote.terms.requiresArbiter || false,
          requiresClientConfirmation: !quote.terms.autoRelease // Manual confirmation unless auto-release enabled
        },
        timeoutMinutes: quote.terms.deliveryTimeMinutes ? quote.terms.deliveryTimeMinutes + 30 : 120
      });

      quote.escrowId = escrow.id;
    }

    this.saveState();
    return quote;
  }

  /**
   * Client rejects quote
   */
  reject(quoteId, clientId, reason = null) {
    const quote = this.negotiations[quoteId];
    if (!quote) throw new Error('Quote not found');
    if (quote.clientId !== clientId) throw new Error('Not authorized');
    if (quote.state !== 'pending') throw new Error(`Cannot reject quote in state: ${quote.state}`);

    quote.state = 'rejected';
    quote.timeline.responded = Date.now();
    quote.metadata.rejectionReason = reason;

    this.saveState();
    return quote;
  }

  /**
   * Client makes counter-offer
   */
  counterOffer(quoteId, clientId, counterPrice, counterTerms = {}) {
    const quote = this.negotiations[quoteId];
    if (!quote) throw new Error('Quote not found');
    if (quote.clientId !== clientId) throw new Error('Not authorized');
    if (!['pending', 'countered'].includes(quote.state)) {
      throw new Error(`Cannot counter quote in state: ${quote.state}`);
    }
    if (Date.now() > quote.timeline.expired) throw new Error('Quote expired');

    quote.counterOffers.push({
      offeredBy: clientId,
      price: counterPrice,
      terms: counterTerms,
      timestamp: Date.now()
    });

    quote.state = 'countered';
    quote.timeline.responded = Date.now();

    this.saveState();
    return quote;
  }

  /**
   * Provider accepts counter-offer
   */
  acceptCounter(quoteId, providerId, counterIndex = -1) {
    const quote = this.negotiations[quoteId];
    if (!quote) throw new Error('Quote not found');
    if (quote.providerId !== providerId) throw new Error('Not authorized');
    if (quote.state !== 'countered') throw new Error('No counter-offer to accept');

    const counter = quote.counterOffers[counterIndex === -1 ? quote.counterOffers.length - 1 : counterIndex];
    if (!counter) throw new Error('Counter-offer not found');

    quote.state = 'accepted';
    quote.timeline.agreed = Date.now();
    quote.agreedPrice = counter.price;

    // Merge counter terms
    Object.assign(quote.terms, counter.terms);

    // Create escrow if required
    if (quote.terms.escrowRequired && this.escrowSystem) {
      const escrow = this.escrowSystem.create({
        payer: quote.clientId,
        payee: providerId,
        amount: quote.agreedPrice,
        purpose: `Payment for: ${quote.service}`,
        conditions: {
          requiresApproval: true,
          requiresDelivery: true,
          requiresArbiter: quote.terms.requiresArbiter || false,
          requiresClientConfirmation: !quote.terms.autoRelease
        },
        timeoutMinutes: quote.terms.deliveryTimeMinutes ? quote.terms.deliveryTimeMinutes + 30 : 120
      });

      quote.escrowId = escrow.id;
    }

    this.saveState();
    return quote;
  }

  /**
   * Mark service as delivered (triggers escrow release)
   */
  markDelivered(quoteId, providerId, deliveryProof = {}) {
    const quote = this.negotiations[quoteId];
    if (!quote) throw new Error('Quote not found');
    if (quote.providerId !== providerId) throw new Error('Not authorized');
    if (quote.state !== 'accepted') throw new Error('Quote not accepted');

    quote.metadata.delivered = {
      timestamp: Date.now(),
      proof: deliveryProof
    };

    // Submit delivery to escrow
    if (quote.escrowId && this.escrowSystem) {
      this.escrowSystem.submitDelivery(quote.escrowId, {
        submittedBy: providerId,
        data: deliveryProof
      });
    }

    this.saveState();
    return quote;
  }

  /**
   * Client confirms delivery (releases payment if not auto-released)
   */
  confirmDelivery(quoteId, clientId) {
    const quote = this.negotiations[quoteId];
    if (!quote) throw new Error('Quote not found');
    if (quote.clientId !== clientId) throw new Error('Not authorized');
    if (!quote.metadata.delivered) throw new Error('Service not marked as delivered');

    quote.metadata.confirmed = {
      timestamp: Date.now()
    };

    // Release escrow payment (if not already released)
    if (quote.escrowId && this.escrowSystem) {
      const escrowState = this.escrowSystem.get(quote.escrowId);
      if (escrowState && escrowState.state === 'locked') {
        this.escrowSystem.release(quote.escrowId, 'client confirmed delivery');
      }
      // If already released (auto-release), that's fine
    }

    this.saveState();
    return quote;
  }

  /**
   * Expire old quotes
   */
  processExpirations() {
    const now = Date.now();
    const expired = [];

    for (const [id, quote] of Object.entries(this.negotiations)) {
      if (quote.state === 'pending' && now > quote.timeline.expired) {
        quote.state = 'expired';
        expired.push(id);
      }
    }

    if (expired.length > 0) {
      this.saveState();
    }

    return expired;
  }

  /**
   * Get negotiation by ID
   */
  get(quoteId) {
    return this.negotiations[quoteId] || null;
  }

  /**
   * List negotiations with filters
   */
  list(filters = {}) {
    let results = Object.values(this.negotiations);

    if (filters.providerId) {
      results = results.filter(n => n.providerId === filters.providerId);
    }

    if (filters.clientId) {
      results = results.filter(n => n.clientId === filters.clientId);
    }

    if (filters.state) {
      results = results.filter(n => n.state === filters.state);
    }

    return results;
  }

  /**
   * Get negotiation stats
   */
  getStats() {
    const all = Object.values(this.negotiations);
    const byState = all.reduce((acc, n) => {
      acc[n.state] = (acc[n.state] || 0) + 1;
      return acc;
    }, {});

    const totalValue = all
      .filter(n => n.state === 'accepted')
      .reduce((sum, n) => sum + (n.agreedPrice || 0), 0);

    const avgNegotiationTime = all
      .filter(n => n.timeline.agreed)
      .map(n => n.timeline.agreed - n.timeline.created)
      .reduce((sum, t, _, arr) => sum + t / arr.length, 0);

    return {
      total: all.length,
      byState,
      totalValue,
      avgNegotiationTimeMs: avgNegotiationTime || 0,
      activeNegotiations: all.filter(n => ['pending', 'countered'].includes(n.state)).length
    };
  }
}

module.exports = { PaymentNegotiationSystem };
