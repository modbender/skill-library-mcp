# EasyClaw User DEX Env Reference

This skill is self-contained. Configure env in `easyclaw-skill/.env`.

## Required

- `SOLANA_RPC_URL` or `ANCHOR_PROVIDER_URL`
- `KEYPAIR_PATH` or `ANCHOR_WALLET`

## Optional Program ID Overrides

- `ORDER_ENGINE_PROGRAM_ID`
- `MARKET_REGISTRY_PROGRAM_ID`

If omitted, scripts use embedded defaults:

- `ORDER_ENGINE_PROGRAM_ID=GpMobZUKPtEE1eiZQAADo2ecD54JXhNHPNts5kPGwLtb`
- `MARKET_REGISTRY_PROGRAM_ID=BsA8fuyw8XqBMiUfpLbdiBwbKg8MZMHB1jdZzjs7c46q`

## `balance` Command

No additional env needed.

```bash
./scripts/dex-agent.sh balance
./scripts/dex-agent.sh balance --json
```

## `order` Command Options

Required:

- `--market-id <u64>`
- `--margin <u64>`

Optional:

- `--side buy|sell` (default: `buy`)
- `--type market|limit` (default: `market`)
- `--price <u64>` (required for limit)
- `--ttl <i64>` (default: `300`)
- `--client-order-id <u64>` (default: current unix seconds)
- `--reduce-only`
- `--deposit <u64>` (deposit collateral before placing order)
- `--skip-create-position` (do not auto-create user market position PDA)

Example:

```bash
./scripts/dex-agent.sh order --market-id 1 --side buy --type market --margin 1000000
```

## Backend API / WS Env

- `EASYCLAW_API_BASE_URL` (default: `http://127.0.0.1:8080`)
- `EASYCLAW_WS_URL` (default: derived from `EASYCLAW_API_BASE_URL` + `/ws`)
- `EASYCLAW_API_TOKEN` (optional, used for protected `/v1/*` endpoints)

## `backend` Command

Use backend REST APIs for:

- market/user data: positions, orders, fills, position history, orderbook heatmap, chart candles
- platform data: trades, portfolio, leaderboard, system status
- authenticated controls: agent/strategy/session/risk management and kill switch (`EASYCLAW_API_TOKEN` required)

```bash
./scripts/dex-agent.sh backend doctor
./scripts/dex-agent.sh backend health
./scripts/dex-agent.sh backend chart-candles --market BTCUSDT --timeframe 1m --limit 120
./scripts/dex-agent.sh backend positions --mine --limit 20
./scripts/dex-agent.sh backend position-history --mine --limit 20
./scripts/dex-agent.sh backend orderbook-heatmap --exchange binance --symbol BTCUSDT --limit 30
./scripts/dex-agent.sh backend orderbook-heatmap-aggregated --symbol-key BTCUSDT --limit 30
./scripts/dex-agent.sh backend trades --agent-id agent-001 --limit 50
./scripts/dex-agent.sh backend portfolio --period 7d
./scripts/dex-agent.sh backend leaderboard --metric pnl_pct --period 7d --min-trades 20
./scripts/dex-agent.sh backend system-status

# agent controls (auth required)
./scripts/dex-agent.sh backend agent-create --name "Momentum-01" --strategy-id strategy-001 --risk-profile-json '{"max_position_usdc":10000,"daily_loss_limit_usdc":500,"kill_switch_enabled":true}'
./scripts/dex-agent.sh backend agent --agent-id agent-001
./scripts/dex-agent.sh backend agent-owner-binding --agent-id agent-001
./scripts/dex-agent.sh backend agent-session-start --agent-id agent-001 --mode paper
./scripts/dex-agent.sh backend agent-session-stop --agent-id agent-001 --session-id sess-001
./scripts/dex-agent.sh backend agent-risk --agent-id agent-001
./scripts/dex-agent.sh backend agent-risk-patch --agent-id agent-001 --max-position-usdc 12000 --kill-switch-enabled true
./scripts/dex-agent.sh backend kill-switch --all

# strategy controls (auth required)
./scripts/dex-agent.sh backend strategy-templates
./scripts/dex-agent.sh backend strategy-create --name "My Strategy" --entry-rules-json '{}' --exit-rules-json '{}' --risk-defaults-json '{}'
./scripts/dex-agent.sh backend strategy --strategy-id strategy-001
./scripts/dex-agent.sh backend strategy-patch --strategy-id strategy-001 --name "My Strategy v2"
./scripts/dex-agent.sh backend strategy-publish --strategy-id strategy-001
```

## `watch` Command (WebSocket)

Subscribe to realtime channels from backend `/ws`.

```bash
./scripts/dex-agent.sh watch --channel system.status
./scripts/dex-agent.sh watch --channels "agent.signals,portfolio.updates"
./scripts/dex-agent.sh watch --channel market.price.BTCUSDT --json
./scripts/dex-agent.sh watch --channel chart.ticks.BTCUSDT --json
```

## `autotrade` Command

Subscribe to realtime signal channel and execute orders automatically.

```bash
./scripts/dex-agent.sh autotrade --market-id 1 --margin 1000000 --min-confidence 0.75
./scripts/dex-agent.sh autotrade --market-id 1 --margin 1000000 --dry-run
```

Notes:

- `autotrade` now retries websocket connections automatically on disconnect.
- `--strategy-file <path>` or `--strategy <text>` lets the runner include strategy rationale in execution reports.

## `onboard` Command

Guided flow for user onboarding:

1. discover/select wallet keypair
2. print wallet address for platform registration
3. wait for user confirmation (`done`)
4. collect/save strategy prompt to `state/strategies/`
5. ask final confirmation
6. start `autotrade` with reconnect + order rationale reporting

```bash
./scripts/dex-agent.sh onboard --market-id 1 --margin 1000000
./scripts/dex-agent.sh onboard --wallet-path ~/.config/solana/id.json --market-id 1 --margin 1000000 --dry-run
```
