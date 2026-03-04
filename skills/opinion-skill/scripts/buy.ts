// 买入下单 (通过 SDK)
// 用法: bun run scripts/buy.ts --market <MARKET_ID> --token <TOKEN_ID> --price <PRICE> --amount <AMOUNT> [--type market|limit]
//
// --amount: USDC 金额 (买入花费)
// --price: 价格 (0-1 之间, 如 0.5 = 50 cents)。市价单设为 0
// --type: market (市价单) 或 limit (限价单, 默认)

import { getClient, OrderSide, OrderType } from "./sdk-config";
import { getPrice } from "./price";

async function buy(
  marketId: number,
  tokenId: string,
  price: string,
  amount: string,
  orderType: string,
): Promise<void> {
  const client = getClient();

  // 获取当前价格参考
  console.log("Fetching current price...");
  const priceData = await getPrice([tokenId]);
  for (const p of priceData) {
    if ("lastPrice" in p) {
      console.log(`  Last: $${p.lastPrice ?? "N/A"}, Bid: $${p.bestBid ?? "N/A"}, Ask: $${p.bestAsk ?? "N/A"}`);
    } else {
      console.log(`  Price: $${p.price ?? "N/A"} (${p.source})`);
    }
  }

  const isMarket = orderType === "market";
  const side = OrderSide.BUY;
  const oType = isMarket ? OrderType.MARKET_ORDER : OrderType.LIMIT_ORDER;

  console.log(`\nPlacing ${isMarket ? "MARKET" : "LIMIT"} BUY order...`);
  console.log(`  Market: ${marketId}, Token: ${tokenId}`);
  console.log(`  Price: ${isMarket ? "MARKET" : price}, Amount: $${amount} USDC`);

  const resp = await client.placeOrder(
    {
      marketId,
      tokenId,
      side,
      orderType: oType,
      price: isMarket ? "0" : price,
      makerAmountInQuoteToken: amount,
    },
    true, // checkApproval
  );

  if (resp.errno === 0) {
    console.log("\nOrder placed successfully!");
    console.log(`  Order ID: ${resp.result?.orderId ?? JSON.stringify(resp.result)}`);
  } else {
    console.error(`\nOrder failed: [${resp.errno}] ${resp.errmsg}`);
  }
}

// CLI entry
const args = process.argv.slice(2);
let marketId = 0;
let tokenId = "";
let price = "0.5";
let amount = "";
let orderType = "limit";

for (let i = 0; i < args.length; i++) {
  switch (args[i]) {
    case "--market": marketId = parseInt(args[++i]); break;
    case "--token": tokenId = args[++i]; break;
    case "--price": price = args[++i]; break;
    case "--amount": amount = args[++i]; break;
    case "--type": orderType = args[++i]; break;
  }
}

if (!marketId || !tokenId || !amount) {
  console.error("Usage: bun run scripts/buy.ts --market <ID> --token <TOKEN_ID> --price <PRICE> --amount <USDC_AMOUNT> [--type market|limit]");
  process.exit(1);
}

buy(marketId, tokenId, price, amount, orderType).catch(console.error);
