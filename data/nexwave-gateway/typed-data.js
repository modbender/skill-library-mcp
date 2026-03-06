import { randomBytes } from "node:crypto";
import { pad, zeroAddress, maxUint256 } from "viem";

///////////////////////////////////////////////////////////////////////////////
// EIP-712 typed data utilities for Gateway burn intents
// Burn intents are the signed messages that authorize Gateway to burn USDC
// from your unified balance on a source chain and mint on a destination chain.

const domain = { name: "GatewayWallet", version: "1" };

const EIP712Domain = [
  { name: "name", type: "string" },
  { name: "version", type: "string" },
];

const TransferSpec = [
  { name: "version", type: "uint32" },
  { name: "sourceDomain", type: "uint32" },
  { name: "destinationDomain", type: "uint32" },
  { name: "sourceContract", type: "bytes32" },
  { name: "destinationContract", type: "bytes32" },
  { name: "sourceToken", type: "bytes32" },
  { name: "destinationToken", type: "bytes32" },
  { name: "sourceDepositor", type: "bytes32" },
  { name: "destinationRecipient", type: "bytes32" },
  { name: "sourceSigner", type: "bytes32" },
  { name: "destinationCaller", type: "bytes32" },
  { name: "value", type: "uint256" },
  { name: "salt", type: "bytes32" },
  { name: "hookData", type: "bytes" },
];

const BurnIntent = [
  { name: "maxBlockHeight", type: "uint256" },
  { name: "maxFee", type: "uint256" },
  { name: "spec", type: "TransferSpec" },
];

const BurnIntentSet = [{ name: "intents", type: "BurnIntent[]" }];

function addressToBytes32(address) {
  return pad(address.toLowerCase(), { size: 32 });
}

/**
 * Construct a burn intent for transferring USDC from one chain to another.
 *
 * @param {Object} params
 * @param {string} params.walletAddress - The wallet address (hex string)
 * @param {Object} params.from - Source chain config (from setup-gateway.js)
 * @param {Object} params.to - Destination chain config (from setup-gateway.js)
 * @param {number} params.amount - Amount of USDC to transfer (in human units, e.g. 2 = 2 USDC)
 * @param {string} [params.recipient] - Destination address (defaults to walletAddress)
 */
export function burnIntent({ walletAddress, from, to, amount, recipient }) {
  return {
    maxBlockHeight: maxUint256, // Needs to be at least 7 days in the future
    maxFee: 2_010000n, // 2.01 USDC covers fees on any chain
    spec: {
      version: 1,
      sourceDomain: from.domain,
      destinationDomain: to.domain,
      sourceContract: from.gatewayWalletAddress,
      destinationContract: from.gatewayMinterAddress,
      sourceToken: from.usdcAddress,
      destinationToken: to.usdcAddress,
      sourceDepositor: walletAddress,
      destinationRecipient: recipient || walletAddress,
      sourceSigner: walletAddress,
      destinationCaller: zeroAddress, // Anyone can submit the attestation
      value: BigInt(Math.floor(amount * 1e6)), // Convert to USDC atomic units (6 decimals)
      salt: "0x" + randomBytes(32).toString("hex"),
      hookData: "0x", // No hook data
    },
  };
}

/**
 * Create EIP-712 typed data for a single burn intent (for signing).
 */
export function burnIntentTypedData(intent) {
  return {
    types: { EIP712Domain, TransferSpec, BurnIntent },
    domain,
    primaryType: "BurnIntent",
    message: {
      ...intent,
      spec: {
        ...intent.spec,
        sourceContract: addressToBytes32(intent.spec.sourceContract),
        destinationContract: addressToBytes32(intent.spec.destinationContract),
        sourceToken: addressToBytes32(intent.spec.sourceToken),
        destinationToken: addressToBytes32(intent.spec.destinationToken),
        sourceDepositor: addressToBytes32(intent.spec.sourceDepositor),
        destinationRecipient: addressToBytes32(intent.spec.destinationRecipient),
        sourceSigner: addressToBytes32(intent.spec.sourceSigner),
        destinationCaller: addressToBytes32(
          intent.spec.destinationCaller ?? zeroAddress
        ),
      },
    },
  };
}

/**
 * Create EIP-712 typed data for a set of burn intents (batch transfer).
 */
export function burnIntentSetTypedData({ intents }) {
  return {
    types: { EIP712Domain, TransferSpec, BurnIntent, BurnIntentSet },
    domain,
    primaryType: "BurnIntentSet",
    message: {
      intents: intents.map((intent) => burnIntentTypedData(intent).message),
    },
  };
}
