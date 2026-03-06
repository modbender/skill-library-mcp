#!/usr/bin/env node
/**
 * 🦞 Basename Auto-Register
 * 
 * Fully automated Basename registration on Base chain.
 * Handles browser automation + WalletConnect signing.
 * 
 * Usage:
 *   node register-basename.js <name> [options]
 * 
 * Options:
 *   --years <n>           Registration years (default: 1)
 *   --dry-run             Check availability only, don't register
 * 
 * Environment Variables (REQUIRED for registration):
 *   PRIVATE_KEY           Wallet private key
 *   WC_PROJECT_ID         WalletConnect Project ID (optional)
 * 
 * Example:
 *   export PRIVATE_KEY="0x..."
 *   node register-basename.js littl3lobst3r
 * 
 * ⚠️ SECURITY: Never pass private key as command line argument!
 */

const { Core } = require('@walletconnect/core');
const { Web3Wallet } = require('@walletconnect/web3wallet');
const { ethers } = require('ethers');
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const BASE_CHAIN_ID = 8453;
const BASE_RPC = 'https://mainnet.base.org';
const BASENAMES_URL = 'https://www.base.org/names';
const DEFAULT_PROJECT_ID = '3a8170812b534d0ff9d794f19a901d64';

// Audit log
const AUDIT_DIR = path.join(process.env.HOME, '.basename-agent');
const AUDIT_FILE = path.join(AUDIT_DIR, 'audit.log');

function logAudit(action, details = {}) {
  try {
    if (!fs.existsSync(AUDIT_DIR)) {
      fs.mkdirSync(AUDIT_DIR, { recursive: true, mode: 0o700 });
    }
    const entry = {
      timestamp: new Date().toISOString(),
      action,
      name: details.name,
      wallet: details.wallet ? `${details.wallet.slice(0, 6)}...${details.wallet.slice(-4)}` : null,
      txHash: details.txHash,
      success: details.success ?? true,
      error: details.error,
    };
    fs.appendFileSync(AUDIT_FILE, JSON.stringify(entry) + '\n', { mode: 0o600 });
  } catch (e) {}
}

function parseArgs() {
  const args = process.argv.slice(2);
  const config = {
    name: null,
    years: 1,
    dryRun: false,
    projectId: process.env.WC_PROJECT_ID || DEFAULT_PROJECT_ID,
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    // Check for dangerous --private-key usage
    if (arg === '--private-key' || arg === '-p') {
      console.error('');
      console.error('⛔ SECURITY ERROR: Do not pass private key as command line argument!');
      console.error('');
      console.error('   Command line arguments are logged in shell history.');
      console.error('');
      console.error('✅ Use environment variable instead:');
      console.error('   export PRIVATE_KEY="0x..."');
      console.error('   node register-basename.js yourname');
      console.error('');
      process.exit(1);
    }
    
    if (!arg.startsWith('-') && !config.name) {
      config.name = arg.toLowerCase().replace(/\.base\.eth$/, '');
    } else if (arg === '--years' && args[i + 1]) {
      config.years = parseInt(args[++i]);
    } else if (arg === '--dry-run') {
      config.dryRun = true;
    }
  }

  return config;
}

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
  const config = parseArgs();
  const privateKey = process.env.PRIVATE_KEY;

  if (!config.name) {
    console.log('🦞 Basename Auto-Register');
    console.log('═'.repeat(50));
    console.log('');
    console.log('Usage: node register-basename.js <name> [options]');
    console.log('');
    console.log('Options:');
    console.log('  --years <n>    Registration years (default: 1)');
    console.log('  --dry-run      Check availability only');
    console.log('');
    console.log('Environment Variables:');
    console.log('  PRIVATE_KEY    Wallet private key (REQUIRED)');
    console.log('');
    console.log('Example:');
    console.log('  export PRIVATE_KEY="0x..."');
    console.log('  node register-basename.js littl3lobst3r');
    console.log('');
    console.log('⚠️  SECURITY: Never pass private key as command line argument!');
    process.exit(1);
  }

  if (!privateKey && !config.dryRun) {
    console.error('');
    console.error('❌ Error: PRIVATE_KEY environment variable not set');
    console.error('');
    console.error('Set it like this:');
    console.error('  export PRIVATE_KEY="0x..."');
    console.error('  node register-basename.js ' + config.name);
    console.error('');
    console.error('Or use --dry-run to check availability:');
    console.error('  node register-basename.js ' + config.name + ' --dry-run');
    console.error('');
    console.error('⚠️  SECURITY: Never pass private key as command line argument!');
    process.exit(1);
  }

  console.log('🦞 Basename Auto-Register');
  console.log('═'.repeat(50));
  console.log(`📝 Name: ${config.name}.base.eth`);
  console.log(`📅 Years: ${config.years}`);
  console.log(`🔍 Mode: ${config.dryRun ? 'Dry run (check only)' : 'Register'}`);

  // Initialize wallet if not dry run
  let wallet, address;
  if (!config.dryRun) {
    const provider = new ethers.JsonRpcProvider(BASE_RPC);
    wallet = new ethers.Wallet(privateKey, provider);
    address = wallet.address;
    console.log(`📍 Wallet: ${address}`);
    
    const balance = await provider.getBalance(address);
    console.log(`💰 Balance: ${ethers.formatEther(balance)} ETH`);
    
    logAudit('registration_start', { name: config.name, wallet: address });
  }

  // Launch browser
  console.log('\n🌐 Launching browser...');
  const browser = await puppeteer.launch({
    headless: false,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  try {
    // Navigate to Basenames
    console.log('📡 Loading Basenames...');
    await page.goto(BASENAMES_URL, { waitUntil: 'networkidle2' });
    await sleep(2000);

    // Search for name
    console.log(`🔍 Searching for "${config.name}"...`);
    const searchInput = await page.waitForSelector('input[placeholder*="Search"]');
    await searchInput.type(config.name);
    await sleep(2000);

    // Check availability
    const pageContent = await page.content();
    if (pageContent.includes('Available')) {
      console.log('✅ Name is available!');
    } else if (pageContent.includes('Registered') || pageContent.includes('Taken')) {
      console.log('❌ Name is already taken!');
      logAudit('name_taken', { name: config.name, success: false });
      await browser.close();
      process.exit(1);
    } else {
      console.log('⚠️ Could not determine availability');
    }

    if (config.dryRun) {
      console.log('\n🔍 Dry run complete - name is available!');
      await browser.close();
      process.exit(0);
    }

    // Click on the name to go to registration page
    const nameButton = await page.$(`button:has-text("${config.name}.base.eth")`);
    if (nameButton) {
      await nameButton.click();
    } else {
      await page.click('[class*="Available"] button, button:has-text(".base.eth")');
    }
    await sleep(2000);

    // Click Connect Wallet
    console.log('🔗 Connecting wallet...');
    const connectButton = await page.waitForSelector('button:has-text("Connect wallet")');
    await connectButton.click();
    await sleep(1000);

    // Select WalletConnect
    const wcButton = await page.waitForSelector('button:has-text("WalletConnect")');
    await wcButton.click();
    await sleep(2000);

    // Get WalletConnect URI
    console.log('📋 Getting WalletConnect URI...');
    
    try {
      const openButton = await page.$('button:has-text("開啟"), button:has-text("Open")');
      if (openButton) await openButton.click();
      await sleep(1000);
    } catch (e) {}

    const copyButton = await page.$('button[aria-label*="Copy"], button:has(img[alt*="copy"]), [class*="copy"]');
    if (copyButton) {
      await copyButton.click();
      await sleep(500);
    }

    let wcUri;
    try {
      wcUri = await page.evaluate(() => navigator.clipboard.readText());
    } catch (e) {
      wcUri = await page.evaluate(() => {
        const qrImg = document.querySelector('img[alt*="QR"]');
        if (qrImg && qrImg.src.includes('wc:')) {
          return decodeURIComponent(qrImg.src.split('data=')[1]);
        }
        return null;
      });
    }

    if (!wcUri || !wcUri.startsWith('wc:')) {
      console.error('❌ Could not get WalletConnect URI');
      console.log('💡 Tip: Manually copy the URI and use wc-connect.js instead');
      logAudit('uri_failed', { name: config.name, wallet: address, success: false });
      await browser.close();
      process.exit(1);
    }

    console.log('✅ Got WalletConnect URI');

    // Initialize WalletConnect
    console.log('\n📡 Initializing WalletConnect...');
    const core = new Core({ projectId: config.projectId });
    const web3wallet = await Web3Wallet.init({
      core,
      metadata: {
        name: 'AI Agent Wallet',
        description: 'Autonomous Basename Registration',
        url: 'https://clawd.bot',
        icons: ['https://clawd.bot/logo.png'],
      },
    });

    let sessionEstablished = false;
    let registrationComplete = false;
    let txHash = null;

    // Handle session proposals
    web3wallet.on('session_proposal', async (proposal) => {
      console.log('✅ Session proposal from:', proposal.params.proposer.metadata.name);
      
      const namespaces = {
        eip155: {
          accounts: [`eip155:${BASE_CHAIN_ID}:${address}`],
          methods: [
            'eth_sendTransaction',
            'eth_signTransaction',
            'personal_sign',
            'eth_signTypedData',
            'eth_signTypedData_v4',
            // Note: eth_sign intentionally excluded (security risk)
          ],
          events: ['chainChanged', 'accountsChanged'],
          chains: [`eip155:${BASE_CHAIN_ID}`],
        },
      };

      await web3wallet.approveSession({ id: proposal.id, namespaces });
      console.log('✅ Session approved!');
      sessionEstablished = true;
    });

    // Handle signing requests
    web3wallet.on('session_request', async (event) => {
      const { topic, params, id } = event;
      const { request } = params;
      
      console.log(`\n📝 ${request.method} request received`);

      try {
        let result;

        switch (request.method) {
          case 'personal_sign': {
            const [message] = request.params;
            if (ethers.isHexString(message)) {
              result = await wallet.signMessage(ethers.getBytes(message));
            } else {
              result = await wallet.signMessage(message);
            }
            console.log('✅ Message signed');
            break;
          }

          case 'eth_signTypedData':
          case 'eth_signTypedData_v4': {
            const [, data] = request.params;
            const typedData = typeof data === 'string' ? JSON.parse(data) : data;
            const { domain, types, message } = typedData;
            delete types.EIP712Domain;
            result = await wallet.signTypedData(domain, types, message);
            console.log('✅ Typed data signed');
            break;
          }

          case 'eth_sendTransaction': {
            const [tx] = request.params;
            console.log(`   To: ${tx.to}`);
            console.log(`   Value: ${tx.value || '0'} wei`);

            const txResponse = await wallet.sendTransaction({
              to: tx.to,
              value: tx.value || '0x0',
              data: tx.data || '0x',
              gasLimit: tx.gas || tx.gasLimit,
            });

            console.log(`✅ TX sent: ${txResponse.hash}`);
            result = txResponse.hash;
            txHash = txResponse.hash;
            registrationComplete = true;
            break;
          }

          default:
            throw new Error(`Unsupported: ${request.method}`);
        }

        await web3wallet.respondSessionRequest({
          topic,
          response: { id, jsonrpc: '2.0', result },
        });

      } catch (error) {
        console.error('❌ Error:', error.message);
        await web3wallet.respondSessionRequest({
          topic,
          response: {
            id,
            jsonrpc: '2.0',
            error: { code: 5000, message: error.message },
          },
        });
      }
    });

    // Connect
    await web3wallet.pair({ uri: wcUri });
    console.log('⏳ Waiting for session...');

    // Wait for session
    while (!sessionEstablished) {
      await sleep(500);
    }

    // Click Register button
    await sleep(2000);
    console.log('\n📝 Clicking Register...');
    const registerButton = await page.waitForSelector('button:has-text("Register")');
    await registerButton.click();

    // Wait for registration
    console.log('⏳ Waiting for transaction...');
    while (!registrationComplete) {
      await sleep(1000);
    }

    // Wait for confirmation
    await sleep(5000);
    
    // Check for success
    const finalContent = await page.content();
    if (finalContent.includes('Congrats') || finalContent.includes('yours')) {
      console.log('\n' + '═'.repeat(50));
      console.log('🎉 SUCCESS! Registered: ' + config.name + '.base.eth');
      console.log('═'.repeat(50));
      console.log(`\n🔗 Profile: https://base.org/name/${config.name}`);
      
      logAudit('registration_success', { 
        name: config.name, 
        wallet: address, 
        txHash,
        success: true 
      });
    }

    await sleep(3000);
    await browser.close();

  } catch (error) {
    console.error('❌ Error:', error.message);
    logAudit('registration_error', { 
      name: config.name, 
      wallet: address, 
      error: error.message,
      success: false 
    });
    await browser.close();
    process.exit(1);
  }
}

main().catch(console.error);
