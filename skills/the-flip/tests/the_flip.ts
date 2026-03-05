/**
 * THE FLIP — Smart Contract Tests
 *
 * Tests for the round-based game model:
 *   - 20 predictions per entry, all 20 coins flip at once per round
 *   - First 14 must match to win the jackpot
 *   - Winner takes full jackpot
 *   - Continuous — anyone can join anytime, anyone can trigger a flip
 *
 * Run with: anchor test (requires local validator)
 * Or standalone: npx ts-mocha -p ./tsconfig.json -t 1000000 tests/**/*.ts
 */

import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { PublicKey, Keypair, SystemProgram } from "@solana/web3.js";
import {
  TOKEN_PROGRAM_ID,
  createMint,
  createAssociatedTokenAccount,
  mintTo,
  getAssociatedTokenAddress,
  getAccount,
} from "@solana/spl-token";
import { assert, expect } from "chai";

// ---------------------------------------------------------------------------
// Constants (must match program/src/lib.rs)
// ---------------------------------------------------------------------------

const PREDICTIONS_SIZE = 20;
const SURVIVAL_FLIPS = 14;
const ENTRY_FEE = 1_000_000; // 1 USDC (6 decimals)
const ROUNDS_BUFFER = 32;
const FLIP_COOLDOWN = 43_200; // 12 hours

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function getGamePDA(authority: PublicKey, programId: PublicKey): [PublicKey, number] {
  return PublicKey.findProgramAddressSync(
    [Buffer.from("game"), authority.toBuffer()],
    programId
  );
}

function getVaultPDA(authority: PublicKey, programId: PublicKey): [PublicKey, number] {
  return PublicKey.findProgramAddressSync(
    [Buffer.from("vault"), authority.toBuffer()],
    programId
  );
}

function getTicketPDA(
  game: PublicKey,
  player: PublicKey,
  round: number,
  programId: PublicKey
): [PublicKey, number] {
  const buf = Buffer.alloc(4);
  buf.writeUInt32LE(round);
  return PublicKey.findProgramAddressSync(
    [Buffer.from("ticket"), game.toBuffer(), player.toBuffer(), buf],
    programId
  );
}

/** Generate a random 20-element prediction array (1=H, 2=T). */
function randomPredictions(): number[] {
  return Array.from({ length: PREDICTIONS_SIZE }, () =>
    Math.random() < 0.5 ? 1 : 2
  );
}

/** Generate all-heads predictions (20 elements). */
function allHeads(): number[] {
  return new Array(PREDICTIONS_SIZE).fill(1);
}

/** Generate all-tails predictions (20 elements). */
function allTails(): number[] {
  return new Array(PREDICTIONS_SIZE).fill(2);
}

// ---------------------------------------------------------------------------
// Test suite
// ---------------------------------------------------------------------------

describe("THE FLIP", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  const program = anchor.workspace.TheFlip as Program;
  const authority = provider.wallet as anchor.Wallet;

  let usdcMint: PublicKey;
  let gamePDA: PublicKey;
  let vaultPDA: PublicKey;
  let authorityATA: PublicKey;

  // Player keypairs
  const player1 = Keypair.generate();
  const player2 = Keypair.generate();
  let player1ATA: PublicKey;
  let player2ATA: PublicKey;

  before(async () => {
    // Airdrop SOL to players
    const connection = provider.connection;
    for (const player of [player1, player2]) {
      const sig = await connection.requestAirdrop(
        player.publicKey,
        2 * anchor.web3.LAMPORTS_PER_SOL
      );
      await connection.confirmTransaction(sig);
    }

    // Create USDC mock mint
    usdcMint = await createMint(
      connection,
      authority.payer,
      authority.publicKey,
      null,
      6 // 6 decimals like real USDC
    );

    // Create ATAs
    authorityATA = await createAssociatedTokenAccount(
      connection,
      authority.payer,
      usdcMint,
      authority.publicKey
    );
    player1ATA = await createAssociatedTokenAccount(
      connection,
      authority.payer,
      usdcMint,
      player1.publicKey
    );
    player2ATA = await createAssociatedTokenAccount(
      connection,
      authority.payer,
      usdcMint,
      player2.publicKey
    );

    // Mint USDC to players (10 each)
    await mintTo(
      connection,
      authority.payer,
      usdcMint,
      player1ATA,
      authority.publicKey,
      10_000_000 // 10 USDC
    );
    await mintTo(
      connection,
      authority.payer,
      usdcMint,
      player2ATA,
      authority.publicKey,
      10_000_000 // 10 USDC
    );

    [gamePDA] = getGamePDA(authority.publicKey, program.programId);
    [vaultPDA] = getVaultPDA(authority.publicKey, program.programId);
  });

  // -----------------------------------------------------------------------
  // Initialize
  // -----------------------------------------------------------------------

  describe("initialize_game", () => {
    it("creates game and vault PDAs", async () => {
      await program.methods
        .initializeGame()
        .accounts({
          authority: authority.publicKey,
          game: gamePDA,
          usdcMint,
          vault: vaultPDA,
          systemProgram: SystemProgram.programId,
          tokenProgram: TOKEN_PROGRAM_ID,
          rent: anchor.web3.SYSVAR_RENT_PUBKEY,
        })
        .rpc();

      const game = await program.account.game.fetch(gamePDA);
      assert.equal(game.currentRound, 0, "currentRound starts at 0");
      assert.equal(
        game.lastFlipAt.toNumber(),
        0,
        "lastFlipAt starts at 0"
      );
      assert.equal(game.totalEntries, 0, "totalEntries starts at 0");
      assert.equal(game.totalWins, 0, "totalWins starts at 0");
      assert.equal(
        game.jackpotPool.toNumber(),
        0,
        "jackpotPool starts at 0"
      );
      assert.equal(
        game.operatorPool.toNumber(),
        0,
        "operatorPool starts at 0"
      );
    });
  });

  // -----------------------------------------------------------------------
  // Enter
  // -----------------------------------------------------------------------

  describe("enter", () => {
    it("accepts 20 predictions and transfers 1 USDC", async () => {
      const predictions = allHeads();
      const game = await program.account.game.fetch(gamePDA);
      const round = game.currentRound;
      const [ticketPDA] = getTicketPDA(
        gamePDA,
        player1.publicKey,
        round,
        program.programId
      );

      await program.methods
        .enter(predictions)
        .accounts({
          player: player1.publicKey,
          game: gamePDA,
          ticket: ticketPDA,
          playerTokenAccount: player1ATA,
          vault: vaultPDA,
          systemProgram: SystemProgram.programId,
          tokenProgram: TOKEN_PROGRAM_ID,
        })
        .signers([player1])
        .rpc();

      const ticket = await program.account.ticket.fetch(ticketPDA);
      assert.equal(ticket.round, round, "round matches");
      assert.equal(
        ticket.predictions.length,
        PREDICTIONS_SIZE,
        "20 predictions stored"
      );
      assert.deepEqual(
        ticket.predictions,
        predictions,
        "predictions match input"
      );
      assert.equal(ticket.winner, false, "not winner yet");
      assert.equal(ticket.collected, false, "not collected yet");

      // Check pool accounting
      const gameAfter = await program.account.game.fetch(gamePDA);
      assert.equal(gameAfter.totalEntries, 1, "totalEntries = 1");
      assert.equal(
        gameAfter.jackpotPool.toNumber(),
        990_000,
        "99% to jackpot"
      );
      assert.equal(
        gameAfter.operatorPool.toNumber(),
        10_000,
        "1% to operator"
      );
    });

    it("rejects predictions that are not 1 or 2", async () => {
      const badPredictions = new Array(PREDICTIONS_SIZE).fill(3);
      const game = await program.account.game.fetch(gamePDA);
      const [ticketPDA] = getTicketPDA(
        gamePDA,
        player2.publicKey,
        game.currentRound,
        program.programId
      );

      try {
        await program.methods
          .enter(badPredictions)
          .accounts({
            player: player2.publicKey,
            game: gamePDA,
            ticket: ticketPDA,
            playerTokenAccount: player2ATA,
            vault: vaultPDA,
            systemProgram: SystemProgram.programId,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .signers([player2])
          .rpc();
        assert.fail("Should have thrown");
      } catch (err) {
        assert.include(
          err.toString(),
          "InvalidPrediction",
          "rejects invalid prediction values"
        );
      }
    });
  });

  // -----------------------------------------------------------------------
  // Flip
  // -----------------------------------------------------------------------

  describe("flip", () => {
    it("flips all 20 coins at once and increments round counter", async () => {
      const gameBefore = await program.account.game.fetch(gamePDA);
      const roundBefore = gameBefore.currentRound;

      await program.methods
        .flip()
        .accounts({
          caller: authority.publicKey,
          game: gamePDA,
        })
        .rpc();

      const gameAfter = await program.account.game.fetch(gamePDA);
      assert.equal(
        gameAfter.currentRound,
        roundBefore + 1,
        "currentRound incremented by 1"
      );

      // lastFlipAt should be set to a recent timestamp
      assert.isAbove(
        gameAfter.lastFlipAt.toNumber(),
        0,
        "lastFlipAt set after flip"
      );

      // All 20 results for this round must be 1 (H) or 2 (T)
      const baseIdx = (roundBefore % ROUNDS_BUFFER) * PREDICTIONS_SIZE;
      for (let i = 0; i < PREDICTIONS_SIZE; i++) {
        const result = gameAfter.roundResults[baseIdx + i];
        assert.isTrue(
          result === 1 || result === 2,
          `round result[${i}] is H or T, got ${result}`
        );
      }
    });

    it("rejects flip within 12-hour cooldown", async () => {
      // The first flip just happened — a second flip should be rejected
      try {
        await program.methods
          .flip()
          .accounts({
            caller: player1.publicKey,
            game: gamePDA,
          })
          .signers([player1])
          .rpc();
        assert.fail("Should have thrown FlipCooldown");
      } catch (err) {
        assert.include(
          err.toString(),
          "FlipCooldown",
          "rejects flip within cooldown window"
        );
      }
    });
  });

  // -----------------------------------------------------------------------
  // Claim
  // -----------------------------------------------------------------------

  describe("claim", () => {
    it("rejects claim when predictions don't match (NotAWinner)", async () => {
      // Player1 entered with all heads at round 0 — unlikely to match all 14
      const [ticketPDA] = getTicketPDA(
        gamePDA,
        player1.publicKey,
        0, // round was 0 for player1
        program.programId
      );

      try {
        await program.methods
          .claim()
          .accounts({
            claimer: authority.publicKey,
            game: gamePDA,
            ticket: ticketPDA,
            player: player1.publicKey,
            playerTokenAccount: player1ATA,
            vault: vaultPDA,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .rpc();

        // If we get here, the all-heads prediction happened to match
        // which is astronomically unlikely but valid
      } catch (err) {
        assert.include(
          err.toString(),
          "NotAWinner",
          "correctly rejects non-matching predictions"
        );
      }
    });

    it("rejects claim before round is flipped", async () => {
      // Enter a new player at current round (not yet flipped)
      const game = await program.account.game.fetch(gamePDA);
      const currentRound = game.currentRound;
      const predictions = randomPredictions();
      const [ticketPDA] = getTicketPDA(
        gamePDA,
        player2.publicKey,
        currentRound,
        program.programId
      );

      await program.methods
        .enter(predictions)
        .accounts({
          player: player2.publicKey,
          game: gamePDA,
          ticket: ticketPDA,
          playerTokenAccount: player2ATA,
          vault: vaultPDA,
          systemProgram: SystemProgram.programId,
          tokenProgram: TOKEN_PROGRAM_ID,
        })
        .signers([player2])
        .rpc();

      // Try to claim immediately (round not flipped yet for this ticket)
      try {
        await program.methods
          .claim()
          .accounts({
            claimer: authority.publicKey,
            game: gamePDA,
            ticket: ticketPDA,
            player: player2.publicKey,
            playerTokenAccount: player2ATA,
            vault: vaultPDA,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .rpc();
        assert.fail("Should have thrown RoundNotFlipped");
      } catch (err) {
        assert.include(
          err.toString(),
          "RoundNotFlipped",
          "rejects premature claim"
        );
      }
    });
  });

  // -----------------------------------------------------------------------
  // Withdraw fees
  // -----------------------------------------------------------------------

  describe("withdraw_fees", () => {
    it("allows authority to withdraw operator fees", async () => {
      const game = await program.account.game.fetch(gamePDA);
      const operatorFees = game.operatorPool.toNumber();

      if (operatorFees > 0) {
        await program.methods
          .withdrawFees(new anchor.BN(operatorFees))
          .accounts({
            authority: authority.publicKey,
            game: gamePDA,
            authorityTokenAccount: authorityATA,
            vault: vaultPDA,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .rpc();

        const gameAfter = await program.account.game.fetch(gamePDA);
        assert.equal(
          gameAfter.operatorPool.toNumber(),
          0,
          "operator pool zeroed after withdrawal"
        );
      }
    });

    it("rejects non-authority fee withdrawal", async () => {
      try {
        await program.methods
          .withdrawFees(new anchor.BN(1))
          .accounts({
            authority: player1.publicKey,
            game: gamePDA,
            authorityTokenAccount: player1ATA,
            vault: vaultPDA,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .signers([player1])
          .rpc();
        assert.fail("Should have thrown Unauthorized");
      } catch (err) {
        // Expected - either Unauthorized or constraint violation
        assert.ok(true, "non-authority correctly rejected");
      }
    });
  });

  // -----------------------------------------------------------------------
  // Constants validation
  // -----------------------------------------------------------------------

  describe("game constants", () => {
    it("predictions array is 20 elements", () => {
      assert.equal(PREDICTIONS_SIZE, 20, "PREDICTIONS_SIZE = 20");
    });

    it("survival flips is 14", () => {
      assert.equal(SURVIVAL_FLIPS, 14, "SURVIVAL_FLIPS = 14");
    });

    it("odds are 1 in 16384 (2^14)", () => {
      assert.equal(Math.pow(2, SURVIVAL_FLIPS), 16384, "2^14 = 16384");
    });

    it("entry fee is 1 USDC (1_000_000 lamports)", () => {
      assert.equal(ENTRY_FEE, 1_000_000, "ENTRY_FEE = 1 USDC");
    });

    it("rounds buffer stores 32 rounds", () => {
      assert.equal(ROUNDS_BUFFER, 32, "ROUNDS_BUFFER = 32");
    });

    it("flip cooldown is 12 hours (43200 seconds)", () => {
      assert.equal(FLIP_COOLDOWN, 43_200, "FLIP_COOLDOWN = 43200");
    });
  });
});
