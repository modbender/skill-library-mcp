# Data Room Builder

Build a structured virtual data room checklist and folder hierarchy for fundraising, M&A, or due diligence.

## When to Use
- Preparing to raise a funding round (Seed through Series C+)
- Selling a business or going through M&A due diligence
- Responding to investor or acquirer document requests
- Organizing company records for board governance

## How It Works

User provides: company stage, industry, round type (or M&A), and any specific investor requests.

You generate:

### 1. Folder Structure
A complete directory tree organized by category:
- **Corporate** — Articles of incorporation, bylaws, board minutes, cap table, shareholder agreements
- **Financial** — P&L (3 years + projections), balance sheet, cash flow, burn rate, revenue breakdown, tax returns
- **Legal** — IP assignments, employment agreements, NDAs, litigation history, regulatory filings
- **Commercial** — Customer contracts, pipeline, churn data, pricing history, partnership agreements
- **Product & Tech** — Architecture docs, security audit, uptime history, roadmap, tech stack summary
- **HR & Team** — Org chart, key employee bios, compensation summary, option pool, hiring plan
- **Compliance** — Data privacy (GDPR/CCPA), insurance certificates, permits, audit reports

### 2. Document Checklist
For each folder, a prioritized checklist:
- 🔴 **Must-have** — Deal won't close without it
- 🟡 **Should-have** — Expected, absence raises questions
- 🟢 **Nice-to-have** — Shows maturity, not required

### 3. Gap Analysis
Compare what the user has against the checklist. Flag missing documents with urgency level and estimated time to produce.

### 4. Access Control Recommendations
- Which documents go in the "teaser" (pre-NDA)
- Which require NDA
- Which are management-presentation-only
- Watermarking and download restrictions

## Rules
- Tailor depth to company stage — don't ask a pre-seed startup for 3 years of audited financials
- Flag documents that typically need legal review before sharing
- Include estimated prep time for each missing document
- Output as Markdown checklist (copy-paste into Notion, Google Docs, or actual data room platform)

## Output Format
Markdown with nested checklists. Each item: `- [ ] Document Name` with priority tag and notes.
