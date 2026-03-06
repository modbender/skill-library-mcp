/**
 * show command — Show evidence for a dispute
 */

import type { Command } from "commander";
import { X402rClient } from "@x402r/client";
import { type Evidence, SubmitterRole } from "@x402r/core";
import { initReadOnly } from "../setup.js";
import { getPaymentInfo, getNonce } from "../state.js";

function shortAddress(address: string): string {
  return `${address.slice(0, 10)}...${address.slice(-8)}`;
}

function roleName(role: SubmitterRole): string {
  switch (role) {
    case SubmitterRole.Payer:
      return "Payer";
    case SubmitterRole.Receiver:
      return "Receiver";
    case SubmitterRole.Arbiter:
      return "Arbiter";
    default:
      return `Unknown(${role})`;
  }
}

function formatEvidence(evidence: Evidence, index: number): string {
  const ts = new Date(Number(evidence.timestamp) * 1000).toISOString();
  return `  [${index}] ${roleName(evidence.role)} ${shortAddress(evidence.submitter)} | ${ts} | CID: ${evidence.cid}`;
}

export function registerShowCommand(program: Command): void {
  program
    .command("show")
    .description("Show all evidence for a dispute")
    .option("-p, --payment-json <json>", "Payment info JSON (uses saved state if omitted)")
    .option("-n, --nonce <nonce>", "Nonce")
    .action(async (options) => {
      const { publicClient, addresses, operatorAddress } = await initReadOnly();
      const paymentInfo = getPaymentInfo(options);
      const nonce = getNonce(options);

      const client = new X402rClient({
        publicClient: publicClient as any,
        operatorAddress,
        refundRequestEvidenceAddress: addresses.evidenceAddress,
        chainId: addresses.chainId,
      });

      console.log("\nFetching evidence...");

      const count = await client.getEvidenceCount(paymentInfo, nonce);
      console.log(`\n=== Evidence (${count} entries) ===`);

      if (count === 0n) {
        console.log("  No evidence submitted.");
        return;
      }

      const entries = await client.getAllEvidence(paymentInfo, nonce);
      for (let i = 0; i < entries.length; i++) {
        console.log(formatEvidence(entries[i], i));
      }
    });
}
