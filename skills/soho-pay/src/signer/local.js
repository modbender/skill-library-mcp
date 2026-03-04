"use strict";

const { ethers } = require("ethers");

/**
 * Local private-key signer — DEV / TESTNET ONLY.
 *
 * This key belongs to the user or agent operator, NOT to SoHo.
 * SoHo never custodies, generates, or controls signing keys.
 *
 * Uses SOHO_DEV_PRIVATE_KEY from env. Config validation in config.js
 * ensures this path is only reachable on testnets (or with the explicit
 * DEV_ALLOW_LOCAL_KEY=YES override, which is strongly discouraged for
 * mainnet).
 */
function createLocalWallet(config) {
  if (!config.devPrivateKey) {
    throw new Error("SOHO_DEV_PRIVATE_KEY is not set");
  }
  const provider = new ethers.JsonRpcProvider(config.rpcUrl);
  return new ethers.Wallet(config.devPrivateKey, provider);
}

async function signEip712Local(wallet, { domain, types, message }) {
  return wallet.signTypedData(domain, types, message);
}

module.exports = { createLocalWallet, signEip712Local };
