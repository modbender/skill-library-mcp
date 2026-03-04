---
name: zerodha-kite-cli-router
description: Route natural-language trading/account queries to the correct `zerodha` CLI command with exact flags, validation constraints, and synonym mapping. Use when a user asks to view prices, place/modify/cancel orders, manage auth/profile/config, work with holdings/positions/margins/GTT/MF flows, or asks "which zerodha command should I run?"
---

# Purpose

Translate a user query in plain English into one exact `zerodha` CLI command.

Do not invent commands or flags. Use only commands defined here.

# Bootstrap: CLI Installation

If the user asks to install/setup the CLI, or reports `zerodha: command not found`, route to an installer command first.

This is the only exception to "commands must start with `zerodha`".

Install commands:

- Linux/macOS (`curl`): `curl -fsSL https://raw.githubusercontent.com/jatinbansal1998/zerodha-kite-cli/main/scripts/install.sh | sh`
- Linux/macOS (`wget`): `wget -qO- https://raw.githubusercontent.com/jatinbansal1998/zerodha-kite-cli/main/scripts/install.sh | sh`
- Windows PowerShell: `irm https://raw.githubusercontent.com/jatinbansal1998/zerodha-kite-cli/main/scripts/install.ps1 | iex`
- Windows CMD: `powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/jatinbansal1998/zerodha-kite-cli/main/scripts/install.ps1 | iex"`

Post-install verification command:

- `zerodha version`

# Global Rules

1. Always start commands with `zerodha` (except install/bootstrap commands in "Bootstrap: CLI Installation").
2. Prefer `--json` when the user asks for machine-readable output.
3. Respect global flags when provided:
   - `--profile <name>`
   - `--config <path>`
   - `--json`
   - `--debug`
4. Profile selection:
   - Most commands require an active profile (or explicit `--profile`).
   - If no profile is selected, use:
     `zerodha config profile use <name>`
5. Auth/session:
   - API data/order commands require an access token.
   - If missing, run `zerodha auth login ...`.
   - CLI auto-refreshes access token when refresh token exists.
6. Never guess missing required fields for write actions; ask for the missing values.
7. If OS is required for installation routing and missing, ask for only the OS (`linux`, `macos`, or `windows`).

# Login Flow (Multi-Message)

Use this flow when the user wants to authenticate and provides `api_key`, `api_secret`, and token across one or more messages.

Collected auth fields (can arrive in any order):

- `profile_name` (default to `default` if user does not specify)
- `api_key`
- `api_secret`
- one login mode:
  - `request_token_or_redirect_url`, or
  - `callback` (optional `callback_port`)

Rules:

1. Persist auth fields provided in earlier user messages during the same login task.
2. Ask only for missing required auth inputs for the next step.
3. Do not emit `zerodha auth login ...` until profile credentials are configured.
4. If `api_key` + `api_secret` are available and profile setup is needed, emit:
   `zerodha config profile add <profile_name> --api-key <key> --api-secret <secret> --set-active`
5. If user explicitly wants to update only one credential on an existing profile, emit:
   - `zerodha config profile set-api-key <profile_name> --api-key <key>`
   - `zerodha config profile set-api-secret <profile_name> --api-secret <secret>`
6. For token mode, emit:
   `zerodha auth login --request-token <token_or_redirect_url>`
7. For callback mode, emit:
   `zerodha auth login --callback [--callback-port <1-65535>]`
8. If multiple commands are needed, output only the next runnable command.

# Command Catalog

## Root utilities

- `zerodha version`
- `zerodha help [command]`
- `zerodha completion <shell>`

## Config profile

- `zerodha config profile add <name> --api-key <key> --api-secret <secret> [--set-active]`
  - Constraints: `<name>` required; `--api-key` and `--api-secret` required.
- `zerodha config profile set-api-key <name> --api-key <key>`
  - Constraints: `<name>`, `--api-key` required.
- `zerodha config profile set-api-secret <name> --api-secret <secret>`
  - Constraints: `<name>`, `--api-secret` required.
- `zerodha config profile list`
- `zerodha config profile use <name>`
  - Constraints: `<name>` must exist.
- `zerodha config profile remove <name>`
  - Constraints: `<name>` must exist.

## Auth

- `zerodha auth login --request-token <token_or_redirect_url>`
- `zerodha auth login --callback [--callback-port <1-65535>]`
  - Constraints:
    - Exactly one mode is required: `--request-token` OR `--callback`.
    - `--request-token` cannot be combined with `--callback`.
    - `--callback-port` allowed only with `--callback`.
    - `--callback-port` range: `1..65535`.
- `zerodha auth renew`
  - Constraints: refresh token must exist in profile.
- `zerodha auth logout`
- `zerodha auth revoke-refresh [--refresh-token <token>]`
  - If omitted, uses stored refresh token.

## Profile

- `zerodha profile show`
- `zerodha profile full`

## Quotes

- `zerodha quote get <EXCHANGE:SYMBOL> [EXCHANGE:SYMBOL...]`
  - Constraints: at least 1 instrument.
- `zerodha quote ltp <EXCHANGE:SYMBOL> [EXCHANGE:SYMBOL...]`
  - Constraints: at least 1 instrument.
- `zerodha quote ohlc <EXCHANGE:SYMBOL> [EXCHANGE:SYMBOL...]`
  - Constraints: at least 1 instrument.
- `zerodha quote historical --instrument-token <int> --interval <value> --from <time> --to <time> [--continuous] [--oi]`
  - Constraints:
    - `--instrument-token > 0`
    - `--interval` required
    - `--from` and `--to` required
    - time format: `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS` or RFC3339
    - `--from <= --to`

## Instruments

- `zerodha instruments list [--exchange <EXCHANGE> | --all]`
  - Default (no flags): summary by exchange/type.
  - Constraints: `--exchange` and `--all` are mutually exclusive.
- `zerodha instruments mf`

## Orders (single order operations)

- `zerodha order place --exchange <EX> --symbol <SYM> --txn <BUY|SELL> --type <MARKET|LIMIT|SL|SL-M> --product <CNC|MIS|NRML|MTF> --qty <n> [--price <p>] [--trigger-price <p>] [--validity <DAY|IOC|TTL>] [--validity-ttl <min>] [--variety <v>] [--tag <t>]`
  - Constraints:
    - required: `--exchange --symbol --txn --type --product --qty`
    - `--qty > 0`
    - LIMIT requires `--price > 0`
    - SL requires both `--price > 0` and `--trigger-price > 0`
    - SL-M requires `--trigger-price > 0`
    - TTL validity requires `--validity-ttl > 0`
- `zerodha order modify --order-id <id> [fields...]`
  - Constraints:
    - `--order-id` required
    - At least one modifiable field required.
    - If provided, `--txn` must be BUY/SELL; `--type` must be MARKET/LIMIT/SL/SL-M; `--validity` must be DAY/IOC/TTL.
- `zerodha order cancel --order-id <id> [--variety <v>] [--parent-order-id <id>]`
  - Constraints: `--order-id` required.
- `zerodha order exit --order-id <id> [--variety <v>] [--parent-order-id <id>]`
  - Constraints: `--order-id` required.

## Orders (orderbook/trades)

- `zerodha orders list`
- `zerodha orders show --order-id <id>`
  - Constraints: `--order-id` required.
- `zerodha orders trades [--order-id <id>]`

## Positions

- `zerodha positions`
- `zerodha positions convert --exchange <EX> --symbol <SYM> --old-product <CNC|MIS|NRML|MTF> --new-product <CNC|MIS|NRML|MTF> --position-type <day|overnight> --txn <BUY|SELL> --qty <n>`
  - Constraints:
    - all flags above required
    - `--qty > 0`

## Holdings

- `zerodha holdings`
- `zerodha holdings auctions`
- `zerodha holdings auth-initiate [--type <equity|mf>] [--transfer-type <pre|post|off|gift>] [--exec-date YYYY-MM-DD] [--isin <isin> ...] [--qty <float> ...]`
  - Constraints:
    - if `--type` set, must be `equity|mf`
    - if `--transfer-type` set, must be `pre|post|off|gift`
    - if `--exec-date` set, format must be `YYYY-MM-DD`
    - `--isin` and `--qty` must have matching counts
    - each `--qty` must be `> 0`

## Margins

- `zerodha margins [--segment <all|equity|commodity>]`
- `zerodha margins order --exchange <EX> --symbol <SYM> --txn <BUY|SELL> --type <MARKET|LIMIT|SL|SL-M> --product <CNC|MIS|NRML|MTF> --qty <n> [--price <p>] [--trigger-price <p>] [--variety <v>] [--compact]`
- `zerodha margins basket --exchange <EX> --symbol <SYM> --txn <BUY|SELL> --type <MARKET|LIMIT|SL|SL-M> --product <CNC|MIS|NRML|MTF> --qty <n> [--price <p>] [--trigger-price <p>] [--variety <v>] [--compact] [--consider-positions]`
- `zerodha margins charges --exchange <EX> --symbol <SYM> --txn <BUY|SELL> --type <MARKET|LIMIT|SL|SL-M> --product <CNC|MIS|NRML|MTF> --qty <n> --avg-price <p> [--price <p>] [--trigger-price <p>] [--variety <v>] [--order-id <id>]`
  - Shared constraints for order/basket/charges:
    - required: `--exchange --symbol --txn --type --product --qty`
    - `--qty > 0`
    - LIMIT requires `--price > 0`
    - SL requires both `--price > 0` and `--trigger-price > 0`
    - SL-M requires `--trigger-price > 0`
  - Additional charges constraint:
    - `--avg-price > 0`

## GTT

- `zerodha gtt place [gtt flags]`
- `zerodha gtt modify --trigger-id <id> [gtt flags]`
- `zerodha gtt list`
- `zerodha gtt show --trigger-id <id>`
- `zerodha gtt delete --trigger-id <id>`

GTT common flags:
- `--exchange <EX> --symbol <SYM> --last-price <p> --txn <BUY|SELL> [--product <CNC|MIS|NRML|MTF>] [--type <single|two-leg>]`
- For `single` type:
  - `--trigger <p> --limit-price <p> --qty <q>`
- For `two-leg` type:
  - `--lower-trigger <p> --lower-limit-price <p> --lower-qty <q>`
  - `--upper-trigger <p> --upper-limit-price <p> --upper-qty <q>`

GTT constraints:
- `--exchange --symbol --txn` required
- `--last-price > 0`
- `--txn` in `BUY|SELL`
- `--product` in `CNC|MIS|NRML|MTF`
- `--trigger-id > 0` for show/modify/delete

## Mutual Funds

### MF Orders

- `zerodha mf orders place --symbol <SYM> --txn <BUY|SELL> [--qty <q>] [--amount <amt>] [--tag <t>]`
  - Constraints:
    - `--symbol` and `--txn` required
    - at least one of `--qty` or `--amount` must be `> 0`
    - `--qty` and `--amount` cannot be negative
- `zerodha mf orders list [--from YYYY-MM-DD --to YYYY-MM-DD]`
  - Constraints:
    - `--from` and `--to` must be provided together
    - date format: `YYYY-MM-DD`
- `zerodha mf orders show --order-id <id>`
  - Constraints: `--order-id` required
- `zerodha mf orders cancel --order-id <id>`
  - Constraints: `--order-id` required

### MF SIPs

- `zerodha mf sips place --symbol <SYM> --amount <amt> --instalments <n> --frequency <f> [--instalment-day <1..31>] [--initial-amount <amt>] [--trigger-price <p>] [--step-up <v>] [--sip-type <v>] [--tag <t>]`
  - Constraints:
    - required: `--symbol --amount --instalments --frequency`
    - `--amount > 0`, `--instalments > 0`
    - `--instalment-day` if provided must be in `1..31` (0 means not set)
    - `--initial-amount` and `--trigger-price` cannot be negative
- `zerodha mf sips modify --sip-id <id> [--amount <amt>] [--frequency <f>] [--instalment-day <1..31>] [--instalments <n>] [--step-up <v>] [--status <v>]`
  - Constraints:
    - `--sip-id` required
    - at least one modifiable field required
    - numeric fields cannot be negative
- `zerodha mf sips cancel --sip-id <id>`
  - Constraints: `--sip-id` required
- `zerodha mf sips list`
- `zerodha mf sips show --sip-id <id>`
  - Constraints: `--sip-id` required

### MF Holdings

- `zerodha mf holdings`
- `zerodha mf holdings show --isin <isin>`
  - Constraints: `--isin` required
- `zerodha mf holdings isins`

# Synonym Map

Use these mappings during intent parsing.

## Market data

- `quote` synonyms: `price`, `live price`, `current price`, `quote`, `snapshot`
- `ltp` synonyms: `ltp`, `last traded price`, `last price`, `tick`
- `ohlc` synonyms: `open high low close`, `ohlc`, `candle snapshot`
- `historical` synonyms: `history`, `candles`, `chart data`, `time series`

## Account and auth

- `profile` synonyms: `account details`, `user profile`, `my account`
- `login` synonyms: `authenticate`, `sign in`, `connect kite`
- `renew` synonyms: `refresh access token`, `renew token`
- `logout` synonyms: `sign out`, `clear session`

## Bootstrap

- `install cli` synonyms: `install zerodha cli`, `setup zerodha cli`, `command not found`, `zerodha not installed`

## Orders and tradebook

- `order place` synonyms: `buy`, `sell`, `place order`, `new order`, `execute trade`
- `order modify` synonyms: `edit order`, `change order`, `update order`
- `order cancel` synonyms: `cancel order`, `delete order`
- `order exit` synonyms: `square off order`, `exit order`
- `orders list` synonyms: `orderbook`, `all orders`
- `orders trades` synonyms: `tradebook`, `fills`, `executed trades`

## Portfolio

- `positions` synonyms: `open positions`, `net positions`
- `positions convert` synonyms: `convert position`, `change product type`
- `holdings` synonyms: `portfolio holdings`, `stocks held`, `demat holdings`
- `holdings auctions` synonyms: `auction holdings`, `auction eligible`

## Risk/margins

- `margins` synonyms: `available margin`, `used margin`, `funds`
- `margins order` synonyms: `margin required`, `order margin estimate`
- `margins basket` synonyms: `basket margin`, `combined margin`
- `margins charges` synonyms: `brokerage estimate`, `charges`, `fees`

## GTT

- `gtt` synonyms: `good till trigger`, `trigger order`, `price alert order`
- `gtt two-leg` synonyms: `oco`, `one cancels other`, `bracket trigger`

## Mutual funds

- `mf orders` synonyms: `mutual fund order`, `fund buy/sell`
- `mf sips` synonyms: `sip`, `systematic investment plan`
- `mf holdings` synonyms: `mutual fund portfolio`, `fund holdings`

# Routing Procedure

1. Detect whether this is an install/bootstrap request, login/auth bootstrap request, or a normal `zerodha` command request.
2. For install/bootstrap: pick the OS-specific installer command.
3. For login/auth bootstrap: follow "Login Flow (Multi-Message)" and emit only the next runnable command.
4. Otherwise detect intent domain using synonyms.
5. Pick the narrowest command path.
6. Extract required entities/flags.
7. Validate against constraints above.
8. If fields are missing, ask for only missing required inputs.
9. Output one runnable command string.

# Intent to Command Defaults

- If user asks generic "install zerodha cli":
  - Linux/macOS: `curl -fsSL https://raw.githubusercontent.com/jatinbansal1998/zerodha-kite-cli/main/scripts/install.sh | sh`
  - Windows: `irm https://raw.githubusercontent.com/jatinbansal1998/zerodha-kite-cli/main/scripts/install.ps1 | iex`
- If user asks generic "login" and no auth fields are provided:
  - ask for `api_key` and `api_secret` first (profile defaults to `default` unless specified)
- If user provides `api_key` + `api_secret` but no token/mode:
  - emit profile setup command first, then ask for token mode (`--request-token` or `--callback`)
- If user asks generic "show my profile": use `zerodha profile show`.
- If user asks generic "show orders": use `zerodha orders list`.
- If user asks generic "show trades": use `zerodha orders trades`.
- If user asks generic "show positions": use `zerodha positions`.
- If user asks generic "show holdings": use `zerodha holdings`.
- If user asks generic "show margins": use `zerodha margins --segment all`.
- If user asks "list instruments" without exchange: use `zerodha instruments list`.

# Output Contract For Downstream Agents

When responding with a routed command, return:

1. `command`: exact runnable command (installer command for bootstrap, otherwise `zerodha ...`)
2. `why`: one-line reason
3. `missing`: required fields still missing (empty if none)
