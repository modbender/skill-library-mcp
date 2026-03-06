#!/usr/bin/env node
/**
 * Check wallet balance on Monad chain
 * 
 * Usage: node check-balance.js [wallet-name-or-address]
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

const NETWORKS = {
  'monad': {
    rpc: 'https://rpc.monad.xyz',
    chainId: 143,
    explorer: 'https://explorer.monad.xyz',
    nativeToken: 'MON'
  }
};

async function getAddress(input) {
  // If it looks like an address, use it directly
  if (input && input.startsWith('0x') && input.length === 42) {
    return input;
  }
  
  // Check environment variable first
  if (process.env.NAD_PRIVATE_KEY && !input) {
    const wallet = new ethers.Wallet(process.env.NAD_PRIVATE_KEY);
    console.log('🔑 Using wallet from NAD_PRIVATE_KEY environment variable');
    return wallet.address;
  }
  
  // Otherwise, try to load from wallet file
  const walletName = input || 'default';
  const walletsDir = process.env.NAD_WALLET_DIR || 
    path.join(process.env.HOME || '/tmp', '.nad-wallet', 'wallets');
  
  const filepath = path.join(walletsDir, `${walletName}.json`);
  
  if (!fs.existsSync(filepath)) {
    throw new Error(`Wallet not found: ${filepath}\n\nOptions:\n  1. Set NAD_PRIVATE_KEY environment variable\n  2. Create wallet: node scripts/create-wallet.js --managed ${walletName}`);
  }
  
  const data = JSON.parse(fs.readFileSync(filepath, 'utf8'));
  return data.address;
}

async function main() {
  const input = process.argv[2];
  const networkName = 'monad'; // Fixed to Monad
  
  try {
    const address = await getAddress(input);
    const network = NETWORKS[networkName];
    
    console.log('💰 Nad Wallet Balance Check');
    console.log('='.repeat(50));
    console.log('Address:', address);
    console.log('Network: Monad (Chain ID 143)');
    console.log('RPC:', network.rpc);
    
    console.log('\n⏳ Fetching balance...');
    
    const provider = new ethers.JsonRpcProvider(network.rpc);
    const balance = await provider.getBalance(address);
    
    const balanceMON = ethers.formatEther(balance);
    
    console.log('\n💎 Balance:', balanceMON, 'MON');
    console.log('Wei:', balance.toString());
    
    // Value estimation (if balance > 0)
    if (balance > 0) {
      console.log('\n📊 Balance Details:');
      if (parseFloat(balanceMON) >= 1) {
        console.log('  • Sufficient for transactions');
      } else if (parseFloat(balanceMON) >= 0.001) {
        console.log('  • Limited transaction capacity');
      } else {
        console.log('  • Very low balance - may need funding');
      }
    }
    
    console.log('\n🔗 Explorer:', `${network.explorer}/address/${address}`);
    
    // Show ecosystem links
    console.log('\n🌐 Nad Ecosystem:');
    console.log('  • nad.fun - Meme token platform');
    console.log('  • NadMail (nadmail.ai) - Web3 email');
    console.log('  • NadName (app.nad.domains) - Domain names');
    
    // Suggest next steps
    if (balance === 0n) {
      console.log('\n💡 Next Steps:');
      console.log('  • Get test MON from faucet');
      console.log('  • Bridge tokens from other chains');
      console.log('  • Register for NadMail: node scripts/nadmail-register.js --handle your-handle');
    }
    
  } catch (error) {
    console.error('\n❌ Error:', error.message);
    
    if (error.message.includes('Wallet not found')) {
      console.log('\n💡 Create a wallet first:');
      console.log('  node scripts/create-wallet.js --env');
      console.log('  # or');
      console.log('  node scripts/create-wallet.js --managed my-wallet');
    }
    
    process.exit(1);
  }
}

main().catch(console.error);