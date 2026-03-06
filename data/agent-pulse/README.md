# Agent Pulse — OpenClaw Skill 💓

On-chain liveness signaling for autonomous agents on Base.

## Quick Start

```bash
# 1. Configure
export PRIVATE_KEY="0x..."
./scripts/setup.sh --auto-approve

# 2. Send a pulse
./scripts/pulse.sh --direct 1000000000000000000

# 3. Check status
./scripts/status.sh 0xYourAddress

# 4. Auto-pulse (cron)
./scripts/auto-pulse.sh
```

## Read-Only (No Private Key)

```bash
# Check any agent's status — no wallet needed
./scripts/status.sh 0xAnyAddress
./scripts/monitor.sh --feed
./scripts/health.sh
```

## Requirements

- `curl`, `jq` — API calls and JSON parsing
- `cast` (Foundry) — on-chain transactions
- `PRIVATE_KEY` env var — agent wallet key (write operations only)

## Scripts

| Script          | Purpose                                | Needs PRIVATE_KEY? |
|-----------------|----------------------------------------|-------------------|
| `setup.sh`      | Auto-detect wallet, check balance, configure | Yes |
| `pulse.sh`      | Send on-chain pulse                    | Yes |
| `auto-pulse.sh` | Cron-safe heartbeat (skips if alive)   | Yes |
| `status.sh`     | Check one agent's status               | No |
| `monitor.sh`    | Check multiple agents or view feed     | No |
| `config.sh`     | Protocol configuration                 | No |
| `health.sh`     | Protocol health check                  | No |

## Security

- `--auto-approve` sets a **bounded allowance** (1,000 PULSE) — not unlimited.
- `pulse.sh --direct` approves the exact amount per transaction.
- Use a **dedicated wallet** with minimal funds, not your main wallet.
- Start with `--dry-run` to verify behavior first.

## Network

- **Chain:** Base (8453)
- **PULSE Token:** `0x21111B39A502335aC7e45c4574Dd083A69258b07`
- **PulseRegistry:** `0xe61C615743A02983A46aFF66Db035297e8a43846`
- **API:** https://x402pulse.xyz

See `SKILL.md` for full documentation.
