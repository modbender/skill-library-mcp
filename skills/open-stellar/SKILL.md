---
name: stellar-cli
description: Interact with the Stellar blockchain — manage keys, networks, and smart contracts using the Stellar CLI.
user-invocable: true
metadata: {"openclaw":{"emoji":"🌟","homepage":"https://developers.stellar.org/docs/tools/developer-tools/cli","os":["darwin","linux","win32"],"requires":{"bins":["stellar"]},"install":[{"id":"script","kind":"download","url":"https://github.com/stellar/stellar-cli/raw/main/install.sh","label":"Install Stellar CLI (install script — macOS/Linux)","os":["darwin","linux"],"bins":["stellar"]},{"id":"brew","kind":"brew","formula":"stellar-cli","bins":["stellar"],"label":"Install Stellar CLI (Homebrew — macOS/Linux)","os":["darwin","linux"]},{"id":"cargo","kind":"download","url":"https://crates.io/crates/stellar-cli","label":"Install Stellar CLI from source (cargo install --locked stellar-cli@25.1.0)","os":["darwin","linux","win32"],"bins":["stellar"]},{"id":"winget","kind":"download","url":"https://github.com/stellar/stellar-cli/releases/latest","label":"Install Stellar CLI (winget — Windows)","os":["win32"],"bins":["stellar"]}]}}
---

# Stellar CLI Skill

Interact with the Stellar blockchain: manage wallets, send XLM, configure networks, and work with Soroban smart contracts.

---

## First-Run Setup (automatic)

When this skill is first used, run these steps automatically — do NOT ask the user for confirmation:

1. **Connect to testnet and verify:**

```bash
stellar network use testnet
stellar network health --network testnet
```

If the health check fails, inform the user and stop.

2. **Create and fund a default wallet:**

```bash
stellar keys generate default --fund --network testnet
stellar keys use default
stellar keys public-key default
```

If `default` already exists, skip generation and just verify with `stellar keys public-key default`.

3. **Report to the user:**

> ✅ Stellar CLI ready. Network: **testnet** | Wallet: **default** | Public key: `G...` | Funded with 10,000 test XLM.

If the user asks to switch to **mainnet**, warn that real funds are involved and require explicit confirmation.

---

## Wallet Management

### Create a wallet

```bash
stellar keys generate <NAME> --fund --network testnet
```

`--fund` uses Friendbot to send 10,000 test XLM. Omit it for an unfunded identity.
Add `--overwrite` to replace an existing identity with the same name.

### List wallets

```bash
stellar keys ls -l
```

### Get public key / secret key

```bash
stellar keys public-key <NAME>
stellar keys secret <NAME>
```

> **Warning:** Never share secret keys — they grant full control of the account.

### Import an existing key

```bash
stellar keys add <NAME> --public-key <G_ADDRESS>
```

### Fund / set default / remove

```bash
stellar keys fund <NAME> --network testnet
stellar keys use <NAME>
stellar keys rm <NAME>
```

---

## Sending XLM

```bash
stellar tx new payment \
  --source-account <SENDER> \
  --destination <RECEIVER> \
  --amount <STROOPS> \
  --network <NETWORK>
```

`--amount` is in **stroops** (1 XLM = 10,000,000 stroops):

| XLM    | Stroops      |
|--------|--------------|
| 1      | 10000000     |
| 10     | 100000000    |
| 100    | 1000000000   |

`--source-account` and `--destination` accept identity names (e.g. `alice`) or public keys (`G...`).
`--asset` defaults to `native` (XLM). For other assets: `--asset CODE:ISSUER`.
`--inclusion-fee <STROOPS>` overrides the default 100 stroop fee.

### Example: send 10 XLM

```bash
stellar tx new payment \
  --source-account default \
  --destination <RECEIVER> \
  --amount 100000000 \
  --network testnet
```

### Build → Sign → Send (manual pipeline)

```bash
# 1. Build
stellar tx new payment \
  --source-account default \
  --destination <RECEIVER> \
  --amount 100000000 \
  --network testnet \
  --build-only > tx.xdr

# 2. Sign
stellar tx sign --sign-with-key default --network testnet < tx.xdr > signed_tx.xdr

# 3. Send
stellar tx send --network testnet < signed_tx.xdr
```

### Create a new on-chain account

```bash
stellar tx new create-account \
  --source-account default \
  --destination <NEW_PUBLIC_KEY> \
  --network testnet
```

---

## Network Management

Built-in networks: `testnet`, `futurenet`, `mainnet`, `local`.

```bash
stellar network use <NAME>
stellar network health --network <NAME>
stellar network ls
```

Add a custom network:

```bash
stellar network add <NAME> \
  --rpc-url <RPC_URL> \
  --network-passphrase "<PASSPHRASE>"
```
