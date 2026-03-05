# Skill: advisory-council

## CRITICAL RULE — NO FABRICATION
**You MUST actually execute the Python command using your shell/exec tool.** Read the real output. NEVER generate fake advisor analyses, fake synthesis, or simulated council responses. If the script fails, report the actual error to Boss Man.

## Purpose
Run the Advisory Council — a multi-perspective market analysis that spawns 5 AI advisors (The Skeptic, The Macro Bull, The Risk Manager, The Technical Analyst, The Contrarian) powered by MiniMax M2.5, then synthesizes their views into one actionable report. Cost: ~$0.006 per run.

## When to Use
- Boss Man asks "what does the council think?" or "run the advisory council"
- Any request for multi-perspective market analysis
- "Should I buy/sell X?" — run the council for a balanced view
- Morning protocol or end-of-day analysis requests
- Boss Man asks to focus analysis on a specific coin

## Run Full Advisory Council (All Assets)
Fetches live prices for BTC, ETH, XRP, SUI and runs all 5 advisors + synthesis.
```bash
cd ~/clawd && python3 advisory_council.py
```

## Run Focused on a Specific Coin
Runs the full council but focuses analysis on one asset.
```bash
cd ~/clawd && python3 advisory_council.py SUI
```
```bash
cd ~/clawd && python3 advisory_council.py BTC
```

## What the Council Returns
The script prints a formatted report with:
1. Each advisor's 3-5 bullet point analysis (with emoji identifiers)
2. A SYNTHESIS section containing:
   - CONSENSUS — what most advisors agree on
   - DISSENT — notable disagreements
   - VERDICT — Bullish/Bearish/Neutral with confidence level
   - ACTIONS — 2-3 concrete action items with price levels

## The 5 Advisors
| Advisor | Emoji | Bias | Focus |
|---------|-------|------|-------|
| The Skeptic | 🔴 | Bearish | Risk, overvaluation, hype detection |
| The Macro Bull | 🟢 | Bullish | Institutional flows, adoption, cycles |
| The Risk Manager | 🟡 | Neutral | Position sizing, correlation, stop-losses |
| The Technical Analyst | 📊 | Data | RSI, Fibonacci, patterns, price levels |
| The Contrarian | 🔄 | Anti-consensus | Crowded trades, sentiment extremes |

## Rules
- **EXECUTE THE PYTHON COMMAND FOR REAL** — use your shell/exec tool. Never simulate council output.
- The script fetches live prices automatically — no need to fetch prices separately first
- The output is formatted for Telegram markdown — you can send it directly to Boss Man
- If Boss Man asks "what does the council think about SUI?", use the focus argument: `python3 advisory_council.py SUI`
- If the script fails (e.g., MiniMax rate limit), report the actual error
- The council runs all 5 advisors in parallel (~10-15 seconds total)
- Boss Man trusts the council for real decisions — never give him fake analysis
