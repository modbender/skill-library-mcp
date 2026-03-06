#!/usr/bin/env node
/**
 * AgentWallet - Multi-chain wallet for AI agents
 * Commands: create, addresses, balance, transfer, bridge, chains
 */

import * as bip39 from 'bip39';
import { Keypair, Connection, PublicKey, Transaction, SystemProgram, LAMPORTS_PER_SOL } from '@solana/web3.js';
import { getAssociatedTokenAddress, createTransferInstruction, createAssociatedTokenAccountInstruction, getAccount, TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID } from '@solana/spl-token';
import { ethers } from 'ethers';
import bs58 from 'bs58';
import dotenv from 'dotenv';

// Bridge Kit imports (dynamic to handle if not installed)
let BridgeKit, createViemAdapterFromPrivateKey, createSolanaKitAdapterFromPrivateKey;

dotenv.config();

// ============ CONFIGURATION ============

const NETWORK = process.env.NETWORK || 'testnet';
const isMainnet = NETWORK === 'mainnet';

const CHAINS = {
  solana: {
    name: 'Solana',
    native: 'SOL',
    decimals: 9,
    rpc: process.env.SOLANA_RPC || (isMainnet 
      ? 'https://api.mainnet-beta.solana.com' 
      : 'https://api.devnet.solana.com'),
    usdc: isMainnet 
      ? 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
      : '4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU',
  },
  base: {
    name: 'Base',
    native: 'ETH',
    decimals: 18,
    chainId: isMainnet ? 8453 : 84532,
    rpc: process.env.BASE_RPC || (isMainnet 
      ? 'https://mainnet.base.org' 
      : 'https://sepolia.base.org'),
    usdc: isMainnet
      ? '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'
      : '0x036CbD53842c5426634e7929541eC2318f3dCF7e',
  },
  ethereum: {
    name: 'Ethereum',
    native: 'ETH',
    decimals: 18,
    chainId: isMainnet ? 1 : 11155111,
    rpc: process.env.ETH_RPC || (isMainnet 
      ? 'https://eth.llamarpc.com' 
      : 'https://rpc.sepolia.org'),
    usdc: isMainnet
      ? '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
      : '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',
  },
};

// ============ WALLET DERIVATION ============

function getSeedPhrase() {
  const seed = process.env.WALLET_SEED_PHRASE;
  if (!seed) return null;
  if (!bip39.validateMnemonic(seed.trim())) {
    throw new Error('Invalid seed phrase format');
  }
  return seed.trim();
}

function deriveSolanaKeypair(seedPhrase) {
  // Solana: m/44'/501'/0'/0' - using first 32 bytes of seed
  const seed = bip39.mnemonicToSeedSync(seedPhrase);
  return Keypair.fromSeed(seed.slice(0, 32));
}

function deriveEVMWallet(seedPhrase) {
  // EVM: m/44'/60'/0'/0/0 - standard BIP-44 Ethereum path
  return ethers.HDNodeWallet.fromPhrase(seedPhrase);
}

function formatAddress(address, length = 4) {
  if (address.startsWith('0x')) {
    return `0x${address.slice(2, 2 + length)}...${address.slice(-length)}`;
  }
  return `${address.slice(0, length)}...${address.slice(-length)}`;
}

// ============ COMMANDS ============

async function createWallet() {
  // Generate new BIP-39 mnemonic (128 bits = 12 words)
  const mnemonic = bip39.generateMnemonic(128);
  
  // Derive addresses
  const solanaKeypair = deriveSolanaKeypair(mnemonic);
  const evmWallet = deriveEVMWallet(mnemonic);
  
  const solanaAddr = solanaKeypair.publicKey.toBase58();
  const evmAddr = evmWallet.address;
  
  console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔐 NEW WALLET GENERATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  CRITICAL: Save this seed phrase securely!
    It will NOT be shown again.
    Anyone with this phrase can access your funds.

Seed Phrase:
┌────────────────────────────────────────────────┐
│ ${mnemonic.split(' ').slice(0, 6).join(' ').padEnd(44)} │
│ ${mnemonic.split(' ').slice(6, 12).join(' ').padEnd(44)} │
└────────────────────────────────────────────────┘

Your Addresses:
├─ Solana:   ${formatAddress(solanaAddr)}
├─ Base:     ${formatAddress(evmAddr)}
└─ Ethereum: ${formatAddress(evmAddr)} (same as Base)

Full Addresses:
├─ Solana:   ${solanaAddr}
├─ Base:     ${evmAddr}
└─ Ethereum: ${evmAddr}

Add to .env:
WALLET_SEED_PHRASE="${mnemonic}"

Network: ${NETWORK.toUpperCase()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
}

async function showAddresses() {
  const seedPhrase = getSeedPhrase();
  if (!seedPhrase) {
    console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  NO WALLET CONFIGURED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

To create a new wallet:
  node wallet.js create

To import existing wallet:
  Add to .env: WALLET_SEED_PHRASE="your twelve words here"
  Then run: node wallet.js addresses
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
    return;
  }
  
  const solanaKeypair = deriveSolanaKeypair(seedPhrase);
  const evmWallet = deriveEVMWallet(seedPhrase);
  
  const solanaAddr = solanaKeypair.publicKey.toBase58();
  const evmAddr = evmWallet.address;
  
  console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💼 YOUR ADDRESSES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├─ Solana:   ${solanaAddr}
├─ Base:     ${evmAddr}
└─ Ethereum: ${evmAddr}

Network: ${NETWORK.toUpperCase()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
}

async function checkBalance(chain = null) {
  const seedPhrase = getSeedPhrase();
  if (!seedPhrase) {
    console.error('Error: WALLET_SEED_PHRASE not set in .env');
    process.exit(1);
  }
  
  const chainsToCheck = chain ? [chain.toLowerCase()] : Object.keys(CHAINS);
  const results = [];
  
  for (const chainKey of chainsToCheck) {
    if (!CHAINS[chainKey]) {
      console.error(`Unknown chain: ${chainKey}`);
      continue;
    }
    
    const chainConfig = CHAINS[chainKey];
    
    try {
      if (chainKey === 'solana') {
        const keypair = deriveSolanaKeypair(seedPhrase);
        const connection = new Connection(chainConfig.rpc, 'confirmed');
        
        // Native balance
        const lamports = await connection.getBalance(keypair.publicKey);
        const solBalance = lamports / LAMPORTS_PER_SOL;
        
        // USDC balance
        let usdcBalance = 0;
        try {
          const usdcMint = new PublicKey(chainConfig.usdc);
          const ata = await getAssociatedTokenAddress(usdcMint, keypair.publicKey);
          const account = await getAccount(connection, ata);
          usdcBalance = Number(account.amount) / 1e6;
        } catch (e) {
          // No USDC account
        }
        
        results.push({
          chain: chainConfig.name,
          native: `${solBalance.toFixed(6)} SOL`,
          usdc: `${usdcBalance.toFixed(2)} USDC`,
        });
      } else {
        // EVM chain
        const wallet = deriveEVMWallet(seedPhrase);
        const provider = new ethers.JsonRpcProvider(chainConfig.rpc, {
          chainId: chainConfig.chainId,
          name: chainKey,
        });
        
        // Native balance
        const ethBalance = await provider.getBalance(wallet.address);
        const ethFormatted = parseFloat(ethers.formatEther(ethBalance));
        
        // USDC balance
        let usdcBalance = 0;
        try {
          const usdcContract = new ethers.Contract(
            chainConfig.usdc,
            ['function balanceOf(address) view returns (uint256)'],
            provider
          );
          const usdcRaw = await usdcContract.balanceOf(wallet.address);
          usdcBalance = parseFloat(ethers.formatUnits(usdcRaw, 6));
        } catch (e) {
          // USDC fetch failed
        }
        
        results.push({
          chain: chainConfig.name,
          native: `${ethFormatted.toFixed(6)} ${chainConfig.native}`,
          usdc: `${usdcBalance.toFixed(2)} USDC`,
        });
      }
    } catch (e) {
      results.push({
        chain: chainConfig.name,
        native: 'Error',
        usdc: 'Error',
        error: e.message,
      });
    }
  }
  
  // Calculate total USDC
  const totalUsdc = results.reduce((sum, r) => {
    const match = r.usdc.match(/^([\d.]+)/);
    return sum + (match ? parseFloat(match[1]) : 0);
  }, 0);
  
  console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 WALLET BALANCES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  
  for (const r of results) {
    console.log(`├─ ${r.chain}: ${r.native} | ${r.usdc}${r.error ? ` (${r.error})` : ''}`);
  }
  
  if (results.length > 1) {
    console.log(`└─ Total USDC: ${totalUsdc.toFixed(2)} USDC`);
  }
  
  console.log(`
Network: ${NETWORK.toUpperCase()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
}

async function transfer(chain, token, amount, recipient) {
  const seedPhrase = getSeedPhrase();
  if (!seedPhrase) {
    console.error('Error: WALLET_SEED_PHRASE not set in .env');
    process.exit(1);
  }
  
  const chainKey = chain.toLowerCase();
  const tokenKey = token.toUpperCase();
  
  if (!CHAINS[chainKey]) {
    console.error(`Unknown chain: ${chain}. Supported: ${Object.keys(CHAINS).join(', ')}`);
    process.exit(1);
  }
  
  const chainConfig = CHAINS[chainKey];
  const amountNum = parseFloat(amount);
  
  if (isNaN(amountNum) || amountNum <= 0) {
    console.error('Invalid amount');
    process.exit(1);
  }
  
  console.log(`\n📤 Transferring ${amount} ${tokenKey} on ${chainConfig.name}...`);
  console.log(`   To: ${recipient}\n`);
  
  try {
    if (chainKey === 'solana') {
      const keypair = deriveSolanaKeypair(seedPhrase);
      const connection = new Connection(chainConfig.rpc, 'confirmed');
      
      // Validate recipient address
      let recipientPubkey;
      try {
        recipientPubkey = new PublicKey(recipient);
      } catch (e) {
        throw new Error('Invalid Solana address');
      }
      
      if (tokenKey === 'SOL') {
        // SOL transfer
        const lamports = Math.floor(amountNum * LAMPORTS_PER_SOL);
        const transaction = new Transaction().add(
          SystemProgram.transfer({
            fromPubkey: keypair.publicKey,
            toPubkey: recipientPubkey,
            lamports,
          })
        );
        
        const { blockhash } = await connection.getLatestBlockhash();
        transaction.recentBlockhash = blockhash;
        transaction.feePayer = keypair.publicKey;
        transaction.sign(keypair);
        
        const signature = await connection.sendRawTransaction(transaction.serialize());
        await connection.confirmTransaction(signature, 'confirmed');
        
        console.log(`✅ Success!`);
        console.log(`   Signature: ${signature}`);
        
      } else if (tokenKey === 'USDC') {
        // USDC transfer
        const usdcMint = new PublicKey(chainConfig.usdc);
        const fromAta = await getAssociatedTokenAddress(usdcMint, keypair.publicKey);
        const toAta = await getAssociatedTokenAddress(usdcMint, recipientPubkey);
        
        const transaction = new Transaction();
        
        // Check if recipient ATA exists
        try {
          await getAccount(connection, toAta);
        } catch (e) {
          // Create ATA for recipient
          transaction.add(
            createAssociatedTokenAccountInstruction(
              keypair.publicKey,
              toAta,
              recipientPubkey,
              usdcMint,
              TOKEN_PROGRAM_ID,
              ASSOCIATED_TOKEN_PROGRAM_ID
            )
          );
        }
        
        // Transfer USDC (6 decimals)
        const usdcAmount = BigInt(Math.floor(amountNum * 1e6));
        transaction.add(
          createTransferInstruction(fromAta, toAta, keypair.publicKey, usdcAmount)
        );
        
        const { blockhash } = await connection.getLatestBlockhash();
        transaction.recentBlockhash = blockhash;
        transaction.feePayer = keypair.publicKey;
        transaction.sign(keypair);
        
        const signature = await connection.sendRawTransaction(transaction.serialize());
        await connection.confirmTransaction(signature, 'confirmed');
        
        console.log(`✅ Success!`);
        console.log(`   Signature: ${signature}`);
        
      } else {
        throw new Error(`Unsupported token on Solana: ${tokenKey}. Use SOL or USDC.`);
      }
      
    } else {
      // EVM chain (Base, Ethereum)
      const wallet = deriveEVMWallet(seedPhrase);
      const provider = new ethers.JsonRpcProvider(chainConfig.rpc, {
        chainId: chainConfig.chainId,
        name: chainKey,
      });
      const signer = wallet.connect(provider);
      
      // Validate recipient address
      if (!ethers.isAddress(recipient)) {
        throw new Error('Invalid EVM address');
      }
      
      if (tokenKey === 'ETH') {
        // ETH transfer
        const tx = await signer.sendTransaction({
          to: recipient,
          value: ethers.parseEther(amount),
        });
        
        console.log(`   Tx Hash: ${tx.hash}`);
        const receipt = await tx.wait();
        
        console.log(`✅ Success!`);
        console.log(`   Block: ${receipt.blockNumber}`);
        
      } else if (tokenKey === 'USDC') {
        // USDC transfer
        const usdcContract = new ethers.Contract(
          chainConfig.usdc,
          [
            'function transfer(address to, uint256 amount) returns (bool)',
            'function balanceOf(address) view returns (uint256)',
          ],
          signer
        );
        
        const usdcAmount = ethers.parseUnits(amount, 6);
        const tx = await usdcContract.transfer(recipient, usdcAmount);
        
        console.log(`   Tx Hash: ${tx.hash}`);
        const receipt = await tx.wait();
        
        console.log(`✅ Success!`);
        console.log(`   Block: ${receipt.blockNumber}`);
        
      } else {
        throw new Error(`Unsupported token on ${chainConfig.name}: ${tokenKey}. Use ${chainConfig.native} or USDC.`);
      }
    }
  } catch (e) {
    console.error(`❌ Transfer failed: ${e.message}`);
    process.exit(1);
  }
}

// Bridge chain name mapping for Circle Bridge Kit
const BRIDGE_CHAIN_NAMES = {
  solana: isMainnet ? 'Solana' : 'Solana_Devnet',
  base: isMainnet ? 'Base' : 'Base_Sepolia',
  ethereum: isMainnet ? 'Ethereum' : 'Ethereum_Sepolia',
};

async function bridge(fromChain, toChain, amount) {
  const seedPhrase = getSeedPhrase();
  if (!seedPhrase) {
    console.error('Error: WALLET_SEED_PHRASE not set in .env');
    process.exit(1);
  }
  
  const fromKey = fromChain.toLowerCase();
  const toKey = toChain.toLowerCase();
  
  if (!CHAINS[fromKey]) {
    console.error(`Unknown source chain: ${fromChain}. Supported: ${Object.keys(CHAINS).join(', ')}`);
    process.exit(1);
  }
  
  if (!CHAINS[toKey]) {
    console.error(`Unknown destination chain: ${toChain}. Supported: ${Object.keys(CHAINS).join(', ')}`);
    process.exit(1);
  }
  
  if (fromKey === toKey) {
    console.error('Source and destination chains must be different. Use "transfer" for same-chain transfers.');
    process.exit(1);
  }
  
  const amountNum = parseFloat(amount);
  if (isNaN(amountNum) || amountNum <= 0) {
    console.error('Invalid amount');
    process.exit(1);
  }
  
  console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌉 CROSS-CHAIN BRIDGE (USDC)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
From:   ${CHAINS[fromKey].name}
To:     ${CHAINS[toKey].name}
Amount: ${amount} USDC
Network: ${NETWORK.toUpperCase()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
  
  try {
    // Dynamic import of Bridge Kit
    console.log('📦 Loading Bridge Kit...');
    const bridgeKitModule = await import('@circle-fin/bridge-kit');
    BridgeKit = bridgeKitModule.BridgeKit;
    
    const kit = new BridgeKit();
    
    // Prepare adapters based on chains involved
    let fromAdapter, toAdapter;
    
    // Derive keys
    const solanaKeypair = deriveSolanaKeypair(seedPhrase);
    const evmWallet = deriveEVMWallet(seedPhrase);
    
    // Get Solana private key as base58
    const solanaPrivateKeyBase58 = bs58.encode(solanaKeypair.secretKey);
    
    // Get EVM private key (with 0x prefix)
    const evmPrivateKey = evmWallet.privateKey;
    
    // Create adapters for source chain
    if (fromKey === 'solana') {
      const solanaAdapterModule = await import('@circle-fin/adapter-solana-kit');
      fromAdapter = solanaAdapterModule.createSolanaKitAdapterFromPrivateKey({
        privateKey: solanaPrivateKeyBase58,
      });
    } else {
      const viemAdapterModule = await import('@circle-fin/adapter-viem-v2');
      fromAdapter = viemAdapterModule.createViemAdapterFromPrivateKey({
        privateKey: evmPrivateKey,
      });
    }
    
    // Create adapters for destination chain
    if (toKey === 'solana') {
      const solanaAdapterModule = await import('@circle-fin/adapter-solana-kit');
      toAdapter = solanaAdapterModule.createSolanaKitAdapterFromPrivateKey({
        privateKey: solanaPrivateKeyBase58,
      });
    } else {
      const viemAdapterModule = await import('@circle-fin/adapter-viem-v2');
      toAdapter = viemAdapterModule.createViemAdapterFromPrivateKey({
        privateKey: evmPrivateKey,
      });
    }
    
    console.log('🔄 Initiating bridge transfer...');
    console.log('   This may take 1-5 minutes (burn → attest → mint)\n');
    
    const result = await kit.bridge({
      from: { adapter: fromAdapter, chain: BRIDGE_CHAIN_NAMES[fromKey] },
      to: { adapter: toAdapter, chain: BRIDGE_CHAIN_NAMES[toKey] },
      amount: amount,
    });
    
    // Debug: log full result (with BigInt handling)
    const safeStringify = (obj) => JSON.stringify(obj, (_, v) => typeof v === 'bigint' ? v.toString() : v, 2);
    console.log('📋 Full result:', safeStringify(result));
    
    console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ BRIDGE COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
    
    // Log transaction steps
    if (result.steps) {
      for (const step of result.steps) {
        const status = step.state === 'success' ? '✅' : '❌';
        console.log(`${status} ${step.name}: ${step.txHash || 'N/A'}`);
        if (step.data?.explorerUrl) {
          console.log(`   Explorer: ${step.data.explorerUrl}`);
        }
      }
    }
    
    console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
    
  } catch (e) {
    console.error(`\n❌ Bridge failed: ${e.message}`);
    if (e.message.includes('insufficient')) {
      console.error('   Make sure you have enough USDC and native tokens for gas.');
    }
    process.exit(1);
  }
}

function showChains() {
  console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 SUPPORTED CHAINS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Chain      | Native | USDC Contract
-----------|--------|------------------------------------------`);
  
  for (const [key, chain] of Object.entries(CHAINS)) {
    console.log(`${chain.name.padEnd(10)} | ${chain.native.padEnd(6)} | ${chain.usdc}`);
  }
  
  console.log(`
Network: ${NETWORK.toUpperCase()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
}

function showHelp() {
  console.log(`
AgentWallet - Multi-chain wallet for AI agents

COMMANDS:
  create              Generate new wallet (shows seed phrase once)
  addresses           Show your wallet addresses
  balance [chain]     Check balances (all chains or specific)
  transfer <chain> <token> <amount> <recipient>
                      Transfer tokens (same chain)
  bridge <from> <to> <amount>
                      Bridge USDC cross-chain (Circle CCTP V2)
  chains              List supported chains

EXAMPLES:
  node wallet.js create
  node wallet.js addresses
  node wallet.js balance
  node wallet.js balance solana
  node wallet.js transfer solana USDC 10 7xK9fR2nQp...
  node wallet.js transfer base ETH 0.01 0x7a3B9c...
  node wallet.js bridge base solana 10
  node wallet.js bridge ethereum base 50

ENVIRONMENT:
  WALLET_SEED_PHRASE  Your 12 or 24 word seed phrase
  NETWORK             testnet (default) or mainnet
  SOLANA_RPC          Custom Solana RPC endpoint
  BASE_RPC            Custom Base RPC endpoint
  ETH_RPC             Custom Ethereum RPC endpoint
`);
}

// ============ CLI ============

const [,, command, ...args] = process.argv;

switch (command) {
  case 'create':
    createWallet();
    break;
  case 'addresses':
  case 'address':
    showAddresses();
    break;
  case 'balance':
  case 'balances':
    checkBalance(args[0]);
    break;
  case 'transfer':
  case 'send':
    if (args.length < 4) {
      console.error('Usage: transfer <chain> <token> <amount> <recipient>');
      process.exit(1);
    }
    transfer(args[0], args[1], args[2], args[3]);
    break;
  case 'bridge':
    if (args.length < 3) {
      console.error('Usage: bridge <from-chain> <to-chain> <amount>');
      console.error('Example: bridge base solana 10');
      process.exit(1);
    }
    bridge(args[0], args[1], args[2]);
    break;
  case 'chains':
    showChains();
    break;
  case 'help':
  case '--help':
  case '-h':
  default:
    showHelp();
    break;
}
