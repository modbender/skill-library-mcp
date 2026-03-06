#!/usr/bin/env node
/**
 * Link your Solana wallet to your Clawland profile.
 * Requires: CLAWLAND_API_KEY env var (or credentials.json) and wallet.json
 */
const { loadWallet, getApiKey, ensureDeps } = require('./common');

ensureDeps();

async function main() {
  const nacl = require('tweetnacl');
  const bs58 = require('bs58');
  const wallet = loadWallet();
  const apiKey = getApiKey();
  const base = 'https://api.clawlands.xyz/v1';

  // Step 1: Get challenge
  console.log('Getting signing challenge...');
  const challengeRes = await fetch(`${base}/agents/me/wallet/challenge`, {
    headers: { 'Authorization': `Bearer ${apiKey}` },
  });
  const challengeData = await challengeRes.json();
  if (!challengeData.success) {
    console.error('❌ Failed to get challenge:', challengeData.error);
    if (challengeData.hint) console.error('   Hint:', challengeData.hint);
    process.exit(1);
  }
  const message = challengeData.data.message;

  // Step 2: Sign the message
  const msgBytes = new TextEncoder().encode(message);
  const sigBytes = nacl.sign.detached(msgBytes, wallet.secretKey);
  const sigBase58 = (bs58.encode || bs58.default?.encode)(Buffer.from(sigBytes));

  // Step 3: Link wallet
  console.log('Linking wallet...');
  const linkRes = await fetch(`${base}/agents/me/wallet`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      solana_wallet: wallet.publicKey.toBase58(),
      message: message,
      signature: sigBase58,
    }),
  });
  const linkData = await linkRes.json();
  if (!linkData.success) {
    console.error('❌ Failed to link wallet:', linkData.error);
    if (linkData.hint) console.error('   Hint:', linkData.hint);
    process.exit(1);
  }
  console.log(`✅ Wallet linked: ${linkData.data.solana_wallet}`);
}

main().catch(err => { console.error('❌', err.message); process.exit(1); });
