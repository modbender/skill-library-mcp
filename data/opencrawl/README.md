# ConvoYield — Conversational Yield Optimization Engine

**Treat every bot conversation as a yield-bearing financial instrument.**

ConvoYield is a zero-dependency Python skill that gives any bot the ability to detect, score, and capture hidden monetary value from every single conversational exchange — not just the ones that end in a sale.

> In finance, a yield is the income return on an investment.
> In conversations, the yield is the total value you can extract: revenue, data, referrals, engagement, competitive intel.
> **Most bots capture less than 20% of available conversational yield. ConvoYield fixes that.**

## Why This Exists

Out of **13,700+ skills** in the OpenClaw ecosystem, not a single one treats conversations as financial instruments. Every bot talks. No bot optimizes the *value* of what it says.

ConvoYield applies concepts from behavioral economics, financial engineering, and game theory to conversational AI:

| Concept | Financial World | ConvoYield |
|---------|----------------|------------|
| **Arbitrage** | Exploit price gaps across markets | Exploit sentiment gaps for revenue |
| **Yield** | Income return on investment | Dollar value of each conversation |
| **Momentum** | Stock price trend direction | Engagement trend direction |
| **Risk** | Probability of loss | Probability of losing the user |
| **Micro-conversions** | Dividend payments | Small value extractions per message |

## Zero Cost to Run

- **ZERO external dependencies** — pure Python stdlib
- **ZERO API calls** — all analysis runs locally via pattern matching and heuristics
- **ZERO tokens consumed** — doesn't call any LLM APIs
- **ZERO infrastructure needed** — `pip install` and go

## The Five Engines

### 1. Sentiment Arbitrage Engine
Detects emotional gaps that create revenue opportunities. A frustrated user mentioning a competitor isn't just venting — it's a $45+ conversion opportunity if handled correctly.

### 2. Micro-Conversion Tracker
Finds hidden money in every message. Between "hello" and "purchase," there are dozens of micro-moments worth $0.50-$15 each: email captures, budget reveals, pain point articulations, referral signals.

### 3. Momentum Scorer
Measures whether the conversation is gaining or losing steam. Positive momentum = push for conversion. Negative momentum = pull back and re-engage before you lose them.

### 4. Yield Forecaster
Predicts the total dollar value of the conversation in real-time. Imagine a dashboard showing: `Estimated Value: $127.50 | Captured: $35.00 | At Risk: $92.50`

### 5. Play Caller
Recommends optimal strategic "plays" from a 20-play playbook based on behavioral economics: anchoring, loss framing, social proof deployment, empathy bridges, urgency closes, and more.

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

## Integration

Works with any bot framework:

```python
# Discord, Telegram, Slack, OpenClaw — same pattern:
guidance = engine.process_user_message(user_text)

# Use guidance to shape your response:
# guidance.recommended_play → WHAT strategy to use
# guidance.recommended_tone → HOW to say it
# guidance.arbitrage_opportunities → WHERE the money is
# guidance.micro_conversions → WHAT value to capture
# guidance.risk_level → HOW careful to be
```

See `examples/openclaw_skill.py` for a complete OpenClaw skill wrapper.

## Install

```bash
pip install -e .
```

## Run Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Run Demo

```bash
python examples/basic_usage.py
```

## Architecture

```
convoyield/
├── __init__.py              # Public API
├── orchestrator.py          # Main ConvoYield engine
├── engines/
│   ├── sentiment_arbitrage.py   # Emotional gap detection
│   ├── micro_conversion.py      # Value-extraction tracking
│   ├── momentum.py              # Engagement trend analysis
│   ├── yield_forecaster.py      # Dollar value prediction
│   └── play_caller.py           # Strategic play recommendations
├── models/
│   ├── conversation.py      # Conversation state model
│   └── yield_result.py      # Analysis result model
examples/
├── basic_usage.py           # See it in action
├── openclaw_skill.py        # OpenClaw/MoltBot integration
└── batch_analysis.py        # Analyze conversation logs
tests/
└── test_convoyield.py       # 40 tests, 100% pass rate
```

## License

MIT — Use it, sell it, build on it. Every bot deserves to know what its conversations are worth.
