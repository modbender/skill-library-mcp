#!/usr/bin/env node
/**
 * NFT Mint Bot — MAXIMUM SPEED Edition
 * Target: sub-100ms from mint-live detection to tx broadcast
 *
 * Optimizations: WebSocket RPC, pre-signed txs, multi-RPC broadcast,
 * raw JSON-RPC sends, mempool monitoring, parallel everything,
 * process.hrtime.bigint() nanosecond timing
 *
 * Supports: direct RPC, Bankr API, Flashbots Protect
 * Features: multi-wallet, pre-signed txs, monitor/instant modes, EIP-1559,
 *           war mode, retry, WebSocket subscriptions, mempool watch
 */

import { ethers } from "ethers";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ─── High-res timing ──────────────────────────────────────────────────────────

const hrtMs = () => Number(process.hrtime.bigint() / 1_000_000n);

// ─── Logging ───────────────────────────────────────────────────────────────────

function ts() { return new Date().toISOString(); }
function log(msg, ...a) { console.log(`[${ts()}] ${msg}`, ...a); }
function logError(msg, ...a) { console.error(`[${ts()}] ❌ ${msg}`, ...a); }
function logSuccess(msg, ...a) { console.log(`[${ts()}] ✅ ${msg}`, ...a); }
function logWarn(msg, ...a) { console.warn(`[${ts()}] ⚠️  ${msg}`, ...a); }


// ─── Batched RPC helper (avoids rate limits on free RPCs) ──────────────────
async function batchedPromiseAll(tasks, batchSize = 10) {
  const results = [];
  for (let i = 0; i < tasks.length; i += batchSize) {
    const batch = tasks.slice(i, i + batchSize);
    const batchResults = await Promise.all(batch.map(fn => fn()));
    results.push(...batchResults);
  }
  return results;
}

// ─── Config ────────────────────────────────────────────────────────────────────

function loadConfig() {
  const configPath = path.join(__dirname, "config.json");
  if (!fs.existsSync(configPath)) throw new Error("config.json not found.");
  const cfg = JSON.parse(fs.readFileSync(configPath, "utf-8"));

  const modeArg = process.argv.find((a) => a.startsWith("--mode"));
  if (modeArg) {
    const idx = process.argv.indexOf(modeArg);
    if (process.argv[idx + 1]) cfg.monitoring.mode = process.argv[idx + 1];
  }

  // Defaults for new fields
  cfg.wsRpcUrl = cfg.wsRpcUrl || "";
  cfg.rpcUrls = cfg.rpcUrls || [cfg.rpcUrl];
  if (!cfg.rpcUrls.includes(cfg.rpcUrl)) cfg.rpcUrls.unshift(cfg.rpcUrl);
  cfg.monitoring.useWebSocket = cfg.monitoring.useWebSocket ?? false;
  cfg.monitoring.mempoolWatch = cfg.monitoring.mempoolWatch ?? false;
  cfg.monitoring.intervalMs = cfg.monitoring.intervalMs ?? 100;

  validate(cfg);
  return cfg;
}

function validate(cfg) {
  if (!cfg.rpcUrl || cfg.rpcUrl.includes("YOUR_KEY")) throw new Error("Set a real rpcUrl");
  if (!cfg.contract.address || cfg.contract.address === "0x" + "0".repeat(40))
    throw new Error("Set a real contract address");
  if (!cfg.bankr.enabled && (!cfg.wallets || cfg.wallets.length === 0))
    throw new Error("Provide wallets or enable Bankr");
}

// ─── Raw JSON-RPC helpers (bypass ethers overhead) ─────────────────────────────

let rpcId = 0;
function rawRpc(url, method, params) {
  return fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jsonrpc: "2.0", id: ++rpcId, method, params }),
  }).then((r) => r.json());
}

/** Broadcast a signed tx to ALL rpc endpoints simultaneously via raw fetch */
function broadcastRawToAll(rpcUrls, signedTx) {
  return Promise.all(
    rpcUrls.map((url) =>
      rawRpc(url, "eth_sendRawTransaction", [signedTx]).then((r) => {
        if (r.error) throw new Error(r.error.message || JSON.stringify(r.error));
        return r.result;
      })
    )
  );
}

/** Pre-warm all RPC connections with a cheap call */
function prewarmConnections(rpcUrls) {
  return Promise.allSettled(rpcUrls.map((url) => rawRpc(url, "eth_blockNumber", [])));
}

// ─── Bankr API helpers ─────────────────────────────────────────────────────────

async function bankrSign(cfg, txData) {
  const resp = await fetch(`${cfg.bankr.apiUrl}/agent/sign`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${cfg.bankr.apiKey}` },
    body: JSON.stringify(txData),
  });
  if (!resp.ok) throw new Error(`Bankr sign failed: ${resp.status} ${await resp.text()}`);
  return resp.json();
}

async function bankrSubmit(cfg, signedTx) {
  const resp = await fetch(`${cfg.bankr.apiUrl}/agent/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${cfg.bankr.apiKey}` },
    body: JSON.stringify(signedTx),
  });
  if (!resp.ok) throw new Error(`Bankr submit failed: ${resp.status} ${await resp.text()}`);
  return resp.json();
}

// ─── Flashbots ─────────────────────────────────────────────────────────────────

async function sendViaFlashbots(cfg, signedTxs, provider) {
  const authSigner = cfg.flashbots.authSignerKey
    ? new ethers.Wallet(cfg.flashbots.authSignerKey)
    : ethers.Wallet.createRandom();

  const blockNumber = await provider.getBlockNumber();
  const targetBlock = blockNumber + 1;

  const body = JSON.stringify({
    jsonrpc: "2.0", id: 1, method: "eth_sendBundle",
    params: [{ txs: signedTxs, blockNumber: ethers.toQuantity(targetBlock) }],
  });

  const signature = await authSigner.signMessage(ethers.id(body));

  const resp = await fetch(cfg.flashbots.relayUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Flashbots-Signature": `${authSigner.address}:${signature}`,
    },
    body,
  });

  if (!resp.ok) throw new Error(`Flashbots relay error: ${resp.status} ${await resp.text()}`);
  const result = await resp.json();
  log("Flashbots bundle submitted for block", targetBlock, result);
  return result;
}

// ─── Transaction Building ──────────────────────────────────────────────────────

// ─── Archetype ERC721a ABI fragments ───────────────────────────────────────────

const ARCHETYPE_ABI = [
  "function mint((bytes32 key, bytes32[] proof) auth, uint256 quantity, address affiliate, bytes signature) payable",
  "function invites(bytes32) view returns (uint128 price, uint128 reservePrice, uint128 delta, uint32 start, uint32 end, uint32 limit, uint32 maxSupply, uint32 unitSize, address tokenAddress, bool isBlacklist)",
  "function config() view returns (string baseUri, address affiliateSigner, uint32 maxSupply, uint32 maxBatchSize, uint32 affiliateFee, uint32 affiliateDiscount, uint32 defaultRoyalty)",
  "function computePrice(bytes32 key, uint256 quantity, bool affiliateUsed) view returns (uint256)",
];

function buildMintInterface(cfg) {
  if (cfg.archetype && cfg.archetype.enabled) {
    return new ethers.Interface(ARCHETYPE_ABI);
  }
  if (cfg.contract.abi && cfg.contract.abi.length > 0) return new ethers.Interface(cfg.contract.abi);
  return new ethers.Interface([`function ${cfg.contract.mintFunction} payable`]);
}

function encodeMintCalldata(iface, cfg) {
  if (cfg.archetype && cfg.archetype.enabled) {
    const auth = { key: cfg.archetype.authKey, proof: cfg.archetype.proof || [] };
    const quantity = cfg.contract.maxMintsPerWallet;
    const affiliate = cfg.archetype.affiliate || ethers.ZeroAddress;
    const signature = cfg.archetype.signature || "0x";
    return iface.encodeFunctionData("mint", [auth, quantity, affiliate, signature]);
  }
  const fnName = cfg.contract.mintFunction.split("(")[0];
  return iface.encodeFunctionData(fnName, cfg.contract.mintArgs);
}

// ─── Archetype helpers ─────────────────────────────────────────────────────────

async function checkArchetypeInvite(provider, cfg) {
  if (!cfg.archetype || !cfg.archetype.enabled) return;

  const iface = new ethers.Interface(ARCHETYPE_ABI);
  const contract = new ethers.Contract(cfg.contract.address, iface, provider);
  const authKey = cfg.archetype.authKey;
  const quantity = cfg.contract.maxMintsPerWallet;
  const hasAffiliate = cfg.archetype.affiliate && cfg.archetype.affiliate !== ethers.ZeroAddress;

  log("🏛️  Archetype mode — checking invite & config...");

  try {
    const invite = await contract.invites(authKey);
    log(`   Invite [${authKey.slice(0, 10)}...]: price=${ethers.formatEther(invite.price)} ETH, start=${invite.start}, end=${invite.end}, limit=${invite.limit}, maxSupply=${invite.maxSupply}`);
    const now = Math.floor(Date.now() / 1000);
    if (Number(invite.start) > now) {
      log(`   ⏰ Invite starts in ${Number(invite.start) - now}s (${new Date(Number(invite.start) * 1000).toISOString()})`);
    } else if (Number(invite.end) > 0 && Number(invite.end) < now) {
      logWarn(`   Invite has ENDED at ${new Date(Number(invite.end) * 1000).toISOString()}`);
    } else {
      logSuccess(`   Invite is ACTIVE`);
    }
  } catch (err) {
    logWarn(`   Failed to read invite: ${err.message}`);
  }

  try {
    const config = await contract.config();
    log(`   Config: maxSupply=${config.maxSupply}, maxBatchSize=${config.maxBatchSize}`);
  } catch (err) {
    logWarn(`   Failed to read config: ${err.message}`);
  }

  try {
    const price = await contract.computePrice(authKey, quantity, hasAffiliate);
    log(`   Computed price for ${quantity} mint(s): ${ethers.formatEther(price)} ETH`);
    cfg.contract.mintPriceEth = ethers.formatEther(price);
    cfg._archetypeComputedPrice = price;
    log(`   ✅ Using computed price: ${cfg.contract.mintPriceEth} ETH total`);
  } catch (err) {
    logWarn(`   Failed to compute price: ${err.message}`);
  }
}

async function waitForArchetypeInvite(provider, cfg) {
  const iface = new ethers.Interface(ARCHETYPE_ABI);
  const contract = new ethers.Contract(cfg.contract.address, iface, provider);
  const authKey = cfg.archetype.authKey;
  const intervalMs = cfg.monitoring.intervalMs || 100;
  const deadline = Date.now() + cfg.monitoring.timeoutMs;

  log(`🔍 Archetype: waiting for invite ${authKey.slice(0, 10)}... to go live...`);

  while (Date.now() < deadline) {
    try {
      const invite = await contract.invites(authKey);
      const now = Math.floor(Date.now() / 1000);
      if (Number(invite.start) > 0 && Number(invite.start) <= now) {
        if (Number(invite.end) === 0 || Number(invite.end) > now) {
          logSuccess(`🏛️  Archetype invite is LIVE! (started at ${new Date(Number(invite.start) * 1000).toISOString()})`);
          return true;
        }
      }
    } catch (err) {
      if (cfg.logging.verbose) log(`   Archetype poll: ${err.reason || err.code || "error"}`);
    }
    await sleep(intervalMs);
  }
  throw new Error("Archetype invite monitoring timeout — invite never went live");
}

// ─── War Mode Gas (fetched ONCE, shared across all wallets) ─────────────────

async function getWarModeGas(provider, cfg) {
  const warMode = cfg.gas.warMode;
  if (!warMode || !warMode.enabled || !warMode.autoAdjust) return null;

  try {
    const feeData = await provider.getFeeData();
    const networkMaxFee = feeData.maxFeePerGas || 0n;
    const networkPriority = feeData.maxPriorityFeePerGas || 0n;
    const configuredMax = ethers.parseUnits(cfg.gas.maxFeePerGas, "gwei");

    if (networkMaxFee > configuredMax) {
      const warMaxFee = ethers.parseUnits(warMode.maxFeeCapGwei, "gwei");
      const warPriority = ethers.parseUnits(warMode.maxPriorityCapGwei, "gwei");
      const adjustedMaxFee = networkMaxFee * 120n / 100n > warMaxFee ? warMaxFee : networkMaxFee * 120n / 100n;
      const adjustedPriority = networkPriority * 150n / 100n > warPriority ? warPriority : networkPriority * 150n / 100n;

      logWarn(`⚔️ WAR MODE ACTIVE — network gas ${ethers.formatUnits(networkMaxFee, "gwei")} gwei > configured ${cfg.gas.maxFeePerGas} gwei`);
      log(`   Adjusted: maxFee=${ethers.formatUnits(adjustedMaxFee, "gwei")} gwei, priority=${ethers.formatUnits(adjustedPriority, "gwei")} gwei`);
      return { maxFeePerGas: adjustedMaxFee, maxPriorityFeePerGas: adjustedPriority };
    }
  } catch (err) {
    logWarn(`War mode gas check failed: ${err.message}, using defaults`);
  }
  return null;
}

function buildTxObject(cfg, calldata, walletAddr, nonce, warGas, gasLimit) {
  // For archetype, computePrice already returns total for quantity
  const totalValue = cfg._archetypeComputedPrice
    ? cfg._archetypeComputedPrice
    : ethers.parseEther(cfg.contract.mintPriceEth) * BigInt(cfg.contract.maxMintsPerWallet);

  return {
    to: cfg.contract.address,
    data: calldata,
    value: totalValue,
    chainId: cfg.chainId,
    type: 2,
    maxFeePerGas: warGas ? warGas.maxFeePerGas : ethers.parseUnits(cfg.gas.maxFeePerGas, "gwei"),
    maxPriorityFeePerGas: warGas ? warGas.maxPriorityFeePerGas : ethers.parseUnits(cfg.gas.maxPriorityFeePerGas, "gwei"),
    nonce,
    gasLimit: gasLimit || cfg.gas.gasLimit || 300000,
  };
}

// ─── Pre-sign all wallets in parallel ──────────────────────────────────────────

async function presignAll(walletEntries) {
  const t0 = hrtMs();
  await Promise.all(
    walletEntries.map(async (entry) => {
      if (!entry.signer) return;
      entry.signedRawTx = await entry.signer.signTransaction(entry.tx);
    })
  );
  log(`⚡ All ${walletEntries.length} txs signed in ${hrtMs() - t0}ms`);
}

// ─── WebSocket Provider ────────────────────────────────────────────────────────

function createWsProvider(cfg) {
  if (!cfg.wsRpcUrl) return null;
  try {
    return new ethers.WebSocketProvider(cfg.wsRpcUrl, cfg.chainId, { staticNetwork: true });
  } catch (err) {
    logWarn(`WebSocket connection failed: ${err.message}, falling back to HTTP`);
    return null;
  }
}

// ─── Monitoring ────────────────────────────────────────────────────────────────

function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }

async function waitForMintLive(provider, wsProvider, cfg, iface, calldata) {
  const { intervalMs, mintLiveCheck, flagFunction, flagExpectedValue, timeoutMs,
    useWebSocket, mempoolWatch } = cfg.monitoring;
  const contract = new ethers.Contract(cfg.contract.address, iface, provider);
  const fnName = cfg.contract.mintFunction.split("(")[0];
  const deadline = Date.now() + timeoutMs;
  const fnSelector = calldata.slice(0, 10).toLowerCase();

  log(`🔍 Monitoring contract ${cfg.contract.address} for mint availability...`);
  log(`   Check: ${mintLiveCheck}, interval: ${intervalMs}ms, ws: ${!!wsProvider && useWebSocket}, mempool: ${mempoolWatch}`);

  // ── Mempool monitoring via WebSocket (fastest detection) ──
  if (mempoolWatch && wsProvider) {
    log("   👁️ Mempool watch active — monitoring pending txs for mint function calls");
    const mempoolPromise = new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        try { wsProvider.removeAllListeners("pending"); } catch {}
        reject(new Error("Mempool watch timeout"));
      }, timeoutMs);

      wsProvider.on("pending", async (txHash) => {
        try {
          const tx = await wsProvider.getTransaction(txHash);
          if (tx && tx.to && tx.to.toLowerCase() === cfg.contract.address.toLowerCase()
            && tx.data && tx.data.slice(0, 10).toLowerCase() === fnSelector) {
            clearTimeout(timeout);
            try { wsProvider.removeAllListeners("pending"); } catch {}
            logSuccess(`🎯 Mempool detected mint tx ${txHash} — FIRING!`);
            resolve(true);
          }
        } catch {}
      });
    });

    return Promise.race([
      mempoolPromise,
      pollForMintLive(contract, provider, cfg, iface, fnName, deadline, intervalMs, mintLiveCheck, flagFunction, flagExpectedValue),
    ]);
  }

  // ── WebSocket newHeads monitoring (block-level) ──
  if (useWebSocket && wsProvider) {
    log("   📡 WebSocket newHeads monitoring active");
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        try { wsProvider.removeAllListeners("block"); } catch {}
        reject(new Error("Monitoring timeout reached"));
      }, timeoutMs);

      wsProvider.on("block", async () => {
        try {
          const live = await checkMintLive(contract, provider, cfg, iface, fnName, mintLiveCheck, flagFunction, flagExpectedValue);
          if (live) {
            clearTimeout(timeout);
            try { wsProvider.removeAllListeners("block"); } catch {}
            resolve(true);
          }
        } catch {}
      });
    });
  }

  return pollForMintLive(contract, provider, cfg, iface, fnName, deadline, intervalMs, mintLiveCheck, flagFunction, flagExpectedValue);
}

async function checkMintLive(contract, provider, cfg, iface, fnName, mintLiveCheck, flagFunction, flagExpectedValue) {
  if (mintLiveCheck === "staticCall") {
    await contract[fnName].staticCall(...cfg.contract.mintArgs, {
      value: ethers.parseEther(cfg.contract.mintPriceEth) * BigInt(cfg.contract.maxMintsPerWallet),
    });
    logSuccess("Mint function callable — MINT IS LIVE!");
    return true;
  } else if (mintLiveCheck === "flag" && flagFunction) {
    const flagIface = new ethers.Interface([`function ${flagFunction} view returns (bool)`]);
    const flagContract = new ethers.Contract(cfg.contract.address, flagIface, provider);
    const flagName = flagFunction.split("(")[0];
    const result = await flagContract[flagName]();
    if (result === flagExpectedValue) {
      logSuccess(`Flag ${flagFunction} returned ${result} — MINT IS LIVE!`);
      return true;
    }
  }
  return false;
}

async function pollForMintLive(contract, provider, cfg, iface, fnName, deadline, intervalMs, mintLiveCheck, flagFunction, flagExpectedValue) {
  while (Date.now() < deadline) {
    try {
      const live = await checkMintLive(contract, provider, cfg, iface, fnName, mintLiveCheck, flagFunction, flagExpectedValue);
      if (live) return true;
    } catch (err) {
      if (cfg.logging.verbose) log(`   Poll: not live yet (${err.reason || err.code || "revert"})`);
    }
    await sleep(intervalMs);
  }
  throw new Error("Monitoring timeout reached — mint never went live");
}

// ─── Submission ────────────────────────────────────────────────────────────────

async function submitWithRetry(fn, label, maxRetries, delayMs) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try { return await fn(); } catch (err) {
      logError(`${label} attempt ${attempt}/${maxRetries} failed: ${err.message}`);
      if (attempt < maxRetries) await sleep(delayMs);
    }
  }
  throw new Error(`${label} failed after ${maxRetries} attempts`);
}

// ─── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  const startNs = process.hrtime.bigint();
  log("🚀 NFT Mint Bot starting... (MAX SPEED EDITION)");

  // 1. Load config
  const cfg = loadConfig();
  log(`Mode: ${cfg.monitoring.mode} | Contract: ${cfg.contract.address}`);
  log(`Mint function: ${cfg.contract.mintFunction} | Price: ${cfg.contract.mintPriceEth} ETH`);
  log(`RPC endpoints: ${cfg.rpcUrls.length} | WebSocket: ${cfg.wsRpcUrl ? "yes" : "no"}`);

  // 2. Pre-warm ALL connections in parallel
  await prewarmConnections(cfg.rpcUrls);
  log(`🔥 Pre-warmed ${cfg.rpcUrls.length} RPC connections`);

  // 3. Create providers
  const provider = new ethers.JsonRpcProvider(cfg.rpcUrl, cfg.chainId, { staticNetwork: true });
  const wsProvider = createWsProvider(cfg);
  if (wsProvider) log("📡 WebSocket provider connected");

  const fastProvider = wsProvider || provider;
  const blockNum = await fastProvider.getBlockNumber();
  log(`Connected to chain ${cfg.chainId}, block ${blockNum}`);

  // 3b. Archetype: check invite info on startup (reads price from chain)
  if (cfg.archetype && cfg.archetype.enabled) {
    log("🏛️  Archetype mode ENABLED");
    await checkArchetypeInvite(fastProvider, cfg);
  }

  // 4. Build interface and calldata (ONCE, cached)
  const iface = buildMintInterface(cfg);
  const calldata = encodeMintCalldata(iface, cfg);
  log(`Calldata: ${calldata.slice(0, 10)}... (${calldata.length} bytes)`);

  // 5. Prepare wallets — fetch ALL nonces + war mode gas in PARALLEL
  let walletEntries = [];

  if (cfg.bankr.enabled) {
    log(`Bankr mode enabled with ${cfg.bankr.walletIds.length} wallet(s)`);
    for (const wid of cfg.bankr.walletIds) {
      walletEntries.push({ bankrWalletId: wid, label: `bankr-${wid}` });
    }
  } else {
    const signers = cfg.wallets.map((w) => new ethers.Wallet(w.privateKey, provider));

    // Parallel: fetch all nonces + war mode gas simultaneously
    const [nonces, warGas] = await Promise.all([
      batchedPromiseAll(signers.map((s) => () => fastProvider.getTransactionCount(s.address, "pending")), 20),
      getWarModeGas(fastProvider, cfg),
    ]);

    // Gas limit: use config or estimate once from first wallet
    let gasLimit = cfg.gas.gasLimit;
    if (!gasLimit) {
      try {
        const mintValue = ethers.parseEther(cfg.contract.mintPriceEth);
        const totalValue = mintValue * BigInt(cfg.contract.maxMintsPerWallet);
        const est = await fastProvider.estimateGas({
          from: signers[0].address, to: cfg.contract.address,
          data: calldata, value: totalValue,
        });
        gasLimit = Number((est * 120n) / 100n);
      } catch {
        gasLimit = 300000;
        logWarn("Gas estimation failed, using default 300k");
      }
    }

    // Build all tx objects (pure CPU, no async)
    for (let i = 0; i < signers.length; i++) {
      const tx = buildTxObject(cfg, calldata, signers[i].address, nonces[i], warGas, gasLimit);
      walletEntries.push({
        signer: signers[i],
        label: cfg.wallets[i].label || signers[i].address.slice(0, 10),
        tx,
        signedRawTx: null,
      });
      log(`Wallet ${walletEntries[i].label}: nonce=${nonces[i]}, gasLimit=${gasLimit}`);
    }

    // 6. PRE-SIGN all transactions (parallel)
    await presignAll(walletEntries);
  }

  log(`${walletEntries.length} wallet(s) pre-loaded and pre-signed`);

  // 7. Monitor (if needed)
  if (cfg.monitoring.mode === "monitor") {
    if (cfg.archetype && cfg.archetype.enabled) {
      await waitForArchetypeInvite(fastProvider, cfg);
    } else {
      await waitForMintLive(fastProvider, wsProvider, cfg, iface, calldata);
    }

    // Refresh nonces and re-sign ONLY if nonces changed
    if (!cfg.bankr.enabled) {
      const freshNonces = await Promise.all(
        batchedPromiseAll(walletEntries.map((e) => () => fastProvider.getTransactionCount(e.signer.address, "pending")), 20)
      );
      let needResign = false;
      for (let i = 0; i < walletEntries.length; i++) {
        if (freshNonces[i] !== walletEntries[i].tx.nonce) {
          logWarn(`Nonce changed for ${walletEntries[i].label}: ${walletEntries[i].tx.nonce} → ${freshNonces[i]}`);
          walletEntries[i].tx.nonce = freshNonces[i];
          needResign = true;
        }
      }
      if (needResign) await presignAll(walletEntries);
    }
  } else {
    log("⚡ Instant mode — firing immediately");
  }

  // 8. 🔥🔥🔥 FIRE — ZERO AWAIT HOT PATH 🔥🔥🔥
  const fireNs = process.hrtime.bigint();
  log("🔥 FIRING ALL TRANSACTIONS...");

  const submissionPromises = walletEntries.map((entry) => {
    if (cfg.bankr.enabled) {
      return submitWithRetry(
        async () => {
          const signed = await bankrSign(cfg, {
            walletId: entry.bankrWalletId, to: cfg.contract.address,
            data: calldata, value: ethers.parseEther(cfg.contract.mintPriceEth).toString(),
            chainId: cfg.chainId,
          });
          const result = await bankrSubmit(cfg, signed);
          return { label: entry.label, hash: result.hash || result.txHash, source: "bankr" };
        },
        entry.label, cfg.retry.maxRetries, cfg.retry.retryDelayMs
      );
    }

    return submitWithRetry(
      async () => {
        if (cfg.flashbots.enabled) {
          const fbResult = await sendViaFlashbots(cfg, [entry.signedRawTx], provider);
          return { label: entry.label, hash: "flashbots-bundle", source: "flashbots", result: fbResult };
        }

        // RAW JSON-RPC broadcast to ALL endpoints simultaneously
        const hashes = await broadcastRawToAll(cfg.rpcUrls, entry.signedRawTx);
        const hash = hashes.find((h) => h) || hashes[0];
        return { label: entry.label, hash, source: `rpc×${cfg.rpcUrls.length}` };
      },
      entry.label, cfg.retry.maxRetries, cfg.retry.retryDelayMs
    );
  });

  const results = await Promise.allSettled(submissionPromises);
  const fireEndNs = process.hrtime.bigint();
  const submitDurationUs = Number((fireEndNs - fireNs) / 1_000n);
  const submitDurationMs = (submitDurationUs / 1000).toFixed(2);

  // 9. Log results
  log("\n═══════════════════ RESULTS ═══════════════════");
  log(`Submission took: ${submitDurationMs}ms (${submitDurationUs}µs)`);

  const successful = [];
  const failed = [];

  for (const r of results) {
    if (r.status === "fulfilled") {
      const v = r.value;
      logSuccess(`${v.label} → tx: ${v.hash} (via ${v.source})`);
      successful.push(v);
    } else {
      logError(`FAILED: ${r.reason?.message || r.reason}`);
      failed.push(r.reason);
    }
  }

  log(`\n✅ Successful: ${successful.length}/${results.length}`);
  if (failed.length) log(`❌ Failed: ${failed.length}/${results.length}`);

  // 10. Wait for confirmations (parallel)
  if (successful.length > 0 && !cfg.bankr.enabled && !cfg.flashbots.enabled) {
    log("\n⏳ Waiting for confirmations...");
    await Promise.all(successful.map(async (s) => {
      try {
        const receipt = await provider.waitForTransaction(s.hash, 1, 120000);
        if (receipt.status === 1) {
          logSuccess(`${s.label} CONFIRMED in block ${receipt.blockNumber} | Gas: ${receipt.gasUsed}`);
        } else {
          logError(`${s.label} REVERTED in block ${receipt.blockNumber}`);
        }
      } catch (err) {
        logWarn(`${s.label} confirmation timeout: ${err.message}`);
      }
    }));
  }

  const totalNs = process.hrtime.bigint() - startNs;
  const totalMs = Number(totalNs / 1_000_000n);
  log(`\n🏁 Total execution time: ${totalMs}ms (${(totalMs / 1000).toFixed(2)}s)`);
  log(`   Fire-to-submit: ${submitDurationMs}ms`);

  if (wsProvider) { try { await wsProvider.destroy(); } catch {} }
}

// ─── Entry ─────────────────────────────────────────────────────────────────────

main().catch((err) => {
  logError("Fatal:", err.message);
  if (err.stack) console.error(err.stack);
  process.exit(1);
});
