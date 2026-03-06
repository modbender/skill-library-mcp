// 按 assetId 查询成交记录 (PredictscanAPI)
// 用法: bun run scripts/trades.ts <assetId> [--limit <n>] [--filter all|taker|maker] [--json]

import { apiFetch } from "./config";

async function getTrades(assetId: string, limit: number, filter: string, json: boolean): Promise<void> {
  const resp = await apiFetch<any>(`/api/orders/by-asset/${assetId}`, { limit, filter });

  if (!resp.success) {
    console.error("API error:", resp.error?.message ?? "unknown");
    process.exit(1);
  }

  const { data: trades, nextCursor, hasMore } = resp;

  if (json) {
    console.log(JSON.stringify(resp, null, 2));
    return;
  }

  if (!trades || trades.length === 0) {
    console.log("No trades found.");
    return;
  }

  console.log(`Trades for asset ${assetId} (${trades.length} found)\n`);

  for (const t of trades) {
    const side = t.side === 0 ? "BUY" : "SELL";
    console.log(`${t.timestamp ? new Date(t.timestamp).toLocaleString() : "—"}  ${side}  price: $${t.price}  size: ${t.size ?? t.amount ?? "—"}`);
    if (t.maker) console.log(`  maker: ${t.maker}`);
    if (t.taker) console.log(`  taker: ${t.taker}`);
    if (t.txHash) console.log(`  tx: ${t.txHash}`);
    console.log("---");
  }

  if (hasMore) {
    console.log(`\nMore trades available. Next cursor: ${nextCursor}`);
  }
}

// CLI entry
const args = process.argv.slice(2);
let assetId = "";
let limit = 100;
let filter = "taker";
let json = false;

for (let i = 0; i < args.length; i++) {
  switch (args[i]) {
    case "--limit": limit = parseInt(args[++i]); break;
    case "--filter": filter = args[++i]; break;
    case "--json": json = true; break;
    default:
      if (!args[i].startsWith("--") && !assetId) assetId = args[i];
  }
}

if (!assetId) {
  console.error("Usage: bun run scripts/trades.ts <assetId> [--limit <n>] [--filter all|taker|maker] [--json]");
  process.exit(1);
}

getTrades(assetId, limit, filter, json).catch(console.error);
