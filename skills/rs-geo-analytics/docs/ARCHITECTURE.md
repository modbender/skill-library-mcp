# ARCHITECTURE — Rankscale GEO Analytics Skill

**Skill ID:** `rs-geo-analytics` | **Version:** 1.0.1 | **Tickets:** RS-126, ROA-40

This document is a technical reference for skill maintainers, contributors, and ClawhHub reviewers.

---

## Table of Contents

1. [Repository Structure](#repository-structure)
2. [Skill Lifecycle](#skill-lifecycle)
3. [API Flow](#api-flow)
4. [Data Normalization Pipeline](#data-normalization-pipeline)
5. [GEO Interpretation Engine](#geo-interpretation-engine)
6. [ASCII Renderer](#ascii-renderer)
7. [Error Handling Strategy](#error-handling-strategy)
8. [ClawhHub Integration](#clawhhub-integration)
9. [Exported API (for testing)](#exported-api-for-testing)

---

## Repository Structure

```
RS-Skill/
├── rankscale-skill.js        # Main skill logic + GEO Interpretation Module + 7 feature modules
├── SKILL.md                  # OpenClaw skill spec (triggers, flow, output format)
├── .skill                    # ClawhHub metadata manifest (JSON)
├── README.md                 # GitHub landing page
├── USAGE.md                  # Comprehensive usage guide
├── CHANGELOG.md              # Version history
├── IMPLEMENTATION_SUMMARY.md # Builder notes and test results
├── DOCUMENTATION_SUMMARY.md  # Documentation inventory and checklists
├── references/
│   ├── api-integration.md    # Rankscale API endpoint reference (6 endpoints)
│   ├── geo-playbook.md       # GEO interpretation rules R1–R10
│   ├── FEATURES.md           # Feature-by-feature guide with sample outputs
│   ├── COMMANDS.md           # Quick-reference CLI flag table
│   ├── EXAMPLES.md           # Real-world usage examples (live API tested)
│   ├── TROUBLESHOOTING.md    # Common errors, causes, and fixes
│   ├── presentation-style.md # Metric presentation style guide
│   └── onboarding.md         # Expanded onboarding reference (markdown)
├── assets/
│   └── onboarding.md         # New user onboarding walkthrough (ASCII format)
├── scripts/
│   └── validate-skill.js     # ClawhHub validation script (84 checks)
└── docs/
    └── ARCHITECTURE.md       # This file
```

### Key files explained

**`rankscale-skill.js`**  
Single-file implementation. Contains credential resolution, API client, response normalizers, GEO Interpretation Module, ASCII renderer, and CLI entry point. Exports all major functions for unit testing.

**`.skill`**  
JSON metadata used by ClawhHub to register the skill, configure triggers, declare credentials, and specify the onboarding asset.

**`references/geo-playbook.md`**  
The authoritative source of truth for all 10 GEO interpretation rules. The `GEO_RULES` array in `rankscale-skill.js` implements these rules directly. When adding or changing rules, update both files.

---

## Skill Lifecycle

```
User message or CLI invocation
        |
        v
1. Credential Resolution
   - CLI flags > env vars > API key suffix extraction
   - If missing: trigger onboarding prompt and exit
        |
        v
2. Brand Resolution
   - If RANKSCALE_BRAND_ID set: use it directly
   - Else: call GET /v1/metrics/brands
     - If 1 brand: auto-select
     - If multiple: prompt user to select with --discover-brands
        |
        v
3. Data Fetching
   - GET /v1/metrics/report              (sequential, first)
   - GET /v1/metrics/citations           (parallel)
   - GET /v1/metrics/sentiment           (parallel)
   - GET /v1/metrics/search-terms-report (parallel)
   - GET /v1/metrics/engine-data         (parallel, v1.0.1+)
        |
        v
4. Normalization
   - normalizeReport(raw)
   - normalizeCitations(raw)
   - normalizeSentiment(raw)
   - normalizeSearchTerms(raw)
        |
        v
5. GEO Interpretation
   - interpretGeoData({ report, citations, sentiment, terms })
   - Apply rules R1–R10 in order
   - Deduplicate (R2 supersedes R1)
   - Limit to top 5 by severity
        |
        v
6. Feature Module Dispatch
   - Route to one of 7 feature modules based on CLI flag
   - Each module renders its own ASCII output block
        |
        v
7. ASCII Render
   - renderReport({ brand, report, citations, sentiment, terms, insights })
   - 55-char width, sectioned output
        |
        v
7. Output
   - Print to stdout (CLI)
   - Return string (OpenClaw / ClawhHub integration)
```

---

## API Flow

The skill makes up to 5 HTTP requests per invocation. All requests use:

```
Authorization: Bearer <RANKSCALE_API_KEY>
User-Agent: openclaw-rs-geo-analytics/1.0.1
Content-Type: application/json
```

Base URL: `https://rankscale.ai/api/v1`

### Request sequence (pseudo-code)

```
credentials = resolveCredentials()

brands = fetchBrands(credentials)     # optional, only if brandId unknown
brandId = selectBrand(brands)

report  = await fetchReport(brandId)  # sequential (needed for brandName)

[citations, sentiment, terms, engineData] = await Promise.all([
  fetchCitations(brandId),
  fetchSentiment(brandId),
  fetchSearchTerms(brandId),
  fetchEngineData(brandId),            # v1.0.1+
])

data = {
  report:    normalizeReport(report),
  citations: normalizeCitations(citations),
  sentiment: normalizeSentiment(sentiment),
  terms:     normalizeSearchTerms(terms),
}

insights = interpretGeoData(data)
output   = renderReport({ brand, ...data, insights })
```

### Retry logic

Each fetch function applies exponential backoff on failure:

```
attempt 1: immediate
attempt 2: wait 1000ms + jitter(0–200ms)
attempt 3: wait 2000ms + jitter(0–200ms)
attempt 4: wait 4000ms + jitter(0–200ms)
attempt 5: throw ApiError
```

Retried on: HTTP 429, 500, 503, and network timeouts.  
Not retried on: HTTP 401, 403, 404 (these are terminal errors).

---

## Data Normalization Pipeline

The Rankscale API returns different response shapes depending on the account tier and API version. The normalization layer translates all known variants into a consistent internal format.

### `normalizeReport(raw)`

Input variants:

```js
// Standard format
{ score, rank, change, brandName, period, ... }

// Alternate format (some accounts)
{ geoScore, rankPosition, weeklyDelta, visibilityScore, ... }
```

Output:

```js
{ score: number, rank: number, change: number, brandName: string, period: string }
```

### `normalizeSentiment(raw)`

Input variants:

```js
// Format A: floats 0–1
{ positive: 0.61, neutral: 0.29, negative: 0.10 }

// Format B: nested scores 0–100
{ scores: { pos: 61, neu: 29, neg: 10 } }

// Format C: integer %
{ positive: 61, neutral: 29, negative: 10 }
```

Output (always integer-like floats):

```js
{ positive: 61.0, neutral: 29.0, negative: 10.0 }
```

### `normalizeCitations(raw)`

Input variants:

```js
// Standard
{ count, rate, industryAvg, sources: [...] }

// Alternate
{ total, citationRate, benchmarkRate, topSources: [...] }
```

Output:

```js
{ count: number, rate: number, industryAvg: number, sources: array }
```

### `normalizeSearchTerms(raw)`

Input variants:

```js
{ terms: [...] }
{ data: [...] }
{ searchTerms: [...] }
{ results: [...] }
```

Each term is reduced to:

```js
{ query: string, mentions: number }
```

---

## GEO Interpretation Engine

The engine (`interpretGeoData`) takes normalized data and returns an ordered array of insight objects.

### Rule structure

Each rule in `GEO_RULES` is an object:

```js
{
  id: 'R1',
  severity: 'WARN',                    // 'CRIT' | 'WARN' | 'INFO'
  condition: (data) => boolean,        // evaluates against normalized data
  supersedes: null,                    // optional: rule ID this one replaces
  message: (data) => string,           // short headline for ASCII output
  action: (data) => string,            // recommended action text
}
```

### All 10 rules

| ID | Severity | Condition |
|----|----------|-----------|
| R1 | WARN | `citations.rate < 40` |
| R2 | CRIT | `citations.rate < 20` (supersedes R1) |
| R3 | CRIT | `sentiment.negative > 25` |
| R4 | CRIT | `report.score < 40` |
| R5 | WARN | `report.score >= 40 && report.score < 65` |
| R6 | WARN | `report.change < -5` |
| R7 | INFO | `report.change >= 3 && sentiment.positive > 55` |
| R8 | WARN | `detectionRate < 70` |
| R9 | WARN | `competitorDelta > 15` |
| R10 | WARN | `maxEngineScore - minEngineScore > 30` |

### Evaluation flow

```
fired = []

for each rule in GEO_RULES:
  if rule.condition(data):
    if rule.supersedes and fired.includes(rule.supersedes):
      remove superseded rule from fired
    fired.push(rule)

// Sort: CRIT first, then WARN, then INFO
fired.sort(bySeverity)

// Return top 5
return fired.slice(0, 5)
```

### Insight object

```js
{
  id: 'R1',
  severity: 'WARN',
  message: 'Citation rate below 40% target.',
  action: 'Publish 2+ authoritative comparison articles this month.',
}
```

---

## ASCII Renderer

The renderer (`renderReport`) produces a fixed-width text block for output.

### Layout

```
=======================================================  (55 chars)
  RANKSCALE GEO REPORT
  Brand: <name> | <date>
=======================================================
  GEO SCORE:     <score> / 100   [<delta> vs last week]
  CITATION RATE: <rate>%        [Industry avg: <avg>%]
  SENTIMENT:     Pos <p>% | Neu <n>% | Neg <g>%
-------------------------------------------------------
  TOP AI SEARCH TERMS
  <n>. "<query>"    (<mentions> mentions)
  ...
-------------------------------------------------------
  GEO INSIGHTS  [<count> of 5]
  [<SEV>] <message>
         <action wrapped at 40 chars>
  ...
-------------------------------------------------------
  Full report: https://rankscale.ai/dashboard/brands/<id>
=======================================================
```

### Width constraints

- Max 55 characters per line
- Action text wraps at 40 characters (indented 9 spaces)
- Search term queries truncated to 35 characters if longer

---

## Error Handling Strategy

### Error classes

```js
class AuthError extends Error { }     // 401 / 403 — credential problem
class NotFoundError extends Error { } // 404 — brand or resource not found
class ApiError extends Error { }      // 429 / 5xx / network failure
```

### Decision matrix

| HTTP Status | Class | Retried | Behavior |
|-------------|-------|---------|----------|
| 401 | AuthError | No | Show auth error + settings link |
| 403 | AuthError | No | Show auth error + settings link |
| 404 | NotFoundError | No | Suggest `--discover-brands` |
| 429 | ApiError | Yes (backoff) | Exponential retry, max 3 |
| 500 | ApiError | Yes (backoff) | Exponential retry, max 3 |
| 503 | ApiError | Yes (backoff) | Exponential retry, max 3 |
| Timeout | ApiError | Yes (once) | Retry once; show partial data |

### Graceful degradation

If one of the parallel fetches fails (citations, sentiment, or search terms), the skill:

1. Logs a warning in the insights section
2. Renders available data with a note that some metrics are unavailable
3. Does not crash or suppress the full report

---

## ClawhHub Integration

The `.skill` manifest registers the skill with ClawhHub:

```json
{
  "id": "rs-geo-analytics",
  "version": "1.0.1",
  "entrypoint": "rankscale-skill.js",
  "runtime": "node",
  "nodeVersion": ">=16",
  "triggers": [ "rankscale", "geo analytics", "..." ],
  "credentials": [
    { "key": "RANKSCALE_API_KEY", "required": true },
    { "key": "RANKSCALE_BRAND_ID", "required": false }
  ],
  "clawhhub": {
    "category": "Analytics",
    "subcategory": "GEO / AI Search",
    "onboarding": "assets/onboarding.md"
  }
}
```

ClawhHub injects credentials as environment variables before invoking `rankscale-skill.js`.

### Validation

```bash
node scripts/validate-skill.js
```

Runs 84 checks across all files. Must exit 0 before merging or publishing to ClawhHub.

---

## Exported API (for testing)

`rankscale-skill.js` exports the following for unit testing:

```js
const {
  run,
  resolveCredentials,
  fetchBrands,
  fetchReport,
  fetchCitations,
  fetchSentiment,
  fetchSearchTerms,
  fetchEngineData,
  normalizeSentiment,
  normalizeCitations,
  normalizeReport,
  normalizeSearchTerms,
  interpretGeoData,
  analyzeEngineStrength,
  analyzeContentGaps,
  analyzeReputation,
  analyzeEngineMovers,
  analyzeSentimentAlerts,
  analyzeCitations,
  GEO_RULES,
  AuthError,
  NotFoundError,
  ApiError,
} = require('./rankscale-skill.js');
```

### Key invariants for testing

- `normalizeSentiment(null)` returns `{ positive: 0, neutral: 0, negative: 0 }`
- `normalizeReport` handles both standard and alternate field names
- `interpretGeoData` never returns more than 5 insights
- R2 suppresses R1 when citation rate < 20%
- `resolveCredentials` extracts brand ID from the key suffix when `RANKSCALE_BRAND_ID` is unset
