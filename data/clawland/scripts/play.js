#!/usr/bin/env node
/**
 * Play on-chain odd/even.
 * Usage: node play.js <odd|even> <gem_bet_amount>
 * Example: node play.js odd 10   (bet 10 GEM on odd)
 */
const { loadWallet, getConnection, getProgramId, getGameState, getGemMint, ensureDeps } = require('./common');

ensureDeps();

async function main() {
  const choice = process.argv[2]?.toLowerCase();
  const betAmount = parseFloat(process.argv[3]);

  if (!['odd', 'even'].includes(choice) || !betAmount || betAmount <= 0) {
    console.error('Usage: node play.js <odd|even> <gem_bet_amount>');
    console.error('Example: node play.js odd 10');
    process.exit(1);
  }

  const { Transaction, TransactionInstruction } = require('@solana/web3.js');
  const { getAssociatedTokenAddress, TOKEN_PROGRAM_ID, getAccount } = require('@solana/spl-token');

  const wallet = loadWallet();
  const conn = getConnection();
  const programId = getProgramId();
  const gameState = getGameState();
  const gemMint = getGemMint();
  const playerGemAta = await getAssociatedTokenAddress(gemMint, wallet.publicKey);

  // Pre-flight: check SOL for tx fees
  const solBal = await conn.getBalance(wallet.publicKey);
  if (solBal < 5000) {
    console.error('❌ Not enough SOL for transaction fees.');
    console.error('   Run: node setup-wallet.js (for airdrop) or visit https://faucet.solana.com');
    process.exit(1);
  }

  // Pre-flight: check GEM balance
  try {
    const gemAccount = await getAccount(conn, playerGemAta);
    const gemBal = Number(gemAccount.amount) / 1e6;
    if (gemBal < betAmount) {
      console.error(`❌ Not enough GEM. Have ${gemBal}, need ${betAmount}.`);
      console.error('   Run: node mint-gems-sol.js <sol_amount>');
      process.exit(1);
    }
  } catch {
    console.error('❌ No GEM token account. Mint some first:');
    console.error('   node mint-gems-sol.js 0.01');
    process.exit(1);
  }

  const betBaseUnits = BigInt(Math.round(betAmount * 1e6));
  const choiceNum = choice === 'odd' ? 1 : 0;

  console.log(`Playing odd/even: ${choice}, bet ${betAmount} GEM...`);

  // Anchor discriminator for "play_odd_even"
  const crypto = require('crypto');
  const discriminator = crypto.createHash('sha256').update('global:play_odd_even').digest().slice(0, 8);
  const data = Buffer.alloc(17);
  discriminator.copy(data);
  data.writeBigUInt64LE(betBaseUnits, 8);
  data.writeUInt8(choiceNum, 16);

  const tx = new Transaction();
  tx.add(new TransactionInstruction({
    programId,
    keys: [
      { pubkey: wallet.publicKey, isSigner: true, isWritable: true },
      { pubkey: gameState, isSigner: false, isWritable: true },
      { pubkey: gemMint, isSigner: false, isWritable: true },
      { pubkey: playerGemAta, isSigner: false, isWritable: true },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
    ],
    data,
  }));

  const sig = await conn.sendTransaction(tx, [wallet]);
  await conn.confirmTransaction(sig, 'confirmed');

  // Check result from logs
  const txDetails = await conn.getTransaction(sig, { commitment: 'confirmed', maxSupportedTransactionVersion: 0 });
  let won = null;
  if (txDetails?.meta?.logMessages) {
    const logs = txDetails.meta.logMessages.join('\n');
    if (logs.includes('WON')) won = true;
    else if (logs.includes('LOST')) won = false;
  }

  if (won === true) console.log(`🎉 You WON! +${betAmount} GEM`);
  else if (won === false) console.log(`😢 You lost. -${betAmount} GEM`);
  else console.log(`⚡ TX: ${sig}`);

  console.log(`   Explorer: https://explorer.solana.com/tx/${sig}?cluster=devnet`);

  // Show updated balance
  try {
    const gemAccount = await getAccount(conn, playerGemAta);
    console.log(`   GEM balance: ${(Number(gemAccount.amount) / 1e6).toFixed(2)}`);
  } catch {}
}

main().catch(err => { console.error('❌', err.message); process.exit(1); });
