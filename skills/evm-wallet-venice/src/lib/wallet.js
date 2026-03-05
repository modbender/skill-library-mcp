/**
 * Wallet state management
 * Handles wallet generation, loading, saving, and client creation
 */

import { existsSync, readFileSync, writeFileSync, chmodSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';
import { createWalletClient, http } from 'viem';
import { privateKeyToAccount, generatePrivateKey } from 'viem/accounts';
import { getChain } from './chains.js';

// Wallet lives in user's home directory — never in the project
const WALLET_PATH = join(homedir(), '.evm-wallet.json');

/**
 * Generate a new wallet
 * @returns {Object} Wallet object with address and private key
 */
export function generate() {
  const privateKey = generatePrivateKey();
  const account = privateKeyToAccount(privateKey);
  
  return {
    address: account.address,
    privateKey,
    createdAt: new Date().toISOString()
  };
}

/**
 * Load wallet from state file
 * @returns {Object|null} Wallet object or null if no wallet exists
 */
export function load() {
  try {
    if (!existsSync(WALLET_PATH)) {
      return null;
    }
    
    const data = readFileSync(WALLET_PATH, 'utf8');
    const wallet = JSON.parse(data);
    
    // Validate wallet structure
    if (!wallet.privateKey || !wallet.address) {
      throw new Error('Invalid wallet file: missing required fields');
    }
    
    return wallet;
  } catch (error) {
    throw new Error(`Failed to load wallet: ${error.message}`);
  }
}

/**
 * Save wallet to state file with secure permissions
 * @param {Object} wallet - Wallet object to save
 */
export function save(wallet) {
  try {
    const data = JSON.stringify(wallet, null, 2);
    writeFileSync(WALLET_PATH, data, 'utf8');
    
    // Set secure permissions (owner read/write only)
    chmodSync(WALLET_PATH, 0o600);
  } catch (error) {
    throw new Error(`Failed to save wallet: ${error.message}`);
  }
}

/**
 * Get viem account from stored wallet
 * @returns {Object} Viem account object
 */
export function getAccount() {
  const wallet = load();
  if (!wallet) {
    throw new Error('No wallet found. Run setup.js first to generate a wallet.');
  }
  
  return privateKeyToAccount(wallet.privateKey);
}

/**
 * Get wallet address
 * @returns {string} Wallet address
 */
export function getAddress() {
  const wallet = load();
  if (!wallet) {
    throw new Error('No wallet found. Run setup.js first to generate a wallet.');
  }
  
  return wallet.address;
}

/**
 * Create viem wallet client for a specific chain
 * @param {string} chainName - Chain name
 * @returns {Object} Viem wallet client
 */
export function getWalletClient(chainName) {
  const chain = getChain(chainName);
  const account = getAccount();
  
  // Create viem chain config
  const viemChain = {
    id: chain.chainId,
    name: chain.name,
    nativeCurrency: {
      name: chain.nativeToken.symbol,
      symbol: chain.nativeToken.symbol,
      decimals: chain.nativeToken.decimals
    },
    rpcUrls: {
      default: { http: chain.rpcs },
      public: { http: chain.rpcs }
    },
    blockExplorers: {
      default: {
        name: chain.explorer.name,
        url: chain.explorer.url
      }
    }
  };
  
  return createWalletClient({
    account,
    chain: viemChain,
    transport: http(chain.rpcs[0], {
      retryCount: 3,
      timeout: 30_000
    })
  });
}

/**
 * Check if wallet exists
 * @returns {boolean} True if wallet exists
 */
export function exists() {
  return existsSync(WALLET_PATH);
}

/**
 * Get wallet info (safe - no private key)
 * @returns {Object} Wallet info without private key
 */
export function getWalletInfo() {
  const wallet = load();
  if (!wallet) {
    return null;
  }
  
  return {
    address: wallet.address,
    createdAt: wallet.createdAt
  };
}