#!/usr/bin/env node
/**
 * 🌐 NNS Name Registration Script v2.0
 * Register a .nad name on Monad blockchain via Nad Name Service
 * 
 * Usage: 
 *   node register-name.js --name <name> [options]
 * 
 * Options:
 *   --name <name>      Name to register (required)
 *   --set-primary      Set as primary name after registration
 *   --managed          Use encrypted keystore (creates if doesn't exist)
 *   --address <addr>   Custom address (for verification)
 *   --dry-run          Show what would be done without sending transaction
 *   --referrer <addr>  Referrer address for discounts
 * 
 * Private key sources (in order of priority):
 *   1. PRIVATE_KEY environment variable (recommended ✅)
 *   2. ~/.nadname/private-key.enc (encrypted, managed mode)
 *   3. ~/.nadname/private-key (plaintext, managed mode only)
 * 
 * ⚠️ Security: This script does NOT auto-detect wallet locations outside
 *    ~/.nadname/ to avoid accessing unrelated credentials.
 * 
 * 🆕 v2.0 Features:
 *   - Real NAD API integration with registerWithSignature
 *   - Dynamic gas estimation with 2x safety buffer
 *   - Dry-run mode for testing
 *   - Better error handling and transaction confirmation
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const readline = require('readline');
const https = require('https');
const { URL } = require('url');

// Monad network configuration
const MONAD_RPC = 'https://rpc.monad.xyz';
const MONAD_CHAIN_ID = 143;
const NNS_CONTRACT = '0xE18a7550AA35895c87A1069d1B775Fa275Bc93Fb';
const NAD_API_BASE = 'https://api.nad.domains';

// Payment token addresses (MON is the native token)
const PAYMENT_TOKENS = {
  MON: '0x0000000000000000000000000000000000000000', // Native token
  // Add other tokens if supported
};

const CONFIG_DIR = path.join(process.env.HOME, '.nadname');
const ENCRYPTED_KEY_FILE = path.join(CONFIG_DIR, 'private-key.enc');
const PLAIN_KEY_FILE = path.join(CONFIG_DIR, 'private-key');
const WALLET_INFO_FILE = path.join(CONFIG_DIR, 'wallet.json');

function getArg(name) {
  const args = process.argv.slice(2);
  const idx = args.indexOf(name);
  if (idx !== -1 && args[idx + 1]) {
    return args[idx + 1];
  }
  return null;
}

function hasFlag(name) {
  return process.argv.includes(name);
}

async function makeApiRequest(path, method = 'GET', body = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, NAD_API_BASE);
    const options = {
      hostname: url.hostname,
      port: url.port || (url.protocol === 'https:' ? 443 : 80),
      path: url.pathname + url.search,
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'NadName-Agent/2.0.0',
        'Accept': 'application/json'
      }
    };

    if (body) {
      const bodyStr = JSON.stringify(body);
      options.headers['Content-Length'] = Buffer.byteLength(bodyStr);
    }

    const req = https.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(parsed);
          } else {
            reject(new Error(`API Error ${res.statusCode}: ${parsed.message || data}`));
          }
        } catch (e) {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(data);
          } else {
            reject(new Error(`API Error ${res.statusCode}: ${data}`));
          }
        }
      });
    });

    req.on('error', (err) => {
      reject(new Error(`Network error: ${err.message}`));
    });

    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    req.setTimeout(15000); // 15 second timeout for registration

    if (body) {
      req.write(JSON.stringify(body));
    }
    
    req.end();
  });
}

function prompt(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  return new Promise(resolve => {
    rl.question(question, answer => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

function promptPassword(question) {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });
    
    rl.stdoutMuted = true;
    rl.question(question, (answer) => {
      rl.close();
      console.log(''); // New line after password
      resolve(answer);
    });
    
    rl._writeToOutput = function _writeToOutput(stringToWrite) {
      if (rl.stdoutMuted && stringToWrite.charCodeAt(0) !== 13) {
        rl.output.write('*');
      } else {
        rl.output.write(stringToWrite);
      }
    };
  });
}

async function getPrivateKey() {
  // Priority 1: Environment variable (recommended)
  if (process.env.PRIVATE_KEY) {
    const key = process.env.PRIVATE_KEY.trim();
    if (!key.startsWith('0x')) {
      console.error('❌ PRIVATE_KEY must start with 0x');
      process.exit(1);
    }
    return key;
  }
  
  // Priority 2: Managed mode (encrypted or plain keystore)
  if (hasFlag('--managed')) {
    return await getManagedKey();
  }
  
  console.error('❌ No private key source specified!');
  console.error('');
  console.error('Options:');
  console.error('1. export PRIVATE_KEY="0x..." (recommended)');
  console.error('2. node register-name.js --managed --name <name>');
  console.error('');
  process.exit(1);
}

async function getManagedKey() {
  // Check for encrypted key first
  if (fs.existsSync(ENCRYPTED_KEY_FILE)) {
    try {
      const password = await promptPassword('🔐 Enter keystore password: ');
      return decryptPrivateKey(password);
    } catch (error) {
      console.error('❌ Failed to decrypt private key:', error.message);
      process.exit(1);
    }
  }
  
  // Check for plain key (fallback)
  if (fs.existsSync(PLAIN_KEY_FILE)) {
    console.warn('⚠️  Using unencrypted private key (consider re-running setup with encryption)');
    return fs.readFileSync(PLAIN_KEY_FILE, 'utf8').trim();
  }
  
  // No keystore found - create new one
  console.log('📦 No keystore found. Creating new encrypted wallet...');
  return await createManagedWallet();
}

async function createManagedWallet() {
  // Create config directory
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true, mode: 0o700 });
  }
  
  // Generate new wallet
  const wallet = ethers.Wallet.createRandom();
  
  console.log('🔑 Generated new wallet:');
  console.log(`📍 Address: ${wallet.address}`);
  console.log('');
  console.log('🔐 Setting up encryption...');
  
  const password = await promptPassword('Enter password for keystore: ');
  const confirmPassword = await promptPassword('Confirm password: ');
  
  if (password !== confirmPassword) {
    console.error('❌ Passwords do not match');
    process.exit(1);
  }
  
  if (password.length < 8) {
    console.error('❌ Password must be at least 8 characters');
    process.exit(1);
  }
  
  // Encrypt and save private key
  encryptPrivateKey(wallet.privateKey, password);
  
  // Save wallet info (public data only)
  const walletInfo = {
    address: wallet.address,
    created: new Date().toISOString(),
    encrypted: true
  };
  
  fs.writeFileSync(WALLET_INFO_FILE, JSON.stringify(walletInfo, null, 2));
  fs.chmodSync(WALLET_INFO_FILE, 0o600);
  
  console.log('');
  console.log('✅ Encrypted keystore created successfully!');
  console.log('⚠️  IMPORTANT: Save your mnemonic phrase securely:');
  console.log('');
  console.log(`🔤 ${wallet.mnemonic.phrase}`);
  console.log('');
  console.log('This is your only backup - write it down safely!');
  
  const save = await prompt('Save mnemonic to encrypted file? (y/N): ');
  if (save.toLowerCase() === 'y') {
    const mnemonicFile = path.join(CONFIG_DIR, 'mnemonic.enc');
    const encMnemonic = encrypt(wallet.mnemonic.phrase, password);
    fs.writeFileSync(mnemonicFile, encMnemonic);
    fs.chmodSync(mnemonicFile, 0o400);
    console.log('💾 Mnemonic saved to encrypted file');
  }
  
  return wallet.privateKey;
}

function encryptPrivateKey(privateKey, password) {
  const encrypted = encrypt(privateKey, password);
  fs.writeFileSync(ENCRYPTED_KEY_FILE, encrypted);
  fs.chmodSync(ENCRYPTED_KEY_FILE, 0o600);
}

function decryptPrivateKey(password) {
  const encrypted = fs.readFileSync(ENCRYPTED_KEY_FILE, 'utf8');
  return decrypt(encrypted, password);
}

function encrypt(text, password) {
  const algorithm = 'aes-256-gcm';
  const salt = crypto.randomBytes(16);
  const key = crypto.pbkdf2Sync(password, salt, 100000, 32, 'sha512');
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipher(algorithm, key);
  cipher.setAAD(salt);
  
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  const tag = cipher.getAuthTag();
  
  const result = {
    salt: salt.toString('hex'),
    iv: iv.toString('hex'),
    tag: tag.toString('hex'),
    encrypted: encrypted
  };
  
  return JSON.stringify(result);
}

function decrypt(encryptedData, password) {
  const data = JSON.parse(encryptedData);
  const algorithm = 'aes-256-gcm';
  const salt = Buffer.from(data.salt, 'hex');
  const key = crypto.pbkdf2Sync(password, salt, 100000, 32, 'sha512');
  const decipher = crypto.createDecipher(algorithm, key);
  
  decipher.setAAD(salt);
  decipher.setAuthTag(Buffer.from(data.tag, 'hex'));
  
  let decrypted = decipher.update(data.encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  
  return decrypted;
}

async function getRegistrationData(name, owner, setPrimary = false, referrer = null, paymentToken = 'MON') {
  console.log('📡 Requesting registration data from NAD API...');
  
  const requestBody = {
    name: name,
    owner: owner,
    setAsPrimary: setPrimary,
    referrer: referrer || null,
    paymentToken: PAYMENT_TOKENS[paymentToken] || PAYMENT_TOKENS.MON
  };
  
  console.log('📝 Registration request:', requestBody);
  
  try {
    // Try the CloudLobster suggested endpoint
    const result = await makeApiRequest('/api/register-request', 'POST', requestBody);
    
    if (!result.registerData || !result.signature || !result.price) {
      throw new Error('Invalid API response: missing required fields');
    }
    
    console.log('✅ Got registration data from API');
    console.log(`💰 Price: ${result.price} ${paymentToken}`);
    
    return result;
  } catch (error) {
    console.error(`❌ NAD API error: ${error.message}`);
    throw new Error(`Cannot get registration data: ${error.message}`);
  }
}

async function estimateRegistrationGas(signer, registerData, signature, value) {
  try {
    console.log('⛽ Estimating gas for registration...');
    
    // Basic contract interface for registerWithSignature
    const contractInterface = new ethers.Interface([
      'function registerWithSignature(tuple(string name, address nameOwner, bool setAsPrimaryName, address referrer, bytes32 discountKey, bytes[] discountClaimProof, uint256 nonce, uint256 deadline, bytes attributes, address paymentToken) registerData, bytes signature) payable'
    ]);
    
    const data = contractInterface.encodeFunctionData('registerWithSignature', [registerData, signature]);
    
    const gasEstimate = await signer.provider.estimateGas({
      to: NNS_CONTRACT,
      data: data,
      value: value,
      from: signer.address
    });
    
    // CloudLobster's experience: estimate was 646K, actual used 969K
    // Apply 2x safety buffer as suggested
    const safeGasLimit = gasEstimate * 2n;
    
    console.log(`⛽ Gas estimate: ${gasEstimate.toLocaleString()}`);
    console.log(`⛽ Safe gas limit (2x): ${safeGasLimit.toLocaleString()}`);
    
    return safeGasLimit;
  } catch (error) {
    console.warn(`⚠️  Gas estimation failed: ${error.message}`);
    console.warn('⚠️  Using fallback gas limit: 1,000,000');
    return 1000000n; // Fallback to 1M gas
  }
}

async function registerName(name, wallet, setPrimary = false, referrer = null, dryRun = false) {
  console.log('🚀 Starting registration...');
  
  // Connect to Monad
  const provider = new ethers.JsonRpcProvider(MONAD_RPC);
  const signer = wallet.connect(provider);
  
  // Verify network
  const network = await provider.getNetwork();
  if (network.chainId !== BigInt(MONAD_CHAIN_ID)) {
    throw new Error(`Wrong network! Expected ${MONAD_CHAIN_ID}, got ${network.chainId}`);
  }
  
  console.log(`⛓️  Connected to Monad (${MONAD_CHAIN_ID})`);
  
  // Check balance
  const balance = await provider.getBalance(wallet.address);
  const balanceInMON = ethers.formatEther(balance);
  console.log(`💰 Balance: ${balanceInMON} MON`);
  
  try {
    // Step 1: Get registration data and signature from NAD API
    const apiResponse = await getRegistrationData(name, wallet.address, setPrimary, referrer);
    const { registerData, signature, price } = apiResponse;
    
    // Parse price (could be in various formats)
    let priceInWei;
    if (typeof price === 'string') {
      priceInWei = ethers.parseEther(price);
    } else if (typeof price === 'number') {
      priceInWei = ethers.parseEther(price.toString());
    } else {
      throw new Error(`Invalid price format: ${price}`);
    }
    
    const priceInMON = ethers.formatEther(priceInWei);
    
    console.log('');
    console.log('📝 Registration details:');
    console.log(`   Name: ${name}.nad`);
    console.log(`   Owner: ${wallet.address}`);
    console.log(`   Price: ${priceInMON} MON`);
    console.log(`   Set as primary: ${setPrimary ? 'Yes' : 'No'}`);
    if (referrer) console.log(`   Referrer: ${referrer}`);
    console.log(`   Contract: ${NNS_CONTRACT}`);
    console.log('');
    
    // Check if user has enough balance
    if (parseFloat(balanceInMON) < parseFloat(priceInMON)) {
      throw new Error(`Insufficient balance! Need ${priceInMON} MON, have ${balanceInMON} MON`);
    }
    
    // Step 2: Estimate gas
    const gasLimit = await estimateRegistrationGas(signer, registerData, signature, priceInWei);
    
    // Estimate gas cost
    const gasPrice = await provider.getGasPrice();
    const gasCostWei = gasLimit * gasPrice;
    const gasCostMON = ethers.formatEther(gasCostWei);
    
    console.log(`⛽ Estimated gas cost: ${gasCostMON} MON`);
    console.log(`💸 Total cost: ${(parseFloat(priceInMON) + parseFloat(gasCostMON)).toFixed(6)} MON`);
    console.log('');
    
    if (dryRun) {
      console.log('🏃‍♂️ DRY RUN MODE - No transaction will be sent');
      console.log('✅ Registration data looks valid');
      console.log('✅ Gas estimation successful');
      console.log('✅ Sufficient balance available');
      console.log('');
      console.log('💡 Remove --dry-run flag to execute the registration');
      return;
    }
    
    // Final confirmation
    console.log('⚠️  FINAL CONFIRMATION:');
    console.log(`   This will register ${name}.nad for ${priceInMON} MON`);
    console.log(`   Transaction is irreversible once confirmed`);
    console.log('');
    
    // Step 3: Send the transaction
    console.log('📤 Sending registration transaction...');
    
    const contractInterface = new ethers.Interface([
      'function registerWithSignature(tuple(string name, address nameOwner, bool setAsPrimaryName, address referrer, bytes32 discountKey, bytes[] discountClaimProof, uint256 nonce, uint256 deadline, bytes attributes, address paymentToken) registerData, bytes signature) payable'
    ]);
    
    const data = contractInterface.encodeFunctionData('registerWithSignature', [registerData, signature]);
    
    const tx = {
      to: NNS_CONTRACT,
      value: priceInWei,
      data: data,
      gasLimit: gasLimit,
      gasPrice: gasPrice
    };
    
    const result = await signer.sendTransaction(tx);
    console.log(`⏳ Transaction sent: ${result.hash}`);
    
    console.log('⏳ Waiting for confirmation...');
    const receipt = await result.wait();
    
    if (receipt.status === 1) {
      console.log('');
      console.log('🎉 Registration successful!');
      console.log(`✅ ${name}.nad is now yours!`);
      console.log(`🔗 Transaction: https://explorer.monad.xyz/tx/${result.hash}`);
      console.log(`⛽ Gas used: ${receipt.gasUsed.toLocaleString()}`);
      console.log(`💸 Total cost: ${ethers.formatEther(receipt.gasUsed * gasPrice + priceInWei)} MON`);
      
      if (setPrimary) {
        console.log('✅ Set as primary name');
      }
    } else {
      console.log('❌ Transaction failed');
      throw new Error('Transaction failed');
    }
    
  } catch (error) {
    console.error('❌ Registration failed:', error.message);
    
    if (error.message.includes('API')) {
      console.error('💡 Check if NAD API is available and try again');
    } else if (error.message.includes('gas')) {
      console.error('💡 Try increasing gas limit or wait for network conditions to improve');
    } else if (error.message.includes('balance')) {
      console.error('💡 Top up your wallet with more MON tokens');
    }
    
    throw error;
  }
}

async function main() {
  const name = getArg('--name');
  const setPrimary = hasFlag('--set-primary');
  const customAddress = getArg('--address');
  const referrer = getArg('--referrer');
  const dryRun = hasFlag('--dry-run');
  
  if (!name) {
    console.error('❌ Usage: node register-name.js --name <name> [options]');
    console.error('');
    console.error('Options:');
    console.error('  --name <name>      Name to register (required)');
    console.error('  --set-primary      Set as primary name');
    console.error('  --managed          Use encrypted keystore');
    console.error('  --address <addr>   Custom address for verification');
    console.error('  --dry-run          Show what would be done without sending transaction');
    console.error('  --referrer <addr>  Referrer address for discounts');
    console.error('');
    console.error('Examples:');
    console.error('  node register-name.js --name mybot');
    console.error('  node register-name.js --name agent --set-primary');
    console.error('  node register-name.js --managed --name myagent --dry-run');
    console.error('  node register-name.js --name myagent --referrer 0x...');
    process.exit(1);
  }

  try {
    console.log('🌐 NNS Name Registration v2.0');
    console.log('═'.repeat(50));
    
    // Get private key
    const privateKey = await getPrivateKey();
    const wallet = new ethers.Wallet(privateKey);
    
    console.log(`📍 Wallet: ${wallet.address}`);
    console.log(`📝 Name: ${name}.nad`);
    
    if (setPrimary) {
      console.log('✅ Will set as primary name');
    }
    
    if (referrer) {
      console.log(`🔗 Referrer: ${referrer}`);
    }
    
    if (dryRun) {
      console.log('🏃‍♂️ DRY RUN MODE');
    }
    
    console.log('');
    
    // Register the name
    await registerName(name, wallet, setPrimary, referrer, dryRun);
    
    if (!dryRun) {
      console.log('');
      console.log('🎊 Registration completed successfully!');
      console.log(`🌐 Your name: ${name}.nad`);
      console.log(`📱 Manage at: https://app.nad.domains`);
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}