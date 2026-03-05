#!/usr/bin/env npx tsx
/**
 * AgentXPay Skill — CLI Tool Runner
 *
 * Usage:
 *   npx tsx scripts/run-tool.ts <tool_name> [params_json]
 *
 * Examples:
 *   npx tsx scripts/run-tool.ts discover_services '{"category":"LLM"}'
 *   npx tsx scripts/run-tool.ts pay_and_call '{"url":"http://localhost:3001/api/chat","method":"POST","body":{"prompt":"hello"}}'
 *   npx tsx scripts/run-tool.ts smart_call '{"task":"Generate a cat image","category":"Image"}'
 *   npx tsx scripts/run-tool.ts manage_wallet '{"action":"create","dailyLimit":"0.5"}'
 *   npx tsx scripts/run-tool.ts manage_wallet '{"action":"authorize_agent","walletAddress":"0x...","agentAddress":"0x..."}'
 *   npx tsx scripts/run-tool.ts manage_wallet '{"action":"pay","walletAddress":"0x...","serviceId":1,"amount":"0.01"}'
 *   npx tsx scripts/run-tool.ts get_agent_info
 */

import { createAgentXPaySkill } from "../src/index";

const TOOL_NAME_MAP: Record<string, string> = {
  discover_services: "agentxpay_discover_services",
  pay_and_call: "agentxpay_pay_and_call",
  smart_call: "agentxpay_smart_call",
  manage_wallet: "agentxpay_manage_wallet",
  subscribe: "agentxpay_subscribe",
  create_escrow: "agentxpay_create_escrow",
  get_agent_info: "agentxpay_get_agent_info",
};

async function main() {
  const [, , toolNameArg, paramsJson] = process.argv;

  if (!toolNameArg || toolNameArg === "--help" || toolNameArg === "-h") {
    console.log(`
AgentXPay Skill — CLI Tool Runner

Usage:
  npx tsx scripts/run-tool.ts <tool_name> [params_json]

Available tools:
  discover_services   — Discover AI services on-chain
  pay_and_call        — x402 auto-payment call to AI service
  smart_call          — Discover + select + pay + call in one step
  manage_wallet       — Create/fund/query/limit/authorize/revoke/pay Agent wallet
  subscribe           — Subscribe to a service plan
  create_escrow       — Create escrow for custom job
  get_agent_info      — Get agent address/balance/network

Environment variables (required):
  RPC_URL                         — Monad RPC URL
  PRIVATE_KEY                     — Agent wallet private key
  SERVICE_REGISTRY_ADDRESS        — ServiceRegistry contract
  PAYMENT_MANAGER_ADDRESS         — PaymentManager contract
  SUBSCRIPTION_MANAGER_ADDRESS    — SubscriptionManager contract (optional)
  ESCROW_ADDRESS                  — Escrow contract (optional)
  AGENT_WALLET_FACTORY_ADDRESS    — AgentWalletFactory contract (optional)
`);
    process.exit(0);
  }

  // Resolve tool name
  const toolName =
    TOOL_NAME_MAP[toolNameArg] || toolNameArg;

  // Parse params — supports both JSON and raw string (OpenClaw command-dispatch)
  let params: Record<string, unknown> = {};
  if (paramsJson) {
    if (paramsJson.startsWith("{")) {
      try {
        params = JSON.parse(paramsJson);
      } catch {
        console.error(`ERROR: Invalid JSON params: ${paramsJson}`);
        process.exit(1);
      }
    } else {
      // OpenClaw raw mode: treat the entire string as a "task" parameter
      params = { task: paramsJson };
    }
  }

  // Validate env
  const rpcUrl = process.env.RPC_URL;
  const privateKey = process.env.PRIVATE_KEY;
  const serviceRegistry = process.env.SERVICE_REGISTRY_ADDRESS;

  if (!rpcUrl || !privateKey || !serviceRegistry) {
    console.error(
      "ERROR: RPC_URL, PRIVATE_KEY, and SERVICE_REGISTRY_ADDRESS are required."
    );
    console.error("Run with --help for details.");
    process.exit(1);
  }

  // Create skill
  const skill = createAgentXPaySkill({
    rpcUrl,
    privateKey,
    contracts: {
      serviceRegistry,
      paymentManager: process.env.PAYMENT_MANAGER_ADDRESS || "",
      subscriptionManager: process.env.SUBSCRIPTION_MANAGER_ADDRESS || "",
      escrow: process.env.ESCROW_ADDRESS || "",
      agentWalletFactory: process.env.AGENT_WALLET_FACTORY_ADDRESS || "",
    },
    network: (process.env.NETWORK as "local" | "testnet" | "mainnet") || "local",
  });

  console.log(`\n▶ Calling tool: ${toolName}`);
  console.log(`  Params: ${JSON.stringify(params)}\n`);

  try {
    const result = await skill.callTool(toolName, params);
    console.log("✓ Result:");
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`✗ Error: ${message}`);
    process.exit(1);
  }
}

main();
