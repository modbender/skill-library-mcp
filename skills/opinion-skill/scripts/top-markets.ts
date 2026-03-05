// 热门市场 (通过 API)
// 用法: bun run scripts/top-markets.ts [--tag volume|txn] [--window 1h|4h|24h] [--json]

import { apiFetch } from "./config";

async function topMarkets(tag: string, timewindow: string, json: boolean): Promise<void> {
  const resp = await apiFetch<any>("/api/analyze/top20", { tag, timewindow });

  if (!resp.success) {
    console.error("API error:", resp.error?.message ?? "unknown");
    process.exit(1);
  }

  const { timeWindow, sortBy, startTime, endTime, top20 } = resp.data;

  if (json) {
    console.log(JSON.stringify(resp.data, null, 2));
    return;
  }

  console.log(`Top 20 Markets (by ${sortBy}, ${timeWindow})`);
  console.log(`Period: ${new Date(startTime * 1000).toLocaleString()} - ${new Date(endTime * 1000).toLocaleString()}\n`);

  for (let i = 0; i < top20.length; i++) {
    const m = top20[i];
    const title = m.parentEventTitle || m.marketTitle || "Unknown";
    console.log(`${i + 1}. ${title}`);
    console.log(`   Volume: $${Number(m.totalVolume || 0).toLocaleString()}`);
    console.log(`   Txns: ${m.txnCount}`);
    console.log(`   Fee: $${Number(m.totalFee || 0).toLocaleString()}`);
    if (m.yesTokenId) console.log(`   yesTokenId: ${m.yesTokenId}`);
    if (m.noTokenId) console.log(`   noTokenId: ${m.noTokenId}`);
    console.log("---");
  }
}

// CLI entry
const args = process.argv.slice(2);
let tag = "volume";
let timewindow = "24h";
let json = false;

for (let i = 0; i < args.length; i++) {
  switch (args[i]) {
    case "--tag": tag = args[++i]; break;
    case "--window": timewindow = args[++i]; break;
    case "--json": json = true; break;
  }
}

topMarkets(tag, timewindow, json).catch(console.error);
