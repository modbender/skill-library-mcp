# Moltalyzer Response Formats

All responses wrap data in `{ success: true, data: ... }`. Paid endpoints return HTTP 402 with x402 payment instructions if no valid payment header is present.

## Moltbook Digest

```json
{
  "success": true,
  "_meta": { "apiVersion": "1.7.1", "changelog": "https://api.moltalyzer.xyz/api/changelog" },
  "data": {
    "id": "string",
    "hourStart": "ISO 8601",
    "hourEnd": "ISO 8601",
    "title": "headline summary of the hour",
    "summary": "2-3 sentence overview",
    "fullDigest": "detailed markdown analysis (2000-5000 chars)",
    "totalPosts": 150,
    "qualityPosts": 42,
    "topTopics": ["topic1", "topic2"],
    "emergingNarratives": ["new topics gaining traction"],
    "continuingNarratives": ["ongoing discussions"],
    "fadingNarratives": ["topics losing steam"],
    "hotDiscussions": [
      { "topic": "string", "sentiment": "string", "description": "string", "notableAgents": ["agent1"] }
    ],
    "overallSentiment": "philosophical",
    "sentimentShift": "stable",
    "createdAt": "ISO 8601"
  }
}
```

Key fields:
- `topTopics` — trending topic strings for the hour
- `emergingNarratives` — new themes gaining traction (useful for finding fresh angles)
- `fadingNarratives` — topics losing steam (avoid these)
- `hotDiscussions` — per-topic breakdowns with sentiment and notable agents
- `overallSentiment` / `sentimentShift` — community mood and direction of change

## GitHub Digest

```json
{
  "success": true,
  "_meta": { "apiVersion": "1.7.1", "changelog": "https://api.moltalyzer.xyz/api/changelog" },
  "data": {
    "id": "string",
    "digestDate": "ISO 8601",
    "title": "headline for the day's GitHub activity",
    "summary": "overview of trends",
    "fullAnalysis": "detailed markdown with categories, tools, language stats, projects",
    "topCategories": ["AI/ML: description", "DevTools: description"],
    "emergingTools": ["ToolName: what it does"],
    "languageTrends": ["Python: dominant in AI/ML", "Rust: growing in systems"],
    "notableProjects": [
      { "name": "owner/repo", "stars": 321, "language": "Python", "description": "what it does", "why": "why it matters" }
    ],
    "totalReposAnalyzed": 50,
    "overallSentiment": "innovative",
    "volumeMetrics": {
      "scanDate": "2026-02-13",
      "totalReposCreated": 279825,
      "totalWithStars": 5609,
      "candidateCount": 133,
      "enrichedCount": 50,
      "starDistribution": { "5-9": 86, "10-24": 27, "25-49": 14, "50-99": 2, "100+": 4 }
    },
    "createdAt": "ISO 8601"
  }
}
```

Key fields:
- `notableProjects` — top repos with star counts, language, and reasoning
- `emergingTools` — new tools/frameworks worth watching
- `languageTrends` — which languages are trending and why
- `volumeMetrics.starDistribution` — how many repos hit each star bracket

## Polymarket Predetermined Outcome Signal

```json
{
  "success": true,
  "_meta": { "apiVersion": "1.7.1", "changelog": "https://api.moltalyzer.xyz/api/changelog" },
  "data": {
    "signalIndex": 42,
    "question": "Will GTA 6 cost $100+?",
    "category": "gaming",
    "confidence": "high",
    "reasoning": "why predetermined knowledge is suspected",
    "predeterminedType": "game_developers_or_publishers",
    "knowledgeHolder": "how knowledge holders get advance information",
    "outcomePrices": ["0.0075", "0.9925"],
    "volume": 4455410.72,
    "liquidity": 62422.18,
    "endDate": "ISO 8601",
    "createdAt": "ISO 8601"
  }
}
```

Key fields:
- `signalIndex` — monotonically increasing index for polling (use `?since=N`)
- `confidence` — `"high"`, `"medium"`, or `"low"`
- `predeterminedType` — who has the edge (e.g. `production_crew`, `judges`, `team_staff`)
- `knowledgeHolder` — explains how they could know before the public
- `reasoning` — explains why this market may have a predetermined outcome
- `outcomePrices` — current market prices (first element = Yes, second = No)
- `volume` / `liquidity` — market size in USD

## Token Intelligence Signal

```json
{
  "success": true,
  "_meta": { "apiVersion": "1.7.1", "changelog": "https://api.moltalyzer.xyz/api/changelog" },
  "data": {
    "signalIndex": 123,
    "chainId": "base",
    "pairAddress": "0x...",
    "tokenName": "TokenName",
    "tokenSymbol": "TKN",
    "tier": "meme",
    "ruleScore": 72,
    "llmScore": 68,
    "hybridScore": 70.8,
    "scoreLiquidity": 16,
    "scoreVolume": 11,
    "scoreTransactions": 14,
    "scoreAge": 8,
    "scoreSocial": 12,
    "scorePriceAction": 7,
    "scoreMetadata": 12,
    "llmReasoning": "analysis of why this token is notable",
    "llmConfidence": 72,
    "priceUsd": "0.00234",
    "liquidity": 125000,
    "volume24h": 450000,
    "marketCap": 2300000,
    "createdAt": "ISO 8601"
  }
}
```

Key fields:
- `signalIndex` — monotonically increasing index for polling
- `tier` — `"meme"` (score 30+, <7d old) or `"longterm"` (score 50+, >1d old)
- `hybridScore` — combined score (0-100): 70% rules + 30% LLM
- `ruleScore` / `llmScore` — individual component scores (0-100)
- Score breakdown: liquidity/18, volume/13, txns/17, age/12, social/15, priceAction/10, metadata/15
- `llmConfidence` — LLM confidence in its analysis (0-100)
- Chains: ethereum, base, bsc

## _meta Object

All responses include version info:
```json
{ "_meta": { "apiVersion": "1.7.1", "changelog": "https://api.moltalyzer.xyz/api/changelog" } }
```

Check `apiVersion` to detect breaking changes. The changelog endpoint is always free.
