# AgResource Newsletter Scraper

Use this skill to scrape, summarize, and analyze AgResource grain marketing newsletters.

## Implementation

- **Scraper:** `scraper.js` (Playwright/Node.js)
- **Sentiment Analyzer:** `agresource_sentiment.py` (Python)
- **Login:** Automatic using `AGRESOURCE_EMAIL` and `AGRESOURCE_PASSWORD` env vars

## Capabilities

- Log in to AgResource dashboard (https://agresource.com/dashboard/#/reports/daily)
- Scrape daily newsletter content using Playwright
- Save screenshot for reference/debugging
- Extract corn/soybean sales advice and recommendations
- Generate concise summaries with key news and weather tidbits
- Analyze sentiment (bullish/bearish) across newsletters
- Compare to previous newsletters to detect trends
- Store summaries in `~/clawd/memory/agresource/YYYY-MM-DD.md` (morning)
- Store summaries in `~/clawd/memory/agresource/YYYY-MM-DD-noon.md` (noon)
- Store summaries in `~/clawd/memory/agresource/YYYY-MM-DD-evening.md` (evening)
- Store summaries in `~/clawd/memory/agresource/YYYY-MM-DD-saturday.md` (saturday)
- Store summaries in `~/clawd/memory/agresource/YYYY-MM-DD-sunday.md` (sunday)
- Track sentiment history in `~/clawd/memory/agresource/sentiment_history.json`
- Send Telegram alerts on new sales advice

## Commands

### Manual Trigger
```
"Check AgResource newsletter"
"Summarize today's grain report"
"Show full newsletter" (detailed view)
```

**To run scraper manually:**
```bash
cd /home/brianppetty/clawd/skills/agresource

# Morning newsletter (default)
node scraper.js
node scraper.js --type=morning

# Noon/midday newsletter
node scraper.js --type=noon

# Evening newsletter
node scraper.js --type=evening

# Saturday newsletter
node scraper.js --type=saturday

# Sunday newsletter
node scraper.js --type=sunday
```

### Cron Job Triggers

When a cron event fires, match the time/type to the correct `--type` parameter:

| Cron Message | Type to Use | Time |
|--------------|-------------|------|
| "Check AgResource newsletter (morning)" | `--type=morning` | 8:30 AM ET (Mon-Fri) |
| "Check AgResource newsletter (afternoon)" | `--type=noon` | 1:30 PM ET (Mon-Fri) |
| "Check AgResource newsletter (evening - positioning)" | `--type=evening` | 7:00 PM ET (Mon-Sat) |
| "Check AgResource newsletter (weekend)" | `--type=saturday` or `--type=sunday` | ~3:00 PM ET (Sat/Sun) |

**For weekend jobs**, determine which day it is and use:
- Saturday: `--type=saturday`
- Sunday: `--type=sunday`

### Sentiment Queries
```
"What's the current market sentiment?"
"Show sentiment trends"
"What's the sentiment history?"
```

## Sentiment Dimensions (PRICE-IMPACT FOCUSED)

**CRITICAL:** Sentiment analysis tracks PRICE IMPACT, not general "good/bad" news.

**Key inverse relationships to remember:**
- ☀️ Favorable weather in SA/NA = More supply = **BEARISH for prices**
- 🌽 Record yields = More supply = **BEARISH for prices**
- 🏜️ Drought/crop stress = Less supply = **BULLISH for prices**
- 🏭 Strong export demand = More demand = **BULLISH for prices**
- 📦 South American competition = Less US exports = **BEARISH for prices**

Track these dimensions across newsletters:
- **market_mood**: bullish | bearish | neutral
  - BULLISH = Prices expected to go UP
  - BEARISH = Prices expected to go DOWN
- **weather_impact**: positive_for_crops | negative_for_crops | mixed | neutral
  - Tracks weather impact on PRODUCTION (inverted for price impact)
  - Positive weather for crops = BEARISH for prices (more supply)
  - Negative weather for crops = BULLISH for prices (less supply)
- **production_outlook**: optimistic | cautious | uncertain
  - Optimistic = more supply = BEARISH for prices
  - Cautious = supply concerns = BULLISH for prices
- **trend_direction**: improving | declining | stable
- **confidence**: high | medium | low

## Sales Advice Detection

**Status phrases to detect:**
- "New sales advice detected" (buy/sell/recommend keywords)
- "Catch up sales recommended" (catch up phrase)
- "No sales recommended at this time" (hold/no action)
- "Position status unchanged" (no change from previous)

**Keywords for sales advice:**
- buy, sell, hold, recommend, recommendation, position, catch up, current positioning

## Telegram Alert Format

Brief summary sent for every newsletter:
```
🌾 AgResource - 2026-01-08 8:30 AM

Summary: No sales recommended
Sentiment: Bullish (↗️ improving)

Full details in ~/clawd/memory/agresource/
```

## Output Format

### Daily Summary File (`YYYY-MM-DD.md`)

```markdown
# AgResource Newsletter - 2026-01-08 8:30 AM

## Quick Summary
[2-3 sentence overview]

## Key Newsworthy Items
- [Grain production relevant news]
- [Weather tidbits]

## Sales Advice Status
- Corn: [New sales advice / No change / No sales recommended]
- Soybeans: [New sales advice / No change / No sales recommended]

## Current Positions (from end of newsletter)
- [Summary of current positioning]

## Sentiment & Trends
- **Market Mood:** Bullish / Bearish / Neutral
- **Previous Mood:** [from last newsletter]
- **Trend:** Improving / Declining / Stable
- **Weather Impact:** Positive / Negative / Mixed
- **Production Outlook:** Optimistic / Cautious / Uncertain

## Full Content
[Optional: full newsletter content for reference]
```

### Sentiment History File (`sentiment_history.json`)

```json
{
  "last_updated": "2026-01-08T08:30:00",
  "sentiment_history": [
    {
      "date": "2026-01-08",
      "time": "08:30 AM",
      "market_mood": "bullish",
      "weather_impact": "positive",
      "production_outlook": "optimistic",
      "trend_direction": "improving",
      "confidence": "high",
      "key_phrases": ["prices advancing", "favorable weather"],
      "sales_advice": "No sales recommended"
    }
  ]
}
```

## Configuration

**Credentials:** Loaded from environment variables
- `AGRESOURCE_EMAIL`
- `AGRESOURCE_PASSWORD`

**Dependencies:**
- Node.js (built-in on Clawdbot)
- Playwright (installed locally: `/home/brianppetty/clawd/skills/agresource/node_modules/playwright`)

**Schedule:** 4x daily (cron jobs)
- Morning: 8:30 AM ET
- Afternoon: 1:30 PM ET
- Evening: 7:00 PM ET
- Weekend: ~3:00 PM ET

**History window:** Keep last 15-20 newsletters for sentiment tracking

## Notes

- Only send Telegram alerts when sales advice CHANGES
- Always store summaries and sentiment data
- Refine sentiment detection patterns over time
- Evening newsletters include current positioning section
- Login credentials should be handled securely
