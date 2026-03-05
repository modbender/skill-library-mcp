# LND Wallet Security Guide

## Default Model: Watch-Only with Remote Signer

The default setup uses lnd's remote signer architecture. The agent machine runs
a **watch-only** lnd node that delegates all signing to a separate **signer**
node on a secured machine. No private keys exist on the agent machine.

```
Agent Machine (watch-only)  <--gRPC-->  Signer Machine (keys)
  - Runs neutrino                        - Holds seed
  - Manages channels                     - Signs commitments
  - Routes payments                      - Signs on-chain txs
  - No key material                      - Minimal attack surface
```

Set up the signer with the `lightning-security-module` skill, then import
credentials on the agent machine with `import-credentials.sh`.

**What stays on the signer:**
- 24-word seed mnemonic
- All private keys (funding, revocation, HTLC)
- Wallet database with key material

**What gets imported to the agent:**
- Account xpubs (public keys only — cannot spend)
- Signer TLS certificate (for authenticated gRPC)
- Signer macaroon (for RPC auth — scope down for production)

**Threat model:**
- Compromised agent machine cannot sign transactions or extract keys
- Attacker with agent access can see balances and channel state but not spend
- Signer compromise is full compromise — secure that machine accordingly

## Standalone Model: Passphrase on Disk (Testing Only)

When running in standalone mode (`--mode standalone`), wallet credentials are
stored as files on disk for agent automation convenience:

| File | Contents | Permissions |
|------|----------|-------------|
| `~/.lnget/lnd/wallet-password.txt` | Wallet unlock passphrase | 0600 |
| `~/.lnget/lnd/seed.txt` | 24-word BIP39 mnemonic | 0600 |

**This is suitable for:**
- Testnet and signet development
- Small mainnet amounts for micropayments
- Quick agent testing where security is not a concern

**Risks:**
- Any process running as the same user can read the files
- Disk compromise exposes both passphrase and seed
- No protection against malicious software on the same machine

### Wallet Passphrase

The wallet passphrase encrypts the wallet database on disk. Without it, the
wallet cannot be unlocked and funds cannot be spent.

**Auto-unlock:** The default lnd config includes `wallet-unlock-password-file`
which reads the passphrase on startup. This means the node is operational
immediately after a restart without manual intervention.

**Manual unlock:** Remove `wallet-unlock-password-file` from `lnd.conf` to
require manual unlock via `lncli unlock` or the REST API after each restart.

### Seed Mnemonic

The 24-word seed is the master secret from which all keys are derived. With the
seed, the entire wallet can be reconstructed on any lnd instance.

**Current storage:** Plain text file at `~/.lnget/lnd/seed.txt` with mode 0600.

**To improve standalone security:**

1. **Encrypted file:** Encrypt the seed file with a separate passphrase using
   GPG or age. The agent would need the encryption passphrase only during
   wallet recovery.

2. **OS keychain:** Store the seed in the operating system's keychain (macOS
   Keychain, Linux Secret Service). Requires keychain unlock but survives
   disk inspection.

3. **Migrate to remote signer:** The recommended path. Use the
   `lightning-security-module` skill to move keys to a separate machine.

## Macaroon Security

lnd uses macaroons for API authentication. Macaroons are bearer tokens with
cryptographic capabilities — whoever holds a macaroon can exercise its
permissions.

### Built-in Macaroons

| Macaroon | Capabilities |
|----------|-------------|
| `admin.macaroon` | Full access (read, write, generate invoices, send payments) |
| `readonly.macaroon` | Read-only access (getinfo, balances, list operations) |
| `invoice.macaroon` | Create and manage invoices only |

### Macaroon Bakery: Least-Privilege Access

**Never give agents the admin macaroon in production.** Use the
`macaroon-bakery` skill to bake custom macaroons with only the permissions each
agent needs. It supports preset roles (`pay-only`, `invoice-only`, `read-only`,
`channel-admin`, `signer-only`) and custom permission sets.

```bash
# Bake a pay-only macaroon
skills/macaroon-bakery/scripts/bake.sh --role pay-only

# Inspect a macaroon's permissions
skills/macaroon-bakery/scripts/bake.sh --inspect <path-to-macaroon>
```

See the `macaroon-bakery` skill for full usage, rotation, and best practices.

### Macaroon Scoping for Remote Signer

When using the remote signer architecture, the macaroon included in the
credentials bundle grants the watch-only node access to the signer's RPC. For
production, replace the admin macaroon with a signing-only macaroon:

```bash
# On the signer machine
skills/macaroon-bakery/scripts/bake.sh --role signer-only \
    --rpc-port 10012 --lnddir ~/.lnd-signer
```

Then re-export the credentials bundle with this macaroon instead of
`admin.macaroon`.

## Production Checklist

- [x] Use remote signer (default mode) — keys never on agent machine
- [ ] Bake least-privilege macaroons for each agent role
- [ ] Replace admin macaroon in signer credentials with signing-only macaroon
- [ ] Set file permissions: `chmod 600` on all credential files
- [ ] Restrict signer RPC to specific IP addresses via firewall
- [ ] Use testnet/signet for development, mainnet only for production
- [ ] Monitor wallet balance for unexpected changes
- [ ] Keep lnd updated to latest stable release
- [ ] Backup seed on signer in a separate, secure location
- [ ] Set up macaroon rotation schedule
- [ ] Run signer on dedicated hardware or hardened VM

## Future Enhancements

- **litd accounts:** Lightning Terminal's account system for spending limits and
  fine-grained access control
- **Hardware signing devices:** Replace signer lnd with an HSM or hardware
  wallet for tamper-resistant key storage
- **Multi-party signing:** Require multiple signers for high-value transactions
  (threshold signatures)
- **Encrypted credential storage:** OS keychain integration for macaroons and
  TLS credentials
