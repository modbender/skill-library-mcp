---
name: convoyield
description: >
  Conversational Yield Optimization Engine — treats every bot conversation as a
  yield-bearing financial instrument. Five zero-cost engines detect sentiment
  arbitrage, micro-conversions, engagement momentum, dollar-value yield forecasts,
  and optimal strategic plays in real-time. No external APIs. No dependencies.
  Pure behavioral economics applied to conversations.
version: 1.0.0
author: J. DeVere Cooley
homepage: https://github.com/jcools1977/Opencrawl
metadata:
  openclaw:
    emoji: "📈"
    requires:
      bins:
        - python
    os: ["macos", "linux", "windows"]
    tags:
      - revenue
      - optimization
      - behavioral-economics
      - zero-cost
      - sentiment
      - conversion
    platforms: ["discord", "telegram", "whatsapp", "slack", "webchat"]
    cost: free
    requires_api: false
---

# ConvoYield — Conversational Yield Optimization Engine

> "Every conversation is a financial instrument. ConvoYield tells you what it's worth."

## What It Does

ConvoYield gives any bot a **real-time revenue intelligence layer**. On every user
message, five engines run in parallel and produce:

- **Sentiment Arbitrage** — Detects emotional gaps that create revenue opportunities
  (frustration capture, competitor displacement, excitement amplification, etc.)
- **Micro-Conversion Tracking** — Finds 12 types of hidden value in every message
  (email captures, budget reveals, pain points, referral signals, etc.)
- **Momentum Scoring** — Measures whether the conversation is gaining or losing steam
- **Yield Forecasting** — Predicts the total dollar value of the conversation in real-time
- **Play Calling** — Recommends from a 20-play behavioral economics playbook
  (anchoring, loss framing, social proof, empathy bridges, urgency closes, etc.)

## Zero Cost Guarantee

- **Zero external dependencies** — Pure Python standard library
- **Zero API calls** — All analysis runs locally via pattern matching and heuristics
- **Zero tokens consumed** — Does not call any LLM API
- **Zero infrastructure** — `pip install` and go
- **<1ms per message** — Adds no latency to your bot

## Quick Start

```python
from convoyield import ConvoYield

engine = ConvoYield(base_conversation_value=50.0)

# Process each user message
result = engine.process_user_message("I'm frustrated with Salesforce, it's way too expensive")

print(result.recommended_play)       # "competitor_displacement"
print(result.estimated_yield)         # 89.50
print(result.recommended_tone)        # "empathetic"
print(result.top_arbitrage.type)      # "frustration_capture"
print(result.risk_level)              # 0.21

# Record bot response for full state tracking
engine.record_bot_response("I hear you. What specifically isn't working?")

# Next message — yield COMPOUNDS
result = engine.process_user_message("The reporting is terrible and costs $500/month")
print(result.estimated_yield)         # 142.30 — value is growing!
```

## The Five Engines

### 1. Sentiment Arbitrage Engine

Detects 7 arbitrage patterns via lexicon-based sentiment scoring tuned for
commercial conversations:

| Pattern | What It Detects | Value Signal |
|---------|----------------|--------------|
| `competitor_displacement` | Frustration with a named competitor | $45+ |
| `frustration_capture` | General frustration with current solution | $35+ |
| `excitement_amplification` | User showing enthusiasm | $25+ |
| `uncertainty_anchoring` | User unsure, needs guidance | $20+ |
| `urgency_premium` | Time pressure detected | $30+ |
| `social_proof_hunger` | User seeking validation | $15+ |
| `budget_value_stack` | User discussing budget/cost | $40+ |

### 2. Micro-Conversion Tracker

Detects 12 micro-conversion opportunities between "hello" and "purchase":

- Email/phone capture opportunities
- Budget and timeline reveals
- Team size and need statements
- Competitor mentions and feature requests
- Referral and testimonial signals
- Pain point articulations

Each micro-conversion has an estimated dollar value ($0.50-$15).

### 3. Momentum Scorer

Scores engagement momentum (-1.0 to +1.0) using four signals:
- Message length trend (expanding = engaged)
- Question frequency trend (asking = curious)
- Emotional intensity trend (feeling = invested)
- Vocabulary richness trend (elaborating = committed)

Labels: `surging` | `accelerating` | `stable` | `declining` | `hemorrhaging`

### 4. Yield Forecaster

Combines all signals to predict a dollar value for the conversation using:
- Phase multipliers (OPENING → DISCOVERY → ENGAGEMENT → NEGOTIATION → CLOSING)
- Micro-conversion portfolio value
- Arbitrage opportunity value
- Engagement and momentum premiums
- Risk assessment (0.0-1.0)

### 5. Play Caller

Recommends from 20 plays inspired by behavioral economics:

`warm_handshake` · `pattern_interrupt` · `deep_probe` · `empathy_bridge` ·
`value_stack` · `competitor_displacement` · `social_proof_deploy` ·
`dopamine_ride` · `anchoring` · `loss_framing` · `budget_reframe` ·
`choice_architecture` · `assumptive_close` · `urgency_close` · `soft_close` ·
`momentum_recovery` · `save_attempt` · `upsell_bridge` · `referral_harvest` ·
`objection_reframe`

## Integration

Works with any bot framework — hook into your message handler:

```python
from convoyield import ConvoYield

engine = ConvoYield()

def on_user_message(text, conversation_id):
    result = engine.process_user_message(text)

    # Shape your bot's response using:
    # result.recommended_play     → WHAT strategy to use
    # result.recommended_tone     → HOW to say it
    # result.arbitrage_opportunities → WHERE the money is
    # result.micro_conversions    → WHAT value to capture
    # result.risk_level           → HOW careful to be
    # result.estimated_yield      → HOW much is at stake

    return generate_response(text, result)
```

## Premium Playbooks

Four industry-specific playbook packs available:

| Playbook | Plays | Price |
|----------|-------|-------|
| SaaS Sales Mastery | 25 | $49/mo |
| E-Commerce Revenue Max | 22 | $39/mo |
| Real Estate Closer | 20 | $79/mo |
| Healthcare Engagement | 18 | $99/mo |

## Revenue Model

ConvoYield is free and open source. Revenue comes from:

1. **Premium playbooks** — Industry-specific play packs ($39-99/mo)
2. **Cloud analytics** — Dashboard and yield tracking ($0/49/299/mo tiers)
3. **Enterprise** — Custom playbooks, webhooks, white-label ($299/mo)

## Architecture

```
convoyield/
├── orchestrator.py              # Main ConvoYield engine
├── engines/
│   ├── sentiment_arbitrage.py   # 7 arbitrage pattern detectors
│   ├── micro_conversion.py      # 12 micro-conversion trackers
│   ├── momentum.py              # 4-signal engagement scorer
│   ├── yield_forecaster.py      # Dollar-value yield prediction
│   └── play_caller.py           # 20-play behavioral economics playbook
├── models/
│   ├── conversation.py          # ConversationState, Turn, Phase
│   └── yield_result.py          # YieldResult, ArbitrageOpportunity
├── playbooks/                   # 4 premium industry packs (85 plays)
├── coin/                        # ConvoCoin — Proof-of-Yield blockchain
└── cloud/                       # Telemetry client for analytics
```

## Tests

40 tests across 7 suites — all passing:

```bash
python -m pytest tests/ -v
```
