// 启用交易 (一次性操作, 需要 BNB gas)
// 用法: bun run scripts/enable-trading.ts

import { getClient } from "./sdk-config";

async function enableTrading(): Promise<void> {
  const client = getClient();

  console.log("Enabling trading (one-time approval)...");
  console.log("This requires BNB for gas on BSC.\n");

  const result = await client.enableTrading();

  console.log("Trading enabled successfully!");
  console.log(`  txHash: ${result.txHash}`);
  console.log(`  safeTxHash: ${result.safeTxHash}`);
}

enableTrading().catch(console.error);
