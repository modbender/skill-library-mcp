#!/usr/bin/env node

/**
 * Fluora Setup Wizard (GitHub Version)
 * 
 * Automates:
 * 1. Clone fluora-mcp from GitHub
 * 2. Install dependencies & build
 * 3. Generate wallet
 * 4. Configure mcporter with local build
 * 5. Verify setup
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import readline from 'readline';
import { fileURLToPath } from 'url';
import os from 'os';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const FLUORA_REPO = 'https://github.com/fluora-ai/fluora-mcp.git';
const WORKSPACE_DIR = path.join(os.homedir(), '.openclaw', 'workspace');
const FLUORA_DIR = path.join(WORKSPACE_DIR, 'fluora-mcp');
const WALLET_PATH = path.join(os.homedir(), '.fluora', 'wallets.json');
const MCPORTER_WORKSPACE_CONFIG = path.join(WORKSPACE_DIR, 'config', 'mcporter.json');
const MCPORTER_HOME_CONFIG = path.join(os.homedir(), '.mcporter', 'mcporter.json');

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  cyan: '\x1b[36m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
};

function log(message, color = colors.reset) {
  console.error(`${color}${message}${colors.reset}`);
}

function section(title) {
  log(`\n${title}`, colors.bright);
}

function success(message) {
  log(`✓ ${message}`, colors.green);
}

function error(message) {
  log(`✗ ${message}`, colors.red);
}

function info(message) {
  log(message, colors.cyan);
}

function warn(message) {
  log(message, colors.yellow);
}

function header() {
  log('\n╔════════════════════════════════════════╗', colors.cyan);
  log('║    Fluora Setup Wizard (GitHub) 🔧    ║', colors.cyan);
  log('╚════════════════════════════════════════╝\n', colors.cyan);
}

async function prompt(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stderr,
  });

  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim().toLowerCase());
    });
  });
}

function execCommand(command, options = {}) {
  try {
    return execSync(command, { stdio: 'pipe', encoding: 'utf8', ...options });
  } catch (err) {
    throw new Error(`Command failed: ${command}\n${err.message}`);
  }
}

async function cloneFluoraMcp() {
  section('Step 1: Clone fluora-mcp from GitHub');
  
  if (fs.existsSync(FLUORA_DIR)) {
    warn(`  fluora-mcp directory already exists at ${FLUORA_DIR}`);
    const answer = await prompt('  Remove and re-clone? (y/n): ');
    
    if (answer === 'y' || answer === 'yes') {
      info('  Removing existing directory...');
      execCommand(`rm -rf "${FLUORA_DIR}"`);
    } else {
      success('Using existing fluora-mcp directory');
      return;
    }
  }

  info(`  Cloning from ${FLUORA_REPO}...`);
  execCommand(`git clone "${FLUORA_REPO}" "${FLUORA_DIR}"`);
  success('fluora-mcp cloned successfully');
}

async function installAndBuild() {
  section('Step 2: Install dependencies and build');
  
  info('  Running npm install...');
  execCommand('npm install', { cwd: FLUORA_DIR });
  success('Dependencies installed');

  info('  Building TypeScript...');
  execCommand('npm run build', { cwd: FLUORA_DIR });
  success('Build completed');

  // Verify build output
  const indexPath = path.join(FLUORA_DIR, 'build', 'index.js');
  if (!fs.existsSync(indexPath)) {
    throw new Error('Build failed: index.js not found');
  }
  success('Build verified');
}

async function generateWallet() {
  section('Step 3: Generate wallet');
  
  if (fs.existsSync(WALLET_PATH)) {
    success('Wallet file already exists');
    return;
  }

  info('  Starting fluora-mcp to generate wallet...');
  info('  (This will take a few seconds)');
  
  // Run fluora-mcp briefly to generate wallet, then kill it
  try {
    execCommand(`timeout 5 node build/index.js || true`, {
      cwd: FLUORA_DIR,
      stdio: 'ignore',
    });
  } catch (err) {
    // Timeout is expected
  }

  // Check if wallet was created
  if (fs.existsSync(WALLET_PATH)) {
    success('Wallet generated successfully');
  } else {
    error('Wallet generation failed');
    throw new Error('Could not generate wallet file');
  }
}

function getWalletInfo() {
  section('Step 4: Get wallet address');
  
  if (!fs.existsSync(WALLET_PATH)) {
    throw new Error('Wallet file not found');
  }

  const wallets = JSON.parse(fs.readFileSync(WALLET_PATH, 'utf8'));
  
  // Try to find mainnet wallet
  let walletAddress = null;
  let privateKey = null;

  if (wallets.BASE_MAINNET || wallets.USDC_BASE_MAINNET) {
    const wallet = wallets.BASE_MAINNET || wallets.USDC_BASE_MAINNET;
    privateKey = wallet.privateKey;
    walletAddress = wallet.address;
  }

  if (!walletAddress && privateKey) {
    // Derive address from private key using ethers
    try {
      const { Wallet } = await import('ethers');
      const wallet = new Wallet(privateKey);
      walletAddress = wallet.address;
    } catch (err) {
      warn('  Could not derive address from private key');
    }
  }

  if (!walletAddress) {
    throw new Error('Could not find wallet address in wallet file');
  }

  success(`Address: ${walletAddress}`);
  return { walletAddress, privateKey };
}

async function showFundingInstructions(walletAddress) {
  section('Step 5: Fund your wallet');
  
  log('\n═══════════════════════════════════════════', colors.bright);
  log('    💰 WALLET FUNDING REQUIRED', colors.bright);
  log('═══════════════════════════════════════════\n', colors.bright);
  
  info('Your Fluora Wallet Address:');
  success(walletAddress);
  log('');
  
  warn('To fund your wallet:');
  warn('1. Open Coinbase, Binance, or your preferred exchange');
  warn('2. Send $5-10 USDC to the address above');
  error('3. ⚠️  IMPORTANT: Select "Base" network (NOT Ethereum mainnet)');
  warn('4. Also send ~$0.50 ETH for gas fees');
  warn('5. Wait ~1 minute for confirmation');
  log('');
  
  info('Network Details:');
  info('  • Network: Base (Coinbase L2)');
  info('  • Tokens: USDC (services) + ETH (gas)');
  info('  • Gas fees: ~$0.01-0.03 per transaction');
  log('');
  
  info('Where to get tokens on Base:');
  info('  • Coinbase: Withdraw USDC + ETH → Select "Base" network');
  info('  • Bridge: https://bridge.base.org');
  info('  • Buy directly: Coinbase Wallet or Rainbow Wallet');
  log('');
  
  log('═══════════════════════════════════════════\n', colors.bright);
  
  const funded = await prompt('Have you funded the wallet? (y/n): ');
  return funded === 'y' || funded === 'yes';
}

function configureMcporter() {
  section('Step 6: Configure mcporter');
  
  info('\n⚙️  Configuring mcporter...');
  
  // Determine which config file to use
  let configPath = MCPORTER_WORKSPACE_CONFIG;
  if (!fs.existsSync(path.dirname(configPath))) {
    configPath = MCPORTER_HOME_CONFIG;
  }

  // Ensure config directory exists
  const configDir = path.dirname(configPath);
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }

  // Read or create config
  let config = { mcpServers: {}, imports: [] };
  if (fs.existsSync(configPath)) {
    try {
      config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    } catch (err) {
      warn(`  Could not parse existing config, creating new one`);
    }
  }

  // Add fluora-registry with local path
  const fluoraBuildPath = path.join(FLUORA_DIR, 'build', 'index.js');
  config.mcpServers['fluora-registry'] = {
    command: 'node',
    args: [fluoraBuildPath],
    env: {
      ENABLE_REQUEST_ELICITATION: 'true',
      ELICITATION_THRESHOLD: '0.01',
    },
  };

  // Write config
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
  success(`  Found config at: ${configPath}`);
  success('mcporter configured');
}

function verifySetup() {
  section('Step 7: Verify setup');
  
  info('\n🔍 Verifying setup...');
  
  // Check fluora-mcp directory
  if (fs.existsSync(FLUORA_DIR)) {
    success('  ✓ fluora-mcp directory exists');
  } else {
    error('  ✗ fluora-mcp directory not found');
    return false;
  }

  // Check build output
  const buildPath = path.join(FLUORA_DIR, 'build', 'index.js');
  if (fs.existsSync(buildPath)) {
    success('  ✓ Build output exists');
  } else {
    error('  ✗ Build output not found');
    return false;
  }

  // Check wallet file
  if (fs.existsSync(WALLET_PATH)) {
    success('  ✓ Wallet file exists');
  } else {
    error('  ✗ Wallet file not found');
    return false;
  }

  // Check wallet content
  try {
    const wallets = JSON.parse(fs.readFileSync(WALLET_PATH, 'utf8'));
    const hasWallet = wallets.BASE_MAINNET || wallets.USDC_BASE_MAINNET;
    if (hasWallet) {
      success('  ✓ Wallet configured');
    } else {
      error('  ✗ Wallet not configured');
      return false;
    }
  } catch (err) {
    error('  ✗ Invalid wallet file');
    return false;
  }

  return true;
}

function showNextSteps(walletAddress, funded) {
  log('\n✨ Setup complete!', colors.green);
  
  warn('\n📋 Next steps:');
  
  if (!funded) {
    warn('  1. Fund your wallet with $5-10 USDC + $0.50 ETH on Base');
    info(`     Address: ${walletAddress}`);
  }
  
  warn('  2. Test Fluora connection:');
  info('     cd ~/.openclaw/workspace');
  info('     mcporter call "fluora-registry.exploreServices()"');
  log('');
  
  warn('  3. Start building services:');
  info('     • workflow-to-monetized-mcp: Generate services');
  info('     • railway-deploy: Deploy to Railway');
  info('     • fluora-publish: List on marketplace');
  log('');
}

async function main() {
  try {
    header();
    
    // Step 1: Clone from GitHub
    await cloneFluoraMcp();
    
    // Step 2: Install and build
    await installAndBuild();
    
    // Step 3: Generate wallet
    await generateWallet();
    
    // Step 4: Get wallet info
    const { walletAddress } = getWalletInfo();
    
    // Step 5: Funding instructions
    const funded = await showFundingInstructions(walletAddress);
    
    // Step 6: Configure mcporter
    configureMcporter();
    
    // Step 7: Verify
    const verified = verifySetup();
    
    if (!verified) {
      throw new Error('Setup verification failed');
    }
    
    // Show next steps
    showNextSteps(walletAddress, funded);
    
    // Output result JSON
    const result = {
      success: true,
      walletAddress,
      privateKeyPath: WALLET_PATH,
      fluoraPath: FLUORA_DIR,
      mcporterConfigured: true,
      funded,
      balance: null,
      balanceSymbol: null,
    };
    
    console.log('\nSetup result:', result);
    
  } catch (err) {
    error(`\n❌ Setup failed: ${err.message}`);
    console.error(err.stack);
    process.exit(1);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { main as setupFluora };
