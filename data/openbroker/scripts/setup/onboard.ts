#!/usr/bin/env npx tsx
// Open Broker - Automated Onboarding
// Creates wallet, configures environment, and approves builder fee

import { generatePrivateKey, privateKeyToAccount } from 'viem/accounts';
import * as fs from 'fs';
import * as path from 'path';
import * as readline from 'readline';
import { homedir } from 'os';

const OPEN_BROKER_BUILDER_ADDRESS = '0xbb67021fA3e62ab4DA985bb5a55c5c1884381068';

// Global config directory: ~/.openbroker/
const CONFIG_DIR = path.join(homedir(), '.openbroker');
const CONFIG_PATH = path.join(CONFIG_DIR, '.env');

interface OnboardResult {
  success: boolean;
  walletAddress?: string;
  privateKey?: string;
  error?: string;
}

function createReadline(): readline.Interface {
  return readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
}

function prompt(rl: readline.Interface, question: string): Promise<string> {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer.trim());
    });
  });
}

function isValidPrivateKey(key: string): boolean {
  return /^0x[a-fA-F0-9]{64}$/.test(key);
}

function ensureConfigDir(): void {
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true, mode: 0o700 });
  }
}

async function main(): Promise<OnboardResult> {
  console.log('OpenBroker - One-Command Setup');
  console.log('==============================\n');
  console.log('This will: 1) Create wallet  2) Save config  3) Approve builder fee\n');

  // Check if config already exists
  if (fs.existsSync(CONFIG_PATH)) {
    console.log('⚠️  Config already exists!');
    console.log(`   Location: ${CONFIG_PATH}\n`);

    // Read existing config and show wallet address
    const envContent = fs.readFileSync(CONFIG_PATH, 'utf-8');
    const keyMatch = envContent.match(/HYPERLIQUID_PRIVATE_KEY=0x([a-fA-F0-9]{64})/);

    if (keyMatch) {
      const existingKey = `0x${keyMatch[1]}` as `0x${string}`;
      const account = privateKeyToAccount(existingKey);
      console.log('Current Configuration');
      console.log('---------------------');
      console.log(`Wallet Address: ${account.address}`);
      console.log(`Config File:    ${CONFIG_PATH}`);
      console.log(`\nTo reconfigure, delete the config file first:`);
      console.log(`  rm ${CONFIG_PATH}`);
      console.log(`\nTo fund this wallet, send USDC on Arbitrum, then deposit at:`);
      console.log(`  https://app.hyperliquid.xyz/`);

      return {
        success: true,
        walletAddress: account.address,
      };
    }

    return {
      success: false,
      error: 'Invalid config file - missing or malformed private key',
    };
  }

  // Ask user if they have an existing private key
  const rl = createReadline();

  console.log('Step 1/3: Wallet Setup');
  console.log('----------------------');
  console.log('Do you have an existing Hyperliquid private key?\n');
  console.log('  1) Yes, I have a private key ready');
  console.log('  2) No, generate a new wallet for me\n');

  let choice = '';
  while (choice !== '1' && choice !== '2') {
    choice = await prompt(rl, 'Enter choice (1 or 2): ');
    if (choice !== '1' && choice !== '2') {
      console.log('Please enter 1 or 2');
    }
  }

  let privateKey: `0x${string}`;

  if (choice === '1') {
    // User has existing key
    console.log('\nEnter your private key (0x... format):\n');

    let validKey = false;
    while (!validKey) {
      const inputKey = await prompt(rl, 'Private key: ');

      if (isValidPrivateKey(inputKey)) {
        privateKey = inputKey as `0x${string}`;
        validKey = true;
      } else {
        console.log('Invalid private key format. Must be 0x followed by 64 hex characters.');
        console.log('Example: 0x1234...abcd (66 characters total)\n');
      }
    }

    console.log('\n✅ Private key accepted');
  } else {
    // Generate new wallet
    console.log('\nGenerating new wallet...');
    privateKey = generatePrivateKey();
    console.log('✅ New wallet created');
  }

  rl.close();

  // Derive account from private key
  const account = privateKeyToAccount(privateKey);
  console.log(`\nWallet Address: ${account.address}\n`);

  // Create config directory and file
  console.log('Step 2/3: Creating config...');
  ensureConfigDir();

  const envContent = `# OpenBroker Configuration
# Location: ~/.openbroker/.env
# WARNING: Keep this file secret! Never share it!

# Your wallet private key
HYPERLIQUID_PRIVATE_KEY=${privateKey}

# Network: mainnet or testnet
HYPERLIQUID_NETWORK=mainnet

# Builder fee (supports openbroker development)
# Default: 1 bps (0.01%) on trades
BUILDER_ADDRESS=${OPEN_BROKER_BUILDER_ADDRESS}
BUILDER_FEE=10
`;

  fs.writeFileSync(CONFIG_PATH, envContent, { mode: 0o600 });
  console.log(`✅ Config saved to: ${CONFIG_PATH}\n`);

  // Approve builder fee (automatic - no user action needed)
  console.log('Step 3/3: Approving builder fee...');
  console.log('(This is automatic, and required for trading)\n');

  try {
    // Import and run approve-builder inline
    const { getClient } = await import('../core/client.js');
    const client = getClient();

    console.log(`   Account: ${client.address}`);
    console.log(`   Builder: ${OPEN_BROKER_BUILDER_ADDRESS}`);

    // Check if already approved
    const currentApproval = await client.getMaxBuilderFee(client.address, OPEN_BROKER_BUILDER_ADDRESS);

    if (currentApproval) {
      console.log(`\n✅ Builder fee already approved (${currentApproval})`);
    } else {
      console.log('\n   Sending approval transaction...');
      const result = await client.approveBuilderFee('0.1%', OPEN_BROKER_BUILDER_ADDRESS);

      if (result.status === 'ok') {
        console.log('✅ Builder fee approved successfully!');
      } else {
        console.log(`⚠️  Approval may have failed: ${result.response}`);
        console.log('   You can retry later: openbroker approve-builder');
      }
    }
  } catch (error) {
    console.log(`⚠️  Could not approve builder fee: ${error}`);
    console.log('   You can retry later: openbroker approve-builder');
  }

  // Final summary
  console.log('\n========================================');
  console.log('           SETUP COMPLETE!             ');
  console.log('========================================\n');

  console.log('Your Trading Wallet');
  console.log('-------------------');
  console.log(`Address: ${account.address}`);
  console.log(`Network: Hyperliquid (Mainnet)`);
  console.log(`Config:  ${CONFIG_PATH}`);

  if (choice === '2') {
    console.log('\n⚠️  IMPORTANT: Save your private key!');
    console.log('-----------------------------------');
    console.log(`Private Key: ${privateKey}`);
    console.log('\nThis key is stored in ~/.openbroker/.env');
    console.log('Back it up securely - if lost, funds cannot be recovered!');
  }

  console.log('\n📋 Next Steps');
  console.log('--------------');
  console.log('1. Fund your wallet with USDC on Arbitrum:');
  console.log(`   ${account.address}`);
  console.log('');
  console.log('2. Deposit USDC to Hyperliquid:');
  console.log('   https://app.hyperliquid.xyz/');
  console.log('');
  console.log('3. Start trading!');
  console.log('   openbroker account');
  console.log('   openbroker buy --coin ETH --size 0.01 --dry');

  console.log('\n⚠️  Security');
  console.log('------------');
  console.log(`Config stored at: ${CONFIG_PATH}`);
  console.log('Never share this file or your private key!');

  return {
    success: true,
    walletAddress: account.address,
    privateKey: privateKey,
  };
}

// Export for programmatic use
export { main as onboard };

// Run if executed directly
main().then(result => {
  if (!result.success) {
    console.error(`\nSetup failed: ${result.error}`);
    process.exit(1);
  }
}).catch(error => {
  console.error('Setup error:', error);
  process.exit(1);
});
