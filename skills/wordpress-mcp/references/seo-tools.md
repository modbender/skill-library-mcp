# SEO Engine Tools Reference

Requires **SEO Engine** plugin (free: https://wordpress.org/plugins/seo-engine/).

## SEO Metadata

### mwseo_get_seo_title
- `post_id` (int, required)

### mwseo_set_seo_title
- `post_id` (int, required)
- `title` (string, required): Custom SEO title (overrides post title in search results)

### mwseo_get_seo_excerpt
- `post_id` (int, required)

### mwseo_set_seo_excerpt
- `post_id` (int, required)
- `excerpt` (string, required): Meta description for search results

### mwseo_get_ai_keywords
- `post_id` (int, required): Get AI-extracted keywords

### mwseo_set_ai_keywords
- `post_id` (int, required)
- `keywords` (array, required): Keywords to guide SEO optimization

## SEO Analysis

### mwseo_get_seo_score
Get complete SEO analysis: score (0-100), status, detailed breakdown.
- `post_id` (int, required)

### mwseo_do_seo_scan
Run fresh comprehensive SEO analysis.
- `post_id` (int, required)

### mwseo_get_issues
Get detailed SEO issues for a post.
- `post_id` (int, required)

### mwseo_bulk_seo_scan
Scan multiple posts at once.
- `post_ids` (array, required): Array of post IDs

### mwseo_skip_post
Mark a post to skip SEO analysis.
- `post_id` (int, required)

## Site-Wide SEO

### mwseo_get_seo_statistics
Comprehensive site SEO stats: total posts, average score, score distribution.

### mwseo_get_scored_posts
All posts with SEO scores. Useful for auditing.

### mwseo_get_posts_by_score_range
- `min_score` (int, required)
- `max_score` (int, required)

### mwseo_get_posts_needing_seo
Posts where effective SEO has actual problems (missing titles, thin content, etc.)

### mwseo_get_posts_missing_seo
Posts without custom SEO titles/descriptions (may have auto-generated ones).

### mwseo_check_duplicate_titles
Find posts with identical SEO titles.

### mwseo_search_posts
- `query` (string, required): Search by title or content keywords

### mwseo_get_recent_posts
- `days` (int): Posts from last N days

## Analytics

Requires analytics connection (Google Analytics, Plausible, or Matomo) in SEO Engine settings.

### mwseo_get_analytics_data
- `start_date` (string, required): "YYYY-MM-DD"
- `end_date` (string, required): "YYYY-MM-DD"
- `metrics` (array): "visits", "unique_visitors", "pageviews", "bounce_rate", "avg_session_duration"

### mwseo_get_post_analytics
- `post_id` (int, required)
- `start_date` (string)
- `end_date` (string)

### mwseo_get_analytics_top_countries
- `start_date` (string)
- `end_date` (string)
- `limit` (int)

## Bot Traffic

### mwseo_query_bot_traffic
Flexible query for AI bot traffic with timeline analysis.
- `start_date` (string)
- `end_date` (string)
- `bot` (string): Filter by bot name
- `rollup` (string): "day", "week", "month"

### mwseo_rank_posts_for_bots
Rank posts by bot visit frequency.
- `bot` (string): Specific bot or all
- `limit` (int)

### mwseo_bot_profile
Deep-dive analysis for a specific AI bot.
- `bot` (string, required)

### mwseo_compare_bot_periods
Compare bot traffic between two time periods.
- `period1_start`, `period1_end`, `period2_start`, `period2_end` (strings, required)

### mwseo_bot_mix
Distribution of bot traffic across AI crawlers.

## Other

### mwseo_get_insights
Google PageSpeed Insights for a URL.
- `url` (string, required)

### mwseo_get_robots_txt / mwseo_set_robots_txt
Read/write robots.txt.

### mwseo_generate_sitemap_preview
Preview sitemap URLs without generating the file.

### mwseo_get_post_by_slug
Look up post by URL slug.
- `slug` (string, required)
