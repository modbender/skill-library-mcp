---
name: optionshawk
description: Options flow analysis, unusual activity detection, and strategy
  evaluation for equities and ETFs.
---


# OptionsHawk

Options flow analysis, unusual activity detection, and strategy evaluation for equities and ETFs.

## What it does

OptionsHawk monitors and analyzes options market activity to surface actionable trading intelligence, including:

- **Unusual activity detection** — identify large or out-of-the-ordinary options trades that may signal institutional positioning or informed flow
- **Flow analysis** — track put/call ratios, volume vs open interest, and net premium by strike and expiration
- **Sweep detection** — flag aggressive multi-exchange sweep orders that indicate urgency from large buyers
- **Strategy identification** — recognize spreads, straddles, strangles, and other multi-leg structures in the flow
- **Earnings plays** — analyze pre-earnings options positioning, implied move vs historical move, and skew shifts

## Usage

Ask your agent to analyze options flow and activity:

- "Show me the biggest unusual options activity today across all equities"
- "What is the put/call ratio and net premium flow for AAPL this week?"
- "Alert me when there are sweep orders over $1M on any tech stock"
- "Analyze the options skew for TSLA heading into earnings"
- "What are the most active strikes and expirations for SPY right now?"

## Configuration

Set the following environment variables:

- `OPTIONSHAWK_API_KEY` — API key for OptionsHawk. Used to authenticate requests for options flow data, unusual activity alerts, and strategy analysis.
- `OPTIONSHAWK_ALERT_THRESHOLD` — (optional) minimum premium in USD to trigger unusual activity alerts. Defaults to `500000`.
