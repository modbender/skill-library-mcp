#!/usr/bin/env node
// Multi-chain Transaction History via RPC — recent blocks
// Usage: node tx-history.js <address> [--chain apechain] [--limit 20]

const { getChain, rpcCall, hexToNumber, parseArgs, TRANSFER_TOPIC, formatOutput } = require("./lib/rpc");

async function initArgs() {
  try {
    return await parseArgs(process.argv);
  } catch (err) {
    console.log(formatOutput({ error: err.message }, "json"));
    process.exit(1);
  }
}

async function main() {
  const { address, chainName, limit, outputFormat } = await initArgs();
  const chain = getChain(chainName);
  const rpc = chain.rpc;

  const latestBlock = await rpcCall(rpc, "eth_blockNumber", []);
  const latestNum = hexToNumber(latestBlock);

  // Scan last 100K blocks for Transfer events involving this address
  const fromBlock = "0x" + Math.max(0, latestNum - 2000000).toString(16);
  const addrPadded = "0x" + address.replace("0x", "").padStart(64, "0");

  // Get ERC-20 + ERC-721 transfers (both use Transfer topic)
  const [logsTo, logsFrom] = await Promise.all([
    rpcCall(rpc, "eth_getLogs", [{ fromBlock, toBlock: "latest", topics: [TRANSFER_TOPIC, null, addrPadded] }]).catch(() => []),
    rpcCall(rpc, "eth_getLogs", [{ fromBlock, toBlock: "latest", topics: [TRANSFER_TOPIC, addrPadded, null] }]).catch(() => []),
  ]);

  const allLogs = [...(logsTo || []), ...(logsFrom || [])].sort((a, b) =>
    hexToNumber(b.blockNumber) - hexToNumber(a.blockNumber)
  );

  // Get block timestamps for unique blocks
  const uniqueBlocks = [...new Set(allLogs.slice(0, limit).map(l => l.blockNumber))];
  const blockTimestamps = {};
  await Promise.all(
    uniqueBlocks.slice(0, 20).map(async bn => {
      try {
        const block = await rpcCall(rpc, "eth_getBlockByNumber", [bn, false]);
        if (block) blockTimestamps[bn] = hexToNumber(block.timestamp);
      } catch {}
    })
  );

  const transactions = allLogs.slice(0, limit).map(log => {
    const isNFT = log.topics?.length === 4;
    const from = log.topics?.[1] ? "0x" + log.topics[1].slice(26) : null;
    const to = log.topics?.[2] ? "0x" + log.topics[2].slice(26) : null;
    const ts = blockTimestamps[log.blockNumber];

    const base = {
      txHash: log.transactionHash,
      block: hexToNumber(log.blockNumber),
      timestamp: ts ? new Date(ts * 1000).toISOString() : null,
      contract: log.address?.toLowerCase(),
      from,
      to,
      direction: from === address ? "OUT" : "IN",
    };

    if (isNFT) {
      return { ...base, type: "NFT", tokenId: hexToNumber(log.topics[3]) };
    } else {
      const value = log.data && log.data !== "0x" ? Number(BigInt(log.data)) / 1e18 : 0;
      return { ...base, type: "ERC-20", value: Math.round(value * 10000) / 10000 };
    }
  });

  console.log(formatOutput({
    address,
    chain: chain.name,
    count: transactions.length,
    transactions,
  }, outputFormat));
}

main().catch(err => {
  console.log(formatOutput({ error: err.message }, "json"));
  process.exit(1);
});
