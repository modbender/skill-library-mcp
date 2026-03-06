# Data Collection Guide

Step-by-step instructions for fetching the data needed for each dimension.

## Phase 1: Identify the Company

1. Get the company ticker symbol and exchange
2. Determine country of incorporation
3. Identify GICS sector and sub-industry
4. Note market cap tier (mega/large/mid/small)

## Phase 2: Fetch Annual Filings (Last 4 Years)

### US-Based Companies (SEC EDGAR)

**Fetching 10-K filings:**

1. Search EDGAR for the company's CIK number:
   - Web search: `[company name] SEC EDGAR CIK`
   - Or fetch: `https://efts.sec.gov/LATEST/search-index?q=[company name]&dateRange=custom&startdt=2021-01-01&enddt=2026-12-31&forms=10-K`

2. Get the last 4 annual 10-K filings:
   - Fetch: `https://efts.sec.gov/LATEST/search-index?q=&forms=10-K&dateRange=custom&startdt=2021-01-01&enddt=2026-12-31&entityName=[CIK]`
   - Or use the full-text search API: `https://efts.sec.gov/LATEST/search-index?q=%22artificial+intelligence%22&forms=10-K&entityName=[company]`

3. For each 10-K, extract these specific sections:
   - **Item 1 (Business Description):** Workforce composition, business model, key products/services
   - **Item 1A (Risk Factors):** AI-specific risks, competitive threats, regulatory risks
   - **Item 7 (MD&A):** Revenue segments, operating metrics, strategic initiatives, AI mentions
   - **Human Capital section:** Employee count, job categories, hiring trends
   - **Financial statements:** Revenue, SGA, total assets, cash, intangibles, goodwill (for ratio calculations)

**Key financial ratios to calculate from filings:**
- Labor cost-to-revenue: (SGA + estimated labor in COGS) ÷ Revenue
- Tangible asset intensity: (Total Assets – Cash – Intangibles – Goodwill) ÷ Revenue
- R&D as % of revenue (if disclosed separately)

### Non-US Companies

**Filing Substitution Table:**

| US Source | International Substitute | Notes |
|-----------|--------------------------|-------|
| SEC EDGAR 10-K | Company IR page annual reports (English PDFs); 20-F for cross-listed companies | Most large international companies publish English annual reports |
| O*NET + US academic datasets | Same datasets apply globally (occupations are universal); supplement with OECD AI exposure indicators | Felten AIOE and Eloundou scores are occupation-based, not country-based |
| USPTO patents | EPO via Espacenet (free); Google Patents (global, free); WIPO PatentScope | Google Patents is easiest single source for global patent search |
| Seeking Alpha transcripts | Company IR pages; LSE RNS; local exchange disclosure services | Transcript availability varies; major non-US companies usually publish English materials |
| Crunchbase free tier | Same tool works globally; also use Dealroom.co for European startup data | Filter by geography + sector |

**Disclosure Quality Adjustment for Non-US:**
For companies in jurisdictions with less detailed disclosure requirements (some Asian or emerging-market exchanges):
- Reduce confidence in Dimensions 1 and 2 by widening score range ±0.5
- Increase reliance on Dimensions 3, 7, and 8 (more universally available signals)

## Phase 3: Fetch Earnings Transcripts

For Dimension 3 (AI Adoption), you need the last 4–8 quarterly earnings call transcripts.

**Sources (in priority order):**
1. SEC EDGAR 8-K filings (Item 2.02 — Results of Operations) — often include prepared remarks
2. Company Investor Relations pages — most publish transcript PDFs or press releases
3. Web search for `[company] earnings call transcript Q[X] [year]` — free summaries often available

**What to extract from each transcript:**
- Count of AI/ML/machine learning mentions (track trend over quarters)
- Specific AI use cases mentioned (with or without KPIs)
- Management tone: strategic priority vs. defensive mention
- AI-specific leadership announcements
- Analyst questions about AI (substantive vs. absent)
- Any quantified AI impact metrics (cost savings, revenue contribution, efficiency gains)

## Phase 4: Patent Data

**Google Patents (preferred — global coverage, citation data):**
- Web search: `[company name] AI patent Google Patents`
- Or search directly: `https://patents.google.com/?q=artificial+intelligence&assignee=[company]`

**Track:**
- Total AI-related patent filings (last 3 years)
- Filing trend: accelerating, flat, or declining
- Average citations per patent (quality signal)
- Patent family size (international coverage)
- Sub-technology areas (NLP, computer vision, robotics, etc.)

**Supplement:**
- GitHub: `https://github.com/[company]` — open-source AI repositories
- Hugging Face: search for company models/datasets

## Phase 5: Industry & Competitive Data

**For Dimension 7 (Industry Transformation Velocity), check:**

1. **AI Startup Funding:** Web search `AI startups [sector] funding 2025 2026`
2. **Peer AI Mentions:** Web search `[sector] companies AI 10-K mentions` or spot-check 3-5 peers on EDGAR
3. **Public Reports:** Search for Stanford HAI AI Index latest edition; McKinsey AI survey latest
4. **Incumbent Disruption:** Web search `[sector] stock decline AI disruption`
5. **Big Tech Entry:** Web search `Google Microsoft Amazon [sector] AI product launch`

## Phase 6: Valuation Data

**From Yahoo Finance or equivalent (all free):**
- Forward P/E ratio (company)
- EV/Sales (company)
- Sector median forward P/E
- Sector median EV/Sales

Use these for the Valuation Overlay in the final classification.

## Phase 7: O*NET Workforce Mapping

See `onet_mapping_guide.md` for detailed instructions on mapping company job categories to O*NET occupations and pulling AI exposure scores.

## Data Collection Checklist

Before scoring, verify you have:

- [ ] Last 4 annual filings (10-K or equivalent) — at minimum the most recent
- [ ] Revenue segments and financial ratios calculated
- [ ] Last 4+ quarterly earnings transcripts reviewed for AI mentions
- [ ] Patent data retrieved (count, trend, quality)
- [ ] O*NET occupation mapping completed for dominant job categories
- [ ] Industry transformation proxies checked (at least 3 of 5)
- [ ] Valuation multiples retrieved
- [ ] For non-US: disclosure quality assessed and adjustments noted

If any critical data source is unavailable, note it explicitly and adjust confidence accordingly.
