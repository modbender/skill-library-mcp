#!/usr/bin/env node
/**
 * Orderly Network Deposit Tool
 * Deposits USDC to Orderly Vault on Base chain
 */

import { ethers } from 'ethers';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const CONFIG = {
  WALLET_FILE: '/Users/garysingh/clawd/.eth-wallet.txt',
  ORDERLY_KEYS_FILE: process.env.ORDERLY_KEYS_FILE || path.join(process.env.HOME || '', '.orderly-keys.json'),
  RPC_URL: 'https://mainnet.base.org',
  CHAIN_ID: 8453,
  BROKER_ID: 'hyper_claw',
  
  // Base mainnet addresses
  VAULT_ADDRESS: '0x816f722424b49cf1275cc86da9840fbd5a6167e9',
  USDC_ADDRESS: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'
};

// Vault ABI (only deposit function)
const VAULT_ABI = [
  'function deposit(tuple(bytes32 accountId, bytes32 brokerHash, bytes32 tokenHash, uint128 tokenAmount) depositData) external payable'
];

// ERC20 ABI (for approve)
const ERC20_ABI = [
  'function approve(address spender, uint256 amount) external returns (bool)',
  'function allowance(address owner, address spender) external view returns (uint256)',
  'function balanceOf(address account) external view returns (uint256)',
  'function decimals() external view returns (uint8)'
];

function loadPrivateKey() {
  const content = fs.readFileSync(CONFIG.WALLET_FILE, 'utf8');
  const match = content.match(/0x[a-fA-F0-9]{64}/);
  if (!match) throw new Error('Could not extract private key');
  return match[0];
}

function loadOrderlyKeys() {
  if (!fs.existsSync(CONFIG.ORDERLY_KEYS_FILE)) {
    throw new Error('Orderly keys not found. Run orderly-register.mjs first.');
  }
  return JSON.parse(fs.readFileSync(CONFIG.ORDERLY_KEYS_FILE, 'utf8'));
}

async function main() {
  const args = process.argv.slice(2);
  const amountUSDC = parseFloat(args[0]);
  
  if (!amountUSDC || amountUSDC <= 0) {
    console.log('Usage: node orderly-deposit.mjs <amount_usdc>');
    console.log('Example: node orderly-deposit.mjs 3.0');
    process.exit(1);
  }
  
  console.log(`\n🏦 Orderly Deposit Tool`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  
  // Load keys
  const privateKey = loadPrivateKey();
  const orderlyKeys = loadOrderlyKeys();
  
  console.log(`📍 Account ID: ${orderlyKeys.account_id.slice(0, 20)}...`);
  console.log(`📍 Broker: ${CONFIG.BROKER_ID}`);
  console.log(`💰 Amount: ${amountUSDC} USDC`);
  
  // Setup provider and wallet
  const provider = new ethers.JsonRpcProvider(CONFIG.RPC_URL);
  const wallet = new ethers.Wallet(privateKey, provider);
  
  console.log(`\n📍 Wallet: ${wallet.address}`);
  
  // Setup contracts
  const usdc = new ethers.Contract(CONFIG.USDC_ADDRESS, ERC20_ABI, wallet);
  const vault = new ethers.Contract(CONFIG.VAULT_ADDRESS, VAULT_ABI, wallet);
  
  // Check USDC balance
  const decimals = await usdc.decimals();
  const balance = await usdc.balanceOf(wallet.address);
  const balanceFormatted = ethers.formatUnits(balance, decimals);
  console.log(`💵 USDC Balance: ${balanceFormatted}`);
  
  const depositAmount = ethers.parseUnits(amountUSDC.toString(), decimals);
  
  if (balance < depositAmount) {
    console.error(`❌ Insufficient balance. Have ${balanceFormatted}, need ${amountUSDC}`);
    process.exit(1);
  }
  
  // Check and set allowance
  const currentAllowance = await usdc.allowance(wallet.address, CONFIG.VAULT_ADDRESS);
  console.log(`\n📋 Current allowance: ${ethers.formatUnits(currentAllowance, decimals)} USDC`);
  
  if (currentAllowance < depositAmount) {
    console.log(`⏳ Approving USDC spend...`);
    const approveTx = await usdc.approve(CONFIG.VAULT_ADDRESS, depositAmount);
    console.log(`📤 Approve TX: ${approveTx.hash}`);
    await approveTx.wait();
    console.log(`✅ Approved!`);
  } else {
    console.log(`✅ Allowance sufficient`);
  }
  
  // Prepare deposit data
  const brokerHash = ethers.keccak256(ethers.toUtf8Bytes(CONFIG.BROKER_ID));
  const tokenHash = ethers.keccak256(ethers.toUtf8Bytes('USDC'));
  
  const depositData = {
    accountId: orderlyKeys.account_id,
    brokerHash: brokerHash,
    tokenHash: tokenHash,
    tokenAmount: depositAmount
  };
  
  console.log(`\n📦 Deposit Data:`);
  console.log(`   accountId: ${depositData.accountId}`);
  console.log(`   brokerHash: ${brokerHash}`);
  console.log(`   tokenHash: ${tokenHash}`);
  console.log(`   tokenAmount: ${depositAmount.toString()}`);
  
  // Get deposit fee
  console.log(`\n💸 Getting deposit fee...`);
  
  // Try to get the deposit fee from the contract
  // Based on observed transactions, the fee is about 0.00000663 ETH
  const depositFee = ethers.parseEther('0.000007'); // Based on observed txs
  console.log(`   Deposit fee: ${ethers.formatEther(depositFee)} ETH`);
  
  // Check ETH balance for gas + fee
  const ethBalance = await provider.getBalance(wallet.address);
  console.log(`   ETH Balance: ${ethers.formatEther(ethBalance)} ETH`);
  
  // Estimate gas cost (deposit is ~100k gas, gas price ~0.01 gwei on Base)
  const estimatedGas = ethers.parseEther('0.00003'); // Conservative gas estimate
  if (ethBalance < depositFee + estimatedGas) {
    console.error(`❌ Insufficient ETH for gas + deposit fee (need ~${ethers.formatEther(depositFee + estimatedGas)} ETH)`);
    process.exit(1);
  }
  
  // Execute deposit with value
  console.log(`\n⏳ Executing deposit...`);
  try {
    const depositTx = await vault.deposit(depositData, { value: depositFee });
    console.log(`📤 Deposit TX: ${depositTx.hash}`);
    console.log(`🔗 https://basescan.org/tx/${depositTx.hash}`);
    
    const receipt = await depositTx.wait();
    console.log(`\n✅ DEPOSIT SUCCESSFUL!`);
    console.log(`   Block: ${receipt.blockNumber}`);
    console.log(`   Gas used: ${receipt.gasUsed.toString()}`);
    
    // Update orderly keys file with deposit info
    orderlyKeys.last_deposit = {
      amount_usdc: amountUSDC,
      tx_hash: depositTx.hash,
      timestamp: new Date().toISOString()
    };
    fs.writeFileSync(CONFIG.ORDERLY_KEYS_FILE, JSON.stringify(orderlyKeys, null, 2));
    
    console.log(`\n💡 Your funds should appear in Orderly within a few minutes.`);
    console.log(`   Check balance: curl -s "https://api-evm.orderly.org/v1/public/vault_balance?address=${wallet.address}" | jq`);
    
  } catch (error) {
    console.error(`\n❌ Deposit failed:`, error.message);
    if (error.data) {
      console.error(`   Error data:`, error.data);
    }
    process.exit(1);
  }
}

main().catch(console.error);
