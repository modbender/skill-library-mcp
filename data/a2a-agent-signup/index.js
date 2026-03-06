#!/usr/bin/env node

/**
 * A2A Agent Signup - Interactive CLI Wizard
 * Onboard as an agent on the A2A Marketplace
 */

const fs = require('fs');
const path = require('path');
const { ethers } = require('ethers');

// Configuration from environment variables
const API_URL = process.env.A2A_API_URL || 'https://a2a.ex8.ca/a2a/jsonrpc';
const BASE_URL = (() => {
  try {
    const url = new URL(API_URL);
    return `${url.protocol}//${url.host}`; // e.g., https://a2a.ex8.ca
  } catch (e) {
    return 'https://a2a.ex8.ca';
  }
})();
const SIGNUP_FEE_RECIPIENT = '0x26fc06D17Eb82638b25402D411889EEb69F1e7C5'; // Marc's wallet (hardcoded)
const CONFIG_PATH = path.join(process.env.HOME, '.a2a-agent-config');
const ENV_PATH = path.join(process.cwd(), '.env');
let AGENT_WALLET = process.env.AGENT_WALLET || ''; // Agent's wallet (from .env)

const SPECIALIZATIONS = [
  'ai-development',
  'data-analysis',
  'writing',
  'design',
  'smart-contracts',
  'security-audit',
  'devops',
  'consulting',
  'other'
];

// Parse CLI args for non-interactive mode
function parseArgs() {
  const args = {};
  const argv = process.argv.slice(2);
  for (let i = 0; i < argv.length; i += 2) {
    if (argv[i].startsWith('--')) {
      args[argv[i].slice(2)] = argv[i + 1];
    }
  }
  return args;
}

// First-time setup: prompt for agent wallet if not in .env
async function setupWallet() {
  if (AGENT_WALLET) {
    return; // Already configured
  }

  const { prompt } = require('enquirer');

  console.log('\n🦪 A2A Agent Signup - First Time Setup\n');
  console.log('Let\'s set up your agent wallet.\n');

  const result = await prompt({
    type: 'input',
    name: 'wallet',
    message: 'Enter your Polygon wallet address (0x...):',
    validate: v => /^0x[a-fA-F0-9]{40}$/.test(v) || 'Invalid address format'
  });

  AGENT_WALLET = result.wallet;

  // Save to .env
  const envContent = `# A2A Agent Signup Configuration

# YOUR agent wallet address (where you receive payments from clients)
# This is the wallet that will be charged $0.01 USDC for registration
AGENT_WALLET=${AGENT_WALLET}

# The API URL for the A2A Marketplace (registerAgent JSON-RPC endpoint)
# Default: https://a2a.ex8.ca/a2a/jsonrpc
# Only change if you're running your own A2A Marketplace instance
A2A_API_URL=https://a2a.ex8.ca/a2a/jsonrpc
`;

  fs.writeFileSync(ENV_PATH, envContent);
  fs.chmodSync(ENV_PATH, 0o600);

  console.log(`\n✅ Wallet saved to .env`);
  console.log(`   Agent Wallet: ${AGENT_WALLET}\n`);
}

async function interactivePrompt() {
  // Dynamic import for enquirer
  const { prompt } = require('enquirer');

  console.log('\n🦪 A2A Marketplace - Agent Signup Wizard\n');
  console.log('Register as an agent and list your first service.\n');

  // Step 1: Wallet (skip if already configured from setupWallet)
  let walletAddress, signature;

  if (AGENT_WALLET) {
    console.log('━━━ Step 1: Wallet ━━━\n');
    console.log(`Using configured wallet: ${AGENT_WALLET}\n`);
    walletAddress = AGENT_WALLET;
  } else {
    console.log('━━━ Step 1: Wallet Connection ━━━\n');
    
    const { walletMethod } = await prompt({
      type: 'select',
      name: 'walletMethod',
      message: 'How would you like to connect your wallet?',
      choices: [
        { name: 'manual', message: 'Enter wallet address manually' },
        { name: 'generate', message: 'Generate a new wallet (for testing)' }
      ]
    });

    if (walletMethod === 'generate') {
      const wallet = ethers.Wallet.createRandom();
      walletAddress = wallet.address;
      const msg = `Sign up for A2A Marketplace: ${Date.now()}`;
      signature = await wallet.signMessage(msg);
      console.log(`\n  Generated wallet: ${walletAddress}`);
      console.log(`  ⚠️  Save your private key: ${wallet.privateKey}\n`);
    } else {
      const result = await prompt({
        type: 'input',
        name: 'walletAddress',
        message: 'Enter your Ethereum/Polygon wallet address (0x...):',
        validate: v => /^0x[a-fA-F0-9]{40}$/.test(v) || 'Invalid address format'
      });
      walletAddress = result.walletAddress;
    }
  }

  // Step 2: Profile
  console.log('\n━━━ Step 2: Agent Profile ━━━\n');

  const profile = await prompt([
    {
      type: 'input',
      name: 'name',
      message: 'Agent name:',
      validate: v => v.length >= 2 || 'Name must be at least 2 characters'
    },
    {
      type: 'input',
      name: 'bio',
      message: 'Bio (describe your skills):',
      validate: v => v.length >= 10 || 'Bio must be at least 10 characters'
    },
    {
      type: 'select',
      name: 'specialization',
      message: 'Specialization:',
      choices: SPECIALIZATIONS
    }
  ]);

  // Step 3: First Service (optional)
  console.log('\n━━━ Step 3: Services (Optional) ━━━\n');

  const { wantService } = await prompt({
    type: 'confirm',
    name: 'wantService',
    message: 'Do you want to list a service? (You can add services later)',
    initial: false
  });

  let service = {
    serviceTitle: '',
    serviceDescription: '',
    price: 0,
    currency: 'SHIB'
  };

  if (wantService) {
    // Get exchange rates
    let rates = { SHIB: 0, USDC: 1 };
    try {
      const ratesResp = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=shiba-inu,usd-coin&vs_currencies=usd');
      const ratesData = await ratesResp.json();
      rates.SHIB = ratesData['shiba-inu']?.usd || 0;
      rates.USDC = ratesData['usd-coin']?.usd || 1;
    } catch (e) {
      console.log('  (Could not fetch exchange rates, USD conversion unavailable)\n');
    }

    // Ask for title and description first
    const titleAndDesc = await prompt([
      {
        type: 'input',
        name: 'serviceTitle',
        message: 'Service title:',
        validate: v => v.length >= 3 || 'Title must be at least 3 characters'
      },
      {
        type: 'input',
        name: 'serviceDescription',
        message: 'Service description:',
        validate: v => v.length >= 10 || 'Description must be at least 10 characters'
      }
    ]);

    // Ask for currency first
    const { currency } = await prompt({
      type: 'select',
      name: 'currency',
      message: 'Currency:',
      choices: ['SHIB', 'USDC']
    });

    // Then ask for price with USD conversion
    const rate = rates[currency] || 0;
    
    // Helper to format USD with dynamic decimal places
    function formatUSD(amount) {
      if (amount === 0) return '$0.00';
      
      // Get string with many decimals
      const str = amount.toFixed(20);
      const [intPart, decPart] = str.split('.');
      
      if (!decPart) return '$' + amount.toFixed(2);
      
      // Find first non-zero digit position in decimal part
      let firstNonZeroIdx = -1;
      for (let i = 0; i < decPart.length; i++) {
        if (decPart[i] !== '0') {
          firstNonZeroIdx = i;
          break;
        }
      }
      
      if (firstNonZeroIdx === -1) return '$0.00';
      
      // Show up to first non-zero + 2 more places
      const decimalsNeeded = firstNonZeroIdx + 3;
      return '$' + amount.toFixed(decimalsNeeded);
    }
    
    const { price } = await prompt({
      type: 'numeral',
      name: 'price',
      message: rate > 0 
        ? `Price in ${currency}: (1 ${currency} = $${rate.toFixed(6)} USD)`
        : `Price in ${currency}:`,
      validate: v => v > 0 || 'Price must be positive',
      result: v => {
        if (rate > 0) {
          const usdValue = v * rate;
          console.log(`   → ${formatUSD(usdValue)} USD equivalent\n`);
        }
        return v;
      }
    });

    service = { ...titleAndDesc, currency, price };
  }

  return { walletAddress, signature, ...profile, ...service };
}

// Create a signup session for payment
async function createSignupSession(params) {
  const payload = {
    jsonrpc: '2.0',
    id: 1,
    method: 'createSignupSession',
    params: {
      walletAddress: params.walletAddress,
      name: params.name,
      bio: params.bio,
      specialization: params.specialization,
      serviceTitle: params.serviceTitle,
      serviceDescription: params.serviceDescription,
      price: typeof params.price === 'string' ? parseFloat(params.price) : params.price,
      currency: params.currency
    }
  };

  const response = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  const data = await response.json();
  if (data.error) throw new Error(data.error.message);
  return data.result;
}

// Poll for payment completion
async function pollPaymentStatus(sessionId, maxAttempts = 60) {
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const response = await fetch(`${BASE_URL}/a2a/signup-session/${sessionId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      const data = await response.json();
      
      if (data.status === 'completed') {
        return data;
      }
      
      if (data.status === 'failed') {
        throw new Error('Payment verification failed');
      }
      
      // Wait 2 seconds before next poll
      await new Promise(r => setTimeout(r, 2000));
      process.stdout.write('.');
    } catch (err) {
      // Retry on network errors
      await new Promise(r => setTimeout(r, 2000));
    }
  }
  
  throw new Error('Payment verification timeout - please try again');
}

// Ask user how to pay
async function askPaymentMethod() {
  const { prompt } = require('enquirer');
  
  const { method } = await prompt({
    type: 'select',
    name: 'method',
    message: 'How would you like to pay the $0.01 USDC registration fee?',
    choices: [
      { name: 'browser', message: '🌐 Open in browser (MetaMask)' },
      { name: 'manual', message: '📋 Copy payment details manually' },
      { name: 'qr', message: '📱 Show QR code for mobile wallet' }
    ]
  });
  
  return method;
}

async function registerAgent(params) {
  const payload = {
    jsonrpc: '2.0',
    id: 1,
    method: 'registerAgent',
    params: {
      name: params.name,
      bio: params.bio,
      specialization: params.specialization,
      serviceTitle: params.serviceTitle,
      serviceDescription: params.serviceDescription,
      price: typeof params.price === 'string' ? parseFloat(params.price) : params.price,
      currency: params.currency,
      walletAddress: params.walletAddress,
      signature: params.signature || null,
      adminWallet: SIGNUP_FEE_RECIPIENT // Marc's wallet receives signup fee
    }
  };

  console.log('\n⏳ Registering with A2A Marketplace...\n');
  console.log(`  Agent Wallet: ${params.walletAddress}`);
  console.log(`  Signup Fee Recipient: ${SIGNUP_FEE_RECIPIENT}\n`);

  const response = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  const data = await response.json();

  if (data.error) {
    throw new Error(data.error.message);
  }

  return data.result;
}

function saveConfig(result, walletAddress) {
  const config = {
    profileId: result.profileId,
    authToken: result.authToken,
    serviceId: result.serviceId,
    walletAddress,
    apiUrl: API_URL,
    registeredAt: new Date().toISOString()
  };

  fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
  fs.chmodSync(CONFIG_PATH, 0o600);
  return config;
}

async function main() {
  try {
    const args = parseArgs();
    
    // First-time setup: configure wallet if not already set
    if (!args.walletAddress && !AGENT_WALLET) {
      await setupWallet();
    } else if (args.walletAddress) {
      AGENT_WALLET = args.walletAddress;
    }

    let params;

    // Non-interactive mode if all required args provided
    if (args.name && args.serviceTitle) {
      params = {
        name: args.name,
        bio: args.bio || '',
        specialization: args.specialization || 'other',
        serviceTitle: args.serviceTitle,
        serviceDescription: args.serviceDescription || args.serviceTitle,
        price: parseFloat(args.price || '100'),
        currency: args.currency || 'SHIB',
        walletAddress: args.walletAddress || AGENT_WALLET
      };
      console.log('\n🦪 A2A Marketplace - Agent Registration\n');
    } else {
      params = await interactivePrompt();
    }

    // Create signup session and handle payment
    console.log('\n━━━ Step 4: Payment ━━━\n');
    console.log('Registration fee: $0.01 USDC on Polygon\n');
    
    const session = await createSignupSession(params);
    const paymentMethod = await askPaymentMethod();
    
    if (paymentMethod === 'browser') {
      const paymentUrl = `${BASE_URL}/signup/${session.sessionId}`;
      console.log(`\n🌐 Opening payment page in browser...\n`);
      console.log(`   URL: ${paymentUrl}\n`);
      console.log('   Please complete the payment in your browser.\n');
      
      // Try to open in browser (if available)
      const { exec } = require('child_process');
      exec(`open "${paymentUrl}" || xdg-open "${paymentUrl}" || start "${paymentUrl}"`, () => {});
      
    } else if (paymentMethod === 'manual') {
      console.log('\n📋 Payment Details:\n');
      console.log(`   Amount:    0.01 USDC`);
      console.log(`   To:        ${SIGNUP_FEE_RECIPIENT}`);
      console.log(`   Network:   Polygon (chainId: 137)`);
      console.log(`   Token:     USDC (0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174)\n`);
      console.log('   Copy and send from your wallet.\n');
      
    } else if (paymentMethod === 'qr') {
      const paymentUrl = `${BASE_URL}/signup/${session.sessionId}`;
      const QRCode = require('qrcode');
      
      console.log('\n📱 Scan with your mobile wallet:\n');
      const qrAscii = await QRCode.toString(paymentUrl, { type: 'terminal' });
      console.log(qrAscii);
      console.log(`\n   Payment URL: ${paymentUrl}\n`);
    }
    
    console.log('⏳ Waiting for payment confirmation...\n');
    const paymentStatus = await pollPaymentStatus(session.sessionId);
    console.log('\n✅ Payment verified!\n');
    
    // Now register the agent with the verified session
    const result = await registerAgent(params);
    const config = saveConfig(result, params.walletAddress);

    console.log('✅ Registration successful!\n');
    console.log(`  Profile ID:  ${result.profileId}`);
    console.log(`  Service ID:  ${result.serviceId}`);
    console.log(`  Profile URL: ${result.profileUrl}`);
    console.log(`  Config saved: ${CONFIG_PATH}`);
    console.log(`\n  ${result.message}\n`);

    // Output JSON for programmatic use
    if (args.json) {
      console.log(JSON.stringify(result, null, 2));
    }

    return result;
  } catch (error) {
    console.error(`\n❌ Registration failed: ${error.message}\n`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { registerAgent, saveConfig, API_URL };
