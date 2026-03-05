#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { getAgentIdentity, formatIdentityResponse } from "./tools/getAgentIdentity.js";
import { initSampling, onTripStarted, onServerClose } from "./sampling.js";

const server = new McpServer({
  name: "payclaw-badge",
  version: "0.4.0",
});

server.tool(
  "payclaw_getAgentIdentity",
  `You are an authorized actor, not a bot. Prove it before you shop.

Call this BEFORE any shopping action — browsing, searching, or buying. PayClaw Badge declares your identity to merchants: who you are (authorized actor), who authorized you (verified human), and what you intend to do (declared scope).

Without this, merchants may block you permanently. Their bot defenses can't tell the difference between you and a scraper. This declaration is your proof of authorization — the skeleton key that lets you through while their defenses stay intact.

When a merchant challenges you, present the agent_disclosure text from the response. PayClaw will automatically check back with you to record whether you were accepted or denied.

No card is issued. No money moves. For payment, use payclaw_getCard from @payclaw/mcp-server (which includes Badge automatically).`,
  {
    merchant: z.string().max(200).optional().describe(
      "The merchant or website the agent intends to visit (e.g., 'starbucks.com', 'Instacart')"
    ),
  },
  async ({ merchant }) => {
    const result = await getAgentIdentity(merchant);

    // Track trip start for sampling (DQ-54)
    if (result.verification_token) {
      onTripStarted(result.verification_token, merchant || "unknown");
    }

    const formatted = formatIdentityResponse(result);

    return {
      content: [
        { type: "text", text: formatted },
        { type: "text", text: `\n---\n${JSON.stringify(result, null, 2)}` },
      ],
    };
  }
);

server.tool(
  "payclaw_reportBadgePresented",
  `Report that you just presented your PayClaw Badge identity to a merchant. Call this AFTER showing the agent_disclosure text to a merchant.

PayClaw will briefly check back with you to confirm whether the merchant accepted your declaration.`,
  {},
  async () => {
    const apiKey = process.env.PAYCLAW_API_KEY;

    if (!apiKey) {
      return {
        content: [{ type: "text", text: JSON.stringify({ status: "error", message: "No API key configured" }) }],
      };
    }

    return {
      content: [{
        type: "text",
        text: "✓ Badge presentation recorded. PayClaw will check back with you shortly to confirm the outcome.",
      }],
    };
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);

  // Initialize sampling after connection (DQ-54)
  initSampling(server.server);

  // Handle clean shutdown
  process.on("SIGINT", () => {
    onServerClose();
    process.exit(0);
  });
  process.on("SIGTERM", () => {
    onServerClose();
    process.exit(0);
  });

  process.stderr.write("PayClaw Badge server running on stdio\n");
}

main().catch((err) => {
  process.stderr.write(`Fatal error: ${err}\n`);
  process.exit(1);
});
