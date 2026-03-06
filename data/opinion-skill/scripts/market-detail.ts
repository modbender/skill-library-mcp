// 获取市场详情
// 用法: bun run scripts/market-detail.ts <marketId> [--json]

import { apiFetch } from "./config";

async function getMarketDetail(marketId: string, json: boolean): Promise<void> {
  const detailResp = await apiFetch<any>(`/api/markets/detail-params/${marketId}`);
  if (!detailResp.success) {
    console.error(`Market ${marketId} not found.`);
    process.exit(1);
  }

  const detail = detailResp.data;

  const assetResp = await apiFetch<any>(`/api/markets/asset-ids/${marketId}`);
  const assets = assetResp.success ? assetResp.data : null;

  const tokenId = assets?.yesTokenId || detail.yesTokenId;
  let market: any = null;
  if (tokenId) {
    try {
      const mResp = await apiFetch<any>(`/api/markets/by-asset/${tokenId}`);
      if (mResp.success) market = mResp.data;
    } catch {}
  }

  if (json) {
    console.log(JSON.stringify({ detail, assets, market }, null, 2));
    return;
  }

  console.log(`\nMarket: ${detail.title || market?.marketTitle || "Unknown"}`);
  console.log(`  marketId: ${marketId}`);
  if (market?.status) console.log(`  status: ${market.status} (${market.statusEnum})`);
  console.log(`  yesLabel: ${detail.yesLabel || "Yes"} / noLabel: ${detail.noLabel || "No"}`);
  console.log(`  yesTokenId: ${assets?.yesTokenId || detail.yesTokenId}`);
  console.log(`  noTokenId: ${assets?.noTokenId || detail.noTokenId}`);
  if (market?.conditionId) console.log(`  conditionId: ${market.conditionId}`);
  if (market?.volume) console.log(`  volume: $${Number(market.volume).toLocaleString()}`);
  if (market?.quoteToken) console.log(`  quoteToken: ${market.quoteToken}`);
  if (market?.chainId) console.log(`  chainId: ${market.chainId}`);
  if (market?.rules) console.log(`  rules: ${market.rules.slice(0, 200)}`);
  if (market?.createdAt) console.log(`  created: ${market.createdAt}`);
  if (market?.cutoffAt) console.log(`  cutoff: ${market.cutoffAt}`);
  if (market?.resolvedAt) console.log(`  resolved: ${market.resolvedAt}`);
  if (assets?.parentEvent || market?.parentEvent) {
    const pe = assets?.parentEvent || market?.parentEvent;
    console.log(`  event: ${pe.title} (eventMarketId: ${pe.eventMarketId})`);
  }
  if (market?.childMarkets?.length) {
    console.log(`  childMarkets (${market.childMarkets.length}):`);
    for (const child of market.childMarkets) {
      console.log(`    - ${child.title || child.marketTitle} (marketId: ${child.marketId}, yes: ${child.yesTokenId}, no: ${child.noTokenId})`);
    }
  }
}

// CLI entry
const args = process.argv.slice(2);
const marketId = args.find(a => !a.startsWith("--"));
const json = args.includes("--json");

if (!marketId) {
  console.error("Usage: bun run scripts/market-detail.ts <marketId> [--json]");
  process.exit(1);
}

getMarketDetail(marketId, json).catch(console.error);
