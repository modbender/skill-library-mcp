---
name: pain-point-finder
description: >-
  Discover pain points, frustrations, and unmet needs on Reddit using PullPush API.
  No API keys required. Use to find startup ideas backed by real user complaints.
metadata: {"clawdbot":{"emoji":"🔬","requires":{"bins":["node"]}}}
---

# Pain Point Finder

Discover validated pain points on Reddit. Searches for frustrations, complaints, and unmet needs, then analyzes comment threads for agreement signals and failed solutions. Powered by PullPush API — no API keys needed.

## Workflow

Follow these 4 phases in order. Each phase builds on the previous.

### Phase 1: Discover Subreddits

Find the right subreddits for the user's domain.

```bash
node {baseDir}/scripts/pain-points.mjs discover --domain "<user's domain>" --limit 8
```

Example:
```bash
node {baseDir}/scripts/pain-points.mjs discover --domain "project management" --limit 8
```

Take the top 3-5 subreddits from the output for phase 2.

### Phase 2: Scan for Pain Points

Broad search across discovered subreddits.

```bash
node {baseDir}/scripts/pain-points.mjs scan \
  --subreddits "<sub1>,<sub2>,<sub3>" \
  --domain "<domain>" \
  --days 90 \
  --limit 20
```

Example:
```bash
node {baseDir}/scripts/pain-points.mjs scan \
  --subreddits "projectmanagement,SaaS,smallbusiness" \
  --domain "project management" \
  --days 90 \
  --limit 20
```

Review the scored posts. Posts with high `painScore` and high `num_comments` are the best candidates for deep analysis.

### Phase 3: Deep-Dive Analysis

Analyze comment threads of top posts for agreement and solution signals.

Single post:
```bash
node {baseDir}/scripts/pain-points.mjs deep-dive --post <post_id>
```

Top N from scan output:
```bash
node {baseDir}/scripts/pain-points.mjs deep-dive --from-scan <scan_output.json> --top 5
```

Look at the `validationStrength` field:
- **strong**: widespread, validated pain (agreementRatio > 0.20, 10+ agreements)
- **moderate**: notable pain with some validation
- **weak**: some signal but limited agreement
- **anecdotal**: one person's complaint, needs more evidence

### Phase 4: Synthesis (you do this)

For each validated pain point, present a structured proposal:

1. **Problem**: One-sentence description of the pain
2. **Evidence**: Top quotes + agreement count + subreddit
3. **Who feels this**: Type of person/business affected
4. **Current solutions & gaps**: What people have tried (from `solutionAttempts`) and why it fails
5. **Competitive landscape**: Tools mentioned (from `mentionedTools`)
6. **Opportunity**: What's missing in current solutions
7. **Idea sketch**: Brief product/service concept
8. **Validation**: strong/moderate/weak + data backing it

## Options Reference

### discover
| Flag | Default | Description |
|------|---------|-------------|
| `--domain` | required | Domain to explore |
| `--limit` | 10 | Max subreddits to return |

### scan
| Flag | Default | Description |
|------|---------|-------------|
| `--subreddits` | required | Comma-separated subreddit list |
| `--domain` | | Domain for extra search queries |
| `--days` | 365 | How far back to search |
| `--minScore` | 1 | Min post score filter |
| `--minComments` | 3 | Min comment count filter |
| `--limit` | 30 | Max posts to return |
| `--pages` | 2 | Pages per query (more = deeper, slower) |

### deep-dive
| Flag | Default | Description |
|------|---------|-------------|
| `--post` | | Single post ID or Reddit URL |
| `--from-scan` | | Path to scan output JSON |
| `--stdin` | | Read scan JSON from stdin |
| `--top` | 10 | How many posts to analyze from scan |
| `--maxComments` | 200 | Max comments to fetch per post |

## Rate Limits

The script self-limits to 1 request/sec, 30/min, 300/run. If PullPush is slow or returns errors, it retries with exponential backoff. Progress is logged to stderr.

## Tips

- Start broad with `--days 90` then narrow to `--days 30` for recent trends
- High `num_comments` + high `score` = validated pain (many people agree)
- High `painScore` + low `num_comments` = niche pain (worth investigating)
- The `mentionedTools` in deep-dive output maps the competitive landscape
- Posts with `validationStrength: "strong"` are the best startup candidates
