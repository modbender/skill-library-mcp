---
name: fear-and-greed
description: Access the Alternative.me Crypto Fear & Greed Index. Use this tool to anchor your baseline market sentiment analysis, determining whether the broader retail market is in a state of Extreme Fear (capitulation risk) or Extreme Greed (euphoria/correction risk).
homepage: https://alternative.me/crypto/fear-and-greed-index/
metadata:
  {
    "openclaw": {
      "emoji": "😨",
      "requires": {},
    },
  }
---

# Crypto Fear & Greed Index API

Access the global crypto market sentiment baseline using the free Alternative.me API.

## API Endpoint

Base URL: `https://api.alternative.me/fng/`

The API requires no authentication or API keys. 

### Get Current Sentiment

Fetch the latest daily Fear & Greed metric (0-100 score + classification label):

```bash
curl -s "https://api.alternative.me/fng/?limit=1"
```

Returns a JSON structure containing:
- `value`: The 0-100 numerical score.
- `value_classification`: The textual label (e.g. "Extreme Fear", "Fear", "Greed", "Extreme Greed").
- `timestamp`: Unix epoch of the data point.

## Common Use Cases

### Sentiment Baseline Anchoring
When conducting qualitative sentiment analysis on news headlines or on-chain flows, first fetch the Fear & Greed index to anchor your assumptions about retail psychology.

1. If `value` < 25 (Extreme Fear): The market is highly sensitive to bearish catalysts. Price may be artificially depressed.
2. If `value` > 75 (Extreme Greed): The market is euphoric and ignoring risk. High danger of sudden liquidations or corrections.

