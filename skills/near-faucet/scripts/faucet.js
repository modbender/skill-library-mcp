#!/usr/bin/env node

const https = require('https');

const FAUCET_API = 'https://wallet.testnet.near.org/api/faucet';

/**
 * Request testnet NEAR tokens from faucet
 */
async function requestTokens(accountId) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ account_id: accountId });

    const options = {
      hostname: 'wallet.testnet.near.org',
      port: 443,
      path: '/api/faucet',
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
 * Check account balance via RPC
 */
async function checkBalance(accountId) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      jsonrpc: '2.0',
      id: 'dontcare',
      method: 'query',
      params: {
        request_type: 'view_account',
        finality: 'final',
        account_id: accountId,
      },
    });

    const options = {
      hostname: 'rpc.testnet.near.org',
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
          const result = JSON.parse(body);
          if (result.error) {
            reject(new Error(result.error.message));
          } else {
            const balance = BigInt(result.result.amount);
            resolve(formatNear(balance));
          }
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

function formatNear(amount) {
  const yoctoToNear = 1e24;
  const near = Number(amount) / yoctoToNear;
  return near.toFixed(4);
}

// CLI interface
const command = process.argv[2];
const arg = process.argv[3];

async function main() {
  try {
    switch (command) {
      case 'request':
        if (!arg) {
          console.error('Error: Account ID required');
          console.error('Usage: near-faucet request <account_id>');
          process.exit(1);
        }
        console.log(`Requesting testnet NEAR for ${arg}...`);
        const result = await requestTokens(arg);
        if (result.error) {
          console.error(`Error: ${result.error}`);
          process.exit(1);
        }
        console.log('✅ Request submitted!');
        console.log(`Transaction hash: ${result.tx_hash || 'N/A'}`);
        console.log('Please wait 1-5 minutes for the tokens to arrive.');
        break;

      case 'balance':
        if (!arg) {
          console.error('Error: Account ID required');
          console.error('Usage: near-faucet balance <account_id>');
          process.exit(1);
        }
        const balance = await checkBalance(arg);
        console.log(`Balance for ${arg}: ${balance} NEAR`);
        break;

      default:
        console.log('NEAR Testnet Faucet');
        console.log('');
        console.log('Commands:');
        console.log('  request <account_id>  Request testnet tokens');
        console.log('  balance <account_id>  Check account balance');
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();
