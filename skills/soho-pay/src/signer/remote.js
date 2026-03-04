"use strict";

/**
 * Wallet Signer — Remote (user/operator-controlled)
 *
 * Delegates EIP-712 signing and (optionally) tx broadcast to an external
 * wallet service owned by the user or agent operator. Examples:
 *   - Turnkey, Privy, Fireblocks, or any MPC / HSM provider
 *   - A self-hosted signing service
 *
 * SoHo does NOT provide this service. SoHo is a credit layer only — it
 * never custodies keys, holds key shards, or produces signatures.
 *
 * Expected API:
 *   POST {WALLET_SIGNER_SERVICE_URL}/sign-eip712  → { signature }
 *   POST {WALLET_SIGNER_SERVICE_URL}/send-tx       → { txHash }  (optional)
 */

function _headers(config) {
  const h = { "Content-Type": "application/json" };
  if (config.signerServiceAuthToken) {
    h["Authorization"] = `Bearer ${config.signerServiceAuthToken}`;
  }
  return h;
}

async function signEip712Remote(config, { domain, types, message }) {
  const url = `${config.walletSignerServiceUrl}/sign-eip712`;

  const res = await fetch(url, {
    method: "POST",
    headers: _headers(config),
    body: JSON.stringify({ domain, types, message }),
  });

  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(
      `Wallet signer returned ${res.status}: ${body || res.statusText}`,
    );
  }

  const { signature } = await res.json();
  if (!signature) {
    throw new Error("Wallet signer did not return a signature");
  }
  return signature;
}

async function sendTxRemote(config, txData) {
  const url = `${config.walletSignerServiceUrl}/send-tx`;

  const res = await fetch(url, {
    method: "POST",
    headers: _headers(config),
    body: JSON.stringify(txData),
  });

  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(
      `Wallet signer send-tx returned ${res.status}: ${body || res.statusText}`,
    );
  }

  const { txHash } = await res.json();
  if (!txHash) {
    throw new Error("Wallet signer send-tx did not return a txHash");
  }
  return txHash;
}

module.exports = { signEip712Remote, sendTxRemote };
