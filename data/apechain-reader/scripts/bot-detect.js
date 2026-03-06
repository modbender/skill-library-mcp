#!/usr/bin/env node
// Multi-chain Bot Detection — scores a wallet for bot behavior (0-100)
// Usage: node bot-detect.js <address> [--chain apechain]

const { getChain, rpcCall, padAddress, unpadAddress, hexToNumber, parseArgs, TRANSFER_TOPIC, formatOutput } = require("./lib/rpc");

const WEIGHTS = { WAPE_RATIO: 30, FAST_FLIP: 25, FAST_LIST: 20, AGGRESSIVE_PRICING: 15, CROSS_COLLECTION: 10 };
const THRESHOLDS = { MIN_BUYS: 3, FAST_FLIP_HOURS: 24, FAST_LIST_MINUTES: 30 };

// Wrapped native token contracts per chain
const WRAPPED_TOKENS = {
  apechain: "0x48b62137edfa95a428d35c09e44256a739f6b557",
  ethereum: "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
  base: "0x4200000000000000000000000000000000000006",
  arbitrum: "0x82af49447d8a07e3bd95bd0d56f35241523fbab1",
  polygon: "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270",
  optimism: "0x4200000000000000000000000000000000000006",
  bsc: "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c",
};

async function initArgs() {
  try {
    return await parseArgs(process.argv);
  } catch (err) {
    console.log(formatOutput({ error: err.message }, "json"));
    process.exit(1);
  }
}

async function main() {
  const { address, chainName, outputFormat } = await initArgs();
  const chain = getChain(chainName);
  const rpc = chain.rpc;
  const wrappedToken = WRAPPED_TOKENS[chainName?.toLowerCase()] || WRAPPED_TOKENS.apechain;

  const latestBlock = await rpcCall(rpc, "eth_blockNumber", []);
  const latestNum = hexToNumber(latestBlock);
  const fromBlock = "0x" + Math.max(0, latestNum - 1000000).toString(16);
  const addrPadded = padAddress(address);

  // Fetch NFT transfers + ERC-20 transfers in parallel
  const [nftIn, nftOut, erc20Out] = await Promise.all([
    rpcCall(rpc, "eth_getLogs", [{ fromBlock, toBlock: "latest", topics: [TRANSFER_TOPIC, null, addrPadded] }]).catch(() => []),
    rpcCall(rpc, "eth_getLogs", [{ fromBlock, toBlock: "latest", topics: [TRANSFER_TOPIC, addrPadded, null] }]).catch(() => []),
    rpcCall(rpc, "eth_getLogs", [{ fromBlock, toBlock: "latest", address: wrappedToken, topics: [TRANSFER_TOPIC, addrPadded, null] }]).catch(() => []),
  ]);

  // Parse ERC-721 only (4 topics)
  const buys = (nftIn || []).filter(l => l.topics?.length === 4).map(l => ({
    contract: l.address?.toLowerCase(),
    tokenId: l.topics[3],
    block: hexToNumber(l.blockNumber),
    txHash: l.transactionHash,
  }));

  const sells = (nftOut || []).filter(l => l.topics?.length === 4).map(l => ({
    contract: l.address?.toLowerCase(),
    tokenId: l.topics[3],
    block: hexToNumber(l.blockNumber),
    txHash: l.transactionHash,
  }));

  if (buys.length < THRESHOLDS.MIN_BUYS) {
    console.log(formatOutput({
      address, chain: chain.name, botScore: 0, verdict: "insufficient_data",
      note: `Only ${buys.length} NFT buys found (min ${THRESHOLDS.MIN_BUYS})`,
      breakdown: { wapeRatio: 0, fastFlip: 0, fastList: 0, aggressivePricing: 0, crossCollection: 0 },
    }, outputFormat));
    return;
  }

  // Get block timestamps for timing analysis
  const allBlocks = new Set([...buys.map(b => b.block), ...sells.map(s => s.block)]);
  const blockTimes = {};
  const sampleBlocks = [...allBlocks].slice(0, 50);
  await Promise.all(sampleBlocks.map(async bn => {
    try {
      const b = await rpcCall(rpc, "eth_getBlockByNumber", ["0x" + bn.toString(16), false]);
      if (b) blockTimes[bn] = hexToNumber(b.timestamp);
    } catch {}
  }));

  // 1. Wrapped token ratio (30pts)
  const wrappedTxHashes = new Set((erc20Out || []).map(l => l.transactionHash));
  const wrappedBuys = buys.filter(b => wrappedTxHashes.has(b.txHash)).length;
  const wrappedRatio = buys.length > 0 ? wrappedBuys / buys.length : 0;
  const wrappedScore = Math.round(wrappedRatio * WEIGHTS.WAPE_RATIO);

  // 2. Fast Flip (25pts) — buy + sell same tokenId within 24h
  const buyMap = new Map(); // `contract:tokenId` -> timestamp
  for (const b of buys) {
    if (blockTimes[b.block]) buyMap.set(`${b.contract}:${b.tokenId}`, blockTimes[b.block]);
  }
  let fastFlips = 0;
  for (const s of sells) {
    const key = `${s.contract}:${s.tokenId}`;
    const buyTs = buyMap.get(key);
    const sellTs = blockTimes[s.block];
    if (buyTs && sellTs && (sellTs - buyTs) < THRESHOLDS.FAST_FLIP_HOURS * 3600) fastFlips++;
  }
  const flipRate = sells.length > 0 ? fastFlips / sells.length : 0;
  const fastFlipScore = Math.round(Math.min(flipRate * 2, 1) * WEIGHTS.FAST_FLIP);

  // 3. Fast List (20pts) — sell very soon after buy
  let fastLists = 0;
  for (const s of sells) {
    const key = `${s.contract}:${s.tokenId}`;
    const buyTs = buyMap.get(key);
    const sellTs = blockTimes[s.block];
    if (buyTs && sellTs && (sellTs - buyTs) < THRESHOLDS.FAST_LIST_MINUTES * 60) fastLists++;
  }
  const fastListRate = sells.length > 0 ? fastLists / sells.length : 0;
  const fastListScore = Math.round(Math.min(fastListRate * 3, 1) * WEIGHTS.FAST_LIST);

  // 4. Aggressive Pricing (15pts) — heuristic from velocity
  const aggressiveScore = Math.round(Math.min((fastFlips + fastLists) / Math.max(buys.length, 1), 1) * WEIGHTS.AGGRESSIVE_PRICING);

  // 5. Cross-Collection (10pts)
  const collections = new Set(buys.map(b => b.contract));
  const crossScore = Math.round(Math.min(collections.size / 10, 1) * WEIGHTS.CROSS_COLLECTION);

  const totalScore = wrappedScore + fastFlipScore + fastListScore + aggressiveScore + crossScore;

  let verdict = "human";
  if (totalScore >= 75) verdict = "definite_bot";
  else if (totalScore >= 60) verdict = "likely_bot";
  else if (totalScore >= 40) verdict = "suspicious";
  else if (totalScore >= 20) verdict = "probably_human";

  console.log(formatOutput({
    address,
    chain: chain.name,
    botScore: totalScore,
    verdict,
    breakdown: {
      wrappedTokenRatio: { score: wrappedScore, max: WEIGHTS.WAPE_RATIO, detail: `${wrappedBuys}/${buys.length} buys with wrapped token (${(wrappedRatio * 100).toFixed(1)}%)` },
      fastFlip: { score: fastFlipScore, max: WEIGHTS.FAST_FLIP, detail: `${fastFlips} flips within ${THRESHOLDS.FAST_FLIP_HOURS}h` },
      fastList: { score: fastListScore, max: WEIGHTS.FAST_LIST, detail: `${fastLists} listed within ${THRESHOLDS.FAST_LIST_MINUTES}min` },
      aggressivePricing: { score: aggressiveScore, max: WEIGHTS.AGGRESSIVE_PRICING, detail: "Estimated from sell velocity" },
      crossCollection: { score: crossScore, max: WEIGHTS.CROSS_COLLECTION, detail: `Active in ${collections.size} collections` },
    },
    stats: { totalBuys: buys.length, totalSells: sells.length, collections: collections.size, wrappedBuys, fastFlips, fastLists },
  }, outputFormat));
}

main().catch(err => {
  console.log(formatOutput({ error: err.message }, "json"));
  process.exit(1);
});
