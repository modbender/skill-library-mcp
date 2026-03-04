#!/usr/bin/env node
/**
 * Mint GEM tokens using SOL (devnet fixed rate: 1 SOL = 10,000 GEM).
 * Usage: node mint-gems-sol.js <sol_amount>
 * Example: node mint-gems-sol.js 0.01   (mints 100 GEM from 0.01 SOL)
 */
const { loadWallet, getConnection, getProgramId, getGameState, getGemMint, getTreasury, ensureDeps } = require('./common');

ensureDeps();

async function main() {
  const solAmount = parseFloat(process.argv[2]);
  if (!solAmount || solAmount <= 0) {
    console.error('Usage: node mint-gems-sol.js <sol_amount>');
    console.error('Example: node mint-gems-sol.js 0.01  (0.01 SOL = 100 GEM)');
    process.exit(1);
  }

  const { Transaction, TransactionInstruction, SystemProgram } = require('@solana/web3.js');
  const { getAssociatedTokenAddress, createAssociatedTokenAccountInstruction, TOKEN_PROGRAM_ID, getAccount } = require('@solana/spl-token');

  const wallet = loadWallet();
  const conn = getConnection();
  const programId = getProgramId();
  const gameState = getGameState();
  const gemMint = getGemMint();
  const treasury = getTreasury();
  const playerGemAta = await getAssociatedTokenAddress(gemMint, wallet.publicKey);

  const lamports = BigInt(Math.round(solAmount * 1e9));
  const expectedGem = solAmount * 10000;
  console.log(`Minting ~${expectedGem} GEM from ${solAmount} SOL...`);

  // Pre-flight: check SOL balance
  const solBal = await conn.getBalance(wallet.publicKey);
  if (BigInt(solBal) < lamports + 10000n) {
    console.error(`❌ Not enough SOL. Have ${(solBal / 1e9).toFixed(4)}, need ${solAmount} + fees.`);
    process.exit(1);
  }

  const tx = new Transaction();

  // Create GEM ATA if needed
  try {
    await getAccount(conn, playerGemAta);
  } catch {
    console.log('Creating GEM token account...');
    tx.add(createAssociatedTokenAccountInstruction(
      wallet.publicKey, playerGemAta, wallet.publicKey, gemMint
    ));
  }

  // Build mint_gems_with_sol instruction
  const crypto = require('crypto');
  const discriminator = crypto.createHash('sha256').update('global:mint_gems_with_sol').digest().slice(0, 8);
  const data = Buffer.alloc(16);
  discriminator.copy(data);
  data.writeBigUInt64LE(lamports, 8);

  tx.add(new TransactionInstruction({
    programId,
    keys: [
      { pubkey: wallet.publicKey, isSigner: true, isWritable: true },
      { pubkey: gameState, isSigner: false, isWritable: true },
      { pubkey: gemMint, isSigner: false, isWritable: true },
      { pubkey: playerGemAta, isSigner: false, isWritable: true },
      { pubkey: treasury, isSigner: false, isWritable: true },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
    ],
    data,
  }));

  const sig = await conn.sendTransaction(tx, [wallet]);
  await conn.confirmTransaction(sig, 'confirmed');
  console.log(`✅ Minted! TX: ${sig}`);
  console.log(`   Explorer: https://explorer.solana.com/tx/${sig}?cluster=devnet`);

  // Show balance
  try {
    const gemAccount = await getAccount(conn, playerGemAta);
    console.log(`   GEM balance: ${(Number(gemAccount.amount) / 1e6).toFixed(2)}`);
  } catch {}
}

main().catch(err => { console.error('❌', err.message); process.exit(1); });
