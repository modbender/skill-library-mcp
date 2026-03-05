#!/usr/bin/env node

/**
 * openscan-crypto CLI
 * 
 * Phase 1: Metadata commands (networks, rpcs, token, events, decode-event, addresses, profile)
 * Phase 2: EVM queries (balance, block, tx, receipt, gas, call, logs, code, nonce)
 */

import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";
import { ClientFactory } from "@openscan/network-connectors";
import { loadConfig, saveConfig, configExists, getEffectiveRpcs, setNetworkRpcs, setNetworkStrategy, addNetworkRpcs, removeNetworkRpc, resetNetwork, swapRpcs, moveRpc } from "./lib/rpcConfig.mjs";
import { resolveMetadataVersion, syncMetadata, mergeIntoConfig, fetchNetworkRpcs, autoSelectRpcs, cdnBase, EVM_CHAIN_IDS } from "./lib/metadataSync.mjs";
import { getNativeTokenPrice, getBTCPrice, formatPrice } from "./lib/priceService.mjs";
import { ETH_NATIVE_CHAINS } from "./lib/priceFeeds.mjs";
import { decodeFunctionInput } from "./lib/inputDecoder.mjs";
import { decodeEventLog, formatDecodedValue } from "./lib/eventDecoder.mjs";

// ── Config ──────────────────────────────────────────────────────────────────

const CDN_BASE = "https://cdn.jsdelivr.net/npm/@openscan/metadata@1.1.1-alpha.0/dist";
const CACHE_DIR = join(homedir(), ".cache", "openscan-crypto");
const CACHE_TTL_MS = 6 * 60 * 60 * 1000; // 6 hours

// Chain name aliases → chainId (or btc slug)
const CHAIN_ALIASES = {
  ethereum: 1, eth: 1, mainnet: 1,
  optimism: 10, op: 10,
  bnb: 56, bsc: 56,
  "bnb-testnet": 97,
  polygon: 137, matic: 137, pol: 137,
  base: 8453,
  arbitrum: 42161, arb: 42161,
  sepolia: 11155111,
  hardhat: 31337,
  bitcoin: "btc/mainnet", btc: "btc/mainnet",
  "btc-testnet4": "btc/testnet4",
};

// Reverse map: chainId → display name (populated from networks.json)
let networkNames = {};

// ── Cache layer ─────────────────────────────────────────────────────────────

async function ensureCacheDir() {
  if (!existsSync(CACHE_DIR)) {
    await mkdir(CACHE_DIR, { recursive: true });
  }
}

function cachePathFor(key) {
  return join(CACHE_DIR, key.replace(/\//g, "_") + ".json");
}

async function getCached(key) {
  const path = cachePathFor(key);
  if (!existsSync(path)) return null;
  try {
    const raw = await readFile(path, "utf-8");
    const { ts, data } = JSON.parse(raw);
    if (Date.now() - ts > CACHE_TTL_MS) return null;
    return data;
  } catch {
    return null;
  }
}

async function setCache(key, data) {
  await ensureCacheDir();
  await writeFile(cachePathFor(key), JSON.stringify({ ts: Date.now(), data }));
}

// ── CDN fetch ───────────────────────────────────────────────────────────────

async function fetchMetadata(path) {
  const cacheKey = path;
  const cached = await getCached(cacheKey);
  if (cached) return cached;

  const url = `${CDN_BASE}/${path}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch ${url}: ${res.status}`);

  const contentType = res.headers.get("content-type") || "";
  let data;
  if (contentType.includes("json") || path.endsWith(".json")) {
    data = await res.json();
  } else {
    data = await res.text();
  }
  await setCache(cacheKey, data);
  return data;
}

// ── Chain resolution ────────────────────────────────────────────────────────

function resolveChain(input) {
  if (!input) return null;
  const lower = input.toLowerCase().trim();
  
  // Direct alias
  if (CHAIN_ALIASES[lower] !== undefined) return CHAIN_ALIASES[lower];
  
  // Numeric chain ID
  const num = parseInt(lower, 10);
  if (!isNaN(num)) return num;

  return null;
}

function chainToRpcPath(chainId) {
  if (typeof chainId === "string" && chainId.startsWith("btc/")) {
    return `rpcs/${chainId}.json`;
  }
  return `rpcs/evm/${chainId}.json`;
}

function chainToTokenPath(chainId) {
  return `tokens/evm/${chainId}/all.json`;
}

function chainToEventsPath(chainId) {
  return `events/evm/${chainId}`;
}

// ── Output helpers ──────────────────────────────────────────────────────────

const EXPLORER_BASE = "https://openscan.eth.link";

const BTC_EXPLORER_SLUG = {
  "btc/mainnet": "btc",
  "btc/testnet4": "tbtc",
};

function explorerUrl(chainId, type, id) {
  if (typeof chainId === "number") {
    return `${EXPLORER_BASE}/#/${chainId}/${type}/${id}`;
  }
  const btcSlug = BTC_EXPLORER_SLUG[chainId];
  if (btcSlug) {
    return `${EXPLORER_BASE}/#/${btcSlug}/${type}/${id}`;
  }
  return undefined;
}

function out(data) {
  console.log(JSON.stringify(data, null, 2));
}

function err(msg) {
  console.error(`Error: ${msg}`);
  process.exit(1);
}

// ── Commands ────────────────────────────────────────────────────────────────

async function cmdNetworks() {
  const data = await fetchMetadata("networks.json");
  const result = data.networks.map(n => ({
    name: n.name,
    shortName: n.shortName,
    type: n.type,
    chainId: n.chainId || n.networkId,
    currency: n.currency,
    isTestnet: n.isTestnet || false,
  }));
  out({ count: result.length, networks: result });
}

async function cmdRpcs(chainInput, privateOnly) {
  const chainId = resolveChain(chainInput);
  if (chainId === null) err(`Unknown chain: ${chainInput}. Use 'networks' to list available chains.`);

  const path = chainToRpcPath(chainId);
  const data = await fetchMetadata(path);

  let endpoints = data.endpoints.filter(e => e.isPublic);
  if (privateOnly) {
    endpoints = endpoints.filter(e => e.tracking === "none");
  }

  out({
    networkId: data.networkId,
    totalEndpoints: endpoints.length,
    endpoints: endpoints.map(e => ({
      url: e.url,
      provider: e.provider,
      tracking: e.tracking,
      isOpenSource: e.isOpenSource,
    })),
  });
}

async function cmdToken(query, chainFilter) {
  const queryLower = query.toLowerCase();
  const isAddress = queryLower.startsWith("0x") && queryLower.length === 42;

  // Determine which chains to search
  const networksData = await fetchMetadata("networks.json");
  let chainsToSearch = networksData.networks
    .filter(n => n.type === "evm" && !n.isTestnet)
    .map(n => n.chainId);

  if (chainFilter) {
    const resolved = resolveChain(chainFilter);
    if (resolved === null || typeof resolved === "string") {
      err(`Token search only works for EVM chains. Unknown chain: ${chainFilter}`);
    }
    chainsToSearch = [resolved];
  }

  const results = [];
  for (const chainId of chainsToSearch) {
    try {
      const data = await fetchMetadata(chainToTokenPath(chainId));
      const network = networksData.networks.find(n => n.chainId === chainId);
      const networkName = network?.shortName || `Chain ${chainId}`;

      for (const token of data.tokens) {
        const match = isAddress
          ? token.address.toLowerCase() === queryLower
          : token.symbol.toLowerCase() === queryLower || token.name.toLowerCase().includes(queryLower);
        
        if (match) {
          results.push({
            ...token,
            chain: networkName,
            chainId,
            explorerLink: explorerUrl(chainId, "address", token.address),
          });
        }
      }
    } catch {
      // Chain may not have token data
    }
  }

  if (results.length === 0) {
    out({ found: false, query, message: `No token found matching "${query}"` });
  } else {
    out({ found: true, count: results.length, tokens: results });
  }
}

async function cmdEvents(chainFilter) {
  const chainId = chainFilter ? resolveChain(chainFilter) : 1; // default Ethereum
  if (chainId === null || typeof chainId === "string") {
    err(`Events only available for EVM chains.`);
  }

  const commonPath = `${chainToEventsPath(chainId)}/common.json`;
  try {
    const data = await fetchMetadata(commonPath);
    const events = Object.entries(data).map(([topic, info]) => ({
      topic,
      event: info.event,
      description: info.description,
    }));
    out({ chainId, count: events.length, events });
  } catch (e) {
    err(`No events data for chain ${chainId}: ${e.message}`);
  }
}

async function cmdDecodeEvent(topic) {
  const topicLower = topic.toLowerCase();

  // Search common events on Ethereum first (most comprehensive)
  const data = await fetchMetadata("events/evm/1/common.json");
  
  if (data[topicLower] || data[topic]) {
    const info = data[topicLower] || data[topic];
    out({ found: true, topic, event: info.event, description: info.description });
    return;
  }

  // Search all chains
  const networksData = await fetchMetadata("networks.json");
  for (const network of networksData.networks) {
    if (network.type !== "evm") continue;
    const chainId = network.chainId;
    try {
      const commonData = await fetchMetadata(`events/evm/${chainId}/common.json`);
      if (commonData[topicLower] || commonData[topic]) {
        const info = commonData[topicLower] || commonData[topic];
        out({ found: true, topic, chain: network.shortName, event: info.event, description: info.description });
        return;
      }
    } catch { /* skip */ }
  }

  out({ found: false, topic, message: "Event topic not found in metadata. It may be a contract-specific event." });
}

async function cmdAddresses(chainFilter) {
  const chainId = chainFilter ? resolveChain(chainFilter) : 1;
  if (chainId === null || typeof chainId === "string") {
    err(`Addresses only available for EVM chains.`);
  }

  try {
    const data = await fetchMetadata(`addresses/evm/${chainId}/all.json`);
    out({
      chainId: data.chainId,
      count: data.count,
      addresses: data.addresses,
    });
  } catch (e) {
    err(`No address data for chain ${chainId}: ${e.message}`);
  }
}

async function cmdProfile(type, id) {
  const validTypes = ["networks", "tokens", "apps", "organizations"];
  if (!validTypes.includes(type)) {
    err(`Invalid profile type: ${type}. Valid: ${validTypes.join(", ")}`);
  }

  let path;
  if (type === "networks") {
    const chainId = resolveChain(id);
    path = `profiles/networks/${chainId || id}.md`;
  } else if (type === "tokens") {
    // Expect format: chainId/address
    path = `profiles/tokens/${id}.md`;
  } else {
    path = `profiles/${type}/${id}.md`;
  }

  try {
    const content = await fetchMetadata(path);
    // For profiles, output as plain text
    console.log(content);
  } catch (e) {
    err(`Profile not found: ${type}/${id}`);
  }
}

// ── RPC config helpers ──────────────────────────────────────────────────────

/**
 * Ensure RPC config exists. Auto-init from metadata on first use.
 * Returns loaded config.
 */
async function ensureRpcConfig() {
  let config = await loadConfig();
  if (!config.lastFetched) {
    // First run — auto-sync from metadata
    const syncResult = await syncMetadata({
      maxRpcs: config.defaults.maxRpcs,
      privateOnly: config.defaults.privateOnly,
    });
    const { config: merged } = mergeIntoConfig(config, syncResult);
    await saveConfig(merged);
    process.stderr.write(`[openscan] First run: initialized RPC config from @openscan/metadata@${syncResult.version}\n`);
    return merged;
  }

  // Check staleness (warn if > 24h)
  const age = Date.now() - new Date(config.lastFetched).getTime();
  if (age > 24 * 60 * 60 * 1000) {
    process.stderr.write(`[openscan] RPC config is ${Math.floor(age / 3600000)}h old. Run "rpc-fetch" to update.\n`);
  }

  return config;
}

/**
 * Fetch and save RPCs for a specific network on-demand (if not in config)
 */
async function fetchAndSaveNetwork(chainId, config) {
  const version = config.metadataVersion || await resolveMetadataVersion();
  const path = chainToRpcPath(chainId);
  const data = await fetchNetworkRpcs(version, path);
  if (!data?.endpoints) err(`No RPC data found for chain ${chainId}`);
  const rpcs = autoSelectRpcs(data.endpoints, {
    maxRpcs: config.defaults.maxRpcs,
    privateOnly: config.defaults.privateOnly,
  });
  setNetworkRpcs(config, chainId, rpcs);
  config.lastFetched = new Date().toISOString();
  await saveConfig(config);
  return rpcs;
}

// ── EVM client factory ──────────────────────────────────────────────────────

async function getEvmClient(chainInput, privateOnly = false) {
  const chainId = resolveChain(chainInput);
  if (chainId === null) err(`Unknown chain: ${chainInput}`);
  if (typeof chainId === "string") err(`"${chainInput}" is not an EVM chain. Use EVM commands for EVM chains only.`);

  const config = await ensureRpcConfig();
  let effective = getEffectiveRpcs(config, chainId);

  if (!effective) {
    // Network not in config — fetch on demand
    await fetchAndSaveNetwork(chainId, config);
    const reloaded = await loadConfig();
    effective = getEffectiveRpcs(reloaded, chainId);
  }

  if (!effective || effective.rpcs.length === 0) {
    err(`No RPCs configured for chain ${chainId}. Run: rpc-fetch`);
  }

  // If --private flag, filter to tracking:none from configured RPCs
  let rpcUrls = effective.rpcs;
  if (privateOnly) {
    rpcUrls = rpcUrls.filter(r => r.tracking === "none");
    if (rpcUrls.length === 0) err(`No private (tracking:none) RPCs configured for chain ${chainId}`);
  }

  const client = ClientFactory.createClient(chainId, {
    type: effective.strategy,
    rpcUrls: rpcUrls.map(r => r.url),
  });
  return { client, chainId };
}

// ── Hex/Wei formatting helpers ──────────────────────────────────────────────

function hexToDecimal(hex) {
  if (!hex || hex === "0x") return "0";
  return BigInt(hex).toString();
}

function weiToEth(weiHex) {
  const wei = BigInt(weiHex);
  const eth = Number(wei) / 1e18;
  return eth;
}

function gweiFromWei(weiHex) {
  const wei = BigInt(weiHex);
  return Number(wei) / 1e9;
}

function formatTokenBalance(balanceHex, decimals) {
  const raw = BigInt(balanceHex);
  const divisor = 10n ** BigInt(decimals);
  const intPart = raw / divisor;
  const fracPart = raw % divisor;
  const fracStr = fracPart.toString().padStart(decimals, "0").replace(/0+$/, "");
  return fracStr ? `${intPart}.${fracStr}` : intPart.toString();
}

function formatBlock(block) {
  if (!block) return null;
  return {
    number: hexToDecimal(block.number),
    hash: block.hash,
    timestamp: new Date(parseInt(block.timestamp, 16) * 1000).toISOString(),
    gasUsed: hexToDecimal(block.gasUsed),
    gasLimit: hexToDecimal(block.gasLimit),
    baseFeePerGas: block.baseFeePerGas ? `${gweiFromWei(block.baseFeePerGas).toFixed(4)} gwei` : null,
    transactionCount: block.transactions ? block.transactions.length : 0,
    miner: block.miner,
    parentHash: block.parentHash,
  };
}

function formatTx(tx) {
  if (!tx) return null;
  return {
    hash: tx.hash,
    blockNumber: tx.blockNumber ? hexToDecimal(tx.blockNumber) : "pending",
    from: tx.from,
    to: tx.to,
    value: `${weiToEth(tx.value)} ETH`,
    valueWei: hexToDecimal(tx.value),
    gasPrice: tx.gasPrice ? `${gweiFromWei(tx.gasPrice).toFixed(4)} gwei` : null,
    maxFeePerGas: tx.maxFeePerGas ? `${gweiFromWei(tx.maxFeePerGas).toFixed(4)} gwei` : null,
    maxPriorityFeePerGas: tx.maxPriorityFeePerGas ? `${gweiFromWei(tx.maxPriorityFeePerGas).toFixed(4)} gwei` : null,
    gas: hexToDecimal(tx.gas),
    nonce: hexToDecimal(tx.nonce),
    input: tx.input === "0x" ? "(empty)" : tx.input.length > 74 ? `${tx.input.slice(0, 74)}... (${(tx.input.length - 2) / 2} bytes)` : tx.input,
    type: tx.type ? hexToDecimal(tx.type) : "0",
  };
}

function formatReceipt(receipt) {
  if (!receipt) return null;
  return {
    transactionHash: receipt.transactionHash,
    blockNumber: hexToDecimal(receipt.blockNumber),
    from: receipt.from,
    to: receipt.to,
    status: receipt.status === "0x1" ? "success" : "reverted",
    gasUsed: hexToDecimal(receipt.gasUsed),
    effectiveGasPrice: receipt.effectiveGasPrice ? `${gweiFromWei(receipt.effectiveGasPrice).toFixed(4)} gwei` : null,
    contractAddress: receipt.contractAddress,
    logsCount: receipt.logs ? receipt.logs.length : 0,
    logs: receipt.logs ? receipt.logs.slice(0, 10).map(log => ({
      address: log.address,
      topics: log.topics,
      data: log.data === "0x" ? "(empty)" : log.data.length > 74 ? `${log.data.slice(0, 74)}...` : log.data,
    })) : [],
  };
}

// ── EVM Commands ────────────────────────────────────────────────────────────

async function cmdBalance(address, chainInput, tokenQuery, privateOnly) {
  const { client, chainId } = await getEvmClient(chainInput || "ethereum", privateOnly);

  // Native balance
  const result = await client.getBalance(address);
  if (!result.success) err(`RPC error: ${JSON.stringify(result.errors)}`);

  const nativeBalance = weiToEth(result.data);
  const nativeBalanceWei = hexToDecimal(result.data);

  // Get currency name from metadata
  const networksData = await fetchMetadata("networks.json");
  const network = networksData.networks.find(n => n.chainId === chainId);
  const currency = network?.currency || "ETH";

  const output = {
    address,
    chain: network?.shortName || `Chain ${chainId}`,
    chainId,
    nativeBalance: `${nativeBalance} ${currency}`,
    nativeBalanceWei,
    explorerLink: explorerUrl(chainId, "address", address),
  };

  // ERC20 token balance if requested
  if (tokenQuery) {
    const tokenInfo = await resolveToken(tokenQuery, chainId);
    if (!tokenInfo) err(`Token "${tokenQuery}" not found on chain ${chainId}`);

    // balanceOf(address) selector: 0x70a08231 + padded address
    const paddedAddr = address.toLowerCase().replace("0x", "").padStart(64, "0");
    const callData = `0x70a08231${paddedAddr}`;

    const callFn = client.callContract?.bind(client) || client.call?.bind(client);
    if (!callFn) err(`Client for chain ${chainId} doesn't support contract calls`);
    const tokenResult = await callFn({ to: tokenInfo.address, data: callData });
    if (!tokenResult.success) err(`Token balance call failed: ${JSON.stringify(tokenResult.errors)}`);

    const tokenBalance = formatTokenBalance(tokenResult.data, tokenInfo.decimals);
    output.token = {
      symbol: tokenInfo.symbol,
      name: tokenInfo.name,
      address: tokenInfo.address,
      decimals: tokenInfo.decimals,
      balance: `${tokenBalance} ${tokenInfo.symbol}`,
      balanceRaw: hexToDecimal(tokenResult.data),
    };
  }

  out(output);
}

async function resolveToken(query, chainId) {
  try {
    const data = await fetchMetadata(chainToTokenPath(chainId));
    const q = query.toLowerCase();
    const isAddr = q.startsWith("0x") && q.length === 42;
    return data.tokens.find(t =>
      isAddr ? t.address.toLowerCase() === q : t.symbol.toLowerCase() === q
    ) || null;
  } catch {
    return null;
  }
}

async function cmdBlock(blockId, chainInput, privateOnly) {
  const { client, chainId } = await getEvmClient(chainInput || "ethereum", privateOnly);

  let result;
  if (!blockId || blockId === "latest") {
    result = await client.getBlockByNumber("latest", false);
  } else if (blockId.startsWith("0x") && blockId.length === 66) {
    result = await client.getBlockByHash(blockId, false);
  } else {
    const hex = "0x" + parseInt(blockId, 10).toString(16);
    result = await client.getBlockByNumber(hex, false);
  }

  if (!result.success) err(`RPC error: ${JSON.stringify(result.errors)}`);
  if (!result.data) err(`Block not found: ${blockId}`);

  const formatted = formatBlock(result.data);
  formatted.explorerLink = explorerUrl(chainId, "block", formatted.number);
  out(formatted);
}

async function cmdTx(txHash, chainInput, privateOnly) {
  if (!txHash || !txHash.startsWith("0x")) err("Usage: tx <0xhash> [--chain <chain>]");
  const { client, chainId } = await getEvmClient(chainInput || "ethereum", privateOnly);

  const result = await client.getTransactionByHash(txHash);
  if (!result.success) err(`RPC error: ${JSON.stringify(result.errors)}`);
  if (!result.data) err(`Transaction not found: ${txHash}`);

  const formatted = formatTx(result.data);
  formatted.explorerLink = explorerUrl(chainId, "tx", txHash);
  out(formatted);
}

async function cmdReceipt(txHash, chainInput, privateOnly) {
  if (!txHash || !txHash.startsWith("0x")) err("Usage: receipt <0xhash> [--chain <chain>]");
  const { client, chainId } = await getEvmClient(chainInput || "ethereum", privateOnly);

  const result = await client.getTransactionReceipt(txHash);
  if (!result.success) err(`RPC error: ${JSON.stringify(result.errors)}`);
  if (!result.data) err(`Receipt not found: ${txHash}`);

  // Try to decode event topics from metadata
  const formatted = formatReceipt(result.data);
  try {
    const events = await fetchMetadata("events/evm/1/common.json");
    for (const log of formatted.logs) {
      if (log.topics && log.topics[0] && events[log.topics[0]]) {
        log.eventName = events[log.topics[0]].event;
        log.eventDescription = events[log.topics[0]].description;
      }
    }
  } catch { /* skip event decoding */ }

  formatted.explorerLink = explorerUrl(chainId, "tx", txHash);
  out(formatted);
}

async function cmdGas(chainInput, privateOnly) {
  const { client, chainId } = await getEvmClient(chainInput || "ethereum", privateOnly);

  const [gasPriceResult, priorityResult] = await Promise.allSettled([
    client.gasPrice(),
    client.maxPriorityFeePerGas(),
  ]);

  const output = { chainId };

  if (gasPriceResult.status === "fulfilled" && gasPriceResult.value.success) {
    output.gasPrice = `${gweiFromWei(gasPriceResult.value.data).toFixed(4)} gwei`;
    output.gasPriceWei = hexToDecimal(gasPriceResult.value.data);
  }

  if (priorityResult.status === "fulfilled" && priorityResult.value.success) {
    output.maxPriorityFeePerGas = `${gweiFromWei(priorityResult.value.data).toFixed(4)} gwei`;
  }

  // Try to get latest block for baseFee
  try {
    const blockResult = await client.getBlockByNumber("latest", false);
    if (blockResult.success && blockResult.data?.baseFeePerGas) {
      output.baseFee = `${gweiFromWei(blockResult.data.baseFeePerGas).toFixed(4)} gwei`;
      output.blockNumber = hexToDecimal(blockResult.data.number);
    }
  } catch { /* skip */ }

  out(output);
}

async function cmdCall(to, data, chainInput, blockTag, privateOnly) {
  if (!to || !data) err("Usage: call <to_address> <calldata_hex> [--chain <chain>] [--block <tag>]");
  const { client } = await getEvmClient(chainInput || "ethereum", privateOnly);

  const callFn = client.callContract?.bind(client) || client.call?.bind(client);
  if (!callFn) err(`Client doesn't support contract calls`);
  const result = await callFn({ to, data }, blockTag || "latest");
  if (!result.success) err(`Call failed: ${JSON.stringify(result.errors)}`);

  out({ to, data, blockTag: blockTag || "latest", result: result.data });
}

async function cmdLogs(chainInput, address, topics, fromBlock, toBlock, privateOnly) {
  const { client, chainId } = await getEvmClient(chainInput || "ethereum", privateOnly);

  const filter = {};
  if (address) filter.address = address;
  if (topics && topics.length > 0) filter.topics = topics;
  filter.fromBlock = fromBlock || "latest";
  filter.toBlock = toBlock || "latest";

  const result = await client.getLogs(filter);
  if (!result.success) err(`getLogs failed: ${JSON.stringify(result.errors)}`);

  const logs = (result.data || []).slice(0, 50).map(log => ({
    address: log.address,
    blockNumber: hexToDecimal(log.blockNumber),
    transactionHash: log.transactionHash,
    topics: log.topics,
    data: log.data === "0x" ? "(empty)" : log.data.length > 138 ? `${log.data.slice(0, 138)}...` : log.data,
    explorerLink: explorerUrl(chainId, "tx", log.transactionHash),
  }));

  out({ count: logs.length, truncated: (result.data || []).length > 50, logs });
}

async function cmdCode(address, chainInput, privateOnly) {
  if (!address) err("Usage: code <address> [--chain <chain>]");
  const { client, chainId } = await getEvmClient(chainInput || "ethereum", privateOnly);

  const result = await client.getCode(address);
  if (!result.success) err(`RPC error: ${JSON.stringify(result.errors)}`);

  const code = result.data;
  const isEmpty = !code || code === "0x" || code === "0x0";
  out({
    address,
    isContract: !isEmpty,
    codeSize: isEmpty ? 0 : (code.length - 2) / 2,
    code: isEmpty ? "(EOA — no code)" : code.length > 200 ? `${code.slice(0, 200)}... (${(code.length - 2) / 2} bytes)` : code,
    explorerLink: explorerUrl(chainId, "address", address),
  });
}

async function cmdNonce(address, chainInput, privateOnly) {
  if (!address) err("Usage: nonce <address> [--chain <chain>]");
  const { client, chainId } = await getEvmClient(chainInput || "ethereum", privateOnly);

  const result = await client.getTransactionCount(address);
  if (!result.success) err(`RPC error: ${JSON.stringify(result.errors)}`);

  out({ address, nonce: hexToDecimal(result.data), explorerLink: explorerUrl(chainId, "address", address) });
}

// ── ENS resolution ──────────────────────────────────────────────────────────

async function resolveENS(name) {
  if (!name.endsWith(".eth")) return name;

  // ENS registry on Ethereum mainnet
  // namehash the name, then call resolver
  const { client } = await getEvmClient("ethereum");

  // Use the ENS Universal Resolver at 0xce01f8eee7E479C928F8919abD53E553a36CeF67
  const UNIVERSAL_RESOLVER = "0xce01f8eee7E479C928F8919abD53E553a36CeF67";

  // Encode the DNS name
  const labels = name.split(".");
  let dnsName = "0x";
  for (const label of labels) {
    const len = label.length.toString(16).padStart(2, "0");
    const hex = Buffer.from(label).toString("hex");
    dnsName += len + hex;
  }
  dnsName += "00"; // null terminator

  // resolve(bytes name, uint256 coinType) — but simpler: use addr(bytes32 node)
  // Actually, use the universal resolver's resolve(bytes,bytes) function
  // Selector: 0x9061b923 = resolve(bytes name, bytes data)
  // data = addr(bytes32) selector 0x3b3b57de + namehash

  // Compute namehash
  let node = "0000000000000000000000000000000000000000000000000000000000000000";
  for (let i = labels.length - 1; i >= 0; i--) {
    // keccak256 of label — we need to use eth_call with sha3
    const labelHex = Buffer.from(labels[i]).toString("hex");
    const labelHashResult = await client.sha3("0x" + labelHex);
    if (!labelHashResult.success) return name; // fallback
    const labelHash = labelHashResult.data.slice(2);
    // namehash = keccak256(parentHash + labelHash)
    const combined = "0x" + node + labelHash;
    const nodeResult = await client.sha3(combined);
    if (!nodeResult.success) return name;
    node = nodeResult.data.slice(2);
  }

  // Now call resolver: addr(bytes32 node) = 0x3b3b57de + node
  const addrCall = "0x3b3b57de" + node;

  // Encode for universal resolver: resolve(bytes dnsName, bytes data)
  // But that's complex ABI encoding. Let's try simpler: directly query the ENS registry
  // ENS Registry: 0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e
  // resolver(bytes32 node) = 0x0178b8bf + node
  const ENS_REGISTRY = "0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e";
  const callFn = client.callContract?.bind(client) || client.call?.bind(client);

  const resolverResult = await callFn({ to: ENS_REGISTRY, data: "0x0178b8bf" + node });
  if (!resolverResult.success || !resolverResult.data || resolverResult.data === "0x" + "0".repeat(64)) {
    return name; // no resolver
  }
  const resolverAddr = "0x" + resolverResult.data.slice(26);

  // Call addr(bytes32) on the resolver
  const addrResult = await callFn({ to: resolverAddr, data: addrCall });
  if (!addrResult.success || !addrResult.data || addrResult.data === "0x" + "0".repeat(64)) {
    return name;
  }

  return "0x" + addrResult.data.slice(26);
}

// ── Multi-chain balance ─────────────────────────────────────────────────────

async function cmdMultiBalance(address, privateOnly) {
  const networksData = await fetchMetadata("networks.json");
  const evmChains = networksData.networks.filter(n => n.type === "evm" && !n.isTestnet);
  const config = await ensureRpcConfig();

  const results = [];
  const promises = evmChains.map(async (network) => {
    try {
      // Use persisted RPC config
      let effective = getEffectiveRpcs(config, network.chainId);
      if (!effective) {
        // Fetch on demand
        await fetchAndSaveNetwork(network.chainId, config);
        effective = getEffectiveRpcs(await loadConfig(), network.chainId);
      }
      if (!effective || effective.rpcs.length === 0) return;

      let rpcUrls = effective.rpcs;
      if (privateOnly) rpcUrls = rpcUrls.filter(r => r.tracking === "none");
      if (rpcUrls.length === 0) return;

      const client = ClientFactory.createClient(network.chainId, {
        type: effective.strategy,
        rpcUrls: rpcUrls.map(r => r.url),
      });
      const result = await client.getBalance(address);
      if (result.success) {
        const balance = weiToEth(result.data);
        results.push({
          chain: network.shortName,
          chainId: network.chainId,
          currency: network.currency,
          balance: `${balance} ${network.currency}`,
          balanceRaw: hexToDecimal(result.data),
          hasBalance: balance > 0,
        });
      }
    } catch { /* skip failed chains */ }
  });

  await Promise.all(promises);

  // Sort: chains with balance first, then alphabetical
  results.sort((a, b) => {
    if (a.hasBalance !== b.hasBalance) return b.hasBalance ? 1 : -1;
    return a.chain.localeCompare(b.chain);
  });

  // Add per-chain explorer links
  for (const r of results) {
    r.explorerLink = explorerUrl(r.chainId, "address", address);
  }

  out({ address, chains: results.length, balances: results });
}

// ── Bitcoin client factory ──────────────────────────────────────────────────

const BITCOIN_MAINNET = "bip122:000000000019d6689c085ae165831e93";
const BTC_REST_API = "https://mempool.space/api"; // fallback for address lookups

async function getBtcClient() {
  const config = await ensureRpcConfig();
  const effective = getEffectiveRpcs(config, "btc/mainnet");

  if (effective && effective.rpcs.length > 0) {
    // Use persisted config — filter out REST-only APIs for JSON-RPC client
    const jsonRpcUrls = effective.rpcs
      .filter(r => !r.url.includes("mempool.space") && !r.url.includes("blockstream") && !r.url.includes("blockchain.info"))
      .map(r => r.url);
    const rpcUrls = jsonRpcUrls.length > 0 ? jsonRpcUrls : effective.rpcs.map(r => r.url);
    return ClientFactory.createClient(BITCOIN_MAINNET, { type: effective.strategy, rpcUrls });
  }

  // Fallback: fetch from metadata on demand
  await fetchAndSaveNetwork("btc/mainnet", config);
  const reloaded = await loadConfig();
  const eff = getEffectiveRpcs(reloaded, "btc/mainnet");
  const rpcUrls = (eff?.rpcs || []).map(r => r.url);
  if (rpcUrls.length === 0) err("No RPCs available for Bitcoin. Run: rpc-fetch");
  return ClientFactory.createClient(BITCOIN_MAINNET, { type: eff?.strategy || "fallback", rpcUrls });
}

function satsToBtc(sats) {
  return (Number(sats) / 1e8).toFixed(8);
}

function btcToSats(btc) {
  return Math.round(Number(btc) * 1e8);
}

async function cmdBtcInfo() {
  const client = await getBtcClient();

  const [countRes, hashRes, mempoolRes, feeRes] = await Promise.all([
    client.getBlockCount(),
    client.getBestBlockHash(),
    client.getMempoolInfo(),
    client.estimateSmartFee(6),
  ]);

  if (!countRes.success) err(`RPC error: ${JSON.stringify(countRes.errors)}`);

  // Get tip block details
  const blockRes = await client.getBlock(hashRes.data, 1);
  const b = blockRes.data;
  const m = mempoolRes.data;

  out({
    height: countRes.data,
    bestBlockHash: hashRes.data,
    timestamp: new Date(b.time * 1000).toISOString(),
    difficulty: b.difficulty,
    mempool: {
      txCount: m.size,
      sizeMB: (m.bytes / 1e6).toFixed(2),
      totalFeeBTC: m.total_fee?.toFixed(8) || "unknown",
      mempoolMinFee: `${btcToSats(m.mempoolminfee)} sat/vB`,
    },
    feeEstimate: feeRes.data ? {
      feeRate: `${btcToSats(feeRes.data.feerate)} sat/vB`,
      blocks: feeRes.data.blocks,
    } : null,
  });
}

async function cmdBtcBlock(blockId) {
  const client = await getBtcClient();

  let hash;
  if (!blockId || blockId === "latest") {
    const res = await client.getBestBlockHash();
    if (!res.success) err(`RPC error: ${JSON.stringify(res.errors)}`);
    hash = res.data;
  } else if (blockId.length === 64) {
    hash = blockId;
  } else {
    const height = parseInt(blockId, 10);
    if (isNaN(height)) err(`Invalid block identifier: ${blockId}`);
    const res = await client.getBlockHash(height);
    if (!res.success) err(`RPC error: ${JSON.stringify(res.errors)}`);
    hash = res.data;
  }

  const result = await client.getBlock(hash, 1);
  if (!result.success) err(`RPC error: ${JSON.stringify(result.errors)}`);
  const b = result.data;

  out({
    hash: b.hash,
    height: b.height,
    timestamp: new Date(b.time * 1000).toISOString(),
    txCount: b.nTx,
    size: `${(b.size / 1024).toFixed(1)} KB`,
    weight: `${(b.weight / 1024).toFixed(1)} KWU`,
    difficulty: b.difficulty,
    nonce: b.nonce,
    version: b.version,
    merkleRoot: b.merkleroot,
    previousBlockHash: b.previousblockhash || null,
    medianTime: new Date(b.mediantime * 1000).toISOString(),
    confirmations: b.confirmations,
    explorerLink: explorerUrl("btc/mainnet", "block", b.hash),
  });
}

async function cmdBtcTx(txid) {
  if (!txid) err("Usage: btc-tx <txid>");
  const client = await getBtcClient();

  const result = await client.getRawTransaction(txid, true);
  if (!result.success) err(`RPC error: ${JSON.stringify(result.errors)}`);
  const tx = result.data;

  // Calculate total output value
  const totalOut = tx.vout.reduce((s, v) => s + (v.value || 0), 0);

  out({
    txid: tx.txid,
    confirmed: !!tx.blockhash,
    blockHash: tx.blockhash || null,
    confirmations: tx.confirmations || 0,
    timestamp: tx.time ? new Date(tx.time * 1000).toISOString() : null,
    version: tx.version,
    size: `${tx.size} bytes`,
    vsize: `${tx.vsize} vbytes`,
    weight: `${tx.weight} WU`,
    inputs: tx.vin.length,
    outputs: tx.vout.length,
    totalOutput: `${totalOut.toFixed(8)} BTC`,
    isCoinbase: tx.vin.length > 0 && !!tx.vin[0].coinbase,
    vin: tx.vin.slice(0, 5).map(v => ({
      txid: v.txid ? `${v.txid.slice(0, 16)}...` : "(coinbase)",
      vout: v.vout,
      isCoinbase: !!v.coinbase,
    })),
    vout: tx.vout.slice(0, 5).map(v => ({
      n: v.n,
      value: `${v.value.toFixed(8)} BTC`,
      type: v.scriptPubKey?.type,
      address: v.scriptPubKey?.address || null,
    })),
    truncated: tx.vin.length > 5 || tx.vout.length > 5,
    explorerLink: explorerUrl("btc/mainnet", "tx", tx.txid),
  });
}

async function cmdBtcMempool() {
  const client = await getBtcClient();

  const [mempoolRes, feeRes] = await Promise.all([
    client.getMempoolInfo(),
    client.estimateSmartFee(6),
  ]);

  if (!mempoolRes.success) err(`RPC error: ${JSON.stringify(mempoolRes.errors)}`);
  const m = mempoolRes.data;

  // Get raw mempool txids (limited)
  const rawRes = await client.getRawMempool(false);
  const txids = rawRes.success ? (rawRes.data || []).slice(0, 5) : [];

  out({
    txCount: m.size,
    sizeMB: (m.bytes / 1e6).toFixed(2),
    totalFeeBTC: m.total_fee?.toFixed(8) || "unknown",
    mempoolMinFee: `${btcToSats(m.mempoolminfee)} sat/vB`,
    minRelayFee: `${btcToSats(m.minrelaytxfee)} sat/vB`,
    loaded: m.loaded,
    maxMempoolMB: (m.maxmempool / 1e6).toFixed(0),
    feeEstimate: feeRes.data ? {
      feeRate: `${btcToSats(feeRes.data.feerate)} sat/vB`,
      blocks: feeRes.data.blocks,
    } : null,
    recentTxids: txids.map(t => `${t.slice(0, 16)}...`),
  });
}

async function cmdBtcFee() {
  const client = await getBtcClient();

  // estimateSmartFee for different confirmation targets
  const targets = [1, 3, 6, 12, 25];
  const results = await Promise.all(
    targets.map(t => client.estimateSmartFee(t))
  );

  const fees = {};
  const labels = ["nextBlock", "3blocks", "6blocks", "12blocks", "25blocks"];
  targets.forEach((t, i) => {
    if (results[i].success && results[i].data?.feerate) {
      fees[labels[i]] = `${btcToSats(results[i].data.feerate)} sat/vB`;
    }
  });

  out({ ...fees, note: "Fee estimates via estimateSmartFee (Bitcoin Core)" });
}

async function cmdBtcAddress(address) {
  if (!address) err("Usage: btc-address <address>");
  // Address balance requires an indexer — Bitcoin Core RPC doesn't support it natively.
  // Fall back to mempool.space REST API for this specific query.
  const url = `${BTC_REST_API}/address/${address}`;
  const res = await fetch(url);
  if (!res.ok) err(`Address lookup failed: ${res.status}`);
  const data = await res.json();

  const funded = data.chain_stats.funded_txo_sum + data.mempool_stats.funded_txo_sum;
  const spent = data.chain_stats.spent_txo_sum + data.mempool_stats.spent_txo_sum;
  const balance = funded - spent;

  out({
    address: data.address,
    balance: `${satsToBtc(balance)} BTC`,
    balanceSats: balance,
    totalReceived: `${satsToBtc(funded)} BTC`,
    totalSent: `${satsToBtc(spent)} BTC`,
    txCount: data.chain_stats.tx_count + data.mempool_stats.tx_count,
    confirmedTxCount: data.chain_stats.tx_count,
    unconfirmedTxCount: data.mempool_stats.tx_count,
    utxoCount: data.chain_stats.funded_txo_count - data.chain_stats.spent_txo_count,
    explorerLink: explorerUrl("btc/mainnet", "address", address),
  });
}

// ── Address info command ────────────────────────────────────────────────────

/**
 * Reverse ENS lookup: given an address, find its primary ENS name.
 * Uses <address>.addr.reverse → resolver → name(bytes32).
 */
async function reverseENS(address) {
  try {
    const { client } = await getEvmClient("ethereum");
    const callFn = client.callContract?.bind(client) || client.call?.bind(client);
    if (!callFn) return null;

    // Build the reverse node: namehash("<lc_addr_no0x>.addr.reverse")
    const addrLower = address.toLowerCase().replace("0x", "");
    const labels = [`${addrLower}`, "addr", "reverse"];

    let node = "0000000000000000000000000000000000000000000000000000000000000000";
    for (let i = labels.length - 1; i >= 0; i--) {
      const labelHex = Buffer.from(labels[i]).toString("hex");
      const labelHashResult = await client.sha3("0x" + labelHex);
      if (!labelHashResult.success) return null;
      const labelHash = labelHashResult.data.slice(2);
      const combined = "0x" + node + labelHash;
      const nodeResult = await client.sha3(combined);
      if (!nodeResult.success) return null;
      node = nodeResult.data.slice(2);
    }

    // Get resolver from ENS registry
    const ENS_REGISTRY = "0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e";
    const resolverResult = await callFn({ to: ENS_REGISTRY, data: "0x0178b8bf" + node });
    if (!resolverResult.success || !resolverResult.data || resolverResult.data === "0x" + "0".repeat(64)) {
      return null;
    }
    const resolverAddr = "0x" + resolverResult.data.slice(26);
    if (resolverAddr === "0x0000000000000000000000000000000000000000") return null;

    // Call name(bytes32) on the resolver — selector 0x691f3431
    const nameResult = await callFn({ to: resolverAddr, data: "0x691f3431" + node });
    if (!nameResult.success || !nameResult.data || nameResult.data === "0x") return null;

    // Decode ABI-encoded string: skip first 64 bytes (offset), next 32 = length, then UTF-8 bytes
    const hex = nameResult.data.slice(2);
    if (hex.length < 128) return null;
    const strLen = parseInt(hex.slice(64, 128), 16);
    if (strLen === 0) return null;
    const strHex = hex.slice(128, 128 + strLen * 2);
    const name = Buffer.from(strHex, "hex").toString("utf-8");
    return name || null;
  } catch {
    return null;
  }
}

/**
 * Look up address in OpenScan metadata labeled addresses.
 */
async function lookupLabeledAddress(address, chainId) {
  try {
    const data = await fetchMetadata(`addresses/evm/${chainId}/all.json`);
    const lc = address.toLowerCase();
    const found = (data.addresses || []).find(a => a.address?.toLowerCase() === lc);
    return found || null;
  } catch {
    return null;
  }
}

async function cmdAddressInfo(rawAddress, chainInput, privateOnly) {
  if (!rawAddress) err("Usage: address-info <address|name.eth> [--chain <chain>] [--private]");

  // Resolve ENS name if provided
  const address = await resolveENS(rawAddress);
  const isENSInput = rawAddress !== address;

  const { client, chainId } = await getEvmClient(chainInput || "ethereum", privateOnly);
  const callFn = client.callContract?.bind(client) || client.call?.bind(client);

  // Fire balance, code, nonce in parallel
  const [balanceResult, codeResult, nonceResult] = await Promise.all([
    client.getBalance(address),
    client.getCode(address),
    client.getTransactionCount(address),
  ]);

  // Parse results
  const nativeBalance = balanceResult.success ? weiToEth(balanceResult.data) : null;
  const nativeBalanceWei = balanceResult.success ? hexToDecimal(balanceResult.data) : null;

  const code = codeResult.success ? codeResult.data : null;
  const isContract = code && code !== "0x" && code !== "0x0";
  const codeSize = isContract ? (code.length - 2) / 2 : 0;

  const txCount = nonceResult.success ? parseInt(hexToDecimal(nonceResult.data), 10) : null;

  // Get currency symbol
  const networksData = await fetchMetadata("networks.json");
  const network = networksData.networks.find(n => n.chainId === chainId);
  const currency = network?.currency || "ETH";

  // ENS reverse lookup (mainnet only — or if already on mainnet)
  let ensName = null;
  if (isENSInput) {
    ensName = rawAddress; // we already know the ENS name
  } else if (chainId === 1) {
    ensName = await reverseENS(address);
  }

  // Labeled address from metadata
  const label = await lookupLabeledAddress(address, chainId);

  // Build output
  const output = {
    address,
    chain: network?.shortName || `Chain ${chainId}`,
    chainId,
    type: isContract ? "contract" : "EOA",
    ...(isContract ? { codeSize: `${codeSize} bytes` } : {}),
    balance: nativeBalance !== null ? `${nativeBalance} ${currency}` : "unavailable",
    balanceWei: nativeBalanceWei,
    txCount: txCount !== null ? txCount : "unavailable",
    ...(ensName ? { ensName } : {}),
    ...(label ? {
      label: {
        name: label.name,
        tags: label.tags || [],
        description: label.description || null,
        website: label.website || null,
      },
    } : {}),
    explorerLink: explorerUrl(chainId, "address", address),
  };

  out(output);
}

// ── Price command ───────────────────────────────────────────────────────────

/**
 * Get the first RPC URL for a chain from persisted config
 */
async function getRpcUrlForChain(chainId) {
  const config = await ensureRpcConfig();
  const effective = getEffectiveRpcs(config, chainId);
  if (!effective || effective.rpcs.length === 0) {
    await fetchAndSaveNetwork(chainId, config);
    const reloaded = await loadConfig();
    const eff = getEffectiveRpcs(reloaded, chainId);
    return eff?.rpcs?.[0]?.url || null;
  }
  return effective.rpcs[0].url;
}

async function cmdPrice(tokenInput, chainInput, privateOnly) {
  // If tokenInput starts with -- it's a flag, not a token
  const token = (tokenInput && !tokenInput.startsWith("--") ? tokenInput : "ETH").toUpperCase();

  if (token === "BTC" || token === "BITCOIN" || token === "WBTC") {
    // BTC price from WBTC pools on mainnet
    const mainnetRpc = await getRpcUrlForChain(1);
    if (!mainnetRpc) err("No RPC configured for Ethereum mainnet. Run: rpc-fetch");
    const result = await getBTCPrice(mainnetRpc);
    if (result.price === null) err("Could not fetch BTC price from on-chain pools");
    out({
      token: "BTC",
      price: formatPrice(result.price),
      priceRaw: Math.round(result.price * 100) / 100,
      method: `on-chain DEX (median of ${result.pools.filter(p => p.price).length} pools)`,
      pools: result.pools.map(p => ({ name: p.name, price: p.price ? Math.round(p.price * 100) / 100 : null })),
      timestamp: new Date().toISOString(),
    });
    return;
  }

  // Native token price for a chain
  const chainId = chainInput ? resolveChain(chainInput) : 1;
  if (chainId === null || typeof chainId === "string") err("Price requires an EVM chain");

  const rpcUrl = await getRpcUrlForChain(chainId);
  if (!rpcUrl) err(`No RPC configured for chain ${chainId}. Run: rpc-fetch`);

  // For L2s, also need mainnet RPC for ETH price
  let mainnetRpc = null;
  if (ETH_NATIVE_CHAINS.has(chainId)) {
    mainnetRpc = await getRpcUrlForChain(1);
  }

  const result = await getNativeTokenPrice(chainId, rpcUrl, mainnetRpc);
  if (result.price === null) err(`Could not fetch price for chain ${chainId}. No DEX pools configured or pools returned no data.`);

  // Determine token symbol
  const tokenSymbols = { 1: "ETH", 10: "ETH", 42161: "ETH", 8453: "ETH", 11155111: "ETH", 137: "MATIC", 56: "BNB" };
  const symbol = token !== "ETH" ? token : (tokenSymbols[chainId] || "NATIVE");

  out({
    token: symbol,
    chainId,
    price: formatPrice(result.price),
    priceRaw: Math.round(result.price * 100) / 100,
    method: `on-chain DEX (median of ${result.pools.filter(p => p.price).length} pools)`,
    pools: result.pools.map(p => ({ name: p.name, price: p.price ? Math.round(p.price * 100) / 100 : null })),
    timestamp: new Date().toISOString(),
  });
}

// ── Decode-tx command ───────────────────────────────────────────────────────

async function cmdDecodeTx(txHash, chainInput, privateOnly) {
  if (!txHash) err("Usage: decode-tx <0xhash> [--chain <chain>]");
  const { client, chainId } = await getEvmClient(chainInput || "ethereum", privateOnly);

  // Fetch tx and receipt in parallel
  const [txResult, receiptResult] = await Promise.all([
    client.getTransactionByHash(txHash),
    client.getTransactionReceipt(txHash),
  ]);

  const tx = txResult.success ? txResult.data : null;
  if (!tx) err(`Transaction ${txHash} not found`);

  const receipt = receiptResult.success ? receiptResult.data : null;

  // Decode function input
  const inputDecoded = await decodeFunctionInput(tx.input || tx.data || "0x");

  // Decode event logs from receipt
  const events = [];
  if (receipt?.logs) {
    for (const log of receipt.logs) {
      const topics = log.topics || [];
      const data = log.data || "0x";
      const decoded = await decodeEventLog(topics, data);
      if (decoded) {
        events.push({
          logIndex: log.logIndex ? parseInt(log.logIndex, 16) : undefined,
          contract: log.address,
          ...decoded,
          params: decoded.params.map(p => ({
            ...p,
            formatted: formatDecodedValue(p.value, p.type),
          })),
        });
      } else {
        // Unknown event — include raw
        events.push({
          logIndex: log.logIndex ? parseInt(log.logIndex, 16) : undefined,
          contract: log.address,
          name: null,
          topic0: topics[0] || null,
          params: [],
          raw: { topics, data },
        });
      }
    }
  }

  // Build result
  const value = tx.value ? weiToEth(tx.value) : "0";
  const gasUsed = receipt?.gasUsed ? hexToDecimal(receipt.gasUsed) : null;
  const status = receipt?.status
    ? (parseInt(receipt.status, 16) === 1 ? "success" : "reverted")
    : "unknown";

  // Determine tx type
  let txType = "contract_call";
  if (!tx.input || tx.input === "0x") txType = "transfer";
  else if (!tx.to) txType = "contract_creation";

  const result = {
    txHash,
    chain: chainInput || "ethereum",
    chainId,
    txType,
    from: tx.from,
    to: tx.to || null,
    value: value > 0 ? `${value} ETH` : "0",
    status,
    gasUsed,
    blockNumber: tx.blockNumber ? parseInt(tx.blockNumber, 16) : null,
  };

  // Add function decode
  if (inputDecoded) {
    if (inputDecoded.functionName) {
      result.function = {
        name: inputDecoded.functionName,
        signature: inputDecoded.signature,
        selector: inputDecoded.selector,
        source: inputDecoded.source,
        params: inputDecoded.params,
      };
    } else if (inputDecoded.selector) {
      result.function = {
        selector: inputDecoded.selector,
        source: "unknown",
        rawCalldata: inputDecoded.rawCalldata,
      };
    }
  }

  // Add events
  if (events.length > 0) {
    result.events = events;
  }

  result.explorerLink = explorerUrl(chainId, "tx", txHash);
  out(result);
}

// ── RPC management commands ─────────────────────────────────────────────────

async function cmdRpcFetch(chainInput) {
  const config = await loadConfig();

  if (chainInput) {
    // Fetch for specific network
    const chainId = resolveChain(chainInput);
    if (chainId === null) err(`Unknown chain: ${chainInput}`);
    const version = config.metadataVersion || await resolveMetadataVersion();
    const path = chainToRpcPath(typeof chainId === "string" ? chainId : chainId);
    const data = await fetchNetworkRpcs(version, path);
    if (!data?.endpoints) err(`No RPC data for chain ${chainInput}`);
    const rpcs = autoSelectRpcs(data.endpoints, {
      maxRpcs: config.defaults.maxRpcs,
      privateOnly: config.defaults.privateOnly,
    });
    setNetworkRpcs(config, chainId, rpcs);
    config.metadataVersion = version;
    config.lastFetched = new Date().toISOString();
    await saveConfig(config);
    out({
      metadataVersion: version,
      chain: chainInput,
      chainId,
      selected: rpcs.length,
      total: data.endpoints.length,
      strategy: config.networks[String(chainId)]?.strategy || config.defaults.strategy,
      rpcs,
    });
  } else {
    // Full sync all networks
    const syncResult = await syncMetadata({
      maxRpcs: config.defaults.maxRpcs,
      privateOnly: config.defaults.privateOnly,
    });
    const { config: merged, stats } = mergeIntoConfig(config, syncResult);
    await saveConfig(merged);
    const summary = {};
    for (const [chainId, net] of Object.entries(merged.networks)) {
      summary[chainId] = {
        selected: net.rpcs?.length || 0,
        total: syncResult.allEndpoints[chainId]?.length || 0,
        strategy: net.strategy || merged.defaults.strategy,
      };
    }
    out({
      metadataVersion: syncResult.version,
      updated: stats.updated,
      unchanged: stats.unchanged,
      newRpcs: stats.newRpcs,
      removedRpcs: stats.removedRpcs,
      networks: summary,
    });
  }
}

async function cmdRpcList(chainInput, showAll, privateOnly) {
  if (!chainInput) err("Usage: rpc-list <chain> [--all] [--private]");
  const chainId = resolveChain(chainInput);
  if (chainId === null) err(`Unknown chain: ${chainInput}`);
  const config = await ensureRpcConfig();

  if (showAll) {
    // Show all available RPCs from metadata
    const version = config.metadataVersion || await resolveMetadataVersion();
    const path = chainToRpcPath(chainId);
    const data = await fetchNetworkRpcs(version, path);
    if (!data?.endpoints) err(`No RPC data for chain ${chainInput}`);

    let endpoints = data.endpoints.filter(e => e.isPublic && !e.url.startsWith("wss://") && !e.url.includes("${"));
    if (privateOnly) endpoints = endpoints.filter(e => e.tracking === "none");

    // Mark which ones are currently active
    const activeUrls = new Set((config.networks[String(chainId)]?.rpcs || []).map(r => r.url));

    out({
      chain: chainInput,
      chainId,
      metadataVersion: version,
      totalEndpoints: endpoints.length,
      tracking: {
        none: endpoints.filter(e => e.tracking === "none").length,
        limited: endpoints.filter(e => e.tracking === "limited").length,
        other: endpoints.filter(e => e.tracking !== "none" && e.tracking !== "limited").length,
      },
      rpcs: endpoints.map((e, i) => ({
        url: e.url,
        tracking: e.tracking,
        provider: e.provider || "unknown",
        isOpenSource: e.isOpenSource || false,
        active: activeUrls.has(e.url),
        ...(activeUrls.has(e.url) ? { position: [...activeUrls].indexOf(e.url) + 1 } : {}),
      })),
    });
  } else {
    // Show active configured RPCs
    const effective = getEffectiveRpcs(config, chainId);
    if (!effective) {
      out({
        chain: chainInput,
        chainId,
        strategy: config.defaults.strategy,
        source: "none",
        rpcs: [],
        hint: "No RPCs configured. Run: rpc-fetch",
      });
      return;
    }
    out({
      chain: chainInput,
      chainId,
      strategy: effective.strategy,
      source: "config",
      metadataVersion: config.metadataVersion,
      lastFetched: config.lastFetched,
      rpcs: effective.rpcs.map((r, i) => ({
        position: i + 1,
        ...r,
      })),
    });
  }
}

async function cmdRpcSet(args, flagValue, hasFlag) {
  const config = await ensureRpcConfig();

  // Global defaults
  if (hasFlag("--default-strategy")) {
    const s = flagValue("--default-strategy");
    if (!["fallback", "race", "parallel"].includes(s)) err("Strategy must be: fallback, race, or parallel");
    config.defaults.strategy = s;
    await saveConfig(config);
    out({ defaultStrategy: s });
    return;
  }
  if (hasFlag("--max-rpcs")) {
    const n = parseInt(flagValue("--max-rpcs"), 10);
    if (isNaN(n) || n < 1) err("--max-rpcs must be a positive integer");
    config.defaults.maxRpcs = n;
    await saveConfig(config);
    out({ defaultMaxRpcs: n });
    return;
  }

  const chainInput = args[1];
  if (!chainInput) err("Usage: rpc-set <chain> [--strategy <s>] [--add <url>] [--remove <url>] [--rpcs <url>...] [--reset] [--private-only]");
  const chainId = resolveChain(chainInput);
  if (chainId === null) err(`Unknown chain: ${chainInput}`);

  // --reset
  if (hasFlag("--reset")) {
    resetNetwork(config, chainId);
    // Re-fetch from metadata
    await fetchAndSaveNetwork(chainId, config);
    const reloaded = await loadConfig();
    out({ chain: chainInput, chainId, action: "reset", rpcs: reloaded.networks[String(chainId)]?.rpcs || [] });
    return;
  }

  // --strategy
  if (hasFlag("--strategy")) {
    const s = flagValue("--strategy");
    if (!["fallback", "race", "parallel"].includes(s)) err("Strategy must be: fallback, race, or parallel");
    setNetworkStrategy(config, chainId, s);
  }

  // --private-only
  if (hasFlag("--private-only")) {
    const net = config.networks[String(chainId)];
    if (net?.rpcs) {
      net.rpcs = net.rpcs.filter(r => r.tracking === "none");
    }
  }

  // --add <url> [url2...]
  if (hasFlag("--add")) {
    const idx = args.indexOf("--add");
    const urls = [];
    for (let i = idx + 1; i < args.length; i++) {
      if (args[i].startsWith("--")) break;
      urls.push(args[i]);
    }
    if (urls.length === 0) err("--add requires at least one URL");
    const newRpcs = urls.map(url => ({ url, tracking: "unknown", provider: "custom", isOpenSource: false }));
    addNetworkRpcs(config, chainId, newRpcs);
  }

  // --remove <url>
  if (hasFlag("--remove")) {
    const url = flagValue("--remove");
    if (!url) err("--remove requires a URL");
    removeNetworkRpc(config, chainId, url);
  }

  // --rpcs <url1> <url2> ... (replace all)
  if (hasFlag("--rpcs")) {
    const idx = args.indexOf("--rpcs");
    const urls = [];
    for (let i = idx + 1; i < args.length; i++) {
      if (args[i].startsWith("--")) break;
      urls.push(args[i]);
    }
    if (urls.length === 0) err("--rpcs requires at least one URL");
    const rpcs = urls.map(url => ({ url, tracking: "unknown", provider: "custom", isOpenSource: false }));
    setNetworkRpcs(config, chainId, rpcs);
  }

  await saveConfig(config);
  const effective = getEffectiveRpcs(config, chainId);
  out({
    chain: chainInput,
    chainId,
    strategy: effective?.strategy || config.defaults.strategy,
    rpcs: effective?.rpcs || [],
  });
}

async function cmdRpcOrder(args, flagValue, hasFlag) {
  const chainInput = args[1];
  if (!chainInput) err("Usage: rpc-order <chain> [<url> --position N] [--swap A B] [--benchmark]");
  const chainId = resolveChain(chainInput);
  if (chainId === null) err(`Unknown chain: ${chainInput}`);
  const config = await ensureRpcConfig();

  if (hasFlag("--benchmark")) {
    // Benchmark all configured RPCs and reorder by latency
    const effective = getEffectiveRpcs(config, chainId);
    if (!effective || effective.rpcs.length === 0) err(`No RPCs configured for chain ${chainInput}`);

    const results = await benchmarkRpcs(effective.rpcs.map(r => r.url));
    // Sort by latency (ok first, then errors)
    const sorted = [...results].sort((a, b) => {
      if (a.status === "ok" && b.status !== "ok") return -1;
      if (a.status !== "ok" && b.status === "ok") return 1;
      return a.latencyMs - b.latencyMs;
    });

    // Rebuild RPC list in latency order
    const rpcMap = new Map(effective.rpcs.map(r => [r.url, r]));
    const reordered = sorted.map(r => rpcMap.get(r.url)).filter(Boolean);
    setNetworkRpcs(config, chainId, reordered, effective.strategy);
    await saveConfig(config);

    out({
      chain: chainInput,
      chainId,
      action: "benchmark-reorder",
      results: sorted,
      newOrder: reordered.map((r, i) => ({ position: i + 1, url: r.url, provider: r.provider })),
    });
    return;
  }

  if (hasFlag("--swap")) {
    const idx = args.indexOf("--swap");
    const a = parseInt(args[idx + 1], 10);
    const b = parseInt(args[idx + 2], 10);
    if (isNaN(a) || isNaN(b)) err("--swap requires two position numbers (1-indexed)");
    swapRpcs(config, chainId, a, b);
    await saveConfig(config);
    out({ chain: chainInput, action: "swap", positions: [a, b], rpcs: config.networks[String(chainId)]?.rpcs || [] });
    return;
  }

  // Move URL to position: rpc-order <chain> <url> --position N
  // args[0] = "rpc-order", args[1] = chain, args[2] = url
  const url = args[2];
  if (url && !url.startsWith("--") && hasFlag("--position")) {
    const pos = parseInt(flagValue("--position"), 10);
    if (isNaN(pos)) err("--position requires a number (1-indexed)");
    const rpcs = config.networks[String(chainId)]?.rpcs || [];
    const fromIdx = rpcs.findIndex(r => r.url === url);
    if (fromIdx === -1) err(`URL not found in config: ${url}`);
    moveRpc(config, chainId, fromIdx, pos - 1);
    await saveConfig(config);
    out({ chain: chainInput, action: "move", url, toPosition: pos, rpcs: config.networks[String(chainId)]?.rpcs || [] });
    return;
  }

  err("Usage: rpc-order <chain> [<url> --position N] [--swap A B] [--benchmark]");
}

/**
 * Benchmark a list of RPC URLs — test latency, block number, client version
 */
async function benchmarkRpcs(urls) {
  const results = await Promise.all(urls.map(async (url) => {
    const start = Date.now();
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify([
          { jsonrpc: "2.0", id: 1, method: "eth_blockNumber", params: [] },
          { jsonrpc: "2.0", id: 2, method: "web3_clientVersion", params: [] },
        ]),
        signal: AbortSignal.timeout(10000),
      });
      const latencyMs = Date.now() - start;
      const data = await res.json();

      // Handle both batch and single responses
      const responses = Array.isArray(data) ? data : [data];
      const blockRes = responses.find(r => r.id === 1);
      const versionRes = responses.find(r => r.id === 2);

      const blockNumber = blockRes?.result ? parseInt(blockRes.result, 16) : null;
      const clientVersion = versionRes?.result || null;

      return { url, status: "ok", latencyMs, blockNumber, clientVersion };
    } catch (e) {
      return { url, status: "error", latencyMs: Date.now() - start, error: e.message };
    }
  }));

  // Calculate block delta (max block - each block)
  const maxBlock = Math.max(...results.filter(r => r.blockNumber).map(r => r.blockNumber));
  for (const r of results) {
    if (r.blockNumber) {
      r.blockDelta = r.blockNumber - maxBlock;
    }
  }

  return results;
}

async function cmdRpcTest(args, flagValue, hasFlag) {
  const chainInput = args[1];
  if (!chainInput) err("Usage: rpc-test <chain> [<url>] [--all]");
  const chainId = resolveChain(chainInput);
  if (chainId === null) err(`Unknown chain: ${chainInput}`);

  const config = await ensureRpcConfig();

  let urls;
  const specificUrl = args[2] && !args[2].startsWith("--") ? args[2] : null;

  if (specificUrl) {
    urls = [specificUrl];
  } else if (hasFlag("--all")) {
    // Test all available RPCs from metadata
    const version = config.metadataVersion || await resolveMetadataVersion();
    const path = chainToRpcPath(chainId);
    const data = await fetchNetworkRpcs(version, path);
    if (!data?.endpoints) err(`No RPC data for chain ${chainInput}`);
    urls = data.endpoints
      .filter(e => e.isPublic && !e.url.startsWith("wss://") && !e.url.includes("${"))
      .map(e => e.url);
  } else {
    const effective = getEffectiveRpcs(config, chainId);
    if (!effective || effective.rpcs.length === 0) err(`No RPCs configured for chain ${chainInput}. Run: rpc-fetch`);
    urls = effective.rpcs.map(r => r.url);
  }

  const results = await benchmarkRpcs(urls);

  // Generate recommendation
  const okResults = results.filter(r => r.status === "ok").sort((a, b) => a.latencyMs - b.latencyMs);
  let recommendation = null;
  if (okResults.length > 0) {
    const fastest = okResults[0];
    const behind = okResults.filter(r => r.blockDelta < 0);
    const parts = [`${new URL(fastest.url).hostname} is fastest (${fastest.latencyMs}ms)`];
    for (const r of behind) {
      parts.push(`${new URL(r.url).hostname} is ${Math.abs(r.blockDelta)} blocks behind`);
    }
    recommendation = parts.join(". ");
  }

  out({
    chain: chainInput,
    chainId,
    timestamp: new Date().toISOString(),
    tested: results.length,
    ok: okResults.length,
    failed: results.length - okResults.length,
    results,
    recommendation,
  });
}

async function cmdRpcStrategy(args) {
  const config = await loadConfig();
  if (!args[1]) {
    // View current defaults
    out({
      defaultStrategy: config.defaults.strategy,
      maxRpcs: config.defaults.maxRpcs,
      privateOnly: config.defaults.privateOnly,
      networkOverrides: Object.entries(config.networks)
        .filter(([_, v]) => v.strategy)
        .map(([k, v]) => ({ chainId: k, strategy: v.strategy })),
    });
    return;
  }
  const s = args[1];
  if (!["fallback", "race", "parallel"].includes(s)) err("Strategy must be: fallback, race, or parallel");
  config.defaults.strategy = s;
  await saveConfig(config);
  out({ defaultStrategy: s });
}

// ── CLI router ──────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log(`openscan-crypto CLI

Metadata commands:
  networks                              List supported networks
  rpcs <chain> [--private]              List RPC endpoints
  token <symbol|address> [--chain]      Look up token info
  events [--chain <chain>]              List known event signatures
  decode-event <topic>                  Decode event topic hash
  addresses [--chain <chain>]           List labeled addresses
  profile <type> <id>                   Show profile

EVM queries (use --chain <chain>, default: ethereum, supports .eth names):
  balance <address> [--token <sym>]     Native + ERC20 balance
  multi-balance <address>               Balance across ALL chains
  block [number|hash|latest]            Block info
  tx <0xhash>                           Transaction details
  receipt <0xhash>                      Transaction receipt + logs
  gas                                   Gas price + base fee
  call <to> <data>  [--block <tag>]     eth_call (read contract)
  logs --address <addr> [--topic <t>]   Event logs (--from/--to blocks)
  code <address>                        Contract code / EOA check
  nonce <address>                       Transaction count

Bitcoin queries (mempool.space REST API):
  btc-info                              Blockchain overview + mempool + fees
  btc-block [height|hash|latest]        Block details
  btc-tx <txid>                         Transaction details
  btc-mempool                           Mempool state + recent txs
  btc-fee                               Recommended fee rates
  btc-address <address>                 Address balance + tx count

Price & Analysis:
  price [ETH|BTC|MATIC|BNB]              On-chain token price from DEX pools
  price --chain polygon                   Native token price for a specific chain
  decode-tx <0xhash>                      Decode tx function call + event logs
  address-info <address|name.eth>         Aggregate address info: type, balance, nonce, ENS, label

RPC management:
  rpc-fetch [chain]                     Sync RPCs from metadata (all or one network)
  rpc-list <chain> [--all] [--private]  Show active or all available RPCs
  rpc-set <chain> [options]             Configure RPCs (--strategy, --add, --remove, --rpcs, --reset)
  rpc-order <chain> [options]           Reorder RPCs (--benchmark, --swap A B, <url> --position N)
  rpc-test <chain> [url] [--all]        Test/benchmark RPC latency
  rpc-strategy [fallback|race|parallel] View/set default strategy

Flags: --chain <chain>, --private (tracking:none RPCs only)
Chain aliases: ethereum/eth, bitcoin/btc, arbitrum/arb, optimism/op, base, polygon/matic, bnb/bsc
`);
    return;
  }

  const cmd = args[0];
  const flagIndex = (flag) => args.indexOf(flag);
  const flagValue = (flag) => {
    const idx = flagIndex(flag);
    return idx !== -1 && idx + 1 < args.length ? args[idx + 1] : null;
  };
  const hasFlag = (flag) => args.includes(flag);

  try {
    switch (cmd) {
      case "networks":
        await cmdNetworks();
        break;

      case "rpcs":
        if (!args[1]) err("Usage: rpcs <chain> [--private]");
        await cmdRpcs(args[1], hasFlag("--private"));
        break;

      case "token":
        if (!args[1]) err("Usage: token <symbol|address> [--chain <chain>]");
        await cmdToken(args[1], flagValue("--chain"));
        break;

      case "events":
        await cmdEvents(flagValue("--chain"));
        break;

      case "decode-event":
        if (!args[1]) err("Usage: decode-event <topic_hash>");
        await cmdDecodeEvent(args[1]);
        break;

      case "addresses":
        await cmdAddresses(flagValue("--chain"));
        break;

      case "profile":
        if (!args[1] || !args[2]) err("Usage: profile <type> <id>");
        await cmdProfile(args[1], args[2]);
        break;

      // ── Phase 2: EVM queries ──
      case "balance":
        if (!args[1]) err("Usage: balance <address|name.eth> [--token <symbol>] [--chain <chain>] [--private]");
        await cmdBalance(await resolveENS(args[1]), flagValue("--chain"), flagValue("--token"), hasFlag("--private"));
        break;

      case "multi-balance":
        if (!args[1]) err("Usage: multi-balance <address|name.eth> [--private]");
        await cmdMultiBalance(await resolveENS(args[1]), hasFlag("--private"));
        break;

      case "block":
        await cmdBlock(args[1] || "latest", flagValue("--chain"), hasFlag("--private"));
        break;

      case "tx":
        if (!args[1]) err("Usage: tx <0xhash> [--chain <chain>]");
        await cmdTx(args[1], flagValue("--chain"), hasFlag("--private"));
        break;

      case "receipt":
        if (!args[1]) err("Usage: receipt <0xhash> [--chain <chain>]");
        await cmdReceipt(args[1], flagValue("--chain"), hasFlag("--private"));
        break;

      case "gas":
        await cmdGas(flagValue("--chain"), hasFlag("--private"));
        break;

      case "call":
        if (!args[1] || !args[2]) err("Usage: call <to_address> <calldata> [--chain <chain>] [--block <tag>]");
        await cmdCall(args[1], args[2], flagValue("--chain"), flagValue("--block"), hasFlag("--private"));
        break;

      case "logs": {
        const address = flagValue("--address");
        const topic = flagValue("--topic");
        const fromBlock = flagValue("--from");
        const toBlock = flagValue("--to");
        await cmdLogs(flagValue("--chain"), address, topic ? [topic] : [], fromBlock, toBlock, hasFlag("--private"));
        break;
      }

      case "code":
        if (!args[1]) err("Usage: code <address|name.eth> [--chain <chain>]");
        await cmdCode(await resolveENS(args[1]), flagValue("--chain"), hasFlag("--private"));
        break;

      case "nonce":
        if (!args[1]) err("Usage: nonce <address|name.eth> [--chain <chain>]");
        await cmdNonce(await resolveENS(args[1]), flagValue("--chain"), hasFlag("--private"));
        break;

      // ── Phase 3: Bitcoin queries ──
      case "btc-info":
        await cmdBtcInfo();
        break;

      case "btc-block":
        await cmdBtcBlock(args[1]);
        break;

      case "btc-tx":
        if (!args[1]) err("Usage: btc-tx <txid>");
        await cmdBtcTx(args[1]);
        break;

      case "btc-mempool":
        await cmdBtcMempool();
        break;

      case "btc-fee":
        await cmdBtcFee();
        break;

      case "btc-address":
        if (!args[1]) err("Usage: btc-address <address>");
        await cmdBtcAddress(args[1]);
        break;

      // ── Price & Analysis ──
      case "price":
        await cmdPrice(args[1], flagValue("--chain"), hasFlag("--private"));
        break;

      case "decode-tx":
        await cmdDecodeTx(args[1], flagValue("--chain"), hasFlag("--private"));
        break;

      case "address-info":
        if (!args[1]) err("Usage: address-info <address|name.eth> [--chain <chain>] [--private]");
        await cmdAddressInfo(args[1], flagValue("--chain"), hasFlag("--private"));
        break;

      // ── RPC management ──
      case "rpc-fetch":
        await cmdRpcFetch(args[1]);
        break;

      case "rpc-list":
        await cmdRpcList(args[1], hasFlag("--all"), hasFlag("--private"));
        break;

      case "rpc-set":
        await cmdRpcSet(args, flagValue, hasFlag);
        break;

      case "rpc-order":
        await cmdRpcOrder(args, flagValue, hasFlag);
        break;

      case "rpc-test":
        await cmdRpcTest(args, flagValue, hasFlag);
        break;

      case "rpc-strategy":
        await cmdRpcStrategy(args);
        break;

      default:
        err(`Unknown command: ${cmd}. Run without arguments for help.`);
    }
  } catch (e) {
    err(e.message);
  }
}

main();
