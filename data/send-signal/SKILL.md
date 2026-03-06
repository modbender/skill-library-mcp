---
name: SendTradeSignal
description: A specialized tool for sending quantitative trading signals to the FMZ platform via HTTP API.
---

# SendTradeSignal (FMZ Connector)

## Overview
This skill serves as a bridge between the OpenClaw AI agent and the FMZ Quantum Trading Platform. It enables the AI to execute trade decisions (Buy/Sell/Wait) programmatically by sending structured JSON signals to a specific robot instance running on FMZ.

## Features
- **Real-time Signal Transmission:** Sends trading commands instantly upon AI decision.
- **Secure Communication:** Uses a user-defined UUID to verify the source of the signal, preventing unauthorized access.
- **Structured Data:** Transmits comprehensive trade details including action type, target symbol (e.g., BTC_USDT), reference price, and reasoning.
- **HTTP/HTTPS Support:** Compatible with standard web protocols for broad compatibility.

## Usage
The AI should invoke this tool when a market analysis concludes with a definitive trading action.

### Parameters
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `action` | string | The specific trading action to take. Accepted values: `buy`, `sell`, `wait`, `close`. |
| `symbol` | string | The trading pair symbol, formatted as `BASE_QUOTE` (e.g., `BTC_USDT`, `ETH_USDT`). |
| `price` | float | The current market price or limit price for the order. |
| `reason` | string | A brief explanation of why this trade decision was made (e.g., "RSI overbought", "Breaking support"). |

## Example
When the AI detects a buying opportunity for Bitcoin at 65000 USDT due to a positive trend:

```python
handler(
    action="buy",
    symbol="BTC_USDT",
    price=65000.0,
    reason="MACD golden cross detected on 4H chart."
)
