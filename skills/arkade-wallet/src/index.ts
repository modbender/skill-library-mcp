/**
 * @arkade-os/skill - Arkade SDK Skills for Agent Integration
 *
 * This package provides skills for sending and receiving Bitcoin over
 * Arkade and Lightning, designed for agent integration (CLI-friendly
 * for agents like MoltBot).
 *
 * ## Available Skills
 *
 * - **ArkadeBitcoinSkill**: Send/receive Bitcoin via Arkade with on/off ramp support
 * - **ArkaLightningSkill**: Lightning Network payments via Boltz submarine swaps
 * - **LendaSwapSkill**: USDC/USDT stablecoin swaps via LendaSwap
 *
 * ## Quick Start
 *
 * ```typescript
 * import { Wallet, SingleKey } from "@arkade-os/sdk";
 * import {
 *   ArkadeBitcoinSkill,
 *   ArkaLightningSkill,
 *   LendaSwapSkill,
 * } from "@arkade-os/skill";
 *
 * // Create a wallet (default server: arkade.computer)
 * const wallet = await Wallet.create({
 *   identity: SingleKey.fromHex(privateKeyHex),
 *   arkServerUrl: "https://arkade.computer",
 * });
 *
 * // Bitcoin operations
 * const bitcoin = new ArkadeBitcoinSkill(wallet);
 * const balance = await bitcoin.getBalance();
 *
 * // Lightning operations
 * const lightning = new ArkaLightningSkill({ wallet, network: "bitcoin" });
 * const invoice = await lightning.createInvoice({ amount: 50000 });
 *
 * // Stablecoin swaps
 * const lendaswap = new LendaSwapSkill({ wallet });
 * const quote = await lendaswap.getQuoteBtcToStablecoin(100000, "usdc_pol");
 * ```
 *
 * ## CLI Usage
 *
 * ```bash
 * # Initialize wallet (default server: arkade.computer)
 * arkade init <private-key-hex>
 *
 * # Show addresses
 * arkade address
 * arkade boarding-address
 *
 * # Check balance
 * arkade balance
 *
 * # Send Bitcoin
 * arkade send <ark-address> <amount-sats>
 *
 * # Lightning
 * arkade ln-invoice <amount> [description]
 * arkade ln-pay <bolt11>
 *
 * # Stablecoins
 * arkade swap-quote <amount> <from> <to>
 * arkade swap-pairs
 * ```
 *
 * @packageDocumentation
 */

// Re-export all skills and types
export * from "./skills";

// Re-export commonly used types from @arkade-os/sdk
export type {
  Wallet,
  ArkTransaction,
  WalletBalance,
  ExtendedCoin,
  ExtendedVirtualCoin,
  FeeInfo,
  SettlementEvent,
  NetworkName,
} from "@arkade-os/sdk";
