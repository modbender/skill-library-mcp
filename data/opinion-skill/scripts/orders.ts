// 查看订单 (通过 SDK)
// 用法: bun run scripts/orders.ts [--market <MARKET_ID>] [--status open] [--json]

import { getClient } from "./sdk-config";

async function listOrders(marketId?: number, status?: string, json?: boolean): Promise<void> {
  const client = getClient();

  const opts: any = { page: 1, limit: 50 };
  if (marketId) opts.marketId = marketId;
  if (status === "open") opts.status = "1";

  const resp = await client.getMyOrders(opts);

  if (resp.errno !== 0) {
    console.error(`API error: [${resp.errno}] ${resp.errmsg}`);
    process.exit(1);
  }

  const orders = resp.result?.list ?? resp.result;

  if (json) {
    console.log(JSON.stringify(resp.result, null, 2));
    return;
  }

  if (!orders || (Array.isArray(orders) && orders.length === 0)) {
    console.log("No orders found.");
    return;
  }

  const orderList = Array.isArray(orders) ? orders : [orders];
  console.log(`Found ${orderList.length} order(s)\n`);

  for (const o of orderList) {
    console.log(`Order: ${o.orderId || o.id}`);
    console.log(`  Side: ${o.side === 0 ? "BUY" : "SELL"}, Type: ${o.orderType === 1 ? "MARKET" : "LIMIT"}`);
    console.log(`  Price: $${o.price}, Status: ${o.status}`);
    console.log(`  Token: ${o.tokenId}`);
    if (o.marketId) console.log(`  Market: ${o.marketId}`);
    if (o.filledAmount) console.log(`  Filled: ${o.filledAmount}`);
    if (o.createdAt) console.log(`  Created: ${new Date(o.createdAt).toLocaleString()}`);
    console.log("---");
  }
}

// CLI entry
const args = process.argv.slice(2);
let marketId: number | undefined;
let status: string | undefined;
let json = false;

for (let i = 0; i < args.length; i++) {
  switch (args[i]) {
    case "--market": marketId = parseInt(args[++i]); break;
    case "--status": status = args[++i]; break;
    case "--json": json = true; break;
  }
}

listOrders(marketId, status, json).catch(console.error);
