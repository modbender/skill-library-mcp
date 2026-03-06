---
name: ResonanceEngine
description: Conversational Frequency Matching — reads invisible micro-signals in every conversation and tells the bot exactly how to respond for maximum engagement, conversion, and revenue. Zero API cost. Pure algorithmic intelligence.
version: 0.1.0
author: J. DeVere Cooley
tags: [engagement, conversion, monetization, optimization, universal, zero-cost]
category: AI & LLMs
---

# ResonanceEngine

**The Physics of Persuasion, Applied to Bots.**

## What It Does

ResonanceEngine reads **15+ invisible micro-signals** in every conversation — message length trends, hedging language, commitment words, mirror behavior, sentiment velocity — and computes **4 real-time frequencies** that tell the bot exactly how to respond for maximum impact.

Think of it like this: In physics, **resonance** amplifies a system dramatically when you match its natural frequency. Every user has a hidden conversational frequency. A bot that matches it converts **3-10x better**.

## The 4 Frequencies

| Frequency | What It Measures |
|-----------|-----------------|
| **Engagement** | Is the user leaning in or pulling away? |
| **Trust** | How much does the user trust the bot? |
| **Decision** | How close are they to converting/deciding? |
| **Style Match** | How well is the bot resonating with the user's style? |

## Why Every Bot Needs This

- **Zero cost** — Pure Python text analysis. No API calls. No ML models. No GPU.
- **Universal** — Works for sales bots, support bots, companion bots, any bot.
- **Revenue multiplier** — Directly increases conversion, retention, and upsell rates.
- **Invisible advantage** — The bot "just seems better" and nobody understands why.

## Usage

```python
from openpaw import ResonanceEngine
from openpaw.models import Conversation

engine = ResonanceEngine()
convo = Conversation(goal="sale")

convo.add_bot_message("Hi! How can I help you today?")
convo.add_user_message("I've been looking at your premium plan, but I'm not sure if it's right for me")

result = engine.analyze(convo)

# Get the resonance level
print(result.profile.resonance_level)  # "BUILDING"

# Get specific recommendations
print(result.recommendation.action)
# "Momentum is building. Keep the conversation flowing. Ask a focused question..."

# Get conversion probability
print(result.yield_prediction.conversion_probability)  # 0.35

# Inject tuning into bot's system prompt
system_prompt += result.recommendation.to_prompt_injection()
```

## What It Outputs

After analyzing each user message, ResonanceEngine returns:

1. **Frequency Profile** — The 4 frequencies (0-1 each) plus composite score
2. **Resonance Level** — PEAK_RESONANCE, HIGH_RESONANCE, BUILDING, WEAK, or NO_RESONANCE
3. **Tuning Recommendation** — Specific guidance: response length, style, techniques, objection handling
4. **Yield Prediction** — Conversion probability, estimated value, optimal turns remaining, risks & opportunities
5. **Prompt Injection** — A ready-to-use string to inject into the bot's system prompt

## Integration

Drop ResonanceEngine into any bot's message processing pipeline:

```python
# In your bot's message handler:
user_msg = get_user_message()
conversation.add_user_message(user_msg)

# Analyze with ResonanceEngine
result = engine.analyze(conversation)

# Use the tuning to adjust the bot's response
if result.yield_prediction.should_close:
    # Present the offer NOW
    response = generate_closing_response(result.recommendation)
else:
    # Build more resonance
    response = generate_response(
        user_msg,
        system_prompt_suffix=result.recommendation.to_prompt_injection()
    )

conversation.add_bot_message(response)
```

## Signals Analyzed

| Signal | Category | What It Detects |
|--------|----------|----------------|
| Message Length Trajectory | Engagement | Growing/shrinking responses |
| Question Density | Engagement | Curiosity vs. skepticism |
| Response Elaboration | Engagement | Investment in conversation |
| Topic Persistence | Engagement | Focus vs. drift |
| Hedge Ratio | Trust | Uncertainty language |
| Personal Disclosure | Trust | Sharing personal info |
| Mirror Behavior | Trust | Copying bot's style |
| Sentiment Trend | Trust | Warming up vs. cooling down |
| Commitment Language | Decision | "Yes", "let's do it" |
| Objection Frequency | Decision | "But", "however", "expensive" |
| Urgency Markers | Decision | "ASAP", "now", "today" |
| Action Language | Decision | "Do", "start", "make" |
| Formality Level | Style | Casual vs. formal |
| Vocabulary Complexity | Style | Simple vs. sophisticated |
| Emotional Energy | Style | Exclamation patterns |

## Install

```bash
pip install openpaw
```

Or add to your project:

```bash
git clone https://github.com/jcools1977/Openpaw-.git
cd Openpaw-
pip install -e .
```
