import { ethers } from 'ethers';
import * as bitcoin from 'bitcoinjs-lib';
import * as ecc from '@bitcoinerlab/secp256k1';
import { ECPairFactory } from 'ecpair';
import { config } from './config.js';
import { logger } from './logger.js';

// Initialize ECC library for Bitcoin
bitcoin.initEccLib(ecc);
const ECPair = ECPairFactory(ecc);

let evmWallet = null;
let btcKeyPair = null;
let btcAddress = null;

export function initializeWallets() {
  logger.info('Initializing wallets...');

  // Initialize EVM wallet
  const provider = new ethers.providers.JsonRpcProvider(config.evm.rpcUrl);
  evmWallet = new ethers.Wallet(config.evm.privateKey, provider);

  // Initialize BTC wallet
  const network = config.btc.network === 'mainnet' ? bitcoin.networks.bitcoin : bitcoin.networks.testnet;
  const btcPrivateKeyBuffer = Buffer.from(config.btc.privateKey, 'hex');
  btcKeyPair = ECPair.fromPrivateKey(btcPrivateKeyBuffer, { network });

  // Generate P2WPKH address (native segwit)
  const { address } = bitcoin.payments.p2wpkh({
    pubkey: btcKeyPair.publicKey,
    network
  });
  btcAddress = address;

  logger.success('Wallets initialized');
  logger.data('EVM Address', evmWallet.address);
  logger.data('BTC Address', btcAddress);
  logger.data('BTC Public Key', btcKeyPair.publicKey.toString('hex'));

  return {
    evmWallet,
    btcKeyPair,
    btcAddress
  };
}

export function getEVMWallet() {
  if (!evmWallet) {
    throw new Error('EVM wallet not initialized. Call initializeWallets() first.');
  }
  return evmWallet;
}

export function getBTCKeyPair() {
  if (!btcKeyPair) {
    throw new Error('BTC wallet not initialized. Call initializeWallets() first.');
  }
  return btcKeyPair;
}

export function getBTCAddress() {
  if (!btcAddress) {
    throw new Error('BTC wallet not initialized. Call initializeWallets() first.');
  }
  return btcAddress;
}

export function getBTCPublicKey() {
  if (!btcKeyPair) {
    throw new Error('BTC wallet not initialized. Call initializeWallets() first.');
  }
  return btcKeyPair.publicKey.toString('hex');
}

export function getBTCNetwork() {
  return config.btc.network === 'mainnet' ? bitcoin.networks.bitcoin : bitcoin.networks.testnet;
}
