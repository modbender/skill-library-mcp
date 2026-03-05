---
name: macaroon-bakery
description: Bake, inspect, and manage lnd macaroons for least-privilege agent access. Use when an agent needs scoped credentials — pay-only, invoice-only, read-only, or custom permissions. Also covers signer macaroon scoping and macaroon rotation.
---

# Macaroon Bakery

Bake custom lnd macaroons so every agent gets only the permissions it needs.
Never hand out `admin.macaroon` in production — bake a scoped one instead.

## Quick Start

```bash
# Bake a pay-only macaroon
skills/macaroon-bakery/scripts/bake.sh --role pay-only

# Bake an invoice-only macaroon
skills/macaroon-bakery/scripts/bake.sh --role invoice-only

# Bake a read-only macaroon
skills/macaroon-bakery/scripts/bake.sh --role read-only

# Inspect any macaroon
skills/macaroon-bakery/scripts/bake.sh --inspect ~/.lnd/data/chain/bitcoin/mainnet/admin.macaroon

# List all available lnd permissions
skills/macaroon-bakery/scripts/bake.sh --list-permissions
```

### Docker

The litd container is auto-detected. You can also specify `--container`:

```bash
# Auto-detect litd container (default)
skills/macaroon-bakery/scripts/bake.sh --role pay-only

# Explicit container
skills/macaroon-bakery/scripts/bake.sh --role pay-only --container litd

# Inspect a macaroon inside a container
skills/macaroon-bakery/scripts/bake.sh --inspect /root/.lnd/data/chain/bitcoin/testnet/admin.macaroon --container litd
```

### Remote Nodes

To bake macaroons on a remote lnd node, provide the connection credentials:

```bash
# Bake a pay-only macaroon on a remote node
skills/macaroon-bakery/scripts/bake.sh --role pay-only \
    --rpcserver remote-host:10009 \
    --tlscertpath ~/remote-tls.cert \
    --macaroonpath ~/remote-admin.macaroon \
    --save-to ~/remote-pay-only.macaroon
```

You need lncli installed locally and copies of the node's TLS cert and a macaroon
with `macaroon:generate` permission (typically admin.macaroon).

## Preset Roles

| Role | What the agent can do | Cannot do |
|------|----------------------|-----------|
| `pay-only` | Pay invoices, decode invoices, get node info | Create invoices, open channels, see balances |
| `invoice-only` | Create invoices, lookup invoices, get node info | Pay, open channels, see wallet balance |
| `read-only` | Get info, balances, list channels/peers/payments | Pay, create invoices, open/close channels |
| `channel-admin` | All of read-only + open/close channels, connect peers | Pay invoices, create invoices |
| `signer-only` | Sign transactions, derive keys (for remote signer) | Everything else |

## Baking Custom Macaroons

For permissions not covered by presets, bake a custom macaroon:

```bash
# Custom: agent can only pay and check wallet balance
skills/macaroon-bakery/scripts/bake.sh --custom \
    uri:/lnrpc.Lightning/SendPaymentSync \
    uri:/lnrpc.Lightning/DecodePayReq \
    uri:/lnrpc.Lightning/WalletBalance \
    uri:/lnrpc.Lightning/GetInfo

# Custom with explicit output path
skills/macaroon-bakery/scripts/bake.sh --custom \
    uri:/lnrpc.Lightning/AddInvoice \
    uri:/lnrpc.Lightning/GetInfo \
    --save-to ~/my-agent.macaroon
```

## Discovering Permissions

```bash
# List all available URI permissions
skills/macaroon-bakery/scripts/bake.sh --list-permissions

# Filter for specific service
skills/macaroon-bakery/scripts/bake.sh --list-permissions | grep -i invoice

# Filter for routing-related permissions
skills/macaroon-bakery/scripts/bake.sh --list-permissions | grep -i router
```

## Inspecting Macaroons

```bash
# See what permissions a macaroon has
skills/macaroon-bakery/scripts/bake.sh --inspect <path-to-macaroon>

# Inspect the admin macaroon to see full permissions
skills/macaroon-bakery/scripts/bake.sh --inspect ~/.lnd/data/chain/bitcoin/mainnet/admin.macaroon
```

## Signer Macaroon Scoping

When using the `lightning-security-module` skill, the credentials bundle includes
`admin.macaroon` by default. For production, bake a signing-only macaroon on the
signer machine:

```bash
# On the signer container
skills/macaroon-bakery/scripts/bake.sh --role signer-only \
    --container litd-signer --rpc-port 10012

# Or on a native signer
skills/macaroon-bakery/scripts/bake.sh --role signer-only \
    --rpc-port 10012 --lnddir ~/.lnd-signer

# Then re-export the credentials bundle with the scoped macaroon
```

## Macaroon Rotation

Rotate macaroons regularly to limit the window if one is compromised:

```bash
# 1. Bake a new macaroon with the same role
skills/macaroon-bakery/scripts/bake.sh --role pay-only --save-to ~/pay-only-v2.macaroon

# 2. Update your agent config to use the new macaroon

# 3. Delete the old macaroon's root key (invalidates it)
skills/lnd/scripts/lncli.sh bakemacaroon --root_key_id 0
# Note: use lncli listmacaroonids and deletemacaroonid for fine-grained control
```

## Best Practices

- **One macaroon per agent role.** Don't share macaroons between agents with
  different responsibilities.
- **Never use admin.macaroon in production.** It's the master key.
- **Inspect before deploying.** Always verify what a baked macaroon can do.
- **Rotate on a schedule.** Monthly for production, immediately if compromised.
- **Scope signer macaroons too.** The remote signer's credentials bundle should
  use `signer-only`, not `admin`.
- **Store with 0600 permissions.** Macaroons are bearer tokens — treat like passwords.

## Common Permission URIs

| Permission | Description |
|-----------|-------------|
| `uri:/lnrpc.Lightning/GetInfo` | Node info (version, pubkey, sync status) |
| `uri:/lnrpc.Lightning/WalletBalance` | On-chain wallet balance |
| `uri:/lnrpc.Lightning/ChannelBalance` | Lightning channel balance |
| `uri:/lnrpc.Lightning/ListChannels` | List open channels |
| `uri:/lnrpc.Lightning/ListPeers` | List connected peers |
| `uri:/lnrpc.Lightning/SendPaymentSync` | Pay a Lightning invoice |
| `uri:/lnrpc.Lightning/DecodePayReq` | Decode a BOLT11 invoice |
| `uri:/lnrpc.Lightning/AddInvoice` | Create a Lightning invoice |
| `uri:/lnrpc.Lightning/LookupInvoice` | Look up an invoice by hash |
| `uri:/lnrpc.Lightning/ListInvoices` | List all invoices |
| `uri:/lnrpc.Lightning/ListPayments` | List all payments |
| `uri:/lnrpc.Lightning/ConnectPeer` | Connect to a peer |
| `uri:/lnrpc.Lightning/OpenChannelSync` | Open a channel |
| `uri:/lnrpc.Lightning/CloseChannel` | Close a channel |
| `uri:/signrpc.Signer/SignOutputRaw` | Sign a transaction output |
| `uri:/signrpc.Signer/ComputeInputScript` | Compute input script for signing |
| `uri:/signrpc.Signer/MuSig2Sign` | MuSig2 signing |
| `uri:/walletrpc.WalletKit/DeriveKey` | Derive a key |
| `uri:/walletrpc.WalletKit/DeriveNextKey` | Derive next key in sequence |
