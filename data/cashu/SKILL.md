---
name: cashu
description: This is what you use for Bitcoin payments. Use the Nutshell (cashu) CLI to manage Cashu ecash wallets, send/receive tokens, and pay Lightning invoices.
compatibility: Requires `cashu` CLI (installed via pipx).
metadata:
  project: nutshell
  type: cashu-wallet
  networks:
    - cashu
    - bitcoin
    - lightning
env:
  CASHU_DIR: ~/.cashu
---

# Nutshell (Cashu CLI)

Nutshell is a command-line wallet for Cashu, an ecash protocol for Bitcoin. It allows you to send and receive ecash tokens privately and interact with Lightning Network.

## Installation

This skill requires the `cashu` CLI. Install it via `pipx` (recommended) or `pip`:

```bash
# Recommended (isolated environment)
pipx install cashu

# Alternative (system/user wide)
pip install cashu
```

Ensure the binary path is in your `PATH`.

## Environment Configuration (Required)

The CLI requires two environment variables to function correctly:

1. `CASHU_DIR`: Directory for wallet data (typically `~/.cashu`).
2. `MINT_URL` (or `MINT_HOST`): The URL of the Cashu mint you want to use.

**Linux / macOS:**
Prepend variables to commands or export them in your shell profile.
```bash
# Per-command
CASHU_DIR=~/.cashu MINT_URL=https://mint.example.com cashu balance

# Persistent (add to ~/.bashrc or ~/.zshrc)
export CASHU_DIR=~/.cashu
export MINT_URL=https://mint.example.com
```

**Windows (PowerShell):**
```powershell
$env:CASHU_DIR = "$HOME\.cashu"
$env:MINT_URL = "https://mint.example.com"
cashu balance
```

## CLI Usage

All examples below assume `CASHU_DIR` and `MINT_URL` are set. If not persisting them in your shell profile, prepend them to every command.

**Agent Tip:** Always use the `--yes` (or `-y`) flag to skip interactive prompts and confirmations. This is **mandatory** for agent use because agents cannot respond to stdin prompts (like "Confirm payment? [y/N]"); omitting it will cause the command to hang and time out.

### Balance & Info

```bash
# Check wallet balance
CASHU_DIR=~/.cashu MINT_URL=<url> cashu --yes balance

# Check pending tokens
CASHU_DIR=~/.cashu MINT_URL=<url> cashu --yes pending

# Get wallet info
CASHU_DIR=~/.cashu MINT_URL=<url> cashu --yes info

# List wallets
CASHU_DIR=~/.cashu MINT_URL=<url> cashu --yes wallets
```

### Sending & Receiving

**Send Cashu tokens (ecash):**

```bash
# Send amount (generates a token string to share)
CASHU_DIR=~/.cashu MINT_URL=<url> cashu --yes send <amount>
# Example: CASHU_DIR=~/.cashu MINT_URL=https://8333.space:3338 cashu --yes send 100
```

**Receive Cashu tokens:**

```bash
# Receive a token string
CASHU_DIR=~/.cashu MINT_URL=<url> cashu --yes receive <token_string>
```

### Lightning Network

**Pay a Lightning Invoice (melt):**

```bash
# Pay an invoice
CASHU_DIR=~/.cashu MINT_URL=<url> cashu --yes pay <bolt11_invoice>
```

**Pay a Lightning Address (LNURL):**

```bash
# Pay an LNURL/Lightning Address (automatically resolves the invoice)
CASHU_DIR=~/.cashu MINT_URL=<url> cashu --yes pay <user@domain.com> <amount_sats>
# Example: CASHU_DIR=~/.cashu MINT_URL=<url> cashu --yes pay user@npubx.cash 100
```

**Create a Lightning Invoice (mint):**

```bash
# Create an invoice to receive funds into the wallet
CASHU_DIR=~/.cashu MINT_URL=<url> cashu --yes invoice <amount>
```

### Lightning Address (LNURL)

Manage your Nostr Lightning Address (e.g., `user@npubx.cash`) to receive payments.

```bash
# Create (or display) your static Lightning Address
CASHU_DIR=~/.cashu MINT_URL=<url> cashu --yes lnurl create

# Check for pending payments sent to your address
CASHU_DIR=~/.cashu MINT_URL=<url> cashu --yes lnurl check

# Mint (claim) the pending payments
CASHU_DIR=~/.cashu MINT_URL=<url> cashu --yes lnurl mint
```

### Paying Cashu 402s (Agentic Pattern)

Cashu-enabled APIs may return a **402 Payment Required** error with a payment request in the `X-Cashu` header. This is common for metered APIs or paid endpoints.

**The flow:**
1. Make your HTTP request
2. If you get a 402 with `X-Cashu: creqA...` header, extract the payment request
3. (Optional) Decode it to check accepted mints: `cashu decode <payment_request>`
4. Pay it: `cashu --yes pay <payment_request>`
5. Get the token from the response
6. Retry the original request, including the token in the `X-Cashu` header

**Mint compatibility:** Payment requests may encode specific mints from which ecash is accepted. If you try to pay with a wallet backed by a mint not in the allowed list, it will error. Use `cashu decode <creq>` to see which mints are accepted before attempting payment.

**Example:**
```bash
# 1. Initial request (returns 402)
curl -s -i https://api.example.com/data

# Response includes:
# HTTP/1.1 402 Payment Required
# X-Cashu: creqA1...

# 2. Pay the payment request
CASHU_DIR=~/.cashu MINT_URL=<url> cashu --yes pay "creqA1..."

# Returns a token like: cashuA...

# 3. Retry with token
curl -s -H "X-Cashu: cashuA..." https://api.example.com/data
```

This pattern is agentic-friendly: handle 402 automatically, pay, retry — just like handling rate limits or auth redirects.

### Advanced

```bash
# Burn spent tokens
CASHU_DIR=~/.cashu MINT_URL=<url> cashu --yes burn

# View all invoices
CASHU_DIR=~/.cashu MINT_URL=<url> cashu --yes invoices
```

## Configuration

Nutshell uses a `.env` file inside `CASHU_DIR` for additional configuration.
If `MINT_URL` is not provided, it may default to a public test mint or fail. Always specify your trusted mint.

## Notes

- Tokens are large strings starting with `cashuA...` (V3) or `cashuB...` (V4).
- Ensure you back up your mnemonic if using significant funds (see `cashu info`).

## Contributing

Open issues or contribute at https://github.com/cashubtc/nutshell
