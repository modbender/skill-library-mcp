# SEO Prospect Research Workflows

Step-by-step guides for different research scenarios.

## Workflow 1: Daily Cron Research Run

**Context:** Automated research via cron job, isolated session, no MCP access

**Steps:**

1. **Get today's clusters**
   ```bash
   python3 prospect_tracker.py today-clusters
   ```
   - Returns which clusters are scheduled for morning/afternoon/evening runs
   - Use cluster industries and keywords for research

2. **Load prospects from KLW directory or SERP**
   - Filter KLW CSV by cluster industries
   - OR run SERP searches using cluster keywords
   - Limit to 3-5 prospects per run (quality > quantity)

3. **For each prospect:**
   ```bash
   python3 research_prospect.py \
     --business "$name" \
     --domain "$domain" \
     --industry "$industry" \
     --cluster "$cluster_name" \
     --priority "$priority" \
     --no-browser  # Cron can't use browser
   ```

4. **Generate daily summary**
   - Count prospects researched
   - List high-priority finds
   - Note any errors/failures
   - Post to Discord channel

**Output locations:**
- Reports: `~/.openclaw/workspace/leads/prospects/YYYY-MM-DD-cluster-name/`
- Summary: `~/.openclaw/workspace/leads/reports/daily/YYYY-MM-DD-summary.md`
- Database: Auto-updated by `research_prospect.py`

---

## Workflow 2: Manual Single-Prospect Research

**Context:** Agent in main session, full tool access, human oversight

**Steps:**

1. **Duplicate check**
   ```bash
   python3 prospect_tracker.py check --business "Business Name"
   ```
   - If found within 14 days: Review existing report instead
   - If not found or >14 days old: Continue

2. **Run SEO audit**
   ```bash
   python3 seo_quick_audit.py "https://example.com"
   ```
   - Note specific weaknesses and strengths
   - Identify primary opportunity (missing H1, no schema, etc.)

3. **Web research via Perplexity**
   ```bash
   python3 perplexity_search.py "Business Name {{YOUR_CITY}} reviews website"
   ```
   - Get business overview, reputation, reviews
   - Note customer sentiment and competitive positioning

4. **Browser verification (HIGH priority only)**
   ```
   Use browser tool to:
   - Take screenshot of homepage (desktop + mobile)
   - Check contact form functionality
   - Assess visual design quality
   - Note UX issues
   ```

5. **Synthesize report**
   - Use `references/research-template.md`
   - Include specific findings from each source
   - Write executive summary (2-3 sentences)
   - Note confidence level (HIGH if browser-verified)

6. **Save and track**
   ```bash
   # Save report
   # (research_prospect.py handles this automatically)
   
   # Manually add if needed:
   python3 prospect_tracker.py add \
     --business "Name" \
     --industry "Industry" \
     --priority "HIGH" \
     --cluster "Cluster" \
     --domain "example.com" \
     --file "path/to/report.md"
   ```

7. **Generate outreach** (optional, immediate follow-up)
   ```bash
   python3 generate_outreach.py \
     --report "path/to/report.md" \
     --type package
   ```

**Decision points:**

- **Skip browser verification** if: MEDIUM/LOW priority, website is obviously broken, time-constrained
- **Upgrade to HIGH priority** if: Clear need + strong fit + professional business
- **Downgrade to LOW priority** if: Recent redesign, corporate-managed site, saturated market

---

## Workflow 3: Batch Research from List

**Context:** User provides list of prospects (e.g., from event, referral source)

**Input format (JSON):**
```json
[
  {
    "business": "Business Name",
    "domain": "example.com",
    "industry": "Restaurant",
    "priority": "HIGH",
    "cluster": "Restaurants",
    "notes": "Referral from John"
  }
]
```

**Steps:**

1. **Save list to file**
   ```bash
   # Save to prospects-input.json
   ```

2. **Run batch research**
   ```bash
   python3 batch_research.py --input prospects-input.json --limit 10
   ```
   - Processes each prospect sequentially
   - Auto-checks for duplicates
   - Skips if recently researched (unless --force)

3. **Review reports**
   - Check `leads/prospects/YYYY-MM-DD-*/` directories
   - Identify any failures or incomplete reports
   - Re-run individually if needed

4. **Generate outreach batch**
   ```bash
   python3 generate_outreach_batch.py --date YYYY-MM-DD
   ```
   - Creates outreach package for all prospects from today
   - Saves to `leads/outreach/YYYY-MM-DD/`

**Best for:**
- Conference attendee lists
- Referral batches
- Manual SERP scraping results
- KLW directory filters

---

## Workflow 4: Quick Triage (No Full Report)

**Context:** Need to quickly assess if a prospect is worth full research

**Steps:**

1. **Quick SEO check**
   ```bash
   python3 seo_quick_audit.py "https://example.com"
   ```
   - Scan for obvious issues
   - If 3+ weaknesses: Good candidate
   - If 0-1 weaknesses: Probably not worth it

2. **Quick Perplexity search**
   ```bash
   python3 perplexity_search.py "Business Name {{YOUR_CITY}}" --max-tokens 300
   ```
   - Check if business is active
   - Look for red flags (closing, sold, franchise)

3. **Decision:**
   - **Green light:** 3+ SEO issues + active business → Full research
   - **Yellow light:** 1-2 issues + active → Maybe (time permitting)
   - **Red light:** Recent redesign or corporate-managed → Skip

**No report generated, no database entry**

Best for: Initial filtering of large prospect lists, SERP results, directory scraping

---

## Workflow 5: Re-Research (Stale Prospects)

**Context:** Follow up on prospects researched 30+ days ago

**Steps:**

1. **Find stale prospects**
   ```bash
   python3 prospect_tracker.py stale --days 30
   ```
   - Returns list of prospects >30 days old
   - Prioritize HIGH priority prospects first

2. **Review old report**
   - Read original research
   - Note what opportunity was identified
   - Check if anything has changed (new website? went out of business?)

3. **Quick re-check**
   ```bash
   # Run new SEO audit
   python3 seo_quick_audit.py "https://example.com"
   
   # Compare to original findings
   # Did they fix the issues? (If yes, skip)
   # Are issues still there? (If yes, good follow-up angle)
   ```

4. **Update report or create new**
   - If website unchanged: Use original report for outreach
   - If website changed: Create new report (note previous research in report)

5. **Generate follow-up outreach**
   - Reference that you reached out before (if you did)
   - OR position as fresh outreach with updated findings

**Best for:**
- Quarterly pipeline refreshes
- Prospects that didn't respond the first time
- Businesses that were "maybe" but now look better

---

## Workflow 6: Competitor Analysis (for existing client)

**Context:** Client wants to know how they compare to local competitors

**Steps:**

1. **Identify competitors**
   - Get list from client
   - OR search Google for "[client's service] {{YOUR_CITY}}"
   - Target top 5-10 results

2. **Research each competitor**
   ```bash
   # For each competitor:
   python3 research_prospect.py \
     --business "Competitor Name" \
     --domain "competitor.com" \
     --industry "Same as client" \
     --cluster "Competitor Analysis" \
     --priority "MEDIUM"
   ```

3. **Comparative analysis**
   - Create comparison table:
     - Domain Authority (if available)
     - SEO score (based on audit findings)
     - Content volume (blog posts, pages)
     - Schema markup presence
     - Page speed
     - Mobile optimization

4. **Generate recommendations**
   - What are competitors doing well?
   - Where are gaps client can exploit?
   - Quick wins to outrank specific competitors

**Output:**
- Individual competitor reports
- Comparison summary document
- Recommendations for client

**Not typical prospect research, but uses the same tools**

---

## Workflow 7: SERP-First Discovery

**Context:** Find prospects by searching Google for high-intent keywords

**Steps:**

1. **Identify keywords**
   ```
   "[industry] {{YOUR_CITY}}"
   "best [industry] {{YOUR_CITY}}"
   "[service] near me" (from {{YOUR_CITY}} IP)
   ```

2. **Manual SERP scraping**
   - Search Google for each keyword
   - Note businesses ranking 2-10 (skip #1, they're doing fine)
   - Extract: business name, website, position

3. **Triage list**
   - Quick check each site (workflow 4)
   - Filter for obvious SEO issues
   - Create input JSON for batch research

4. **Batch research survivors**
   ```bash
   python3 batch_research.py --input serp-prospects.json
   ```

5. **Outreach with competitor hook**
   - "Saw [competitor] ranking above you for '[keyword]'"
   - Use Template 3 from outreach-templates.md

**Best for:**
- Discovering new prospects outside KLW directory
- Competitive industries (restaurants, contractors)
- Keywords with commercial intent

---

## Decision Trees

### Should I browser-verify this prospect?

```
Is priority HIGH?
├─ Yes → Does website look broken in SEO audit?
│  ├─ Yes → SKIP (waste of time, they need full rebuild)
│  └─ No → VERIFY (worth the time for high-priority)
└─ No → SKIP (not worth time for MEDIUM/LOW)
```

### What priority should I assign?

```
Does business fit SEO Prospector ideal client?
(Local, small business, 10-50 employees, budget $3k-$10k)
├─ Yes → How many SEO issues?
│  ├─ 3+ → How's their reputation?
│  │  ├─ Good reviews → HIGH
│  │  └─ Mixed/unknown → MEDIUM
│  └─ 1-2 → MEDIUM (unless other factors)
└─ No → How strong is the opportunity?
   ├─ Very clear need → MEDIUM
   └─ Speculative → LOW
```

### Should I re-research a stale prospect?

```
Was priority HIGH originally?
├─ Yes → Did they respond to outreach?
│  ├─ No → Re-research (they might be ready now)
│  └─ Yes but didn't close → Review original notes
└─ No → How long has it been?
   ├─ >90 days AND now different cluster → Re-research
   └─ <90 days → Skip for now
```

---

## Error Handling

### SEO audit fails (timeout, SSL error, etc.)

**Fallback:**
1. Note the error in report
2. Continue with Perplexity research only
3. Mark confidence as LOW
4. In report: "Website audit unavailable due to [technical issue]"

### Perplexity API rate limit

**Fallback:**
1. Use basic web search (browser tool)
2. Check review sites directly (Google Maps, Yelp)
3. Note in report: "Limited web research due to API constraints"

### Duplicate business names

**Resolution:**
1. Use domain for differentiation
2. Check address if available
3. Note in database: "Business Name (example.com)" vs "Business Name (example2.com)"

### Website completely broken (404, expired domain)

**Actions:**
1. Note in report: "Website appears to be offline"
2. Search for new domain via Perplexity
3. If found: Update domain and continue
4. If not found: Mark as LOW priority, note "Business may be closed"

### Missing critical data (no domain, no industry)

**Minimum requirements:**
- Must have: Business name
- Must have ONE of: Domain OR industry

**If missing domain:**
- Search Perplexity for business info
- Check KLW directory
- If still not found: Mark as incomplete, skip

**If missing industry:**
- Infer from business name
- Check website (if domain available)
- Default to "Other/General Business"

---

## Quality Checklist

Before marking research complete, verify:

- [ ] Executive summary is 2-3 sentences (not longer)
- [ ] At least one specific SEO finding is mentioned
- [ ] Business overview explains what they actually do
- [ ] Primary opportunity is clear and actionable
- [ ] Confidence level matches verification depth
- [ ] Report follows template structure
- [ ] Saved to correct directory (`YYYY-MM-DD-cluster-name/`)
- [ ] Added to prospect database (unless dry-run)
- [ ] No placeholder "[TODO]" text remains
- [ ] Business name is spelled correctly throughout
- [ ] Domain is correctly formatted (https://)

---

## Performance Targets

**Per-prospect research time:**
- Automated (cron): 2-3 minutes per prospect
- Manual (no browser): 5-10 minutes per prospect
- Manual (with browser): 15-20 minutes per prospect

**Daily targets:**
- Morning run: 3-5 prospects (Tier A cluster)
- Afternoon run: 3-5 prospects (Tier B cluster)
- Total per day: 6-10 prospects
- Weekly: 30-50 prospects
- Monthly: 120-200 prospects

**Quality over quantity:** Better to do 5 HIGH-quality reports than 20 mediocre ones.

---

## Integration with Existing Cron Jobs

**Current SEO Prospector cron schedule:**

- 8:30 AM: SERP Gap Scanner → feeds into prospect discovery
- 10:00 AM: Prospect Run 1 (use this workflow)
- 11:30 AM: Prospect Run 2 (use this workflow)
- 5:00 PM: Daily Summary → includes prospect stats

**Workflow integration:**

1. SERP scanner identifies industries with opportunities
2. Prospect runs research businesses in those industries
3. Daily summary reports progress and high-priority finds
4. Weekly: Generate outreach packages for the week's prospects

This workflow guide ensures consistency across manual and automated research.
