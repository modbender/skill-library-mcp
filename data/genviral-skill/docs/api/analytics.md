# Analytics Commands

## analytics-summary (alias: `get-analytics-summary`)
Get analytics summary with KPIs, trends, and content mix.

```bash
genviral.sh analytics-summary
genviral.sh analytics-summary --range 30d
genviral.sh analytics-summary --start 2026-01-01 --end 2026-01-31
genviral.sh analytics-summary --platforms tiktok,instagram
genviral.sh analytics-summary --accounts TARGET_ID_1,TARGET_ID_2
genviral.sh analytics-summary --json
```

Options:
- `--range` - Date preset: `14d`, `30d`, `90d`, `1y`, `all`
- `--start` / `--end` - Custom date range (YYYY-MM-DD), must use both together
- `--platforms` - Comma-separated platform filter
- `--accounts` - Comma-separated analytics target IDs

Returns:
- `kpis` - publishedVideos, activeAccounts, views, likes, comments, shares, saves, engagementRate (with deltas)
- `interactionSeries` - Daily interactions
- `engagementSeries` - Daily engagement rate
- `postingHeatmap` - Daily post counts
- `postingStreak` - Consecutive posting days
- `contentMix` - Posts by platform

---

## analytics-posts (alias: `list-analytics-posts`)
List post-level analytics.

```bash
genviral.sh analytics-posts
genviral.sh analytics-posts --range 90d --sort-by views --sort-order desc --limit 25
genviral.sh analytics-posts --start 2026-01-01 --end 2026-01-31 --platforms tiktok
genviral.sh analytics-posts --json
```

Options:
- `--range` - Date preset: `14d`, `30d`, `90d`, `1y`, `all`
- `--start` / `--end` - Custom date range
- `--platforms`, `--accounts` - Filters
- `--sort-by` - `published_at`, `views`, `likes`, `comments`, `shares`
- `--sort-order` - `asc` or `desc`
- `--limit` (max 100), `--offset`

---

## analytics-targets
List tracked analytics accounts.

```bash
genviral.sh analytics-targets
genviral.sh analytics-targets --json
```

---

## analytics-target-create
Add a new tracked account.

```bash
genviral.sh analytics-target-create --platform tiktok --identifier @brand
genviral.sh analytics-target-create --platform instagram --identifier @brand --alias "Brand HQ"
```

Options: `--platform` (tiktok/instagram/youtube, required), `--identifier` (required), `--alias`

**Propagation note:** New targets are not always queryable instantly. Wait ~30-90 seconds after `analytics-target-create` before expecting full data population in summary/posts endpoints.

---

## analytics-target
Get details for a single analytics target.

```bash
genviral.sh analytics-target --id TARGET_ID
```

---

## analytics-target-update
```bash
genviral.sh analytics-target-update --id TARGET_ID --display-name "New Name"
genviral.sh analytics-target-update --id TARGET_ID --favorite true
genviral.sh analytics-target-update --id TARGET_ID --clear-display-name
genviral.sh analytics-target-update --id TARGET_ID --refresh-policy-json '{"freeDailyRefresh":true}'
genviral.sh analytics-target-update --id TARGET_ID --clear-refresh-policy
```

---

## analytics-target-delete
```bash
genviral.sh analytics-target-delete --id TARGET_ID
```

---

## analytics-target-refresh
Trigger a refresh for an analytics target.

```bash
genviral.sh analytics-target-refresh --id TARGET_ID
```

Returns: refresh ID, status, `wasFree`.

**Freshness note:** A refresh is asynchronous. After triggering `analytics-target-refresh`, wait ~30-90 seconds, then poll `analytics-refresh --id REFRESH_ID` until `status=completed` before trusting the updated numbers.

---

## analytics-refresh | get-analytics-refresh
Check refresh status.

```bash
genviral.sh analytics-refresh --id REFRESH_ID
```

Returns: `status` (pending/processing/completed/failed), `credits_used`, `free_refresh_used`, `started_at`, `completed_at`, `error`.

---

## analytics-workspace-suggestions (alias: `get-analytics-workspace-suggestions`)
List other workspace/personal scopes with tracked accounts.

```bash
genviral.sh analytics-workspace-suggestions
genviral.sh get-analytics-workspace-suggestions
genviral.sh analytics-workspace-suggestions --json
```

---

## trend-brief (alias: `get-trend-brief`)
Generate a one-call TikTok trend brief for a keyword (hashtags, sounds, creators, posting windows, hook angles, and sample videos).

```bash
genviral.sh trend-brief --keyword "morning routine"
genviral.sh trend-brief --keyword "fitness" --range 24h --limit 15
genviral.sh get-trend-brief --keyword "grwm" --range 30d --json
```

Options:
- `--platform` - currently only `tiktok` (default)
- `--keyword` - required trend query seed
- `--limit` - number of returned sample videos (`1..30`, default `10`)
- `--range` - `24h`, `7d`, or `30d` (default `7d`)
- `--json` - print only the `.data` payload

Returns:
- `summary.top_hashtags`, `summary.top_sounds`, `summary.top_creators`, `summary.posting_windows_utc`
- `recommendations.hook_angles`, `recommendations.hashtags`, `recommendations.sounds`
- `evidence.sample_videos`

Caching:
- Cached for ~3 hours by `platform + keyword + range`
- `limit` changes only `evidence.sample_videos` length in the final response

### Niche Research Playbook (fast)

Use this when asked to "research a niche":

```bash
# 1) Baseline trend picture
genviral.sh trend-brief --keyword "YOUR NICHE" --range 7d --limit 10

# 2) Fresh momentum check
genviral.sh trend-brief --keyword "YOUR NICHE" --range 24h --limit 10
```

Then combine with competitor deep-dive (`docs/references/competitor-research.md`) and output:
- top 5 hashtags
- top 3 sounds
- 2 best posting windows (UTC)
- 3 hook angles to test
- 1 gap competitors are missing
