/**
 * E2E Integration Test: CLI Dispute Flow
 *
 * Tests the x402r CLI commands end-to-end against real contracts.
 * Reuses the SDK's shared e2e infrastructure for account setup, operator
 * deployment, and HTTP 402 payment, then runs CLI commands via execSync.
 * Chain is determined by NETWORK_ID env var (default: shared infra default).
 *
 * Modes:
 *   - Default: deploys fresh operator, runs full 12-step lifecycle
 *   - OPERATOR_ADDRESS=0x...: uses existing operator, runs payment + dispute
 *     only (steps 1-7), skips SDK arbiter steps so the live arbiter server
 *     can evaluate the dispute and show it on the dashboard
 *
 * Flow (full):
 *   Setup → HTTP 402 Payment → CLI config → CLI dispute → CLI status →
 *   CLI show → Arbiter approve → CLI status → Execute refund → CLI show
 *
 * Flow (existing operator):
 *   Setup → HTTP 402 Payment → CLI config → CLI dispute → CLI status →
 *   CLI show → Done (arbiter server handles the rest)
 *
 * Prerequisites:
 *   - ETH on target chain (~0.01 for gas)
 *   - USDC on target chain (0.01 USDC = 10000 units)
 *   - SDK packages built (cd x402r-sdk && pnpm build)
 *
 * Usage:
 *   PRIVATE_KEY=0x... NETWORK_ID=eip155:11155111 pnpm cli:e2e
 *   PRIVATE_KEY=0x... NETWORK_ID=eip155:11155111 OPERATOR_ADDRESS=0x... pnpm cli:e2e
 */

import dotenv from "dotenv";
import { execSync } from "child_process";
import * as path from "path";
import { fileURLToPath } from "url";
import { toHex } from "viem";

dotenv.config();
import {
  StepRunner,
  PAYMENT_AMOUNT,
  USDC_ADDRESS,
  NETWORK_ID as SHARED_NETWORK_ID,
  RPC_URL as SHARED_RPC_URL,
  setupE2EAccounts,
  checkAndLogBalances,
  fundDerivedAccounts,
  deployTestOperator,
  setupHTTP402,
  performHTTP402Payment,
  createSDKInstances,
  shortAddr,
  waitForTx,
  erc20Abi,
  formatUnits,
  type Address,
} from "../../x402r-sdk/examples/e2e-test/shared.js";
import { savePaymentState } from "./src/state.js";

// ============ Config ============

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PROJECT_ROOT = path.resolve(__dirname, "..");
const CLI_BIN = path.join(__dirname, "bin", "x402r.ts");

// If OPERATOR_ADDRESS is set, use existing operator (skip deploy + arbiter steps)
const EXISTING_OPERATOR = process.env.OPERATOR_ADDRESS as Address | undefined;

// ============ CLI Helper ============

// Override env so CLI commands use the same network as the shared e2e infra
const cliEnv = {
  ...process.env,
  NETWORK_ID: SHARED_NETWORK_ID,
  RPC_URL: SHARED_RPC_URL,
};

function runCli(args: string): string {
  const cmd = `tsx "${CLI_BIN}" ${args}`;
  try {
    return execSync(cmd, {
      cwd: PROJECT_ROOT,
      env: cliEnv,
      encoding: "utf-8",
      timeout: 120000,
    });
  } catch (error: unknown) {
    const execError = error as {
      stdout?: string;
      stderr?: string;
    };
    if (execError.stdout) return execError.stdout;
    throw new Error(
      `CLI failed: ${cmd}\nstdout: ${execError.stdout ?? ""}\nstderr: ${execError.stderr ?? ""}`,
    );
  }
}

// ============ Main ============

async function main() {
  const mode = EXISTING_OPERATOR ? "live arbiter" : "full lifecycle";
  console.log(
    "╔══════════════════════════════════════════════════════════╗",
  );
  console.log(
    `║     x402r CLI E2E Test — ${SHARED_NETWORK_ID.padEnd(24)}║`,
  );
  console.log(
    `║     Mode: ${mode.padEnd(43)}║`,
  );
  console.log(
    "╚══════════════════════════════════════════════════════════╝",
  );

  const runner = new StepRunner();

  // ---- Step 1: Setup Accounts ----
  runner.step("1. Setup Accounts & Clients");

  const privateKey = process.env.PRIVATE_KEY as `0x${string}`;
  if (!privateKey) {
    console.error("Error: PRIVATE_KEY environment variable is required");
    console.error("Usage: PRIVATE_KEY=0x... npm run cli:e2e");
    process.exit(1);
  }

  const derivedCount = EXISTING_OPERATOR ? 1 : 2;
  const accounts = await setupE2EAccounts(privateKey, { derivedCount });

  runner.log(`Payer:    ${accounts.payerAccount.address}`);
  runner.log(`Merchant: ${accounts.merchantAccount.address}`);
  if (accounts.arbiterAccount) {
    runner.log(`Arbiter:  ${accounts.arbiterAccount.address}`);
  }

  await checkAndLogBalances(accounts, runner);
  await fundDerivedAccounts(accounts, runner);
  runner.pass("Setup accounts and fund derived wallets");

  // ---- Step 2: Deploy or use existing Operator ----
  let operatorAddress: Address;

  if (EXISTING_OPERATOR) {
    runner.step("2. Using Existing Operator");
    operatorAddress = EXISTING_OPERATOR;
    runner.log(`Operator: ${operatorAddress} (from OPERATOR_ADDRESS env)`);
    runner.pass("Using existing operator");
  } else {
    runner.step("2. Deploy Marketplace Operator");
    const deployResult = await deployTestOperator(accounts, runner);
    operatorAddress = deployResult.operatorAddress as Address;
    runner.log(`Operator: ${operatorAddress}`);
  }

  // ---- Step 3: HTTP 402 Payment ----
  runner.step("3. HTTP 402 Payment (402 → Pay → Verify → Settle)");

  const infra = await setupHTTP402(accounts, operatorAddress);
  runner.pass("Setup HTTP 402 infrastructure");

  const { paymentInfo } = await performHTTP402Payment(
    infra,
    accounts,
    runner,
  );
  runner.log(`PaymentInfo operator: ${shortAddr(paymentInfo.operator)}`);
  runner.log(`PaymentInfo payer: ${shortAddr(paymentInfo.payer)}`);
  runner.log(`PaymentInfo receiver: ${shortAddr(paymentInfo.receiver)}`);

  // Save payment state so CLI + merchant bot pick it up
  const merchantHdKey = accounts.merchantAccount.getHdKey();
  const merchantPrivateKey = merchantHdKey.privateKey
    ? toHex(merchantHdKey.privateKey)
    : undefined;

  savePaymentState({
    paymentInfo,
    operatorAddress,
    paymentHash: "e2e-test",
    timestamp: new Date().toISOString(),
    networkId: SHARED_NETWORK_ID,
    merchantPrivateKey,
  });
  runner.pass("Payment state saved to ~/.x402r/last-payment.json");

  // ---- Step 4: CLI config ----
  runner.step("4. CLI config command");

  try {
    const configOutput = runCli(
      `config --key ${privateKey} --operator ${operatorAddress} --network ${SHARED_NETWORK_ID} --rpc ${SHARED_RPC_URL}`,
    );
    runner.log(configOutput.trim());
    runner.assert(
      configOutput.includes("Config updated") &&
        configOutput.includes(operatorAddress),
      "CLI config sets key and operator",
    );
  } catch (error) {
    runner.fail(
      "CLI config",
      error instanceof Error ? error.message : String(error),
    );
  }

  // ---- Step 5: CLI dispute ----
  runner.step(
    "5. CLI dispute command (requestRefund + submitEvidence)",
  );

  let disputeOutput = "";
  try {
    disputeOutput = runCli(
      'dispute "E2E test: service returned wrong data" --evidence "Expected sunny, got rainy"',
    );
    runner.log(disputeOutput.trim());
    runner.assert(
      disputeOutput.includes("Dispute Created") ||
        disputeOutput.includes("Evidence submitted"),
      "CLI dispute creates refund request and submits evidence",
    );
  } catch (error) {
    runner.fail(
      "CLI dispute",
      error instanceof Error ? error.message : String(error),
    );
  }

  // ---- Step 5b: Verify compositeKey in dispute output ----
  const compositeKeyMatch = disputeOutput.match(/Composite Key:\s+(0x[a-fA-F0-9]+)/);
  if (compositeKeyMatch) {
    runner.log(`Composite Key: ${compositeKeyMatch[1]}`);
    runner.assert(true, "Dispute output includes composite key");
  } else {
    runner.fail("Dispute composite key", "No composite key found in dispute output");
  }

  // ---- Step 6: CLI status ----
  runner.step("6. CLI status command (Pending)");

  try {
    const statusOutput = runCli("status");
    runner.log(statusOutput.trim());
    runner.assert(
      statusOutput.includes("Pending") ||
        statusOutput.includes("Dispute Status"),
      "CLI status shows Pending dispute",
    );
  } catch (error) {
    runner.fail(
      "CLI status",
      error instanceof Error ? error.message : String(error),
    );
  }

  // ---- Step 7: CLI show ----
  runner.step("7. CLI show command (evidence)");

  // Brief delay for RPC state propagation after evidence confirmation
  await new Promise(resolve => setTimeout(resolve, 3000));

  try {
    const showOutput = runCli("show");
    runner.log(showOutput.trim());
    runner.assert(
      showOutput.includes("Evidence") && showOutput.includes("Payer"),
      "CLI show displays payer evidence",
    );
  } catch (error) {
    runner.fail(
      "CLI show",
      error instanceof Error ? error.message : String(error),
    );
  }

  // ---- Steps 8-12: Arbiter lifecycle (skip when using existing operator) ----
  if (EXISTING_OPERATOR) {
    runner.step("8-12. Skipped (live arbiter server handles approval)");
    runner.log("Dispute created on existing operator — check the dashboard!");
    runner.log(`  Dashboard: http://localhost:3001`);
    runner.log(`  Operator:  ${operatorAddress}`);
    runner.log(`  Payer:     ${accounts.payerAccount.address}`);
    runner.pass("Live arbiter mode — dispute submitted for server evaluation");
  } else {
    // ---- Step 8: Arbiter approves (SDK) ----
    runner.step(
      "8. Arbiter approves refund (SDK — no CLI approve command)",
    );

    const { arbiter } = createSDKInstances(accounts, operatorAddress);

    try {
      const { txHash: approveTx } = await arbiter!.approveRefundRequest(
        paymentInfo,
        0n,
      );
      await waitForTx(accounts.publicClient, approveTx);
      runner.pass("Arbiter approves refund", approveTx);
    } catch (error) {
      runner.fail(
        "Arbiter approve",
        error instanceof Error ? error.message : String(error),
      );
    }

    // ---- Step 9: CLI status after approval ----
    runner.step("9. CLI status command (Approved)");

    // Delay for RPC state propagation after arbiter approval
    await new Promise(resolve => setTimeout(resolve, 3000));

    try {
      const statusOutput = runCli("status");
      runner.log(statusOutput.trim());
      runner.assert(
        statusOutput.includes("Approved"),
        "CLI status shows Approved after arbiter ruling",
      );
    } catch (error) {
      runner.fail(
        "CLI status after approval",
        error instanceof Error ? error.message : String(error),
      );
    }

    // ---- Step 10: Arbiter executes refund ----
    runner.step("10. Arbiter executes refund (SDK)");

    const payerUsdcBefore = await accounts.publicClient.readContract({
      address: USDC_ADDRESS,
      abi: erc20Abi,
      functionName: "balanceOf",
      args: [accounts.payerAccount.address],
    });

    try {
      const { txHash: executeTx } = await arbiter!.executeRefundInEscrow(
        paymentInfo,
        PAYMENT_AMOUNT,
      );
      await waitForTx(accounts.publicClient, executeTx);
      runner.pass("Execute refund in escrow", executeTx);

      const payerUsdcAfter = await accounts.publicClient.readContract({
        address: USDC_ADDRESS,
        abi: erc20Abi,
        functionName: "balanceOf",
        args: [accounts.payerAccount.address],
      });

      const recovered = payerUsdcAfter - payerUsdcBefore;
      runner.log(`Payer recovered: ${formatUnits(recovered, 6)} USDC`);
      runner.assert(
        recovered > 0n,
        "USDC returned to payer",
        `recovered=${recovered}`,
      );
    } catch (error) {
      runner.fail(
        "Execute refund",
        error instanceof Error ? error.message : String(error),
      );
    }

    // ---- Step 11: CLI status final ----
    runner.step("11. CLI status command (final)");

    try {
      const statusOutput = runCli("status");
      runner.log(statusOutput.trim());
      runner.assert(
        statusOutput.includes("Approved"),
        "CLI status still shows Approved after execution",
      );
    } catch (error) {
      runner.fail(
        "CLI status final",
        error instanceof Error ? error.message : String(error),
      );
    }

    // ---- Step 12: CLI show final ----
    runner.step("12. CLI show command (evidence persists)");

    try {
      const showOutput = runCli("show");
      runner.log(showOutput.trim());
      runner.assert(
        showOutput.includes("Evidence") && showOutput.includes("Payer"),
        "CLI show displays evidence after full lifecycle",
      );
    } catch (error) {
      runner.fail(
        "CLI show final",
        error instanceof Error ? error.message : String(error),
      );
    }
  }

  // ---- Summary ----
  console.log(
    "\n╔══════════════════════════════════════════════════════════╗",
  );
  console.log(
    "║                    TEST SUMMARY                        ║",
  );
  console.log(
    "╚══════════════════════════════════════════════════════════╝",
  );

  runner.printSummary("CLI E2E TEST RESULTS");
  runner.exitWithResults(
    EXISTING_OPERATOR
      ? "CLI E2E TEST PASSED — Dispute submitted, check dashboard!"
      : "CLI E2E TEST PASSED — Full dispute lifecycle verified",
    "CLI E2E TEST FAILED",
  );
}

main().catch((error) => {
  console.error("\nCLI E2E test failed with error:", error);
  process.exit(1);
});
