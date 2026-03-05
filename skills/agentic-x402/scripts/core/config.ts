import { config as dotenvConfig } from 'dotenv';
import { resolve } from 'path';
import { existsSync } from 'fs';
import { homedir } from 'os';

// Load environment variables from multiple locations
function loadEnvFiles() {
  const cwd = process.env.X402_CWD || process.cwd();
  const globalConfigDir = resolve(homedir(), '.x402');

  // Priority: env vars > local .env > global ~/.x402/.env
  const envPaths = [
    resolve(globalConfigDir, '.env'),
    resolve(cwd, '.env'),
  ];

  for (const envPath of envPaths) {
    if (existsSync(envPath)) {
      dotenvConfig({ path: envPath, override: false });
    }
  }
}

loadEnvFiles();

export interface X402Config {
  // Wallet
  evmPrivateKey: `0x${string}`;

  // Network
  network: 'mainnet' | 'testnet';
  chainId: number;

  // Facilitator
  facilitatorUrl: string;

  // 21cash integration (optional)
  x402LinksApiUrl?: string;

  // Defaults
  maxPaymentUsd: number;
  slippageBps: number;
  verbose: boolean;
}

function getRequiredEnv(key: string): string {
  const value = process.env[key];
  if (!value) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
  return value;
}

function getOptionalEnv(key: string, defaultValue: string): string {
  return process.env[key] || defaultValue;
}

export function getConfig(): X402Config {
  const network = getOptionalEnv('X402_NETWORK', 'mainnet') as 'mainnet' | 'testnet';

  // Chain IDs: Base mainnet = 8453, Base Sepolia = 84532
  const chainId = network === 'mainnet' ? 8453 : 84532;

  // Facilitator URLs
  const defaultFacilitator = network === 'mainnet'
    ? 'https://api.cdp.coinbase.com/platform/v2/x402'
    : 'https://x402.org/facilitator';

  return {
    evmPrivateKey: getRequiredEnv('EVM_PRIVATE_KEY') as `0x${string}`,
    network,
    chainId,
    facilitatorUrl: getOptionalEnv('X402_FACILITATOR_URL', defaultFacilitator),
    x402LinksApiUrl: process.env.X402_LINKS_API_URL || 'https://21.cash',
    maxPaymentUsd: parseFloat(getOptionalEnv('X402_MAX_PAYMENT_USD', '10')),
    slippageBps: parseInt(getOptionalEnv('X402_SLIPPAGE_BPS', '50'), 10),
    verbose: getOptionalEnv('X402_VERBOSE', '0') === '1',
  };
}

// Network identifier in CAIP-2 format
export function getNetworkId(config: X402Config): string {
  return `eip155:${config.chainId}`;
}

// USDC contract addresses
export const USDC_ADDRESSES: Record<number, `0x${string}`> = {
  8453: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',   // Base mainnet
  84532: '0x036CbD53842c5426634e7929541eC2318f3dCF7e', // Base Sepolia
};

export function getUsdcAddress(chainId: number): `0x${string}` {
  const address = USDC_ADDRESSES[chainId];
  if (!address) {
    throw new Error(`USDC not supported on chain ${chainId}`);
  }
  return address;
}
