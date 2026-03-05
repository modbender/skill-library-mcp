#!/usr/bin/env node
// ApeChain/Multi-chain Wallet Lookup — returns wallet profile as JSON
// Usage: node wallet-lookup.js <address> [--chain apechain|ethereum|base|arbitrum|polygon|optimism|avalanche|bsc]

const { getChain, rpcCall, padAddress, unpadAddress, hexToNumber, parseArgs, TRANSFER_TOPIC, formatOutput, resolveCollectionName, getTokenPrice } = require("./lib/rpc");

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

  // Handle special addresses that could cause performance issues
  const isZeroAddress = address.toLowerCase() === "0x0000000000000000000000000000000000000000";
  const isDeadAddress = address.toLowerCase() === "0xdeaddeaddeaddeaddeaddeaddeaddeaddeaddead";

  // Parallel: balance, tx count, code check, recent blocks for activity
  const [balanceHex, txCountHex, code] = await Promise.all([
    rpcCall(rpc, "eth_getBalance", [address, "latest"]),
    rpcCall(rpc, "eth_getTransactionCount", [address, "latest"]),
    rpcCall(rpc, "eth_getCode", [address, "latest"]),
  ]);

  const balanceWei = BigInt(balanceHex || "0x0");
  const balance = Number(balanceWei) / 1e18;
  const txCount = parseInt(txCountHex || "0x0", 16);
  const isContract = code && code !== "0x" && code !== "0x0";

  // Get USD price for the token
  const tokenPrice = await getTokenPrice(chainName);
  const balanceUSD = tokenPrice ? balance * tokenPrice : null;

  // Get latest block for range calc
  const latestBlock = await rpcCall(rpc, "eth_blockNumber", []);
  const latestNum = hexToNumber(latestBlock);

  // Scan last ~500K blocks for NFT transfers (ERC-721 Transfer events)
  // Skip log queries for problematic addresses (zero/dead) to avoid timeouts
  let logsTo = [], logsFrom = [];
  
  if (!isZeroAddress && !isDeadAddress) {
    const fromBlock = "0x" + Math.max(0, latestNum - 500000).toString(16);
    const addrPadded = padAddress(address);

    [logsTo, logsFrom] = await Promise.all([
      rpcCall(rpc, "eth_getLogs", [{ fromBlock, toBlock: "latest", topics: [TRANSFER_TOPIC, null, addrPadded] }]).catch(() => []),
      rpcCall(rpc, "eth_getLogs", [{ fromBlock, toBlock: "latest", topics: [TRANSFER_TOPIC, addrPadded, null] }]).catch(() => []),
    ]);
  }

  // Parse NFT transfers (ERC-721 has 4 topics: event, from, to, tokenId)
  const nftIn = (logsTo || []).filter(l => l.topics?.length === 4);
  const nftOut = (logsFrom || []).filter(l => l.topics?.length === 4);

  // Build collection map with resolved names
  const holdings = new Map();
  for (const log of nftIn) {
    const contract = log.address?.toLowerCase();
    if (!holdings.has(contract)) holdings.set(contract, new Set());
    holdings.get(contract).add(log.topics[3]); // tokenId
  }
  for (const log of nftOut) {
    const contract = log.address?.toLowerCase();
    if (holdings.has(contract)) holdings.get(contract).delete(log.topics[3]);
  }

  // Resolve collection names for holdings
  const collections = await Promise.all([...holdings.entries()]
    .filter(([, tokens]) => tokens.size > 0)
    .map(async ([contract, tokens]) => ({
      contract,
      name: await resolveCollectionName(contract, chainName),
      count: tokens.size
    })));
  
  collections.sort((a, b) => b.count - a.count);

  // Activity timestamps from logs
  const allLogs = [...(logsTo || []), ...(logsFrom || [])];
  let firstBlock = null, lastBlock = null;
  for (const log of allLogs) {
    const bn = hexToNumber(log.blockNumber);
    if (!firstBlock || bn < firstBlock) firstBlock = bn;
    if (!lastBlock || bn > lastBlock) lastBlock = bn;
  }

  const result = {
    address,
    chain: chain.name,
    chainId: chain.id,
    isContract,
    balance: { [chain.symbol]: Math.round(balance * 10000) / 10000 },
    balanceUSD: balanceUSD ? Math.round(balanceUSD * 100) / 100 : null,
    transactionCount: txCount,
    nftActivity: { received: nftIn.length, sent: nftOut.length },
    nftCollectionsHeld: collections.length,
    topHoldings: collections.slice(0, 10),
    explorer: `${chain.explorer}/address/${address}`,
  };

  // Generate natural language summary for pretty mode
  if (outputFormat === "pretty") {
    const totalNFTs = collections.reduce((sum, c) => sum + c.count, 0);
    const balanceStr = balanceUSD 
      ? `~$${balanceUSD.toFixed(2)} in ${chain.symbol}`
      : `${balance.toFixed(4)} ${chain.symbol}`;
    
    let summary = `📋 `;
    if (isContract) {
      summary += `Smart contract on ${chain.name} with ${balanceStr}`;
    } else {
      const activity = txCount > 100 ? "Active" : txCount > 10 ? "Moderate" : "Low-activity";
      summary += `${activity} ${chain.name} wallet with ${balanceStr}`;
      if (totalNFTs > 0) {
        summary += `, ${totalNFTs} NFT${totalNFTs !== 1 ? 's' : ''} across ${collections.length} collection${collections.length !== 1 ? 's' : ''}`;
      }
    }
    summary += `.`;
    
    // Add to result for pretty formatting
    result.summary = summary;
  }

  console.log(formatOutput(result, outputFormat));
}

main().catch(err => {
  console.log(formatOutput({ error: err.message }, "json"));
  process.exit(1);
});
