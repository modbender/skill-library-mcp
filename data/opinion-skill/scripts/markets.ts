// 浏览市场/事件列表
// 用法: bun run scripts/markets.ts [--limit <n>] [--offset <n>] [--json]

import { apiFetch } from "./config";

async function listMarkets(limit: number, offset: number, json: boolean): Promise<void> {
  const resp = await apiFetch<any>("/api/markets/wrap-events", { limit, offset });

  if (!resp.success) {
    console.error("API error:", resp.error?.message ?? "unknown");
    process.exit(1);
  }

  const { data, total } = resp;

  if (json) {
    console.log(JSON.stringify(resp, null, 2));
    return;
  }

  console.log(`Markets/Events: showing ${data.length} of ${total} (offset: ${offset})\n`);

  for (const item of data) {
    const title = item.title || item.marketTitle || "Untitled";
    console.log(`${title}`);
    if (item.marketId) console.log(`  marketId: ${item.marketId}`);
    if (item.status) console.log(`  status: ${item.status}`);
    if (item.volume) console.log(`  volume: $${Number(item.volume).toLocaleString()}`);
    if (item.yesTokenId) console.log(`  yesTokenId: ${item.yesTokenId}`);
    if (item.noTokenId) console.log(`  noTokenId: ${item.noTokenId}`);
    if (item.childMarkets?.length) {
      console.log(`  childMarkets: ${item.childMarkets.length}`);
      for (const child of item.childMarkets.slice(0, 5)) {
        console.log(`    - ${child.title || child.marketTitle} (marketId: ${child.marketId})`);
      }
      if (item.childMarkets.length > 5) {
        console.log(`    ... and ${item.childMarkets.length - 5} more`);
      }
    }
    console.log("---");
  }

  if (data.length < total) {
    console.log(`\nMore results available. Use --offset ${offset + limit} to see next page.`);
  }
}

// CLI entry
const args = process.argv.slice(2);
let limit = 20;
let offset = 0;
let json = false;

for (let i = 0; i < args.length; i++) {
  switch (args[i]) {
    case "--limit": limit = parseInt(args[++i]); break;
    case "--offset": offset = parseInt(args[++i]); break;
    case "--json": json = true; break;
  }
}

listMarkets(limit, offset, json).catch(console.error);
