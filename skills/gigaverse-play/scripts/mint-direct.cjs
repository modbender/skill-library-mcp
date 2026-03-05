#!/usr/bin/env node
/**
 * Direct EOA mint - calls contract directly from EOA
 */

const { createPublicClient, createWalletClient, http, parseEther, encodeFunctionData } = require('viem');
const { privateKeyToAccount } = require('viem/accounts');
const { abstract } = require('viem/chains');
const { readFileSync } = require('fs');
const { join } = require('path');
const { homedir } = require('os');

// Config
const CHAIN = abstract;
const RPC_URL = 'https://api.mainnet.abs.xyz';
const ACCOUNT_SYSTEM = '0x5f8b7eb615D5FCE81fafFb107450EdE201384C00';

// ABI
const MINT_ABI = [{
  name: 'mintWithEth',
  type: 'function',
  inputs: [
    { name: '_username', type: 'string' },
    { name: 'signature', type: 'bytes' }
  ],
  outputs: [],
  stateMutability: 'payable'
}];

async function main() {
  const username = process.argv[2];
  if (!username) {
    console.error('Usage: node mint-direct.cjs <username>');
    process.exit(1);
  }

  // Load private key
  const keyPath = join(homedir(), '.secrets', 'gigaverse-private-key.txt');
  let privateKey = readFileSync(keyPath, 'utf8').trim();
  if (!privateKey.startsWith('0x')) privateKey = '0x' + privateKey;

  const account = privateKeyToAccount(privateKey);
  console.log('EOA Address:', account.address);

  // Load JWT
  const jwtPath = join(homedir(), '.secrets', 'gigaverse-jwt.txt');
  const jwt = readFileSync(jwtPath, 'utf8').trim();

  // Get mint signature for username
  console.log(`\nChecking username "${username}"...`);
  const sigResponse = await fetch(
    `https://gigaverse.io/api/indexer/usernameAvailable/${username}`,
    { headers: { Authorization: `Bearer ${jwt}` } }
  );

  if (!sigResponse.ok) {
    console.error('Failed to check username:', await sigResponse.text());
    process.exit(1);
  }

  const sigData = await sigResponse.json();
  if (!sigData.available) {
    console.error('Username not available');
    process.exit(1);
  }

  console.log('✅ Username available');
  console.log('Signature:', sigData.signature.slice(0, 20) + '...');

  // Create clients
  const publicClient = createPublicClient({
    chain: CHAIN,
    transport: http(RPC_URL),
  });

  const walletClient = createWalletClient({
    account,
    chain: CHAIN,
    transport: http(RPC_URL),
  });

  // Check balance
  const balance = await publicClient.getBalance({ address: account.address });
  console.log('\nEOA Balance:', Number(balance) / 1e18, 'ETH');

  const mintPrice = parseEther('0.005');
  if (balance < mintPrice) {
    console.error('❌ Insufficient balance for mint (need 0.005 ETH + gas)');
    process.exit(1);
  }

  // Encode function call
  const callData = encodeFunctionData({
    abi: MINT_ABI,
    functionName: 'mintWithEth',
    args: [username, sigData.signature]
  });

  console.log('\nSending transaction directly from EOA...');
  console.log('Contract:', ACCOUNT_SYSTEM);
  console.log('Function: mintWithEth');
  console.log('Username:', username);
  console.log('Value: 0.005 ETH');

  try {
    const hash = await walletClient.sendTransaction({
      to: ACCOUNT_SYSTEM,
      data: callData,
      value: mintPrice,
    });

    console.log('\n✅ Transaction sent:', hash);
    console.log('Explorer: https://abscan.org/tx/' + hash);

    console.log('\nWaiting for confirmation...');
    const receipt = await publicClient.waitForTransactionReceipt({ hash });
    
    if (receipt.status === 'success') {
      console.log('✅ Confirmed in block:', receipt.blockNumber);
      console.log('Gas used:', receipt.gasUsed.toString());
    } else {
      console.log('❌ Transaction reverted');
    }

  } catch (e) {
    console.error('\n❌ Transaction failed:', e.message);
    if (e.cause?.reason) console.error('Reason:', e.cause.reason);
    if (e.cause?.data) console.error('Data:', e.cause.data);
  }
}

main();
