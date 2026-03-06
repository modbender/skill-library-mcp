/**
 * Skills module for the Arkade SDK.
 *
 * Skills are modular capabilities that provide specific functionality for agents
 * and applications. This module provides skills for:
 *
 * - **ArkadeBitcoinSkill**: Send and receive Bitcoin over Arkade
 * - **ArkaLightningSkill**: Lightning Network payments via Boltz swaps
 * - **LendaSwapSkill**: USDC/USDT stablecoin swaps via LendaSwap
 *
 * @example
 * ```typescript
 * import { Wallet, SingleKey } from "@arkade-os/sdk";
 * import {
 *   ArkadeBitcoinSkill,
 *   ArkaLightningSkill,
 *   LendaSwapSkill,
 * } from "@arkade-os/skill";
 *
 * // Create a wallet
 * const wallet = await Wallet.create({
 *   identity: SingleKey.fromHex(privateKeyHex),
 *   arkServerUrl: "https://arkade.computer",
 * });
 *
 * // === Bitcoin Skill ===
 * const bitcoin = new ArkadeBitcoinSkill(wallet);
 *
 * // Get addresses for receiving
 * const arkAddress = await bitcoin.getArkAddress();
 * console.log("Ark address:", arkAddress);
 *
 * // Check balance
 * const balance = await bitcoin.getBalance();
 * console.log("Balance:", balance.total, "sats");
 *
 * // === Lightning Skill ===
 * const lightning = new ArkaLightningSkill({
 *   wallet,
 *   network: "bitcoin",
 * });
 *
 * // Create invoice to receive Lightning payment
 * const invoice = await lightning.createInvoice({
 *   amount: 25000,
 *   description: "Coffee payment",
 * });
 * console.log("Invoice:", invoice.bolt11);
 *
 * // === LendaSwap Skill ===
 * const lendaswap = new LendaSwapSkill({ wallet });
 *
 * // Get quote for BTC to USDC
 * const quote = await lendaswap.getQuoteBtcToStablecoin(100000, "usdc_pol");
 * console.log("Quote:", quote.targetAmount, "USDC");
 * ```
 *
 * @module skills
 */

// Types and interfaces
export type {
  Skill,
  BitcoinSkill,
  RampSkill,
  LightningSkill,
  StablecoinSwapSkill,
  BitcoinAddress,
  SendParams,
  SendResult,
  BalanceInfo,
  IncomingFundsEvent,
  OnboardParams,
  OffboardParams,
  RampResult,
  LightningInvoice,
  CreateInvoiceParams,
  PayInvoiceParams,
  PaymentResult,
  LightningFees,
  LightningLimits,
  SwapStatus,
  SwapInfo,
  EvmChain,
  StablecoinToken,
  BtcSource,
  BtcToStablecoinParams,
  StablecoinToBtcParams,
  StablecoinSwapResult,
  StablecoinSwapStatus,
  StablecoinSwapInfo,
  StablecoinQuote,
  StablecoinPair,
} from "./types";

// Bitcoin skill
export { ArkadeBitcoinSkill, createArkadeBitcoinSkill } from "./arkadeBitcoin";

// Lightning skill
export {
  ArkaLightningSkill,
  createLightningSkill,
  type ArkaLightningSkillConfig,
} from "./lightning";

// LendaSwap skill
export {
  LendaSwapSkill,
  createLendaSwapSkill,
  type LendaSwapSkillConfig,
} from "./lendaswap";
