import { privateKeyToAccount, type PrivateKeyAccount } from 'viem/accounts';
import { createPublicClient, createWalletClient, http, formatUnits, type PublicClient, type WalletClient } from 'viem';
import { base, baseSepolia } from 'viem/chains';
import { wrapFetchWithPayment } from '@x402/fetch';
import { x402Client, x402HTTPClient } from '@x402/core/client';
import { registerExactEvmScheme } from '@x402/evm/exact/client';
import { getConfig, getUsdcAddress, type X402Config } from './config.js';

export interface X402ClientWrapper {
  config: X402Config;
  account: PrivateKeyAccount;
  x402: x402Client;
  httpClient: x402HTTPClient;
  fetchWithPayment: typeof fetch;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  publicClient: PublicClient<any, any>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  walletClient: WalletClient<any, any, any>;
}

let clientInstance: X402ClientWrapper | null = null;

export function getClient(): X402ClientWrapper {
  if (clientInstance) {
    return clientInstance;
  }

  const config = getConfig();

  // Create viem account from private key
  const account = privateKeyToAccount(config.evmPrivateKey);

  // Select chain
  const chain = config.network === 'mainnet' ? base : baseSepolia;

  // Create viem clients
  const publicClient = createPublicClient({
    chain,
    transport: http(),
  });

  const walletClient = createWalletClient({
    account,
    chain,
    transport: http(),
  });

  // Create x402 client and register EVM scheme
  const x402 = new x402Client();
  registerExactEvmScheme(x402, { signer: account });

  // Create HTTP client wrapper
  const httpClient = new x402HTTPClient(x402);

  // Wrap fetch with payment handling
  const fetchWithPayment = wrapFetchWithPayment(fetch, x402);

  const wrapper: X402ClientWrapper = {
    config,
    account,
    x402,
    httpClient,
    fetchWithPayment,
    publicClient,
    walletClient,
  };

  clientInstance = wrapper;
  return wrapper;
}

// Get wallet address
export function getWalletAddress(): `0x${string}` {
  const client = getClient();
  return client.account.address;
}

// Get USDC balance
export async function getUsdcBalance(): Promise<{ raw: bigint; formatted: string }> {
  const client = getClient();
  const usdcAddress = getUsdcAddress(client.config.chainId);

  // USDC has 6 decimals
  const balance = await client.publicClient.readContract({
    address: usdcAddress,
    abi: [{
      name: 'balanceOf',
      type: 'function',
      stateMutability: 'view',
      inputs: [{ name: 'account', type: 'address' }],
      outputs: [{ name: '', type: 'uint256' }],
    }],
    functionName: 'balanceOf',
    args: [client.account.address],
  });

  return {
    raw: balance,
    formatted: formatUnits(balance, 6),
  };
}

// Get ETH balance (for gas)
export async function getEthBalance(): Promise<{ raw: bigint; formatted: string }> {
  const client = getClient();
  const balance = await client.publicClient.getBalance({
    address: client.account.address,
  });

  return {
    raw: balance,
    formatted: formatUnits(balance, 18),
  };
}
