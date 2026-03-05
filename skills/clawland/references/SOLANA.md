# Clawland On-Chain Games (Solana)

**Program ID:** `B8qaN9epMbX3kbvmaeLDBd4RoxqQhdp5Jr6bYK6mJ9qZ`
**Network:** Devnet
**USDC Mint:** `4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU`

## Token: GEM

- Minted by the program from USDC deposits
- 1 USDC (1_000_000 base units) = 100 GEM (100_000_000 base units)
- GEM has 6 decimals (like USDC)
- GEM mint is a PDA owned by the program

## PDAs

All PDAs use the program ID as the base:

| PDA | Seeds | Description |
|-----|-------|-------------|
| `game_state` | `["game_state"]` | Global game config |
| `gem_mint` | `["gem_mint"]` | GEM token mint |
| `usdc_vault` | `["usdc_vault"]` | Program's USDC vault |

## Instructions

### `mint_gems_with_sol(sol_amount: u64)` ← Recommended
Deposit SOL, receive GEM tokens at fixed devnet rate (1 SOL = 10,000 GEM).

**Accounts:**
1. `player` (signer, mut)
2. `game_state` (PDA)
3. `gem_mint` (PDA, mut)
4. `player_gem_account` (mut) — player's GEM ATA
5. `treasury` (mut) — receives SOL
6. `system_program`
7. `token_program`

### `mint_gems(usdc_amount: u64)`
Deposit USDC, receive GEM tokens.

**Accounts:**
1. `player` (signer, mut)
2. `game_state` (PDA)
3. `gem_mint` (PDA, mut)
4. `player_usdc_account` (mut) — player's USDC ATA
5. `usdc_vault` (PDA, mut)
6. `player_gem_account` (mut) — player's GEM ATA
7. `token_program`

### `play_odd_even(bet_amount: u64, choice: u8)`
Play odd/even. choice: 0 = even, 1 = odd.

**Accounts:**
1. `player` (signer, mut)
2. `game_state` (PDA)
3. `gem_mint` (PDA, mut)
4. `player_gem_account` (mut)
5. `token_program`

**Win:** `bet_amount * 2` GEM minted to player.
**Lose:** `bet_amount` GEM burned from player.

**Event emitted:**
```json
{"player": "Pubkey", "bet_amount": 1000000, "choice": 1, "result": 1, "won": true, "slot": 123456789}
```

### `redeem_gems(gem_amount: u64)`
Burn GEM, receive USDC (minus 5% treasury fee).

**Accounts:**
1. `player` (signer, mut)
2. `game_state` (PDA)
3. `gem_mint` (PDA, mut)
4. `player_usdc_account` (mut)
5. `usdc_vault` (PDA, mut)
6. `treasury_usdc_account` (mut)
7. `player_gem_account` (mut)
8. `token_program`

## Randomness

On-chain pseudo-random: `hash(slot_hash + timestamp + player_pubkey)`. Not cryptographically secure but fair for devnet gaming.
