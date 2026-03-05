"use strict";

const { SignerProvider } = require("../config");
const { signEip712Remote, sendTxRemote } = require("./remote");
const { createLocalWallet, signEip712Local } = require("./local");
const { ethers } = require("ethers");

/**
 * Factory — returns a unified wallet-signer interface.
 *
 * The signer is ALWAYS user/operator-controlled. SoHo is credit-only;
 * it never participates in signing.
 *
 * Interface:
 *   { signEip712(typedData) → signature, getAddress() → address, provider?, sendTx? }
 */
function createSigner(config) {
  if (config.signerProvider === SignerProvider.WALLET_SIGNER_REMOTE) {
    return {
      type: "remote",
      async signEip712(typedData) {
        return signEip712Remote(config, typedData);
      },
      async getAddress() {
        throw new Error(
          "getAddress() is not available for WALLET_SIGNER_REMOTE. " +
            "Pass the payer address explicitly or add a /address endpoint to your wallet signing service.",
        );
      },
      async sendTx(txData) {
        return sendTxRemote(config, txData);
      },
    };
  }

  // LOCAL_PRIVATE_KEY — dev-only, gated by config validation
  const wallet = createLocalWallet(config);
  const provider = new ethers.JsonRpcProvider(config.rpcUrl);

  return {
    type: "local",
    wallet,
    provider,
    async signEip712(typedData) {
      return signEip712Local(wallet, typedData);
    },
    async getAddress() {
      return wallet.address;
    },
  };
}

module.exports = { createSigner };
