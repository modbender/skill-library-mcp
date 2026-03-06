---
name: entradex
description: Use the EntradeX CLI for DNSE workflows. Use when (1) setting DNSE API credentials via env vars or config file, (2) reading account, market, and order data, (3) placing, modifying, or canceling real trades.
metadata:
  openclaw:
    requires:
      bins:
        - entradex
      env:
        - DNSE_API_KEY
        - DNSE_API_SECRET
    primaryEnv: DNSE_API_KEY
    install:
      - kind: node
        package: entradex-cli
        bins:
          - entradex
        label: Install EntradeX CLI (npm)
    homepage: https://www.npmjs.com/package/entradex-cli
---

# EntradeX CLI

Install

```bash
npm i -g entradex-cli
```

## Usage

```bash
entradex [global-options] [command]
```

## Configuration

Credential priority order:

1. Config file (`~/.entradex-cli/config.json`) - recommended
2. Environment variables (`DNSE_API_KEY`, `DNSE_API_SECRET`)
3. Global command options (`--api-key`, `--api-secret`)

Setup and inspect config:

```bash
entradex config set --key "<api-key>" --secret "<api-secret>"
entradex config set
entradex config get
entradex config clear
```

## Security & Safety

**Before using this skill:**

- Verify the npm package: `npm view entradex-cli` - check author is `hieuhani` and repository matches
- Inspect package contents: `npm pack entradex-cli --dry-run` or view on [npmjs.com](https://www.npmjs.com/package/entradex-cli)
- Treat `DNSE_API_KEY` and `DNSE_API_SECRET` as highly sensitive trading credentials

**Autonomous execution warning:**

- This skill can place **real trades** using provided credentials
- Consider using a separate limited-permission account
- Rotate API keys if you suspect unauthorized access

## Global Options

- `--api-key <key>` DNSE API key
- `--api-secret <secret>` DNSE API secret
- `--base-url <url>` API base URL (default: `https://openapi.dnse.com.vn`)
- `--debug` Show request details
- `-V, --version` Show CLI version
- `-h, --help` Show help

## Commands

### Config

```bash
entradex config set [--key <key>] [--secret <secret>] [--url <url>]
entradex config get
entradex config clear
```

### Account

```bash
entradex account list
entradex account balances <accountNo>
entradex account loan-packages <accountNo> <marketType> [--symbol <symbol>]
```

### Trade

```bash
entradex trade order <marketType> <symbol> <side> <orderType> <price> <quantity> <tradingToken> [--price-stop <price>]
entradex trade modify <accountNo> <orderId> <marketType> <symbol> <side> <orderType> <price> <quantity> <tradingToken> [--price-stop <price>]
entradex trade cancel <accountNo> <orderId> <marketType> <tradingToken>
```

Parameters:

- `marketType` (enum): `STOCK`, `DERIVATIVE`
- `side` (enum): `NB` (buy), `NS` (sell)
- `orderType` (enum): `ATO`, `ATC`, `LO`, `MTL`, `MOK`, `PLO`
  - `ATO`: At The Opening
  - `ATC`: At The Close
  - `LO`: Limit Order
  - `MTL`: Market To Limit
  - `MOK`: Market Order Kill
  - `PLO`: Post Limit Order
- `price` (number): unit price; follow DNSE tick-size/market constraints
  - If `orderType=LO`, `price` must be greater than `0`.
  - If `orderType` is anything other than `LO` (`ATO`, `ATC`, `MTL`, `MOK`, `PLO`), `price` must be exactly `0`.
- `quantity` (integer): order quantity; must satisfy market lot rules
  - For `marketType=STOCK`, valid quantity is either:
    - Board lot: multiples of 100 (`100`, `200`, ...)
    - Odd lot: integers from `1` to `99`
  - For `marketType=STOCK`, values like `101`, `102`, ... are invalid odd lots and must be rejected.
- `tradingToken` (string): token from `entradex auth create-token`

Normalization rules for user intent:

- If user says `buy`/`sell`, map to `NB`/`NS`.
- Uppercase enum-style params before execution (`marketType`, `side`, `orderType`).
- If user provides an unsupported enum value, stop and ask for a valid value.
- If `orderType` is not supported by the target market/session, stop and ask user to choose a supported type.

### Order

```bash
entradex order list <accountNo> <marketType>
entradex order detail <accountNo> <orderId> <marketType>
entradex order history <accountNo> <marketType> [--from <date>] [--to <date>] [--page-size <size>] [--page-index <index>]
entradex order deals <accountNo> <marketType>
```

### Market

```bash
entradex market secdef <symbol> [--board-id <id>]
entradex market ppse <accountNo> <marketType> <symbol> <price> <loanPackageId>
```

### Auth

```bash
entradex auth send-otp <email> [--otp-type <type>]
entradex auth create-token <otpType> <passcode>
```

### Dry Run

```bash
entradex dry-run accounts
entradex dry-run balances <accountNo>
entradex dry-run order <marketType> <symbol> <side> <orderType> <price> <quantity> [--price-stop <price>]
```

## Common Workflow

```bash
# 1) Configure credentials
entradex config set

# 2) Send OTP
entradex auth send-otp user@example.com

# 3) Create trading token with passcode
entradex auth create-token smart_otp <passcode>

# 4) Place an order
entradex trade order STOCK VIC NB LO 15000 100 <trading-token>
```
