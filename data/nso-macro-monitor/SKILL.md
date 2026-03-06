---
name: nso-macro-monitor
description: Monitors official Vietnam NSO monthly and quarterly socio-economic releases and compares same-period trends; used when users request official macro updates and year-over-year context.
compatibility: Requires Brave API access.
---

# NSO Macro Monitor (Web Workflow)

Use this skill when the user asks for official macro updates from Vietnam's NSO.

## Data source
- Primary page: https://www.nso.gov.vn/bao-cao-tinh-hinh-kinh-te-xa-hoi-hang-thang

## Tooling assumption
- OpenClaw has built-in web fetch and Brave API.
- Do not write Python for this skill unless explicitly requested.

## Execution workflow
1. Fetch the NSO listing page and extract latest report links.
2. Open the latest monthly/quarterly report page (and linked PDF if available).
3. Extract key macro blocks: growth, inflation, industrial production, trade, credit, retail, FDI.
4. Identify the same period in the previous year.
5. Build a same-period comparison table.
6. Produce a concise sector-impact summary for Vietnam equities.

## Data quality gate (required)
Run this gate before publishing:
1. Freshness: include release date and extraction time in ICT (`UTC+7`).
2. Coverage: confirm both summary page and report/PDF were attempted.
3. Completeness: report missing indicator blocks explicitly (GDP/CPI/IIP/trade/retail/FDI/credit).
4. De-duplication: if multiple reposts of same NSO release exist, keep canonical NSO URL.
5. Claim tagging: mark statements as `Fact` (from NSO) vs `Inference` (sector impact mapping).

## Shared confidence rubric (required)
Apply this common standard:
- `High`: canonical NSO release retrieved, key indicator blocks mostly complete, and dates clearly mapped to same period comparison.
- `Medium`: release retrieved but some indicator blocks or historical comparators are missing.
- `Low`: release not fully accessible (or PDF/text extraction fails materially) and only partial directional summary is possible.

Always output confidence with:
1. Release date + extraction timestamp (ICT `UTC+7`).
2. Completed vs missing indicator blocks.
3. Exact missing items that could alter sector interpretation.

## Output format (required)
- Section 1: Latest NSO release metadata (title, date, URL).
- Section 2: Key indicators table (current vs prior-period vs YoY direction).
- Section 3: Sector implications (banks, real estate, export, energy, consumer, industrials).
- Section 4: Confidence and data gaps.

## Watchlist mode (optional)
If the user provides an `ACTIVE_WATCHLIST`, add Section 3b:
- `Watchlist Impact Map`: map each ticker to the most relevant NSO indicators (Fact) and the transmission channel (Inference).
- Provide 1–2 monitoring triggers per ticker and a confidence tag.

Do **not** output absolute buy/sell instructions.

## Trigger examples
- "Fetch the latest NSO report and compare to the same period last year."
- "Summarize this month NSO macro release for Vietnam equities."
- "What changed in CPI, trade, and industrial production versus last year?"

## Quality rules
- Separate facts from interpretation.
- Cite URLs for every key claim.
- If PDF parsing fails, state it explicitly and continue with accessible text.
- Never fabricate missing statistics.
- If key blocks are missing, downgrade confidence and state what to verify later.
