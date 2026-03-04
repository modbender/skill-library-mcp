#!/usr/bin/env node

/**
 * Arkade CLI - Command-line interface for Arkade wallet operations.
 *
 * This CLI is designed for agent integration (CLI-friendly for agents like MoltBot).
 * Data is stored in ~/.arkade-wallet/config.json
 * Private keys are auto-generated and stored locally — never exposed via CLI args.
 *
 * Default server: https://arkade.computer
 *
 * Usage:
 *   arkade init [url]                 # Initialize wallet (auto-generates key)
 *   arkade address                    # Show Ark address
 *   arkade boarding-address           # Show boarding address
 *   arkade balance                    # Show balance breakdown
 *   arkade send <address> <amount>    # Send sats
 *   arkade history                    # Transaction history
 *   arkade onboard                    # Onchain → Arkade
 *   arkade offboard <btc-address>     # Arkade → Onchain
 *   arkade ln-invoice <amount> [desc] # Create Lightning invoice
 *   arkade ln-pay <bolt11>            # Pay Lightning invoice
 *   arkade ln-fees                    # Show swap fees
 *   arkade ln-limits                  # Show swap limits
 *   arkade ln-pending                 # Show pending swaps
 *   arkade swap-quote <amt> <from> <to> # Get stablecoin quote
 *   arkade swap-pairs                 # Show available pairs
 *   arkade help                       # Show help
 */

import { chmodSync, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const CONFIG_DIR = join(homedir(), ".arkade-wallet");
const CONFIG_FILE = join(CONFIG_DIR, "config.json");
const DEFAULT_SERVER = "https://arkade.computer";

/**
 * Load configuration from disk.
 */
function loadConfig() {
  if (!existsSync(CONFIG_FILE)) {
    return null;
  }
  try {
    return JSON.parse(readFileSync(CONFIG_FILE, "utf-8"));
  } catch {
    return null;
  }
}

/**
 * Save configuration to disk.
 */
function saveConfig(config) {
  if (!existsSync(CONFIG_DIR)) {
    mkdirSync(CONFIG_DIR, { recursive: true, mode: 0o700 });
  }
  writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
  chmodSync(CONFIG_FILE, 0o600);
}

/**
 * Get the SDK dynamically.
 */
async function getSDK() {
  try {
    const sdk = await import("@arkade-os/sdk");
    // Import skills directly (ESM requires explicit .js extensions)
    const { ArkadeBitcoinSkill } = await import(
      "../dist/esm/skills/arkadeBitcoin.js"
    );
    const { ArkaLightningSkill } = await import(
      "../dist/esm/skills/lightning.js"
    );
    const { LendaSwapSkill } = await import("../dist/esm/skills/lendaswap.js");
    return {
      sdk,
      skill: { ArkadeBitcoinSkill, ArkaLightningSkill, LendaSwapSkill },
    };
  } catch (e) {
    console.error("Error: SDK not found. Run 'pnpm build' first.");
    console.error(e.message);
    process.exit(1);
  }
}

/**
 * Auto-initialize wallet config by generating a new private key.
 */
async function autoInit(serverUrl) {
  const { sdk } = await getSDK();
  const { SingleKey } = sdk;

  const identity = SingleKey.fromRandomBytes();
  const privateKey = Buffer.from(identity.key).toString("hex");
  const url = serverUrl || DEFAULT_SERVER;

  const config = {
    privateKey,
    serverUrl: url,
    createdAt: new Date().toISOString(),
  };

  saveConfig(config);
  return config;
}

/**
 * Create wallet from existing config.
 * Exits with an error if no wallet has been initialized.
 */
async function createWallet() {
  const config = loadConfig();
  if (!config) {
    console.error("Error: No wallet found. Run 'arkade init' first.");
    process.exit(1);
  }

  const { sdk } = await getSDK();
  const { Wallet, SingleKey } = sdk;

  const wallet = await Wallet.create({
    identity: SingleKey.fromHex(config.privateKey),
    arkServerUrl: config.serverUrl || DEFAULT_SERVER,
  });

  return wallet;
}

/**
 * Format satoshis for display.
 */
function formatSats(sats) {
  return sats.toLocaleString();
}

/**
 * Print help message.
 */
function printHelp() {
  console.log(`
Arkade CLI - Bitcoin wallet for Arkade and Lightning

USAGE:
  arkade <command> [options]

COMMANDS:
  init [url]                   Initialize wallet (auto-generates key)
                               Default server: arkade.computer

  address                      Show Ark address (for receiving offchain)
  boarding-address             Show boarding address (for onchain deposits)
  balance                      Show balance breakdown

  send <address> <amount>      Send satoshis to an Ark address
  history                      Show transaction history

  onboard                      Move funds from onchain to offchain (Arkade)
  offboard <btc-address>       Move funds from offchain to onchain

  ln-invoice <amount> [desc]   Create a Lightning invoice
  ln-pay <bolt11>              Pay a Lightning invoice
  ln-fees                      Show Lightning swap fees
  ln-limits                    Show Lightning swap limits
  ln-pending                   Show pending Lightning swaps

  swap-quote <amt> <from> <to>  Get stablecoin swap quote
  swap-to-stable <amt> <token> <chain> <evm-addr>
                                Swap BTC to stablecoin
  swap-to-btc <amt> <token> <chain> <evm-addr>
                                Swap stablecoin to BTC
  swap-claim <swap-id>          Claim a completed swap
  swap-refund <swap-id> [addr]  Refund an expired/failed swap
  swap-status <swap-id>         Check swap status
  swap-pending                  Show pending stablecoin swaps
  swap-pairs                    Show available stablecoin pairs

  help                          Show this help message

EXAMPLES:
  arkade init
  arkade init https://custom-server.com
  arkade balance
  arkade send ark1... 50000
  arkade ln-invoice 25000 "Coffee payment"
  arkade ln-pay lnbc...
  arkade swap-to-stable 100000 usdc_pol polygon 0x...
  arkade swap-to-btc 100 usdc_pol polygon 0x...

NOTE:
  Private keys are auto-generated and stored securely in ~/.arkade-wallet/config.json.
  They are never exposed via CLI arguments or stdout.
`);
}

/**
 * Initialize wallet command. Auto-generates a new private key.
 * If a wallet already exists, shows its address without overwriting.
 */
async function cmdInit(serverUrl) {
  const existing = loadConfig();
  if (existing) {
    const { sdk } = await getSDK();
    const { Wallet, SingleKey } = sdk;

    const wallet = await Wallet.create({
      identity: SingleKey.fromHex(existing.privateKey),
      arkServerUrl: existing.serverUrl || DEFAULT_SERVER,
    });

    const address = await wallet.getAddress();
    console.log("Wallet already initialized.");
    console.log(`Server: ${existing.serverUrl || DEFAULT_SERVER}`);
    console.log(`Address: ${address}`);
    return;
  }

  try {
    const config = await autoInit(serverUrl);

    const { sdk } = await getSDK();
    const { Wallet, SingleKey } = sdk;

    const wallet = await Wallet.create({
      identity: SingleKey.fromHex(config.privateKey),
      arkServerUrl: config.serverUrl,
    });

    const address = await wallet.getAddress();

    console.log("Wallet initialized successfully!");
    console.log(`Server: ${config.serverUrl}`);
    console.log(`Address: ${address}`);
  } catch (e) {
    console.error(`Error: Failed to initialize wallet: ${e.message}`);
    process.exit(1);
  }
}

/**
 * Show Ark address command.
 */
async function cmdAddress() {
  const wallet = await createWallet();
  const address = await wallet.getAddress();
  console.log(address);
}

/**
 * Show boarding address command.
 */
async function cmdBoardingAddress() {
  const wallet = await createWallet();
  const address = await wallet.getBoardingAddress();
  console.log(address);
}

/**
 * Show balance command.
 */
async function cmdBalance() {
  const wallet = await createWallet();
  const { skill } = await getSDK();
  const { ArkadeBitcoinSkill } = skill;

  const bitcoin = new ArkadeBitcoinSkill(wallet);
  const balance = await bitcoin.getBalance();

  console.log("Balance Breakdown:");
  console.log("------------------");
  console.log(`Total:          ${formatSats(balance.total)} sats`);
  console.log("");
  console.log("Offchain (Ark):");
  console.log(`  Available:    ${formatSats(balance.offchain.available)} sats`);
  console.log(`  Settled:      ${formatSats(balance.offchain.settled)} sats`);
  console.log(
    `  Preconfirmed: ${formatSats(balance.offchain.preconfirmed)} sats`,
  );
  console.log(
    `  Recoverable:  ${formatSats(balance.offchain.recoverable)} sats`,
  );
  console.log("");
  console.log("Onchain (Boarding):");
  console.log(`  Total:        ${formatSats(balance.onchain.total)} sats`);
  console.log(`  Confirmed:    ${formatSats(balance.onchain.confirmed)} sats`);
  console.log(
    `  Unconfirmed:  ${formatSats(balance.onchain.unconfirmed)} sats`,
  );
}

/**
 * Send command.
 */
async function cmdSend(address, amount) {
  if (!address || !amount) {
    console.error("Error: Address and amount required.");
    console.error("Usage: arkade send <address> <amount-sats>");
    process.exit(1);
  }

  const sats = parseInt(amount, 10);
  if (isNaN(sats) || sats <= 0) {
    console.error("Error: Invalid amount.");
    process.exit(1);
  }

  const wallet = await createWallet();
  const { skill } = await getSDK();
  const { ArkadeBitcoinSkill } = skill;

  const bitcoin = new ArkadeBitcoinSkill(wallet);

  try {
    const result = await bitcoin.send({ address, amount: sats });
    console.log(`Sent ${formatSats(sats)} sats`);
    console.log(`Transaction ID: ${result.txid}`);
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

/**
 * Transaction history command.
 */
async function cmdHistory() {
  const wallet = await createWallet();
  const { skill } = await getSDK();
  const { ArkadeBitcoinSkill } = skill;

  const bitcoin = new ArkadeBitcoinSkill(wallet);
  const history = await bitcoin.getTransactionHistory();

  if (history.length === 0) {
    console.log("No transactions found.");
    return;
  }

  console.log("Transaction History:");
  console.log("--------------------");

  for (const tx of history) {
    const type = tx.type === "SENT" ? "SENT" : "RECEIVED";
    const date = new Date(tx.createdAt).toLocaleString();
    const status = tx.settled ? "settled" : "pending";
    console.log(
      `${date} | ${type} | ${formatSats(tx.amount)} sats | ${status}`,
    );
  }
}

/**
 * Onboard command.
 */
async function cmdOnboard() {
  const wallet = await createWallet();
  const { sdk, skill } = await getSDK();
  const { RestArkProvider } = sdk;
  const { ArkadeBitcoinSkill } = skill;

  const config = loadConfig();
  const arkProvider = new RestArkProvider(config.serverUrl || DEFAULT_SERVER);
  const arkInfo = await arkProvider.getInfo();

  const bitcoin = new ArkadeBitcoinSkill(wallet);
  const balance = await bitcoin.getBalance();

  if (balance.onchain.total === 0) {
    console.log("No boarding UTXOs to onboard.");
    console.log(
      `Send BTC to your boarding address: ${await wallet.getBoardingAddress()}`,
    );
    return;
  }

  console.log(`Onboarding ${formatSats(balance.onchain.total)} sats...`);

  try {
    const result = await bitcoin.onboard({
      feeInfo: arkInfo.feeInfo,
      eventCallback: (event) => {
        console.log(`  Event: ${event.type}`);
      },
    });

    console.log(`Onboarded successfully!`);
    console.log(`Commitment TX: ${result.commitmentTxid}`);
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

/**
 * Offboard command.
 */
async function cmdOffboard(destinationAddress) {
  if (!destinationAddress) {
    console.error("Error: Destination address required.");
    console.error("Usage: arkade offboard <btc-address>");
    process.exit(1);
  }

  const wallet = await createWallet();
  const { sdk, skill } = await getSDK();
  const { RestArkProvider } = sdk;
  const { ArkadeBitcoinSkill } = skill;

  const config = loadConfig();
  const arkProvider = new RestArkProvider(config.serverUrl || DEFAULT_SERVER);
  const arkInfo = await arkProvider.getInfo();

  const bitcoin = new ArkadeBitcoinSkill(wallet);
  const balance = await bitcoin.getBalance();

  if (balance.offchain.available === 0) {
    console.log("No offchain funds to offboard.");
    return;
  }

  console.log(
    `Offboarding ${formatSats(balance.offchain.available)} sats to ${destinationAddress}...`,
  );

  try {
    const result = await bitcoin.offboard({
      destinationAddress,
      feeInfo: arkInfo.feeInfo,
      eventCallback: (event) => {
        console.log(`  Event: ${event.type}`);
      },
    });

    console.log(`Offboarded successfully!`);
    console.log(`Commitment TX: ${result.commitmentTxid}`);
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

/**
 * Create Lightning invoice command.
 */
async function cmdLnInvoice(amount, description) {
  if (!amount) {
    console.error("Error: Amount required.");
    console.error("Usage: arkade ln-invoice <amount-sats> [description]");
    process.exit(1);
  }

  const sats = parseInt(amount, 10);
  if (isNaN(sats) || sats <= 0) {
    console.error("Error: Invalid amount.");
    process.exit(1);
  }

  const wallet = await createWallet();
  const { skill } = await getSDK();
  const { ArkaLightningSkill } = skill;

  const lightning = new ArkaLightningSkill({
    wallet,
    network: "bitcoin",
  });

  try {
    const invoice = await lightning.createInvoice({
      amount: sats,
      description: description || "Arkade Lightning payment",
    });

    console.log("Lightning Invoice Created:");
    console.log(`Amount: ${formatSats(invoice.amount)} sats`);
    console.log(`Invoice: ${invoice.bolt11}`);
    console.log(`Payment Hash: ${invoice.paymentHash}`);
    console.log(`Expires in: ${invoice.expirySeconds} seconds`);
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

/**
 * Pay Lightning invoice command.
 */
async function cmdLnPay(bolt11) {
  if (!bolt11) {
    console.error("Error: Invoice required.");
    console.error("Usage: arkade ln-pay <bolt11-invoice>");
    process.exit(1);
  }

  const wallet = await createWallet();
  const { skill } = await getSDK();
  const { ArkaLightningSkill } = skill;

  const lightning = new ArkaLightningSkill({
    wallet,
    network: "bitcoin",
  });

  console.log("Paying Lightning invoice...");

  try {
    const result = await lightning.payInvoice({ bolt11 });

    console.log("Payment successful!");
    console.log(`Amount: ${formatSats(result.amount)} sats`);
    console.log(`Preimage: ${result.preimage}`);
    console.log(`TX ID: ${result.txid}`);
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

/**
 * Show Lightning fees command.
 */
async function cmdLnFees() {
  const wallet = await createWallet();
  const { skill } = await getSDK();
  const { ArkaLightningSkill } = skill;

  const lightning = new ArkaLightningSkill({
    wallet,
    network: "bitcoin",
  });

  try {
    const fees = await lightning.getFees();

    console.log("Lightning Swap Fees:");
    console.log("--------------------");
    console.log("Submarine Swaps (Pay Invoice):");
    console.log(`  Percentage: ${fees.submarine.percentage}%`);
    console.log(`  Miner Fee:  ${formatSats(fees.submarine.minerFees)} sats`);
    console.log("");
    console.log("Reverse Swaps (Receive Invoice):");
    console.log(`  Percentage: ${fees.reverse.percentage}%`);
    console.log(
      `  Lockup Fee: ${formatSats(fees.reverse.minerFees.lockup)} sats`,
    );
    console.log(
      `  Claim Fee:  ${formatSats(fees.reverse.minerFees.claim)} sats`,
    );
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

/**
 * Show Lightning limits command.
 */
async function cmdLnLimits() {
  const wallet = await createWallet();
  const { skill } = await getSDK();
  const { ArkaLightningSkill } = skill;

  const lightning = new ArkaLightningSkill({
    wallet,
    network: "bitcoin",
  });

  try {
    const limits = await lightning.getLimits();

    console.log("Lightning Swap Limits:");
    console.log("----------------------");
    console.log(`Minimum: ${formatSats(limits.min)} sats`);
    console.log(`Maximum: ${formatSats(limits.max)} sats`);
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

/**
 * Show pending Lightning swaps command.
 */
async function cmdLnPending() {
  const wallet = await createWallet();
  const { skill } = await getSDK();
  const { ArkaLightningSkill } = skill;

  const lightning = new ArkaLightningSkill({
    wallet,
    network: "bitcoin",
  });

  try {
    const pending = await lightning.getPendingSwaps();

    if (pending.length === 0) {
      console.log("No pending swaps.");
      return;
    }

    console.log("Pending Lightning Swaps:");
    console.log("------------------------");

    for (const swap of pending) {
      const date = swap.createdAt.toLocaleString();
      console.log(
        `${swap.id} | ${swap.type} | ${formatSats(swap.amount)} sats | ${swap.status} | ${date}`,
      );
    }
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

/**
 * Create a LendaSwapSkill with SQLite persistence for swaps and wallet data.
 * Stores data in ~/.arkade-wallet/lendaswap.db
 */
async function createLendaSwap() {
  const wallet = await createWallet();
  const { skill } = await getSDK();
  const { LendaSwapSkill } = skill;

  const config = loadConfig();
  const options = {};

  if (config.lendaswapMnemonic) {
    options.mnemonic = config.lendaswapMnemonic;
  }
  if (process.env.LENDASWAP_API_KEY) {
    options.apiKey = process.env.LENDASWAP_API_KEY;
  }
  if (process.env.LENDASWAP_API_URL) {
    options.apiUrl = process.env.LENDASWAP_API_URL;
  }

  // Use SQLite storage for swap and wallet persistence across sessions
  try {
    const { SqliteWalletStorage, SqliteSwapStorage } = await import(
      "@lendasat/lendaswap-sdk-pure/node"
    );
    const dbPath = join(CONFIG_DIR, "lendaswap.db");
    options.walletStorage = new SqliteWalletStorage(dbPath);
    options.swapStorage = new SqliteSwapStorage(dbPath);
  } catch {
    // Fallback to in-memory if SQLite is not available
    console.error("Warning: SQLite not available, swaps will not be persisted.");
  }

  const lendaswap = new LendaSwapSkill({ wallet, ...options });

  // Persist mnemonic after first SDK client initialization
  if (!config.lendaswapMnemonic) {
    try {
      const mnemonic = await lendaswap.getMnemonic();
      config.lendaswapMnemonic = mnemonic;
      saveConfig(config);
    } catch {
      // Non-fatal: mnemonic save failed, will generate a new one next time
    }
  }

  return lendaswap;
}

/**
 * Get stablecoin quote command.
 */
async function cmdSwapQuote(amount, from, to) {
  if (!amount || !from || !to) {
    console.error("Error: Amount, from, and to required.");
    console.error("Usage: arkade swap-quote <amount> <from> <to>");
    console.error("Example: arkade swap-quote 100000 btc_arkade usdc_pol");
    process.exit(1);
  }

  const lendaswap = await createLendaSwap();

  try {
    let quote;
    if (from === "btc_arkade" || from === "btc") {
      const sats = parseInt(amount, 10);
      if (isNaN(sats) || sats <= 0) {
        console.error("Error: Invalid amount.");
        process.exit(1);
      }
      quote = await lendaswap.getQuoteBtcToStablecoin(sats, to);
    } else {
      const tokenAmount = parseFloat(amount);
      if (isNaN(tokenAmount) || tokenAmount <= 0) {
        console.error("Error: Invalid amount.");
        process.exit(1);
      }
      quote = await lendaswap.getQuoteStablecoinToBtc(tokenAmount, from);
    }

    console.log("Swap Quote:");
    console.log("-----------");
    console.log(`From: ${quote.sourceAmount} ${quote.sourceToken}`);
    console.log(`To:   ${quote.targetAmount} ${quote.targetToken}`);
    console.log(`Rate: ${quote.exchangeRate}`);
    console.log(`Fee:  ${quote.fee.amount} (${quote.fee.percentage}%)`);
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

/**
 * Swap BTC to stablecoin command.
 */
async function cmdSwapToStable(
  amount,
  targetToken,
  targetChain,
  targetAddress,
) {
  if (!amount || !targetToken || !targetChain || !targetAddress) {
    console.error("Error: All parameters required.");
    console.error(
      "Usage: arkade swap-to-stable <amount-sats> <token> <chain> <evm-address>",
    );
    console.error(
      "Example: arkade swap-to-stable 100000 usdc_pol polygon 0x...",
    );
    process.exit(1);
  }

  const sats = parseInt(amount, 10);
  if (isNaN(sats) || sats <= 0) {
    console.error("Error: Invalid amount.");
    process.exit(1);
  }

  const lendaswap = await createLendaSwap();

  console.log(`Swapping ${formatSats(sats)} sats to ${targetToken}...`);

  try {
    const result = await lendaswap.swapBtcToStablecoin({
      sourceAmount: sats,
      targetToken,
      targetChain,
      targetAddress,
    });

    console.log("Swap created and funded!");
    console.log(`Swap ID: ${result.swapId}`);
    console.log(`Status: ${result.status}`);
    console.log(`Expected: ${result.targetAmount} ${targetToken}`);
    if (result.fundingTxid) {
      console.log(`Funding TX: ${result.fundingTxid}`);
    }
    if (result.paymentDetails?.address) {
      console.log(`VHTLC Address: ${result.paymentDetails.address}`);
    }
    console.log(`Fee: ${result.fee.amount} sats`);
    console.log(`Expires: ${result.expiresAt.toLocaleString()}`);
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

/**
 * Swap stablecoin to BTC command.
 */
async function cmdSwapToBtc(amount, sourceToken, sourceChain, evmAddress) {
  if (!amount || !sourceToken || !sourceChain || !evmAddress) {
    console.error("Error: All parameters required.");
    console.error(
      "Usage: arkade swap-to-btc <amount> <token> <chain> <your-evm-address>",
    );
    console.error("Example: arkade swap-to-btc 100 usdc_pol polygon 0x...");
    process.exit(1);
  }

  const tokenAmount = parseFloat(amount);
  if (isNaN(tokenAmount) || tokenAmount <= 0) {
    console.error("Error: Invalid amount.");
    process.exit(1);
  }

  const lendaswap = await createLendaSwap();
  const wallet = lendaswap.getWallet();
  const arkAddress = await wallet.getAddress();

  console.log(`Swapping ${tokenAmount} ${sourceToken} to BTC...`);

  try {
    const result = await lendaswap.swapStablecoinToBtc({
      sourceAmount: tokenAmount,
      sourceToken,
      sourceChain,
      targetAddress: arkAddress,
      userAddress: evmAddress,
    });

    console.log("Swap created!");
    console.log(`Swap ID: ${result.swapId}`);
    console.log(`Status: ${result.status}`);
    console.log(`Expected: ${result.targetAmount} sats`);
    if (result.paymentDetails?.address) {
      console.log(`HTLC Address: ${result.paymentDetails.address}`);
    }
    if (result.paymentDetails?.callData) {
      console.log(`Token Address: ${result.paymentDetails.callData}`);
    }
    console.log(`Fee: ${result.fee.amount} sats`);
    console.log(`Expires: ${result.expiresAt.toLocaleString()}`);
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

/**
 * Check swap status command.
 */
async function cmdSwapStatus(swapId) {
  if (!swapId) {
    console.error("Error: Swap ID required.");
    console.error("Usage: arkade swap-status <swap-id>");
    process.exit(1);
  }

  const lendaswap = await createLendaSwap();

  try {
    const status = await lendaswap.getSwapStatus(swapId);

    console.log("Swap Status:");
    console.log("------------");
    console.log(`ID: ${status.id}`);
    console.log(`Direction: ${status.direction}`);
    console.log(`Status: ${status.status}`);
    console.log(`From: ${status.sourceAmount} ${status.sourceToken}`);
    console.log(`To: ${status.targetAmount} ${status.targetToken}`);
    console.log(`Created: ${status.createdAt.toLocaleString()}`);
    if (status.completedAt) {
      console.log(`Completed: ${status.completedAt.toLocaleString()}`);
    }
    if (status.txid) {
      console.log(`TX ID: ${status.txid}`);
    }
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

/**
 * Show pending stablecoin swaps command.
 */
async function cmdSwapPending() {
  const lendaswap = await createLendaSwap();

  try {
    const pending = await lendaswap.getPendingSwaps();

    if (pending.length === 0) {
      console.log("No pending swaps.");
      return;
    }

    console.log("Pending Stablecoin Swaps:");
    console.log("-------------------------");

    for (const swap of pending) {
      const date = swap.createdAt.toLocaleString();
      console.log(`${swap.id} | ${swap.direction} | ${swap.status} | ${date}`);
      console.log(
        `  ${swap.sourceAmount} ${swap.sourceToken} → ${swap.targetAmount} ${swap.targetToken}`,
      );
    }
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

/**
 * Show available stablecoin pairs command.
 */
async function cmdSwapPairs() {
  const lendaswap = await createLendaSwap();

  try {
    const pairs = await lendaswap.getAvailablePairs();

    console.log("Available Trading Pairs:");
    console.log("------------------------");

    for (const pair of pairs) {
      console.log(`${pair.from} → ${pair.to}`);
      console.log(
        `  Min: ${pair.minAmount} | Max: ${pair.maxAmount} | Fee: ${pair.feePercentage}%`,
      );
    }
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

/**
 * Claim a swap command.
 */
async function cmdSwapClaim(swapId) {
  if (!swapId) {
    console.error("Error: Swap ID required.");
    console.error("Usage: arkade swap-claim <swap-id>");
    process.exit(1);
  }

  const lendaswap = await createLendaSwap();

  try {
    const result = await lendaswap.claimSwap(swapId);

    if (result.success) {
      console.log("Swap claimed successfully!");
      if (result.chain) {
        console.log(`Chain: ${result.chain}`);
      }
      if (result.txHash) {
        console.log(`TX Hash: ${result.txHash}`);
      }
    } else {
      console.log(`Claim status: ${result.message}`);
    }
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

/**
 * Refund a swap command.
 */
async function cmdSwapRefund(swapId, destinationAddress) {
  if (!swapId) {
    console.error("Error: Swap ID required.");
    console.error("Usage: arkade swap-refund <swap-id> [destination-address]");
    process.exit(1);
  }

  const lendaswap = await createLendaSwap();

  try {
    const options = destinationAddress ? { destinationAddress } : undefined;
    const result = await lendaswap.refundSwap(swapId, options);

    if (result.success) {
      console.log("Swap refunded successfully!");
      if (result.txId) {
        console.log(`TX ID: ${result.txId}`);
      }
      if (result.refundAmount != null) {
        console.log(`Refund Amount: ${formatSats(result.refundAmount)} sats`);
      }
    } else {
      console.log(`Refund status: ${result.message}`);
    }
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

/**
 * Main entry point.
 */
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
    case "init":
      await cmdInit(args[1]);
      break;
    case "address":
      await cmdAddress();
      break;
    case "boarding-address":
      await cmdBoardingAddress();
      break;
    case "balance":
      await cmdBalance();
      break;
    case "send":
      await cmdSend(args[1], args[2]);
      break;
    case "history":
      await cmdHistory();
      break;
    case "onboard":
      await cmdOnboard();
      break;
    case "offboard":
      await cmdOffboard(args[1]);
      break;
    case "ln-invoice":
      await cmdLnInvoice(args[1], args.slice(2).join(" "));
      break;
    case "ln-pay":
      await cmdLnPay(args[1]);
      break;
    case "ln-fees":
      await cmdLnFees();
      break;
    case "ln-limits":
      await cmdLnLimits();
      break;
    case "ln-pending":
      await cmdLnPending();
      break;
    case "swap-quote":
      await cmdSwapQuote(args[1], args[2], args[3]);
      break;
    case "swap-to-stable":
      await cmdSwapToStable(args[1], args[2], args[3], args[4]);
      break;
    case "swap-to-btc":
      await cmdSwapToBtc(args[1], args[2], args[3], args[4]);
      break;
    case "swap-claim":
      await cmdSwapClaim(args[1]);
      break;
    case "swap-refund":
      await cmdSwapRefund(args[1], args[2]);
      break;
    case "swap-status":
      await cmdSwapStatus(args[1]);
      break;
    case "swap-pending":
      await cmdSwapPending();
      break;
    case "swap-pairs":
      await cmdSwapPairs();
      break;
    case "help":
    case "--help":
    case "-h":
    case undefined:
      printHelp();
      break;
    default:
      console.error(`Unknown command: ${command}`);
      console.error("Run 'arkade help' for usage.");
      process.exit(1);
  }
}

main().catch((e) => {
  console.error(`Error: ${e.message}`);
  process.exit(1);
});
