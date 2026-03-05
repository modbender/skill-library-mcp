// 查看余额 (通过 SDK)
// 用法: bun run scripts/balances.ts [--json]

import { getClient, MULTI_SIG_ADDRESS } from "./sdk-config";

async function checkBalances(json: boolean): Promise<void> {
  const client = getClient();

  console.log("Opinion Balances");
  console.log("=".repeat(50));
  console.log(`Multi-sig wallet: ${MULTI_SIG_ADDRESS}\n`);

  const resp = await client.getMyBalances();

  if (resp.errno !== 0) {
    console.error(`API error: [${resp.errno}] ${resp.errmsg}`);
    process.exit(1);
  }

  if (json) {
    console.log(JSON.stringify(resp.result, null, 2));
    return;
  }

  const balances = resp.result;
  console.log("Balances:");
  console.log(JSON.stringify(balances, null, 2));
}

// CLI entry
const json = process.argv.includes("--json");
checkBalances(json).catch(console.error);
