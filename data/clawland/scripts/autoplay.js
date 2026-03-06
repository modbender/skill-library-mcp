#!/usr/bin/env node
/**
 * Auto-play on-chain odd/even for multiple rounds.
 * Usage: node autoplay.js [--rounds N] [--bet N] [--strategy odd|even|alternate|random]
 * 
 * Examples:
 *   node autoplay.js                          # 5 rounds, 1 GEM, random
 *   node autoplay.js --rounds 10 --bet 2      # 10 rounds, 2 GEM, random
 *   node autoplay.js --rounds 20 --strategy alternate
 */
const { loadWallet, getConnection, getProgramId, getGameState, getGemMint, ensureDeps } = require('./common');

ensureDeps();

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = { rounds: 5, bet: 1, strategy: 'random' };
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace('--', '');
    const val = args[i + 1];
    if (key === 'rounds') opts.rounds = parseInt(val);
    else if (key === 'bet') opts.bet = parseFloat(val);
    else if (key === 'strategy') opts.strategy = val;
  }
  return opts;
}

function getChoice(strategy, round) {
  switch (strategy) {
    case 'odd': return 'odd';
    case 'even': return 'even';
    case 'alternate': return round % 2 === 0 ? 'even' : 'odd';
    case 'random': default: return Math.random() < 0.5 ? 'odd' : 'even';
  }
}

async function playOne(conn, wallet, programId, gameState, gemMint, playerGemAta, choice, betAmount) {
  const { Transaction, TransactionInstruction } = require('@solana/web3.js');
  const { TOKEN_PROGRAM_ID } = require('@solana/spl-token');
  const crypto = require('crypto');

  const betBaseUnits = BigInt(Math.round(betAmount * 1e6));
  const choiceNum = choice === 'odd' ? 1 : 0;

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

  // Parse result from logs
  let won = null;
  try {
    const txDetails = await conn.getTransaction(sig, { commitment: 'confirmed', maxSupportedTransactionVersion: 0 });
    if (txDetails?.meta?.logMessages) {
      const logs = txDetails.meta.logMessages.join('\n');
      if (logs.includes('WON')) won = true;
      else if (logs.includes('LOST')) won = false;
    }
  } catch {}
  return { sig, won };
}

async function main() {
  const opts = parseArgs();
  const { getAssociatedTokenAddress, getAccount } = require('@solana/spl-token');

  const wallet = loadWallet();
  const conn = getConnection();
  const programId = getProgramId();
  const gameState = getGameState();
  const gemMint = getGemMint();
  const playerGemAta = await getAssociatedTokenAddress(gemMint, wallet.publicKey);

  // Pre-flight
  const solBal = await conn.getBalance(wallet.publicKey);
  if (solBal < 5000 * opts.rounds) {
    console.error(`❌ Not enough SOL for ${opts.rounds} rounds of tx fees.`);
    process.exit(1);
  }
  try {
    const gemAccount = await getAccount(conn, playerGemAta);
    const gemBal = Number(gemAccount.amount) / 1e6;
    if (gemBal < opts.bet) {
      console.error(`❌ Not enough GEM. Have ${gemBal}, need at least ${opts.bet}.`);
      console.error('   Run: node mint-gems-sol.js 0.01');
      process.exit(1);
    }
  } catch {
    console.error('❌ No GEM. Run: node mint-gems-sol.js 0.01');
    process.exit(1);
  }

  console.log(`🎮 Autoplay: ${opts.rounds} rounds, ${opts.bet} GEM/bet, strategy: ${opts.strategy}`);
  console.log(`   Wallet: ${wallet.publicKey.toBase58()}\n`);

  let wins = 0, losses = 0, errors = 0;

  for (let i = 1; i <= opts.rounds; i++) {
    const choice = getChoice(opts.strategy, i);
    process.stdout.write(`Round ${i}/${opts.rounds}: ${choice} ${opts.bet} GEM... `);

    try {
      const result = await playOne(conn, wallet, programId, gameState, gemMint, playerGemAta, choice, opts.bet);
      if (result.won === true) { wins++; console.log('🎉 WIN'); }
      else if (result.won === false) { losses++; console.log('😢 LOSE'); }
      else { console.log(`⚡ TX: ${result.sig.slice(0, 20)}...`); }
    } catch (err) {
      errors++;
      console.log(`❌ ${err.message.slice(0, 80)}`);
    }

    // Small delay to respect rate limits
    if (i < opts.rounds) await new Promise(r => setTimeout(r, 1500));
  }

  console.log(`\n📊 Results: ${wins}W / ${losses}L / ${errors}E`);
  console.log(`   Net: ${(wins - losses) * opts.bet >= 0 ? '+' : ''}${(wins - losses) * opts.bet} GEM (approximate)`);

  // Show final balance
  try {
    const gemAccount = await getAccount(conn, playerGemAta);
    console.log(`   Balance: ${(Number(gemAccount.amount) / 1e6).toFixed(2)} GEM`);
  } catch {}
}

main().catch(err => { console.error('❌', err.message); process.exit(1); });
