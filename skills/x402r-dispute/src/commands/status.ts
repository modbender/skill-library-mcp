/**
 * status command — Check dispute status via arbiter server or SDK
 */

import type { Command } from "commander";
import { X402rClient } from "@x402r/client";
import { initReadOnly } from "../setup.js";
import { getPaymentInfo, getNonce, getCompositeKey } from "../state.js";
import { getConfig } from "../config.js";

export function registerStatusCommand(program: Command): void {
  program
    .command("status")
    .description("Check the status of a dispute")
    .option("--id <compositeKey>", "Composite key of the dispute")
    .option("-p, --payment-json <json>", "Payment info JSON (uses saved state if omitted)")
    .option("-n, --nonce <nonce>", "Nonce")
    .action(async (options) => {
      const config = getConfig();
      const compositeKey = getCompositeKey(options);

      // Try arbiter server first if composite key available
      if (compositeKey && config.arbiterUrl) {
        try {
          console.log(`\nQuerying arbiter at ${config.arbiterUrl}...`);
          const response = await fetch(`${config.arbiterUrl}/api/dispute/${compositeKey}`);
          if (response.ok) {
            const data = await response.json() as Record<string, unknown>;
            const statusNames: Record<number, string> = { 0: "Pending", 1: "Approved", 2: "Denied", 3: "Cancelled" };
            console.log("\n=== Dispute Status ===");
            console.log("  Composite Key:", compositeKey);
            console.log("  Status:", statusNames[data.status as number] || data.status);
            console.log("  Amount:", data.amount);
            console.log("  Nonce:", data.nonce);
            console.log("  Payment Info Hash:", data.paymentInfoHash);
            return;
          }
          console.log("  Arbiter returned", response.status, "— falling back to on-chain");
        } catch {
          console.log("  Arbiter unavailable — falling back to on-chain");
        }
      }

      // Fall back to on-chain query
      const { publicClient, addresses, operatorAddress } = await initReadOnly();
      const paymentInfo = getPaymentInfo(options);
      const nonce = getNonce(options);

      const client = new X402rClient({
        publicClient: publicClient as any,
        operatorAddress,
        refundRequestAddress: addresses.refundRequestAddress,
        chainId: addresses.chainId,
      });

      const hasRequest = await client.hasRefundRequest(paymentInfo, nonce);
      if (!hasRequest) {
        console.log("\nNo refund request found for this payment (nonce:", nonce.toString(), ")");
        return;
      }

      const status = await client.getRefundStatus(paymentInfo, nonce);
      const statusNames = ["Pending", "Approved", "Denied", "Cancelled"];
      console.log("\n=== Dispute Status (on-chain) ===");
      console.log("  Status:", statusNames[status] || status);
      console.log("  Nonce:", nonce.toString());
    });
}
