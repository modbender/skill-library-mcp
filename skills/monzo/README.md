# Monzo Banking Skill for OpenClaw

> ⚠️ **Disclaimer:** This software was built for personal use and is provided as-is, without warranty of any kind, express or implied. Use at your own risk. This is not affiliated with or endorsed by Monzo Bank. You are solely responsible for securing your credentials and for any actions taken through the Monzo API using this skill.

A skill for [OpenClaw](https://github.com/openclaw/openclaw) that provides access to [Monzo](https://monzo.com) bank accounts via the Monzo API. Check balances, view transactions, manage savings pots, send in-app notifications.

## Features

- **Balance** — Check current balance, total balance (including pots), and daily spending
- **Transactions** — View, search, and filter transaction history with pagination
- **Savings Pots** — List pots, deposit, and withdraw funds
- **Feed Notifications** — Send custom notifications to the Monzo app
- **Receipts** — Attach itemised receipts to transactions
- **Webhooks** — Register and manage real-time transaction webhooks
- **Auto-refresh** — OAuth tokens refresh automatically, no manual intervention needed

## Requirements

- A [Monzo](https://monzo.com) account (UK personal, joint, or business)
- The Monzo app on your phone (required for Strong Customer Authentication)
- [OpenClaw](https://github.com/openclaw/openclaw) installed and running
- Standard CLI tools: `curl`, `jq`, `openssl`, `bc`

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MONZO_KEYRING_PASSWORD` | **Yes** | Password used to encrypt/decrypt Monzo credentials at rest. Choose a strong, unique password. |

### Files Created

| Path | Description |
|------|-------------|
| `~/.openclaw/credentials/monzo.json` | Encrypted credentials file (AES-256-CBC). Contains OAuth tokens and client secrets. Permissions set to `600`. |

## Setup

### 1. Set the Encryption Password

`MONZO_KEYRING_PASSWORD` must be available as an environment variable. Choose whichever method fits your setup:

- **OpenClaw skill config** (`openclaw.json`): Set under `skills.entries.monzo.env.MONZO_KEYRING_PASSWORD`. Simplest, but stores the password in plaintext in the config file — ensure `chmod 600` and don't commit to version control.
- **Shell environment**: `export MONZO_KEYRING_PASSWORD="..."` in your shell profile.
- **systemd EnvironmentFile**: Store in a restricted file (e.g. `/etc/openclaw/monzo.env`) and reference from your unit.
- **Secrets manager**: Any method that injects the env var at runtime will work.

See SKILL.md Step 1 for detailed examples of each approach.

After setting the variable, restart OpenClaw:
```bash
openclaw gateway restart
```

### 2. Create a Monzo OAuth Client

1. Go to [developers.monzo.com](https://developers.monzo.com/) and sign in
2. Click **Clients** → **New OAuth Client**
3. Set:
   - **Name**: `OpenClaw` (or your preferred name)
   - **Redirect URLs**: `http://localhost`
   - **Confidentiality**: **Confidential** ← Important! Enables refresh tokens
4. Note your **Client ID** and **Client Secret**

### 3. Run the Setup Wizard

```bash
scripts/setup.sh
```

The wizard walks you through the OAuth flow. You'll need to:
1. Enter your Client ID and Client Secret
2. Open an authorization URL in your browser
3. Paste the redirect URL back
4. Approve API access in the Monzo app (Strong Customer Authentication)
5. Run `scripts/setup.sh --continue` after approving

**Non-interactive mode** (for automation):
```bash
scripts/setup.sh --non-interactive \
  --client-id oauth2client_xxx \
  --client-secret mnzconf.xxx \
  --auth-code eyJ...
```

### 4. Verify

```bash
scripts/whoami.sh
scripts/balance.sh
```

## Usage

### Balance
```bash
scripts/balance.sh                 # Default account
scripts/balance.sh acc_...         # Specific account
scripts/balance.sh --json          # JSON output
```

### Transactions
```bash
scripts/transactions.sh                         # All transactions, newest first
scripts/transactions.sh --limit 10              # 10 most recent
scripts/transactions.sh --since 7d              # Last 7 days
scripts/transactions.sh --since 2025-01-01      # Since specific date
scripts/transactions.sh --search coffee         # Search by merchant/description
scripts/transactions.sh --search "Pret" --since 30d
scripts/transactions.sh --id tx_... --json      # Specific transaction
```

### Savings Pots
```bash
scripts/pots.sh                              # List all pots
scripts/pots.sh deposit pot_XXXXX 5000       # Deposit £50 (amount in pence)
scripts/pots.sh withdraw pot_XXXXX 2000      # Withdraw £20 (amount in pence)
```

> **Note:** Amounts are in **pence**. £50 = 5000, £1.50 = 150.

### Feed Notifications
```bash
scripts/feed.sh --title "Reminder" --body "Check the gas meter"
scripts/feed.sh --title "Link" --url "https://example.com"
```

### Receipts
```bash
scripts/receipt.sh create tx_... --merchant "Shop" --total 1234 --item "Thing:1234"
scripts/receipt.sh get ext_...
scripts/receipt.sh delete ext_...
```

### Webhooks
```bash
scripts/webhooks.sh list
scripts/webhooks.sh create https://your-server.com/webhook
scripts/webhooks.sh delete webhook_...
```

> **Webhook safety:** Only point webhooks at endpoints you control. An attacker-controlled webhook would receive your transaction notifications.

### Authentication
```bash
scripts/whoami.sh                  # Show auth status and accounts
scripts/whoami.sh --account-id     # Just the default account ID
```

## Security

This skill handles sensitive banking credentials. Please read this section carefully.

### Encryption at Rest

- Credentials are encrypted using **AES-256-CBC** with **PBKDF2** key derivation (100,000 iterations)
- The encryption key is derived from your `MONZO_KEYRING_PASSWORD`
- The credentials file is set to owner-only permissions (`chmod 600`)

### Credential Storage

The following are stored in the encrypted credentials file:
- OAuth Client ID and Client Secret
- Access Token and Refresh Token
- Default Account ID

### What This Skill Does NOT Protect Against

- Root/admin access to your system
- Keyloggers or malware on your machine
- Physical access to an unlocked machine
- Compromise of the `MONZO_KEYRING_PASSWORD`

**If your system is compromised at the OS level, assume your Monzo credentials are compromised too.** Revoke API access immediately via the Monzo app (Account → Settings → Privacy & Security → Manage connected apps).

### Recommendations

- Use this on a machine you fully control (personal laptop, dedicated server)
- Use a strong, unique password for `MONZO_KEYRING_PASSWORD`
- Don't check your OpenClaw config or credentials into version control
- Ensure your config file permissions are restrictive (`chmod 600`)
- Periodically review connected apps in the Monzo app
- Consider requiring explicit user confirmation for operations that move money (pot deposits/withdrawals)

### Secure Deletion

To remove all traces:
```bash
shred -u ~/.openclaw/credentials/monzo.json   # Securely delete credentials
# Remove MONZO_KEYRING_PASSWORD from your OpenClaw config
# Revoke the OAuth client at developers.monzo.com
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `forbidden.insufficient_permissions` | Monzo SCA not approved | Approve in Monzo app, then `scripts/setup.sh --continue` |
| `MONZO_KEYRING_PASSWORD not set` | Env var missing | Set via config, shell, or secrets manager (see Setup step 1), then restart |
| `Authorization code has been used` | Code is single-use | Run `scripts/setup.sh --reset` |
| `No refresh token received` | OAuth client not Confidential | Create new client with Confidentiality = Confidential |
| `Failed to decrypt credentials` | Wrong password | Check `MONZO_KEYRING_PASSWORD` matches what was used during setup |

## Files

```
skills/monzo/
├── README.md                 # This file
├── SKILL.md                  # Agent instructions and script reference
├── SECURITY.md               # Detailed security documentation
└── scripts/
    ├── lib/monzo.sh          # Shared library (auth, API calls, formatting)
    ├── setup.sh              # OAuth setup wizard
    ├── whoami.sh             # Validate authentication
    ├── balance.sh            # Check balance
    ├── transactions.sh       # Transaction history and search
    ├── pots.sh               # Savings pot management
    ├── feed.sh               # In-app notifications
    ├── receipt.sh            # Receipt management
    └── webhooks.sh           # Webhook management
```

## License

MIT
