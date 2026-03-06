#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Generate a structured payment receipt from a verified transaction.

Usage:
  evm-receipt.sh --tx-hash <0x...> --chain-id <id> [options]

Options:
  --tx-hash     Transaction hash (required)
  --chain-id    Chain ID (required)
  --memo        Payment memo/order ID (optional)
  --merchant    Merchant name (optional)
  --format      json | markdown | both (default: both)
  --out         Output directory for receipt files (optional, prints to stdout if omitted)
USAGE
}

TX_HASH=""
CHAIN_ID=""
MEMO=""
MERCHANT=""
FORMAT="both"
OUT_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tx-hash) TX_HASH="${2:-}"; shift 2 ;;
    --chain-id) CHAIN_ID="${2:-}"; shift 2 ;;
    --memo) MEMO="${2:-}"; shift 2 ;;
    --merchant) MERCHANT="${2:-}"; shift 2 ;;
    --format) FORMAT="$(echo "${2:-}" | tr '[:upper:]' '[:lower:]')"; shift 2 ;;
    --out) OUT_DIR="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ -z "$TX_HASH" || -z "$CHAIN_ID" ]]; then
  echo "Missing required args --tx-hash and --chain-id." >&2
  usage
  exit 1
fi

# Resolve RPC + explorer via shared config
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RPC="$(node -e "const c=require('$SCRIPT_DIR/lib/rpc-config.js'); const r=c.getRpc('$CHAIN_ID'); if(!r){process.exit(1)} process.stdout.write(r)")" || { echo "No RPC for chain $CHAIN_ID. Set RPC_$CHAIN_ID env var or add to config.json" >&2; exit 1; }
EXPLORER="$(node -e "const c=require('$SCRIPT_DIR/lib/rpc-config.js'); const m=c.getChainMeta('$CHAIN_ID'); process.stdout.write(m?m.explorer+'/tx/':'')")"
CHAIN_NAME="$(node -e "const c=require('$SCRIPT_DIR/lib/rpc-config.js'); const m=c.getChainMeta('$CHAIN_ID'); process.stdout.write(m?m.name:'Chain '+$CHAIN_ID)")"

node -e '
const http = require("https");
const RPC = process.argv[1];
const TX_HASH = process.argv[2];
const CHAIN_ID = process.argv[3];
const CHAIN_NAME = process.argv[4];
const EXPLORER = process.argv[5];
const MEMO = process.argv[6] || "";
const MERCHANT = process.argv[7] || "";
const FORMAT = process.argv[8];
const OUT_DIR = process.argv[9] || "";

function rpcCall(method, params) {
  return new Promise((resolve, reject) => {
    const url = new URL(RPC);
    const body = JSON.stringify({ jsonrpc: "2.0", method, params, id: 1 });
    const mod = url.protocol === "http:" ? require("http") : require("https");
    const req = mod.request({
      hostname: url.hostname, port: url.port || (url.protocol === "http:" ? 80 : 443),
      path: url.pathname, method: "POST",
      headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(body) }
    }, res => {
      let data = "";
      res.on("data", c => data += c);
      res.on("end", () => { try { resolve(JSON.parse(data).result); } catch(e) { reject(new Error(data)); } });
    });
    req.on("error", reject);
    req.setTimeout(15000, () => { req.destroy(); reject(new Error("timeout")); });
    req.write(body); req.end();
  });
}

const TRANSFER_SIG = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef";

// Known tokens
const TOKENS = {
  "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": { symbol: "USDC", decimals: 6 },
  "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913": { symbol: "USDC", decimals: 6 },
  "0x1c7d4b196cb0c7b01d743fbc6116a902379c7238": { symbol: "USDC", decimals: 6 },
  "0x036cbd53842c5426634e7929541ec2318f3dcf7e": { symbol: "USDC", decimals: 6 },
  "0xdac17f958d2ee523a2206206994597c13d831ec7": { symbol: "USDT", decimals: 6 },
};

function formatUnits(raw, decimals) {
  const s = raw.toString().padStart(decimals + 1, "0");
  const whole = s.slice(0, s.length - decimals) || "0";
  const frac = s.slice(s.length - decimals).replace(/0+$/, "");
  return frac ? `${whole}.${frac}` : whole;
}

function shortAddr(a) {
  return a ? `${a.slice(0, 8)}...${a.slice(-6)}` : "-";
}

async function main() {
  const [tx, receipt] = await Promise.all([
    rpcCall("eth_getTransactionByHash", [TX_HASH]),
    rpcCall("eth_getTransactionReceipt", [TX_HASH])
  ]);

  if (!tx || !receipt) {
    console.error(JSON.stringify({ error: "Transaction not found or still pending." }));
    process.exit(1);
  }

  const success = receipt.status === "0x1";
  const from = (tx.from || "").toLowerCase();
  const gasUsed = BigInt(receipt.gasUsed);
  const gasPrice = BigInt(tx.gasPrice || receipt.effectiveGasPrice || "0x0");
  const feeWei = gasUsed * gasPrice;
  const feeEth = formatUnits(feeWei, 18);
  const blockNum = parseInt(receipt.blockNumber, 16);
  const timestamp = new Date().toISOString(); // best-effort, block timestamp not always in tx

  // Detect transfer type
  let transferType = "ETH";
  let to = (tx.to || "").toLowerCase();
  let amount = formatUnits(BigInt(tx.value), 18);
  let symbol = "ETH";
  let tokenAddr = "";

  // Check for ERC20 Transfer events
  const transferLogs = (receipt.logs || []).filter(l => l.topics && l.topics[0] === TRANSFER_SIG);
  if (transferLogs.length > 0) {
    const log = transferLogs[0]; // primary transfer
    tokenAddr = log.address.toLowerCase();
    const info = TOKENS[tokenAddr] || { symbol: "TOKEN", decimals: 18 };
    symbol = info.symbol;
    to = "0x" + (log.topics[2] || "").slice(26).toLowerCase();
    amount = formatUnits(BigInt(log.data), info.decimals);
    transferType = "ERC20";
  }

  const explorerUrl = EXPLORER + TX_HASH;

  const receiptObj = {
    status: success ? "SUCCESS" : "FAILED",
    txHash: TX_HASH,
    chain: CHAIN_NAME,
    chainId: Number(CHAIN_ID),
    block: blockNum,
    from: from,
    to: to,
    transferType,
    token: tokenAddr || null,
    symbol,
    amount,
    fee: `${feeEth} ETH`,
    memo: MEMO || null,
    merchant: MERCHANT || null,
    explorer: explorerUrl,
    generatedAt: timestamp
  };

  // Markdown receipt
  const md = [
    `# 🧾 Payment Receipt`,
    ``,
    `| Field | Value |`,
    `|-------|-------|`,
    `| **Status** | ${receiptObj.status === "SUCCESS" ? "✅ Success" : "❌ Failed"} |`,
    `| **Amount** | ${amount} ${symbol} |`,
    `| **From** | \`${shortAddr(from)}\` |`,
    `| **To** | \`${shortAddr(to)}\` |`,
    MERCHANT ? `| **Merchant** | ${MERCHANT} |` : null,
    MEMO ? `| **Memo** | ${MEMO} |` : null,
    `| **Chain** | ${CHAIN_NAME} (${CHAIN_ID}) |`,
    `| **Block** | ${blockNum} |`,
    `| **Gas Fee** | ${feeEth} ETH |`,
    `| **Tx Hash** | \`${TX_HASH.slice(0, 18)}...\` |`,
    `| **Explorer** | [View on Explorer](${explorerUrl}) |`,
    ``,
    `---`,
    `*Generated: ${timestamp}*`,
  ].filter(Boolean).join("\n");

  if (OUT_DIR) {
    const fs = require("fs");
    const path = require("path");
    fs.mkdirSync(OUT_DIR, { recursive: true });
    const base = `receipt-${TX_HASH.slice(2, 10)}`;
    if (FORMAT === "json" || FORMAT === "both") {
      const p = path.join(OUT_DIR, base + ".json");
      fs.writeFileSync(p, JSON.stringify(receiptObj, null, 2));
      console.error(`Wrote: ${p}`);
    }
    if (FORMAT === "markdown" || FORMAT === "both") {
      const p = path.join(OUT_DIR, base + ".md");
      fs.writeFileSync(p, md);
      console.error(`Wrote: ${p}`);
    }
  }

  // Always output JSON to stdout
  if (FORMAT === "markdown") {
    console.log(md);
  } else {
    console.log(JSON.stringify(receiptObj, null, 2));
  }
}

main().catch(e => {
  console.error(JSON.stringify({ error: e.message }));
  process.exit(1);
});
' "$RPC" "$TX_HASH" "$CHAIN_ID" "$CHAIN_NAME" "$EXPLORER" "$MEMO" "$MERCHANT" "$FORMAT" "$OUT_DIR"
