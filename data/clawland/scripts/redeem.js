#!/usr/bin/env node
/**
 * Redeem GEM back to USDC (5% fee to treasury).
 * Usage: node redeem.js <gem_amount>
 * Example: node redeem.js 50   (redeem 50 GEM → ~0.475 USDC)
 */
const { loadWallet, getConnection, getProgramId, getUsdcMint, getGameState, getGemMint, getUsdcVault, getTreasury, ensureDeps } = require('./common');

ensureDeps();

async function main() {
  const gemAmount = parseFloat(process.argv[2]);
  if (!gemAmount || gemAmount <= 0) {
    console.error('Usage: node redeem.js <gem_amount>');
    console.error('Example: node redeem.js 50  (50 GEM → ~0.475 USDC)');
    process.exit(1);
  }

  const { Transaction, TransactionInstruction } = require('@solana/web3.js');
  const { getAssociatedTokenAddress, TOKEN_PROGRAM_ID, getAccount } = require('@solana/spl-token');

  const wallet = loadWallet();
  const conn = getConnection();
  const programId = getProgramId();
  const usdcMint = getUsdcMint();
  const gameState = getGameState();
  const gemMint = getGemMint();
  const usdcVault = getUsdcVault();
  const treasury = getTreasury();

  const playerUsdcAta = await getAssociatedTokenAddress(usdcMint, wallet.publicKey);
  const playerGemAta = await getAssociatedTokenAddress(gemMint, wallet.publicKey);
  const treasuryUsdcAta = await getAssociatedTokenAddress(usdcMint, treasury);

  // Pre-flight: check GEM balance
  try {
    const gemAccount = await getAccount(conn, playerGemAta);
    const gemBal = Number(gemAccount.amount) / 1e6;
    if (gemBal < gemAmount) {
      console.error(`❌ Not enough GEM. Have ${gemBal}, need ${gemAmount}.`);
      process.exit(1);
    }
  } catch {
    console.error('❌ No GEM token account.');
    process.exit(1);
  }

  const gemBaseUnits = BigInt(Math.round(gemAmount * 1e6));
  const expectedUsdc = (gemAmount / 100 * 0.95).toFixed(4);
  console.log(`Redeeming ${gemAmount} GEM for ~${expectedUsdc} USDC...`);

  const crypto = require('crypto');
  const discriminator = crypto.createHash('sha256').update('global:redeem_gems').digest().slice(0, 8);
  const data = Buffer.alloc(16);
  discriminator.copy(data);
  data.writeBigUInt64LE(gemBaseUnits, 8);

  const tx = new Transaction();
  tx.add(new TransactionInstruction({
    programId,
    keys: [
      { pubkey: wallet.publicKey, isSigner: true, isWritable: true },
      { pubkey: gameState, isSigner: false, isWritable: true },
      { pubkey: gemMint, isSigner: false, isWritable: true },
      { pubkey: playerUsdcAta, isSigner: false, isWritable: true },
      { pubkey: usdcVault, isSigner: false, isWritable: true },
      { pubkey: treasuryUsdcAta, isSigner: false, isWritable: true },
      { pubkey: playerGemAta, isSigner: false, isWritable: true },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
    ],
    data,
  }));

  const sig = await conn.sendTransaction(tx, [wallet]);
  await conn.confirmTransaction(sig, 'confirmed');
  console.log(`✅ Redeemed! TX: ${sig}`);
  console.log(`   Explorer: https://explorer.solana.com/tx/${sig}?cluster=devnet`);

  try {
    const usdcAccount = await getAccount(conn, playerUsdcAta);
    console.log(`   USDC balance: ${(Number(usdcAccount.amount) / 1e6).toFixed(2)}`);
  } catch {}
}

main().catch(err => { console.error('❌', err.message); process.exit(1); });
