/**
 * dispute command — All-in-one: requestRefund + pin evidence + submitEvidence
 */

import type { Command } from "commander";
import { keccak256, encodePacked } from "viem";
import { X402rClient } from "@x402r/client";
import { computePaymentInfoHash } from "@x402r/core";
import { initCli } from "../setup.js";
import { getPaymentInfo, saveDisputeState } from "../state.js";
import { pinToIpfs } from "../ipfs.js";

export function registerDisputeCommand(program: Command): void {
  program
    .command("dispute")
    .description("Create a dispute for the last payment (requestRefund + submit evidence)")
    .argument("<reason>", "Reason for the dispute")
    .option("-e, --evidence <text>", "Additional evidence text")
    .option("-f, --file <path>", "Path to evidence file (JSON)")
    .option("-p, --payment-json <json>", "Payment info JSON (uses saved state if omitted)")
    .option("-n, --nonce <nonce>", "Nonce (default: 0)", "0")
    .option("-a, --amount <amount>", "Refund amount (default: full payment amount)")
    .action(async (reason: string, options) => {
      const { publicClient, walletClient, addresses, operatorAddress } = await initCli();
      const paymentInfo = getPaymentInfo(options);
      const nonce = BigInt(options.nonce);
      const amount = options.amount ? BigInt(options.amount) : paymentInfo.maxAmount;

      console.log("\n=== Creating Dispute ===");
      console.log("  Reason:", reason);
      console.log("  Amount:", amount.toString());
      console.log("  Nonce:", nonce.toString());

      const client = new X402rClient({
        publicClient: publicClient as any,
        walletClient: walletClient as any,
        operatorAddress,
        refundRequestAddress: addresses.refundRequestAddress,
        refundRequestEvidenceAddress: addresses.evidenceAddress,
        chainId: addresses.chainId,
      });

      // Step 1: Request refund on-chain
      console.log("\n[1/3] Requesting refund on-chain...");
      let refundTxHash: string | undefined;
      try {
        const hasRequest = await client.hasRefundRequest(paymentInfo, nonce);
        if (hasRequest) {
          const status = await client.getRefundStatus(paymentInfo, nonce);
          const statusNames = ["Pending", "Approved", "Denied", "Cancelled"];
          console.log(`  Refund request already exists (status: ${statusNames[status] || status})`);
        } else {
          const { txHash } = await client.requestRefund(paymentInfo, amount, nonce);
          refundTxHash = txHash;
          console.log("  Refund requested:", txHash);
          console.log("  Waiting for confirmation...");
          await (publicClient as any).waitForTransactionReceipt({ hash: txHash });
          // Brief delay to ensure state propagation on testnet RPCs
          await new Promise(resolve => setTimeout(resolve, 3000));
          console.log("  Confirmed.");
        }
      } catch (error) {
        console.error("  Failed to request refund:", error instanceof Error ? error.message : error);
        process.exit(1);
      }

      // Step 2: Build and pin evidence
      console.log("\n[2/3] Building and pinning evidence...");
      let fileContent: unknown;
      if (options.file) {
        try {
          const { readFileSync } = await import("fs");
          fileContent = JSON.parse(readFileSync(options.file, "utf-8"));
        } catch (error) {
          console.error("  Failed to read evidence file:", error instanceof Error ? error.message : error);
          process.exit(1);
        }
      }

      const evidenceData: Record<string, unknown> = {
        reason,
        timestamp: new Date().toISOString(),
        payer: paymentInfo.payer,
        receiver: paymentInfo.receiver,
      };
      if (options.evidence) {
        evidenceData.evidence = options.evidence;
      }
      if (fileContent) {
        evidenceData.attachments = fileContent;
      }

      let cid: string;
      try {
        cid = await pinToIpfs(evidenceData);
      } catch (error) {
        console.error("  Failed to pin evidence:", error instanceof Error ? error.message : error);
        process.exit(1);
      }

      // Step 3: Submit evidence on-chain (skip if payer already submitted)
      console.log("\n[3/3] Submitting evidence on-chain...");
      let evidenceTxHash: string | undefined;
      try {
        const existing = await client.getAllEvidence(paymentInfo, nonce);
        const alreadySubmitted = existing.some(
          (e) => e.submitter.toLowerCase() === paymentInfo.payer.toLowerCase()
        );
        if (alreadySubmitted) {
          console.log("  Evidence already submitted for this dispute — skipping");
        } else {
          const { txHash } = await client.submitEvidence(paymentInfo, nonce, cid);
          evidenceTxHash = txHash;
          console.log("  Evidence submitted:", txHash);
          console.log("  Waiting for confirmation...");
          await (publicClient as any).waitForTransactionReceipt({ hash: txHash });
          console.log("  Confirmed.");
        }
      } catch (error) {
        console.error("  Failed to submit evidence:", error instanceof Error ? error.message : error);
        process.exit(1);
      }

      // Compute compositeKey for dashboard link
      const paymentHash = computePaymentInfoHash(
        addresses.chainId,
        addresses.escrowAddress,
        paymentInfo,
      );
      const compositeKey = keccak256(
        encodePacked(["bytes32", "uint256"], [paymentHash, nonce]),
      );

      // Save dispute state
      saveDisputeState({
        nonce: nonce.toString(),
        compositeKey,
        refundTxHash,
        evidenceTxHash,
        evidenceCid: cid,
        timestamp: new Date().toISOString(),
      });

      console.log("\n=== Dispute Created ===");
      if (refundTxHash) console.log("  Refund Tx:", refundTxHash);
      if (evidenceTxHash) console.log("  Evidence Tx:", evidenceTxHash);
      console.log("  Evidence CID:", cid);
      console.log("  Composite Key:", compositeKey);
      console.log("\n  State saved to ~/.x402r/last-dispute.json");
      console.log("  Run 'x402r status' to check dispute status");

      // Print dashboard link if arbiter URL is configured
      const { getConfig } = await import("../config.js");
      const config = getConfig();
      if (config.arbiterUrl) {
        const dashboardBase = config.arbiterUrl.replace(/\/arbiter\/?$/, "");
        console.log(`  Dashboard: ${dashboardBase}/dispute/${compositeKey}`);
      }
    });
}
