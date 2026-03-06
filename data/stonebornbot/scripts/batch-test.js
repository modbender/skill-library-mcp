import { ethers } from "ethers";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BATCH_SIZE = 10;
const BATCH_DELAY = 600; // ms between batches

function ts() { return new Date().toISOString(); }
function log(msg) { console.log(`[${ts()}] ${msg}`); }

const cfg = JSON.parse(fs.readFileSync(path.join(__dirname, "config-test-all.json"), "utf-8"));
const provider = new ethers.JsonRpcProvider(cfg.rpcUrl, cfg.chainId, { staticNetwork: true });

const iface = new ethers.Interface(["function mintApe(uint256) payable"]);
const calldata = iface.encodeFunctionData("mintApe", [1]);

async function run() {
  const startTime = process.hrtime.bigint();
  log("🚀 BATCH TEST — " + cfg.wallets.length + " wallets, " + BATCH_SIZE + " per batch");

  // Pre-warm
  await provider.getBlockNumber();
  log("🔥 RPC connected");

  // Batch nonce fetch
  log("📋 Fetching nonces in batches of " + BATCH_SIZE + "...");
  const signers = cfg.wallets.map(w => new ethers.Wallet(w.privateKey, provider));
  const nonces = [];
  for (let i = 0; i < signers.length; i += BATCH_SIZE) {
    const batch = signers.slice(i, i + BATCH_SIZE);
    const batchNonces = await Promise.all(batch.map(s => provider.getTransactionCount(s.address, "pending")));
    nonces.push(...batchNonces);
    if (i + BATCH_SIZE < signers.length) await new Promise(r => setTimeout(r, 1000));
  }
  log("✅ All " + nonces.length + " nonces fetched");

  // Pre-sign all
  const signStart = process.hrtime.bigint();
  const signed = await Promise.all(signers.map((s, i) => {
    const tx = {
      to: cfg.contract.address,
      data: calldata,
      value: 0n,
      chainId: cfg.chainId,
      type: 2,
      maxFeePerGas: ethers.parseUnits(cfg.gas.maxFeePerGas, "gwei"),
      maxPriorityFeePerGas: ethers.parseUnits(cfg.gas.maxPriorityFeePerGas, "gwei"),
      gasLimit: cfg.gas.gasLimit,
      nonce: nonces[i],
    };
    return s.signTransaction(tx);
  }));
  const signMs = Number(process.hrtime.bigint() - signStart) / 1e6;
  log("⚡ All " + signed.length + " txs signed in " + signMs.toFixed(0) + "ms");

  // Batched broadcast
  const fireStart = process.hrtime.bigint();
  log("🔥 FIRING in batches of " + BATCH_SIZE + "...");

  let success = 0, fail = 0;
  const rpcUrls = cfg.rpcUrls || [cfg.rpcUrl];

  for (let b = 0; b < signed.length; b += BATCH_SIZE) {
    const batchNum = Math.floor(b / BATCH_SIZE) + 1;
    const totalBatches = Math.ceil(signed.length / BATCH_SIZE);
    const batch = signed.slice(b, b + BATCH_SIZE);
    const labels = cfg.wallets.slice(b, b + BATCH_SIZE).map(w => w.label);

    const results = await Promise.allSettled(batch.map((raw, i) => {
      // Send to first RPC only to avoid rate limits
      return fetch(rpcUrls[0], {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "eth_sendRawTransaction", params: [raw] }),
      }).then(r => r.json()).then(j => {
        if (j.error) throw new Error(j.error.message);
        return j.result;
      });
    }));

    let batchOk = 0, batchFail = 0;
    for (const r of results) {
      if (r.status === "fulfilled") { success++; batchOk++; }
      else { fail++; batchFail++; }
    }
    log("   Batch " + batchNum + "/" + totalBatches + ": ✅ " + batchOk + " ❌ " + batchFail);

    if (b + BATCH_SIZE < signed.length) await new Promise(r => setTimeout(r, BATCH_DELAY));
  }

  const fireMs = Number(process.hrtime.bigint() - fireStart) / 1e6;
  const totalMs = Number(process.hrtime.bigint() - startTime) / 1e6;

  log("");
  log("═══════════════════ RESULTS ═══════════════════");
  log("Total wallets: " + signed.length);
  log("✅ Accepted: " + success + " | ❌ Rejected: " + fail);
  log("Sign time: " + signMs.toFixed(0) + "ms");
  log("Fire time: " + fireMs.toFixed(0) + "ms");
  log("Total time: " + totalMs.toFixed(0) + "ms (" + (totalMs/1000).toFixed(2) + "s)");
}

run().catch(e => { console.error("Fatal:", e.message); process.exit(1); });
