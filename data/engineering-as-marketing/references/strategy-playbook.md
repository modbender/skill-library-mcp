# Engineering as Marketing — Strategy Playbook

## Table of Contents
1. Core Concept
2. Keyword Research Process
3. Free Tool Design Patterns
4. Conversion Funnel Architecture
5. Tool Creation Workflow
6. API & Automation Options
7. Measurement & Iteration

---

## 1. Core Concept

"Engineering as Marketing" = building free, useful tools that attract your target audience via organic search, instead of spending on ads or content marketing.

**Why it works for builders:**
- Each tool is a permanent SEO asset (unlike blog posts that decay)
- Tools have higher engagement (longer dwell time, bookmarks, backlinks)
- Users who find your tool are pre-qualified leads (they have the problem you solve)
- AI coding tools make creation nearly free (5 min/tool with templates)

**Case study benchmark (SiteGPT):**
- 50+ free tools → 50K monthly visitors → 90% from Google organic
- 50K visitors → 200 leads → 60 trials → 15-24 paying customers/month
- $0 marketing budget, $13K MRR, 130 customers at ~$100/month

---

## 2. Keyword Research Process

### Step-by-step (adapted from SiteGPT playbook)

1. **Pick seed terms** related to your product domain
   - Example: If you sell an email tool → "email", "newsletter", "smtp"
   
2. **Expand with modifiers** — combine seed terms with action words:
   - `[seed] + generator` → "email signature generator"
   - `[seed] + checker` → "email deliverability checker"
   - `[seed] + converter` → "html to text converter"
   - `[seed] + validator` → "email validator"
   - `[seed] + calculator` → "email ROI calculator"
   - `[seed] + tester` → "subject line tester"

3. **Filter for opportunity**:
   - **Keyword Difficulty (KD) < 10-15** — realistic for new/small domains
   - **Search volume > 500/month** — enough traffic to matter
   - **Commercial adjacency** — searchers should overlap with your buyers

4. **Prioritize by**:
   - Volume (higher = more traffic)
   - KD (lower = easier to rank)
   - Relevance to main product (higher = better conversion)
   - Build effort (lower = faster ROI)

### Tools for keyword research

| Tool | Cost | Best For |
|------|------|----------|
| Google Keyword Planner | Free (Ads account) | Search volume ranges |
| Ubersuggest (free tier) | Free (3/day) | Quick KD + volume check |
| Keyword Surfer (Chrome) | Free | Inline search volume |
| Mangools/KWFinder | $29/month | Best UX for low-KD hunting |
| LowFruits | $29/month | Finds weak SERP competitors |
| DataForSEO API | ~$0.002/req | Automation at scale |
| SE Ranking | $44/month | Best value with API included |
| Ahrefs | $99+/month | Most comprehensive data |
| Google Search Console API | Free | Your site's actual performance |

---

## 3. Free Tool Design Patterns

### Pattern A: Single-Purpose Converter/Generator
- Input → Transform → Output
- Examples: PDF to Markdown, JSON formatter, color palette generator
- Lowest build effort, highest volume potential

### Pattern B: Checker/Validator/Tester
- Input → Analyze → Report
- Examples: sitemap validator, SSL checker, page speed tester
- Builds trust, shows expertise

### Pattern C: Calculator/Estimator
- Input params → Calculate → Display result
- Examples: ROI calculator, pricing estimator, resource calculator
- Strong commercial intent (users evaluating purchases)

### Pattern D: AI-Powered Generator
- Input → AI processing → Generated output
- Examples: chatbot name generator, meta description writer, FAQ generator
- Trendy, high engagement, showcases AI capability

### Anatomy of a high-converting tool page

```
┌─────────────────────────────────┐
│ H1: [Keyword] — Free [Tool]    │
│ Subtitle: What it does (1 line) │
├─────────────────────────────────┤
│                                 │
│   [  TOOL INPUT / UI AREA  ]   │
│   [    OUTPUT / RESULTS     ]   │
│                                 │
├─────────────────────────────────┤
│ CTA: "Need [bigger solution]?" │
│ → Link to main product          │
├─────────────────────────────────┤
│ How to use (brief)              │
│ FAQ (targets related keywords)  │
│ Related tools (internal links)  │
└─────────────────────────────────┘
```

**Key rules:**
- Tool ABOVE the fold (no long intros)
- CTA contextually relevant (not generic "sign up")
- FAQ section captures long-tail variations
- Internal links to related tools (builds topical authority)
- Schema markup (SoftwareApplication) for rich snippets

---

## 4. Conversion Funnel Architecture

```
Free Tool User
  │
  ├── Sees contextual CTA → Visits product page
  │     ├── Signs up for trial (3-5% of tool users)
  │     └── 25-40% trial → paid conversion
  │
  ├── Bookmarks tool → Returns later → Eventually converts
  │
  └── Shares tool → Backlinks → Higher rankings → More traffic
```

### CTA strategies by tool type

- **Converter tool** → "Need to convert at scale? Try [Product]"
- **Checker tool** → "Found issues? [Product] monitors automatically"
- **Generator tool** → "[Product] does this + 10x more features"
- **Calculator tool** → "Ready to get started? [Product] from $X/month"

---

## 5. Tool Creation Workflow

### Rapid creation with AI assistance

1. Build first tool manually — this becomes the **template**
2. For each new tool:
   ```
   a. Pick keyword from prioritized list
   b. Give AI assistant the template + new keyword
   c. AI generates the tool (< 5 min)
   d. Review, test, deploy
   e. Submit to Google Search Console for indexing
   ```

### Tech stack recommendations

**Static/simple tools (Pattern A, C):**
- Single HTML page + vanilla JS
- Host on same domain as product (inherits domain authority)
- Route: `/tools/[keyword-slug]`

**Dynamic tools (Pattern B, D):**
- Lightweight backend (Flask/Express/Next.js API route)
- Rate limit to prevent abuse
- Cache results for performance

### SEO checklist per tool page

- [ ] Title tag: `[Primary Keyword] — Free Online [Tool Type]`
- [ ] Meta description with keyword + benefit
- [ ] H1 matches primary keyword
- [ ] Schema markup (SoftwareApplication or WebApplication)
- [ ] Open Graph tags for social sharing
- [ ] Internal links to 3-5 related tools
- [ ] FAQ section (3-5 questions targeting long-tail keywords)
- [ ] Canonical URL set
- [ ] Mobile responsive
- [ ] Page speed < 2s
- [ ] Sitemap updated

---

## 6. API & Automation Options

### Automated keyword discovery pipeline

```python
# Pseudocode for keyword opportunity finder
def find_opportunities(seed_terms, max_kd=15, min_volume=500):
    keywords = []
    modifiers = ["generator", "checker", "converter", "validator",
                 "calculator", "tester", "maker", "builder", "finder"]
    
    for seed in seed_terms:
        for mod in modifiers:
            query = f"{seed} {mod}"
            data = keyword_api.get_metrics(query)  # DataForSEO / SE Ranking
            if data.kd <= max_kd and data.volume >= min_volume:
                keywords.append({
                    "keyword": query,
                    "volume": data.volume,
                    "kd": data.kd,
                    "score": data.volume / (data.kd + 1)  # opportunity score
                })
    
    return sorted(keywords, key=lambda x: x["score"], reverse=True)
```

### Recommended API stack for full automation

1. **DataForSEO** ($0.002/req) — keyword metrics + SERP analysis
2. **Google Search Console API** (free) — track actual rankings
3. **Google Keyword Planner API** (free) — search volume data
4. **ValueSERP / SerpAPI** ($25-50/month) — SERP monitoring

---

## 7. Measurement & Iteration

### KPIs to track

| Metric | Tool | Target |
|--------|------|--------|
| Organic traffic per tool | Google Analytics / Search Console | Growing month-over-month |
| Keyword rankings | Rank tracker / Search Console | Top 10 for target keyword |
| Tool → Product CTR | Analytics events | 3-5% |
| Trial conversion rate | Product analytics | 25-40% |
| Backlinks per tool | Ahrefs / Moz | 5+ referring domains |
| Time on page | Analytics | > 2 minutes |

### Iteration checklist (monthly)

- [ ] Review rankings for each tool's target keyword
- [ ] Identify tools not ranking (KD too high? content thin?)
- [ ] Check for new keyword opportunities in same domain
- [ ] Update underperforming tool pages (add FAQ, improve content)
- [ ] Build internal links between new and existing tools
- [ ] Monitor competitor tools appearing for same keywords
