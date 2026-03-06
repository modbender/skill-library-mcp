#!/usr/bin/env node
/**
 * 🌐 NNS Name Lookup Script
 * List all .nad names owned by an address
 * 
 * Usage: 
 *   node my-names.js [options]
 * 
 * Options:
 *   --address <addr>   Check specific address
 *   --managed          Use encrypted keystore address
 * 
 * If no address specified, uses:
 *   1. PRIVATE_KEY environment variable address
 *   2. ~/.nadname/wallet.json address (managed mode)
 * 
 * This is a read-only operation - no private key needed for custom addresses.
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

// Monad network configuration
const MONAD_RPC = 'https://rpc.monad.xyz';
const MONAD_CHAIN_ID = 143;
const NNS_CONTRACT = '0xE18a7550AA35895c87A1069d1B775Fa275Bc93Fb';

const CONFIG_DIR = path.join(process.env.HOME, '.nadname');
const WALLET_INFO_FILE = path.join(CONFIG_DIR, 'wallet.json');

function getArg(name) {
  const args = process.argv.slice(2);
  const idx = args.indexOf(name);
  if (idx !== -1 && args[idx + 1]) {
    return args[idx + 1];
  }
  return null;
}

function hasFlag(name) {
  return process.argv.includes(name);
}

function getWalletAddress() {
  const customAddress = getArg('--address');
  if (customAddress) {
    // Validate address format
    if (!ethers.isAddress(customAddress)) {
      console.error('❌ Invalid address format');
      process.exit(1);
    }
    return customAddress;
  }
  
  // Try to get from PRIVATE_KEY env var
  if (process.env.PRIVATE_KEY) {
    try {
      const wallet = new ethers.Wallet(process.env.PRIVATE_KEY.trim());
      return wallet.address;
    } catch (error) {
      console.error('❌ Invalid PRIVATE_KEY format');
      process.exit(1);
    }
  }
  
  // Try managed mode wallet info
  if (hasFlag('--managed') || fs.existsSync(WALLET_INFO_FILE)) {
    try {
      const walletInfo = JSON.parse(fs.readFileSync(WALLET_INFO_FILE, 'utf8'));
      if (walletInfo.address) {
        return walletInfo.address;
      }
    } catch (error) {
      console.error('❌ Could not read wallet info from managed keystore');
    }
  }
  
  console.error('❌ No address specified!');
  console.error('');
  console.error('Options:');
  console.error('1. node my-names.js --address 0x...');
  console.error('2. export PRIVATE_KEY="0x..." && node my-names.js');
  console.error('3. node my-names.js --managed');
  console.error('');
  process.exit(1);
}

async function lookupNames(provider, address) {
  console.log(`🔍 Looking up names for: ${address}`);
  console.log('');
  
  try {
    // In a real implementation, you'd query the NNS contract for names owned by this address
    // This would typically involve:
    // 1. Getting the contract instance with ABI
    // 2. Calling a view function like getNamesOwnedBy(address)
    // 3. Parsing the results to get name details
    
    // For now, we'll simulate some results
    console.log('🔄 Querying NNS contract...');
    console.log('⚠️  SIMULATION MODE - Using mock data');
    console.log('');
    
    // Mock data - replace with real contract calls
    const mockNames = [];
    
    // Simulate some owned names based on address
    const addressLower = address.toLowerCase();
    if (addressLower.includes('beef') || addressLower.includes('dead')) {
      mockNames.push({
        name: 'agent',
        isPrimary: true,
        registeredDate: '2026-02-08T10:30:00Z',
        expiryDate: null // Permanent
      });
      
      mockNames.push({
        name: '🦞',
        isPrimary: false,
        registeredDate: '2026-02-08T11:15:00Z',
        expiryDate: null
      });
    }
    
    if (mockNames.length === 0) {
      console.log('📭 No .nad names found for this address');
      console.log('');
      console.log('💡 To register a name:');
      console.log('   node scripts/check-name.js <name>');
      console.log('   node scripts/register-name.js --name <name>');
      return;
    }
    
    console.log(`📋 Found ${mockNames.length} name(s):`);
    console.log('');
    
    mockNames.forEach((nameInfo, index) => {
      console.log(`${index + 1}. ${nameInfo.name}.nad`);
      console.log(`   ${nameInfo.isPrimary ? '⭐ Primary name' : '   Regular name'}`);
      console.log(`   📅 Registered: ${new Date(nameInfo.registeredDate).toLocaleDateString()}`);
      console.log(`   ♾️  Expires: Never (permanent ownership)`);
      console.log('');
    });
    
    const primaryName = mockNames.find(n => n.isPrimary);
    if (primaryName) {
      console.log(`🎯 Primary name: ${primaryName.name}.nad`);
    } else {
      console.log('💡 No primary name set. Use --set-primary when registering.');
    }
    
    // TODO: Replace with real implementation
    /*
    const contract = new ethers.Contract(NNS_CONTRACT, nnsABI, provider);
    const ownedNames = await contract.getNamesOwnedBy(address);
    
    if (ownedNames.length === 0) {
      console.log('📭 No .nad names found for this address');
      return;
    }
    
    console.log(`📋 Found ${ownedNames.length} name(s):`);
    console.log('');
    
    for (let i = 0; i < ownedNames.length; i++) {
      const nameInfo = await contract.getNameInfo(ownedNames[i]);
      const isPrimary = await contract.getPrimaryName(address) === ownedNames[i];
      
      console.log(`${i + 1}. ${ownedNames[i]}.nad`);
      console.log(`   ${isPrimary ? '⭐ Primary name' : '   Regular name'}`);
      console.log(`   📅 Registered: ${new Date(nameInfo.registeredAt * 1000).toLocaleDateString()}`);
      console.log(`   ♾️  Expires: Never (permanent ownership)`);
      console.log('');
    }
    */
    
  } catch (error) {
    console.error('❌ Error querying names:', error.message);
    
    if (error.message.includes('revert')) {
      console.error('💡 Contract call failed - check if address has any names');
    } else if (error.message.includes('timeout')) {
      console.error('💡 Network timeout - try again later');
    }
    
    throw error;
  }
}

async function getAddressInfo(provider, address) {
  try {
    // Get basic address info
    const balance = await provider.getBalance(address);
    const txCount = await provider.getTransactionCount(address);
    
    console.log('📊 Address Information:');
    console.log(`   💰 Balance: ${ethers.formatEther(balance)} MON`);
    console.log(`   📤 Transactions: ${txCount}`);
    console.log('');
    
  } catch (error) {
    console.warn('⚠️  Could not fetch address info:', error.message);
  }
}

async function main() {
  try {
    console.log('🌐 NNS Name Lookup');
    console.log('═'.repeat(50));
    
    const address = getWalletAddress();
    
    console.log(`📍 Target address: ${address}`);
    console.log(`⛓️  Network: Monad (${MONAD_CHAIN_ID})`);
    console.log(`📍 Contract: ${NNS_CONTRACT}`);
    console.log('');
    
    // Connect to Monad
    const provider = new ethers.JsonRpcProvider(MONAD_RPC);
    
    // Verify network connection
    const network = await provider.getNetwork();
    console.log(`🔗 Connected to chain ID: ${network.chainId}`);
    console.log('');
    
    // Get address info
    await getAddressInfo(provider, address);
    
    // Look up names
    await lookupNames(provider, address);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    if (error.message.includes('network')) {
      console.error('💡 Check your internet connection and try again');
    } else if (error.message.includes('timeout')) {
      console.error('💡 Monad RPC might be slow, try again in a moment');
    }
    
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}