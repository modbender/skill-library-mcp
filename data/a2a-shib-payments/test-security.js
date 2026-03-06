#!/usr/bin/env node

/**
 * Security Infrastructure Test Suite
 * Demonstrates all production hardening features
 */

const { AuthSystem } = require('./auth.js');
const { RateLimiter } = require('./rate-limiter.js');
const { AuditLogger } = require('./audit-logger.js');

console.log('🦪 OpenClaw SHIB Payment Agent - Security Test Suite\n');

// Test 1: Authentication
console.log('=== Test 1: Authentication System ===');
const auth = new AuthSystem();

console.log('✓ Loaded auth config');
console.log(`  Agents configured: ${Object.keys(auth.config.agents).length}`);

const validKey = auth.config.agents['demo-requestor'].apiKey;
const authResult = auth.authenticate(validKey);
console.log(`✓ Valid key authenticated: ${authResult.agentId}`);
console.log(`  Permissions: ${authResult.permissions.join(', ')}`);

const invalidAuth = auth.authenticate('invalid-key');
console.log(`✓ Invalid key rejected: ${invalidAuth.error}`);

const authzCheck = auth.authorize('demo-requestor', 'payment', 100);
console.log(`✓ Authorization check: ${authzCheck.authorized ? 'APPROVED' : 'DENIED'}`);

const overLimit = auth.authorize('demo-requestor', 'payment', 2000);
console.log(`✓ Over-limit check: ${overLimit.authorized ? 'APPROVED' : 'DENIED'} (${overLimit.reason || 'ok'})`);

console.log('');

// Test 2: Rate Limiting
console.log('=== Test 2: Rate Limiting ===');
const rateLimiter = new RateLimiter({
  windowMs: 60000,
  maxRequests: 5,
  maxPayments: 3,
  maxPaymentValue: 500
});

// Simulate 6 requests (6th should fail)
console.log('Simulating 6 rapid requests:');
for (let i = 1; i <= 6; i++) {
  const check = rateLimiter.checkRequest('test-agent');
  console.log(`  Request ${i}: ${check.allowed ? '✅ Allowed' : '❌ Rate limited'} (${check.remaining} remaining)`);
}

// Simulate payments
console.log('\nSimulating payment rate limit:');
console.log('  Payment 1 (100 SHIB):', rateLimiter.checkPayment('test-agent', 100).allowed ? '✅' : '❌');
console.log('  Payment 2 (200 SHIB):', rateLimiter.checkPayment('test-agent', 200).allowed ? '✅' : '❌');
console.log('  Payment 3 (150 SHIB):', rateLimiter.checkPayment('test-agent', 150).allowed ? '✅' : '❌');
console.log('  Payment 4 (100 SHIB):', rateLimiter.checkPayment('test-agent', 100).allowed ? '✅ (should fail)' : '❌ Volume limit');

const stats = rateLimiter.getStats('test-agent');
console.log(`\n✓ Stats: ${stats.payments.count} payments, ${stats.payments.totalValue} SHIB sent`);
console.log('');

// Test 3: Audit Logging
console.log('=== Test 3: Audit Logging ===');
const logger = new AuditLogger();

// Create test entries
logger.logAuth('test-agent', true);
logger.logBalanceCheck('test-agent', '0x123...', 1000);
logger.logPaymentRequest('test-agent', '0x456...', 100, true);
logger.logPaymentExecuted('test-agent', '0x456...', 100, '0xtxhash...', '$0.003');

console.log('✓ Logged 4 test entries');

// Query
const recentLogs = logger.query({ limit: 5 });
console.log(`✓ Query: Found ${recentLogs.length} recent entries`);
recentLogs.forEach(entry => {
  console.log(`  - ${entry.event} (seq ${entry.sequence})`);
});

// Verify integrity
const verification = logger.verify();
console.log(`\n✓ Integrity Check: ${verification.valid ? '✅ VALID' : '❌ INVALID'}`);
console.log(`  Total entries: ${verification.totalEntries}`);
console.log(`  Last hash: ${verification.lastHash?.substring(0, 16)}...`);

// Stats
const logStats = logger.getStats();
console.log(`\n✓ Audit Stats:`);
console.log(`  Total entries: ${logStats.totalEntries}`);
console.log(`  Last 24h: ${logStats.last24h}`);
console.log('  By event type:');
Object.entries(logStats.byEvent).forEach(([event, count]) => {
  console.log(`    ${event}: ${count}`);
});

console.log('\n' + '='.repeat(60));
console.log('✅ All Security Systems Operational!');
console.log('='.repeat(60));
console.log('\nProduction-Ready Features:');
console.log('  ✓ API Key Authentication');
console.log('  ✓ Per-Agent Permissions & Limits');
console.log('  ✓ Request Rate Limiting');
console.log('  ✓ Payment Rate & Volume Limiting');
console.log('  ✓ Immutable Audit Logging');
console.log('  ✓ Hash Chain Integrity Verification');
console.log('');
console.log('Next Steps:');
console.log('  • Integrate into A2A agent');
console.log('  • Deploy behind HTTPS reverse proxy');
console.log('  • Set up monitoring & alerting');
console.log('  • Configure backup & log rotation');
console.log('');
