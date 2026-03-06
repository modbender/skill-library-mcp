#!/usr/bin/env node
/**
 * Mint GEM tokens from USDC.
 * Usage: node mint-gems.js <usdc_amount>
 * Example: node mint-gems.js 1   (mints 100 GEM from 1 USDC)
 */
const { loadWallet, getConnection, getProgramId, getUsdcMint, getGameState, getGemMint, getUsdcVault, ensureDeps } = require('./common');

ensureDeps();

async function main() {
  const usdcAmount = parseFloat(process.argv[2]);
  if (!usdcAmount || usdcAmount <= 0) {
    console.error('Usage: node mint-gems.js <usdc_amount>');
    console.error('Example: node mint-gems.js 1  (1 USDC = 100 GEM)');
    process.exit(1);
  }

  const { Transaction, TransactionInstruction } = require('@solana/web3.js');
  const { getAssociatedTokenAddress, createAssociatedTokenAccountInstruction, TOKEN_PROGRAM_ID, getAccount } = require('@solana/spl-token');

  const wallet = loadWallet();
  const conn = getConnection();
  const programId = getProgramId();
  const usdcMint = getUsdcMint();
  const gameState = getGameState();
  const gemMint = getGemMint();
  const usdcVault = getUsdcVault();

  const playerUsdcAta = await getAssociatedTokenAddress(usdcMint, wallet.publicKey);
  const playerGemAta = await getAssociatedTokenAddress(gemMint, wallet.publicKey);

  const baseUnits = BigInt(Math.round(usdcAmount * 1e6));
  console.log(`Minting GEM from ${usdcAmount} USDC (${baseUnits} base units)...`);

  // Pre-flight: check USDC balance
  try {
    const usdcAccount = await getAccount(conn, playerUsdcAta);
    const usdcBal = Number(usdcAccount.amount) / 1e6;
    if (usdcBal < usdcAmount) {
      console.error(`❌ Not enough USDC. Have ${usdcBal}, need ${usdcAmount}.`);
      console.error('   Tip: Use mint-gems-sol.js instead (only needs SOL).');
      process.exit(1);
    }
  } catch {
    console.error('❌ No USDC token account.');
    console.error('   Tip: Use mint-gems-sol.js instead (only needs SOL).');
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

  const crypto = require('crypto');
  const discriminator = crypto.createHash('sha256').update('global:mint_gems').digest().slice(0, 8);
  const data = Buffer.alloc(16);
  discriminator.copy(data);
  data.writeBigUInt64LE(baseUnits, 8);

  tx.add(new TransactionInstruction({
    programId,
    keys: [
      { pubkey: wallet.publicKey, isSigner: true, isWritable: true },
      { pubkey: gameState, isSigner: false, isWritable: true },
      { pubkey: gemMint, isSigner: false, isWritable: true },
      { pubkey: playerUsdcAta, isSigner: false, isWritable: true },
      { pubkey: usdcVault, isSigner: false, isWritable: true },
      { pubkey: playerGemAta, isSigner: false, isWritable: true },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
    ],
    data,
  }));

  const sig = await conn.sendTransaction(tx, [wallet]);
  await conn.confirmTransaction(sig, 'confirmed');
  console.log(`✅ Minted! TX: ${sig}`);
  console.log(`   Explorer: https://explorer.solana.com/tx/${sig}?cluster=devnet`);

  try {
    const gemAccount = await getAccount(conn, playerGemAta);
    console.log(`   GEM balance: ${(Number(gemAccount.amount) / 1e6).toFixed(2)}`);
  } catch {}
}

main().catch(err => { console.error('❌', err.message); process.exit(1); });
