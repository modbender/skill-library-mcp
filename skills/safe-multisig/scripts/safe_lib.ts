import { Command } from 'commander';
import { getAddress, isHexString } from 'ethers';

// ── Types ──

export interface CommonOptions {
  chain?: string;
  txServiceUrl?: string;
  rpcUrl?: string;
  apiKey?: string;
  debug?: boolean;
}

export interface SafeOptions extends CommonOptions {
  safe?: string;
}

export interface TxHashOptions extends SafeOptions {
  safeTxHash?: string;
}

export interface TxFileOptions extends CommonOptions {
  txFile?: string;
}

export interface ListOptions extends SafeOptions {
  limit?: string;
  offset?: string;
  executed?: string;
}

// ── Chain Configuration ──

// Chain slug → default public RPC URLs
const DEFAULT_RPCS: Record<string, string> = {
  mainnet: 'https://eth.llamarpc.com', ethereum: 'https://eth.llamarpc.com',
  optimism: 'https://mainnet.optimism.io', 'op-mainnet': 'https://mainnet.optimism.io',
  bsc: 'https://bsc-dataseed.binance.org', gnosis: 'https://rpc.gnosischain.com',
  polygon: 'https://polygon-rpc.com', base: 'https://mainnet.base.org',
  arbitrum: 'https://arb1.arbitrum.io/rpc', 'arbitrum-one': 'https://arb1.arbitrum.io/rpc',
  avalanche: 'https://api.avax.network/ext/bc/C/rpc', sepolia: 'https://rpc.sepolia.org',
  'base-sepolia': 'https://sepolia.base.org', 'optimism-sepolia': 'https://sepolia.optimism.io',
  'arbitrum-sepolia': 'https://sepolia-rollup.arbitrum.io/rpc'
};

// Chain slug → chainId mapping (common chains)
const CHAIN_IDS: Record<string, bigint> = {
  mainnet: 1n, ethereum: 1n,
  optimism: 10n, 'op-mainnet': 10n,
  bsc: 56n, gnosis: 100n,
  polygon: 137n, base: 8453n,
  arbitrum: 42161n, 'arbitrum-one': 42161n,
  avalanche: 43114n, sepolia: 11155111n,
  'base-sepolia': 84532n, 'optimism-sepolia': 11155420n,
  'arbitrum-sepolia': 421614n
};

// FIX SM-002: Chain slug → EIP-3770 short name for Safe Transaction Service URLs
// Verified live against https://api.safe.global/tx-service/{slug}/api/v1/about/
const CHAIN_SHORT_NAMES: Record<string, string> = {
  mainnet: 'eth', ethereum: 'eth',
  optimism: 'oeth', 'op-mainnet': 'oeth',
  bsc: 'bnb', gnosis: 'gno',
  polygon: 'pol', base: 'base',
  arbitrum: 'arb1', 'arbitrum-one': 'arb1',
  avalanche: 'avax', sepolia: 'sep',
  'base-sepolia': 'basesep', 'optimism-sepolia': 'osep',
  'arbitrum-sepolia': 'arbsep'
};

// ── Helpers ──

export function addCommonOptions(cmd: Command): Command {
  return cmd
    .option('--chain <slug>', 'Safe tx-service chain slug (e.g. base, base-sepolia, mainnet)')
    .option('--tx-service-url <url>', 'Override tx-service base URL')
    .option('--rpc-url <url>', 'RPC URL (required for signing/executing)', process.env.RPC_URL)
    .option('--api-key <key>', 'Safe Transaction Service API key', process.env.SAFE_TX_SERVICE_API_KEY)
    .option('--debug', 'Verbose logging');
}

/**
 * FIX SM-001 + SM-002: Resolve the transaction service URL.
 * Appends /api suffix and uses correct EIP-3770 short names.
 */
export function resolveTxServiceUrl(opts: CommonOptions): string {
  if (opts.txServiceUrl) return opts.txServiceUrl.replace(/\/$/, '');
  if (!opts.chain) throw new Error('Missing --chain or --tx-service-url');

  const slug = opts.chain.toLowerCase();
  const shortName = CHAIN_SHORT_NAMES[slug];
  if (!shortName) {
    throw new Error(
      `Unknown chain slug "${opts.chain}" for Safe Transaction Service. ` +
      `Known: ${Object.keys(CHAIN_SHORT_NAMES).join(', ')}`
    );
  }
  // FIX SM-001: Use api.safe.global gateway with /api suffix
  // The per-chain subdomains (safe-transaction-{slug}.safe.global) are deprecated.
  // The unified gateway at api.safe.global is the current standard.
  return `https://api.safe.global/tx-service/${shortName}/api`;
}

export function resolveChainId(opts: CommonOptions): bigint {
  if (opts.chain) {
    const id = CHAIN_IDS[opts.chain.toLowerCase()];
    if (!id) throw new Error(`Unknown chain slug "${opts.chain}". Known: ${Object.keys(CHAIN_IDS).join(', ')}`);
    return id;
  }
  throw new Error('Missing --chain (needed to resolve chainId)');
}

export function resolveRpcUrl(opts: CommonOptions): string {
  if (opts.rpcUrl) return opts.rpcUrl;
  if (process.env.RPC_URL) return process.env.RPC_URL;
  if (opts.chain) {
    const url = DEFAULT_RPCS[opts.chain.toLowerCase()];
    if (url) return url;
    throw new Error(`No default RPC URL for chain "${opts.chain}". Pass --rpc-url explicitly.`);
  }
  throw new Error('Missing --rpc-url or --chain (needed to resolve RPC URL)');
}

export function requirePrivateKey(): string {
  const pk = process.env.SAFE_SIGNER_PRIVATE_KEY;
  if (!pk) throw new Error('Missing SAFE_SIGNER_PRIVATE_KEY env var');
  return pk.startsWith('0x') ? pk : `0x${pk}`;
}

// FIX SM-006: Validate Ethereum addresses
export function validateAddress(addr: string, label: string): void {
  try {
    getAddress(addr);
  } catch {
    throw new Error(`Invalid ${label} address: "${addr}"`);
  }
}

export function validateTxHash(hash: string, label = 'safeTxHash'): void {
  if (!isHexString(hash, 32)) {
    throw new Error(`Invalid ${label}: "${hash}". Expected 0x-prefixed 32-byte hex.`);
  }
}

// FIX SM-004: Validate API key is present when using official service
export function validateApiKey(opts: CommonOptions): void {
  const isOfficialService = !opts.txServiceUrl ||
    opts.txServiceUrl.includes('safe.global') ||
    opts.txServiceUrl.includes('5afe.dev');
  if (isOfficialService && !opts.apiKey) {
    console.error(
      'WARNING: No API key provided. The Safe Transaction Service at safe.global ' +
      'requires an API key. Obtain one from https://developer.safe.global and pass ' +
      'via --api-key or SAFE_TX_SERVICE_API_KEY env var.'
    );
  }
}

interface FetchOptions {
  method?: string;
  headers?: Record<string, string>;
  body?: unknown;
  timeoutMs?: number;
}

export async function fetchJson<T = unknown>(url: string, options: FetchOptions = {}): Promise<T> {
  const { method = 'GET', headers = {}, body, timeoutMs = 30000 } = options;

  // FIX PT-008: Add timeout to prevent indefinite hangs
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(url, {
      method,
      headers: { 'content-type': 'application/json', ...headers },
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal
    });
    if (!res.ok) {
      const text = await res.text().catch(() => '');
      throw new Error(`HTTP ${res.status} ${res.statusText}: ${text.slice(0, 800)}`);
    }
    return (await res.json()) as T;
  } finally {
    clearTimeout(timer);
  }
}

export function createCommand(name: string, description: string): Command {
  const c = new Command();
  c.name(name);
  c.description(description);
  c.showHelpAfterError(true);
  c.showSuggestionAfterError(true);
  return c;
}

// Alias for backward compat — old code used cmd()
export { createCommand as cmd };
