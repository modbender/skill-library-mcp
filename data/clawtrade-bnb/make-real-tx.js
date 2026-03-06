#!/usr/bin/env node
/**
 * Make REAL Transactions
 * Deposits tokens to vault and executes real TX
 */

const fs = require('fs');
const { ethers } = require('ethers');

// Load config
const config = JSON.parse(fs.readFileSync('./config.deployed.json', 'utf8'));
const env = {};
fs.readFileSync('.env', 'utf8').split('\n').forEach(line => {
  const [k, v] = line.split('=');
  if (k && v) env[k.trim()] = v.trim();
});

async function makeRealTransaction() {
  const RPC = config.rpc;
  const PRIVATE_KEY = env.PRIVATE_KEY;
  const VAULT_ADDRESS = config.contracts[0].address; // vault_eth_staking_001

  const provider = new ethers.providers.JsonRpcProvider(RPC);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
  const signer = wallet.connect(provider);

  console.log(`
╔════════════════════════════════════════════════════════════╗
║         MAKING REAL TRANSACTION ON BNB TESTNET             ║
╠════════════════════════════════════════════════════════════╣
║ Wallet: ${wallet.address}
║ Vault: ${VAULT_ADDRESS}
║ Network: ${config.network}
╚════════════════════════════════════════════════════════════╝
  `);

  try {
    // First: Get wallet balance
    const balance = await provider.getBalance(wallet.address);
    console.log(`\n💰 Wallet Balance: ${ethers.utils.formatEther(balance)} BNB`);

    if (balance.lt(ethers.utils.parseEther('0.01'))) {
      console.log('❌ Not enough BNB (need > 0.01)');
      process.exit(1);
    }

    // Second: Call compound() on vault (REAL TX)
    const vaultABI = config.abi;
    const vault = new ethers.Contract(VAULT_ADDRESS, vaultABI, signer);

    console.log('\n🔄 Calling compound() on vault...');
    const tx = await vault.compound({ gasLimit: 300000 });
    
    console.log(`📝 Transaction submitted: ${tx.hash}`);
    console.log(`   URL: https://testnet.bscscan.com/tx/${tx.hash}`);

    // Wait for confirmation
    console.log('\n⏳ Waiting for confirmation...');
    const receipt = await tx.wait(1);

    console.log(`\n✅ TRANSACTION CONFIRMED`);
    console.log(`   Block: ${receipt.blockNumber}`);
    console.log(`   Gas Used: ${receipt.gasUsed.toString()}`);
    console.log(`   Status: ${receipt.status === 1 ? 'SUCCESS' : 'FAILED'}`);
    console.log(`\n🔗 View on BNB Testnet Scanner:`);
    console.log(`   https://testnet.bscscan.com/tx/${tx.hash}`);

    // Save to log
    const logEntry = {
      timestamp: Math.floor(Date.now() / 1000),
      action: 'REAL_COMPOUND',
      vault: 'vault_eth_staking_001',
      tx_hash: tx.hash,
      block: receipt.blockNumber,
      gas_used: receipt.gasUsed.toString(),
      status: 'success',
    };
    fs.appendFileSync('./execution-log.jsonl', JSON.stringify(logEntry) + '\n');

    console.log(`\n✅ Logged to execution-log.jsonl`);
    console.log(`\n📊 Check dashboard: https://15e7e68f3bcacc.lhr.life`);

  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

makeRealTransaction();
