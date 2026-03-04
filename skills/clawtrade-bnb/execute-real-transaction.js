#!/usr/bin/env node
/**
 * Execute Real Transaction
 * Makes an actual on-chain transaction to generate real TX hash
 */

const fs = require('fs');
const { ethers } = require('ethers');

// Load config and env
const config = JSON.parse(fs.readFileSync('./config.deployed.json', 'utf8'));
const env = {};
fs.readFileSync('.env', 'utf8').split('\n').forEach(line => {
  const [k, v] = line.split('=');
  if (k && v) env[k.trim()] = v.trim();
});

const PRIVATE_KEY = env.PRIVATE_KEY;
const RPC_URL = config.rpc;
const VAULT_ADDRESS = config.contracts[0].address; // vault_eth_staking_001

async function executeRealTransaction() {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║         Execute REAL Transaction on BNB Testnet             ║
╠════════════════════════════════════════════════════════════╣
║  Network: ${config.network}
║  RPC: ${RPC_URL}
║  Vault: ${config.contracts[0].name}
║  Address: ${VAULT_ADDRESS}
╚════════════════════════════════════════════════════════════╝
  `);

  try {
    const provider = new ethers.providers.JsonRpcProvider(RPC_URL);
    const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

    console.log(`\n🔌 Connected`);
    console.log(`   Wallet: ${wallet.address}`);

    // Get balance
    const balance = await provider.getBalance(wallet.address);
    const balanceBNB = parseFloat(ethers.utils.formatEther(balance));
    console.log(`   Balance: ${balanceBNB.toFixed(4)} BNB`);

    if (balanceBNB < 0.001) {
      console.error('❌ Insufficient BNB for gas (need at least 0.001 BNB)');
      process.exit(1);
    }

    // Create contract instance
    const vaultABI = config.abi;
    const vaultContract = new ethers.Contract(VAULT_ADDRESS, vaultABI, wallet);

    console.log(`\n📝 Preparing transaction...`);

    // Try to call a simple read function first (getVaultInfo)
    console.log(`   Reading vault info...`);
    const vaultInfo = await vaultContract.getVaultInfo();
    console.log(`   ✓ Vault is responsive`);

    // Now try compound() - which should work even with 0 yield
    console.log(`\n⚡ Executing compound() on vault...`);
    console.log(`   (This will generate a REAL tx hash on blockchain)`);

    const tx = await vaultContract.compound({
      gasLimit: 200000,
      gasPrice: ethers.utils.parseUnits('1', 'gwei'),
    });

    console.log(`\n✅ Transaction submitted!`);
    console.log(`   TX Hash: ${tx.hash}`);
    console.log(`   Block: Pending...`);

    // Wait for confirmation
    console.log(`\n⏳ Waiting for confirmation...`);
    const receipt = await tx.wait(1);

    console.log(`\n✅ TRANSACTION CONFIRMED!`);
    console.log(`   TX Hash: ${receipt.transactionHash}`);
    console.log(`   Block: ${receipt.blockNumber}`);
    console.log(`   Gas Used: ${receipt.gasUsed.toString()}`);
    console.log(`   Status: ${receipt.status === 1 ? 'SUCCESS' : 'FAILED'}`);

    // Verify on bscscan
    console.log(`\n🔍 Verify on BNB Testnet Scanner:`);
    console.log(`   https://testnet.bscscan.com/tx/${receipt.transactionHash}`);

    // Log to execution-log.jsonl
    const logEntry = {
      timestamp: Math.floor(Date.now() / 1000),
      action: 'REAL_TRANSACTION_EXECUTED',
      vault: config.contracts[0].vaultId,
      tx_hash: receipt.transactionHash,
      block: receipt.blockNumber,
      gas_used: receipt.gasUsed.toString(),
      status: receipt.status === 1 ? 'success' : 'failed',
      verified: 'REAL on-chain transaction',
      bscscan_link: `https://testnet.bscscan.com/tx/${receipt.transactionHash}`,
    };

    fs.appendFileSync('./execution-log.jsonl', JSON.stringify(logEntry) + '\n');
    console.log(`\n📋 Logged to execution-log.jsonl`);

    console.log(`\n${'═'.repeat(60)}`);
    console.log(`✅ REAL TRANSACTION COMPLETE`);
    console.log(`${'═'.repeat(60)}`);
    console.log(`\nThis TX hash is REAL and exists on BNB Testnet!`);
    console.log(`It will appear in the dashboard and can be verified on bscscan.\n`);

  } catch (error) {
    console.error('\n❌ Transaction failed:', error.message);
    console.error('\nDetails:', error);
    process.exit(1);
  }
}

executeRealTransaction().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
