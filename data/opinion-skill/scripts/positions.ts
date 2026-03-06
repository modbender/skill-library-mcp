// 查看持仓
// 用法: bun run scripts/positions.ts <address> [--limit <n>] [--json]

import { apiFetch, OPINION_API_HOST } from "./config";

async function getPositions(address: string, limit: number, json: boolean): Promise<void> {
  const resp = await apiFetch<any>(`/api/user/positions/${address}`, { limit, includeConditionId: "true" });

  if (!resp.success) {
    console.error("API error:", resp.error?.message ?? "unknown");
    process.exit(1);
  }

  const { data: positions, nextCursor, hasMore } = resp.data;

  if (json) {
    console.log(JSON.stringify(resp.data, null, 2));
    return;
  }

  if (!positions || positions.length === 0) {
    console.log("No positions found.");
    return;
  }

  console.log(`Positions for ${address} (${positions.length} found)\n`);

  // Batch fetch market info
  const assetIds = positions.map((p: any) => p.assetId);
  let marketMap: Record<string, any> = {};
  try {
    const res = await fetch(`${OPINION_API_HOST}/api/markets/batch-by-assets`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ assetIds }),
      signal: AbortSignal.timeout(30000),
    });
    const batchResp = await res.json() as any;
    if (batchResp.success) marketMap = batchResp.data;
  } catch {}

  for (const pos of positions) {
    const market = marketMap[pos.assetId];
    const title = market?.marketTitle || market?.title || "Unknown";
    console.log(`${title}`);
    console.log(`  assetId: ${pos.assetId}`);
    console.log(`  shares: ${pos.shares}`);
    if (pos.conditionId) console.log(`  conditionId: ${pos.conditionId}`);
    if (market) {
      const isYes = market.yesTokenId === pos.assetId;
      console.log(`  side: ${isYes ? "YES" : "NO"}`);
    }
    console.log("---");
  }

  if (hasMore) {
    console.log(`\nMore positions available. Next cursor: ${nextCursor}`);
  }
}

// CLI entry
const args = process.argv.slice(2);
let address = "";
let limit = 100;
let json = false;

for (let i = 0; i < args.length; i++) {
  switch (args[i]) {
    case "--limit": limit = parseInt(args[++i]); break;
    case "--json": json = true; break;
    default:
      if (!args[i].startsWith("--") && !address) address = args[i];
  }
}

if (!address) {
  console.error("Usage: bun run scripts/positions.ts <address> [--limit <n>] [--json]");
  process.exit(1);
}

getPositions(address, limit, json).catch(console.error);
