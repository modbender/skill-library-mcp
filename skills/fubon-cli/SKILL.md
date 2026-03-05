---
name: fubon-cli
description: AI-agent skill for Taiwan stock/futures/options operations via fubon-cli. Use this skill whenever the user asks about Fubon Neo login, order placement, account/inventory queries, market quote or candle retrieval, realtime subscription, conditional orders, or wants natural-language trading assistance through fubon ask/chat. Trigger even when the user does not explicitly say "fubon-cli" but mentions command-line automation for Fubon trading workflows, JSON trading outputs, or scripted order operations.
compatibility:
  tools: terminal
  runtime: python>=3.8
---

# fubon-cli Skill

Use this skill to execute `fubon` commands safely and return parseable results for downstream automation.

## What This Skill Does

- Executes `fubon-cli` command groups end to end.
- Keeps command usage aligned with actual CLI behavior.
- Returns standardized JSON output and error handling guidance.
- Supports order lifecycle workflows: login -> query -> place order -> verify -> adjust/cancel.

## When To Use

Use this skill if the user asks for any of these intents:

- Login/logout/session status for Fubon Neo.
- Place or manage stock/futures/options orders.
- Query inventory, unrealized PnL, settlement, balances, margin quota.
- Read market quotes, candles, trade details, movers, actives, snapshots, history.
- Subscribe to realtime market or callback streams.
- Manage conditional orders.
- Use natural language to produce trading commands (`fubon ask`, `fubon chat`).

## Preconditions

1. Install platform wheel for `fubon_neo`.
2. Install `fubon-cli`.
3. Ensure certificate files and account credentials are available.

Example:

```bash
pip install ./wheels/fubon_neo-2.2.8-cp37-abi3-win_amd64.whl
pip install fubon-cli
```

## Core Workflow

1. Authenticate first.
2. Run requested query or order action.
3. Inspect `success` and `error` keys.
4. If placing an order, run follow-up query to confirm state.

```bash
fubon login --id <ID> --password <PW> --cert-path <PATH> --cert-password <CERT_PW>
fubon market quote 2330
fubon stock buy 2330 1000 --price 580
fubon stock orders
```

## Command Map

### Auth

```bash
fubon login --id <ID> --password <PW> --cert-path <PATH> [--cert-password <PW>]
fubon login status
fubon login logout
```

## Command Surface

The `Command Surface` below lists the primary CLI entrypoints and example usages. These map 1:1 to the `fubon-cli` commands and are safe to invoke from automation when preconditions are met.

See the examples in the `Command Map` section for concrete invocations.

### Stock

```bash
fubon stock buy <SYMBOL> <QTY> --price <PRICE>
fubon stock sell <SYMBOL> <QTY> --price <PRICE>
fubon stock orders
fubon stock cancel <ORDER_NO>
fubon stock modify-price <ORDER_NO> <NEW_PRICE>
fubon stock modify-quantity <ORDER_NO> <NEW_QTY>
```

### Account

```bash
fubon account inventory
fubon account unrealized
fubon account settlement
fubon account margin-quota <SYMBOL>
```

### Market

```bash
fubon market quote <SYMBOL>
fubon market ticker <SYMBOL>
fubon market candles <SYMBOL> --timeframe 5
fubon market trades <SYMBOL> --limit 50
fubon market snapshot TSE
fubon market movers TSE --direction up
fubon market actives TSE --trade volume
fubon market history <SYMBOL> --from 2024-01-01 --to 2024-06-30
```

### Realtime

```bash
fubon realtime subscribe <SYMBOL>
fubon realtime callbacks
```

### Futures and Options

```bash
fubon futopt buy TXF202406 1 --price 20000
fubon futopt sell TXF202406 1 --price 20100
fubon futopt orders
```

### Conditional Orders

```bash
fubon condition create --payload '{"symbol":"2330","trigger":{}}'
fubon condition list
fubon condition cancel <CONDITION_ID>
```

### AI

```bash
fubon ask "台積電現在的價格是多少？"
fubon chat
fubon config set openai-key <OPENAI_KEY>
fubon config show
```

## Output Contract

Non-streaming commands:

```json
{
  "success": true,
  "data": {}
}
```

Failure example:

```json
{
  "success": false,
  "error": "Error message"
}
```

Streaming commands output JSONL (one JSON object per line).

## Execution Rules

1. Never assume login state; check status or handle not-logged-in errors.
2. For orders, always confirm with `fubon stock orders` or equivalent query command.
3. For retriable failures (network/transient), retry conservatively once.
4. For parameter or auth failures, stop and surface exact `error` text.

## Safety Boundaries

- Do not expose raw credentials in logs or chat output.
- Encourage verification of symbol, quantity, price, and account index before order placement.
- Prefer non-production or low-risk validation paths for first-time automation.

## Release Binding

This skill is version-bound with `fubon-cli`.

- `scripts/validate_skill_doc.py` validates coverage.
- `scripts/build_skill_bundle.py` builds skill artifact.
- `scripts/publish_skill.py` publishes to clawhub endpoint.
- CI/CD should publish skill after package release to keep tool and skill synchronized.

## Version Binding

This skill's version must be kept in sync with the `fubon-cli` package version. The CI/CD pipeline is configured to build and publish the skill bundle immediately after a successful package release so the skill metadata (`skill.manifest.json`) and `SKILL.md` match the released package.

- Use `scripts/build_skill_bundle.py` to create `dist/skill` artifacts tied to the current git tag or package version.
- Use `scripts/publish_skill.py` (requires `CLAWHUB_API_TOKEN`) to publish the bundle to the skill registry.
