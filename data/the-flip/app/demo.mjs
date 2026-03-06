/**
 * THE FLIP — Round-Based Game Demo & Operations Script
 *
 * Each round flips all 20 coins at once.
 * Pick 20 H/T predictions, first 14 must match to win the jackpot.
 * Enter anytime — anyone can join for the next round.
 *
 * Works with deployed program: 7rSMKhD3ve2NcR4qdYK5xcbMHfGtEjTgoKCS5Mgx9ECX
 *
 * Usage:
 *   node app/demo.mjs init                    Initialize game + vault
 *   node app/demo.mjs enter <20 H/T chars>    Enter with 20 H/T predictions
 *   node app/demo.mjs flip                    Flip all 20 coins for the round (permissionless)
 *   node app/demo.mjs claim <player> <round>  Claim jackpot (first 14 must match)
 *   node app/demo.mjs status                  Show game state
 *   node app/demo.mjs ticket <player> <round> Show a player's ticket
 *   node app/demo.mjs withdraw-fees [amount]  Withdraw operator fees
 *   node app/demo.mjs close-game-v1           Close old game PDA for migration
 */

import { Connection, Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import {
  getAssociatedTokenAddress,
  TOKEN_PROGRAM_ID
} from '@solana/spl-token';
import * as anchor from '@coral-xyz/anchor';
import fs from 'fs';
import path from 'path';

// --- Config ---
const DEVNET_URL = 'https://api.devnet.solana.com';
const USDC_MINT = new PublicKey('4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU');
const PROGRAM_ID = new PublicKey('7rSMKhD3ve2NcR4qdYK5xcbMHfGtEjTgoKCS5Mgx9ECX');
const PREDICTIONS_SIZE = 20;   // Players pick 20 H/T predictions
const SURVIVAL_FLIPS = 14;     // First 14 must match to win
const ROUNDS_BUFFER = 32;
const FLIP_COOLDOWN = 43_200;  // 12 hours in seconds

// Load IDL
const IDL_PATH = path.join(import.meta.dirname, '..', 'target', 'idl', 'the_flip.json');

// Load wallet
function loadWallet(keyPath) {
  const raw = JSON.parse(fs.readFileSync(keyPath || process.env.ANCHOR_WALLET ||
    path.join(process.env.HOME, '.config', 'solana', 'id.json'), 'utf8'));
  return Keypair.fromSecretKey(Uint8Array.from(raw));
}

// PDA derivation
function getGamePDA(authority) {
  return PublicKey.findProgramAddressSync(
    [Buffer.from('game'), authority.toBuffer()], PROGRAM_ID
  );
}

function getVaultPDA(authority) {
  return PublicKey.findProgramAddressSync(
    [Buffer.from('vault'), authority.toBuffer()], PROGRAM_ID
  );
}

function getTicketPDA(game, player, round) {
  const buf = Buffer.alloc(4);
  buf.writeUInt32LE(round);
  return PublicKey.findProgramAddressSync(
    [Buffer.from('ticket'), game.toBuffer(), player.toBuffer(), buf],
    PROGRAM_ID
  );
}

// Parse predictions string (HHTHTT...) to array of u8 (1=H, 2=T)
function parsePredictions(str) {
  if (str.length !== PREDICTIONS_SIZE) throw new Error('Must be exactly ' + PREDICTIONS_SIZE + ' predictions (H or T)');
  const result = [];
  for (let i = 0; i < PREDICTIONS_SIZE; i++) {
    const c = str[i].toUpperCase();
    if (c === 'H') result.push(1);
    else if (c === 'T') result.push(2);
    else throw new Error('Invalid char: ' + c + ' (must be H or T)');
  }
  return result;
}

// Format flip result (1=H, 2=T)
function flipToStr(r) { return r === 1 ? 'H' : r === 2 ? 'T' : '?'; }

// Format USDC amount (6 decimals)
function fmtUsdc(raw) {
  const n = typeof raw === 'number' ? raw : Number(raw.toString());
  return (n / 1_000_000).toFixed(6);
}

async function main() {
  const cmd = process.argv[2];
  if (!cmd) {
    console.log('Usage: node app/demo.mjs <command> [args]');
    console.log('Commands: init, enter, flip, claim, status, ticket, withdraw-fees, close-game-v1');
    process.exit(1);
  }

  const connection = new Connection(DEVNET_URL, 'confirmed');
  const wallet = loadWallet();
  const provider = new anchor.AnchorProvider(
    connection,
    new anchor.Wallet(wallet),
    { commitment: 'confirmed' }
  );
  anchor.setProvider(provider);

  if (!fs.existsSync(IDL_PATH)) {
    console.error('IDL not found at', IDL_PATH);
    console.error('Run anchor build first or copy the IDL.');
    process.exit(1);
  }
  const idl = JSON.parse(fs.readFileSync(IDL_PATH, 'utf8'));
  const program = new anchor.Program(idl, provider);

  const [gamePDA] = getGamePDA(wallet.publicKey);
  const [vaultPDA] = getVaultPDA(wallet.publicKey);

  switch (cmd) {
    case 'init': {
      console.log('Initializing THE FLIP (round-based game)...');
      console.log('  Authority:', wallet.publicKey.toBase58());
      console.log('  Game PDA: ', gamePDA.toBase58());
      console.log('  Vault PDA:', vaultPDA.toBase58());
      console.log('  Program:  ', PROGRAM_ID.toBase58());

      try {
        const tx = await program.methods.initializeGame().accounts({
          authority: wallet.publicKey,
          game: gamePDA,
          usdcMint: USDC_MINT,
          vault: vaultPDA,
          systemProgram: SystemProgram.programId,
          tokenProgram: TOKEN_PROGRAM_ID,
          rent: anchor.web3.SYSVAR_RENT_PUBKEY,
        }).rpc();
        console.log('Game initialized! TX:', tx);
      } catch (e) {
        if (e.message?.includes('already in use')) {
          console.log('Game already initialized.');
        } else {
          throw e;
        }
      }
      break;
    }

    case 'enter': {
      const preds = process.argv[3];
      const playerKeyPath = process.argv[4];
      if (!preds) { console.error('Usage: enter <HHTHTT...> [player_keypair_path]'); process.exit(1); }

      const parsed = parsePredictions(preds);
      const player = playerKeyPath ? loadWallet(playerKeyPath) : wallet;

      const playerProvider = new anchor.AnchorProvider(
        connection,
        new anchor.Wallet(player),
        { commitment: 'confirmed' }
      );
      const playerProgram = new anchor.Program(idl, playerProvider);

      const game = await program.account.game.fetch(gamePDA);
      const round = game.currentRound;
      const [ticketPDA] = getTicketPDA(gamePDA, player.publicKey, round);
      const playerATA = await getAssociatedTokenAddress(USDC_MINT, player.publicKey);

      console.log('Entering for round #' + round + ' with player ' + player.publicKey.toBase58());
      console.log('Predictions: ' + preds.toUpperCase() + ' (20 total, first 14 must match)');

      const tx = await playerProgram.methods.enter(parsed).accounts({
        player: player.publicKey,
        game: gamePDA,
        ticket: ticketPDA,
        playerTokenAccount: playerATA,
        vault: vaultPDA,
        systemProgram: SystemProgram.programId,
        tokenProgram: TOKEN_PROGRAM_ID,
      }).rpc();

      console.log('Entry accepted! TX:', tx);
      console.log('Ticket PDA:', ticketPDA.toBase58());
      break;
    }

    case 'flip': {
      // Check cooldown before attempting
      const gameBeforeFlip = await program.account.game.fetch(gamePDA);
      const now = Math.floor(Date.now() / 1000);
      const elapsed = now - Number(gameBeforeFlip.lastFlipAt.toString());
      if (elapsed < FLIP_COOLDOWN) {
        const remaining = FLIP_COOLDOWN - elapsed;
        const hours = Math.floor(remaining / 3600);
        const mins = Math.floor((remaining % 3600) / 60);
        console.log('Cooldown active — next flip available in ' + hours + 'h ' + mins + 'm');
        console.log('Last flip: ' + new Date(Number(gameBeforeFlip.lastFlipAt.toString()) * 1000).toISOString());
        break;
      }

      console.log('Flipping all 20 coins for current round...');
      const tx = await program.methods.flip().accounts({
        caller: wallet.publicKey,
        game: gamePDA,
      }).rpc();

      const game = await program.account.game.fetch(gamePDA);
      const roundNum = game.currentRound - 1; // flip increments, so the just-flipped round is currentRound-1
      const baseIdx = (roundNum % ROUNDS_BUFFER) * PREDICTIONS_SIZE;
      const results = [];
      for (let i = 0; i < PREDICTIONS_SIZE; i++) {
        results.push(flipToStr(game.roundResults[baseIdx + i]));
      }
      console.log('Round #' + roundNum + ' flipped! Results: ' + results.join(''));
      console.log('TX: ' + tx);
      break;
    }

    case 'claim': {
      const playerPubkey = process.argv[3];
      const roundArg = process.argv[4];
      if (!playerPubkey || !roundArg) {
        console.error('Usage: claim <player_pubkey> <round>');
        process.exit(1);
      }

      const player = new PublicKey(playerPubkey);
      const round = parseInt(roundArg);
      const [ticketPDA] = getTicketPDA(gamePDA, player, round);
      const playerATA = await getAssociatedTokenAddress(USDC_MINT, player);

      console.log('Claiming for player ' + playerPubkey + ' at round #' + round + '...');
      const tx = await program.methods.claim().accounts({
        claimer: wallet.publicKey,
        game: gamePDA,
        ticket: ticketPDA,
        player: player,
        playerTokenAccount: playerATA,
        vault: vaultPDA,
        tokenProgram: TOKEN_PROGRAM_ID,
      }).rpc();
      console.log('Claim TX:', tx);

      const game = await program.account.game.fetch(gamePDA);
      const ticket = await program.account.ticket.fetch(ticketPDA);
      if (ticket.winner) {
        console.log('WINNER! Jackpot collected. New jackpot:', fmtUsdc(game.jackpotPool), 'USDC');
      } else {
        console.log('Not a winner.');
      }
      break;
    }

    case 'status': {
      try {
        const game = await program.account.game.fetch(gamePDA);
        console.log('=== THE FLIP — Round-Based Game Status ===');
        console.log('Program:       ' + PROGRAM_ID.toBase58());
        console.log('Authority:     ' + game.authority.toBase58());
        console.log('Vault:         ' + game.vault.toBase58());
        console.log('');
        console.log('Current round: ' + game.currentRound);
        console.log('Total entries: ' + game.totalEntries);
        console.log('Total wins:    ' + game.totalWins);
        console.log('');
        console.log('Jackpot pool:  ' + fmtUsdc(game.jackpotPool) + ' USDC');
        console.log('Operator pool: ' + fmtUsdc(game.operatorPool) + ' USDC');
        console.log('');

        // Cooldown status
        const now = Math.floor(Date.now() / 1000);
        const lastFlip = Number(game.lastFlipAt.toString());
        const elapsed = now - lastFlip;
        if (lastFlip === 0) {
          console.log('Flip status:   Ready (never flipped)');
        } else if (elapsed >= FLIP_COOLDOWN) {
          console.log('Flip status:   Ready (cooldown elapsed)');
        } else {
          const remaining = FLIP_COOLDOWN - elapsed;
          const hours = Math.floor(remaining / 3600);
          const mins = Math.floor((remaining % 3600) / 60);
          console.log('Flip status:   Cooldown — ' + hours + 'h ' + mins + 'm remaining');
          console.log('Last flip:     ' + new Date(lastFlip * 1000).toISOString());
        }
        console.log('');

        // Show last round's results
        if (game.currentRound > 0) {
          const lastRound = game.currentRound - 1;
          const baseIdx = (lastRound % ROUNDS_BUFFER) * PREDICTIONS_SIZE;
          const results = [];
          for (let i = 0; i < PREDICTIONS_SIZE; i++) {
            results.push(flipToStr(game.roundResults[baseIdx + i]));
          }
          console.log('Last round #' + lastRound + ': ' + results.join(''));
          console.log('  Survival:    ' + results.slice(0, SURVIVAL_FLIPS).join('') + ' (first 14)');
          console.log('  Extra:       ' + results.slice(SURVIVAL_FLIPS).join('') + ' (15-20)');
        }
        console.log('='.repeat(44));
      } catch (e) {
        console.log('Game not initialized. Run: node app/demo.mjs init');
      }
      break;
    }

    case 'ticket': {
      const playerPubkey = process.argv[3];
      const roundArg = process.argv[4];
      if (!playerPubkey) { console.error('Usage: ticket <player_pubkey> [round]'); process.exit(1); }

      const player = new PublicKey(playerPubkey);
      const game = await program.account.game.fetch(gamePDA);

      // If round not provided, try to find it
      let round;
      if (roundArg) {
        round = parseInt(roundArg);
      } else {
        let found = false;
        for (let r = game.currentRound; r >= Math.max(0, game.currentRound - 20); r--) {
          try {
            const [pda] = getTicketPDA(gamePDA, player, r);
            await program.account.ticket.fetch(pda);
            round = r;
            found = true;
            break;
          } catch (e) { /* not found, try next */ }
        }
        if (!found) {
          console.log('No recent ticket found for this player. Try: ticket <player> <round>');
          break;
        }
      }

      const [ticketPDA] = getTicketPDA(gamePDA, player, round);

      try {
        const ticket = await program.account.ticket.fetch(ticketPDA);
        const allPredictions = ticket.predictions.map(p => p === 1 ? 'H' : 'T').join('');
        const survivalPredictions = allPredictions.slice(0, SURVIVAL_FLIPS);

        console.log('=== Ticket for ' + player.toBase58() + ' ===');
        console.log('Round:          #' + ticket.round);
        console.log('All predictions: ' + allPredictions + ' (20 total)');
        console.log('Survival check:  ' + survivalPredictions + ' (first 14 must match)');

        const flipped = game.currentRound > ticket.round;

        if (!flipped) {
          console.log('Status:         WAITING (round not yet flipped)');
        } else {
          // Get round results
          const baseIdx = (ticket.round % ROUNDS_BUFFER) * PREDICTIONS_SIZE;
          const results = [];
          for (let i = 0; i < PREDICTIONS_SIZE; i++) {
            results.push(game.roundResults[baseIdx + i]);
          }
          const resultsStr = results.map(flipToStr).join('');

          console.log('Round results:  ' + resultsStr);

          // Compare first 14
          let score = 0;
          let survived = true;
          const comparison = [];
          for (let i = 0; i < PREDICTIONS_SIZE; i++) {
            const predicted = flipToStr(ticket.predictions[i]);
            const actual = flipToStr(results[i]);
            const match = predicted === actual;
            if (i < SURVIVAL_FLIPS) {
              if (match) score++;
              else survived = false;
            }
            comparison.push((i + 1) + ':' + predicted + (match ? '=' : '≠') + actual);
          }

          if (ticket.winner && ticket.collected) {
            console.log('Status:         WINNER (collected)');
          } else if (ticket.winner) {
            console.log('Status:         WINNER');
          } else if (survived && score === SURVIVAL_FLIPS) {
            console.log('Status:         ALL 14 CORRECT — claim available!');
          } else {
            console.log('Status:         ELIMINATED (scored ' + score + '/' + SURVIVAL_FLIPS + ')');
          }

          console.log('');
          console.log('Comparison (all 20):');
          // Print 10 per line
          for (let i = 0; i < comparison.length; i += 10) {
            console.log('  ' + comparison.slice(i, i + 10).join('  '));
          }
        }
      } catch (e) {
        console.log('No ticket found for this player at round ' + round + '.');
      }
      break;
    }

    case 'withdraw-fees': {
      const game = await program.account.game.fetch(gamePDA);
      const amount = process.argv[3] ? parseInt(process.argv[3]) : Number(game.operatorPool.toString());
      if (amount <= 0) { console.log('No operator fees to withdraw.'); return; }

      const authorityATA = await getAssociatedTokenAddress(USDC_MINT, wallet.publicKey);
      console.log('Withdrawing ' + fmtUsdc(amount) + ' USDC in operator fees...');
      const tx = await program.methods.withdrawFees(new anchor.BN(amount)).accounts({
        authority: wallet.publicKey,
        game: gamePDA,
        authorityTokenAccount: authorityATA,
        vault: vaultPDA,
        tokenProgram: TOKEN_PROGRAM_ID,
      }).rpc();
      console.log('Fees withdrawn! TX:', tx);
      break;
    }

    case 'close-game-v1': {
      console.log('Closing old game PDA...');
      const tx = await program.methods.closeGameV1().accounts({
        authority: wallet.publicKey,
        game: gamePDA,
      }).rpc();
      console.log('Old game PDA closed! TX:', tx);
      break;
    }

    default:
      console.error('Unknown command:', cmd);
      console.log('Commands: init, enter, flip, claim, status, ticket, withdraw-fees, close-game-v1');
      process.exit(1);
  }
}

main().catch(e => {
  console.error('Error:', e.message || e);
  process.exit(1);
});
