// 查询价格
// 用法: bun run scripts/price.ts <assetId> [<assetId2> ...] [--json]

import { apiFetch, OPINION_API_HOST } from "./config";

export async function getPrice(assetIds: string[]): Promise<any[]> {
  if (assetIds.length === 1) {
    const resp = await apiFetch<any>(`/api/orderbook/${assetIds[0]}`, { chainId: "56" });
    if (resp.success) {
      const d = resp.data;
      const bids = d.bids || [];
      const asks = d.asks || [];
      const bestBid = bids.length > 0 ? Math.max(...bids.map((b: any) => parseFloat(b[0]))) : null;
      const bestAsk = asks.length > 0 ? Math.min(...asks.map((a: any) => parseFloat(a[0]))) : null;
      return [{
        assetId: assetIds[0],
        lastPrice: d.lastPrice,
        bestBid,
        bestAsk,
        mid: bestBid != null && bestAsk != null ? (bestBid + bestAsk) / 2 : d.lastPrice,
      }];
    }
  }

  // Batch price via POST
  const res = await fetch(`${OPINION_API_HOST}/api/orderbook/batchprice`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ assetIds }),
    signal: AbortSignal.timeout(30000),
  });
  const resp = await res.json() as any;
  if (!resp.success) {
    console.error("API error:", resp.error?.message ?? "unknown");
    process.exit(1);
  }
  return resp.data;
}

if (import.meta.main) {
  const args = process.argv.slice(2);
  const json = args.includes("--json");
  const assetIds = args.filter(a => !a.startsWith("--"));

  if (assetIds.length === 0) {
    console.error("Usage: bun run scripts/price.ts <assetId> [<assetId2> ...] [--json]");
    process.exit(1);
  }

  getPrice(assetIds).then(results => {
    if (json) {
      console.log(JSON.stringify(results, null, 2));
      return;
    }
    for (const r of results) {
      if ('lastPrice' in r) {
        console.log(`Asset: ${r.assetId}`);
        console.log(`  Last Price: ${r.lastPrice != null ? `$${r.lastPrice}` : "N/A"}`);
        console.log(`  Best Bid: ${r.bestBid != null ? `$${r.bestBid}` : "N/A"}`);
        console.log(`  Best Ask: ${r.bestAsk != null ? `$${r.bestAsk}` : "N/A"}`);
        console.log(`  Mid: ${r.mid != null ? `$${Number(r.mid).toFixed(4)}` : "N/A"}`);
      } else {
        console.log(`Asset: ${r.assetId}`);
        console.log(`  Price: ${r.price != null ? `$${r.price}` : "N/A"} (source: ${r.source})`);
      }
      console.log("---");
    }
  }).catch(console.error);
}
