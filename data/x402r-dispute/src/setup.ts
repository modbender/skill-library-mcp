/**
 * CLI setup — creates viem clients from resolved config.
 * Ported from x402r-sdk/examples/dev-tools/shared/cli-setup.ts with config file support.
 */

import {
  createPublicClient,
  createWalletClient,
  http,
  type PublicClient,
  type WalletClient,
  type Chain,
} from "viem";
import { baseSepolia, base, sepolia } from "viem/chains";
import { privateKeyToAccount, type PrivateKeyAccount } from "viem/accounts";
import { resolveAddresses, type ResolvedAddresses } from "@x402r/core";
import { getConfig, getConfigWithDiscovery } from "./config.js";

const CHAINS: Record<number, Chain> = {
  84532: baseSepolia,
  8453: base,
  11155111: sepolia,
};

export interface CliSetup {
  account: PrivateKeyAccount;
  publicClient: PublicClient;
  walletClient: WalletClient;
  networkId: string;
  addresses: ResolvedAddresses;
  operatorAddress: `0x${string}`;
  arbiterUrl: string;
}

/**
 * Initialize CLI: validates config, creates viem clients.
 * Auto-discovers operator and network from arbiter if not set locally.
 */
export async function initCli(): Promise<CliSetup> {
  const config = await getConfigWithDiscovery();

  if (!config.privateKey) {
    console.error("Error: Private key not configured.");
    console.error("Run: x402r config --key 0x...");
    process.exit(1);
  }

  if (!config.operatorAddress) {
    console.error("Error: Operator address not configured.");
    console.error("Run: x402r config --operator 0x...");
    process.exit(1);
  }

  const account = privateKeyToAccount(config.privateKey as `0x${string}`);
  const addresses = resolveAddresses(config.networkId);

  const chainId = addresses.chainId;
  const chain = CHAINS[chainId];
  if (!chain) {
    console.error(`Unsupported chain ID: ${chainId} (network: ${config.networkId})`);
    process.exit(1);
  }

  const rpcUrl = config.rpcUrl?.startsWith("http") ? config.rpcUrl : undefined;
  const transport = http(rpcUrl);

  const publicClient = createPublicClient({ chain, transport });
  const walletClient = createWalletClient({ account, chain, transport });

  return {
    account,
    publicClient,
    walletClient,
    networkId: config.networkId,
    addresses,
    operatorAddress: config.operatorAddress as `0x${string}`,
    arbiterUrl: config.arbiterUrl,
  };
}

/**
 * Read-only setup — no private key required.
 * Auto-discovers operator and network from arbiter if not set locally.
 */
export async function initReadOnly(): Promise<Pick<CliSetup, "publicClient" | "networkId" | "addresses" | "arbiterUrl" | "operatorAddress">> {
  const config = await getConfigWithDiscovery();
  const addresses = resolveAddresses(config.networkId);

  const chainId = addresses.chainId;
  const chain = CHAINS[chainId];
  if (!chain) {
    console.error(`Unsupported chain ID: ${chainId}`);
    process.exit(1);
  }

  const rpcUrl = config.rpcUrl?.startsWith("http") ? config.rpcUrl : undefined;
  const publicClient = createPublicClient({ chain, transport: http(rpcUrl) });

  return {
    publicClient,
    networkId: config.networkId,
    addresses,
    arbiterUrl: config.arbiterUrl,
    operatorAddress: (config.operatorAddress || "0x0000000000000000000000000000000000000000") as `0x${string}`,
  };
}
