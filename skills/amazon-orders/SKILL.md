---
name: amazon-orders
description: Download and query your Amazon order history via an unofficial Python API and CLI.
homepage: https://github.com/alexdlaird/amazon-orders
metadata: {"clawdbot":{"emoji":"📦","requires":{"bins":["python3","pip3"],"env":["AMAZON_USERNAME", "AMAZON_PASSWORD", "AMAZON_OTP_SECRET_KEY"]}}}
---

# amazon-orders Skill

Interact with your Amazon.com order history using the unofficial `amazon-orders` Python package and CLI.

> Note: `amazon-orders` works by scraping/parsing Amazon's consumer website, so it can break if Amazon changes their pages. Only the English Amazon **.com** site is officially supported. 

## Setup

### Install / upgrade
```bash
python3 -m pip install --upgrade amazon-orders
```
(Install details and version pinning guidance are in the project README.) 

### Authentication options

`amazon-orders` can get credentials from (highest precedence first): environment variables, parameters passed to `AmazonSession`, or a local config. 

Environment variables:
```bash
export AMAZON_USERNAME="you@example.com"
export AMAZON_PASSWORD="your-password"
# Optional: for accounts with OTP/TOTP enabled
export AMAZON_OTP_SECRET_KEY="BASE32_TOTP_SECRET"
```
(OTP secret key usage is documented by the project.) 

## Usage

You can use `amazon-orders` either as a **Python library** or from the **command line**. 

### Python: basic usage

```python
from amazonorders.session import AmazonSession
from amazonorders.orders import AmazonOrders

amazon_session = AmazonSession("<AMAZON_EMAIL>", "<AMAZON_PASSWORD>")
amazon_session.login()

amazon_orders = AmazonOrders(amazon_session)

# Orders from a specific year
orders = amazon_orders.get_order_history(year=2023)

# Or use a time filter for recent orders
orders = amazon_orders.get_order_history(time_filter="last30")     # Last 30 days
orders = amazon_orders.get_order_history(time_filter="months-3")   # Past 3 months

for order in orders:
    print(f"{order.order_number} - {order.grand_total}")
```


#### Full details (slower, more fields)
Some order fields only populate when you request full details; enable it when you need richer order data:
- Python: `full_details=True`
- CLI: `--full-details` on `history` 

### CLI: common commands

```bash
# Authenticate (interactive / uses env vars if set)
amazon-orders login

# Order history
amazon-orders history --year 2023
amazon-orders history --last-30-days
amazon-orders history --last-3-months
```


### Tips

- If your account has MFA enabled, prefer setting `AMAZON_OTP_SECRET_KEY` for automated runs. 
- When automating, keep credentials out of shell history: use environment variables and a secret manager (1Password, Vault, GitHub Actions secrets, etc.).

## Examples

### Export yearly history to JSON
```bash
amazon-orders history --year 2023 --full-details > orders_2023.json
```

### Quick totals check (requires jq)
```bash
amazon-orders history --last-30-days --full-details   | jq -r '.[] | [.order_number, .grand_total] | @tsv'
```

## Notes

- This is an unofficial scraper-based tool (no official Amazon API). 
- Official docs are hosted on Read the Docs for advanced usage and APIs (Orders, Transactions, etc.). 
