#!/usr/bin/env node

/**
 * PayTheFlyPro - Order Status Query
 * Query payment/withdrawal order status from blockchain
 */

import { Contract, JsonRpcProvider } from 'ethers';

// =============================================================================
// Configuration
// =============================================================================

const CHAIN_CONFIG = {
  56: {
    name: 'BSC Mainnet',
    rpcUrls: ['https://bsc-dataseed1.binance.org', 'https://bsc-dataseed2.binance.org'],
  },
  97: {
    name: 'BSC Testnet',
    rpcUrls: ['https://data-seed-prebsc-1-s1.binance.org:8545', 'https://data-seed-prebsc-2-s1.binance.org:8545'],
  },
  1: {
    name: 'Ethereum',
    rpcUrls: ['https://eth.llamarpc.com', 'https://rpc.ankr.com/eth'],
  },
  'tron:mainnet': {
    name: 'TRON Mainnet',
    rpcUrls: ['https://api.trongrid.io'],
    isTron: true,
  },
  'tron:nile': {
    name: 'TRON Nile',
    rpcUrls: ['https://nile.trongrid.io'],
    isTron: true,
  },
};

// Minimal ABI for status query
const CONTRACT_ABI = [
  'function isPaymentSerialNoUsed(string) view returns (bool)',
  'function isWithdrawalSerialNoUsed(string) view returns (bool)',
];

// =============================================================================
// Helpers
// =============================================================================

function usage() {
  console.error(`Usage: query.mjs --type <payment|withdrawal> --serialNo <value>

Required:
  --type <value>        Order type: "payment" or "withdrawal"
  --serialNo <value>    Serial number to query

Environment variables required:
  PTF_CONTRACT_ADDRESS  Project smart contract address
  PTF_CHAIN_ID          Chain ID (56, 97, 1, tron:mainnet, tron:nile)

Optional:
  PTF_CUSTOM_RPC        Custom RPC endpoint`);
  process.exit(2);
}

function parseArgs(args) {
  const result = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '-h' || arg === '--help') usage();
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
  const contractAddress = (process.env.PTF_CONTRACT_ADDRESS ?? '').trim();
  const chainIdRaw = (process.env.PTF_CHAIN_ID ?? '').trim();
  const customRpc = (process.env.PTF_CUSTOM_RPC ?? '').trim();

  if (!contractAddress) throw new Error('Missing PTF_CONTRACT_ADDRESS');
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

  return { contractAddress, chainId, chainConfig, customRpc };
}

async function queryEvmContract(contractAddress, rpcUrls, customRpc, type, serialNo) {
  const urls = customRpc ? [customRpc, ...rpcUrls] : rpcUrls;
  const errors = [];

  for (const rpcUrl of urls) {
    try {
      const provider = new JsonRpcProvider(rpcUrl, undefined, { staticNetwork: true });
      const contract = new Contract(contractAddress, CONTRACT_ABI, provider);

      // Query based on type (pass serialNo as string directly)
      let used;
      if (type === 'payment') {
        used = await contract.isPaymentSerialNoUsed(serialNo);
      } else {
        used = await contract.isWithdrawalSerialNoUsed(serialNo);
      }

      return { used, rpcUrl };
    } catch (error) {
      errors.push(`${rpcUrl}: ${error.message}`);
      continue;
    }
  }

  throw new Error(`All RPC endpoints failed:\n${errors.join('\n')}`);
}

async function queryTronContract(contractAddress, rpcUrls, customRpc, type, serialNo) {
  const TronWeb = (await import('tronweb')).default;
  const urls = customRpc ? [customRpc, ...rpcUrls] : rpcUrls;

  for (const rpcUrl of urls) {
    try {
      const tronWeb = new TronWeb({
        fullHost: rpcUrl,
      });

      const contract = await tronWeb.contract().at(contractAddress);

      // Query based on type (pass serialNo as string directly)
      let used;
      if (type === 'payment') {
        used = await contract.isPaymentSerialNoUsed(serialNo).call();
      } else {
        used = await contract.isWithdrawalSerialNoUsed(serialNo).call();
      }

      return { used, rpcUrl };
    } catch (error) {
      // Try next RPC
      continue;
    }
  }

  throw new Error('All RPC endpoints failed');
}

// =============================================================================
// Main
// =============================================================================

const args = process.argv.slice(2);
if (args.length === 0) usage();

const params = parseArgs(args);

// Validate required params
if (!params.type) {
  console.error('Missing required parameter: --type');
  usage();
}
if (!params.serialNo) {
  console.error('Missing required parameter: --serialNo');
  usage();
}
if (params.type !== 'payment' && params.type !== 'withdrawal') {
  console.error('Invalid --type. Must be "payment" or "withdrawal"');
  usage();
}

try {
  const config = getConfig();
  const { contractAddress, chainId, chainConfig, customRpc } = config;

  console.log(`## Querying ${params.type} status\n`);
  console.log(`- **Serial No**: ${params.serialNo}`);
  console.log(`- **Chain**: ${chainConfig.name}`);
  console.log(`- **Contract**: ${contractAddress}`);
  console.log('');

  let result;
  if (chainConfig.isTron) {
    result = await queryTronContract(
      contractAddress,
      chainConfig.rpcUrls,
      customRpc,
      params.type,
      params.serialNo
    );
  } else {
    result = await queryEvmContract(
      contractAddress,
      chainConfig.rpcUrls,
      customRpc,
      params.type,
      params.serialNo
    );
  }

  const status = result.used ? 'confirmed' : 'not_found';
  const statusDesc = result.used
    ? 'Serial number has been used (order completed)'
    : 'Serial number has not been used (order pending or not created)';

  console.log(`**Status**: ${status}`);
  console.log(`**Description**: ${statusDesc}`);

} catch (error) {
  console.error(`Error: ${error.message}`);
  process.exit(1);
}
