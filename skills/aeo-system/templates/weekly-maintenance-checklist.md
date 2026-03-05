# AEO Weekly Maintenance Checklist
**90-minute protocol — run every Monday morning**

*Version 1.0 — AEO 7-Layer System*

---

## Before You Start

Open your Answer Intent Map spreadsheet. You'll be updating it throughout this session.  
Have ChatGPT and Perplexity open in separate tabs — fresh sessions, no history.  
Check the "Last Maintained" date at the bottom and confirm it's been ~7 days.

---

## Block 1: Prompt Audit (30 minutes)

**Goal:** Detect position changes before competitors compound their advantage.

Run your top 15 priority queries — 8 on Perplexity, 7 on ChatGPT. These should be the highest-value queries from Layer 1.

For each query:

- [ ] Run query in fresh browser session
- [ ] Record which brand appears as #1 recommendation
- [ ] Record which brand appears as #2 and #3 (if named)
- [ ] Note the source URL the AI cites (Perplexity shows these directly)
- [ ] Note any verbatim text quoted about your brand (positive or negative)
- [ ] Update the "Date Tested" column in your Answer Intent Map

**Red flags to act on immediately:**
- Your brand dropped from #1 to #2 or lower
- A new competitor appeared that wasn't in last week's results
- Your Answer Hub URL is no longer being cited
- A competitor's review site listing is being cited (and you don't have one)

**Copy-paste to log results in Answer Intent Map:**
```
Date: [YYYY-MM-DD]
Query: 
Platform: ChatGPT / Perplexity
#1: 
#2: 
#3: 
Source cited: 
Change from last week: [same / moved up / moved down / new competitor]
Notes:
```

---

## Block 2: Answer Hub Update (15 minutes)

**Goal:** Keep the Answer Hub page current so AI models see fresh, accurate data.

Open your Answer Hub page at `/guides/best-[category]-[year]`.

Check each of these — update if anything has changed:

- [ ] **TL;DR section:** Is every fact accurate?
  - Product pricing still correct?
  - Review count current? (Update to latest number)
  - Any new certifications or test results to add?
  - Any competitor changes worth acknowledging?

- [ ] **Comparison table:** All specs accurate?
  - Price per serving current for all products?
  - Review counts current?
  - Any competitor products discontinued or reformulated?

- [ ] **FAQ section:** Any new queries from this week's Prompt Audit that should become FAQ entries?
  - If yes, write a 100–150 word answer and add it

- [ ] **External citations:** All links still live?
  - Run a quick check on citations — if a source has been removed, replace it

- [ ] After any update: update `lastUpdated` in `brand-facts.json` to today's date

**Time check:** If you're at 15 minutes and still editing, save remaining updates for next week. Prioritize the TL;DR and review counts — those have the most impact.

---

## Block 3: Content Expansion (20 minutes)

**Goal:** Add one new FAQ entry targeting a query you're not yet winning.

From this week's Prompt Audit, pick the one query where:
- You don't currently appear in the top 3 results
- The query has clear purchase intent
- The answer would naturally reference your product

Write a 100–150 word answer to that query. Include:
- A direct answer to the question
- Specific data or specs that support the answer
- A natural reference to your product where appropriate
- One external citation if possible

Add the new FAQ to your Answer Hub.  
Add the question to the FAQ schema in the page `<head>`.

- [ ] New FAQ written
- [ ] Added to Answer Hub FAQ section
- [ ] Added to FAQ JSON-LD schema
- [ ] Answer Hub "Last updated" date refreshed

**Optional (if time allows):** Start a comparison page for a query where a competitor is consistently #1. Template: `/compare/[your-brand]-vs-[competitor]`. Even a stub page with accurate specs starts building the bidirectional citation signal.

---

## Block 4: Merchant Center Hygiene (15 minutes)

**Goal:** Keep GPT Shopping eligibility clean.

Log into Google Merchant Center. Check:

- [ ] **Disapprovals:** Any products disapproved this week? Fix immediately — disapprovals suppress Shopping visibility
  - Common causes: pricing mismatch (fix the feed sync), image violations (update images), policy issues (check the reason code)

- [ ] **Review push:** Identify the hero SKU with the lowest review count. Export any new verified reviews from your review platform and confirm they're syncing to Merchant Center.
  - Minimum target: 50 reviews per hero SKU, 4.0+ average rating
  - If below minimum: send a post-purchase review request to recent buyers of that SKU this week

- [ ] **Pricing:** Are all product prices in the feed current? If you've changed pricing in Shopify, confirm the feed has updated (usually within 24 hours for automated feeds)

- [ ] **Availability:** Any products marked out-of-stock in the feed that are back in stock? Fix sync delay if so.

---

## Block 5: KPI Tracking (10 minutes)

**Goal:** Update your dashboard with three numbers so you can see trends over time.

Pull these from GA4:

**1. AI Recommendation Position (from Prompt Audit)**
Count: How many of your top 15 queries are you #1 for this week?
- This week: ___
- Last week: ___
- Trend: up / flat / down

**2. AI Referral Traffic Volume**
Filter in GA4:
- Source: `chatgpt.com` + `perplexity.ai` + `claude.ai` + `gemini.google.com`
- Or: `utm_medium = organic` + `utm_source = chatgpt` (if UTM-tagged)
- Sessions this week: ___
- Sessions last week: ___

**3. AI Referral Conversion Rate**
In GA4, segment sessions from AI referral sources and check ecommerce conversion rate.
- AI referral conv rate this week: ____%
- Site average conv rate: ____%
- Multiplier: ____x

**Log format (add to KPI spreadsheet tab):**
```
Week of: [YYYY-MM-DD]
Queries at #1: [N] / 15
AI referral sessions: [N]
AI conv rate: [X.X]%
Site average conv rate: [X.X]%
AI revenue (if GA4 tracks it): $[N]
Notes: [Any significant changes this week]
```

---

## Monthly Add-Ons (Do These on the 1st of Each Month)

In addition to the weekly protocol, on the first Monday of each month:

- [ ] **Refresh `brand-facts.json`**
  - Update `lastUpdated` to today's date
  - Review all fields for accuracy — any product changes, price changes, or policy changes?
  - Push the updated file to `/.well-known/brand-facts.json`

- [ ] **Schema audit**
  - Run your Answer Hub and 2 product pages through Google Rich Results Test (search.google.com/test/rich-results)
  - Fix any schema errors flagged
  - Verify FAQ schema is rendering correctly

- [ ] **Answer Hub year check**
  - If January: update the URL year reference in the Answer Hub title and content (e.g., 2025 → 2026)
  - Redirect the old URL to the new one
  - Update the link in `brand-facts.json`

- [ ] **Competitor comparison table check**
  - Have any competitors changed their products, pricing, or specs?
  - Update comparison table to keep it accurate
  - Inaccurate competitor data damages AI trust in your page as a citation source

- [ ] **Citation count**
  - Check Google Alerts for your brand name (set one up if you haven't)
  - Count new external mentions this month
  - Log: total external citations to date

- [ ] **Comparison page review**
  - Add one new comparison page targeting the competitor you're winning against most consistently in AI results
  - Template: `/compare/[your-brand]-vs-[competitor-brand]`

---

## Escalation: When to Take Emergency Action

**Act the same day if:**
- You drop from #1 to #3 on more than 5 priority queries in a single week
- A competitor's Answer Hub page appears in your citation sources (they're now getting cited where you were)
- Your `brand-facts.json` URL returns an error (404 or invalid JSON)
- A negative review is being cited by AI models verbatim (check the source and respond)
- A competitor's Wikidata entry is more complete than yours

**Response protocol:**
1. Identify the specific layer that's failing (which of the 7 layers is the source of the position change?)
2. Update that layer within 48 hours
3. Re-run the affected queries to verify recovery
4. Log the incident in your Answer Intent Map notes column

---

## Maintenance Log

Keep a running log at the bottom of your Answer Intent Map spreadsheet:

| Date | Queries Audited | Our #1 Count | Key Changes | Actions Taken |
|------|----------------|--------------|-------------|---------------|
| [date] | 15 | [N]/15 | [what changed] | [what you did] |

Review this log monthly. If your #1 count is declining over multiple weeks, increase content expansion velocity (Block 3) before it becomes a serious position problem.

---

*AEO Weekly Maintenance Checklist v1.0*  
*Part of the AEO 7-Layer System — A SkillStack Product*  
*Last session completed: ___________*  
*Next session due: ___________*
