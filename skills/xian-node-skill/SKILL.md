---
name: xian-node
description: Set up and manage Xian blockchain nodes. Use when deploying a Xian node to join mainnet/testnet, creating a new Xian network, or managing running nodes. Covers Docker-based setup via xian-stack, CometBFT configuration, and node monitoring.
---

# Xian Node Skill

Deploy and manage [Xian](https://xian.org) blockchain nodes — an L1 with native Python smart contracts on CometBFT.

## Quick Reference

| Task | Command |
|------|---------|
| Join mainnet | `make setup && make core-build && make core-up && make init && make configure CONFIGURE_ARGS='--genesis-file-name genesis-mainnet.json --seed-node-address <seed> --copy-genesis'` |
| Start node | `make core-shell` then `make up` inside container |
| View logs | `pm2 logs --lines 100` (inside container) |
| Stop node | `make down` (inside container) or `make core-down` (stop container) |
| Check sync | `curl -s localhost:26657/status \| jq '.result.sync_info'` |

## Setup: Join Existing Network

### 1. Clone and Build

```bash
git clone https://github.com/xian-network/xian-stack.git
cd xian-stack
make setup CORE_BRANCH=mainnet CONTRACTING_BRANCH=mainnet
make core-build
make core-up
```

### 2. Initialize CometBFT

```bash
make init
```

### 3. Configure Node

**Mainnet:**
```bash
make configure CONFIGURE_ARGS='--moniker "my-node" --genesis-file-name "genesis-mainnet.json" --seed-node-address "c3861ffd16cf6708aef6683d3d0471b6dedb3116@152.53.18.220" --copy-genesis'
```

**Testnet:**
```bash
make configure CONFIGURE_ARGS='--moniker "my-node" --genesis-file-name "genesis-testnet.json" --seed-node-address "<testnet-seed>" --copy-genesis'
```

**Validator node** (add private key):
```bash
make configure CONFIGURE_ARGS='--moniker "my-validator" --genesis-file-name "genesis-mainnet.json" --validator-privkey "<your-privkey>" --seed-node-address "..." --copy-genesis'
```

**Service node** (with BDS - Blockchain Data Service):
```bash
make configure CONFIGURE_ARGS='--moniker "my-service" --genesis-file-name "genesis-mainnet.json" --seed-node-address "..." --copy-genesis --service-node'
```

### 4. Start Node

```bash
make core-shell   # Enter container
make up           # Start pm2 processes
pm2 logs          # Watch sync progress
exit              # Leave shell (node keeps running)
```

## Setup: Create New Network

### 1. Build Stack

```bash
git clone https://github.com/xian-network/xian-stack.git
cd xian-stack
make setup CORE_BRANCH=mainnet CONTRACTING_BRANCH=mainnet
make core-build
make core-up
make init
```

### 2. Generate Validator Keys

Inside container (`make core-shell`):

```bash
# Generate new validator key
python -c "
from nacl.signing import SigningKey
import secrets
sk = SigningKey(secrets.token_bytes(32))
print(f'Private key: {sk.encode().hex()}')
print(f'Public key:  {sk.verify_key.encode().hex()}')
"
```

### 3. Create Genesis File

Create `genesis.json` with initial validators and state. See `references/genesis-template.md`.

### 4. Configure as Genesis Validator

```bash
make configure CONFIGURE_ARGS='--moniker "genesis-validator" --genesis-file-name "genesis-custom.json" --validator-privkey "<privkey>"'
```

### 5. Start Network

```bash
make core-shell
make up
```

Other nodes join using your node as seed.

## Node Management

### Inside Container Commands

| Command | Description |
|---------|-------------|
| `make up` | Start xian + cometbft via pm2 |
| `make down` | Stop all pm2 processes |
| `make restart` | Restart node |
| `make logs` | View pm2 logs |
| `make wipe` | Clear node data (keeps config) |
| `make dwu` | Down + wipe + init + up (full reset) |

### Monitoring

**Sync status:**
```bash
curl -s localhost:26657/status | jq '.result.sync_info'
```

**Response fields:**
- `latest_block_height`: Current height
- `catching_up`: `true` if still syncing
- `earliest_block_height`: Lowest available block

**Node info:**
```bash
curl -s localhost:26657/status | jq '.result.node_info'
make node-id   # Get node ID for peering
```

**Validators:**
```bash
curl -s localhost:26657/validators | jq '.result.validators'
```

### Docker Commands

| Command | Description |
|---------|-------------|
| `make core-up` | Start container |
| `make core-down` | Stop container |
| `make core-shell` | Enter container shell |
| `make core-bds-up` | Start with BDS (PostgreSQL + GraphQL) |

## Ports

| Port | Service |
|------|---------|
| 26656 | P2P (peering) |
| 26657 | RPC (queries) |
| 26660 | Prometheus metrics |
| 5000 | GraphQL (BDS only) |

## Troubleshooting

**Database lock error** (`resource temporarily unavailable`):
```bash
# Duplicate pm2 processes - clean up:
pm2 delete all
make up
```

**Sync stuck**:
```bash
# Check peer connections
curl -s localhost:26657/net_info | jq '.result.n_peers'

# Verify seed node is reachable
make wipe
make init
# Re-run configure with correct seed
```

**Container not starting**:
```bash
make core-down
make core-build --no-cache
make core-up
```

## File Locations

| Path | Contents |
|------|----------|
| `.cometbft/` | CometBFT data + config |
| `.cometbft/config/genesis.json` | Network genesis |
| `.cometbft/config/config.toml` | Node configuration |
| `.cometbft/data/` | Blockchain data |
| `xian-core/` | Xian ABCI application |
| `xian-contracting/` | Python contracting engine |

## Test Your Node

After syncing, verify your node works with [xian-py](https://github.com/xian-network/xian-py):

```bash
pip install xian-py
```

```python
from xian_py import Xian, Wallet

# Connect to your local node
xian = Xian('http://localhost:26657')

# Query balance
balance = xian.get_balance('your_address')
print(f"Balance: {balance}")

# Get contract state
state = xian.get_state('currency', 'balances', 'some_address')
print(f"State: {state}")

# Create wallet and send transaction
wallet = Wallet()  # or Wallet('your_private_key')
xian = Xian('http://localhost:26657', wallet=wallet)
result = xian.send(amount=10, to_address='recipient_address')
```

For full SDK docs (contracts, HD wallets, async) — see [xian-py](https://github.com/xian-network/xian-py).

## Resources

- [xian-network/xian-stack](https://github.com/xian-network/xian-stack) — Docker setup
- [xian-network/xian-core](https://github.com/xian-network/xian-core) — Core node
- [xian-network/xian-py](https://github.com/xian-network/xian-py) — Python SDK
- [CometBFT docs](https://docs.cometbft.com/) — Consensus engine
- [xian.org](https://xian.org) — Project site
