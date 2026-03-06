/**
 * CLI configuration — loads from ~/.x402r/config.json, .env, and env vars.
 * Priority: env vars > .env > config file > arbiter auto-discovery > defaults
 */

import * as fs from "fs";
import * as path from "path";
import * as os from "os";

export interface CliConfigFile {
  privateKey?: string;
  operatorAddress?: string;
  arbiterUrl?: string;
  courtUrl?: string;
  networkId?: string;
  rpcUrl?: string;
  pinataJwt?: string;
}

interface ArbiterContracts {
  chainId: number;
  rpcUrl: string;
  operatorAddress: string | null;
}

const CONFIG_DIR = path.join(os.homedir(), ".x402r");
const CONFIG_FILE = path.join(CONFIG_DIR, "config.json");

/** Cache so we only fetch once per CLI invocation */
let arbiterContractsCache: ArbiterContracts | null = null;

/**
 * Fetch operator address, network, and RPC from the arbiter's /api/contracts endpoint.
 */
export async function fetchArbiterContracts(arbiterUrl: string): Promise<ArbiterContracts | null> {
  if (arbiterContractsCache) return arbiterContractsCache;
  try {
    const res = await fetch(`${arbiterUrl}/api/contracts`, { signal: AbortSignal.timeout(5000) });
    if (!res.ok) return null;
    const data = (await res.json()) as ArbiterContracts;
    arbiterContractsCache = data;
    return data;
  } catch {
    return null;
  }
}

/**
 * Load config from ~/.x402r/config.json
 */
export function loadConfigFile(): CliConfigFile {
  if (!fs.existsSync(CONFIG_FILE)) {
    return {};
  }
  try {
    return JSON.parse(fs.readFileSync(CONFIG_FILE, "utf-8"));
  } catch {
    return {};
  }
}

/**
 * Save config to ~/.x402r/config.json
 */
export function saveConfigFile(config: CliConfigFile): void {
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
  }
  // Merge with existing config
  const existing = loadConfigFile();
  const merged = { ...existing, ...config };
  // Remove undefined/null values
  for (const key of Object.keys(merged)) {
    if (merged[key as keyof CliConfigFile] === undefined || merged[key as keyof CliConfigFile] === null) {
      delete merged[key as keyof CliConfigFile];
    }
  }
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(merged, null, 2));
}

/**
 * Get resolved config: env vars > .env > config file > defaults
 */
export function getConfig(): Required<Pick<CliConfigFile, "networkId" | "arbiterUrl">> & CliConfigFile {
  const file = loadConfigFile();

  return {
    privateKey: process.env.PRIVATE_KEY || file.privateKey,
    operatorAddress: process.env.OPERATOR_ADDRESS || file.operatorAddress,
    arbiterUrl: process.env.ARBITER_URL || file.arbiterUrl || "http://localhost:3000",
    courtUrl: process.env.COURT_URL || file.courtUrl,
    networkId: process.env.NETWORK_ID || file.networkId || "eip155:11155111",
    rpcUrl: process.env.RPC_URL || file.rpcUrl,
    pinataJwt: process.env.PINATA_JWT || file.pinataJwt,
  };
}

/**
 * Get resolved config with auto-discovery from arbiter.
 * Falls back to local config if arbiter is unreachable.
 */
export async function getConfigWithDiscovery(): Promise<Required<Pick<CliConfigFile, "networkId" | "arbiterUrl">> & CliConfigFile> {
  const config = getConfig();

  // If operator or network are already set locally, skip discovery
  if (config.operatorAddress && config.networkId !== "eip155:11155111") {
    return config;
  }

  const contracts = await fetchArbiterContracts(config.arbiterUrl);
  if (contracts) {
    if (!config.operatorAddress && contracts.operatorAddress) {
      config.operatorAddress = contracts.operatorAddress;
    }
    if (contracts.chainId) {
      config.networkId = `eip155:${contracts.chainId}`;
    }
    if (!config.rpcUrl && contracts.rpcUrl) {
      config.rpcUrl = contracts.rpcUrl;
    }
  }

  return config;
}

/**
 * Print current config (masked key)
 */
export async function printConfig(): Promise<void> {
  const config = await getConfigWithDiscovery();
  console.log("\n=== x402r CLI Config ===");
  console.log("  Private Key:", config.privateKey ? `${config.privateKey.slice(0, 6)}...${config.privateKey.slice(-4)}` : "(not set)");
  console.log("  Operator:", config.operatorAddress || "(not set)");
  console.log("  Arbiter URL:", config.arbiterUrl);
  console.log("  Court URL:", config.courtUrl || "(not set)");
  console.log("  Network:", config.networkId);
  console.log("  RPC URL:", config.rpcUrl || "(chain default)");
  console.log("  Pinata JWT:", config.pinataJwt ? `${config.pinataJwt.slice(0, 12)}...` : "(not set)");
  console.log(`\n  Config file: ${CONFIG_FILE}`);
}
