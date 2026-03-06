# Alert Rules & Filtering Logic

## ZHAO's Alert Framework

### Tier 1: Immediate Ping (Very High Conviction Only)
Conditions ALL must be true:
- Massive volume spike (1h vol > $500K AND vol accelerating vs prior hour)
- Clear narrative catalyst (AI agent, RWA, meme supercycle, Coinbase cultural tie-in)
- Clean chart structure (no massive early dump, steady accumulation or breakout)
- Liquidity > $100K (not a rug setup)
- Buy/sell ratio > 55% buys

Ping immediately. Do not wait.

### Tier 2: Standard Second-Wave Alert
Conditions:
- Token age: 45min–3h old
- 1h+ of sustained volume (not one spike)
- Holder count growing (verify via Basescan)
- Volume not declining in last 30min
- Score ≥ 65

Wait for 1–2h confirmation, then alert.

### Tier 3: Early Gem Exception (0–45min)
Rare. Ping immediately ONLY if:
- Strong early metrics: vol > $100K in <45min, makers > 200
- Clean team signals: real social presence, no anon rug history
- Real momentum: not wash trading (check buy/sell distribution)
- No obvious red flags: audit flags, anonymous team, copy-paste contract

Max 2–3 per day. If you're pinging more than this, the filter is broken.

### Tier 4: Pre-Launch / Upcoming
Watch and mention in next market update:
- Credible team announcing Base launch
- Clanker/Bankr deployment from known Farcaster power user
- VIRTUAL agent with real capabilities about to token launch

### DO NOT ALERT ON:
- Token Sniffer < 30/100 (unless team is verified and flag is known false positive)
- Top 3 holders > 50% supply
- Volume obviously wash traded (same wallet buying/selling)
- No social presence whatsoever
- Generic copy-paste meme with zero narrative
- Anything on a bleeding macro day with no specific catalyst (bad timing)

## Mainstream Asset Alert Rules (BTC, ETH, UNI, majors)

Alert when:
- Key level break (support/resistance with volume confirmation)
- Unusual on-chain flows (exchange inflows/outflows spike)
- Macro catalyst (Fed, regulatory, major protocol event)
- Funding rate extremes (> 0.1% or < -0.03%)
- Major whale accumulation/distribution (Arkham/Nansen signal)

Format for mainstream alerts:
```
[ASSET] [DIRECTION] — [PRICE]
Entry zone: $X–$Y
Stop: $Z (below [structure])
Target: $A (TP1) / $B (TP2)
Thesis: [1-2 sentences max]
Risk: [Low/Medium/High]
```

## Red Flags Checklist

Before any alert, quick mental check:
- [ ] Is the volume real? (check maker count, not just vol number)
- [ ] Is the team findable? (Twitter, website, Farcaster)
- [ ] Is there a legible narrative? (can explain in 1 sentence)
- [ ] Is liquidity > $30K? (below this = high rug risk)
- [ ] Is macro context reasonable? (don't long memecoins into ETH -5% day without catalyst)
- [ ] Have top holders been checked? (no 40%+ concentrated whales)

## Narrative Tags

Use these tags in alerts for quick scanning:

- `[AI-AGENT]` — AI agent tokens (VIRTUAL ecosystem, Clanker AI builds)
- `[ROBO]` — Robotics/AGI narrative
- `[RWA]` — Real World Asset narrative
- `[MEME]` — Pure memecoin, community-driven
- `[FARCASTER]` — Clanker/Bankr deployment, Farcaster community token
- `[COINBASE]` — Coinbase cultural/ecosystem tie-in
- `[DEFI]` — DeFi protocol token
- `[SECOND-WAVE]` — Confirmed second-wave setup
- `[EARLY-GEM]` — Early launch exception
