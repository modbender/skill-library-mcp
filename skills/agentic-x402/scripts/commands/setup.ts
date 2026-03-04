#!/usr/bin/env npx tsx
// x402 Agent Skill - Wallet Setup
// Creates a new wallet or configures an existing one

import { generatePrivateKey, privateKeyToAccount } from 'viem/accounts';
import * as fs from 'fs';
import * as path from 'path';
import * as readline from 'readline';
import { homedir } from 'os';

// Global config directory: ~/.x402/
const CONFIG_DIR = path.join(homedir(), '.x402');
const CONFIG_PATH = path.join(CONFIG_DIR, '.env');

interface SetupResult {
  success: boolean;
  walletAddress?: string;
  privateKey?: string;
  isNewWallet?: boolean;
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

function backupExistingConfig(): string | null {
  if (!fs.existsSync(CONFIG_PATH)) {
    return null;
  }

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const backupPath = path.join(CONFIG_DIR, `.env.backup.${timestamp}`);

  fs.copyFileSync(CONFIG_PATH, backupPath);
  fs.chmodSync(backupPath, 0o600);

  return backupPath;
}

async function main(): Promise<SetupResult> {
  console.log('x402 Agent Skill - Wallet Setup');
  console.log('================================\n');

  // Check if config already exists
  if (fs.existsSync(CONFIG_PATH)) {
    console.log('Existing config found!');
    console.log(`Location: ${CONFIG_PATH}\n`);

    // Read existing config and show wallet address
    const envContent = fs.readFileSync(CONFIG_PATH, 'utf-8');
    const keyMatch = envContent.match(/EVM_PRIVATE_KEY=0x([a-fA-F0-9]{64})/);

    if (keyMatch) {
      const existingKey = `0x${keyMatch[1]}` as `0x${string}`;
      const account = privateKeyToAccount(existingKey);

      console.log('Current Configuration');
      console.log('---------------------');
      console.log(`Wallet Address: ${account.address}`);
      console.log(`Config File:    ${CONFIG_PATH}`);

      const rl = createReadline();
      console.log('\nOptions:');
      console.log('  1) Keep existing config (exit)');
      console.log('  2) Create new wallet (backs up existing config)\n');

      let choice = '';
      while (choice !== '1' && choice !== '2') {
        choice = await prompt(rl, 'Enter choice (1 or 2): ');
        if (choice !== '1' && choice !== '2') {
          console.log('Please enter 1 or 2');
        }
      }

      if (choice === '1') {
        rl.close();
        console.log('\nKeeping existing config.');
        console.log(`\nTo check your balance:`);
        console.log(`  x402 balance`);

        return {
          success: true,
          walletAddress: account.address,
        };
      }

      // User wants to reconfigure - backup first
      rl.close();
      const backupPath = backupExistingConfig();
      console.log(`\nExisting config backed up to:`);
      console.log(`  ${backupPath}`);
      console.log('');

      // Continue with setup flow below...
    } else {
      // Config exists but is invalid - back it up and continue
      const backupPath = backupExistingConfig();
      console.log('Invalid config file found (missing private key).');
      console.log(`Backed up to: ${backupPath}\n`);
    }
  }

  const rl = createReadline();

  // Step 1: Wallet choice
  console.log('Step 1/2: Wallet Setup');
  console.log('----------------------');
  console.log('Do you have an existing wallet private key?\n');
  console.log('  1) Generate a NEW wallet (Recommended for agents)');
  console.log('  2) Use an EXISTING private key\n');

  let choice = '';
  while (choice !== '1' && choice !== '2') {
    choice = await prompt(rl, 'Enter choice (1 or 2): ');
    if (choice !== '1' && choice !== '2') {
      console.log('Please enter 1 or 2');
    }
  }

  let privateKey: `0x${string}`;
  let isNewWallet = false;

  if (choice === '1') {
    // Generate new wallet (recommended)
    console.log('\nGenerating new wallet...');
    privateKey = generatePrivateKey();
    isNewWallet = true;
    console.log('New wallet created!\n');
  } else {
    // User wants to use existing key - show warnings
    console.log('\n' + '='.repeat(60));
    console.log('                    SECURITY WARNING');
    console.log('='.repeat(60));
    console.log('\nUsing your main wallet with automated agents is RISKY:');
    console.log('');
    console.log('  - Agents can sign transactions without your approval');
    console.log('  - A bug or misconfiguration could drain funds');
    console.log('  - Private keys stored in env files can be exposed');
    console.log('');
    console.log('RECOMMENDED: Use a DEDICATED wallet with limited funds.');
    console.log('Only transfer what you need for payments to this wallet.');
    console.log('='.repeat(60) + '\n');

    const confirm = await prompt(rl, 'I understand the risks (type "yes" to continue): ');

    if (confirm.toLowerCase() !== 'yes') {
      console.log('\nSetup cancelled. Run "x402 setup" again to generate a new wallet.');
      rl.close();
      return { success: false, error: 'User cancelled setup' };
    }

    console.log('\nEnter your private key (0x... format):\n');

    // Loop until we get a valid key
    let inputKey = '';
    while (!isValidPrivateKey(inputKey)) {
      inputKey = await prompt(rl, 'Private key: ');

      if (!isValidPrivateKey(inputKey)) {
        console.log('Invalid private key format. Must be 0x followed by 64 hex characters.');
        console.log('Example: 0x1234...abcd (66 characters total)\n');
      }
    }

    privateKey = inputKey as `0x${string}`;
    console.log('\nPrivate key accepted');
  }

  rl.close();

  // Derive account from private key
  const account = privateKeyToAccount(privateKey);
  console.log(`Wallet Address: ${account.address}\n`);

  // Step 2: Create config
  console.log('Step 2/2: Saving configuration...');
  ensureConfigDir();

  const envContent = `# x402 Agent Skill Configuration
# Location: ~/.x402/.env
# Created: ${new Date().toISOString()}
#
# WARNING: Keep this file secret! Never share your private key!
# This wallet can sign payment transactions automatically.

# Your wallet private key (required)
EVM_PRIVATE_KEY=${privateKey}

# Network: mainnet or testnet
# mainnet = Base (chain 8453) - real USDC
# testnet = Base Sepolia (chain 84532) - test tokens
X402_NETWORK=mainnet

# Maximum payment limit in USD (safety feature)
# Payments exceeding this will be rejected
X402_MAX_PAYMENT_USD=10

# Verbose logging (0 = off, 1 = on)
X402_VERBOSE=0
`;

  fs.writeFileSync(CONFIG_PATH, envContent, { mode: 0o600 });
  console.log(`Config saved to: ${CONFIG_PATH}\n`);

  // Final summary
  console.log('='.repeat(50));
  console.log('           SETUP COMPLETE!');
  console.log('='.repeat(50) + '\n');

  console.log('Your x402 Payment Wallet');
  console.log('------------------------');
  console.log(`Address: ${account.address}`);
  console.log(`Network: Base Mainnet (chain 8453)`);
  console.log(`Config:  ${CONFIG_PATH}`);

  if (isNewWallet) {
    console.log('\n' + '!'.repeat(50));
    console.log('       BACKUP YOUR PRIVATE KEY NOW!');
    console.log('!'.repeat(50));
    console.log('\nYour private key (save this securely):');
    console.log(`\n  ${privateKey}\n`);
    console.log('Store this in a password manager or secure location.');
    console.log('If lost, your funds CANNOT be recovered!');
    console.log('!'.repeat(50));
  }

  console.log('\nNext Steps');
  console.log('----------');
  console.log('1. Fund your wallet with USDC on Base:');
  console.log(`   Address: ${account.address}`);
  console.log('');
  console.log('2. Add a small amount of ETH for gas (optional):');
  console.log('   ~0.001 ETH is enough for many transactions');
  console.log('');
  console.log('3. Check your balance:');
  console.log('   x402 balance');
  console.log('');
  console.log('4. Try paying for an x402 resource:');
  console.log('   x402 pay https://some-x402-api.com/endpoint');

  console.log('\nBackup Reminder');
  console.log('---------------');
  console.log(`Your config is stored at: ${CONFIG_PATH}`);
  console.log('Back up this file or your private key securely!');
  console.log('Consider using a password manager like 1Password or Bitwarden.');

  console.log('\nSecurity Tips');
  console.log('-------------');
  console.log('- Only fund this wallet with what you need');
  console.log('- Set X402_MAX_PAYMENT_USD to limit exposure');
  console.log('- Never share your private key or config file');
  console.log('- Use testnet first to verify everything works');

  return {
    success: true,
    walletAddress: account.address,
    privateKey: privateKey,
    isNewWallet,
  };
}

// Export for programmatic use
export { main as setup };

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
