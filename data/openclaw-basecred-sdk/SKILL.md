---
name: openclaw-basecred-sdk
version: 1.0.2
author: teeclaw
license: MIT
description: Check human reputation via Ethos Network, Talent Protocol, and Farcaster using the neutral basecred-sdk. Fetches composable reputation data without judgment - raw scores, levels, and signals for identity verification and trust assessment. Use when you need to check someone's onchain credibility, builder/creator scores, or Farcaster quality metrics.
tags: [reputation, identity, ethos, talent, farcaster, basecred, onchain, verification]
metadata:
  openclaw:
    requires:
      bins: [node]
---

# basecred-sdk-skill

**OpenClaw skill for checking human reputation via Ethos Network, Talent Protocol, and Farcaster using the neutral basecred-sdk.**

## Overview

This skill provides a CLI interface to the [@basecred/sdk](https://www.npmjs.com/package/@basecred/sdk) for fetching neutral, composable reputation data from multiple web3 identity providers:

- **Ethos Network** - Social credibility (vouches, reviews, score)
- **Talent Protocol** - Builder and creator scores
- **Farcaster (Neynar)** - Account quality metrics

The SDK is designed to make reputation data **observable without turning it into judgment**. It returns raw scores, levels, and signals—no rankings, no percentiles, no trust verdicts.

## Security

**This skill uses secure, hardcoded credential loading** — see [SECURITY.md](./SECURITY.md) for full audit details.

**TL;DR:**
- ✅ Credentials loaded from `~/.openclaw/.env` (hardcoded path, no directory traversal)
- ✅ Upstream package `@basecred/sdk@0.6.2` audited and clean (MIT licensed, minimal deps)
- ✅ No secrets logged or written to disk
- ✅ Read-only API access (public reputation data)

## Prerequisites

### Required

- Node.js 18+
- OpenClaw runtime

### Optional API Keys

**Environment variables** (in `~/.openclaw/.env`):

```bash
# Optional: Enables Talent Protocol builder/creator scores
TALENT_API_KEY=your_talent_api_key

# Optional: Enables Farcaster quality scores
NEYNAR_API_KEY=your_neynar_api_key
```

**Notes:**
- Ethos Network requires **no API key**
- Without `TALENT_API_KEY`, builder/creator scores will be unavailable
- Without `NEYNAR_API_KEY`, Farcaster scores will be unavailable
- The skill works with partial data (graceful degradation)

**Get API keys:**
- Talent Protocol: https://talentprotocol.com
- Neynar: https://neynar.com

## Installation

```bash
cd ~/.openclaw/workspace/skills/openclaw-basecred-sdk
npm install
```

## Usage

### Basic Check

```bash
./scripts/check-reputation.mjs 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```

**Output (JSON summary):**
```json
{
  "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
  "timestamp": "2026-02-10T07:00:00.000Z",
  "availability": {
    "ethos": "not_found",
    "talent": "available",
    "farcaster": "available"
  },
  "data": {
    "talent": {
      "builderScore": 86,
      "builderLevel": "Practitioner",
      "builderRank": 8648,
      "creatorScore": 103,
      "creatorLevel": "Established",
      "creatorRank": null
    },
    "farcaster": {
      "score": 1,
      "passesQuality": true
    }
  },
  "recency": "recent"
}
```

### Command Options

```bash
# Summary format (default)
./scripts/check-reputation.mjs <address>

# Full unified profile
./scripts/check-reputation.mjs <address> --full

# Human-readable output
./scripts/check-reputation.mjs <address> --human

# JSON output (default)
./scripts/check-reputation.mjs <address> --json

# Show help
./scripts/check-reputation.mjs --help
```

### Examples

**Check vitalik.eth:**
```bash
./scripts/check-reputation.mjs 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```

**Human-readable format:**
```bash
./scripts/check-reputation.mjs 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 --human
```

Output:
```
📊 Reputation Summary for 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
⏰ 2026-02-10T07:00:00.000Z

📡 Data Sources:
   🔍 ethos: not_found
   ✅ talent: available
   ✅ farcaster: available

🛠️  Talent Protocol:
   Builder: 86 (Practitioner) - Rank #8648
   Creator: 103 (Established)

🎭 Farcaster:
   Quality Score: 1
   Passes Threshold: ✅

📅 Recency: recent
```

**Full profile with all data:**
```bash
./scripts/check-reputation.mjs 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 --full
```

## Output Format

### Summary Format (default)

```json
{
  "address": "0x...",
  "timestamp": "ISO-8601",
  "availability": {
    "ethos": "available|not_found|error",
    "talent": "available|not_found|error",
    "farcaster": "available|not_found|error"
  },
  "data": {
    "ethos": {
      "score": 1732,
      "level": "Established",
      "vouches": 5,
      "reviews": { "positive": 12, "neutral": 1, "negative": 0 },
      "hasNegativeReviews": false
    },
    "talent": {
      "builderScore": 86,
      "builderLevel": "Practitioner",
      "builderRank": 8648,
      "creatorScore": 103,
      "creatorLevel": "Established",
      "creatorRank": null
    },
    "farcaster": {
      "score": 0.97,
      "passesQuality": true
    }
  },
  "recency": "recent|stale|dormant"
}
```

### Full Profile Format

See [@basecred/sdk documentation](https://github.com/Callmedas69/basecred/tree/main/packages/sdk#output-schema) for complete schema.

## Data Sources

### Ethos Network

**What it provides:**
- Social credibility score (0-2800)
- Vouches received (trust endorsements)
- Reviews (positive/neutral/negative)
- Semantic credibility level (Untrusted → Renowned)

**No API key required.**

### Talent Protocol

**What it provides:**
- **Builder Score** - Technical/development credibility (0-250+)
- **Creator Score** - Content/creative credibility (0-250+)
- Rank positions (when available)
- Semantic levels (Novice → Master / Emerging → Elite)

**Requires:** `TALENT_API_KEY`

### Farcaster (Neynar)

**What it provides:**
- Account quality score (0-1)
- Quality threshold pass/fail (default: 0.5)

**Requires:** `NEYNAR_API_KEY`

## Availability States

Each data source returns exactly one state:

| State | Meaning |
|-------|---------|
| `available` | Profile exists, data fetched successfully |
| `not_found` | No profile exists for this address |
| `error` | API error or failure |

The skill **never crashes** on missing data. Partial responses are valid and useful.

## Semantic Levels

The SDK derives human-readable levels from raw scores:

**Ethos Credibility Levels:**
- 0-799: Untrusted
- 800-1199: Questionable
- 1200-1399: Neutral
- 1400-1599: Known
- 1600-1799: Established
- 1800-1999: Reputable
- 2000-2199: Exemplary
- 2200-2399: Distinguished
- 2400-2599: Revered
- 2600-2800: Renowned

**Talent Builder Levels:**
- 0-39: Novice
- 40-79: Apprentice
- 80-119: Practitioner
- 120-169: Advanced
- 170-249: Expert
- 250+: Master

**Talent Creator Levels:**
- 0-39: Emerging
- 40-79: Growing
- 80-119: Established
- 120-169: Accomplished
- 170-249: Prominent
- 250+: Elite

## Recency Buckets

Data freshness indicator:

| Bucket | Condition |
|--------|-----------|
| `recent` | Updated within 30 days |
| `stale` | Updated 31-90 days ago |
| `dormant` | Updated more than 90 days ago |

## Testing

Run the test suite with known addresses:

```bash
npm test
```

This tests:
- Vitalik Buterin (vitalik.eth)
- Mr. Tee (main wallet)

## Integration with Other Skills

Import the library in your own scripts:

```javascript
import { checkReputation, getSummary, formatHuman } from './lib/basecred.mjs';

const result = await checkReputation('0x...');
const summary = getSummary(result);
console.log(summary);
```

## Error Handling

The skill uses graceful error handling:

- Invalid address → returns error object with message
- Missing API keys → warns but continues with available sources
- API failures → surfaced via `availability` field
- Network errors → returns error object with details

**Never throws exceptions** - always returns structured data.

## Design Principles

This skill follows the basecred-sdk philosophy:

- **Absence is explicit** - Missing data is declared, never hidden
- **Time matters more than score** - Temporal fields enable continuity analysis
- **Sources are parallel** - No source is "better" than another
- **Data is reported, not judged** - Consumers interpret meaning

## Non-Goals

This skill intentionally does **NOT**:

- Decide trustworthiness
- Rank users against each other
- Compare users
- Produce composite scores
- Replace human judgment

## Performance

- **Average query time:** 1-3 seconds (depends on network + API response times)
- **API calls:** 1-3 concurrent requests (one per enabled source)
- **No rate limiting** - but respect upstream API limits

## Troubleshooting

**"TALENT_API_KEY not found" warning:**
- Add `TALENT_API_KEY=xxx` to `~/.openclaw/.env`
- Or accept that Talent scores will be unavailable

**"NEYNAR_API_KEY not found" warning:**
- Add `NEYNAR_API_KEY=xxx` to `~/.openclaw/.env`
- Or accept that Farcaster scores will be unavailable

**All sources return `not_found`:**
- Address may not have profiles on any platform
- This is valid - absence is data

**Unexpected errors:**
- Check network connectivity
- Verify API keys are valid
- Check upstream API status

## Related Links

- **Source SDK:** https://github.com/Callmedas69/basecred/tree/main/packages/sdk
- **npm package:** https://www.npmjs.com/package/@basecred/sdk
- **Ethos Network:** https://ethos.network
- **Talent Protocol:** https://talentprotocol.com
- **Neynar (Farcaster):** https://neynar.com

## License

MIT

## Author

Built by **teeclaw** for OpenClaw.

---

**Version:** 1.0.1  
**Last Updated:** 2026-02-10  
**SDK Version:** @basecred/sdk@0.6.2
