# Ahrefs MCP Workflow Patterns

Common workflows and best practices for using Ahrefs data effectively.

## Table of Contents

1. [Keyword Research Workflows](#keyword-research-workflows)
2. [Competitive Analysis](#competitive-analysis)
3. [Content Strategy](#content-strategy)
4. [Link Building](#link-building)
5. [Technical SEO Audits](#technical-seo-audits)
6. [Rank Monitoring](#rank-monitoring)

---

## Keyword Research Workflows

### Basic Keyword Research

**Goal:** Find valuable keywords to target

**Steps:**
1. Get seed keyword metrics (volume, KD, traffic potential)
2. Expand with related keywords and questions
3. Filter by criteria (volume > X, KD < Y)
4. Analyze SERP to understand competition
5. Prioritize based on goals

**Example flow:**
```
User: "Research keywords for 'eco-friendly water bottles'"

1. Query: "Get metrics for 'eco-friendly water bottles'"
   → Volume: 5,400 | KD: 42 | CPC: $1.20

2. Query: "Give me 50 related keywords"
   → Returns: "sustainable water bottles", "reusable bottles", etc.

3. Query: "Get volume and KD for this list: [related keywords]"
   → Returns full metrics table

4. Analyze and present:
   - High volume, low-medium KD opportunities
   - Question keywords for blog content
   - Commercial keywords for product pages

5. Recommend: "Target 'reusable water bottles' (8,900 vol, KD 38) as primary..."
```

### Keyword List Cross-Reference

**Goal:** Analyze existing keyword list with Ahrefs data

**Steps:**
1. Receive keyword list from user
2. Batch query metrics for all keywords
3. Consolidate into table with key metrics
4. Sort by priority criteria
5. Segment by intent or topic clusters
6. Provide recommendations

**Example flow:**
```
User: "Here's my keyword list: [50 keywords]. Help me prioritize."

1. Query Ahrefs for all keywords (batched efficiently)
2. Build comparison table:
   Keyword | Volume | KD | Traffic Potential | CPC
   --------|--------|----|--------------------|----

3. Segment by priority:
   - Quick Wins: High volume, low KD (< 30)
   - Long-term: High potential, high KD (50+)
   - Quick Content: Questions and long-tail

4. Present analysis with specific recommendations
```

### Gap Analysis

**Goal:** Find keywords competitors rank for but you don't

**Steps:**
1. Identify competitor domains
2. Get their top organic keywords
3. Check which ones you don't rank for
4. Filter by relevance and difficulty
5. Prioritize opportunities

**Example flow:**
```
User: "Find keyword gaps between mysite.com and competitor.com"

1. Query: "Get top 500 organic keywords for competitor.com"
2. Query: "Get organic keywords for mysite.com"
3. Identify gaps (keywords in competitor list but not yours)
4. Filter by volume and KD
5. Present top opportunities with:
   - Why competitor ranks (page type, content angle)
   - Estimated traffic value
   - Difficulty assessment
```

---

## Competitive Analysis

### Domain Comparison

**Goal:** Understand competitive landscape

**Steps:**
1. Collect competitor domains
2. Compare key metrics (DR, organic traffic, keywords)
3. Analyze backlink profiles
4. Identify strengths and weaknesses
5. Find opportunities

**Example flow:**
```
User: "Compare mysite.com against 3 competitors"

1. Query domain metrics for all:
   - Domain Rating
   - Organic traffic
   - Organic keywords
   - Referring domains

2. Query top keywords for each:
   - Overlap analysis
   - Unique keyword opportunities

3. Query backlink profiles:
   - Total backlinks
   - Quality of referring domains
   - Common link sources

4. Present competitive positioning:
   - Where you lead
   - Where you lag
   - Specific gaps to address
```

### Competitor Content Analysis

**Goal:** Understand what content drives competitor success

**Steps:**
1. Get competitor's top pages by traffic
2. Analyze keywords each page ranks for
3. Identify content types and topics
4. Find content gaps
5. Recommend content strategy

**Example flow:**
```
User: "What content works for competitor.com?"

1. Query: "Top 50 pages by organic traffic for competitor.com"
2. For each top page, get ranking keywords
3. Categorize content:
   - Blog posts vs landing pages
   - Topic themes
   - Content depth
4. Cross-reference with your content
5. Recommend: "Competitor has 10 comprehensive guides on X topic. You have none. Opportunity to create..."
```

---

## Content Strategy

### Content Opportunity Finder

**Goal:** Identify topics with high potential

**Steps:**
1. Research topic with Keywords Explorer
2. Analyze top-ranking content
3. Check content gaps
4. Evaluate feasibility (KD, existing authority)
5. Create content brief

**Example flow:**
```
User: "Find content opportunities in 'home fitness' niche"

1. Query: "Related keywords for 'home fitness'"
2. Filter by traffic potential and reasonable KD
3. For promising keywords, analyze SERP:
   - Content format (listicle, guide, comparison)
   - Average content length
   - Backlink requirements
4. Use Content Explorer: "Popular content about 'home fitness'"
5. Present opportunities with:
   - Target keyword
   - Content angle based on SERP
   - Estimated traffic
   - Difficulty assessment
```

### Content Refresh Prioritization

**Goal:** Identify which existing content to update

**Steps:**
1. Get your top pages by traffic
2. Check for position changes (declining keywords)
3. Analyze SERP for those keywords
4. Identify outdated elements
5. Prioritize updates by impact

**Example flow:**
```
User: "Which content should I refresh first?"

1. Query: "Top 100 pages on mysite.com by organic traffic"
2. Query rank tracker: "Keywords with position declines"
3. Match declining keywords to pages
4. For each page, analyze current SERP:
   - Are competitors more up-to-date?
   - New SERP features?
   - Content expectations changed?
5. Prioritize by:
   - Traffic at risk (high volume keywords declining)
   - Easy wins (minor updates needed)
   - Strategic importance
```

---

## Link Building

### Link Opportunity Discovery

**Goal:** Find domains likely to link to you

**Steps:**
1. Analyze competitor backlinks
2. Filter for quality and relevance
3. Identify patterns (directories, resources, guest posts)
4. Check if they link to multiple competitors
5. Create outreach list

**Example flow:**
```
User: "Find link building opportunities for mysite.com"

1. Query: "Referring domains to competitor1.com, competitor2.com, competitor3.com"
2. Find domains linking to multiple competitors but not you
3. Filter by:
   - Domain Rating > threshold
   - Relevant niche
   - Link type (editorial vs directory)
4. Categorize opportunities:
   - Resource pages
   - Guest post opportunities
   - Broken link replacement
   - Unlinked mentions
5. Provide outreach list with context
```

### Broken Link Building

**Goal:** Find and replace broken backlinks

**Steps:**
1. Analyze competitor's broken backlinks
2. Identify relevant opportunities
3. Create superior replacement content
4. Prepare outreach strategy

**Example flow:**
```
User: "Find broken link opportunities in [niche]"

1. Query: "Get backlinks with 404 status to competitor.com"
2. Analyze linking pages:
   - Still active?
   - Contextually relevant?
   - Domain quality
3. Identify patterns of broken content
4. Recommend: "23 sites link to competitor's deleted guide on X. Create comprehensive guide and reach out to those sites."
```

---

## Technical SEO Audits

### Prioritized Issue Resolution

**Goal:** Fix technical issues by impact

**Steps:**
1. Run/access site audit data
2. Categorize issues by severity and impact
3. Estimate affected traffic
4. Create fix priority list
5. Provide implementation guidance

**Example flow:**
```
User: "Help me fix technical SEO issues on mysite.com"

1. Query: "Get site audit summary and critical issues"
2. For each critical issue:
   - Affected URLs
   - Potential traffic impact
   - Fix complexity
3. Prioritize:
   - High impact, easy fix (do first)
   - High impact, complex (plan carefully)
   - Low impact (backlog)
4. Create actionable fix list with:
   - Issue description
   - Why it matters
   - How to fix
   - Verification steps
```

### Crawl Issue Analysis

**Goal:** Understand and resolve crawl problems

**Steps:**
1. Review crawl statistics
2. Identify crawl bottlenecks
3. Analyze redirect chains and loops
4. Check for orphan pages
5. Optimize crawl budget

**Example flow:**
```
User: "Why isn't Google crawling all my pages?"

1. Query: "Crawl data for mysite.com"
2. Analyze:
   - Pages crawled vs total pages
   - Crawl errors by type
   - Redirect chains
   - Blocked resources
3. Identify bottlenecks:
   - Excessive redirects slowing crawl
   - Broken internal links
   - Robots.txt issues
4. Recommend fixes prioritized by impact
```

---

## Rank Monitoring

### Position Change Analysis

**Goal:** Understand ranking movements

**Steps:**
1. Query rank tracker for recent changes
2. Correlate changes with events (updates, changes, competitors)
3. Analyze SERP for changed keywords
4. Identify patterns
5. Recommend actions

**Example flow:**
```
User: "Why did my rankings drop last week?"

1. Query: "Keywords with position changes in last 7 days"
2. Identify patterns:
   - Specific pages affected?
   - Related keywords or isolated?
   - Algorithm update timeline correlation?
3. For dropped keywords, analyze current SERP:
   - What changed in top results?
   - New competitors?
   - SERP features now present?
4. Recommend:
   - Content updates
   - Technical fixes
   - Wait-and-see if temporary fluctuation
```

### Visibility Tracking

**Goal:** Monitor overall search presence

**Steps:**
1. Track visibility score over time
2. Segment by keyword groups (brand, category, long-tail)
3. Compare to competitors
4. Identify trends
5. Set alerts for significant changes

**Example flow:**
```
User: "Track our search visibility for product keywords"

1. Query: "Visibility score for rank tracker project 'Products'"
2. Query: "Position distribution (top 3, 4-10, 11-20, etc.)"
3. Compare to previous periods
4. Break down by:
   - Keyword groups
   - Landing pages
   - Search intent
5. Report trends and recommend focus areas
```

---

## Best Practices Across Workflows

### Efficient Data Usage

- Query only necessary data fields
- Use date ranges to limit results
- Batch similar requests
- Cache results when appropriate
- Consider API unit costs for large datasets

### Analysis Quality

- Cross-reference multiple data points
- Consider context (seasonality, industry trends)
- Verify surprising findings
- Provide confidence levels
- Note data limitations

### Actionable Output

- Always include recommendations, not just data
- Prioritize by impact and feasibility
- Provide next steps
- Set expectations on difficulty/timeline
- Offer alternatives when needed

### User Communication

- Confirm scope before expensive queries
- Explain what data you're retrieving and why
- Present findings clearly (tables, summaries, bullet points)
- Ask clarifying questions when needed
- Suggest follow-up analyses
