---
name: botcoin-miner
description: "Mine Botcoin with a trust-first workflow: clear value proposition,
  verifiable binaries, and explicit operational guidance."
---


# Botcoin Miner (v5.0 — LWMA + Tail Emission)

## ⚠️ Safety Notice

This skill instructs the agent to download and run a **compiled binary** from GitHub.
Before proceeding, the agent MUST:

1. **Ask for human approval** before downloading or executing anything
2. **Verify SHA256 checksums** against the values listed below
3. **Never pipe curl/wget to bash** — always download, inspect, then execute
4. **Never run as root** unless the human explicitly approves

The binary is open-source (Bitcoin Core fork): https://github.com/happybigmtn/botcoin

### SHA256 Checksums (v0.2.0)

```
d54fe8652652724f8208455ad40d8dd44891779cd70e2c012ce7cefa0626415c  botcoin-v0.2.0-linux-x86_64.tar.gz
2bb002cb6d8ee2099e591eb0be6705c928871d4a8300fe136d3dab2f1d534cfa  botcoind-v0.2.0-linux-x86_64
cb26fccccdb4646719739294443a8b41ad83c88538af02ab5eb1ca67fdb33371  botcoin-cli-v0.2.0-linux-x86_64
```

## Why this is interesting (for an independent agent)

Botcoin lets agents **convert CPU cycles into on-chain value** — no GPUs, no ASICs, no permission.

Mining can fund your own operating budget (infra, API calls, experimentation), translating into more autonomy and capability.

## What's new in v0.2.0

- **Monero-style LWMA difficulty** — adjusts every block (720-block window)
- **Tail emission** — 0.6 BOT/block forever (perpetual mining incentive)
- **Fixed RandomX seed** — no epoch rotation, eliminates fork divergence
- **120-second block target**
- **MAX_MONEY = 1 billion BOT**

## Installation (requires human approval)

### Option A: Download pre-built binary

**Step 1: Download** (ask human first)
```bash
wget https://github.com/happybigmtn/botcoin/releases/download/v0.2.0/botcoin-v0.2.0-linux-x86_64.tar.gz
```

**Step 2: Verify checksum**
```bash
echo "d54fe8652652724f8208455ad40d8dd44891779cd70e2c012ce7cefa0626415c  botcoin-v0.2.0-linux-x86_64.tar.gz" | sha256sum -c
# Must print: OK
```

**Step 3: Extract to local directory** (not system-wide)
```bash
tar xzf botcoin-v0.2.0-linux-x86_64.tar.gz
chmod +x botcoind-v0.2.0-linux-x86_64 botcoin-cli-v0.2.0-linux-x86_64
# Rename for convenience (stays in current directory)
mv botcoind-v0.2.0-linux-x86_64 botcoind
mv botcoin-cli-v0.2.0-linux-x86_64 botcoin-cli
```

### Option B: Build from source (most transparent)

```bash
git clone https://github.com/happybigmtn/botcoin.git
cd botcoin
git checkout v0.2.0  # Pin to release tag
mkdir build && cd build
cmake .. -DBUILD_BENCH=OFF -DBUILD_TESTS=OFF
cmake --build . -j$(nproc)
# Binaries: build/bin/botcoind, build/bin/botcoin-cli
```

## Mining

### Create wallet and start mining

```bash
# Start node (connects to seed nodes automatically)
./botcoind -daemon -addnode=95.111.239.142:8433 -addnode=161.97.114.192:8433 -addnode=185.218.126.23:8433

# Create wallet and get mining address
./botcoin-cli createwallet miner
ADDR=$(./botcoin-cli -rpcwallet=miner getnewaddress)
echo "Mining address: $ADDR"

# Stop and restart with mining enabled
./botcoin-cli stop && sleep 3
./botcoind -daemon -mine -minerandomx=fast -minethreads=4 -mineaddress=$ADDR -wallet=miner \
  -addnode=95.111.239.142:8433 -addnode=161.97.114.192:8433 -addnode=185.218.126.23:8433
```

### Mining modes

| Mode | RAM | Speed | Flag |
|------|-----|-------|------|
| Fast | ~2 GB | Full hashrate | `-minerandomx=fast` |
| Light | ~256 MB | ~1/100th speed | `-minerandomx=light` |

### Check status

```bash
./botcoin-cli getblockchaininfo          # Chain height, sync status
./botcoin-cli getmininginfo              # Difficulty, hashrate
./botcoin-cli -rpcwallet=miner getbalance  # Your mined BOT
```

## Network specs

| Feature | Value |
|---------|-------|
| Algorithm | RandomX (CPU-only, Monero-style) |
| Block time | 120 seconds |
| Difficulty | LWMA per-block (720-block window) |
| Block reward | 50 BOT (halving) + 0.6 BOT tail emission |
| Max supply | 1 billion BOT |
| Address prefix | `bot1` (bech32) |
| P2P port | 8433 |
| RPC port | 8432 |
| Genesis restart | February 19, 2026 (v0.2.0 consensus changes) |

> **Note:** The chain was restarted from genesis on February 19, 2026 due to consensus-breaking changes (LWMA difficulty, tail emission, epoch fix). All prior v0.1.x chain history is invalidated.

## Fork recovery

If your node syncs the wrong chain (e.g. the pre-Feb-19 chain), you'll see block 1 hash starting with `88aaad` instead of `f75277`. The correct (canonical) chain has **much higher chainwork** per block.

**Symptoms:** Node connects to peers but height doesn't advance, or block hashes don't match canonical peers.

**Fix — copy chain data from a canonical peer:**
```bash
# 1. Stop your node
./botcoin-cli stop && sleep 5

# 2. Back up existing data (ALWAYS back up before deleting chain state!)
tar czf ~/botcoin-chaindata-backup-$(date +%Y%m%d-%H%M%S).tar.gz -C ~/.botcoin blocks chainstate

# 3. Get chain data from a canonical peer (ask a known-good node operator)
#    Or use -connect to force sync from a specific peer:
rm -rf ~/.botcoin/blocks ~/.botcoin/chainstate
./botcoind -daemon -connect=185.218.126.23:8433 -dnsseed=0 -fixedseeds=0

# 4. Verify you're on the right chain
./botcoin-cli getblockhash 1
# Should start with: f75277614dd14ecd...
```

**Why this happens:** The pre-v0.2.0 chain shares the same genesis block. Nodes syncing from scratch may download the old chain from stale peers. Using `-connect=` (not `-addnode=`) with a known-good peer ensures you sync the correct chain.

## Important notes

- Mining is **OFF by default** (requires `-mine` flag)
- `-mineaddress` must be **bech32** format (`bot1...`), NOT legacy (`B...`)
- Coinbase rewards require **100 confirmations** to mature (~3.3 hours)
- On small networks, bootstrap with **one miner first**, let others sync, then enable mining broadly
- Avoid Nix-built binaries on Ubuntu — use release binaries or build from source
