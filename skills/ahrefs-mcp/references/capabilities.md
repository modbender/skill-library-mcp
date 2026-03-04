# Ahrefs MCP Capabilities Reference

Comprehensive guide to data available through Ahrefs MCP.

## Table of Contents

1. [Site Explorer](#site-explorer)
2. [Keywords Explorer](#keywords-explorer)
3. [Rank Tracker](#rank-tracker)
4. [Site Audit](#site-audit)
5. [Content Explorer](#content-explorer)

---

## Site Explorer

Analyze any website or URL's backlink profile, organic traffic, and overall SEO health.

### Domain-Level Metrics

**Available data:**
- Domain Rating (DR) - Domain authority score (0-100)
- URL Rating (UR) - Individual page authority
- Ahrefs Rank - Global ranking position
- Referring domains - Total unique domains linking
- Backlinks - Total backlink count
- Dofollow backlinks - Links passing PageRank
- Organic traffic - Estimated monthly visitors from search
- Organic keywords - Number of ranking keywords
- Traffic value - Estimated value of organic traffic

**Example queries:**
```
"Get domain metrics for example.com"
"Compare DR and organic traffic for example.com and competitor.com"
"What's the Ahrefs Rank of mysite.com?"
```

### Backlink Analysis

**Available data:**
- Backlink list with source URLs
- Anchor text distribution
- Link types (dofollow, nofollow, ugc, sponsored)
- Referring pages
- Link attributes and context
- First seen / last checked dates
- Traffic and DR of linking domains

**Example queries:**
```
"Show me top backlinks for example.com"
"Get anchor text distribution for mysite.com"
"Find all nofollow links pointing to example.com"
```

### Organic Search Performance

**Available data:**
- Top organic keywords
- Keyword positions and URLs
- Search volume and traffic estimates
- Position history and changes
- SERP features won
- Organic competitors

**Example queries:**
```
"What are the top 50 organic keywords for example.com?"
"Show me keywords where mysite.com ranks in top 10"
"Which pages get the most organic traffic on example.com?"
```

### Referring Domains

**Available data:**
- List of all referring domains
- Domain Rating of each referrer
- Number of backlinks from each domain
- Dofollow vs nofollow status
- First/last seen dates
- Link types and contexts

**Example queries:**
```
"List all referring domains for example.com with DR > 50"
"How many unique domains link to mysite.com?"
"Show new referring domains in the last 30 days"
```

### Pages Analysis

**Available data:**
- Top pages by organic traffic
- Best by links
- URL Rating distribution
- Individual page backlink profiles
- Ranking keywords per page

**Example queries:**
```
"What are the top 20 pages by organic traffic on example.com?"
"Show me the most linked-to pages on mysite.com"
"Get backlinks for specific URL: example.com/blog/post"
```

---

## Keywords Explorer

Research keywords, analyze search volumes, and understand SERP landscapes.

### Keyword Metrics

**Available data:**
- Search volume (monthly)
- Keyword Difficulty (KD) - Ranking difficulty score (0-100)
- Cost Per Click (CPC) - Paid search value
- Traffic potential - Estimated traffic for #1 position
- Return rate - How often users search again
- Clicks - Average clicks per search
- Parent topic - Broader topic grouping
- SERP features present

**Example queries:**
```
"Get search volume and KD for 'best running shoes'"
"Show me metrics for these keywords: [list]"
"What's the traffic potential for 'seo tools'?"
```

### Keyword Ideas

**Available data:**
- Related keywords
- Questions containing keyword
- Also rank for (keywords top-ranking pages also rank for)
- Search suggestions
- Newly discovered keywords

**Example queries:**
```
"Give me 100 related keywords for 'digital marketing'"
"What questions do people ask about 'keto diet'?"
"Find keywords related to 'project management software'"
```

### SERP Analysis

**Available data:**
- Current top 100 ranking pages
- Domain Rating of ranking domains
- URL Rating of ranking pages
- Estimated traffic to each result
- Backlinks to ranking pages
- SERP features (featured snippets, PAA, etc.)

**Example queries:**
```
"Show me the SERP for 'best laptops 2024'"
"What's the average DR of pages ranking for 'seo agency'?"
"Which SERP features appear for 'how to lose weight'?"
```

### Keyword Difficulty Analysis

**Available data:**
- Detailed KD breakdown
- Referring domains needed to rank
- Backlink profile strength required
- Ranking page analysis

**Example queries:**
```
"Is 'best vpn' a competitive keyword?"
"How hard is it to rank for 'workout routines'?"
"Compare keyword difficulty across this list: [keywords]"
```

---

## Rank Tracker

Monitor keyword positions and track ranking changes over time.

### Position Tracking

**Available data (from existing rank tracker projects):**
- Current positions for tracked keywords
- Position changes (daily, weekly, monthly)
- Visibility score
- Average position
- Position distribution
- SERP feature tracking
- Competitor positions

**Example queries:**
```
"Show me current rankings for project 'Main Website'"
"What keywords moved in the last 7 days?"
"Get visibility score for my rank tracker project"
```

### Ranking Changes

**Available data:**
- Position gains and losses
- Keywords entering/leaving top 10, 20, 50, 100
- New ranking keywords
- Lost rankings
- Position volatility

**Example queries:**
```
"Which keywords gained positions this week?"
"Show me keywords that dropped out of top 10"
"What's my biggest ranking improvement this month?"
```

### Competitor Tracking

**Available data:**
- Competitor positions for same keywords
- Comparative visibility
- Position gaps
- Competitor movement

**Example queries:**
```
"Compare my rankings to competitor.com"
"Where do competitors rank better than me?"
"Show me visibility comparison across tracked competitors"
```

**Note:** Rank tracker data is based on projects you've already configured in your Ahrefs account. You cannot create new tracking projects via MCP—set those up in the Ahrefs web interface first.

---

## Site Audit

Technical SEO analysis and site health monitoring.

### Site Health Score

**Available data:**
- Overall health score
- Critical issues count
- Warnings and notices
- Crawl statistics
- Issue trends over time

**Example queries:**
```
"What's the site health score for mysite.com?"
"How many critical issues are on example.com?"
"Show me site audit summary for mysite.com"
```

### Issue Breakdown

**Available data:**
- Issues by category (crawl, performance, content, security, etc.)
- Severity classification (critical, warning, notice)
- Affected pages per issue
- Priority recommendations
- Issue descriptions and fix guidance

**Example queries:**
```
"List all critical issues from site audit"
"Show me duplicate content issues"
"What are the top 10 priority fixes for mysite.com?"
```

### Crawl Data

**Available data:**
- Total pages crawled
- Crawlable vs non-crawlable pages
- Redirect chains
- Broken links (404s, 5xx errors)
- Response codes distribution

**Example queries:**
```
"How many pages were crawled in last audit?"
"Show me all 404 errors on mysite.com"
"List redirect chains found in audit"
```

### Page Performance

**Available data:**
- Page load times
- Resource sizes
- Performance issues
- HTML/CSS/JS errors

**Example queries:**
```
"Which pages have slow load times?"
"Show me all pages over 5MB"
"Find JavaScript errors in site audit"
```

**Note:** Site audit data requires you to have an active audit project set up in Ahrefs. Create projects through the Ahrefs web interface.

---

## Content Explorer

Discover top-performing content and identify content opportunities.

### Content Search

**Available data:**
- Articles matching search query
- Social shares (Facebook, Twitter, Pinterest, Reddit)
- Referring domains to content
- Organic traffic estimates
- Domain Rating of publishing site
- Published dates
- Content length

**Example queries:**
```
"Find top content about 'artificial intelligence' with 50+ referring domains"
"Show me popular articles on 'productivity tips'"
"What content about 'web design' has the most shares?"
```

### Content Analysis

**Available data:**
- Top shared content in a niche
- Content published by domain
- Trending topics
- Content gaps (topics competitors cover but you don't)

**Example queries:**
```
"What content does competitor.com publish that ranks well?"
"Find content gaps between mysite.com and competitor.com"
"Show me trending topics in 'digital marketing' this month"
```

### Outreach Opportunities

**Available data:**
- Authors and publishers
- Contact information (when available)
- Domain authority of publishers
- Historical publication patterns

**Example queries:**
```
"Find websites that published about 'sustainability' recently"
"Who are the top publishers in the 'fitness' niche?"
```

---

## Data Freshness and Updates

- Most metrics update daily (backlinks, keywords, rankings)
- Some data updates weekly (site audits, crawl data)
- Rank tracker updates depend on project settings
- Real-time SERP data available on-demand

## API Efficiency Tips

- Request only needed columns/fields
- Use date ranges to limit historical data
- Batch similar queries together
- Cache results when appropriate
- Be mindful of row limits per plan tier
