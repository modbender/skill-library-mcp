use anchor_lang::prelude::*;
use solana_sha256_hasher::hash;
use anchor_spl::token::{self, Mint, Token, TokenAccount, Transfer};

declare_id!("7rSMKhD3ve2NcR4qdYK5xcbMHfGtEjTgoKCS5Mgx9ECX");

// Game constants
const ENTRY_FEE: u64 = 1_000_000; // 1 USDC (6 decimals)
const PREDICTIONS_SIZE: usize = 20; // Players pick 20 H/T
const SURVIVAL_FLIPS: usize = 14; // First 14 must match to win
const OPERATOR_FEE_BPS: u64 = 100; // 1% to operator
const BPS_BASE: u64 = 10000;
const ROUNDS_BUFFER: usize = 32; // Store last 32 rounds of results
const FLIP_COOLDOWN: i64 = 43_200; // 12 hours in seconds
// Jackpot gets the rest: 99%

#[program]
pub mod the_flip {
    use super::*;

    /// Initialize a new game. Creates the game state PDA and the USDC vault.
    pub fn initialize_game(ctx: Context<InitializeGame>) -> Result<()> {
        let game = &mut ctx.accounts.game;
        game.authority = ctx.accounts.authority.key();
        game.usdc_mint = ctx.accounts.usdc_mint.key();
        game.vault = ctx.accounts.vault.key();
        game.bump = ctx.bumps.game;
        game.vault_bump = ctx.bumps.vault;
        game.current_round = 0;
        game.round_results = [0u8; ROUNDS_BUFFER * PREDICTIONS_SIZE];
        game.jackpot_pool = 0;
        game.operator_pool = 0;
        game.total_entries = 0;
        game.total_wins = 0;
        game.last_flip_at = 0;

        msg!("THE FLIP initialized. Vault: {}", game.vault);
        Ok(())
    }

    /// Player enters the game. Transfers 1 USDC to the vault and creates a ticket PDA.
    /// Always open — enter anytime, pick 20 predictions.
    /// When the next flip happens, all 20 coins are flipped at once.
    /// First 14 of your predictions must match the first 14 results to win.
    pub fn enter(ctx: Context<Enter>, predictions: [u8; PREDICTIONS_SIZE]) -> Result<()> {
        let game = &mut ctx.accounts.game;

        // Validate predictions: each byte must be 1 (H) or 2 (T)
        for &p in predictions.iter() {
            require!(p == 1 || p == 2, FlipError::InvalidPrediction);
        }

        // Transfer 1 USDC from player to vault
        let cpi_ctx = CpiContext::new(
            ctx.accounts.token_program.to_account_info(),
            Transfer {
                from: ctx.accounts.player_token_account.to_account_info(),
                to: ctx.accounts.vault.to_account_info(),
                authority: ctx.accounts.player.to_account_info(),
            },
        );
        token::transfer(cpi_ctx, ENTRY_FEE)?;

        // Split into pools: 1% operator, 99% jackpot
        let operator_amount = ENTRY_FEE * OPERATOR_FEE_BPS / BPS_BASE;
        let jackpot_amount = ENTRY_FEE - operator_amount;
        game.operator_pool += operator_amount;
        game.jackpot_pool += jackpot_amount;
        game.total_entries += 1;

        // Initialize ticket — enters for the NEXT round to be flipped
        let ticket = &mut ctx.accounts.ticket;
        ticket.game = game.key();
        ticket.player = ctx.accounts.player.key();
        ticket.round = game.current_round;
        ticket.predictions = predictions;
        ticket.winner = false;
        ticket.collected = false;
        ticket.bump = ctx.bumps.ticket;

        msg!(
            "Player {} entered for round #{}. Total entries: {}",
            ctx.accounts.player.key(),
            game.current_round,
            game.total_entries
        );
        Ok(())
    }

    /// Flip all 20 coins at once for the current round. Permissionless — anyone can call.
    /// Generates 20 H/T results using on-chain entropy and increments the round counter.
    pub fn flip(ctx: Context<FlipCtx>) -> Result<()> {
        let game = &mut ctx.accounts.game;
        let clock = Clock::get()?;

        // Enforce 12-hour cooldown between flips
        require!(
            clock.unix_timestamp - game.last_flip_at >= FLIP_COOLDOWN,
            FlipError::FlipCooldown
        );

        // Build entropy from multiple sources
        let mut seed_data = [0u8; 52];
        seed_data[0..4].copy_from_slice(&game.current_round.to_le_bytes());
        seed_data[4..12].copy_from_slice(&clock.slot.to_le_bytes());
        seed_data[12..20].copy_from_slice(&clock.unix_timestamp.to_le_bytes());
        seed_data[20..52].copy_from_slice(game.key().as_ref());

        let hash_result = hash(&seed_data);
        let hash_bytes = hash_result.to_bytes(); // 32 bytes = 256 bits

        // Store 20 results for this round (use 20 bits from the hash)
        let base_idx = (game.current_round as usize % ROUNDS_BUFFER) * PREDICTIONS_SIZE;
        for i in 0..PREDICTIONS_SIZE {
            let byte_idx = i / 8;
            let bit_idx = i % 8;
            let bit = (hash_bytes[byte_idx] >> bit_idx) & 1;
            game.round_results[base_idx + i] = if bit == 0 { 1 } else { 2 };
        }

        game.last_flip_at = clock.unix_timestamp;
        game.current_round += 1;

        msg!("Round #{} flipped! 20 coins revealed.", game.current_round);
        Ok(())
    }

    /// Verify first 14 predictions match the round results and pay the entire jackpot.
    pub fn claim(ctx: Context<Claim>) -> Result<()> {
        let game = &mut ctx.accounts.game;
        let ticket = &mut ctx.accounts.ticket;

        // Round must have been flipped
        require!(
            game.current_round > ticket.round,
            FlipError::RoundNotFlipped
        );

        // Must be within buffer window (last 32 rounds)
        require!(
            game.current_round - ticket.round <= ROUNDS_BUFFER as u32,
            FlipError::BufferExpired
        );

        require!(!ticket.collected, FlipError::AlreadyCollected);

        // Verify first 14 predictions match round results
        let base_idx = (ticket.round as usize % ROUNDS_BUFFER) * PREDICTIONS_SIZE;
        for i in 0..SURVIVAL_FLIPS {
            require!(
                ticket.predictions[i] == game.round_results[base_idx + i],
                FlipError::NotAWinner
            );
        }

        ticket.winner = true;
        ticket.collected = true;
        game.total_wins += 1;

        // Winner takes the entire jackpot
        let payout = game.jackpot_pool;

        // PDA signer seeds for vault
        let authority_key = game.authority;
        let seeds = &[
            b"vault" as &[u8],
            authority_key.as_ref(),
            &[game.vault_bump],
        ];
        let signer_seeds = &[&seeds[..]];

        let cpi_ctx = CpiContext::new_with_signer(
            ctx.accounts.token_program.to_account_info(),
            Transfer {
                from: ctx.accounts.vault.to_account_info(),
                to: ctx.accounts.player_token_account.to_account_info(),
                authority: ctx.accounts.vault.to_account_info(),
            },
            signer_seeds,
        );
        token::transfer(cpi_ctx, payout)?;

        game.jackpot_pool = 0;

        msg!(
            "WINNER! {} claimed {} USDC at round #{} (win #{})",
            ticket.player,
            payout,
            ticket.round,
            game.total_wins
        );
        Ok(())
    }

    /// Authority withdraws accumulated operator fees from the vault.
    pub fn withdraw_fees(ctx: Context<WithdrawFees>, amount: u64) -> Result<()> {
        let game = &mut ctx.accounts.game;

        require!(amount <= game.operator_pool, FlipError::InsufficientFees);

        let authority_key = game.authority;
        let seeds = &[
            b"vault" as &[u8],
            authority_key.as_ref(),
            &[game.vault_bump],
        ];
        let signer_seeds = &[&seeds[..]];

        let cpi_ctx = CpiContext::new_with_signer(
            ctx.accounts.token_program.to_account_info(),
            Transfer {
                from: ctx.accounts.vault.to_account_info(),
                to: ctx.accounts.authority_token_account.to_account_info(),
                authority: ctx.accounts.vault.to_account_info(),
            },
            signer_seeds,
        );
        token::transfer(cpi_ctx, amount)?;

        game.operator_pool -= amount;
        msg!("Withdrew {} USDC units in operator fees", amount);
        Ok(())
    }

    /// Close old game PDA for migration. Authority only.
    pub fn close_game_v1(ctx: Context<CloseGameV1>) -> Result<()> {
        let game_info = ctx.accounts.game.to_account_info();
        let authority_info = ctx.accounts.authority.to_account_info();

        // Return lamports to authority
        let lamports = game_info.lamports();
        **game_info.try_borrow_mut_lamports()? = 0;
        **authority_info.try_borrow_mut_lamports()? += lamports;

        // Zero out data
        let mut data = game_info.try_borrow_mut_data()?;
        for byte in data.iter_mut() {
            *byte = 0;
        }

        msg!("Old game PDA closed.");
        Ok(())
    }
}

// ─── Account Contexts ───────────────────────────────────────────────────────

#[derive(Accounts)]
pub struct InitializeGame<'info> {
    #[account(mut)]
    pub authority: Signer<'info>,

    #[account(
        init,
        payer = authority,
        space = 8 + Game::INIT_SPACE,
        seeds = [b"game", authority.key().as_ref()],
        bump,
    )]
    pub game: Account<'info, Game>,

    pub usdc_mint: Account<'info, Mint>,

    #[account(
        init_if_needed,
        payer = authority,
        token::mint = usdc_mint,
        token::authority = vault,
        seeds = [b"vault", authority.key().as_ref()],
        bump,
    )]
    pub vault: Account<'info, TokenAccount>,

    pub system_program: Program<'info, System>,
    pub token_program: Program<'info, Token>,
    pub rent: Sysvar<'info, Rent>,
}

#[derive(Accounts)]
pub struct Enter<'info> {
    #[account(mut)]
    pub player: Signer<'info>,

    #[account(
        mut,
        seeds = [b"game", game.authority.as_ref()],
        bump = game.bump,
    )]
    pub game: Box<Account<'info, Game>>,

    #[account(
        init,
        payer = player,
        space = 8 + Ticket::INIT_SPACE,
        seeds = [b"ticket", game.key().as_ref(), player.key().as_ref(), &game.current_round.to_le_bytes()],
        bump,
    )]
    pub ticket: Account<'info, Ticket>,

    #[account(
        mut,
        constraint = player_token_account.owner == player.key(),
        constraint = player_token_account.mint == game.usdc_mint,
    )]
    pub player_token_account: Account<'info, TokenAccount>,

    #[account(
        mut,
        address = game.vault,
    )]
    pub vault: Account<'info, TokenAccount>,

    pub system_program: Program<'info, System>,
    pub token_program: Program<'info, Token>,
}

/// Permissionless — anyone can execute the next round's flip.
#[derive(Accounts)]
pub struct FlipCtx<'info> {
    pub caller: Signer<'info>,

    #[account(
        mut,
        seeds = [b"game", game.authority.as_ref()],
        bump = game.bump,
    )]
    pub game: Account<'info, Game>,
}

#[derive(Accounts)]
pub struct Claim<'info> {
    pub claimer: Signer<'info>,

    #[account(
        mut,
        seeds = [b"game", game.authority.as_ref()],
        bump = game.bump,
    )]
    pub game: Box<Account<'info, Game>>,

    #[account(
        mut,
        constraint = ticket.game == game.key() @ FlipError::TicketGameMismatch,
        constraint = ticket.player == player.key() @ FlipError::PlayerMismatch,
    )]
    pub ticket: Account<'info, Ticket>,

    /// CHECK: Verified via ticket.player constraint
    pub player: UncheckedAccount<'info>,

    #[account(
        mut,
        constraint = player_token_account.owner == player.key(),
        constraint = player_token_account.mint == game.usdc_mint,
    )]
    pub player_token_account: Account<'info, TokenAccount>,

    #[account(
        mut,
        address = game.vault,
    )]
    pub vault: Account<'info, TokenAccount>,

    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct WithdrawFees<'info> {
    #[account(
        constraint = authority.key() == game.authority @ FlipError::Unauthorized,
    )]
    pub authority: Signer<'info>,

    #[account(
        mut,
        seeds = [b"game", game.authority.as_ref()],
        bump = game.bump,
    )]
    pub game: Account<'info, Game>,

    #[account(
        mut,
        constraint = authority_token_account.owner == authority.key(),
        constraint = authority_token_account.mint == game.usdc_mint,
    )]
    pub authority_token_account: Account<'info, TokenAccount>,

    #[account(
        mut,
        address = game.vault,
    )]
    pub vault: Account<'info, TokenAccount>,

    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct CloseGameV1<'info> {
    #[account(mut)]
    pub authority: Signer<'info>,

    /// CHECK: Old game PDA being closed. Verified by seeds.
    #[account(
        mut,
        seeds = [b"game", authority.key().as_ref()],
        bump,
    )]
    pub game: UncheckedAccount<'info>,
}

// ─── State ──────────────────────────────────────────────────────────────────

#[account]
#[derive(InitSpace)]
pub struct Game {
    pub authority: Pubkey,           // 32
    pub usdc_mint: Pubkey,           // 32
    pub vault: Pubkey,               // 32
    pub bump: u8,                    // 1
    pub vault_bump: u8,              // 1
    pub current_round: u32,          // 4  — rounds completed (each round = 20 flips at once)
    pub round_results: [u8; 640],    // 640 — 32 rounds × 20 results (circular buffer)
    pub jackpot_pool: u64,           // 8
    pub operator_pool: u64,          // 8
    pub total_entries: u32,          // 4
    pub total_wins: u32,             // 4  — lifetime winners
    pub last_flip_at: i64,           // 8  — unix timestamp of last flip (12h cooldown)
}

#[account]
#[derive(InitSpace)]
pub struct Ticket {
    pub game: Pubkey,                // 32
    pub player: Pubkey,              // 32
    pub round: u32,                  // 4  — which round this ticket is for
    pub predictions: [u8; 20],       // 20 — player picks 20 H/T, first 14 must match to survive
    pub winner: bool,                // 1
    pub collected: bool,             // 1
    pub bump: u8,                    // 1
}

// ─── Errors ─────────────────────────────────────────────────────────────────

#[error_code]
pub enum FlipError {
    #[msg("Invalid prediction: must be 1 (H) or 2 (T)")]
    InvalidPrediction,
    #[msg("Did not survive 14 flips")]
    NotAWinner,
    #[msg("Already collected payout")]
    AlreadyCollected,
    #[msg("Unauthorized")]
    Unauthorized,
    #[msg("Ticket/game mismatch")]
    TicketGameMismatch,
    #[msg("Player mismatch")]
    PlayerMismatch,
    #[msg("Insufficient operator fees")]
    InsufficientFees,
    #[msg("Round has not been flipped yet")]
    RoundNotFlipped,
    #[msg("Ticket expired — results overwritten (claim within 32 rounds)")]
    BufferExpired,
    #[msg("Flip cooldown — wait 12 hours between rounds")]
    FlipCooldown,
}
