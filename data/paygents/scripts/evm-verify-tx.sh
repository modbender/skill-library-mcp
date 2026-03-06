#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Verify an on-chain EVM transaction matches expected payment parameters.

Usage:
  evm-verify-tx.sh --chain-id <id> --from <0x...> --to <0x...> --asset <ETH|ERC20> --amount <decimal> [options]

Options:
  --chain-id    Chain ID (required)
  --from        Sender address (required)
  --to          Recipient address (required)
  --asset       ETH or ERC20 (required)
  --amount      Expected human-readable amount (required)
  --token       ERC20 contract address (auto-detected for USDC)
  --decimals    Token decimals (default: 6 for ERC20, 18 for ETH)
  --blocks      How many recent blocks to scan (default: 50)
  --tx-hash     Verify a specific tx hash instead of scanning
USAGE
}

CHAIN_ID=""
FROM=""
TO=""
ASSET=""
AMOUNT=""
TOKEN=""
DECIMALS=""
BLOCKS="50"
TX_HASH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --chain-id) CHAIN_ID="${2:-}"; shift 2 ;;
    --from) FROM="${2:-}"; shift 2 ;;
    --to) TO="${2:-}"; shift 2 ;;
    --asset) ASSET="$(echo "${2:-}" | tr '[:lower:]' '[:upper:]')"; shift 2 ;;
    --amount) AMOUNT="${2:-}"; shift 2 ;;
    --token) TOKEN="${2:-}"; shift 2 ;;
    --decimals) DECIMALS="${2:-}"; shift 2 ;;
    --blocks) BLOCKS="${2:-}"; shift 2 ;;
    --tx-hash) TX_HASH="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ -z "$CHAIN_ID" || -z "$FROM" || -z "$TO" || -z "$ASSET" || -z "$AMOUNT" ]]; then
  echo "Missing required args." >&2
  usage
  exit 1
fi

if [[ "$ASSET" == "ETH" ]]; then
  DECIMALS="${DECIMALS:-18}"
else
  DECIMALS="${DECIMALS:-6}"
  if [[ -z "$TOKEN" ]]; then
    case "$CHAIN_ID" in
      1) TOKEN="0xA0b86991c6218b36c1d19d4a2e9eb0ce3606eb48" ;;
      8453) TOKEN="0x833589fCD6eDb6E08f4c7C32D4f71b54bDa02913" ;;
      11155111) TOKEN="0x1c7d4b196cb0c7b01d743fbc6116a902379c7238" ;;
      84532) TOKEN="0x036CbD53842c5426634e7929541eC2318f3dCf7e" ;;
      *) echo "No default token for chain $CHAIN_ID. Provide --token." >&2; exit 1 ;;
    esac
  fi
fi

# Resolve RPC + explorer via shared config
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RPC="$(node -e "const c=require('$SCRIPT_DIR/lib/rpc-config.js'); const r=c.getRpc('$CHAIN_ID'); if(!r){process.exit(1)} process.stdout.write(r)")" || { echo "No RPC for chain $CHAIN_ID. Set RPC_$CHAIN_ID env var or add to config.json" >&2; exit 1; }
EXPLORER="$(node -e "const c=require('$SCRIPT_DIR/lib/rpc-config.js'); const m=c.getChainMeta('$CHAIN_ID'); process.stdout.write(m?m.explorer+'/tx/':'')")"

AMOUNT_BASE_UNITS="$(node -e '
const amount = process.argv[1];
const decimals = Number(process.argv[2]);
const [whole, fracRaw = ""] = amount.split(".");
const frac = (fracRaw + "0".repeat(decimals)).slice(0, decimals);
const value = BigInt(whole) * (10n ** BigInt(decimals)) + BigInt(frac || "0");
process.stdout.write(value.toString());
' "$AMOUNT" "$DECIMALS")"

# Run verification in node
node -e '
const http = require("https");

const RPC = process.argv[1];
const FROM = process.argv[2].toLowerCase();
const TO = process.argv[3].toLowerCase();
const ASSET = process.argv[4];
const TOKEN = (process.argv[5] || "").toLowerCase();
const AMOUNT_BASE = process.argv[6];
const BLOCKS = Number(process.argv[7]);
const TX_HASH = process.argv[8] || "";
const EXPLORER = process.argv[9];

function rpcCall(method, params) {
  return new Promise((resolve, reject) => {
    const url = new URL(RPC);
    const body = JSON.stringify({ jsonrpc: "2.0", method, params, id: 1 });
    const opts = { hostname: url.hostname, port: url.port || 443, path: url.pathname, method: "POST",
      headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(body) } };
    const req = (url.protocol === "http:" ? require("http") : require("https")).request(opts, res => {
      let data = "";
      res.on("data", c => data += c);
      res.on("end", () => {
        try { resolve(JSON.parse(data).result); } catch(e) { reject(new Error(data)); }
      });
    });
    req.on("error", reject);
    req.setTimeout(15000, () => { req.destroy(); reject(new Error("timeout")); });
    req.write(body);
    req.end();
  });
}

async function verifySpecificTx(hash) {
  const tx = await rpcCall("eth_getTransactionByHash", [hash]);
  if (!tx) { console.log(JSON.stringify({ verified: false, error: "tx not found" })); return; }
  const receipt = await rpcCall("eth_getTransactionReceipt", [hash]);
  if (!receipt || receipt.status !== "0x1") { console.log(JSON.stringify({ verified: false, error: "tx failed or pending" })); return; }

  const txFrom = (tx.from || "").toLowerCase();
  if (txFrom !== FROM) { console.log(JSON.stringify({ verified: false, error: "sender mismatch" })); return; }

  if (ASSET === "ETH") {
    const txTo = (tx.to || "").toLowerCase();
    const txValue = BigInt(tx.value).toString();
    if (txTo === TO && txValue === AMOUNT_BASE) {
      console.log(JSON.stringify({ verified: true, txHash: hash, explorer: EXPLORER + hash }));
    } else {
      console.log(JSON.stringify({ verified: false, error: "to/amount mismatch" }));
    }
  } else {
    // Check ERC20 Transfer logs
    const transferSig = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef";
    const match = receipt.logs.find(log => {
      if (log.address.toLowerCase() !== TOKEN) return false;
      if (log.topics[0] !== transferSig) return false;
      const logFrom = "0x" + (log.topics[1] || "").slice(26).toLowerCase();
      const logTo = "0x" + (log.topics[2] || "").slice(26).toLowerCase();
      const logAmount = BigInt(log.data).toString();
      return logFrom === FROM && logTo === TO && logAmount === AMOUNT_BASE;
    });
    if (match) {
      console.log(JSON.stringify({ verified: true, txHash: hash, explorer: EXPLORER + hash }));
    } else {
      console.log(JSON.stringify({ verified: false, error: "no matching Transfer event" }));
    }
  }
}

async function scanBlocks() {
  const latest = parseInt(await rpcCall("eth_blockNumber", []), 16);
  const start = latest - BLOCKS;

  if (ASSET === "ETH") {
    // Scan blocks for native ETH transfers
    for (let i = latest; i > start; i--) {
      const block = await rpcCall("eth_getBlockByNumber", ["0x" + i.toString(16), true]);
      if (!block || !block.transactions) continue;
      for (const tx of block.transactions) {
        const txFrom = (tx.from || "").toLowerCase();
        const txTo = (tx.to || "").toLowerCase();
        if (txFrom === FROM && txTo === TO && BigInt(tx.value).toString() === AMOUNT_BASE) {
          const receipt = await rpcCall("eth_getTransactionReceipt", [tx.hash]);
          if (receipt && receipt.status === "0x1") {
            console.log(JSON.stringify({ verified: true, txHash: tx.hash, explorer: EXPLORER + tx.hash, block: i }));
            return;
          }
        }
      }
    }
    console.log(JSON.stringify({ verified: false, error: "no matching tx in last " + BLOCKS + " blocks" }));
  } else {
    // Scan ERC20 Transfer events via getLogs
    const transferSig = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef";
    const fromTopic = "0x" + FROM.slice(2).padStart(64, "0");
    const toTopic = "0x" + TO.slice(2).padStart(64, "0");
    const logs = await rpcCall("eth_getLogs", [{
      fromBlock: "0x" + (start).toString(16),
      toBlock: "latest",
      address: TOKEN,
      topics: [transferSig, fromTopic, toTopic]
    }]);
    if (logs && logs.length > 0) {
      for (const log of logs.reverse()) {
        const logAmount = BigInt(log.data).toString();
        if (logAmount === AMOUNT_BASE) {
          console.log(JSON.stringify({ verified: true, txHash: log.transactionHash, explorer: EXPLORER + log.transactionHash }));
          return;
        }
      }
    }
    console.log(JSON.stringify({ verified: false, error: "no matching Transfer in last " + BLOCKS + " blocks" }));
  }
}

(TX_HASH ? verifySpecificTx(TX_HASH) : scanBlocks()).catch(e => {
  console.log(JSON.stringify({ verified: false, error: e.message }));
});
' "$RPC" "$FROM" "$TO" "$ASSET" "$TOKEN" "$AMOUNT_BASE_UNITS" "$BLOCKS" "$TX_HASH" "$EXPLORER"
