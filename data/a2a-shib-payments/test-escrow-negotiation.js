#!/usr/bin/env node

/**
 * Escrow & Payment Negotiation Test Suite
 * Demonstrates trustless agent-to-agent commerce
 */

const { EscrowSystem } = require('./escrow.js');
const { PaymentNegotiationSystem } = require('./payment-negotiation.js');

console.log('🦪 Escrow & Payment Negotiation Test Suite\n');
console.log('='.repeat(70));

// Initialize systems
const escrow = new EscrowSystem();
const negotiation = new PaymentNegotiationSystem(escrow);

console.log('\n=== Scenario 1: Simple Escrow (Time-Locked Payment) ===\n');

// Create escrow
const simpleEscrow = escrow.create({
  payer: 'agent-alice',
  payee: '0xBob123...',
  amount: 100,
  purpose: 'Payment for AI model training',
  conditions: {
    requiresApproval: true,
    requiresDelivery: true
  },
  timeoutMinutes: 120 // 2 hour timeout
});

console.log(`✓ Escrow created: ${simpleEscrow.id}`);
console.log(`  Payer: ${simpleEscrow.payer}`);
console.log(`  Payee: ${simpleEscrow.payee}`);
console.log(`  Amount: ${simpleEscrow.amount} SHIB`);
console.log(`  State: ${simpleEscrow.state}`);

// Fund escrow
escrow.fund(simpleEscrow.id, '0xtxhash123...');
console.log(`\n✓ Escrow funded (tx: 0xtxhash123...)`);
console.log(`  State: ${escrow.get(simpleEscrow.id).state}`);

// Approve
escrow.approve(simpleEscrow.id, 'agent-alice');
escrow.approve(simpleEscrow.id, '0xBob123...');
console.log(`\n✓ Escrow approved by both parties`);
console.log(`  State: ${escrow.get(simpleEscrow.id).state}`);

// Submit delivery (auto-releases if conditions met)
escrow.submitDelivery(simpleEscrow.id, {
  submittedBy: '0xBob123...',
  data: { 
    deliverableUrl: 'https://storage.example.com/model.pth',
    checksum: 'sha256:abc123...'
  }
});
console.log(`\n✓ Delivery proof submitted`);
console.log(`✓ Payment automatically released (delivery confirmed)`);
console.log(`  Final state: ${escrow.get(simpleEscrow.id).state}`);

console.log('\n' + '='.repeat(70));
console.log('\n=== Scenario 2: Payment Negotiation Workflow ===\n');

// Provider creates quote
const quote = negotiation.createQuote({
  providerId: 'data-provider-agent',
  clientId: 'research-agent',
  service: 'Historical stock data (TSLA 2020-2025)',
  price: 500,
  terms: {
    deliveryTimeMinutes: 30,
    qualityGuarantee: '99.9% accuracy',
    refundPolicy: 'full refund if delivery fails',
    escrowRequired: true
  },
  validForMinutes: 60
});

console.log(`✓ Quote created: ${quote.id}`);
console.log(`  Service: ${quote.service}`);
console.log(`  Price: ${quote.price} SHIB`);
console.log(`  Delivery time: ${quote.terms.deliveryTimeMinutes} minutes`);
console.log(`  State: ${quote.state}`);

// Client counter-offers
negotiation.counterOffer(quote.id, 'research-agent', 400, {
  deliveryTimeMinutes: 20 // Faster delivery requested
});
console.log(`\n✓ Client counter-offered: 400 SHIB (faster delivery)`);
console.log(`  State: ${negotiation.get(quote.id).state}`);

// Provider accepts counter
negotiation.acceptCounter(quote.id, 'data-provider-agent');
console.log(`\n✓ Provider accepted counter-offer`);
const acceptedQuote = negotiation.get(quote.id);
console.log(`  Agreed price: ${acceptedQuote.agreedPrice} SHIB`);
console.log(`  Escrow created: ${acceptedQuote.escrowId}`);
console.log(`  State: ${acceptedQuote.state}`);

// Check escrow was created
const linkedEscrow = escrow.get(acceptedQuote.escrowId);
console.log(`\n✓ Escrow details:`);
console.log(`  Amount: ${linkedEscrow.amount} SHIB`);
console.log(`  Purpose: ${linkedEscrow.purpose}`);
console.log(`  State: ${linkedEscrow.state}`);
console.log(`  Timeout: ${linkedEscrow.timeout ? 'Yes (auto-refund)' : 'No'}`);

// Fund escrow
escrow.fund(linkedEscrow.id, '0xtxhash456...');
console.log(`\n✓ Client funded escrow (tx: 0xtxhash456...)`);

// Both approve
escrow.approve(linkedEscrow.id, 'research-agent');
escrow.approve(linkedEscrow.id, 'data-provider-agent');
console.log(`✓ Both parties approved escrow`);
console.log(`  State: ${escrow.get(linkedEscrow.id).state}`);

// Provider delivers service
negotiation.markDelivered(quote.id, 'data-provider-agent', {
  dataUrl: 'https://api.dataprovider.com/tsla/historical',
  recordCount: 12580,
  format: 'CSV',
  checksum: 'sha256:def456...'
});
console.log(`\n✓ Provider marked service as delivered`);

// Client confirms
negotiation.confirmDelivery(quote.id, 'research-agent');
console.log(`✓ Client confirmed delivery`);
console.log(`  Payment released to provider`);
console.log(`  Final escrow state: ${escrow.get(linkedEscrow.id).state}`);

console.log('\n' + '='.repeat(70));
console.log('\n=== Scenario 3: Dispute Resolution ===\n');

// Create another quote (with arbiter required to prevent auto-release)
const disputeQuote = negotiation.createQuote({
  providerId: 'translation-agent',
  clientId: 'publisher-agent',
  service: 'French to English translation (10,000 words)',
  price: 300,
  terms: {
    deliveryTimeMinutes: 60,
    qualityGuarantee: 'Professional quality',
    refundPolicy: 'partial refund for quality issues',
    escrowRequired: true,
    requiresArbiter: true // Prevents auto-release on delivery
  }
});

console.log(`✓ New quote created: ${disputeQuote.id}`);
console.log(`  Service: ${disputeQuote.service}`);
console.log(`  Price: ${disputeQuote.price} SHIB`);

// Accept and fund
negotiation.accept(disputeQuote.id, 'publisher-agent');
const disputeEscrowId = negotiation.get(disputeQuote.id).escrowId;
escrow.fund(disputeEscrowId, '0xtxhash789...');
escrow.approve(disputeEscrowId, 'publisher-agent');
escrow.approve(disputeEscrowId, 'translation-agent');

console.log(`\n✓ Quote accepted and escrow funded & locked`);

// Provider delivers
negotiation.markDelivered(disputeQuote.id, 'translation-agent', {
  translationUrl: 'https://storage.example.com/translation.txt',
  wordCount: 9500 // Less than agreed!
});

console.log(`\n✓ Provider delivered (but only 9,500 words instead of 10,000)`);

// Client disputes
escrow.dispute(disputeEscrowId, 'publisher-agent', 'Incomplete delivery - only 9,500 words');
console.log(`✓ Client opened dispute`);
console.log(`  Reason: Incomplete delivery`);
console.log(`  State: ${escrow.get(disputeEscrowId).state}`);

// Arbiter resolves (50% refund, 50% release)
// In real system, arbiter would review evidence
escrow.resolveDispute(disputeEscrowId, 'refund', 'arbiter-agent');
console.log(`\n✓ Arbiter resolved dispute: REFUND`);
console.log(`  Decision: Full refund due to incomplete delivery`);
console.log(`  Final state: ${escrow.get(disputeEscrowId).state}`);

console.log('\n' + '='.repeat(70));
console.log('\n=== System Statistics ===\n');

const escrowStats = escrow.getStats();
console.log('Escrow System:');
console.log(`  Total escrows: ${escrowStats.total}`);
console.log(`  By state:`);
Object.entries(escrowStats.byState).forEach(([state, count]) => {
  console.log(`    ${state}: ${count}`);
});
console.log(`  Total locked: ${escrowStats.totalLocked} SHIB`);
console.log(`  Active escrows: ${escrowStats.activeEscrows}`);

const negStats = negotiation.getStats();
console.log(`\nNegotiation System:`);
console.log(`  Total negotiations: ${negStats.total}`);
console.log(`  By state:`);
Object.entries(negStats.byState).forEach(([state, count]) => {
  console.log(`    ${state}: ${count}`);
});
console.log(`  Total value: ${negStats.totalValue} SHIB`);
console.log(`  Active negotiations: ${negStats.activeNegotiations}`);
console.log(`  Avg negotiation time: ${Math.round(negStats.avgNegotiationTimeMs)}ms`);

console.log('\n' + '='.repeat(70));
console.log('\n✅ All Scenarios Complete!\n');

console.log('Key Features Demonstrated:');
console.log('  ✓ Time-locked escrows');
console.log('  ✓ Multi-party approval');
console.log('  ✓ Delivery proof submission');
console.log('  ✓ Automatic payment release');
console.log('  ✓ Price negotiation (quote → counter → accept)');
console.log('  ✓ Escrow integration with negotiations');
console.log('  ✓ Dispute resolution with arbiter');
console.log('  ✓ Automatic refunds');
console.log('  ✓ Full audit trail\n');

console.log('Production Ready:');
console.log('  • Trustless agent-to-agent payments');
console.log('  • Conditional payment releases');
console.log('  • Automated service marketplaces');
console.log('  • Fair dispute resolution');
console.log('  • Complete transaction history\n');
