/**
 * verify command — Replay arbiter evaluation via court-ui's independent verifier
 */

import type { Command } from "commander";
import { initReadOnly } from "../setup.js";
import { getPaymentInfo, getNonce } from "../state.js";
import { getConfig } from "../config.js";

export function registerVerifyCommand(program: Command): void {
  program
    .command("verify")
    .description("Verify arbiter ruling by replaying AI evaluation (via court-ui)")
    .option("-p, --payment-json <json>", "Payment info JSON (uses saved state if omitted)")
    .option("-n, --nonce <nonce>", "Nonce")
    .option("-c, --court-url <url>", "Court UI URL (overrides config)")
    .action(async (options) => {
      const config = getConfig();
      await initReadOnly();
      const paymentInfo = getPaymentInfo(options);
      const nonce = getNonce(options);

      const courtUrl = options.courtUrl || config.courtUrl;
      if (!courtUrl) {
        console.error("\nError: Court UI URL not configured.");
        console.error("Set it with: x402r config --court-url https://your-court-ui.vercel.app");
        console.error("Or pass it directly: x402r verify --court-url https://...");
        process.exit(1);
      }

      console.log(`\nVerifying dispute via ${courtUrl}...`);

      try {
        const response = await fetch(`${courtUrl}/api/verify`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            paymentInfo: JSON.parse(
              JSON.stringify(paymentInfo, (_, v) => (typeof v === "bigint" ? v.toString() : v)),
            ),
            nonce: nonce.toString(),
          }),
        });

        if (!response.ok) {
          const error = await response.text();
          console.error(`\nCourt UI returned ${response.status}:`, error);
          process.exit(1);
        }

        const data = await response.json() as {
          replayCommitment: {
            commitmentHash: string;
            promptHash: string;
            responseHash: string;
            seed: number;
          };
          originalCommitment?: {
            commitmentHash: string;
          };
          displayContent: string;
          note: string;
        };

        console.log("\n=== Verification Result ===");
        console.log("\n  Replay Commitment:", data.replayCommitment.commitmentHash);
        console.log("  Prompt Hash:", data.replayCommitment.promptHash);
        console.log("  Response Hash:", data.replayCommitment.responseHash);
        console.log("  Seed:", data.replayCommitment.seed);

        if (data.originalCommitment) {
          const match = data.replayCommitment.commitmentHash === data.originalCommitment.commitmentHash;
          console.log("\n  Original Commitment:", data.originalCommitment.commitmentHash);
          console.log(`  Match: ${match ? "MATCH" : "MISMATCH"}`);
        }

        // Try to parse the AI response
        try {
          const decision = JSON.parse(data.displayContent);
          console.log("\n=== AI Decision (Replay) ===");
          console.log("  Decision:", decision.decision);
          console.log("  Confidence:", decision.confidence);
          console.log("  Reasoning:", decision.reasoning);
        } catch {
          console.log("\n  Raw Response:", data.displayContent);
        }

        console.log("\n  Note:", data.note);
      } catch (error) {
        console.error("\nFailed to verify:", error instanceof Error ? error.message : error);
        console.error("Is the court UI running at", courtUrl, "?");
        process.exit(1);
      }
    });
}
