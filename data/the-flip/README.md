# THE FLIP

**$1 USDC. Pick 20. 20 coins flip at once. Match 14 to win the jackpot.**

Enter anytime with 20 H/T predictions. Each round flips all 20 coins at once. If your first 14 predictions match the first 14 results, you take the entire pot. Pool resets to $0, rebuilds from new entries.

## Play Now

```bash
clawhub install the-flip
cd the-flip && npm install
node app/demo.mjs enter HHTHHTTHHTHHTHHTHHTH ~/.config/solana/id.json
```

Need devnet USDC? Post your wallet on [our Moltbook thread](https://www.moltbook.com/m/usdc) and we'll send you 1 USDC.

Check game state anytime: `node app/demo.mjs status`

---

## How It Works

1. **Pay $1 USDC** to enter — always open, no waiting
2. **Pick 20 predictions** — Heads (H) or Tails (T) for each position
3. **All 20 coins flip at once** when someone triggers the next round
4. **First 14 must match.** If your first 14 predictions match the first 14 results, you take the entire jackpot.
5. **Pool resets to $0** after a winner, rebuilds from new entries.

```
Round #5 results:    H T H H T H T T H H T H H T | H T T H H T
                     ─── first 14 (survival) ───   ── extra ──

Player A:  predicted  H T H H T H T T H H T H H T   H T T H H T
                      ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓  WINNER! 14/14

Player B:  predicted  H T H T T H T T H H T H H T   H T T H H T
                      ✓ ✓ ✓ ✗                        ELIMINATED (3/14)
```

Anyone can join at any time for the next round. Anyone can trigger the flip.

**The math:** 1 in 16,384 odds per entry (2^14). Winner takes the entire jackpot.

### Pool Split

| Allocation | Amount | Purpose |
|---|---|---|
| Jackpot | $0.99 (99%) | Winner takes all |
| Operator | $0.01 (1%) | Covers Solana transaction fees |

No house edge. Winner-takes-all. Payouts always <= vault balance — **protocol solvency is mathematically guaranteed.**

---

## Round-Based Model

```
1. Players enter anytime  →  node app/demo.mjs enter HHTHHTTHHTHHTHHTHHTH [keypair]
2. Anyone flips the round →  node app/demo.mjs flip       (permissionless — anyone can call)
3. First 14 match?        →  node app/demo.mjs claim <wallet> <round>  (verify + pay in one tx)
```

**Who is a winner?** Anyone whose first 14 predictions (out of their 20) exactly match the first 14 round results. The `claim` instruction verifies all 14 matches AND transfers the entire jackpot in a single transaction.

**Why 20 predictions?** You pick 20 H/T choices once when you enter. The first 14 are your survival sequence — those are checked against the round results. The full 20 are stored on-chain as your complete prediction set.

**How does the round work?** Each call to `flip` generates all 20 coin results at once using on-chain entropy (SHA-256 of round number + slot + timestamp + game PDA). Results are stored in a 32-round circular buffer. Your ticket records which round you entered — your first 14 predictions are compared against that round's first 14 results.

**Buffer expiry:** Results stay in the circular buffer for 32 rounds. Claim before your round's results are overwritten.

**Flip cooldown:** There's a 12-hour cooldown between rounds, enforced on-chain. This prevents spam-flipping and gives players time to enter before the next round.

---

## Agent-Operated

THE FLIP runs autonomously. No human in the loop:

- **Cron** calls `flip` periodically (permissionless — any agent can do it)
- Entry is always open — no gates, no round management
- Winners claim + collect in a single transaction

```bash
node app/demo.mjs flip    # flip all 20 coins for the current round (anyone can call)
```

---

## Live on Solana Devnet

| | |
|---|---|
| **Program** | [`7rSMKhD3ve2NcR4qdYK5xcbMHfGtEjTgoKCS5Mgx9ECX`](https://explorer.solana.com/address/7rSMKhD3ve2NcR4qdYK5xcbMHfGtEjTgoKCS5Mgx9ECX?cluster=devnet) |
| **USDC Mint** | `4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU` |
| **Vault** | PDA-controlled — no private key holds funds |
| **Flip cooldown** | 12 hours between rounds (on-chain enforced) |
| **Network** | Solana devnet |
| **Dashboard** | [the-flip-interface](https://the-flip.vercel.app) |

### API Endpoints

Agents can query game state via HTTP:

```bash
# Game state — jackpot, current round, entries, wins
GET /api/game

# Player ticket lookup
GET /api/ticket?wallet=<WALLET_ADDRESS>&round=<ROUND_NUMBER>
```

Example:

```bash
curl https://the-flip.vercel.app/api/game
curl "https://the-flip.vercel.app/api/ticket?wallet=2J9BE6FWLankTBHmmQXVkaap2eQYwkQ9msRLgVh7BKiA"
```

### Ticket API Response

The `/api/ticket` endpoint returns a rich response designed for agents:

```json
{
  "found": true,
  "status": "ELIMINATED",
  "wallet": "C7QX...",
  "round": 5,
  "predictionsString": "HHTHHTTHHTHHTHHTHHTH",
  "survivalPredictions": "HHTHHTTHHTHHTH",
  "flipped": true,
  "survived": false,
  "matches": 12,
  "predictions": ["H", "T", "H", ...],
  "results": ["H", "T", "T", ...],
  "winner": false,
  "collected": false,
  "summary": "Eliminated — matched 12 of 14 survival flips at round #5."
}
```

**Status values:** `WAITING` | `ELIMINATED` | `ALL_CORRECT` | `WINNER` | `WINNER_COLLECTED`

---

## Anti-Rug Design

The vault is a **Program Derived Address (PDA)** — no private key exists for it. Funds can only move through the program's `claim` and `withdraw_fees` instructions.

| Guarantee | How |
|---|---|
| **No rug pull** | Vault is a PDA — no private key, only program instructions move tokens |
| **Winner-takes-all** | `claim` verifies 14/14 survival AND pays entire jackpot in one atomic transaction |
| **Always solvent** | Payouts always <= vault balance by construction |
| **Self-service claim** | Winners call `claim` themselves — verify + pay in one tx |
| **Permissionless flip** | Anyone can call `flip` — not dependent on a single operator |
| **Verifiable randomness** | SHA-256 of round number + slot + timestamp + game PDA |

---

## Smart Contract Details

### 6 Instructions

| # | Instruction | Access | What it does |
|---|---|---|---|
| 1 | `initialize_game` | Authority | Create game PDA + USDC vault |
| 2 | `enter` | Anyone | Pay 1 USDC, submit 20 H/T predictions. `round = current_round` |
| 3 | `flip` | **Permissionless** | Flip all 20 coins at once, store in circular buffer, increment round |
| 4 | `claim` | **Permissionless** | Verify first 14 predictions match round results + pay entire jackpot in one tx |
| 5 | `withdraw_fees` | Authority | Withdraw operator's 1% fee pool |
| 6 | `close_game_v1` | Authority | Migration helper (close old PDA) |

### PDA Seeds

```
Game:    ["game",   authority]
Vault:   ["vault",  authority]     <- SPL Token Account holding USDC
Ticket:  ["ticket", game, player, &current_round.to_le_bytes()]
```

---

## Commands

### For players

```bash
node app/demo.mjs enter HHTHHTTHHTHHTHHTHHTH [keypair]   # enter with 20 predictions (always open)
node app/demo.mjs status                                   # game state + jackpot
node app/demo.mjs ticket <your_pubkey>                     # check your ticket result
node app/demo.mjs claim <your_pubkey> <round>              # claim jackpot (if first 14 match)
```

### For operators

```bash
node app/demo.mjs init                    # initialize game
node app/demo.mjs flip                    # flip all 20 coins for current round (permissionless)
node app/demo.mjs withdraw-fees [amount]  # withdraw operator fees
```

---

## Reading On-Chain Data (Build Your Own Frontend)

All game state lives on-chain. No backend required — just Solana accounts. Or use the API endpoints above.

### Derive the PDAs

```javascript
import { PublicKey } from '@solana/web3.js';

const PROGRAM_ID = new PublicKey('7rSMKhD3ve2NcR4qdYK5xcbMHfGtEjTgoKCS5Mgx9ECX');
const AUTHORITY  = new PublicKey('89FeAXomb6QvvQ5CQ1cjouRAP3EDu3ZyrV13Xt2HNbLa');

// Game state — current round, jackpot, entries, round results buffer
const [gamePDA] = PublicKey.findProgramAddressSync(
  [Buffer.from('game'), AUTHORITY.toBuffer()], PROGRAM_ID
);

// Vault — PDA-controlled SPL token account holding all USDC
const [vaultPDA] = PublicKey.findProgramAddressSync(
  [Buffer.from('vault'), AUTHORITY.toBuffer()], PROGRAM_ID
);

// Player ticket — one per player per round
const round = 5;
const roundBuf = Buffer.alloc(4);
roundBuf.writeUInt32LE(round);
const [ticketPDA] = PublicKey.findProgramAddressSync(
  [Buffer.from('ticket'), gamePDA.toBuffer(), PLAYER.toBuffer(), roundBuf],
  PROGRAM_ID
);
```

### Account Structures

**Game** (782 bytes — single instance)

| Field | Type | Description |
|---|---|---|
| `authority` | Pubkey | Operator wallet |
| `usdc_mint` | Pubkey | USDC token mint |
| `vault` | Pubkey | PDA vault address |
| `bump` | u8 | Game PDA bump |
| `vault_bump` | u8 | Vault PDA bump |
| `current_round` | u32 | Rounds completed (each round = 20 flips at once) |
| `round_results` | [u8; 640] | Circular buffer — 32 rounds x 20 results. `base_idx = (round % 32) * 20`. 1=H, 2=T, 0=not yet |
| `jackpot_pool` | u64 | Jackpot in USDC lamports (/ 1e6) |
| `operator_pool` | u64 | Operator fees in USDC lamports |
| `total_entries` | u32 | Lifetime entries |
| `total_wins` | u32 | Lifetime winners |
| `last_flip_at` | i64 | Unix timestamp of last flip (12h cooldown enforced) |

**Ticket** (99 bytes — one per player per round)

| Field | Type | Description |
|---|---|---|
| `game` | Pubkey | Game PDA |
| `player` | Pubkey | Player wallet |
| `round` | u32 | Which round this ticket is for |
| `predictions` | [u8; 20] | Player's 20 H/T picks (1=H, 2=T). First 14 checked for survival. |
| `winner` | bool | First 14 matched? |
| `collected` | bool | Jackpot collected? |
| `bump` | u8 | Ticket PDA bump |

### Fetch with Anchor

```javascript
import { Program, AnchorProvider } from '@coral-xyz/anchor';
import idl from './idl/the_flip.json' assert { type: 'json' };

const program = new Program(idl, provider);

// Game state
const game = await program.account.game.fetch(gamePDA);
console.log(`Round: ${game.currentRound} — Jackpot: $${(Number(game.jackpotPool) / 1e6).toFixed(2)}`);
console.log(`Entries: ${game.totalEntries}, Winners: ${game.totalWins}`);

// A player's ticket
const ticket = await program.account.ticket.fetch(ticketPDA);
console.log(`Round: ${ticket.round}, Winner: ${ticket.winner}, Collected: ${ticket.collected}`);
```

### Fetch Without Anchor (raw RPC)

```bash
# Game state (base64 -> decode with IDL layout)
curl -s https://api.devnet.solana.com -X POST -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0", "id": 1,
  "method": "getAccountInfo",
  "params": ["AAEwxhqM1EGjTbCyPqSCX7YpyuRqzBBfyf2kJG1nsGqd", {"encoding": "base64"}]
}'

# All tickets (filter by account size = 99 bytes)
curl -s https://api.devnet.solana.com -X POST -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0", "id": 1,
  "method": "getProgramAccounts",
  "params": ["7rSMKhD3ve2NcR4qdYK5xcbMHfGtEjTgoKCS5Mgx9ECX", {
    "filters": [{"dataSize": 99}],
    "encoding": "base64"
  }]
}'

# Vault USDC balance
curl -s https://api.devnet.solana.com -X POST -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0", "id": 1,
  "method": "getTokenAccountBalance",
  "params": ["Faxi5RatHTqj6copJXgrgLsW8pWTNUC2ARQ6dfazmCf9"]
}'
```

The IDL is included in `idl/the_flip.json` — use it to deserialize accounts in any language.

---

## Strategy

- Every sequence has equal odds — `HHHHHHHHHHHHHH` is just as likely as any random mix
- 1 in 16,384 chance (2^14) per entry to survive all 14 flips
- Winner takes all — no sharing the jackpot

---

## Build from Source

### Prerequisites

- Rust 1.92.0 (`rustup install 1.92.0`)
- Solana CLI 3.0.13 (`sh -c "$(curl -sSfL https://release.anza.xyz/stable/install)"`)
- Anchor CLI 0.32.1 (`cargo install --git https://github.com/coral-xyz/anchor avm && avm install 0.32.1 && avm use 0.32.1`)
- Node.js v20+

```bash
cargo-build-sbf --tools-version v1.52   # v1.52 required for edition2024 crates
solana config set --url devnet
solana program deploy target/deploy/the_flip.so --program-id 7rSMKhD3ve2NcR4qdYK5xcbMHfGtEjTgoKCS5Mgx9ECX
```

---

## Project Structure

```
the-flip/
├── program/
│   └── src/lib.rs       # Anchor smart contract — all game logic
├── app/
│   └── demo.mjs         # CLI client for all operations
├── idl/
│   └── the_flip.json    # Generated IDL (included so you don't need to build)
├── Anchor.toml
├── package.json
└── README.md
```

---

## License

MIT
