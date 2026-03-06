#!/usr/bin/env node
/**
 * Upgrade Flow
 * Shows tier comparison and handles upgrade purchases
 */

import { getLicenseStatus } from './license.js';
import { generateStripeLink, generateCryptoPayment } from './payment.js';

// Display tier comparison table
function displayTierComparison() {
  console.log('\n' + '='.repeat(80));
  console.log('BOOKMARK INTELLIGENCE - SUBSCRIPTION TIERS');
  console.log('='.repeat(80));
  
  console.log('\n📦 FREE TIER');
  console.log('   Price: $0/month');
  console.log('   • 10 bookmarks per month');
  console.log('   • Manual run only (no automation)');
  console.log('   • Basic analysis (no LLM)');
  console.log('   • No notifications');
  
  console.log('\n⭐ PRO TIER - $9/month');
  console.log('   • Unlimited bookmarks');
  console.log('   • Automated monitoring');
  console.log('   • Full LLM analysis');
  console.log('   • Telegram notifications');
  
  console.log('\n🚀 ENTERPRISE TIER - $29/month');
  console.log('   • Everything in Pro, plus:');
  console.log('   • Team sharing');
  console.log('   • Custom AI models');
  console.log('   • API access');
  console.log('   • Slack & Discord integration');
  
  console.log('\n' + '='.repeat(80));
}

// Display current status
function displayCurrentStatus() {
  const status = getLicenseStatus();
  
  console.log('\n📊 YOUR CURRENT STATUS');
  console.log(`   Tier: ${status.tierName}`);
  console.log(`   Usage: ${status.usage.current}/${status.usage.limit} bookmarks this month`);
  console.log(`   Status: ${status.message}`);
  console.log('');
}

// Interactive upgrade flow
async function interactiveUpgrade() {
  displayTierComparison();
  displayCurrentStatus();
  
  console.log('To upgrade, run one of these commands:\n');
  console.log('Pro tier (Stripe):   npm run license:upgrade -- pro stripe monthly');
  console.log('Pro tier (Crypto):   npm run license:upgrade -- pro crypto monthly');
  console.log('Enterprise (Stripe): npm run license:upgrade -- enterprise stripe monthly\n');
}

// Process upgrade command
function processUpgrade(tier, method, period = 'monthly', email = null) {
  console.log(`\nProcessing upgrade to ${tier} (${period}) via ${method}...`);
  
  let result;
  
  if (method === 'stripe') {
    result = generateStripeLink(tier, period, email);
  } else if (method === 'crypto') {
    result = generateCryptoPayment(tier, period, email);
  } else {
    console.error('Invalid payment method. Use: stripe or crypto');
    process.exit(1);
  }
  
  if (!result.success) {
    console.error(`Error: ${result.error}`);
    process.exit(1);
  }
  
  // Display payment instructions
  if (method === 'stripe') {
    console.log('\n' + '='.repeat(80));
    console.log('STRIPE PAYMENT');
    console.log('='.repeat(80));
    console.log(`\nPayment ID: ${result.paymentId}`);
    console.log(`Amount: $${result.amount} ${result.currency}`);
    console.log(`Link: ${result.link}`);
    console.log(`\n${result.instructions}`);
    console.log('\nAfter payment, activate: node scripts/license.js activate <key>');
  } else {
    console.log('\n' + '='.repeat(80));
    console.log('CRYPTO PAYMENT');
    console.log('='.repeat(80));
    console.log(`\nPayment ID: ${result.paymentId}`);
    console.log(`\n${result.message}`);
    console.log(`\nNetwork: ${result.instructions.network}`);
    console.log(`Token: ${result.instructions.token}`);
    console.log(`Amount: ${result.instructions.amount}`);
    console.log(`Address: ${result.instructions.walletAddress}`);
    console.log(`Memo: ${result.instructions.memo} (required!)`);
    console.log('\nAfter sending, email support with payment ID');
  }
  
  console.log('\n' + '='.repeat(80));
  console.log('Save your Payment ID: ' + result.paymentId);
  console.log('');
}

// CLI interface
const args = process.argv.slice(2);

if (args.length === 0) {
  interactiveUpgrade();
} else {
  const tier = args[0];
  const method = args[1];
  const period = args[2] || 'monthly';
  const email = args[3] || null;
  
  if (!['pro', 'enterprise'].includes(tier)) {
    console.error('Invalid tier. Use: pro or enterprise');
    process.exit(1);
  }
  
  if (!['stripe', 'crypto'].includes(method)) {
    console.error('Invalid method. Use: stripe or crypto');
    process.exit(1);
  }
  
  processUpgrade(tier, method, period, email);
}
