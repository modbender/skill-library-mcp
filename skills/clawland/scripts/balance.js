#!/usr/bin/env node
/**
 * Check GEM and USDC balances for your Clawland wallet.
 */
const { loadWallet, getConnection, getUsdcMint, getGemMint, ensureDeps } = require('./common');

ensureDeps();

async function main() {
  const { getAssociatedTokenAddress, getAccount } = require('@solana/spl-token');
  const wallet = loadWallet();
  const conn = getConnection();
  const usdcMint = getUsdcMint();
  const gemMint = getGemMint();

  console.log(`Wallet: ${wallet.publicKey.toBase58()}\n`);

  // SOL balance
  const solBalance = await conn.getBalance(wallet.publicKey);
  console.log(`SOL:  ${(solBalance / 1e9).toFixed(4)}`);

  // USDC balance
  try {
    const usdcAta = await getAssociatedTokenAddress(usdcMint, wallet.publicKey);
    const usdcAccount = await getAccount(conn, usdcAta);
    console.log(`USDC: ${(Number(usdcAccount.amount) / 1e6).toFixed(2)}`);
  } catch {
    console.log(`USDC: 0.00 (no token account)`);
  }

  // GEM balance
  try {
    const gemAta = await getAssociatedTokenAddress(gemMint, wallet.publicKey);
    const gemAccount = await getAccount(conn, gemAta);
    console.log(`GEM:  ${(Number(gemAccount.amount) / 1e6).toFixed(2)}`);
  } catch {
    console.log(`GEM:  0.00 (no token account)`);
  }
}

main().catch(err => { console.error('❌', err.message); process.exit(1); });
