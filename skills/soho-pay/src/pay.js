"use strict";

const { ethers } = require("ethers");
const crypto = require("crypto");

// ─── ABIs ─────────────────────────────────────────────────────────────
const CREDITOR_ABI = [
  "function spendWithAuthorization(address,address,address,uint256,uint256,bytes32,uint256,uint256,bytes)",
];
const BORROWER_MANAGER_ABI = [
  "function isBorrowerRegistered(address) view returns (bool)",
  "function isActiveBorrower(address) view returns (bool)",
  "function getAgentSpendLimit(address) view returns (uint256)",
];

// ─── Address Validation ───────────────────────────────────────────────
function validateMerchantAddress(raw) {
  if (!raw || typeof raw !== "string") {
    throw new Error("merchantAddress is required and must be a string.");
  }

  if (!ethers.isAddress(raw)) {
    throw new Error(
      `Invalid EVM address: "${raw}". ` +
        "A valid 0x-prefixed checksummed address is required. " +
        "Generating addresses from merchant names is not permitted.",
    );
  }

  return ethers.getAddress(raw);
}

/**
 * Execute a SOHO Pay spendWithAuthorization payment.
 *
 * Orchestration flow:
 *   1. Wallet Signer (user/operator) → produces EIP-712 signature
 *   2. SoHo (credit layer)           → pre-flight credit checks + JIT funding
 *   3. Blockchain                     → settlement via Creditor contract
 *
 * SoHo never signs. All signatures come from the Wallet Signer.
 *
 * @param {object} opts
 * @param {object} opts.config          - validated config from loadConfig()
 * @param {object} opts.signer          - from createSigner() (user-controlled)
 * @param {string} opts.merchantAddress - explicit checksummed EVM address
 * @param {string} opts.amount          - human-readable USDC amount (e.g. "10")
 * @param {string} [opts.payerAddress]  - required for WALLET_SIGNER_REMOTE
 * @param {number} [opts.paymentPlanId=0]
 */
async function executePayment({
  config,
  signer,
  merchantAddress: rawMerchant,
  amount: amountStr,
  payerAddress: explicitPayer,
  paymentPlanId = 0,
}) {
  const merchantAddress = validateMerchantAddress(rawMerchant);
  const amount = ethers.parseUnits(amountStr, config.usdcDecimals);

  // Determine payer address
  let payerAddress;
  if (signer.type === "local") {
    payerAddress = await signer.getAddress();
  } else if (explicitPayer) {
    payerAddress = ethers.getAddress(explicitPayer);
  } else {
    throw new Error(
      "payerAddress is required when using WALLET_SIGNER_REMOTE " +
        "(the wallet service does not expose addresses by default).",
    );
  }

  const provider =
    signer.provider || new ethers.JsonRpcProvider(config.rpcUrl);

  console.log("--- SOHO Pay Transaction ---");
  console.log(`  Network:        ${config.network.name} (${config.chainId})`);
  console.log(`  Wallet Signer:  ${signer.type.toUpperCase()}`);
  console.log(`  Payer:          ${payerAddress}`);
  console.log(`  Merchant:       ${merchantAddress}`);
  console.log(`  Amount:         ${amountStr} USDC`);
  console.log("----------------------------\n");

  // ── Pre-flight credit checks (SoHo credit layer) ───────────────────
  console.log("Pre-flight checks (SoHo credit layer)...");
  const bmContract = new ethers.Contract(
    config.addresses.borrowerManager,
    BORROWER_MANAGER_ABI,
    provider,
  );

  const [isRegistered, isActive, creditLimit] = await Promise.all([
    bmContract.isBorrowerRegistered(payerAddress),
    bmContract.isActiveBorrower(payerAddress),
    bmContract.getAgentSpendLimit(payerAddress),
  ]);

  console.log(`  Registered: ${isRegistered ? "yes" : "NO"}`);
  console.log(`  Active:     ${isActive ? "yes" : "NO"}`);
  console.log(
    `  Limit:      ${ethers.formatUnits(creditLimit, config.usdcDecimals)} USDC`,
  );

  const failures = [];
  if (!isRegistered) failures.push("Borrower is not registered");
  if (!isActive) failures.push("Borrower is not active");
  if (creditLimit < amount)
    failures.push(
      `Credit limit (${ethers.formatUnits(creditLimit, config.usdcDecimals)}) < amount (${amountStr})`,
    );

  if (failures.length) {
    throw new Error(
      `Pre-flight failed:\n${failures.map((f) => `  - ${f}`).join("\n")}`,
    );
  }
  console.log("  All checks passed.\n");

  // ── Build EIP-712 typed data ────────────────────────────────────────
  const domain = {
    name: "CreditContract",
    version: "1",
    chainId: config.chainId,
    verifyingContract: config.addresses.creditor,
  };
  const types = {
    SpendWithAuthorization: [
      { name: "payer", type: "address" },
      { name: "merchant", type: "address" },
      { name: "asset", type: "address" },
      { name: "amount", type: "uint256" },
      { name: "paymentPlanId", type: "uint256" },
      { name: "nonce", type: "bytes32" },
      { name: "validAfter", type: "uint256" },
      { name: "expiry", type: "uint256" },
    ],
  };
  const nonce = "0x" + crypto.randomBytes(32).toString("hex");
  const now = Math.floor(Date.now() / 1000);
  const message = {
    payer: payerAddress,
    merchant: merchantAddress,
    asset: config.addresses.usdc,
    amount,
    paymentPlanId,
    nonce,
    validAfter: now - 60,
    expiry: now + 600,
  };

  // ── Request signature from Wallet Signer (NOT SoHo) ────────────────
  console.log("Requesting EIP-712 signature from wallet signer...");
  const signature = await signer.signEip712({ domain, types, message });
  console.log("  Signature obtained.\n");

  // ── Submit transaction to blockchain ────────────────────────────────
  console.log("Submitting transaction to blockchain...");

  if (signer.type === "local") {
    const creditor = new ethers.Contract(
      config.addresses.creditor,
      CREDITOR_ABI,
      signer.wallet,
    );
    const tx = await creditor.spendWithAuthorization(
      message.payer,
      message.merchant,
      message.asset,
      message.amount,
      message.paymentPlanId,
      message.nonce,
      message.validAfter,
      message.expiry,
      signature,
    );
    console.log(`  Tx sent: ${tx.hash}`);
    const receipt = await tx.wait();
    console.log(`  Confirmed in block ${receipt.blockNumber}`);
    return { txHash: tx.hash, blockNumber: receipt.blockNumber };
  }

  // WALLET_SIGNER_REMOTE: try send-tx endpoint on the wallet service
  if (signer.sendTx) {
    try {
      const txHash = await signer.sendTx({
        to: config.addresses.creditor,
        data: new ethers.Interface(CREDITOR_ABI).encodeFunctionData(
          "spendWithAuthorization",
          [
            message.payer,
            message.merchant,
            message.asset,
            message.amount,
            message.paymentPlanId,
            message.nonce,
            message.validAfter,
            message.expiry,
            signature,
          ],
        ),
      });
      console.log(`  Tx sent via wallet signer: ${txHash}`);
      return { txHash };
    } catch (err) {
      console.warn(
        `  Wallet signer /send-tx unavailable (${err.message}).`,
      );
    }
  }

  throw new Error(
    "Cannot broadcast transaction: WALLET_SIGNER_REMOTE mode requires " +
      "the wallet signing service to expose /send-tx, or the caller must " +
      "handle broadcast externally.",
  );
}

module.exports = { executePayment, validateMerchantAddress };
