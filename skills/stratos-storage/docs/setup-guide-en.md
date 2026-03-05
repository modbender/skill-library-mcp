# Stratos SDS Resource Node Setup Guide

## Prerequisites

- ppd v0.12.11 installed (verify with `ppd version`)
- Go 1.19+
- Stable network connection
- STOS tokens (for node activation)

## 1. Initialize the Node

```bash
mkdir -p ~/rsnode && cd ~/rsnode
ppd config -w -p
```

Interactive prompts:

| Prompt | Description |
|--------|-------------|
| Wallet nickname | A name for your wallet, e.g. `main1` |
| Password | Wallet password (enter twice to confirm) |
| BIP39 mnemonic | Press Enter to generate a new wallet; paste 24 words to recover an existing one |
| HD-path | Press Enter for default `m/44'/606'/0'/0/0` |
| P2P key password | Password for the P2P key |
| P2P generation method | Select `1) From the wallet` |

**Important: Back up your 24-word mnemonic phrase. It cannot be recovered if lost.**

## 2. Configuration Reference

The configuration file is located at `~/rsnode/config/config.toml`.

### [version]

| Parameter | Default | Description |
|-----------|---------|-------------|
| `app_ver` | `12` | Application version number |
| `min_app_ver` | `11` | Minimum compatible version; connections from lower versions are rejected |
| `show` | `"v0.12.11"` | Version display string |

### [blockchain]

| Parameter | Default | Description |
|-----------|---------|-------------|
| `chain_id` | `"stratos-1"` | Chain ID; `stratos-1` for mainnet |
| `gas_adjustment` | `1.5` | Gas estimation multiplier |
| `insecure` | `false` | Whether to use unencrypted connection |
| `grpc_server` | `"grpc.thestratos.org:443"` | Chain gRPC endpoint |

### [home]

| Parameter | Default | Description |
|-----------|---------|-------------|
| `accounts_path` | `"./accounts"` | Directory for wallet and P2P key files |
| `download_path` | `"./download"` | Directory for downloaded files |
| `peers_path` | `"./peers"` | Directory for peer list |
| `storage_path` | `"./storage"` | Directory for stored files |

### [keys]

| Parameter | Description |
|-----------|-------------|
| `p2p_address` | P2P address (`stsds` prefix), auto-generated during init |
| `p2p_password` | P2P key password |
| `wallet_address` | Wallet address (`st` prefix), auto-generated during init |
| `wallet_password` | Wallet password |
| `beneficiary_address` | Address for receiving mining rewards; defaults to `wallet_address` |

### [node]

| Parameter | Default | Description |
|-----------|---------|-------------|
| `debug` | `false` | Enable debug logging |
| `max_disk_usage` | `7629394` | Maximum disk usage in MB; adjust based on available disk space |

### [node.connectivity] (Key Section)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `internal` | `false` | Whether the node is on an internal network. Set to `true` for local testing |
| `network_address` | `""` | **Required.** External IP address. Use `127.0.0.1` for local testing |
| `network_port` | `"18081"` | Main communication port; must be open to the internet |
| `metrics_port` | `"18152"` | Prometheus metrics port |
| `rpc_port` | `"18252"` | JSON-RPC API port |
| `rpc_namespaces` | `"user,owner"` | RPC namespaces to enable |

### [node.connectivity.seed_meta_node]

| Parameter | Description |
|-----------|-------------|
| `p2p_address` | Initial meta node P2P address |
| `p2p_public_key` | Initial meta node public key |
| `network_address` | Initial meta node network address |

> Defaults point to official meta nodes. Usually no changes needed.

### [streaming]

| Parameter | Default | Description |
|-----------|---------|-------------|
| `internal_port` | `"18452"` | SPFS internal HTTP port (used by the OpenClaw plugin) |
| `rest_port` | `"18552"` | REST API port |

### [traffic]

| Parameter | Default | Description |
|-----------|---------|-------------|
| `log_interval` | `10` | Traffic logging interval in seconds |
| `max_connections` | `1000` | Maximum concurrent connections |
| `max_download_rate` | `0` | Download rate limit (0 = unlimited) |
| `max_upload_rate` | `0` | Upload rate limit (0 = unlimited) |

### [monitor]

| Parameter | Default | Description |
|-----------|---------|-------------|
| `tls` | `false` | Enable TLS |
| `cert_file_path` | `""` | TLS certificate path |
| `key_file_path` | `""` | TLS private key path |
| `port` | `"18352"` | Monitor WebSocket port |
| `allowed_origins` | `"localhost"` | IPs allowed to connect to monitor |

### [web_server]

| Parameter | Default | Description |
|-----------|---------|-------------|
| `path` | `"./web"` | Web server files directory |
| `port` | `"18652"` | Web server port |
| `token_on_startup` | `false` | Auto-enter monitor token on startup |

## 3. Essential Configuration Changes

After initialization, edit the config file:

```bash
vim ~/rsnode/config/config.toml
```

**Must change:**

```toml
[node.connectivity]
# For local testing
internal = true
network_address = '127.0.0.1'

# For a public node, use your external IP
# internal = false
# network_address = 'YOUR_PUBLIC_IP'
```

**Recommended:**

```toml
[node]
# Adjust based on available disk (in MB), example for 500GB
max_disk_usage = 512000
```

## 4. Start the Node

```bash
# Recommended: use tmux to keep it running in background
tmux new -s rsnode
cd ~/rsnode
ppd start
```

## 5. Activate the Node

Open ppd terminal in a separate session:

```bash
cd ~/rsnode
ppd terminal
```

Run the following commands in order:

```
# 1. Register to meta node
rp

# 2. Stake and activate (minimum 1600 STOS)
activate 1600stos 0.01stos

# 3. Start mining
startmining
```

> Ensure your wallet has sufficient STOS tokens before activation.

## 6. Port Summary

| Port | Purpose |
|------|---------|
| 18081 | Main communication (must be open) |
| 18152 | Prometheus metrics |
| 18252 | JSON-RPC API |
| 18352 | Monitor WebSocket |
| 18452 | SPFS HTTP API (used by OpenClaw plugin) |
| 18552 | REST API |
| 18652 | Web management UI |

## 7. FAQ

**Q: How do I check my wallet address?**
Run `wallets` in ppd terminal.

**Q: Node can't connect?**
Verify port 18081 is open in your firewall and `network_address` is correct.

**Q: OpenClaw plugin connection failed?**
Confirm the `streaming.internal_port` (default 18452) is accessible, and check `STRATOS_SPFS_GATEWAY` in `skill.json`.
