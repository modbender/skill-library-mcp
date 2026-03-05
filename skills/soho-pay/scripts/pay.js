"use strict";

/**
 * CLI entry-point for the SOHO Pay skill.
 *
 * Usage:
 *   node scripts/pay.js <amount> <merchantAddress> [payerAddress]
 *
 * Environment variables must be set per src/config.js (see SKILL.md).
 *
 * IMPORTANT — Invocation safety:
 *   This skill is MANUAL-INVOCATION ONLY.
 *   Autonomous agent invocation is disabled.
 *   The user must explicitly confirm every payment.
 *
 * IMPORTANT — Architecture:
 *   SoHo is a credit layer only. It never signs.
 *   All EIP-712 signatures come from the user/operator's Wallet Signer.
 */

const { loadConfig } = require("../src/config");
const { createSigner } = require("../src/signer");
const { executePayment } = require("../src/pay");

async function main() {
  // ── Invocation guard ────────────────────────────────────────────────
  if (
    process.env.SOHO_AUTONOMOUS === "true" ||
    process.env.SOHO_AUTONOMOUS === "1"
  ) {
    console.error(
      "ABORT: This skill cannot run autonomously. " +
        "It must be invoked manually with explicit user confirmation.",
    );
    process.exit(1);
  }

  // ── Parse args ──────────────────────────────────────────────────────
  const [, , amountStr, merchantAddress, payerAddress] = process.argv;

  if (!amountStr || !merchantAddress) {
    console.error(
      "Usage: node scripts/pay.js <amount> <merchantAddress> [payerAddress]\n\n" +
        "  amount           Decimal USDC amount (e.g. 10, 0.5)\n" +
        "  merchantAddress  Explicit 0x checksummed EVM address\n" +
        "  payerAddress     Required for WALLET_SIGNER_REMOTE mode\n",
    );
    process.exit(1);
  }

  const config = loadConfig();
  const signer = createSigner(config);

  const result = await executePayment({
    config,
    signer,
    merchantAddress,
    amount: amountStr,
    payerAddress,
  });

  console.log("\nDone.", JSON.stringify(result, null, 2));
}

main().catch((err) => {
  console.error(`\nFATAL: ${err.message}`);
  process.exit(1);
});
