import { initiateDeveloperControlledWalletsClient } from "@circle-fin/developer-controlled-wallets";

///////////////////////////////////////////////////////////////////////////////
// Circle Programmable Wallets client for secure agent-native key management.
// Uses MPC-secured developer-controlled wallets — no raw private keys needed.
// This client wraps the Circle SDK to provide Gateway-specific operations:
// - EIP-712 signing for burn intents
// - Contract execution for approve, deposit, mint
// - Transaction polling for confirmation

// Maps our internal chain names to Circle blockchain identifiers
const BLOCKCHAIN_MAP = {
  sepolia: "ETH-SEPOLIA",
  baseSepolia: "BASE-SEPOLIA",
  arcTestnet: "ARC-TESTNET",
};

/**
 * Custom JSON serializer that handles BigInt values.
 * Circle's signTypedData API accepts EIP-712 typed data as a JSON string,
 * but JSON.stringify chokes on BigInt. We convert to string representation.
 */
function bigIntSerializer(key, value) {
  if (typeof value === "bigint") return value.toString();
  return value;
}

export class CircleWalletClient {
  constructor() {
    this.client = initiateDeveloperControlledWalletsClient({
      apiKey: process.env.CIRCLE_API_KEY,
      entitySecret: process.env.CIRCLE_ENTITY_SECRET,
    });
    this.walletSetId = process.env.CIRCLE_WALLET_SET_ID;
    this.wallets = {}; // chainName -> { walletId, address, blockchain }
    this.address = null;
  }

  /**
   * Initialize: discover wallets in the wallet set for each needed chain.
   * If a wallet doesn't exist for a chain, create one automatically.
   */
  async init() {
    console.log("🔐 Initializing Circle Programmable Wallets...");

    // List existing wallets in the set
    const response = await this.client.listWallets({
      walletSetId: this.walletSetId,
    });
    const existingWallets = response.data?.wallets || [];

    // Map existing wallets by blockchain
    for (const w of existingWallets) {
      for (const [chainName, blockchain] of Object.entries(BLOCKCHAIN_MAP)) {
        if (w.blockchain === blockchain && w.state === "LIVE") {
          this.wallets[chainName] = {
            walletId: w.id,
            address: w.address,
            blockchain,
          };
        }
      }
    }

    // Create wallets for any missing chains
    const missingChains = Object.entries(BLOCKCHAIN_MAP).filter(
      ([name]) => !this.wallets[name]
    );

    if (missingChains.length > 0) {
      console.log(
        `   Creating wallets for: ${missingChains.map(([, b]) => b).join(", ")}`
      );
      const createResponse = await this.client.createWallets({
        blockchains: missingChains.map(([, blockchain]) => blockchain),
        count: 1,
        walletSetId: this.walletSetId,
      });
      const created = createResponse.data?.wallets || [];
      for (const w of created) {
        for (const [chainName, blockchain] of missingChains) {
          if (w.blockchain === blockchain) {
            this.wallets[chainName] = {
              walletId: w.id,
              address: w.address,
              blockchain,
            };
          }
        }
      }
    }

    // All wallets in a set share the same address
    const firstWallet = Object.values(this.wallets)[0];
    if (!firstWallet) {
      throw new Error("No wallets found or created. Check your CIRCLE_WALLET_SET_ID.");
    }
    this.address = firstWallet.address;

    console.log(`   ✅ Wallet address: ${this.address}`);
    for (const [name, w] of Object.entries(this.wallets)) {
      console.log(`   • ${w.blockchain}: ${w.walletId}`);
    }

    return this;
  }

  /**
   * Get wallet ID for a given chain name.
   */
  walletIdForChain(chainName) {
    const w = this.wallets[chainName];
    if (!w) throw new Error(`No wallet found for chain: ${chainName}`);
    return w.walletId;
  }

  /**
   * Sign EIP-712 typed data using Circle's MPC signing.
   * Returns the signature as a hex string (0x-prefixed).
   *
   * @param {string} chainName - e.g. "sepolia", "arcTestnet"
   * @param {Object} typedData - Full EIP-712 typed data { types, domain, primaryType, message }
   * @param {string} [memo] - Human-readable description
   * @returns {Promise<string>} Hex-encoded signature
   */
  async signTypedData(chainName, typedData, memo) {
    const walletId = this.walletIdForChain(chainName);
    const response = await this.client.signTypedData({
      walletId,
      data: JSON.stringify(typedData, bigIntSerializer),
      memo: memo || "Gateway burn intent",
    });

    let sig = response.data?.signature;
    if (!sig) throw new Error("signTypedData returned no signature");

    // Ensure hex format (Circle may return base64 for some chains)
    if (!sig.startsWith("0x")) {
      sig = "0x" + Buffer.from(sig, "base64").toString("hex");
    }
    return sig;
  }

  /**
   * Execute a smart contract function via Circle's transaction API.
   * Submits the transaction and polls until it completes.
   *
   * @param {string} chainName - e.g. "sepolia", "baseSepolia", "arcTestnet"
   * @param {Object} opts
   * @param {string} opts.contractAddress - Target contract
   * @param {string} opts.functionSignature - e.g. "approve(address,uint256)"
   * @param {Array} opts.params - ABI parameters
   * @param {string} [opts.feeLevel] - "LOW", "MEDIUM", or "HIGH"
   * @returns {Promise<Object>} Completed transaction object
   */
  async executeContract(
    chainName,
    { contractAddress, functionSignature, params, feeLevel = "MEDIUM" }
  ) {
    const walletId = this.walletIdForChain(chainName);
    const response = await this.client.createContractExecutionTransaction({
      walletId,
      contractAddress,
      abiFunctionSignature: functionSignature,
      abiParameters: params,
      fee: { type: "level", config: { feeLevel } },
    });

    const txId = response.data?.id;
    if (!txId) throw new Error("createContractExecutionTransaction returned no id");

    // Poll for completion
    return this.waitForTransaction(txId);
  }

  /**
   * Poll a transaction until it reaches a terminal state.
   */
  async waitForTransaction(txId, timeoutMs = 120_000) {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      const response = await this.client.getTransaction({ id: txId });
      const tx = response.data?.transaction;

      if (tx?.state === "COMPLETE") return tx;
      if (tx?.state === "FAILED" || tx?.state === "CANCELLED" || tx?.state === "DENIED") {
        throw new Error(
          `Transaction ${txId} ${tx.state}: ${tx.errorReason || "unknown error"}`
        );
      }

      await new Promise((r) => setTimeout(r, 2000)); // Poll every 2s
    }
    throw new Error(`Transaction ${txId} timed out after ${timeoutMs}ms`);
  }
}
