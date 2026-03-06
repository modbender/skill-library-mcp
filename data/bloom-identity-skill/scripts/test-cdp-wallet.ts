/**
 * Test CDP Wallet Creation
 *
 * Diagnoses issues with CDP wallet creation
 */

import dotenv from 'dotenv';
import path from 'path';

// Explicitly load .env from project root (works with ts-node)
dotenv.config({ path: path.join(__dirname, '..', '.env') });

import { AgentWallet } from '../src/blockchain/agent-wallet';

async function testCDPWallet() {
  console.log('🧪 Testing CDP Wallet Creation\n');
  console.log('━'.repeat(60));

  // Step 1: Check environment variables
  console.log('\n📋 STEP 1: Environment Variables');
  console.log('━'.repeat(60));

  const cdpApiKeyId = process.env.CDP_API_KEY_ID;
  const cdpApiKeySecret = process.env.CDP_API_KEY_SECRET;
  const cdpWalletSecret = process.env.CDP_WALLET_SECRET;
  const network = process.env.NETWORK || 'base-mainnet';

  console.log(`CDP_API_KEY_ID: ${cdpApiKeyId ? '✅ SET (length: ' + cdpApiKeyId.length + ')' : '❌ NOT SET'}`);
  console.log(`CDP_API_KEY_SECRET: ${cdpApiKeySecret ? '✅ SET (length: ' + cdpApiKeySecret.length + ')' : '❌ NOT SET'}`);
  console.log(`CDP_WALLET_SECRET: ${cdpWalletSecret ? '✅ SET (length: ' + cdpWalletSecret.length + ')' : '❌ NOT SET'}`);
  console.log(`NETWORK: ${network}`);

  if (!cdpApiKeyId || !cdpApiKeySecret || !cdpWalletSecret) {
    console.error('\n❌ ERROR: CDP credentials are not set in .env file');
    console.error('\nPlease set the following in your .env file:');
    console.error('CDP_API_KEY_ID=your_api_key_id');
    console.error('CDP_API_KEY_SECRET=your_api_key_secret');
    console.error('CDP_WALLET_SECRET=your_wallet_secret');
    process.exit(1);
  }

  // Step 2: Test wallet creation
  console.log('\n\n🤖 STEP 2: Creating Agent Wallet');
  console.log('━'.repeat(60));

  try {
    const testUserId = `test-user-${Date.now()}`;
    console.log(`User ID: ${testUserId}`);
    console.log(`Network: ${network}`);

    const wallet = new AgentWallet({
      userId: testUserId,
      network: network as 'base-mainnet' | 'base-sepolia',
    });

    console.log('\n⏳ Initializing wallet (may take a few seconds)...');
    const walletInfo = await wallet.initialize();

    console.log('\n✅ Wallet Created Successfully!');
    console.log(`   Address: ${walletInfo.address}`);
    console.log(`   Network: ${walletInfo.network}`);
    console.log(`   X402 Endpoint: ${walletInfo.x402Endpoint || 'N/A'}`);

    // Step 3: Get wallet info
    console.log('\n\n📊 STEP 3: Wallet Information');
    console.log('━'.repeat(60));

    const info = await wallet.getWalletInfo();
    console.log(`Address: ${info.address}`);
    console.log(`Network: ${info.network}`);
    console.log(`X402 Endpoint: ${info.x402Endpoint || 'N/A'}`);
    console.log(`Balance: ${info.balance || 'N/A'}`);

    console.log('\n\n🎉 Test Complete!');
    console.log('━'.repeat(60));
    console.log('✅ CDP wallet creation is working correctly\n');

  } catch (error) {
    console.error('\n\n❌ STEP 2 FAILED: Wallet Creation Error');
    console.error('━'.repeat(60));

    if (error instanceof Error) {
      console.error(`Error: ${error.message}`);
      console.error(`\nStack trace:`);
      console.error(error.stack);

      // Provide helpful hints based on error message
      if (error.message.includes('timeout')) {
        console.error('\n💡 Hint: CDP API is taking too long to respond.');
        console.error('   - Check your internet connection');
        console.error('   - Verify CDP service status: https://status.coinbase.com/');
        console.error('   - Try again in a few moments');
      } else if (error.message.includes('unauthorized') || error.message.includes('invalid')) {
        console.error('\n💡 Hint: CDP credentials may be invalid.');
        console.error('   - Verify your CDP API keys are correct');
        console.error('   - Generate new keys at: https://portal.cdp.coinbase.com/');
        console.error('   - Ensure keys have proper permissions');
      } else if (error.message.includes('network')) {
        console.error('\n💡 Hint: Network configuration issue.');
        console.error('   - Check NETWORK environment variable');
        console.error('   - Valid values: base-mainnet, base-sepolia');
      } else {
        console.error('\n💡 Hint: Unknown error.');
        console.error('   - Check CDP SDK documentation: https://docs.cdp.coinbase.com/');
        console.error('   - Verify all environment variables are set correctly');
      }
    } else {
      console.error('Unknown error:', error);
    }

    process.exit(1);
  }
}

// Run test
testCDPWallet().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
