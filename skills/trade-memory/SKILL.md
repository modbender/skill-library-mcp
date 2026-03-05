---
name: trade-memory
version: 1.0.0
description: Save a trade or signal event to local memory log file (trades.jsonl). Use when a trade signal is confirmed and needs to be recorded, saved, or logged for future reference and history tracking.
metadata:
  {
    "openclaw":
      {
        "emoji": "🧠",
        "requires": { "bins": ["python3"] },
      },
  }
---

# Trade Memory

Append confirmed trade signals or executed trades to a local JSONL log file for persistent memory and history tracking.

## When to Use

- User says: "simpan trade ini"
- User says: "catat sinyal BTC tadi"
- User says: "log trade BUY BTC entry 94500"
- Agent wants to record a signal after btc-analyzer returns a result
- User says: "tambahkan ke trade history"

## How It Works

This skill runs a local Python script that:
1. Accepts a JSON object as input (symbol, side, entry, sl, tp, note, source, ts).
2. Validates the input is proper JSON.
3. Appends the trade as a single line to trades.jsonl (creates file and directory if not exists).
4. Returns a JSON confirmation object.

## Workflow

Step 1 — Collect trade data from user or agent:
- symbol: trading pair (e.g. BTCUSDT)
- side: BUY or SELL
- entry: entry price (number)
- sl: stop loss price (number)
- tp: take profit price (number)
- note: optional description or reason
- source: origin of signal (e.g. btc-analyzer, manual, telegram)
- ts: ISO timestamp (auto-filled if not provided)

Step 2 — Run the save script via bash tool:
python3 ~/.npm-global/lib/node_modules/openclaw/skills/trade-memory/save.py '<JSON_INPUT>'

Step 3 — Confirm to user that trade was saved successfully.

## Input Format

{
  "symbol": "BTCUSDT",
  "side": "BUY",
  "entry": 94500,
  "sl": 94000,
  "tp": 95500,
  "note": "sweep+fvg signal, RSI 58",
  "source": "btc-analyzer",
  "ts": "2026-02-23T00:00:00Z"
}

## Output Format

{"ok": true, "path": "/home/windows_11/.openclaw/polymarket-workspace/trades.jsonl", "appended": 1, "trade": {...}}

## Log File Location

/home/windows_11/.openclaw/polymarket-workspace/trades.jsonl

Each line is one JSON object representing one trade event.

## Error Handling

If input is not valid JSON:
{"ok": false, "error": "Invalid JSON: <error detail>"}

## Guardrails

- Always APPEND to the file, never overwrite existing trades.
- Create directory and file automatically if they do not exist.
- Always run the script — never simulate or fake a save confirmation.
- Timestamp (ts) is auto-generated in UTC if not provided by user.
- Output must be JSON only.
