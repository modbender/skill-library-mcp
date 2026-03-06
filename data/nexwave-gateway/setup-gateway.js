import "dotenv/config";
import {
  createPublicClient,
  getContract,
  http,
  erc20Abi,
  defineChain,
} from "viem";
import * as chains from "viem/chains";
import { GatewayClient } from "./gateway-client.js";
import { CircleWalletClient } from "./circle-wallet-client.js";
import { gatewayWalletAbi, gatewayMinterAbi } from "./abis.js";

///////////////////////////////////////////////////////////////////////////////
// Chain configuration for Circle Gateway testnet
// Uses Circle Programmable Wallets for secure MPC-based key management.
// No raw private keys — the Circle SDK handles signing via API.

const gatewayWalletAddress = "0x0077777d7EBA4688BDeF3E311b846F25870A19B9";
const gatewayMinterAddress = "0x0022222ABE238Cc2C7Bb1f21003F0a260052475B";

export const usdcAddresses = {
  sepolia: "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
  baseSepolia: "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
  arcTestnet: "0x3600000000000000000000000000000000000000",
};

export { gatewayWalletAddress, gatewayMinterAddress };

// Arc Testnet is not in viem's built-in chains, so we define it manually.
// Arc is Circle's purpose-built L1 where USDC is the native gas token.
const arcTestnet = defineChain({
  id: 5042002,
  name: "Arc Testnet",
  nativeCurrency: { name: "USDC", symbol: "USDC", decimals: 18 },
  rpcUrls: {
    default: { http: ["https://rpc.testnet.arc.network"] },
  },
  blockExplorers: {
    default: { name: "ArcScan", url: "https://testnet.arcscan.app" },
  },
  testnet: true,
});

function setup(chainName) {
  const chain = chainName === "arcTestnet" ? arcTestnet : chains[chainName];
  const client = createPublicClient({
    chain,
    transport:
      chainName === "baseSepolia"
        ? http("https://sepolia-preconf.base.org")
        : chainName === "arcTestnet"
          ? http("https://rpc.testnet.arc.network")
          : http(),
  });

  return {
    client,
    chainName, // Internal key used by CircleWalletClient
    name: chain.name,
    domain: GatewayClient.DOMAINS[chainName],
    currency: chain.nativeCurrency.symbol,
    usdcAddress: usdcAddresses[chainName],
    gatewayWalletAddress,
    gatewayMinterAddress,
    usdc: getContract({
      address: usdcAddresses[chainName],
      abi: erc20Abi,
      client,
    }),
    gatewayWallet: getContract({
      address: gatewayWalletAddress,
      abi: gatewayWalletAbi,
      client,
    }),
    gatewayMinter: getContract({
      address: gatewayMinterAddress,
      abi: gatewayMinterAbi,
      client,
    }),
  };
}

// Initialize Circle Programmable Wallet (MPC-secured, no raw private keys)
export const circleWallet = await new CircleWalletClient().init();
export const walletAddress = circleWallet.address;

// Initialize read-only clients for each testnet chain
export const ethereum = setup("sepolia");
export const base = setup("baseSepolia");
export const arc = setup("arcTestnet");
