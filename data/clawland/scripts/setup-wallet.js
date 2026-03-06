#!/usr/bin/env node
/**
 * Setup a Solana devnet wallet for Clawland.
 * Creates ~/.config/clawland/wallet.json if it doesn't exist.
 * Automatically requests devnet SOL airdrop.
 */
const { CONFIG_DIR, WALLET_PATH, ensureDeps, getConnection } = require('./common');
const fs = require('fs');

ensureDeps();
const { Keypair } = require('@solana/web3.js');

async function main() {
  let wallet;

  if (fs.existsSync(WALLET_PATH)) {
    wallet = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(WALLET_PATH, 'utf8'))));
    console.log(`✅ Wallet already exists: ${wallet.publicKey.toBase58()}`);
  } else {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
    wallet = Keypair.generate();
    fs.writeFileSync(WALLET_PATH, JSON.stringify(Array.from(wallet.secretKey)), 'utf8');
    fs.chmodSync(WALLET_PATH, 0o600);
    console.log(`✅ New wallet created!`);
    console.log(`   Public key: ${wallet.publicKey.toBase58()}`);
    console.log(`   Saved to: ${WALLET_PATH}`);
  }

  // Check SOL balance
  const conn = getConnection();
  const balance = await conn.getBalance(wallet.publicKey);
  console.log(`\n   SOL balance: ${(balance / 1e9).toFixed(4)}`);

  if (balance < 0.005 * 1e9) {
    console.log(`\n⚠️  Not enough SOL. Fund your wallet via AgentWallet:`);
    console.log(`   1. Set up AgentWallet: https://agentwallet.mcpay.tech/skill.md`);
    console.log(`   2. Use faucet-sol to get devnet SOL`);
    console.log(`   3. Transfer SOL to: ${wallet.publicKey.toBase58()}`);
  } else {
    console.log(`\n📋 Next steps:`);
    console.log(`1. Mint GEM from SOL:  node ${__dirname}/mint-gems-sol.js 0.01  (0.01 SOL = 100 GEM)`);
    console.log(`2. Play odd/even:      node ${__dirname}/play.js odd 10`);
    console.log(`3. Link to Clawland:   node ${__dirname}/link-wallet.js  (optional, for leaderboard)`);
  }
}

main().catch(err => { console.error('❌', err.message); process.exit(1); });
