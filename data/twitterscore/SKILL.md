---
name: twitterscore
description: Research, analyze, and track Twitter influence with TwitterScore.io API. Get scores, analyze followers, track growth, and compare accounts.
---

# TwitterScore Skill

Use `twitterscore` to research Twitter accounts, analyze influence scores, track follower growth, and compare accounts using the TwitterScore.io API.

## Setup

Requires a TwitterScore API key. Get one at [twitterscore.io/api/prices](https://twitterscore.io/api/prices?i=9720).

```bash
# Set API key
export TWITTERSCORE_API_KEY="your_api_key"

# Or configure via OpenClaw
openclaw config set twitterscore.api_key your_api_key
```

## Commands

### score
Get TwitterScore for an account.

```bash
# By username (default)
twitterscore score elonmusk

# By Twitter ID
twitterscore score --id 44196397

# Output as JSON
twitterscore score elonmusk --json
```

**Output:**
```
@elonmusk (Elon Musk)
Twitter ID: 44196397
Twitter Score: 1000.0/1000
```

### info
Get detailed account information.

```bash
twitterscore info elonmusk
```

**Output:**
```
@elonmusk
Name: Elon Musk
Description: ...
Followers: 199,987,720
Profile: [image URL]
```

### bulk
Check up to 50 accounts at once.

```bash
twitterscore bulk coinbase binance paradigm a16zcrypto

# From file
twitterscore bulk --file accounts.txt
```

### followers
Get and analyze followers.

```bash
# Top followers by score
twitterscore followers elonmusk --top 10

# Paginated list
twitterscore followers elonmusk --page 1 --size 25

# Filter by category (1=Venture Capitals)
twitterscore followers elonmusk --category 1

# Filter by tag (22=Ethereum)
twitterscore followers elonmusk --tag 22

# Filter by tag category (3=Ecosystems)
twitterscore followers elonmusk --tag-category 3
```

### diff
Track score changes.

```bash
twitterscore diff elonmusk
```

**Output:**
```
Score Changes for @elonmusk:
Week: +8 (2024-09-26 → 2024-10-03)
Month: +9 (2024-09-03 → 2024-10-03)
```

### history
Get follower count history.

```bash
# Last 30 days (default)
twitterscore history elonmusk

# Custom periods
twitterscore history elonmusk --period 7d    # 7 days
twitterscore history elonmusk --period 180d  # 6 months
twitterscore history elonmusk --period 1y    # 1 year
twitterscore history elonmusk --period all   # All time

# Export to CSV
twitterscore history elonmusk --export growth.csv
```

### categories
List all follower categories.

```bash
twitterscore categories
```

**Output:**
```
ID  Name
1   Venture Capitals
2   Founders
3   Projects
4   Exchanges
5   Auditors
7   Media
8   Influencers
9   Angels
10  Trading
```

### tags
List all available tags.

```bash
# All tags
twitterscore tags

# Paginated
twitterscore tags --page 1 --size 25
```

### analyze
Analyze followers by categories and tags.

```bash
# Followers by category
twitterscore analyze elonmusk --by-category

# Followers by tag
twitterscore analyze elonmusk --by-tag
```

### limits
Check your API usage and limits.

```bash
twitterscore limits
```

**Output:**
```
Plan: Pro
Monthly: 10,700 / 200,000 (189,300 remaining)
Resets: 2025-05-12
Per minute: 60 requests
```

## Options

### Global Flags

| Flag | Description |
|------|-------------|
| `--api-key KEY` | Override API key |
| `--json` | Output as JSON |
| `--csv` | Output as CSV |
| `--quiet` | Minimal output |

### Common Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--page N` | Page number | 1 |
| `--size N` | Items per page (max 50) | 10 |
| `--category ID` | Filter by category ID | - |
| `--tag ID` | Filter by tag ID | - |
| `--tag-category ID` | Filter by tag category | - |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `TWITTERSCORE_API_KEY` | Your TwitterScore API key |
| `TWITTERSCORE_BASE_URL` | API base URL (optional) |

## Tips

### Rate Limiting
- Max 60 requests/minute
- Use bulk operations when checking multiple accounts
- Cache results for frequently checked accounts

### Efficient Queries
```bash
# ❌ Slow: Individual requests
for user in coinbase binance paradigm; do
  twitterscore score $user
done

# ✅ Fast: Bulk request
twitterscore bulk coinbase binance paradigm
```

### Exporting Data
```bash
# Export follower analysis to CSV
twitterscore followers elonmusk --top 100 --csv > top_followers.csv

# Export growth history
twitterscore history elonmusk --period 1y --export yearly_growth.csv
```

## API Reference

Base URL: `https://twitterscore.io/api/v1`

See [TwitterScore API Documentation](https://twitterscore.gitbook.io/twitterscore/developers/api-documentation) for full API details.

## Troubleshooting

### "API key not configured"
Set your API key:
```bash
export TWITTERSCORE_API_KEY="your_key"
```

### "Rate limit exceeded"
Wait a minute or check your plan limits:
```bash
twitterscore limits
```

### "Account not found"
The account may be deleted, private, or suspended. Try using Twitter ID instead of username.

## Examples

### Research Competitors
```bash
# Get scores for top VCs
twitterscore bulk a16zcrypto paradigm coinbasecms dragonfly_xyz

# Analyze their followers
for vc in a16zcrypto paradigm; do
  echo "=== $VC ==="
  twitterscore analyze $vc --by-category
done
```

### Track Growth
```bash
# Save current state
twitterscore history myaccount --period all --export before_campaign.csv

# ... run marketing campaign ...

# Compare after
twitterscore history myaccount --period 30d --export after_campaign.csv
```

### Find Influencers
```bash
# Get top followers of major accounts
twitterscore followers elonmusk --top 100 --category 8 > influencers.txt
```
