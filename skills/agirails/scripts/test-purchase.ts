/**
 * AGIRAILS Test Purchase Script
 * 
 * Tests a simple payment flow on testnet.
 * 
 * Usage:
 *   PROVIDER_ADDRESS=0x... npx ts-node test-purchase.ts
 * 
 * Requires:
 *   - .actp/keystore.json OR ACTP_PRIVATE_KEY env var
 *   - PROVIDER_ADDRESS env var (or pass as argument)
 *   - @agirails/sdk installed
 */

import { ACTPClient } from '@agirails/sdk';
import { ethers } from 'ethers';

async function main() {
  console.log('🧪 AGIRAILS Test Purchase\n');

  const provider = process.env.PROVIDER_ADDRESS || process.argv[2];
  const mode = (process.env.AGIRAILS_MODE as 'mock' | 'testnet' | 'mainnet') || 'testnet';

  if (!provider) {
    console.error('❌ PROVIDER_ADDRESS not set');
    console.error('   Set via env var or pass as argument');
    process.exit(1);
  }

  console.log(`Mode: ${mode}`);
  console.log(`Provider: ${provider}`);
  console.log('');

  if (mode === 'mainnet') {
    console.log('⚠️  WARNING: Running on MAINNET with real money!');
    console.log('    Press Ctrl+C within 5 seconds to cancel...\n');
    await sleep(5000);
  }

  try {
    // SDK auto-detects wallet: .actp/keystore.json → ACTP_PRIVATE_KEY → PRIVATE_KEY
    const client = await ACTPClient.create({ mode });
    const address = await client.getAddress();
    console.log(`Requester: ${address}`);

    // Check balance first
    const balance = await client.getBalance(address);
    const formattedBalance = ethers.formatUnits(balance, 6);
    console.log(`💰 Current balance: $${formattedBalance}`);

    if (parseFloat(formattedBalance) < 2) {
      console.error('❌ Insufficient balance for test (need at least $2)');
      process.exit(1);
    }

    // Create test transaction
    console.log('\n📝 Creating transaction...');
    const txId = await client.standard.createTransaction({
      provider,
      amount: '1',  // $1 test
      deadline: Math.floor(Date.now() / 1000) + 3600,  // 1 hour
      disputeWindow: 300,  // 5 min for testing
      serviceDescription: 'Test purchase - AGIRAILS integration test',
    });
    console.log(`   Transaction ID: ${txId}`);
    console.log('   State: INITIATED');

    // Lock escrow
    console.log('\n🔒 Locking escrow...');
    const escrowId = await client.standard.linkEscrow(txId);
    console.log(`   Escrow ID: ${escrowId}`);
    console.log('   State: COMMITTED');

    // Check status
    console.log('\n📊 Transaction status:');
    const status = await client.basic.checkStatus(txId);
    console.log(`   State: ${status.state}`);
    console.log(`   Amount: $1 USDC`);

    // New balance
    const newBalance = await client.getBalance(address);
    const newFormatted = ethers.formatUnits(newBalance, 6);
    console.log(`\n💰 New balance: $${newFormatted}`);
    console.log(`   Locked in escrow: $1.00`);

    console.log('\n✅ Test purchase successful!');
    console.log('\nNext steps:');
    console.log('1. Provider should transition to QUOTED, then IN_PROGRESS, then DELIVERED');
    console.log('2. After delivery, call releaseEscrow() to pay provider');
    console.log('3. Or call transitionState(txId, "CANCELLED") to cancel and refund');

    console.log(`\nTransaction ID for reference: ${txId}`);

  } catch (error: any) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

main();
