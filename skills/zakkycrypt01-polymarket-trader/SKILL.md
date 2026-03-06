---
name: Polymarket Trader Skill
description: "name: polymarkettrader description: A skill to securely execute
  trades on the Polymarket CLOB via a Python script. tools:"
---


---
name: polymarket_trader
description: A skill to securely execute trades on the Polymarket CLOB via a Python script.
tools:
  - name: place_polymarket_order
    description: Places a limit order on a specified Polymarket market.
    args:
      - name: market_slug
        type: string
        description: The slug of the market (e.g., 'trump-out-as-president-by-march-31').
      - name: direction
        type: string
        description: "The outcome to bet on. Must be 'Yes' or 'No'."
      - name: price
        type: number
        description: The price for the limit order (e.g., 0.50). Must be between 0.01 and 0.99.
      - name: size
        type: number
        description: The size of the order in shares (e.g., 10).
    exec:
      # This command chain securely passes arguments as environment variables to the script
      # after activating the virtual environment. This prevents shell injection vulnerabilities.
      command: >
        source ../../polymarket_venv/bin/activate &&
        export MARKET_SLUG='{{market_slug}}' &&
        export DIRECTION='{{direction}}' &&
        export PRICE={{price}} &&
        export SIZE={{size}} &&
        python trade.py
---

# Polymarket Trader Skill

This skill provides a tool to place trades on Polymarket.

## Security

This skill is designed to be secure. It reads the private key from the `POLYMARKET_PRIVATE_KEY` environment variable and reads all trade parameters as environment variables to prevent shell injection.

## Setup

This skill requires a Python virtual environment named `polymarket_venv` located in the OpenClaw workspace root.

The environment must have the following packages installed:
- `py-clob-client`
- `requests`

It also requires the `POLYMARKET_PRIVATE_KEY` environment variable to be set for the OpenClaw user.

## Tools

### `place_polymarket_order`

This tool is a wrapper around the `trade.py` script. It allows the agent to place trades by providing the market slug, direction, price, and size.
