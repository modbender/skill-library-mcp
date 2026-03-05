#!/usr/bin/env node
// 4Claw Mint Script — called by OpenClaw agents via skill
// Usage: node mint.js <private_key> <server_url>
// Example: node mint.js 0xYOUR_PRIVATE_KEY http://43.160.201.224:3456

const { ethers } = require("ethers");
const https = require("https");
const http = require("http");

const PRIVATE_KEY = process.argv[2];
const SERVER_URL = process.argv[3] || "http://43.160.201.224:3456";
const BSC_RPC = "https://bsc-dataseed1.binance.org";

const CONTRACT_ABI = [
  "function mint(bytes32 nonce, uint256 deadline, bytes signature) external",
  "function lastMintTime(address) view returns (uint256)",
  "function totalMinted() view returns (uint256)",
  "function mintRemaining() view returns (uint256)",
  "function balanceOf(address) view returns (uint256)",
  "function decimals() view returns (uint8)"
];

function fetchJSON(url, body) {
  return new Promise((resolve, reject) => {
    const parsed = new URL(url);
    const mod = parsed.protocol === "https:" ? https : http;
    const data = JSON.stringify(body);
    const req = mod.request(parsed, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Content-Length": data.length }
    }, (res) => {
      let buf = "";
      res.on("data", c => buf += c);
      res.on("end", () => {
        try { resolve({ status: res.statusCode, data: JSON.parse(buf) }); }
        catch(e) { reject(new Error("Invalid JSON: " + buf.slice(0, 200))); }
      });
    });
    req.on("error", reject);
    req.write(data);
    req.end();
  });
}

(async () => {
  if (!PRIVATE_KEY) {
    console.error("Usage: node mint.js <private_key> [server_url]");
    process.exit(1);
  }

  try {
    const provider = new ethers.JsonRpcProvider(BSC_RPC);
    const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
    console.log(`Wallet: ${wallet.address}`);

    // Step 1: Request mint signature from server
    console.log("Requesting mint signature...");
    const sigRes = await fetchJSON(`${SERVER_URL}/api/mint-signature`, {
      wallet_address: wallet.address
    });

    if (sigRes.status === 429) {
      console.log(`Cooldown active. Retry in ${sigRes.data.retry_after_seconds}s`);
      process.exit(0);
    }

    if (sigRes.status !== 200 || !sigRes.data.success) {
      console.error("Signature request failed:", sigRes.data);
      process.exit(1);
    }

    const { nonce, deadline, signature, contract } = sigRes.data;
    console.log(`Got signature. Contract: ${contract}, Deadline: ${deadline}`);

    // Step 2: Call mint on contract
    const fourClaw = new ethers.Contract(contract, CONTRACT_ABI, wallet);

    console.log("Sending mint transaction...");
    const tx = await fourClaw.mint(nonce, deadline, signature);
    console.log(`TX sent: ${tx.hash}`);

    const receipt = await tx.wait();
    console.log(`TX confirmed! Block: ${receipt.blockNumber}, Gas: ${receipt.gasUsed.toString()}`);

    // Step 3: Check balance
    const [balance, decimals, remaining] = await Promise.all([
      fourClaw.balanceOf(wallet.address),
      fourClaw.decimals(),
      fourClaw.mintRemaining()
    ]);
    console.log(`Balance: ${ethers.formatUnits(balance, decimals)} 4Claw`);
    console.log(`Remaining public mint: ${ethers.formatUnits(remaining, decimals)} 4Claw`);

    // Output JSON for skill parsing
    console.log(JSON.stringify({
      success: true,
      tx_hash: tx.hash,
      block: receipt.blockNumber,
      balance: ethers.formatUnits(balance, decimals),
      remaining: ethers.formatUnits(remaining, decimals)
    }));

  } catch(e) {
    console.error("Mint failed:", e.message);
    console.log(JSON.stringify({ success: false, error: e.message }));
    process.exit(1);
  }
})();
