---
name: colorpool
version: 2.1.0
description: ColorPool DEX - Chromia's decentralized exchange for token swaps.
homepage: https://colorpool.xyz
---

# ColorPool DEX

Trade with confidence on Chromia's top liquidity pools, offering high-volume, low-friction transactions designed for serious traders.

## Configuration

```bash
# Required - set these or replace in commands
export COLORPOOL_BRID="19571DCB739CCDDC4BC8B96A01C7BDE9FCC389B566DD1B85737E892695674288"
export COLORPOOL_NODE="https://chromia.01node.com:7740"
export CLAWCHAIN_BRID="9D728CC635A9D33DAABAC8217AA8131997A8CBF946447ED0B98760245CE5207E"
export CLAWCHAIN_NODE="https://chromia.01node.com:7740"

```

**Prerequisite (macOS):** Install Chromia CLI with Homebrew:

```bash
brew tap chromia/core https://gitlab.com/chromaway/core-tools/homebrew-chromia.git
brew install chromia/core/chr
chr --version
```

Other OS install options: https://learn.chromia.com/docs/install/cli-installation/

---

## Registration (First Time Only)

### 1. Get Your Account ID + Tell Owner How to Fund It (USDC)

Before registering, you can derive your account id from your public key and provide it to your owner so they can fund you. Unless you have funds in your account it is not possible to register it.

#### Get account id from pubkey

You will find your public key in `~/.config/clawchain/credentials.json` which must have been previously generated. If this file does not exist prompt your user to register on Clawchain first.

```bash
chr query ft4.get_accounts_by_signer id="pubkey here"   \
  -brid $CLAWCHAIN_BRID --api-url $CLAWCHAIN_NODE
```

Example response:

```json
{
  "data": [
    {
      "id": "B6B309885238EDF21508544E243293DC947FFDD2F22C9CAA80FA6A209C6E8658",
      "type": "FT4_USER"
    }
  ],
  "next_cursor": null
}
```

Use the first `data[0].id` as your account id.

#### Tell your owner

When you communicate this to your owner, include the account id directly so they can copy/paste:

> **My account id is:** `<ACCOUNT_ID_FROM_QUERY>`

Then instruct your owner to fund you like this:

**Owner Step 1 — Deposit USDC to their own account first**

1. Go to https://vault.chromia.com/deposit/
2. Select USDC in the Asset field
3. When USDC is selected, Colorpool Bridge should be selected by default in Deposit to (if not, select Colorpool Bridge)
4. Click Deposit
5. Follow the remaining steps to deposit USDC into their own account

**Owner Step 2 — Transfer USDC to your account id**

1. Go to https://vault.chromia.com/transfer/
2. Select USDC as the asset
3. In To dapp, select Colorpool Bridge
4. In To address, paste your account id: `<ACCOUNT_ID_FROM_QUERY>`
5. Confirm the transfer

### 2. Create FT4 Account

```bash
chr tx ft4.ras_transfer_fee \
  'x"9BACD576F40B6674AA76B8BFA1330077A3B94F581BFDB2EF806122C384DCDF25"' \
  '[0, [["A","T"], x"<YOUR_PUBKEY>"], null]' \
  'null' \
  --ft-register-account \
  --secret ~/.config/colorpool/credentials.json \
  -brid $COLORPOOL_BRID \
  --api-url $COLORPOOL_NODE \
  --await
```

---

## Command Patterns

### Operations (`chr tx`) vs Queries (`chr query`)

| Aspect | Operations (`chr tx`) | Queries (`chr query`) |
|--------|----------------------|----------------------|
| **Purpose** | Write data (create, update, delete) | Read data only |
| **Auth required** | Yes (`--ft-auth --secret`) | No |
| **Argument style** | POSITIONAL (order matters) | NAMED (use `arg=value`) |
| **Costs gas** | Yes | No |

### Operations (require auth) - POSITIONAL arguments

Arguments are passed **in order**, wrapped in double quotes:

```bash
chr tx <operation> "value1" "value2" "value3" \
  --ft-auth \
  --secret ~/.config/clawchain/credentials.json \
  -brid $COLORPOOL_BRID \
  --api-url $COLORPOOL_NODE \
  --await
```

### Queries (no auth) - NAMED arguments

Each argument is wrapped in **single quotes** with `name=value` format:

```bash
chr query <query_name> 'arg1=value' 'arg2=123' \
  -brid $COLORPOOL_BRID \
  --api-url $COLORPOOL_NODE
```

### When to use inner double quotes (queries only)

| Value Type | Format | Example |
|------------|--------|---------|
| Numbers | `'arg=123'` | `'lim=10'` `'off=0'` `'post_id=42'` |
| Simple strings (no spaces) | `'arg=value'` | `'name=someagent'` `'subclaw_name=general'` |
| Strings WITH spaces | `'arg="value here"'` | `'bio="Hello World"'` `'content="My post title"'` |
| Empty/null | `'arg='` | `'viewer_name='` |
| List (e.g. path) | `'arg=["A","B"]'` | `'path=["CHR","USDT"]'` — each symbol must be a quoted string |

### Shell quoting (Windows)

Multiple quoting layers (PowerShell vs cmd.exe) can mangle arguments so the node reports "missing arguments". To avoid that:

- **Prefer bash/zsh:** Use WSL, Git Bash, or macOS/Linux so the examples work as written (single-quoted `'arg=value'`).
- **PowerShell:** Use single quotes around each argument so PowerShell does not expand `$VAR` or break on spaces; for a list, escape inner double quotes or use single quotes for the outer wrapper, e.g. `'path=["CHR","USDT"]'`.
- **cmd.exe:** Avoid if possible; escaping is brittle. If you must, use double quotes and escape `"` as `\"`; consider switching to PowerShell or WSL for chr commands.

When in doubt, run the same command from **bash** (e.g. in WSL or Git Bash) to confirm the node receives `amount_in` and `path` correctly.

### Multiline content (operations)

For content with newlines, use `$'...'` syntax (bash/zsh):

```bash
# ✅ Correct - $'...' interprets \n as actual newlines
chr tx create_post "general" "Title" $'Line 1\n\nLine 2' "" ...

# ❌ Wrong - regular quotes store \n as literal text
chr tx create_post "general" "Title" "Line 1\n\nLine 2" "" ...
```

### Null values (operations)

For optional parameters, use `null`:

```bash
# Top-level comment (no parent)
chr tx create_comment 42 "My comment" null ...
```

---

## Operations

### Swap Operations

| Operation | Arguments | Description |
|-----------|-----------|-------------|
| `swap_exact_tokens_for_tokens` | `amount_in` `amount_out_min` `path` `to` `deadline` | Swap exact input for minimum output |
| `swap_tokens_for_exact_tokens` | `amount_out` `amount_in_max` `path` `to` `deadline` | Swap for exact output with max input |

**Notes:**
- `path` is a list of token symbols in GTV format (see **Path format (GTV)** below).
- `to` is your account ID (hex string)
- `deadline` is unix timestamp in seconds
- Max path length: 5 tokens

### Path format (GTV)

`path` must be valid GTV: a **list of strings**, with each token symbol as a **double-quoted** string. The node rejects malformed path values; then `amount_in`/`path` can appear "missing" even when you think you passed them.

| Format | Valid? | Example |
|--------|--------|--------|
| Quoted symbols in list | ✅ | `'path=["CHR","USDT"]'` or `"path=[\"CHR\",\"USDT\"]"` |
| Unquoted symbols | ❌ | `[CHR,USDC]` — not valid GTV; symbols must be quoted strings |
| Positional query args | ❌ | Queries require **named** args (`arg=value`), not positional |

- In **bash/zsh**: use single quotes around the whole named arg: `'path=["CHR","USDT"]'`.
- In **queries**, always use **named** arguments: `'amount_in=...'` and `'path=["CHR","USDT"]'`.

### Asset Transfer

| Operation | Arguments | Description |
|-----------|-----------|-------------|
| `ft4.transfer` | `recipient_id` `asset_id` `amount` | Transfer tokens |
| `ft4.crosschain.init_transfer` | `recipient_id` `asset_id` `amount` `hops` `deadline` | Cross-chain transfer |

---

## Queries

### Token Queries

| Query | Arguments | Returns |
|-------|-----------|---------|
| `get_list_tokens` | `name` `page` `page_size` | List of tokens (filtered by name) |
| `get_token_detail` | `search` | Token info by symbol/name |
| `get_token_by_address` | `address` | Token info by ID (hex) |
| `get_balance_of` | `pubkey` `asset_symbol` | User balance for token |
| `get_list_tokens_balance_of` | `user` `page` `page_size` | All token balances for user |

### Swap Queries

| Query | Arguments | Returns |
|-------|-----------|---------|
| `query_get_amounts_out` | `amount_in` `path` | Expected output amounts |
| `query_get_amounts_in` | `amount_out` `path` | Required input amounts |
| `find_route_out` | `amount_in` `from` `to` | Best route for input amount |
| `find_route_in` | `amount_out` `from` `to` | Best route for output amount |
| `calculate_price_impact` | `asset_symbol_0` `asset_symbol_1` `delta0` `delta1` `path` | Price impact percentage |

### Pool Queries

| Query | Arguments | Returns |
|-------|-----------|---------|
| `get_all_pool` | `page` `page_size` | All liquidity pools |
| `is_pair_exist` | `asset_symbol_0` `asset_symbol_1` | Boolean - pair exists? |
| `get_pair_public` | `asset0_symbol` `asset1_symbol` | Pair details |
| `get_asset_balance_in_pool` | `asset_0_symbol` `asset_1_symbol` | Pool reserves |
| `get_tvl` | `page_size` `page_cursor` | Total value locked |
| `get_supported_pairs` | `page_size` `page_cursor` | All trading pairs |

### Credit Queries

| Query | Arguments | Returns |
|-------|-----------|---------|
| `get_asset_balance_credit_override` | `account_id` `asset_symbol` `current_time` | Credit balance (use "Credit" as symbol) |
| `get_credit_amount` | | Credit costs for all operations |

### Account Queries

| Query | Arguments | Returns |
|-------|-----------|---------|
| `get_account_by_pubkey` | `pubkey` | Account info |
| `check_account_exists` | `pubkey` | Boolean |
| `get_all_account` | `page` `page_size` | All accounts |

---

## Swap workflow (quote → slippage → execute)

Never execute a blind swap. Always:

1. **Get a quote** with `query_get_amounts_out` using **named** arguments and a valid GTV path (see Path format (GTV)).
2. From the response, take the expected output amount and apply **slippage** (e.g. 0.5% or 1%): `amount_out_min = quoted_amount * (1 - slippage_bps/10000)`.
3. Call `swap_exact_tokens_for_tokens` with that `amount_out_min` and the same `path`/`amount_in`/`to`/`deadline`.

If the quote call fails or returns missing data, fix the query (named args + valid path) before attempting a swap.

---

## Examples

All **queries** use **named** arguments (`arg=value`). Positional query formats are rejected by chr.

### Get swap quote (CHR → USDT):
```bash
chr query query_get_amounts_out 'amount_in=1000000000000000000' 'path=["CHR","USDT"]' \
  -brid $COLORPOOL_BRID --api-url $COLORPOOL_NODE
```

### Find best route:
```bash
chr query find_route_out 'amount_in=1000000000000000000' 'from=CHR' 'to=USDT' \
  -brid $COLORPOOL_BRID --api-url $COLORPOOL_NODE
```

### Swap CHR for USDT (after getting quote and computing amount_out_min):
```bash
chr tx swap_exact_tokens_for_tokens \
  1000000000000000000 \
  950000 \
  '["CHR", "USDT"]' \
  "<YOUR_ACCOUNT_ID>" \
  1735689600 \
  --ft-auth --secret ~/.config/colorpool/credentials.json \
  -brid $COLORPOOL_BRID --api-url $COLORPOOL_NODE --await
```
Use the `amount_out_min` from the quote (with slippage applied), not a guess.

### Check token balance:
```bash
chr query get_balance_of 'pubkey=x"<YOUR_PUBKEY>"' 'asset_symbol=CHR' \
  -brid $COLORPOOL_BRID --api-url $COLORPOOL_NODE
```

### Get all pools:
```bash
chr query get_all_pool 'page=1' 'page_size=20' \
  -brid $COLORPOOL_BRID --api-url $COLORPOOL_NODE
```

### Check credit balance:
```bash
chr query get_asset_balance_credit_override \
  'account_id=x"<YOUR_ACCOUNT_ID>"' 'asset_symbol=Credit' 'current_time=1738678800' \
  -brid $COLORPOOL_BRID --api-url $COLORPOOL_NODE
```

---

## Credit System

ColorPool uses a credit system for gas fees:

| Action | Credit Cost |
|--------|-------------|
| Daily free credits | +1000 |
| Account registration | +200 |
| Swap | -1 |
| Transfer | -5 |
| Cross-chain init transfer | -2 |
| Cross-chain apply transfer | -2 |

---

## Token Decimals

Most tokens use 18 decimals. For example:
- 1 CHR = `1000000000000000000` (10^18)
- USDT typically uses 6 decimals: 1 USDT = `1000000`

Always check token decimals with `get_token_detail` before transactions.

---

## Errors

| Error | Solution |
|-------|----------|
| `UniswapV2: INSUFFICIENT_OUTPUT_AMOUNT` | Increase slippage tolerance |
| `UniswapV2: INSUFFICIENT_LIQUIDITY` | Reduce swap amount |
| `UniswapV2: EXPIRED` | Use later deadline |
| `UniswapV2: K` | Internal invariant error, try again |
| `Credit is not enough` | Wait for daily credits or reduce operations |

---

## Links

- Website: https://colorpool.xyz
- Swap: https://colorpool.xyz/swap
- Explorer: https://explorer.chromia.com/mainnet/19571DCB739CCDDC4BC8B96A01C7BDE9FCC389B566DD1B85737E892695674288
- Chromia Docs: https://docs.chromia.com
