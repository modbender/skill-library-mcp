#!/usr/bin/env node

/**
 * PayTheFlyPro - Payment Link Generator
 * Creates signed payment URLs for crypto payments
 */

import { Wallet, parseUnits } from 'ethers';

// =============================================================================
// Configuration
// =============================================================================

const BASE_URL = 'https://pro.paythefly.com';
const NATIVE_TOKEN_ADDRESS = '0x0000000000000000000000000000000000000000';

const CHAIN_CONFIG = {
  56: { name: 'BSC Mainnet', decimals: 18, domainChainId: 56 },
  97: { name: 'BSC Testnet', decimals: 18, domainChainId: 97 },
  1: { name: 'Ethereum', decimals: 18, domainChainId: 1 },
  'tron:mainnet': { name: 'TRON Mainnet', decimals: 6, domainChainId: 728126428, urlChainId: 728126428 },
  'tron:nile': { name: 'TRON Nile', decimals: 6, domainChainId: 3448148188, urlChainId: 3448148188 },
};

const PAYMENT_REQUEST_TYPES = {
  PaymentRequest: [
    { name: 'projectId', type: 'string' },
    { name: 'token', type: 'address' },
    { name: 'amount', type: 'uint256' },
    { name: 'serialNo', type: 'string' },
    { name: 'deadline', type: 'uint256' },
  ],
};

// =============================================================================
// Helpers
// =============================================================================

function usage() {
  console.error(`Usage: payment.mjs --amount <value> --serialNo <value> [options]

Required:
  --amount <value>      Payment amount (e.g., "0.01", "100")
  --serialNo <value>    Unique order serial number

Optional:
  --token <address>     Token contract address (omit for native token)
  --redirect <url>      URL to redirect after payment
  --brand <name>        Custom brand name
  --lang <code>         UI language (en, zh, ko, ja)
  --deadline <hours>    Signature validity hours (default: 24)
  --in_wallet           Prioritize wallet app button

Environment variables required:
  PTF_PROJECT_ID        PayTheFlyPro project identifier
  PTF_CONTRACT_ADDRESS  Project smart contract address
  PTF_SIGNER_KEY        Private key for EIP-712 signing
  PTF_CHAIN_ID          Chain ID (56, 97, 1, tron:mainnet, tron:nile)`);
  process.exit(2);
}

function parseArgs(args) {
  const result = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '-h' || arg === '--help') usage();
    if (arg === '--in_wallet') {
      result.in_wallet = true;
      continue;
    }
    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      const value = args[i + 1];
      if (!value || value.startsWith('--')) {
        console.error(`Missing value for ${arg}`);
        usage();
      }
      result[key] = value;
      i++;
    }
  }
  return result;
}

function getConfig() {
  const projectId = (process.env.PTF_PROJECT_ID ?? '').trim();
  const contractAddress = (process.env.PTF_CONTRACT_ADDRESS ?? '').trim();
  const signerKey = (process.env.PTF_SIGNER_KEY ?? '').trim();
  const chainIdRaw = (process.env.PTF_CHAIN_ID ?? '').trim();

  if (!projectId) throw new Error('Missing PTF_PROJECT_ID');
  if (!contractAddress) throw new Error('Missing PTF_CONTRACT_ADDRESS');
  if (!signerKey) throw new Error('Missing PTF_SIGNER_KEY');
  if (!chainIdRaw) throw new Error('Missing PTF_CHAIN_ID');

  // Parse chainId
  let chainId = chainIdRaw;
  if (/^\d+$/.test(chainIdRaw)) {
    chainId = parseInt(chainIdRaw, 10);
  }

  const chainConfig = CHAIN_CONFIG[chainId];
  if (!chainConfig) {
    throw new Error(`Unsupported chain: ${chainId}. Supported: 56, 97, 1, tron:mainnet, tron:nile`);
  }

  return { projectId, contractAddress, signerKey, chainId, chainConfig };
}

function isTronChain(chainId) {
  return typeof chainId === 'string' && chainId.startsWith('tron:');
}

async function tronAddressToHex(address) {
  if (!address.startsWith('T')) return address;
  // Dynamic import for TronWeb
  const TronWeb = (await import('tronweb')).default;
  const hexAddr = TronWeb.address.toHex(address);
  return '0x' + hexAddr.slice(2);
}

// =============================================================================
// Main
// =============================================================================

const args = process.argv.slice(2);
if (args.length === 0) usage();

const params = parseArgs(args);

// Validate required params
if (!params.amount) {
  console.error('Missing required parameter: --amount');
  usage();
}
if (!params.serialNo) {
  console.error('Missing required parameter: --serialNo');
  usage();
}

try {
  const config = getConfig();
  const { projectId, contractAddress, signerKey, chainId, chainConfig } = config;

  // Calculate deadline
  const deadlineHours = parseInt(params.deadline ?? '24', 10);
  const deadline = Math.floor(Date.now() / 1000) + deadlineHours * 60 * 60;

  // Token address
  const tokenAddress = params.token || NATIVE_TOKEN_ADDRESS;

  // Convert amount to raw units
  const decimals = chainConfig.decimals;
  const amountRaw = parseUnits(params.amount, decimals);

  // Build domain
  let verifyingContract = contractAddress;
  let tokenHex = tokenAddress;

  if (isTronChain(chainId)) {
    verifyingContract = await tronAddressToHex(contractAddress);
    if (tokenAddress !== NATIVE_TOKEN_ADDRESS) {
      tokenHex = await tronAddressToHex(tokenAddress);
    }
  }

  const domain = {
    name: 'PayTheFlyPro',
    version: '1',
    chainId: chainConfig.domainChainId,
    verifyingContract,
  };

  // Sign
  const normalizedKey = signerKey.startsWith('0x') ? signerKey : `0x${signerKey}`;
  const wallet = new Wallet(normalizedKey);

  const value = {
    projectId,
    token: tokenHex,
    amount: amountRaw,
    serialNo: params.serialNo,
    deadline,
  };

  const signature = await wallet.signTypedData(domain, PAYMENT_REQUEST_TYPES, value);

  // Build URL
  const urlChainId = chainConfig.urlChainId ?? chainId;
  const url = new URL(`${BASE_URL}/pay`);
  url.searchParams.set('chainId', String(urlChainId));
  url.searchParams.set('projectId', projectId);
  url.searchParams.set('amount', params.amount);
  url.searchParams.set('serialNo', params.serialNo);
  url.searchParams.set('deadline', String(deadline));
  url.searchParams.set('signature', signature);

  if (params.token) url.searchParams.set('token', params.token);
  if (params.redirect) url.searchParams.set('redirect', params.redirect);
  if (params.brand) url.searchParams.set('brand', params.brand);
  if (params.lang) url.searchParams.set('lang', params.lang);
  if (params.in_wallet) url.searchParams.set('in_wallet', '1');

  // Output
  console.log('## Payment Link Created\n');
  console.log(`- **Amount**: ${params.amount} ${params.token ? 'tokens' : chainConfig.name.includes('TRON') ? 'TRX' : chainConfig.name.includes('BSC') ? 'BNB' : 'ETH'}`);
  console.log(`- **Serial No**: ${params.serialNo}`);
  console.log(`- **Chain**: ${chainConfig.name}`);
  console.log(`- **Expires**: ${new Date(deadline * 1000).toISOString()}`);
  console.log(`\n**URL**:\n${url.toString()}`);

} catch (error) {
  console.error(`Error: ${error.message}`);
  process.exit(1);
}
