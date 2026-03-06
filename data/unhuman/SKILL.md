---
name: unhuman
description: Search, register, and manage domain names via unhuman.domains. Pay with bitcoin using agent-wallet. Use when the user wants to find available domains, register a new domain, manage DNS records, update nameservers, or renew a domain.
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["npx"] },
        "install":
          [
            {
              "id": "unhuman-npm",
              "kind": "node",
              "package": "unhuman",
              "bins": ["unhuman"],
              "label": "Install unhuman CLI (npm)",
            },
          ],
      },
  }
---

# unhuman — Domain Management CLI

Register and manage domains at [unhuman.domains](https://unhuman.domains), paid with bitcoin via Lightning Network.

- **npm package**: [unhuman](https://www.npmjs.com/package/unhuman) (published by moneydevkit)
- **Source**: Domain registration API at unhuman.domains

## Commands

### Search domains

```bash
npx unhuman domains search myproject
npx unhuman domains search myproject --tld com,dev,xyz
npx unhuman domains search myproject --json
```

### Register a domain

```bash
# Manual payment (prints Lightning invoice, waits for preimage)
npx unhuman domains register mysite.xyz --email recovery@example.com

# Auto-pay with agent-wallet (requires explicit --wallet flag)
npx unhuman domains register mysite.xyz --wallet --email recovery@example.com
```

- `--email` sets recovery email (recommended)
- On success, stores management token to `~/.unhuman/tokens.json`

### Domain info

```bash
npx unhuman domains info mysite.xyz
```

### DNS records

```bash
npx unhuman domains dns mysite.xyz
npx unhuman domains dns set mysite.xyz --records '[{"type":"A","name":"@","value":"1.2.3.4","ttl":3600}]'
```

### Update nameservers

```bash
npx unhuman domains nameservers mysite.xyz ns1.example.com ns2.example.com
```

### Renew a domain

```bash
npx unhuman domains renew mysite.xyz
npx unhuman domains renew mysite.xyz --wallet --period 2
```

### Recover management token

```bash
npx unhuman domains recover mysite.xyz --email recovery@example.com
npx unhuman domains recover mysite.xyz --email recovery@example.com --code 123456
```

### List stored tokens

```bash
npx unhuman domains tokens
```

## Payment with --wallet flag

The `--wallet` flag enables autonomous payment via `@moneydevkit/agent-wallet`. **Only use when the user explicitly requests autonomous payment.**

Requires:
- A running agent-wallet daemon (`npx @moneydevkit/agent-wallet start`)
- Sufficient balance in the wallet

Flow: submit request → receive 402 with Lightning invoice → agent-wallet pays → retry with preimage.

**⚠️ Always confirm with the user before using --wallet.** This flag triggers a real bitcoin payment. Without --wallet, the CLI prints the invoice for the user to pay manually.

## Credentials & Storage

- **Management tokens**: Stored at `~/.unhuman/tokens.json` after successful registration. These tokens are required for DNS/nameserver/renewal operations. Protect this file.
- **No API keys required**: Domain search is free. Registration/renewal uses the MDK 402 payment protocol (pay-per-use via Lightning invoice).
- **agent-wallet**: If using --wallet, the wallet daemon must be initialized and running. The wallet's mnemonic and keys are managed separately by agent-wallet at `~/.agent-wallet/`.

## Notes

- All commands support `--json` for machine-readable output
- Prices are in USD, paid in bitcoin at current exchange rate
- Recovery email is optional but strongly recommended for token recovery
