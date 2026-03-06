#!/usr/bin/env node

const { exec } = require('child_process');
const { promisify } = require('util');
const fs = require('fs').promises;
const execAsync = promisify(exec);

let isTestnet = true;
const networkFlag = isTestnet ? '--networkId testnet' : '';

/**
 * Create a subaccount
 */
async function createSubaccount(subaccountName, masterAccount) {
  const subaccountId = `${subaccountName}.${masterAccount}`;
  const cmd = `near create-account ${subaccountId} --masterAccount ${masterAccount} --initialBalance 0.1 ${networkFlag}`;

  try {
    await execAsync(cmd);
    return subaccountId;
  } catch (error) {
    throw new Error(`Failed to create subaccount: ${error.message}`);
  }
}

/**
 * List subaccounts using contract call
 */
async function listSubaccounts(accountId) {
  const cmd = `near view ${accountId} list_subaccounts ${networkFlag}`;

  try {
    const { stdout } = await execAsync(cmd);
    const result = JSON.parse(stdout);
    return result || [];
  } catch (error) {
    // If contract doesn't support list_subaccounts, return empty
    return [];
  }
}

/**
 * Delete a subaccount
 */
async function deleteSubaccount(subaccountId, masterAccount) {
  const cmd = `near delete-account ${subaccountId} --beneficiaryId ${masterAccount} ${networkFlag}`;

  try {
    await execAsync(cmd);
    return true;
  } catch (error) {
    throw new Error(`Failed to delete subaccount: ${error.message}`);
  }
}

/**
 * Bulk distribute NEAR to subaccounts
 */
async function bulkDistribute(filePath, amount = '0.1', masterAccount) {
  try {
    const data = await fs.readFile(filePath, 'utf8');
    const { subaccounts } = JSON.parse(data);

    if (!Array.isArray(subaccounts)) {
      throw new Error('Invalid JSON: subaccounts must be an array');
    }

    const results = [];
    for (const subaccountId of subaccounts) {
      try {
        const cmd = `near send ${masterAccount} ${subaccountId} ${amount} ${networkFlag}`;
        await execAsync(cmd);
        results.push({ account: subaccountId, status: 'success' });
        console.log(`✅ Sent ${amount} NEAR to ${subaccountId}`);
      } catch (error) {
        results.push({ account: subaccountId, status: 'failed', error: error.message });
        console.error(`❌ Failed to send to ${subaccountId}: ${error.message}`);
      }
    }

    return results;
  } catch (error) {
    throw new Error(`Bulk distribute failed: ${error.message}`);
  }
}

// CLI interface
const command = process.argv[2];
const arg1 = process.argv[3];
const arg2 = process.argv[4] || process.env.NEAR_ACCOUNT;

async function main() {
  try {
    switch (command) {
      case 'create':
        if (!arg1) {
          console.error('Error: Subaccount name required');
          console.error('Usage: near-subaccount create <name> [master_account]');
          process.exit(1);
        }
        if (!arg2) {
          console.error('Error: Master account required');
          console.error('Set NEAR_ACCOUNT env var or pass as argument');
          process.exit(1);
        }
        console.log(`Creating subaccount ${arg1}.${arg2}...`);
        const created = await createSubaccount(arg1, arg2);
        console.log(`✅ Created: ${created}`);
        break;

      case 'list':
        const accountToList = arg1 || process.env.NEAR_ACCOUNT;
        if (!accountToList) {
          console.error('Error: Account ID required');
          console.error('Set NEAR_ACCOUNT env var or pass as argument');
          process.exit(1);
        }
        console.log(`Listing subaccounts for ${accountToList}...`);
        const subaccounts = await listSubaccounts(accountToList);
        if (subaccounts.length === 0) {
          console.log('No subaccounts found');
        } else {
          console.log('Subaccounts:');
          subaccounts.forEach(sub => console.log(`  - ${sub}`));
        }
        break;

      case 'delete':
        if (!arg1) {
          console.error('Error: Subaccount ID required');
          console.error('Usage: near-subaccount delete <subaccount_id> [master_account]');
          process.exit(1);
        }
        if (!arg2) {
          console.error('Error: Master account required (for beneficiary)');
          process.exit(1);
        }
        console.log(`Deleting ${arg1}...`);
        await deleteSubaccount(arg1, arg2);
        console.log(`✅ Deleted: ${arg1}`);
        break;

      case 'distribute':
        if (!arg1) {
          console.error('Error: JSON file path required');
          console.error('Usage: near-subaccount distribute <file.json> [amount]');
          process.exit(1);
        }
        const amount = arg2 || '0.1';
        const masterAccount = process.env.NEAR_ACCOUNT;
        if (!masterAccount) {
          console.error('Error: Master account required (set NEAR_ACCOUNT)');
          process.exit(1);
        }
        await bulkDistribute(arg1, amount, masterAccount);
        break;

      default:
        console.log('NEAR Subaccount Manager');
        console.log('');
        console.log('Commands:');
        console.log('  create <name> [acc]   Create a subaccount');
        console.log('  list [account]         List subaccounts');
        console.log('  delete <id> [acc]      Delete a subaccount');
        console.log('  distribute <file> [amt] Bulk distribute NEAR');
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();
