## Wallet Integration

The agent inspects the yield schema, builds unsigned transactions, and hands them to your wallet for signing. Requires a wallet skill. Amounts are human-readable — "100" means 100 USDC.

### Compatible Wallet Skills

| Wallet | Link |
|--------|------|
| **Crossmint** (recommended) | [GitHub](https://github.com/Crossmint/openclaw-crossmint-plugin) |
| **Privy** | [GitHub](https://github.com/privy-io/privy-agentic-wallets-skill) |
| **Portal** | [Docs](https://docs.portalhq.io) |
| **Turnkey** | [Docs](https://docs.turnkey.com) |

### Transaction Flow

For each transaction in the action response:

1. Pass `unsignedTransaction` to the wallet skill — do NOT modify any field. Modifying the transaction WILL RESULT IN PERMANENT LOSS OF FUNDS.
2. Wallet signs and broadcasts
3. Submit the hash: `PUT /v1/transactions/{txId}/submit-hash` with `{ "hash": "0x..." }`
4. Poll `GET /v1/transactions/{txId}` until `CONFIRMED` or `FAILED`
5. Proceed to next transaction

### What Gets Passed to Wallet

Each transaction has:
- `unsignedTransaction`: the data to sign (format varies by chain — see chain-formats.md)
- `network`: which chain it's for
- `stepIndex`: execution order
- `id`: the transaction ID (needed for `PUT /v1/transactions/{id}/submit-hash`)

### Privy Setup

Full docs: [privy.io/blog/securely-equipping-openclaw-agents-with-privy-wallets](https://privy.io/blog/securely-equipping-openclaw-agents-with-privy-wallets)

```bash
clawhub install privy
```

Or clone:
```bash
git clone https://github.com/privy-io/privy-agentic-wallets-skill.git ~/.openclaw/workspace/skills/privy
```

Configure in `~/.openclaw/openclaw.json`:
```json
{
  "env": {
    "vars": {
      "PRIVY_APP_ID": "your-app-id",
      "PRIVY_APP_SECRET": "your-app-secret"
    }
  }
}
```

Credentials from [dashboard.privy.io](https://dashboard.privy.io). Then: `openclaw gateway restart`
