// 取消订单 (通过 SDK)
// 用法:
//   bun run scripts/cancel.ts --order <ORDER_ID>                    # 取消单个
//   bun run scripts/cancel.ts --all [--market <MARKET_ID>]          # 取消全部

import { getClient } from "./sdk-config";

async function cancelOrder(orderId: string): Promise<void> {
  const client = getClient();
  console.log(`Cancelling order: ${orderId}`);

  const resp = await client.cancelOrder(orderId);
  if (resp.errno === 0) {
    console.log("Order cancelled successfully.");
  } else {
    console.error(`Cancel failed: [${resp.errno}] ${resp.errmsg}`);
  }
}

async function cancelAll(marketId?: number): Promise<void> {
  const client = getClient();
  const label = marketId ? `all orders for market ${marketId}` : "all orders";
  console.log(`Cancelling ${label}...`);

  const resp = await client.cancelAllOrders(marketId ? { marketId } : undefined);
  console.log(`Total: ${resp.totalOrders}, Cancelled: ${resp.cancelled}, Failed: ${resp.failed}`);
  if (resp.failed > 0 && resp.results) {
    for (const r of resp.results) {
      if (!r.success) console.log(`  Failed: ${r.error}`);
    }
  }
}

// CLI entry
const args = process.argv.slice(2);
let orderId: string | undefined;
let all = false;
let marketId: number | undefined;

for (let i = 0; i < args.length; i++) {
  switch (args[i]) {
    case "--order": orderId = args[++i]; break;
    case "--all": all = true; break;
    case "--market": marketId = parseInt(args[++i]); break;
  }
}

if (orderId) {
  cancelOrder(orderId).catch(console.error);
} else if (all) {
  cancelAll(marketId).catch(console.error);
} else {
  console.error("Usage:");
  console.error("  bun run scripts/cancel.ts --order <ORDER_ID>");
  console.error("  bun run scripts/cancel.ts --all [--market <MARKET_ID>]");
  process.exit(1);
}
