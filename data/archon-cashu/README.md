# Archon Cashu Wallet

DID-native ecash wallet. Locks cashu tokens to Archon DID public keys (NUT-11 P2PK) so tokens are spendable only by the recipient — even if sent in the clear. Optionally delivers via encrypted dmail for privacy.

## Security Model

**Two layers of protection:**

1. **P2PK (NUT-11)** — Token-level. Locks ecash to the recipient's DID secp256k1 pubkey. The mint enforces that only a valid Schnorr signature from the DID's private key can spend the token. **This is the primary security mechanism.**

2. **Dmail encryption** — Transport-level. Hides the token from observers. Adds sender authentication. **Optional — P2PK alone is sufficient for security.**

Every Archon DID already has a secp256k1 key. No extra setup needed.

## Prerequisites

- [Nutshell](https://github.com/cashubtc/nutshell) (`pip install cashu`) — cashu protocol CLI
- [Archon](https://github.com/ArcHive-tech/archon) node with keymaster running
- Archon keymaster wallet with at least one DID identity
- (Optional) [LNbits](https://lnbits.com) for auto-minting via Lightning

## Setup

```bash
# Create config (edit with your paths)
./config.sh --create

# Edit the config
nano ~/.config/archon/cashu.env

# Verify
./config.sh
```

## Scripts

| Script | Description |
|--------|-------------|
| `config.sh` | Configuration management |
| `balance.sh` | Show cashu wallet balance |
| `mint.sh <amount>` | Mint tokens (auto-pays from LNbits if configured) |
| `send.sh <did> <amount> [memo]` | **P2PK-locked** send via encrypted dmail (default, most secure) |
| `send-unlocked.sh <did> <amount> [memo]` | Bearer token send via dmail (no P2PK lock) |
| `lock.sh <did> <amount>` | Create P2PK-locked token without sending (for Nostr, public channels) |
| `receive.sh [--auto]` | Scan inbox for cashu tokens, redeem (handles both P2PK and bearer) |

## Usage

```bash
# Check balance
./balance.sh

# Mint 100 sats (pays Lightning invoice from LNbits)
./mint.sh 100

# Send 50 sats — P2PK-locked to recipient's DID key + encrypted dmail
./send.sh did:cid:bagaaiera... 50 "Payment for services"

# Create a locked token for public use (Nostr, paste anywhere)
TOKEN=$(./lock.sh did:cid:bagaaiera... 25)
echo "$TOKEN"  # Safe to post publicly — only the DID holder can spend

# Check inbox and redeem received tokens
./receive.sh

# Send bearer tokens via dmail (no P2PK, relies on dmail encryption only)
./send-unlocked.sh did:cid:bagaaiera... 10 "Quick tip"
```

## How P2PK + DID Works

```
Sender                          Mint                        Recipient
  |                               |                             |
  |-- resolve DID doc ----------->|                             |
  |   extract secp256k1 pubkey    |                             |
  |                               |                             |
  |-- cashu send --lock <pubkey> ->|                            |
  |   token.secret.data = pubkey  |                             |
  |                               |                             |
  |-- dmail (encrypted) or public channel ------------------>   |
  |                               |                             |
  |                               |<-- cashu receive (signs) ---|
  |                               |    Schnorr sig with DID key |
  |                               |-- verify sig, swap proofs ->|
  |                               |                             |
```

## Configuration

Edit `~/.config/archon/cashu.env`:

```bash
CASHU_BIN="cashu"                              # Path to nutshell CLI
CASHU_MINT_URL="https://bolverker.com/cashu"   # Default mint
LNBITS_ENV="~/.config/lnbits.env"              # LNbits credentials (optional)
ARCHON_CONFIG_DIR="~/.config/archon"           # Archon keymaster config
ARCHON_WALLET_PATH="~/.config/archon/wallet.json"
ARCHON_PASSPHRASE=""                           # Wallet passphrase
```

## Minimum Amount

The mint charges a 1 sat fee per transaction. **Minimum send: 2 sats.**

## Security Notes

- **P2PK tokens can be sent anywhere** — Nostr, email, public paste — only the DID holder can spend
- **Bearer tokens** (`send-unlocked.sh`) are anyone-can-spend — rely on dmail encryption for security
- **DID key rotation**: Receive P2PK tokens before rotating DID keys (old-key tokens become unspendable)
- **NUT-11 refund tags**: Future support for sender refund paths with `locktime` expiry
- Config file is created with `chmod 600` (owner-only)
