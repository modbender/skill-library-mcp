# agentic-x402

Agent skill for x402 payments — pay for and sell gated content using USDC on Base.

## What is x402?

[x402](https://docs.x402.org/) is an open payment standard built around HTTP 402 Payment Required. It enables services to charge for API access directly over HTTP using crypto payments.

This skill gives AI agents the ability to:
- **Pay** for x402-gated resources automatically
- **Fetch** content with automatic payment handling
- **Create** payment links to sell content (via 21.cash)
- **Manage** wallet balances (USDC + ETH for gas)

## Installation

```bash
npm i -g agentic-x402
```

Once installed, the `x402` command is available globally:

```bash
x402 --help
x402 --version
```

### Configure

Run the interactive setup to create a new wallet:

```bash
x402 setup
```

This will:
1. Generate a new wallet (recommended) or accept an existing key
2. Save configuration to `~/.x402/.env`
3. Display your wallet address for funding
4. Show your private key for backup

**Back up your private key immediately!** See [Backup](#backup-your-private-key) below.

#### Manual Configuration

Alternatively, set the environment variable directly:

```bash
export EVM_PRIVATE_KEY=0x...your_private_key...
```

### Development / Local Install

```bash
git clone https://github.com/monemetrics/agentic-x402.git
cd agentic-x402
pnpm install
cp config/example.env .env
# Edit .env and add your EVM_PRIVATE_KEY
```

## Quick Start

```bash
# 1. Create a wallet
x402 setup

# 2. Fund your wallet with USDC on Base (send to the address shown)

# 3. Check balance
x402 balance

# 4. Pay for a resource
x402 pay https://api.example.com/paid-endpoint

# 5. Fetch with auto-payment
x402 fetch https://api.example.com/data --json

# 6. Create a payment link (requires x402-links-server)
x402 create-link --name "My API" --price 1.00 --url https://api.example.com/premium
```

## Commands

### setup — Create or Configure Wallet

Interactive setup that generates a new wallet or accepts an existing private key. Saves configuration to `~/.x402/.env`.

```bash
x402 setup
```

**Security:** If you choose to use an existing private key, you'll see a warning. We recommend using a **dedicated wallet** with limited funds for automated agents.

---

### balance — Check Wallet Balances

Show your wallet address, USDC balance (for payments), and ETH balance (for gas). Warns if either balance is low.

```bash
x402 balance
x402 balance --json
x402 balance --full
```

| Flag | Description | Default |
|------|-------------|---------|
| `--json` | Output as JSON (address, network, chainId, balances) | — |
| `--full` | Show full wallet address instead of truncated | — |
| `-h, --help` | Show help | — |

---

### pay — Pay for an x402-Gated Resource

Make a request to an x402-gated URL. If the server responds with HTTP 402, the CLI extracts payment requirements, verifies the amount is within your max limit, and automatically signs and sends payment. Shows the response body after successful payment.

```bash
x402 pay https://api.example.com/data
x402 pay https://api.example.com/submit --method POST --body '{"data":"value"}'
x402 pay https://api.example.com/data --max 5
x402 pay https://api.example.com/data --dry-run
```

| Flag | Description | Default |
|------|-------------|---------|
| `<url>` | The URL of the x402-gated resource (positional) | **required** |
| `--method` | HTTP method | `GET` |
| `--body` | Request body (for POST/PUT requests) | — |
| `--header` | Add custom header (can be used multiple times) | — |
| `--max` | Maximum payment in USD (overrides config) | from config |
| `--dry-run` | Show payment details without paying | — |
| `-h, --help` | Show help | — |

If the URL does not require payment (non-402 response), the response is returned directly.

---

### fetch — Fetch with Automatic Payment

A simpler, pipe-friendly version of `pay`. Uses the x402 SDK's wrapped fetch to handle 402 responses automatically. Supports `--json` and `--raw` output modes for easy integration with scripts and agents.

```bash
x402 fetch https://api.example.com/data
x402 fetch https://api.example.com/data --json
x402 fetch https://api.example.com/data --raw
x402 fetch https://api.example.com/submit --method POST --body '{"key":"value"}'
```

| Flag | Description | Default |
|------|-------------|---------|
| `<url>` | The URL to fetch (positional) | **required** |
| `--method` | HTTP method | `GET` |
| `--body` | Request body (for POST/PUT) | — |
| `--header` | Add header as `"Key: Value"` | — |
| `--json` | Output as JSON only (for piping to other tools) | — |
| `--raw` | Output raw response body only (no headers or status) | — |
| `-h, --help` | Show help | — |

---

### create-link — Create a Payment Link

Create a payment link via the [21.cash](https://21.cash) x402-links-server. You can gate a URL or text content behind a USDC payment. Requires `X402_LINKS_API_URL` environment variable. Link creation costs $0.10 USDC, paid automatically via x402.

```bash
x402 create-link --name "Premium Guide" --price 5.00 --url https://mysite.com/guide.pdf
x402 create-link --name "Secret Message" --price 0.50 --text "The secret is..."
x402 create-link --name "API Access" --price 1.00 --url https://api.example.com/data --webhook https://mysite.com/webhook
```

| Flag | Description | Default |
|------|-------------|---------|
| `--name` | Name of the payment link | **required** |
| `--price` | Price in USD (e.g., `"5.00"` or `"0.10"`) | **required** |
| `--url` | URL to gate behind payment | — |
| `--text` | Text content to gate behind payment | — |
| `--desc` | Description of the link | — |
| `--webhook` | Webhook URL for payment notifications | — |
| `--json` | Output as JSON | — |
| `-h, --help` | Show help | — |

> **Note:** Either `--url` or `--text` is required. The link is deployed as a smart contract on Base.

---

### link-info — Get Payment Link Details

Look up details of a payment link by its router address or full URL.

```bash
x402 link-info 0x1234...5678
x402 link-info https://21.cash/pay/0x1234...5678
```

| Flag | Description | Default |
|------|-------------|---------|
| `<address>` | Router contract address or full payment URL (positional) | **required** |
| `--json` | Output as JSON | — |
| `-h, --help` | Show help | — |

## Configuration

Config is loaded from these locations (in order of priority):

1. Environment variables
2. `.env` file in current directory
3. `~/.x402/.env` (global config)

### Environment Variables

#### Required

| Variable | Description |
|----------|-------------|
| `EVM_PRIVATE_KEY` | Your wallet private key (0x-prefixed). Used to sign payment authorizations. |

#### Network Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `X402_NETWORK` | `mainnet` (Base, chain 8453) or `testnet` (Base Sepolia, chain 84532) | `mainnet` |
| `X402_MAX_PAYMENT_USD` | Safety limit — payments exceeding this are rejected unless `--max` is used | `10` |
| `X402_FACILITATOR_URL` | Custom facilitator URL | Coinbase (mainnet) / x402.org (testnet) |
| `X402_VERBOSE` | Enable verbose logging (`1` = on, `0` = off) | `0` |

#### 21.cash Integration (for link commands)

| Variable | Description |
|----------|-------------|
| `X402_LINKS_API_URL` | Base URL of x402-links-server (e.g., `https://21.cash`) |

## Global Options

| Flag | Description |
|------|-------------|
| `-h, --help` | Show help for a command |
| `-v, --version` | Show CLI version |

## CLI Reference

| Category | Command | Description |
|----------|---------|-------------|
| **Setup** | `setup` | Create or configure your x402 wallet |
| **Info** | `balance` | Check wallet USDC and ETH balances |
| **Payments** | `pay <url>` | Pay for an x402-gated resource (verbose output) |
| **Payments** | `fetch <url>` | Fetch with auto-payment (pipe-friendly `--json`/`--raw`) |
| **Links** | `create-link` | Create a payment link to sell content (21.cash) |
| **Links** | `link-info <addr>` | Get info about a payment link |

## For Agents

This skill is designed for use with AI agents (Claude Code, OpenClaw, etc.). The `SKILL.md` file contains full agent-readable documentation. Agents can use the `--json` flag on all commands for structured output:

```bash
# Structured balance output
x402 balance --json

# Pipe-friendly fetch
x402 fetch https://api.example.com/data --json

# Raw output for further processing
x402 fetch https://api.example.com/data --raw
```

## Backup Your Private Key

Your private key is stored in `~/.x402/.env`. **If lost, your funds cannot be recovered.**

### Recommended Backup Methods

1. **Password Manager** (Recommended)
   - Store in 1Password, Bitwarden, or similar
   - Create a secure note with your private key

2. **Encrypted File**
   ```bash
   gpg -c ~/.x402/.env
   # Store the encrypted .env.gpg file securely
   ```

3. **Paper Backup** (for larger amounts)
   - Write down the private key
   - Store in a safe or safety deposit box

### View Your Private Key

```bash
cat ~/.x402/.env | grep EVM_PRIVATE_KEY
```

### Recovery

```bash
mkdir -p ~/.x402
echo "EVM_PRIVATE_KEY=0x...your_backed_up_key..." > ~/.x402/.env
chmod 600 ~/.x402/.env
x402 balance  # verify
```

## Security Best Practices

- **Use a dedicated wallet** — Never use your main wallet with automated agents
- **Limit funds** — Only transfer what you need for payments
- **Set payment limits** — Configure `X402_MAX_PAYMENT_USD` to cap exposure
- **Test first** — Use `X402_NETWORK=testnet` before mainnet
- **Protect the config** — Keep `~/.x402/.env` with 600 permissions
- **Never share** — Your private key gives full access to your wallet

## License

MIT
