---
name: fuku-predictions
description: Trade Kalshi prediction markets through conversation, powered by Fuku sports model predictions. Use when a user asks about Kalshi markets, wants sports predictions with edge analysis, wants to place or exit trades, or wants autonomous scanning. Supports CBB, NBA, NHL, and Soccer with personalized trading profiles. User defines preferences in natural language ("I want home dogs getting 7+ points in CBB"), agent builds a profile, scans markets, and presents opportunities with edge, payout, and recommendation. Kalshi API key stored locally — never transmitted externally.
---

# Fuku Predictions — Conversational Kalshi Trading Skill

Trade prediction markets through conversation. The agent learns what you care about, builds a personalized profile, then scans Kalshi markets for opportunities that match your style.

## Three Modes

### 1. Profile Building (Interactive)
User describes preferences → agent builds a trading profile → saves for reuse.

### 2. Conversational Scanning
Agent scans markets using the profile → presents matching opportunities → user approves trades.

### 3. Autonomous Trading
Agent scans and trades automatically within risk limits.

---

## Setup

### Dependencies
```bash
pip install httpx cryptography python-dotenv
```

### Kalshi API Key
Create `.env` in the skill directory:
```env
KALSHI_API_KEY_ID=your_key_id
KALSHI_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----"
```
Get credentials: https://kalshi.com/profile/api

---

## Defining Preferences

Users express what they care about in natural language:

**Situational:** "I want home dogs getting 7+ points in CBB" · "Show me letdown spots after big wins" · "Find revenge games where the underdog lost by 15+ last time"

**Player Mismatches:** "Games where the best player has a 50+ FPR gap" · "Matchups when a star player is injured"

**Statistical:** "Only games with top 30 defenses" · "Pace mismatches (fast vs slow)" · "Spreads under 3 points"

**Risk & Sizing:** "$5 bets on highest confidence plays" · "Max 8 trades per day" · "Quarter-Kelly sizing"

---

## Agent Tools

### Profile Management
```bash
# Process user preference input
python3 scripts/agent_interface.py --input "I want home dogs getting 7+ points in CBB"

# Scan using a profile
python3 scripts/agent_interface.py --scan --profile default

# List profiles
python3 scripts/agent_interface.py --input "list my profiles"
```

### Market Browser
```bash
# Tonight's markets with predictions and edges
python3 scripts/browse.py

# Filter by sport or game
python3 scripts/browse.py --sport cbb
python3 scripts/browse.py --game "Duke" --date 2026-03-03

# Change bet display amount (default $5)
python3 scripts/browse.py --bet 10
```

### Direct Kalshi Access
```bash
python3 scripts/kalshi_client.py balance
python3 scripts/kalshi_client.py positions
python3 scripts/kalshi_client.py markets --series KXNBASPREAD
```

---

## Presenting Markets to Users

**Always include:** the market, price (dollars), model prediction, edge, payout, and recommendation.

**Talk in dollars, not contracts.** Users say "$5 on Boston" — convert to contracts internally.

**Three-tier display per market type:**
- **Main line** — contract closest to 50¢ (market consensus)
- **🔒 Safer** — highest edge (high confidence, modest payout)
- **🎰 Riskier** — near model's predicted line (~50% model probability, bigger payout, ≥3% edge required)

**Edge icons:** 🔥 ≥20% · ✅ ≥10% · 📊 ≥5% · ➖ <5%

Example:
```
🏀 Boston @ Milwaukee — 7:30 PM
📊 Our model: BOS -8.4 | Total 224.1

• BOS -2.5 at 50¢ → 70% model (+20% edge 🔥) — $5 pays $10
  ↳ 🔒 Safer: BOS -1.5 at 57¢ → 82% model (+25% edge) — $5 pays $8
  ↳ 🎰 Riskier: BOS -8.5 at 31¢ → 50% model (+19% edge) — $5 pays $16
• Over 215.5 at 52¢ → 79% model (+27% edge 🔥) — $5 pays $9

💰 Balance: $49.95
Want me to put money on any of these?
```

### Dollar-to-Contract Math
"$5 on BOS -8.5" at 31¢ → floor($5 / $0.31) = 16 contracts × $0.31 = $4.96 cost → $16.00 payout if YES → $11.04 profit.

---

## Trading

```python
from kalshi_client import KalshiClient
c = KalshiClient()

# Buy
c.place_order(ticker="KXNBA...", side="yes", action="buy",
              count=16, order_type="limit", yes_price=31)

# Sell to exit
c.place_order(ticker="KXNBA...", side="yes", action="sell",
              count=16, order_type="limit", yes_price=current_bid)
```

---

## Edge Math

Normal distribution probability conversion (no scipy):
- Uses `math.erfc` for CDF
- Sport-specific σ: CBB spread 12.0 / total 11.0, NBA 11.0 / 10.5, NHL 1.5 / 1.3, Soccer 1.2 / 1.1
- Player props: σ = 30% of predicted value (min 2.0)

---

## Kalshi Market Structure

- **Series** (sport): `KXNBASPREAD`, `KXNBATOTAL`, `KXNBAGAME`
- **Event** (game): `KXNBASPREAD-26MAR02BOSMIL`
- **Market** (contract): `KXNBASPREAD-26MAR02BOSMIL-BOS7` → "Boston wins by over 7.5?"

Pricing: YES/NO in cents (1-99). YES 31¢ = 31% implied. 1 contract = $1 max payout.

### Supported Sports
| Sport | Spread | Total | ML | Props |
|-------|--------|-------|----|-------|
| NBA | `KXNBASPREAD` | `KXNBATOTAL` | `KXNBAGAME` | — |
| CBB | `KXNCAAMBSPREAD` | `KXNCAAMBTOTAL` | `KXNCAABGAME` | — |
| NHL | `KXNHLSPREAD` | `KXNHLTOTAL` | `KXNHLGAME` | Goals/Pts/Ast |
| Soccer | Per-league (EPL/La Liga/Serie A/Bundesliga/Ligue 1/UCL/MLS) | Per-league | Per-league | BTTS |

---

## Autopilot Config

`config/config.json`:
```json
{
  "strategy": "model_follower",
  "sports": ["nba", "cbb"],
  "min_edge_pct": 3.0,
  "max_daily_loss_pct": 10,
  "max_daily_bets": 15,
  "sizing": "quarter_kelly",
  "mode": "approve"
}
```

**Modes:** `dry_run` (log only) · `approve` (ask user) · `auto` (hands-free)

---

## Safety

- Max daily loss limit (default 10%)
- Position size caps (default 5% per trade)
- Kill switch: `touch KILL_SWITCH` in skill directory
- All trades logged locally to `trades.json`
- API keys never leave the machine

---

## Kalshi API Auth

RSA-PSS signatures. The client handles this automatically.

**Signing quirk:** Portfolio endpoints sign path WITHOUT query strings. Market endpoints sign WITH. See `_SIGN_PATH_ONLY` in `kalshi_client.py`.

---

## Fuku Prediction API (Public)

Base: `https://cbb-predictions-api-nzpk.onrender.com`

| Endpoint | Data |
|----------|------|
| `/api/public/cbb/predictions?date=YYYY-MM-DD` | CBB predictions |
| `/api/public/nba/predictions?date=YYYY-MM-DD` | NBA predictions |
| `/api/public/nhl/predictions?date=YYYY-MM-DD` | NHL predictions |
| `/api/public/soccer/predictions?date=YYYY-MM-DD` | Soccer predictions |
| `/api/public/cbb/rankings?limit=N` | Team FPR rankings |
| `/api/public/cbb/players?team=X&limit=N` | Player FPR data |

---

## Files

| File | Purpose |
|------|---------|
| `scripts/browse.py` | **Primary** — markets with predictions, edges, payouts |
| `scripts/agent_interface.py` | Conversational profile building + scanning |
| `scripts/profile_engine.py` | Profile-based opportunity scoring |
| `scripts/profile_builder.py` | Natural language → profile JSON |
| `scripts/autopilot.py` | Autonomous scanning + trading pipeline |
| `scripts/kalshi_client.py` | Kalshi API client (auth, orders, markets) |
| `scripts/scanner.py` | Full edge scanner (all contracts) |
| `scripts/executor.py` | Trade execution with risk management |
| `scripts/portfolio.py` | Position tracking and P&L |
| `scripts/setup.py` | Interactive setup wizard |
| `config/config.json` | Strategy and risk settings |
| `config/profiles/*.json` | User trading profiles |
| `references/strategies.md` | Strategy explanations |
| `references/kalshi-markets.md` | How Kalshi markets work |
