---
name: valuation-calculator
description: Fast stock valuation calculator - compute PEG, EV/EBITDA, Rule of 40, DCF and more with simple commands. Inspired by YouTube tutorial and Day1Global Tech Earnings Deepdive Skill.
---

# Valuation Calculator

Fast stock valuation calculator with instant market valuation metrics.

## Commands

| Command | Description |
|---------|-------------|
| `value <ticker>` | Full valuation for a single stock |
| `value peg <ticker>` | PEG + Forward/Trailing P/E + Implied Growth |
| `value ev <ticker>` | EV/EBITDA + Rule of 40 |
| `value dcf <ticker>` | DCF valuation (default parameters) |
| `value dcf <ticker> --auto` | DCF with **auto-calculated WACC** (CAPM model) |
| `value dcf <ticker> --wacc=0.10 --growth=0.15 --terminal=0.03` | Custom DCF parameters |
| `value` | All holdings valuation (reads from holdings.md) |
| `value --index` | Three major indices (SPY, QQQ, DIA) |

## Output Metrics

- **PEG Ratio** = Forward P/E ÷ EPS Growth Rate
- **Forward P/E** = Based on next 12 months expected earnings
- **Trailing P/E** = Based on past 12 months actual earnings
- **Implied EPS Growth** = (Trailing P/E ÷ Forward P/E - 1) × 100%
- **EV/EBITDA** = Enterprise Value ÷ EBITDA
- **Rule of 40** = Revenue Growth % + Profit Margin %
- **DCF** = Discounted Cash Flow valuation

## DCF Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--auto` | Auto-calculate WACC using CAPM model | - |
| `--wacc=N` | Weighted Average Cost of Capital | 10% |
| `--growth=N` | Future growth rate | 5% |
| `--terminal=N` | Terminal growth rate | 2.5% |

### Auto WACC (CAPM Model)

WACC = Rf + β × (Rm - Rf)

- **Rf** = 10-year Treasury yield (auto-fetched from Yahoo Finance)
- **β** = Stock beta (from Yahoo Finance)
- **Rm - Rf** = Market risk premium (5.5%)

## Holdings File

Default reads from `~/.openclaw/workspace/holdings.md`

## Data Source

Yahoo Finance API (yfinance)

## Usage Examples

```
value NVDA          # Full valuation
value peg NVDA      # PEG only
value ev NVDA       # EV/EBITDA + Rule of 40
value dcf NVDA     # DCF (default params)
value dcf NVDA --auto  # DCF with auto-WACC
value dcf NVDA --wacc=0.08 --growth=0.15 --terminal=0.03  # Custom
value               # All holdings dashboard
value --index       # Major indices
```

## Evaluation Criteria

| PEG | Rating |
|-----|--------|
| < 0.5 | 🔥 Severely Undervalued |
| 0.5 - 1.0 | 👍 Undervalued |
| 1.0 - 1.5 | ✅ Fair Value |
| > 1.5 | ⚠️ Overvalued |

| Rule of 40 | Rating |
|------------|--------|
| >= 40% | ✅ Pass |
| < 40% | ⚠️ Below |

| DCF Upside | Rating |
|------------|--------|
| > 20% | ✅ Undervalued |
| -20% ~ 20% | ⚠️ Fair Value |
| < -20% | ❌ Overvalued |

---

**Inspired by:**
- YouTube: [布萊恩穩賺 - Stock valuation screening](https://youtu.be/gVWvhIAtGDE)
- Day1Global Tech Earnings Deepdive Skill
