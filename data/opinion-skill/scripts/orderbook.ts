// 查看订单簿
// 用法: bun run scripts/orderbook.ts <assetId> [--json]

import { apiFetch } from "./config";

async function getOrderbook(assetId: string, json: boolean): Promise<void> {
  const resp = await apiFetch<any>(`/api/orderbook/${assetId}`, { chainId: "56" });

  if (!resp.success) {
    console.error("API error:", resp.error?.message ?? "unknown");
    process.exit(1);
  }

  const { bids, asks, lastPrice, assetId: aid, timestamp } = resp.data;

  if (json) {
    console.log(JSON.stringify(resp.data, null, 2));
    return;
  }

  console.log(`Orderbook for ${aid}`);
  if (lastPrice != null) console.log(`Last Price: $${lastPrice}`);
  console.log(`Timestamp: ${new Date(timestamp).toLocaleString()}\n`);

  const sortedBids = [...(bids || [])].sort((a: any, b: any) => parseFloat(b[0]) - parseFloat(a[0]));
  console.log("--- Bids (high to low) ---");
  if (sortedBids.length > 0) {
    console.log("Price\t\tQty");
    sortedBids.slice(0, 10).forEach((b: any) => console.log(`$${b[0]}\t\t${b[1]}`));
    if (sortedBids.length > 10) console.log(`... ${sortedBids.length - 10} more`);
  } else {
    console.log("No bids");
  }

  const sortedAsks = [...(asks || [])].sort((a: any, b: any) => parseFloat(a[0]) - parseFloat(b[0]));
  console.log("\n--- Asks (low to high) ---");
  if (sortedAsks.length > 0) {
    console.log("Price\t\tQty");
    sortedAsks.slice(0, 10).forEach((a: any) => console.log(`$${a[0]}\t\t${a[1]}`));
    if (sortedAsks.length > 10) console.log(`... ${sortedAsks.length - 10} more`);
  } else {
    console.log("No asks");
  }

  if (sortedBids.length > 0 && sortedAsks.length > 0) {
    const bestBid = parseFloat(sortedBids[0][0]);
    const bestAsk = parseFloat(sortedAsks[0][0]);
    const spread = bestAsk - bestBid;
    const mid = (bestBid + bestAsk) / 2;
    console.log("\n--- Summary ---");
    console.log(`Best Bid: $${bestBid}`);
    console.log(`Best Ask: $${bestAsk}`);
    console.log(`Spread: $${spread.toFixed(4)}`);
    console.log(`Mid Price: $${mid.toFixed(4)}`);
  }
}

// CLI entry
const args = process.argv.slice(2);
const assetId = args.find(a => !a.startsWith("--"));
const json = args.includes("--json");

if (!assetId) {
  console.error("Usage: bun run scripts/orderbook.ts <assetId> [--json]");
  process.exit(1);
}

getOrderbook(assetId, json).catch(console.error);
