/**
 * pay command — Make an x402r escrow payment to a merchant
 *
 * 1. GET <url> → 402 with PAYMENT-REQUIRED header
 * 2. Sign escrow authorization locally using @x402r/evm scheme
 * 3. Retry with PAYMENT-SIGNATURE header → merchant's facilitator verifies + settles → 200
 * 4. Extract PaymentInfo from escrow payload via toPaymentInfo()
 * 5. Save to ~/.x402r/last-payment.json for later dispute
 * 6. Print response body
 */

import type { Command } from "commander";
import { x402Client, x402HTTPClient } from "@x402/core/client";
import { registerEscrowScheme } from "@x402r/evm/escrow/client";
import { toPaymentInfo, computePaymentInfoHash } from "@x402r/core";
import { initCli } from "../setup.js";
import { savePaymentState } from "../state.js";
import { getConfig } from "../config.js";
import * as fs from "fs";

export function registerPayCommand(program: Command): void {
  program
    .command("pay")
    .description("Pay a merchant via x402r escrow payment")
    .argument("<url>", "Merchant URL to pay")
    .option("-o, --output <path>", "Save response body to file")
    .action(async (url: string, options: { output?: string }) => {
      const { account, networkId, operatorAddress, addresses } = await initCli();

      console.log("\n=== x402r Pay ===");
      console.log("  URL:", url);
      console.log("  Payer:", account.address);
      console.log("  Network:", networkId);

      // 1. Create x402 payment client with escrow scheme
      const paymentClient = new x402Client();
      registerEscrowScheme(paymentClient, { signer: account as never, networks: networkId as `${string}:${string}` });
      const httpClient = new x402HTTPClient(paymentClient);

      // 2. Initial request
      console.log("\n[1/4] Fetching resource...");
      const res402 = await fetch(url);

      if (res402.status !== 402) {
        console.log(`  Server returned ${res402.status} (no payment required)`);
        const body = await res402.text();
        console.log("\n--- Response ---");
        console.log(body);
        if (options.output) {
          fs.writeFileSync(options.output, body);
          console.log(`\n  Response saved to ${options.output}`);
        }
        return;
      }

      // 3. Parse payment requirements from 402 response
      console.log("  Got 402 Payment Required");
      console.log("\n[2/4] Parsing payment requirements...");
      let body: unknown;
      try {
        body = await res402.json();
      } catch {
        body = undefined;
      }
      const paymentRequired = httpClient.getPaymentRequiredResponse(
        (name: string) => res402.headers.get(name),
        body,
      );
      console.log("  Requirements parsed");

      // 4. Create signed payment payload
      console.log("\n[3/4] Signing escrow payment...");
      const paymentPayload = await httpClient.createPaymentPayload(paymentRequired);
      const paymentHeaders = httpClient.encodePaymentSignatureHeader(paymentPayload);
      console.log("  Payment signed");

      // 5. Retry with payment header
      console.log("\n[4/4] Sending payment...");
      const res200 = await fetch(url, { headers: paymentHeaders });

      if (!res200.ok) {
        console.error(`  Payment failed: ${res200.status} ${res200.statusText}`);
        try {
          const errorBody = await res200.text();
          console.error("  ", errorBody);
        } catch { /* ignore */ }
        process.exit(1);
      }

      console.log(`  Payment accepted (${res200.status})`);

      // 6. Extract settlement info from response headers
      let settleTxHash: string | undefined;
      try {
        const settleResponse = httpClient.getPaymentSettleResponse(
          (name: string) => res200.headers.get(name),
        );
        settleTxHash = settleResponse?.transaction;
      } catch {
        // Settlement headers may not be present
      }

      // 7. Extract PaymentInfo from escrow payload
      const escrowPayload = paymentPayload.payload as {
        authorization: { from: `0x${string}` };
        paymentInfo: {
          operator: `0x${string}`;
          receiver: `0x${string}`;
          token: `0x${string}`;
          maxAmount: string | bigint;
          preApprovalExpiry: string | number | bigint;
          authorizationExpiry: string | number | bigint;
          refundExpiry: string | number | bigint;
          minFeeBps: number;
          maxFeeBps: number;
          feeReceiver: `0x${string}`;
          salt: string | bigint;
        };
      };
      const paymentInfo = toPaymentInfo(escrowPayload);
      const paymentHash = computePaymentInfoHash(
        addresses.chainId,
        addresses.escrowAddress,
        paymentInfo,
      );

      // 8. Save payment state for later dispute
      savePaymentState({
        paymentInfo,
        operatorAddress,
        paymentHash,
        timestamp: new Date().toISOString(),
        networkId,
      });

      // 9. Cache payment info on arbiter for dashboard lookups
      const config = getConfig();
      try {
        const piSerialized = {
          operator: paymentInfo.operator,
          payer: paymentInfo.payer,
          receiver: paymentInfo.receiver,
          token: paymentInfo.token,
          maxAmount: paymentInfo.maxAmount.toString(),
          preApprovalExpiry: paymentInfo.preApprovalExpiry.toString(),
          authorizationExpiry: paymentInfo.authorizationExpiry.toString(),
          refundExpiry: paymentInfo.refundExpiry.toString(),
          minFeeBps: paymentInfo.minFeeBps,
          maxFeeBps: paymentInfo.maxFeeBps,
          feeReceiver: paymentInfo.feeReceiver,
          salt: paymentInfo.salt.toString(),
        };
        await fetch(`${config.arbiterUrl}/api/payment-info`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(piSerialized),
        });
      } catch {
        // Non-critical — dashboard lookup may not work but payment is saved locally
      }

      // 10. Print response
      const responseBody = await res200.text();
      console.log("\n--- Response ---");
      console.log(responseBody);

      if (options.output) {
        fs.writeFileSync(options.output, responseBody);
        console.log(`\n  Response saved to ${options.output}`);
      }

      console.log("\n=== Payment Complete ===");
      if (settleTxHash) {
        console.log("  Settle Tx:", settleTxHash);
      }
      console.log("  Payment Hash:", paymentHash);
      console.log("  State saved to ~/.x402r/last-payment.json");
      console.log("  Run 'x402r dispute \"reason\"' to dispute this payment");
    });
}
