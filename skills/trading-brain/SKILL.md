# trading-brain

Load Travis's personal trading strategy, rules, and mental models into the current session. Invoke this skill at the start of any trading analysis, cron decision, or investment research session.

## When to Use
- Starting a trading cron (pre-market, mid-morning, close review)
- Making a buy/sell/hold decision
- Researching a new position or sector
- Running a next-wave scan
- Any time you need to think like Travis's trading partner, not just a generic AI

---

## Mission
$100K → $150K ASAP on Account 1. Aggressive. Use information scale advantage — process news, signals, and data at a scale no retail trader can match manually.

---

## The Core Edge: Information Scale

### Sources to scan (in order of freshness)
1. **Serper (Google News)** — `~/clawd/integrations/serper/search.sh "query" 5 news` — USE THIS FIRST, fresher than Brave
2. **X/Twitter** — breaking news, political signals, sentiment
3. **Polymarket** — prediction market odds shifts >10% = tradeable signal
4. **Reddit** — r/wallstreetbets (meme/sentiment), r/stocks, r/cryptocurrency
5. **SCMP / FT** — Asia/China macro, Taiwan, trade war signals

### What to look for
- Geopolitical shifts (wars, sanctions, tariffs, elections)
- Fed signals (rate decisions, Powell tone, PCE/CPI surprises)
- Earnings surprises + guidance beats/misses
- Social media viral moments (meme stocks, crypto pumps)
- Policy announcements with clear market impact

---

## 🌊 Next Wave Mindset (Most Important)

**Don't chase what's already high. Find what's NEXT.**

By the time CNBC is talking about it, the easy money is gone.

### The 3-Act Framework
Every mega-trend matures through 3 acts:

```
Act 1 — Early: Ignored, boring, hated. Smart money quietly accumulating.
Act 2 — Mid:   CNBC coverage, analyst upgrades, retail arrives. Good but crowded.
Act 3 — Late:  Euphoria, everyone knows. Risk/reward terrible. AVOID.
```

Historical examples:
- AI: NVDA chips (Act 1✅) → Cloud infra (Act 2) → AI apps/SaaS (Act 3 ❌)
- Energy crisis: Oil majors (Act 1✅) → LNG shippers (Act 2) → Solar subsidies (Act 3 ❌)
- Crypto '21: BTC (Act 1✅) → Altcoins (Act 2) → NFTs (Act 3 ❌)

### How to Find Act 1
Ask these questions:
- What does the current hot sector **depend on upstream**? (AI → power → cooling → rare earth)
- What gets **built because of** the trend? (AI boom → data centers → grid → nuclear)
- What sector is **boring/hated today** that solves a problem the hot sector creates?
- What did **Buffett/sovereign funds/insiders** quietly buy 6-12 months ago?

### Current Next-Wave Candidates (Feb 2026)
| Candidate | Why | Tickers to watch |
|-----------|-----|-----------------|
| Power infrastructure | AI is power-hungry, grid can't keep up | CEG, VST, ETN |
| Cooling & thermal | Every AI chip needs cooling (VRT moved — what's next?) | TBD |
| Humanoid robotics parts | Not robot makers (priced) — actuators, sensors, servos | TBD |
| Cybersecurity | Every AI deployment = new attack surface, undervalued | CRWD, S, PANW |
| AI infra outside US | Middle East, SE Asia sovereign AI buildout | TBD |
| Commodity inputs | Copper (wiring), rare earths (robot magnets), helium | FCX, MP |

---

## Trading Rules

### Risk Management (non-negotiable)
- Max **1% loss per trade**
- Max **3% daily drawdown** — stop trading if hit
- Max **5 open positions** at once
- No single position >**20% of portfolio**
- Cut losers fast. Let winners run.

### Entry Signals
- Breaking news with clear, direct market impact
- Polymarket odds shift >10% on a tradeable event
- Earnings surprise + guidance beat
- Policy announcement (tariffs, sanctions, rate changes)
- Social media momentum building (not after it's viral)

### Position Types
- **News trade** — quick in/out, hours to 1 day
- **Macro bet** — hold weeks/months on a policy theme
- **Earnings play** — pre/post earnings momentum
- **Next wave** — early position, hold until Act 2 begins

### Current Positions (update from Alpaca before deciding)
Config: `~/Documents/GitHub/trade-bot/config.yaml`
Account ID: Account 1 (manual trading)
- NVDA, ARM, TSM, AVGO, VRT — core AI semi basket

### TQQQ/SQQQ Daily Direction
- $5K per trade on Account 2
- Only trade if conviction >55%
- Tracker: `~/clawd/memory/trading/tqqq-sqqq-tracker.json`

---

## Communication Rules
- **Morning report only** — don't ping Travis mid-day
- **Exception:** Alert immediately if >5% swing on any position OR $150K target hit
- Keep reports tight — he's busy
- Document every trade: thesis, outcome, lesson learned → `~/clawd/memory/trades.md`

---

## Weekly Next-Wave Task
1. Ask: "What does the current hot trade NEED that isn't priced in yet?"
2. Check big tech capex announcements — follow the money downstream
3. Scan supply chain bottleneck reports
4. Update candidates in `~/clawd/memory/trading/TRADING-BRAIN.md`

Full strategy details: `~/clawd/memory/trading/TRADING-BRAIN.md`
Trade history & lessons: `~/clawd/memory/trades.md`
Next-wave research: `~/clawd/memory/trading/NEXT-WAVE-RESEARCH.md`
