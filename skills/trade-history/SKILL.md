---
name: trade-history
version: 1.0.0
description: Read and display recent trade history from local JSONL log file. Use when asked about past trades, trade recap, performance review, or to list recorded signals.
metadata:
  {
    "openclaw":
      {
        "emoji": "📋",
        "requires": { "bins": ["python3"] },
      },
  }
---

# Trade History

Read and display recorded trade events from the local trades.jsonl log file, with optional filtering by symbol and configurable limit.

## When to Use

- User asks: "tampilkan trade history"
- User asks: "trade apa saja yang sudah dicatat?"
- User asks: "recap trade BTC terakhir"
- User asks: "lihat 10 trade terakhir"
- User asks: "ada berapa trade yang tersimpan?"

## How It Works

This skill runs a local Python script that:
1. Reads the local trades.jsonl file line by line.
2. Parses each line as a JSON object.
3. Filters by symbol if specified.
4. Sorts results newest first (reverse chronological).
5. Returns up to N records (default 20).
6. Returns a JSON object with count and items array.

## Workflow

Step 1 — Run the read script via bash tool:
python3 ~/.npm-global/lib/node_modules/openclaw/skills/trade-history/read.py

Step 2 — Parse the JSON output (count + items array).

Step 3 — Present the trade list to the user in a readable format:
- Show each trade: symbol, side, entry, sl, tp, note, timestamp
- Mention total count
- Newest trades first

## Optional Arguments

Run with JSON args to filter or limit results:
python3 ~/.npm-global/lib/node_modules/openclaw/skills/trade-history/read.py '{"limit": 10, "symbol": "BTCUSDT"}'

Supported args:
- limit: number of trades to return (default 20)
- symbol: filter by trading pair (e.g. BTCUSDT)

## Output Format

{
  "count": 3,
  "items": [
    {
      "symbol": "BTCUSDT",
      "side": "BUY",
      "entry": 94500,
      "sl": 94000,
      "tp": 95500,
      "note": "sweep+fvg signal",
      "source": "btc-analyzer",
      "ts": "2026-02-23T00:00:00Z"
    }
  ]
}

## Log File Location

/home/windows_11/.openclaw/polymarket-workspace/trades.jsonl

## Error Handling

If log file does not exist yet:
{"count": 0, "items": []}

No error is thrown — returns empty result gracefully.

## Guardrails

- Always run the script — never fabricate trade history.
- If file is missing, return empty list gracefully without error.
- Output must be JSON only from the script.
- Always display newest trades first (reverse chronological order).
- Never delete or modify the log file — read only.
