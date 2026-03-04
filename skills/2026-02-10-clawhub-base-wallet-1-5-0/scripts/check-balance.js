#!/usr/bin/env node
/**
 * Check wallet balance on Base chain
 * 
 * Usage: node check-balance.js [wallet-name-or-address]
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

const NETWORKS = {
  'base-mainnet': {
    rpc: 'https://mainnet.base.org',
    chainId: 8453,
    explorer: 'https://basescan.org'
  },
  'base-sepolia': {
    rpc: 'https://sepolia.base.org',
    chainId: 84532,
    explorer: 'https://sepolia.basescan.org'
  }
};

async function getAddress(input) {
  // If it looks like an address, use it directly
  if (input && input.startsWith('0x') && input.length === 42) {
    return input;
  }
  
  // Otherwise, try to load from wallet file
  const walletName = input || 'default';
  const walletsDir = process.env.WALLET_DIR || 
    path.join(process.env.HOME || '/tmp', '.openclaw', 'wallets');
  
  const filepath = path.join(walletsDir, `${walletName}.json`);
  
  if (!fs.existsSync(filepath)) {
    throw new Error(`Wallet not found: ${filepath}`);
  }
  
  const data = JSON.parse(fs.readFileSync(filepath, 'utf8'));
  return data.address;
}

async function main() {
  const input = process.argv[2];
  const networkName = process.argv[3] || 'base-mainnet';
  
  const address = await getAddress(input);
  const network = NETWORKS[networkName];
  
  if (!network) {
    console.error('Unknown network:', networkName);
    console.error('Available:', Object.keys(NETWORKS).join(', '));
    process.exit(1);
  }
  
  console.log('💰 Wallet Balance Check');
  console.log('='.repeat(50));
  console.log('Address:', address);
  console.log('Network:', networkName);
  
  const provider = new ethers.JsonRpcProvider(network.rpc);
  const balance = await provider.getBalance(address);
  
  console.log('\nBalance:', ethers.formatEther(balance), 'ETH');
  console.log('Wei:', balance.toString());
  console.log('\n🔗 Explorer:', `${network.explorer}/address/${address}`);
}

main().catch(console.error);
