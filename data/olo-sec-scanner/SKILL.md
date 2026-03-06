---
name: olo-sec-scanner
version: 1.0.0
description: SEC EDGAR filing analysis for M&A due diligence — extract financials, detect risks, and track corporate events from 10-K, 10-Q, and 8-K filings
author: ololand.ai
author_url: https://ololand.ai
license: MIT
triggers:
  - sec filing
  - edgar
  - 10-k analysis
  - 10-q analysis
  - 8-k filing
  - annual report
  - quarterly report
  - sec extraction
  - xbrl
tags:
  - finance
  - sec
  - m-and-a
  - due-diligence
  - regulatory
---

# SEC Filing Scanner for M&A

Extract and analyze SEC EDGAR filings for acquisition due diligence.

## Data Source

SEC EDGAR API (free, no API key, 10 req/sec rate limit):
- Company Facts: `https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json`
- Submissions: `https://data.sec.gov/submissions/CIK{cik}.json`
- Full-Text Search: `https://efts.sec.gov/LATEST/search-index?q=...`

## Filing Types & M&A Relevance

| Filing | Use Case |
|--------|----------|
| 10-K | Annual financials, risk factors, segment data, legal proceedings |
| 10-Q | Quarterly trends, interim changes, going concern flags |
| 8-K | Material events: acquisitions, dispositions, leadership changes, restatements |
| DEF 14A | Executive comp, related-party transactions, governance |
| SC 13D/G | Activist positions, ownership changes above 5% |
| Form 4 | Insider buying/selling patterns (signal conviction) |
| Form D | Private placement activity (pre-IPO targets) |

## Extraction Framework

### 1. Financial Extraction (from XBRL)
- Revenue (3-5 year trend from `Revenues` or `RevenueFromContractWithCustomerExcludingAssessedTax`)
- EBITDA (computed: `OperatingIncome` + `DepreciationAndAmortization`)
- Net income, EPS, diluted shares
- Total assets, total liabilities, stockholders' equity
- Operating cash flow, CapEx, free cash flow
- Segment revenue breakdown (if multi-segment)

### 2. Risk Factor Analysis (from 10-K Item 1A)
- Categorize risks: market, operational, regulatory, financial, legal, technology
- Flag risks mentioning: litigation, regulatory investigation, material weakness, going concern
- Compare risk factors year-over-year to detect new disclosures
- Score overall risk severity (low / moderate / elevated / high)

### 3. Material Event Detection (from 8-K)
- Item 1.01: Entry into material agreement
- Item 2.01: Completion of acquisition or disposition
- Item 2.05: Costs of restructuring
- Item 4.01: Change in accountant (red flag)
- Item 5.02: Departure of directors/officers
- Item 8.01: Other material events

### 4. Ownership & Governance (from DEF 14A, 13D/G)
- Top institutional holders and concentration
- Insider ownership percentage
- Recent insider transactions (net buying vs. selling)
- Activist involvement flags

## Output Format

```
SEC Filing Analysis: [Company Name] (CIK: XXXXXXXXXX)

Filings Scanned: 12 (3x 10-K, 8x 10-Q, 1x 8-K)
Date Range: 2023-01-01 to 2025-12-31

Financial Summary (from XBRL):
  Revenue TTM:     $164.5M (↑ 12% YoY)
  EBITDA TTM:      $28.3M  (17.2% margin)
  FCF TTM:         $22.1M
  Net Debt:        $45.0M  (1.6x EBITDA)

Risk Flags:
  ⚠ New risk factor: "concentration of revenue" (added FY2025)
  ⚠ Material weakness in internal controls (10-K Item 9A)
  ✓ No going concern language
  ✓ No change in auditor

Material Events (8-K):
  2025-09-15: Entered into $50M credit facility (Item 1.01)
  2025-06-01: CFO departure (Item 5.02)

Insider Activity (Last 12 months):
  Net Selling: $2.3M (3 insiders sold, 0 bought)
```

## M&A-Specific Checks

- **Change of control provisions**: Search 10-K for "change of control", "golden parachute", "poison pill"
- **Material contracts**: Identify contracts with change-of-control triggers
- **Customer concentration**: Extract from risk factors or segment data
- **Pending litigation**: Quantify contingent liabilities from footnotes
- **NOL carryforwards**: Extract tax asset values (Section 382 limitation risk in acquisition)
- **Lease obligations**: Right-of-use assets and total lease commitments
