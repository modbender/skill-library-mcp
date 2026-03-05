#!/usr/bin/env node

const fs = require('fs').promises;
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

/**
 * Batch send NEAR tokens
 */
async function batchSend(senderAccount, recipients) {
  const results = [];
  console.log(`Batch sending from ${senderAccount}...`);
  console.log('');

  for (const recipient of recipients) {
    try {
      const cmd = `near send ${senderAccount} ${recipient.account} ${recipient.amount}`;
      await execAsync(cmd);
      results.push({ account: recipient.account, status: 'success', amount: recipient.amount });
      console.log(`✅ Sent ${recipient.amount} NEAR to ${recipient.account}`);
    } catch (error) {
      results.push({ account: recipient.account, status: 'failed', error: error.message });
      console.error(`❌ Failed to send to ${recipient.account}: ${error.message}`);
    }
  }

  console.log('');
  return results;
}

/**
 * Batch transfer NFTs
 */
async function batchNFT(senderAccount, transfers) {
  const results = [];
  console.log(`Batch transferring NFTs from ${senderAccount}...`);
  console.log('');

  for (const transfer of transfers) {
    try {
      const cmd = `near call ${transfer.contract} nft_transfer '{"receiver_id":"${transfer.receiver}","token_id":"${transfer.token_id}"}' --accountId ${senderAccount}`;
      await execAsync(cmd);
      results.push({ token_id: transfer.token_id, receiver: transfer.receiver, status: 'success' });
      console.log(`✅ Transferred NFT ${transfer.token_id} to ${transfer.receiver}`);
    } catch (error) {
      results.push({ token_id: transfer.token_id, receiver: transfer.receiver, status: 'failed', error: error.message });
      console.error(`❌ Failed to transfer ${transfer.token_id}: ${error.message}`);
    }
  }

  console.log('');
  return results;
}

/**
 * Estimate gas costs
 */
async function estimateCosts(senderAccount, operations, type) {
  console.log(`Estimating costs for ${type} operation...`);
  console.log('');

  let estimatedGas = 0;
  let estimatedGasPrice = 0.0000001; // ~0.1 yoctoNEAR per gas

  // Rough estimates
  if (type === 'send') {
    estimatedGas = operations.length * 30000000000000; // ~30 Tgas per send
  } else if (type === 'nft') {
    estimatedGas = operations.length * 35000000000000; // ~35 Tgas per NFT transfer
  }

  const yoctoToNear = 1e24;
  const costNear = (estimatedGas * estimatedGasPrice) / yoctoToNear;

  console.log(`Operations: ${operations.length}`);
  console.log(`Estimated Gas: ${estimatedGas.toLocaleString()}`);
  console.log(`Estimated Cost: ~${costNear.toFixed(6)} NEAR`);

  return {
    operations: operations.length,
    estimatedGas,
    estimatedCost: costNear
  };
}

// CLI interface
const command = process.argv[2];
const arg1 = process.argv[3];
const arg2 = process.argv[4];

async function main() {
  try {
    switch (command) {
      case 'send': {
        if (!arg1 || !arg2) {
          console.error('Error: Sender account and JSON file required');
          console.error('Usage: near-batch send <sender_account> <file.json>');
          process.exit(1);
        }
        const data = await fs.readFile(arg2, 'utf8');
        const { recipients } = JSON.parse(data);
        await batchSend(arg1, recipients);
        console.log('✅ Batch send complete!');
        break;
      }

      case 'nft': {
        if (!arg1 || !arg2) {
          console.error('Error: Sender account and JSON file required');
          console.error('Usage: near-batch nft <sender_account> <file.json>');
          process.exit(1);
        }
        const data = await fs.readFile(arg2, 'utf8');
        const { transfers } = JSON.parse(data);
        await batchNFT(arg1, transfers);
        console.log('✅ Batch NFT transfer complete!');
        break;
      }

      case 'estimate': {
        if (!arg1 || !arg2) {
          console.error('Error: Sender account and JSON file required');
          console.error('Usage: near-batch estimate <sender_account> <file.json> [type]');
          process.exit(1);
        }
        const data = await fs.readFile(arg2, 'utf8');
        const jsonData = JSON.parse(data);
        const type = process.argv[5] || 'send';
        const operations = type === 'send' ? jsonData.recipients : jsonData.transfers;
        await estimateCosts(arg1, operations, type);
        break;
      }

      case 'claim':
        console.log('Batch claim functionality requires integration with specific protocols');
        console.log('Implement based on the airdrop/claim protocol requirements');
        break;

      default:
        console.log('NEAR Batch Sender');
        console.log('');
        console.log('Commands:');
        console.log('  send <sender> <file>    Batch send NEAR');
        console.log('  nft <sender> <file>     Batch transfer NFTs');
        console.log('  estimate <sender> <file> [type]  Estimate costs');
        console.log('  claim <file>            Batch claim rewards');
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();
