---
name: ceorater
description: "Get institutional-grade CEO performance analytics for S&P 500 companies. Proprietary scores: CEORaterScore (composite), AlphaScore (market outperformance), RevenueCAGRScore (revenue growth), CompScore (compensation efficiency). Underlying data includes Total Stock Return (TSR) vs. S&P 500 (SPY), average annual returns, CEO total compensation (most recent fiscal year from proxy filings), and tenure-adjusted Revenue CAGR. Each record includes CEO name, company name, ticker, sector, industry, and tenure dates. Coverage: 500+ CEOs, updated daily. For live record count and last refresh timestamp, call GET /v1/meta. Useful for investment research, due diligence, and executive compensation analysis."
homepage: https://www.ceorater.com
disable-model-invocation: true
requires:
  env:
    - CEORATER_API_KEY
primaryEnv: CEORATER_API_KEY
triggers: ["CEO performance", "CEORater", "CEO score", "CEO rating", "executive performance", "CEO compensation", "AlphaScore", "CompScore", "TSR", "total stock return"]
metadata: {"openclaw":{"requires":{"env":["CEORATER_API_KEY"]},"primaryEnv":"CEORATER_API_KEY","homepage":"https://www.ceorater.com"},"pricing":{"model":"subscription","individual":"$99/month per user for research and analysis","enterprise":"Contact sales@ceorater.com for proprietary model integration, AI/ML training, or product development"},"provider":{"name":"CEORater","url":"https://www.ceorater.com","support":"support@ceorater.com","sales":"sales@ceorater.com"}}
---
# CEORater Skill

Query CEO performance data for S&P 500 and major U.S. public companies via the CEORater API.

## Prerequisites

1. Get an API key at https://www.ceorater.com/api-docs.html ($99/month per user)
2. Set the environment variable: `CEORATER_API_KEY=zpka_your_key_here`

**Licensing Note:** Self-serve API access permits individual research and analysis. Integrating CEORater data into proprietary firm models, AI/ML training, or building products requires an Enterprise Agreement — contact sales@ceorater.com.

## Available Metrics

| Metric | Range | Description |
|--------|-------|-------------|
| CEORaterScore | 0-100 | Composite CEO effectiveness rating |
| AlphaScore | 0-100 | Performance vs. market benchmark |
| RevenueCAGRScore | 0-100 | Tenure-adjusted revenue growth percentile |
| CompScore | A-F | Compensation efficiency grade |
| TSR During Tenure | % | Total Stock Return during CEO tenure |
| TSR vs. S&P 500 | % | Performance relative to S&P 500 (SPY) |
| CEO Compensation | $M | Total compensation from most recent proxy filing |
| Revenue CAGR | % | Tenure-adjusted compound annual revenue growth |

## API Endpoints

### Get CEO by Ticker
```bash
curl -H "Authorization: Bearer $CEORATER_API_KEY" \
  "https://api.ceorater.com/v1/ceo/AAPL?format=raw"
```

### Search CEOs
```bash
curl -H "Authorization: Bearer $CEORATER_API_KEY" \
  "https://api.ceorater.com/v1/search?q=technology&format=raw"
```

### List All CEOs
```bash
curl -H "Authorization: Bearer $CEORATER_API_KEY" \
  "https://api.ceorater.com/v1/ceos?limit=100&format=raw"
```

### Get Metadata (live record count + last refresh timestamp)
```bash
curl -H "Authorization: Bearer $CEORATER_API_KEY" \
  "https://api.ceorater.com/v1/meta"
```

## Usage Instructions

When the user asks about CEO performance, ratings, or executive compensation:

1. **Single CEO lookup:** Use the `/v1/ceo/{ticker}` endpoint
2. **Sector/industry analysis:** Use `/v1/search?q={query}` 
3. **Bulk data:** Use `/v1/ceos?limit=N`

Always use `format=raw` for numeric values suitable for calculations.

### Example Queries

- "What's the CEORaterScore for Tim Cook?" → GET /v1/ceo/AAPL
- "Show me technology sector CEOs" → GET /v1/search?q=technology
- "Who are the top-rated CEOs?" → GET /v1/ceos, sort by ceoraterScore
- "Compare Tim Cook vs Satya Nadella" → GET /v1/ceo/AAPL and /v1/ceo/MSFT

## Response Format (raw)

```json
{
  "companyName": "Apple Inc.",
  "ticker": "AAPL",
  "sector": "Technology",
  "industry": "Computer Manufacturing",
  "ceo": "Tim Cook",
  "founderCEO": false,
  "ceoraterScore": 87,
  "alphaScore": 93.5,
  "revenueCagrScore": 75.2,
  "revenueCagr": 0.042,
  "compScore": "C",
  "tsrMultiple": 22.23,
  "tenureYears": 14.4,
  "avgAnnualTsrRatio": 1.55,
  "compPer1PctTsrMM": 0.482,
  "tsrVsSpyRatio": 15.64,
  "avgAnnualVsSpyRatio": 1.09,
  "compensationMM": 74.6
}
```

## Error Handling

| Code | Meaning |
|------|---------|
| 401 | Missing or invalid API key |
| 404 | Ticker not found |
| 400 | Bad request parameters (for example, missing `q` on search) |
| 429 | Rate limited, retry with backoff |

## Helper Script

For convenience, use `{baseDir}/scripts/ceorater.sh`:

```bash
# Get single CEO
{baseDir}/scripts/ceorater.sh get AAPL

# Search
{baseDir}/scripts/ceorater.sh search "healthcare"

# List top N
{baseDir}/scripts/ceorater.sh list 20
```

## Data Coverage

- 500+ CEOs, including S&P 500 constituents
- Live record count and refresh timestamp are available via `GET /v1/meta`
- Updated daily on weekdays after U.S. market close
- Safe to cache responses for up to 24 hours

## More Information

- Documentation: https://www.ceorater.com/api-docs.html
- Agent manifest: https://www.ceorater.com/.well-known/agent.json
- Support: support@ceorater.com
- Enterprise sales: sales@ceorater.com
