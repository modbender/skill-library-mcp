#!/usr/bin/env node
// Multi-chain NFT Holdings via RPC — ERC-721 Transfer events
// Usage: node nft-holdings.js <address> [--chain apechain] [--collection <contract>]

const { getChain, rpcCall, padAddress, hexToNumber, parseArgs, TRANSFER_TOPIC, formatOutput, resolveCollectionName } = require("./lib/rpc");

async function initArgs() {
  try {
    return await parseArgs(process.argv);
  } catch (err) {
    console.log(formatOutput({ error: err.message }, "json"));
    process.exit(1);
  }
}

async function main() {
  const { address, chainName, args, outputFormat } = await initArgs();
  
  const collIdx = args.indexOf("--collection");
  const filterCollection = collIdx >= 0 ? args[collIdx + 1]?.toLowerCase() : null;
  
  const chain = getChain(chainName);
  const rpc = chain.rpc;

  const latestBlock = await rpcCall(rpc, "eth_blockNumber", []);
  const latestNum = hexToNumber(latestBlock);
  const fromBlock = "0x" + Math.max(0, latestNum - 2000000).toString(16); // ~2M blocks back
  const addrPadded = padAddress(address);

  // NFT transfers: ERC-721 has 4 topics (event, from, to, tokenId)
  const logParams = { fromBlock, toBlock: "latest", topics: [TRANSFER_TOPIC] };
  if (filterCollection) logParams.address = filterCollection;

  const [logsTo, logsFrom] = await Promise.all([
    rpcCall(rpc, "eth_getLogs", [{ ...logParams, topics: [TRANSFER_TOPIC, null, addrPadded] }]).catch(() => []),
    rpcCall(rpc, "eth_getLogs", [{ ...logParams, topics: [TRANSFER_TOPIC, addrPadded, null] }]).catch(() => []),
  ]);

  // Only ERC-721 (4 topics)
  const nftIn = (logsTo || []).filter(l => l.topics?.length === 4);
  const nftOut = (logsFrom || []).filter(l => l.topics?.length === 4);

  // Build ownership: contract -> Set(tokenId)
  const ownership = new Map();
  const stats = new Map(); // contract -> { inCount, outCount }

  for (const log of nftIn) {
    const contract = log.address?.toLowerCase();
    const tokenId = log.topics[3];
    if (!ownership.has(contract)) { ownership.set(contract, new Set()); stats.set(contract, { inCount: 0, outCount: 0 }); }
    ownership.get(contract).add(tokenId);
    stats.get(contract).inCount++;
  }

  for (const log of nftOut) {
    const contract = log.address?.toLowerCase();
    const tokenId = log.topics[3];
    if (ownership.has(contract)) ownership.get(contract).delete(tokenId);
    if (!stats.has(contract)) stats.set(contract, { inCount: 0, outCount: 0 });
    stats.get(contract).outCount++;
  }

  const holdingsList = [...ownership.entries()]
    .filter(([, tokens]) => tokens.size > 0)
    .map(([contract, tokens]) => ({
      contract,
      held: tokens.size,
      totalIn: stats.get(contract)?.inCount || 0,
      totalOut: stats.get(contract)?.outCount || 0,
      tokenIds: [...tokens].slice(0, 20).map(t => hexToNumber(t)),
    }))
    .sort((a, b) => b.held - a.held);

  // Resolve collection names
  const holdings = await Promise.all(holdingsList.map(async (holding) => ({
    ...holding,
    name: await resolveCollectionName(holding.contract, chainName)
  })));

  console.log(formatOutput({
    address,
    chain: chain.name,
    totalNFTs: holdings.reduce((s, h) => s + h.held, 0),
    collections: holdings.length,
    holdings,
  }, outputFormat));
}

main().catch(err => {
  console.log(formatOutput({ error: err.message }, "json"));
  process.exit(1);
});
