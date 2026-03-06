#!/usr/bin/env node

const https = require('https');
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

const NAMING_CONTRACT = 'naming.near';
const TESTNET_RPC = 'https://rpc.testnet.near.org';
const MAINNET_RPC = 'https://rpc.mainnet.near.org';

let isTestnet = true;

/**
 * Query NEAR RPC
 */
async function queryRPC(method, params = {}) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      jsonrpc: '2.0',
      id: 'dontcare',
      method,
      params,
    });

    const rpc = isTestnet ? TESTNET_RPC : MAINNET_RPC;
    const url = new URL(rpc);

    const options = {
      hostname: url.hostname,
      port: 443,
      path: '/',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length,
      },
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          reject(new Error(`Failed to parse response: ${e.message}`));
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

/**
 * Check if a name is available
 */
async function checkAvailability(name) {
  const fullName = `${name}.near`;
  const result = await queryRPC('query', {
    request_type: 'view_account',
    finality: 'final',
    account_id: fullName,
  });

  if (result.result) {
    return false; // Account exists
  }
  if (result.error?.message?.includes('does not exist')) {
    return true; // Available
  }
  throw new Error(result.error?.message || 'Unknown error');
}

/**
 * Resolve a name to account ID
 */
async function resolveName(name) {
  const fullName = name.endsWith('.near') ? name : `${name}.near`;
  const result = await queryRPC('query', {
    request_type: 'view_account',
    finality: 'final',
    account_id: fullName,
  });

  if (result.result) {
    return fullName;
  }
  throw new Error(`Name ${fullName} does not exist`);
}

/**
 * Register a name using NEAR CLI
 */
async function registerName(name, accountId) {
  const fullName = `${name}.near`;
  const cmd = isTestnet
    ? `near call ${NAMING_CONTRACT} register '{"account_id":"${fullName}"}' --accountId ${accountId} --networkId testnet`
    : `near call ${NAMING_CONTRACT} register '{"account_id":"${fullName}"}' --accountId ${accountId}`;

  try {
    await execAsync(cmd);
    return true;
  } catch (error) {
    throw new Error(`Registration failed: ${error.message}`);
  }
}

/**
 * Call contract view method
 */
async function viewCall(contractId, method, args = {}) {
  const result = await queryRPC('query', {
    request_type: 'call_function',
    finality: 'final',
    account_id: contractId,
    method_name: method,
    args_base64: Buffer.from(JSON.stringify(args)).toString('base64'),
  });

  if (result.result && result.result.result) {
    return JSON.parse(Buffer.from(result.result.result, 'base64').toString());
  }
  throw new Error('View call failed');
}

// CLI interface
const command = process.argv[2];
const name = process.argv[3];
const accountId = process.argv[4] || process.env.NEAR_ACCOUNT;

async function main() {
  try {
    switch (command) {
      case 'check':
        if (!name) {
          console.error('Error: Name required');
          console.error('Usage: near-name check <name>');
          process.exit(1);
        }
        const available = await checkAvailability(name);
        if (available) {
          console.log(`✅ ${name}.near is available!`);
        } else {
          console.log(`❌ ${name}.near is already taken.`);
        }
        break;

      case 'resolve':
        if (!name) {
          console.error('Error: Name required');
          console.error('Usage: near-name resolve <name>');
          process.exit(1);
        }
        const resolved = await resolveName(name);
        console.log(`Resolved: ${resolved}`);
        break;

      case 'register':
        if (!name) {
          console.error('Error: Name required');
          console.error('Usage: near-name register <name> [account_id]');
          process.exit(1);
        }
        if (!accountId) {
          console.error('Error: Account ID required (set NEAR_ACCOUNT env var or pass as argument)');
          process.exit(1);
        }
        console.log(`Registering ${name}.near for ${accountId}...`);
        await registerName(name, accountId);
        console.log('✅ Registration successful!');
        break;

      default:
        console.log('NEAR Name Service');
        console.log('');
        console.log('Commands:');
        console.log('  check <name>          Check if a name is available');
        console.log('  resolve <name>        Resolve a name to account');
        console.log('  register <name> [acc] Register a name');
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();
