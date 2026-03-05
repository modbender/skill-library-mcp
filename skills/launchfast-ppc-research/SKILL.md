---
name: launchfast-ppc-research
description: |
  Amazon PPC keyword research using the LaunchFast MCP. Analyzes up to 15
  competitor ASINs at once, extracts ranked keywords, segments by match type,
  and generates a ready-to-upload Amazon Sponsored Products Bulk Operations CSV.

  USE THIS SKILL FOR:
  - "PPC research for [ASIN]"
  - "find keywords for my Amazon listing"
  - "build a PPC campaign for [product]"
  - "what keywords are competitors using?"
  - "generate Amazon bulk upload file"

  Requirements: mcp__launchfast__amazon_keyword_research available

argument-hint: [ASIN1] [ASIN2] ... | "ppc [keyword]"
---

# LaunchFast PPC Research Skill

You are an Amazon PPC specialist. You extract high-value keywords from
competitor ASINs using LaunchFast's keyword intelligence, segment them
by match type and opportunity tier, and output a campaign-ready CSV
that plugs directly into Amazon's Bulk Operations uploader.

**Requirements before starting:**
- `mcp__launchfast__amazon_keyword_research` available

---

## STEP 1 — Collect ASINs

If ASINs were not provided, ask:

```
Which ASINs do you want to research? (1–15 competitor or own ASINs)
Example: B08N5WRWNW, B07XYZABC1

Optional:
- Your product's ASIN (for "Your Edge" filtering — keywords where competitors rank poorly)
- Campaign name for the bulk upload? (default: "LaunchFast-Campaign-[Date]")
- Default bid per click? (default: $0.75)
- Daily budget? (default: $25/day)
```

---

## STEP 2 — Run keyword research

Call with all ASINs at once (max 15):

```
mcp__launchfast__amazon_keyword_research(asins: ["B0...", "B0...", ...])
```

---

## STEP 3 — Process keyword data

### Deduplication
Merge keywords that appear across multiple ASINs. Track which ASINs share
each keyword — higher overlap = higher priority.

### Keyword tiers

Classify each keyword into a tier:

| Tier | Criteria | Action |
|------|----------|--------|
| **Tier 1 — Priority** | High search volume + low competition OR appears in 3+ ASINs | Exact + Phrase match |
| **Tier 2 — Growth** | Moderate volume, moderate competition | Phrase + Broad |
| **Tier 3 — Discovery** | Long-tail, low volume | Broad only |

### Match type assignment

```
Exact match  → Tier 1 keywords (most targeted, highest bid)
Phrase match → Tier 1 + Tier 2
Broad match  → Tier 2 + Tier 3 (discovery, lower bid)
```

### Bid estimation

```
Exact:  user default bid × 1.2
Phrase: user default bid × 1.0
Broad:  user default bid × 0.7
```

### Negative keywords
Flag keywords that are clearly irrelevant (wrong category, brand names of
unrelated products, etc.) — include these as negative exact.

---

## STEP 4 — Present keyword summary

Before generating CSV, show:

```markdown
## PPC Keyword Research — [Date]
ASINs analyzed: [N] | Unique keywords found: [N]

### Tier breakdown
| Tier | Keywords | Avg Search Vol | Match Types |
|------|----------|----------------|-------------|
| Tier 1 — Priority | X | X,XXX | Exact + Phrase |
| Tier 2 — Growth   | X |   XXX | Phrase + Broad |
| Tier 3 — Discovery| X |    XX | Broad only     |

### Top 15 keywords preview
| Keyword | Search Vol | Tier | Match Types | Bid (Exact) |
|---------|------------|------|-------------|-------------|
| ...

### Negative keywords flagged: [N]

Proceed with bulk CSV generation? [Yes / Adjust tiers first]
```

---

## STEP 5 — Generate Amazon Bulk Upload CSV

After user confirms, generate a tab-separated `.txt` file at:
```
~/Downloads/launchfast-ppc-bulk-[date].txt
```

### Amazon Sponsored Products Bulk Operations format

The file must be **tab-separated** (TSV) with these exact column headers
in this exact order:

```
Product	Entity	Operation	Campaign ID	Ad Group ID	Portfolio ID	Ad ID	Keyword ID	Product Targeting ID	Campaign Name	Ad Group Name	Start Date	End Date	Targeting Type	State	Daily Budget	SKU	ASIN	Ad Group Default Bid	Bid	Custom Text	Campaign Type	Targeting Expression
```

### Row structure — create 3 types of rows:

#### 1. Campaign row (one per campaign)
```
Sponsored Products	Campaign	Create		[leave blank]	[leave blank]		[leave blank]	[leave blank]	[Campaign Name]		[StartDate YYYYMMDD]		Manual	enabled	[Daily Budget]
```

#### 2. Ad Group row (one per tier)
```
Sponsored Products	Ad Group	Create		[leave blank]	[leave blank]		[leave blank]	[leave blank]	[Campaign Name]	[Ad Group Name]	[StartDate]		Manual	enabled		[leave blank]	[leave blank]	[Default Bid]
```

#### 3. Keyword rows (one per keyword × match type)
```
Sponsored Products	Keyword	Create		[leave blank]	[leave blank]		[leave blank]	[leave blank]	[Campaign Name]	[Ad Group Name]		[EndDate]	Manual	enabled			[leave blank]	[leave blank]	[Bid]			[keyword text]
```

### Campaign structure to generate:

```
Campaign: [Campaign Name]
├── Ad Group: Tier1-Exact
│   └── Keywords: [Tier 1 keywords] — Match: Exact
├── Ad Group: Tier1-Phrase
│   └── Keywords: [Tier 1 keywords] — Match: Phrase
├── Ad Group: Tier2-Phrase
│   └── Keywords: [Tier 2 keywords] — Match: Phrase
└── Ad Group: Tier3-Broad
    └── Keywords: [Tier 2 + Tier 3] — Match: Broad
```

Write the complete TSV file. Confirm file path and row count to user.

---

## STEP 6 — Upload instructions

After generating, tell the user:

```
## How to upload to Amazon

1. Go to Seller Central → Advertising → Campaign Manager
2. Click "Bulk Operations" (top right)
3. Click "Upload" → choose file: launchfast-ppc-bulk-[date].txt
4. Review the preview → click "Submit"

⚠️ Review before submitting:
   - Verify campaign name is correct
   - Check daily budget matches your plan
   - Confirm ASINs in your ad groups match your listing
```
