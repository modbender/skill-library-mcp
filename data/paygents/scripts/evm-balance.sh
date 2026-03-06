#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Check wallet balances via RPC. Returns native + major ERC20 token balances.
RPC resolution: env var RPC_<chainId> → config.json → public fallback.

Usage:
  evm-balance.sh --address <0x...> [--chain-id <id>] [--all]

Options:
  --address     Wallet address (required)
  --chain-id    Single chain to query (default: all supported)
  --all         Query all supported chains (default if no --chain-id)
USAGE
}

ADDRESS=""
CHAIN_ID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --address) ADDRESS="${2:-}"; shift 2 ;;
    --chain-id) CHAIN_ID="${2:-}"; shift 2 ;;
    --all) CHAIN_ID=""; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ -z "$ADDRESS" ]]; then
  echo "Missing --address" >&2; usage; exit 1
fi

if [[ ! "$ADDRESS" =~ ^0x[a-fA-F0-9]{40}$ ]]; then
  echo "Invalid address: $ADDRESS" >&2; exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
node -e '
const https = require("https");
const http = require("http");
const { getRpc, getChainMeta, CHAIN_META } = require(process.argv[3] + "/lib/rpc-config.js");

const ADDRESS = process.argv[1].toLowerCase();
const FILTER_CHAIN = process.argv[2] || "";

const CHAINS = {};
for (const [id, meta] of Object.entries(CHAIN_META)) {
  const rpc = getRpc(id);
  if (rpc) CHAINS[id] = { name: meta.name, rpc, symbol: meta.symbol, explorer: meta.explorer + "/address/" };
}

// Major tokens per chain (address → {symbol, decimals})
const TOKENS = {
  "1": {
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": { symbol: "USDC", decimals: 6 },
    "0xdac17f958d2ee523a2206206994597c13d831ec7": { symbol: "USDT", decimals: 6 },
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": { symbol: "WETH", decimals: 18 },
    "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599": { symbol: "WBTC", decimals: 8 },
    "0x6b175474e89094c44da98b954eedeac495271d0f": { symbol: "DAI",  decimals: 18 },
  },
  "8453": {
    "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913": { symbol: "USDC", decimals: 6 },
    "0x4200000000000000000000000000000000000006": { symbol: "WETH", decimals: 18 },
    "0x50c5725949a6f0c72e6c4a641f24049a917db0cb": { symbol: "DAI",  decimals: 18 },
  },
  "137": {
    "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359": { symbol: "USDC", decimals: 6 },
    "0xc2132d05d31c914a87c6611c10748aeb04b58e8f": { symbol: "USDT", decimals: 6 },
    "0x7ceb23fd6bc0add59e62ac25578270cff1b9f619": { symbol: "WETH", decimals: 18 },
  },
  "42161": {
    "0xaf88d065e77c8cc2239327c5edb3a432268e5831": { symbol: "USDC", decimals: 6 },
    "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9": { symbol: "USDT", decimals: 6 },
    "0x82af49447d8a07e3bd95bd0d56f35241523fbab1": { symbol: "WETH", decimals: 18 },
  },
  "10": {
    "0x0b2c639c533813f4aa9d7837caf62653d097ff85": { symbol: "USDC", decimals: 6 },
    "0x94b008aa00579c1307b0ef2c499ad98a8ce58e58": { symbol: "USDT", decimals: 6 },
    "0x4200000000000000000000000000000000000006": { symbol: "WETH", decimals: 18 },
  },
  "56": {
    "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d": { symbol: "USDC", decimals: 18 },
    "0x55d398326f99059ff775485246999027b3197955": { symbol: "USDT", decimals: 18 },
    "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c": { symbol: "WBNB", decimals: 18 },
  },
};

function rpcCall(rpcUrl, method, params) {
  return new Promise((resolve, reject) => {
    const url = new URL(rpcUrl);
    const body = JSON.stringify({ jsonrpc: "2.0", method, params, id: 1 });
    const mod = url.protocol === "http:" ? http : https;
    const req = mod.request({
      hostname: url.hostname, port: url.port || (url.protocol === "http:" ? 80 : 443),
      path: url.pathname + url.search, method: "POST",
      headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(body) }
    }, res => {
      let data = "";
      res.on("data", c => data += c);
      res.on("end", () => {
        try {
          const parsed = JSON.parse(data);
          resolve(parsed.result || null);
        } catch(e) { reject(new Error(data.slice(0, 200))); }
      });
    });
    req.on("error", reject);
    req.setTimeout(10000, () => { req.destroy(); reject(new Error("timeout")); });
    req.write(body); req.end();
  });
}

function formatUnits(raw, decimals) {
  if (raw === 0n) return "0";
  const s = raw.toString().padStart(decimals + 1, "0");
  const whole = s.slice(0, s.length - decimals) || "0";
  const frac = s.slice(s.length - decimals).replace(/0+$/, "");
  return frac ? `${whole}.${frac}` : whole;
}

// balanceOf(address) selector = 0x70a08231
function encodeBalanceOf(addr) {
  return "0x70a08231" + addr.slice(2).padStart(64, "0");
}

async function queryChain(chainId, chainInfo) {
  const result = { chain: chainInfo.name, chainId: Number(chainId), native: { symbol: chainInfo.symbol }, tokens: [] };

  try {
    // Native balance
    const rawBal = await rpcCall(chainInfo.rpc, "eth_getBalance", [ADDRESS, "latest"]);
    const native = rawBal ? BigInt(rawBal) : 0n;
    result.native.balance = formatUnits(native, 18);
    result.native.balanceWei = native.toString();

    // ERC20 balances (batch with individual calls — no multicall dependency)
    const chainTokens = TOKENS[chainId] || {};
    const tokenEntries = Object.entries(chainTokens);

    if (tokenEntries.length > 0) {
      const promises = tokenEntries.map(async ([addr, info]) => {
        try {
          const raw = await rpcCall(chainInfo.rpc, "eth_call", [{ to: addr, data: encodeBalanceOf(ADDRESS) }, "latest"]);
          const bal = raw && raw !== "0x" ? BigInt(raw) : 0n;
          if (bal > 0n) {
            return { token: addr, symbol: info.symbol, decimals: info.decimals, balance: formatUnits(bal, info.decimals), balanceRaw: bal.toString() };
          }
        } catch { /* skip failed token queries */ }
        return null;
      });
      const results = await Promise.all(promises);
      result.tokens = results.filter(Boolean);
    }
  } catch (e) {
    result.error = e.message;
  }

  return result;
}

async function main() {
  const chainIds = FILTER_CHAIN ? [FILTER_CHAIN] : Object.keys(CHAINS).filter(id => !["11155111","84532"].includes(id));

  const results = await Promise.all(
    chainIds.filter(id => CHAINS[id]).map(id => queryChain(id, CHAINS[id]))
  );

  // Summary
  const output = {
    address: ADDRESS,
    queriedAt: new Date().toISOString(),
    chains: results
  };

  console.log(JSON.stringify(output, null, 2));
}

main().catch(e => {
  console.error(JSON.stringify({ error: e.message }));
  process.exit(1);
});
' "$ADDRESS" "$CHAIN_ID" "$SCRIPT_DIR"
