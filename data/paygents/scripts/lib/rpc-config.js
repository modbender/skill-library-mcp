// RPC resolution order:
// 1. Environment variable: RPC_<chainId> (e.g. RPC_1, RPC_8453)
// 2. Config file: config.json in skill root
// 3. Public fallbacks (last resort)

const fs = require("fs");
const path = require("path");

const PUBLIC_FALLBACKS = {
  "1":        "https://eth.llamarpc.com",
  "8453":     "https://mainnet.base.org",
  "137":      "https://polygon-rpc.com",
  "42161":    "https://arb1.arbitrum.io/rpc",
  "10":       "https://mainnet.optimism.io",
  "56":       "https://bsc-dataseed.binance.org",
  "11155111": "https://rpc.sepolia.org",
  "84532":    "https://sepolia.base.org",
};

const CHAIN_META = {
  "1":        { name: "Ethereum",     symbol: "ETH", explorer: "https://etherscan.io" },
  "8453":     { name: "Base",         symbol: "ETH", explorer: "https://basescan.org" },
  "137":      { name: "Polygon",      symbol: "POL", explorer: "https://polygonscan.com" },
  "42161":    { name: "Arbitrum",     symbol: "ETH", explorer: "https://arbiscan.io" },
  "10":       { name: "Optimism",     symbol: "ETH", explorer: "https://optimistic.etherscan.io" },
  "56":       { name: "BNB Chain",    symbol: "BNB", explorer: "https://bscscan.com" },
  "11155111": { name: "Sepolia",      symbol: "ETH", explorer: "https://sepolia.etherscan.io" },
  "84532":    { name: "Base Sepolia", symbol: "ETH", explorer: "https://sepolia.basescan.org" },
};

function loadConfig() {
  // Look for config.json in skill root (parent of scripts/)
  const candidates = [
    path.resolve(__dirname, "../../config.json"),
    path.resolve(process.cwd(), "config.json"),
  ];
  for (const p of candidates) {
    try {
      if (fs.existsSync(p)) {
        return JSON.parse(fs.readFileSync(p, "utf8"));
      }
    } catch { /* skip */ }
  }
  return {};
}

let _config = null;
function getConfig() {
  if (!_config) _config = loadConfig();
  return _config;
}

function getRpc(chainId) {
  const id = String(chainId);

  // 1. Env var: RPC_1, RPC_8453, etc.
  const envKey = `RPC_${id}`;
  if (process.env[envKey]) return process.env[envKey];

  // 2. Config file
  const cfg = getConfig();
  if (cfg.rpc && cfg.rpc[id]) return cfg.rpc[id];

  // 3. Public fallback
  if (PUBLIC_FALLBACKS[id]) return PUBLIC_FALLBACKS[id];

  return null;
}

function getChainMeta(chainId) {
  return CHAIN_META[String(chainId)] || null;
}

function getExplorerTxUrl(chainId, txHash) {
  const meta = getChainMeta(chainId);
  if (!meta) return null;
  return `${meta.explorer}/tx/${txHash}`;
}

function getExplorerAddressUrl(chainId, address) {
  const meta = getChainMeta(chainId);
  if (!meta) return null;
  return `${meta.explorer}/address/${address}`;
}

function isUsingPublicRpc(chainId) {
  const id = String(chainId);
  const envKey = `RPC_${id}`;
  if (process.env[envKey]) return false;
  const cfg = getConfig();
  if (cfg.rpc && cfg.rpc[id]) return false;
  return true;
}

module.exports = { getRpc, getChainMeta, getExplorerTxUrl, getExplorerAddressUrl, isUsingPublicRpc, PUBLIC_FALLBACKS, CHAIN_META };
