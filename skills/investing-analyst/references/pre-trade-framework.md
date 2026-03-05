# Pre-Trade Framework — Options Discipline

---

## The 3 Gate Questions

Answer all 3 before entering. If any answer is "no" or vague — don't trade.

### Gate 1: Thesis Test
Complete this sentence out loud:
> "I'm buying because **[specific structural/fundamental reason]**, and I'll exit if **[specific condition that invalidates the thesis]**."

If you can't complete it clearly, you're reacting to price — not trading a thesis.

**Red flags:**
- "It's been running / everyone's bullish"
- "I missed the move and want in"
- "It reversed hard, must be a buy"
- Thesis is just "strong company" with no catalyst or mispricing identified

---

### Gate 2: Edge Test
Ask honestly: **Do I have real informational advantage on this name?**

**High-edge criteria:**
- You've followed this company for >3 months
- You understand the key metrics that drive earnings surprises
- You have a view on guidance that differs from consensus
- You've been right on this name before and understand why

**Low-edge criteria (proceed with caution or avoid options):**
- You're reacting to news or price action on a name you don't follow regularly
- The thesis is driven purely by macro narrative ("AI will win")
- You haven't read recent earnings transcripts

**Rule:** If it's a low-edge name, use a defined-risk spread with a max loss you're comfortable losing 100% of, and size small.

---

### Gate 3: Entry Timing
- Are you entering because price confirms your thesis, or because price is moving?
- For contrarian plays: is there a technical trigger (200 SMA, Donchian washout, overextension)?
- For earnings plays: has IV been compared to HV? Are options expensive?

---

## Position Management Rules

### Stop Loss
- **Set max loss before entry. No exceptions.**
- Suggested defaults:
  - Spreads: close if value drops to 30% of debit paid (you lose 70%)
  - Long calls: close if down 50%
  - Never add to a losing options position. Ever.

### The Escalation Rule
> If a trade goes against you and you feel the urge to add — that's a signal to **close**, not add.

Averaging down on options accelerates losses. Example: a winning first contract (+$1,100) followed by two additional contracts bought lower (-$4,300) = net loss of -$3,200. The escalation cost 4× the original gain. This pattern is well-documented in options trading; resist it every time.

### Profit Taking
- Set a target return at entry (e.g., 50%, 100%)
- When you hit it, close at least 50% of the position
- Don't hold winners to expiry chasing the last 10-20% — IV crush and theta eat it

### Expiry Rule
- Never hold short-dated spreads to expiry (pin risk, assignment risk)
- Close spreads with <2 weeks to expiry regardless of P&L if they're ITM

---

## Trade Log Template (fill before every entry)

```
Date:
Ticker:
Structure (e.g. $30C 3/20, bull call spread $190/195):
Entry debit/credit:
Max profit:
Max loss:

THESIS: I'm buying because...

INVALIDATION: I'll exit early if...

EXIT TARGET: Close at $__ or __% gain
STOP LOSS: Close at $__ or __% loss (never add below this)
EDGE: [High / Low] — reason:
```

---

## Playbook by Trade Type

### Earnings Catalyst Play (highest edge)
- **Who it's for:** Names you know deeply — earnings cadence, key metrics, guidance patterns
- Structure: Long call or call debit spread, 2-4 weeks out
- Entry: 2-3 weeks before earnings, after IV is elevated but not peak
- Exit: Close 1-2 days before earnings OR hold through if thesis is strong + IV vs HV checked
- Watch: IV crush post-earnings — options expensive pre-earnings, use spreads to cap premium paid

### Contrarian Structural Play (proven edge)
- **Who it's for:** Stocks at technical extremes with a clear fundamental thesis
- Examples of triggers: 200 SMA touch after extended downtrend, RSI extreme, Donchian washout
- Structure: Defined-risk spread or long call with >30 days to expiry
- Entry trigger: Technical confirmation
- Exit: Take profits at 50-75% of max gain; don't wait for full ITM

### Macro/Index Play (acceptable, size small)
- Names: SPY, QQQ LEAPs
- Structure: Wide call spreads, long-dated (6mo+)
- Size: Keep total debit small relative to portfolio (suggest <0.5% of portfolio per position)
- Exit: Patient, but set a target and take it when hit

### Momentum / FOMO Trade (avoid)
- Trigger: Price moving fast + emotional pull to participate
- **Rule: Do not trade. If you must, size at $200 max, 0 adds.**

---

## Monthly Review Checklist
- [ ] What trades did I close this month?
- [ ] Which were thesis-based vs reactive?
- [ ] Did I add to any losers? (If yes, note why and what happened)
- [ ] Did I leave significant money on the table by not having a profit target?
- [ ] What's my options win rate and average gain/loss ratio?
