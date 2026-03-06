---
name: incorporate
description: Generate complete incorporation documents for a new business entity. Use when forming a C-Corp, S-Corp, or LLC in any US state. Produces Articles of Incorporation/Organization, Bylaws/Operating Agreement, Incorporator Action, Organizational Resolutions, Stock/Membership Ledger, and Filing Checklist — all from a simple config. Handles cap tables, voting structures, registered agents, and multi-class stock. Currently optimized for Nevada; extensible to other states.
---

# Incorporate — Business Formation Document Generator

Generate all legal documents needed to incorporate a business entity from a single configuration.

## Supported Entity Types & States

| Entity | States | Reference File |
|--------|--------|---------------|
| C-Corp | Nevada | `references/nevada-corp.md` |
| C-Corp | Delaware | `references/delaware-corp.md` |
| LLC | Nevada | `references/nevada-llc.md` |
| LLC | Delaware | `references/delaware-llc.md` |

## Quick Start

1. Ask the user for their company details (or have them fill out the config)
2. Read `references/config-template.md` — this is the input format
3. Read the appropriate state + entity reference file (see table above)
4. Read the document templates from `assets/templates/` (use `de-*` for Delaware, `llc-*` for LLCs)
5. Generate all documents using the config values
6. Upload to Google Drive (or output as .docx files)

## Workflow

### Step 1: Gather Configuration

Ask the user these questions (or accept a pre-filled config):

**Required:**
- Company name
- Entity type (C-Corp, LLC)
- State of incorporation
- Registered agent name + address
- Directors/managers (names, titles)
- Shareholders/members (names, share counts or %)
- Stock structure (classes, authorized shares, par value, voting rights)

**Optional (defaults provided):**
- Par value (default: $0.00001)
- Fiscal year end (default: December 31)
- Consideration type (default: "Services")
- Principal office address (default: registered agent address)

Validate the config: share percentages must total 100%, authorized shares must cover all issuances.

### Step 2: Select Entity + State References

Based on entity type and state, read the appropriate reference file:
- Nevada C-Corp → `references/nevada-corp.md`
- Delaware C-Corp → `references/delaware-corp.md`
- Nevada LLC → `references/nevada-llc.md`
- Delaware LLC → `references/delaware-llc.md`

**Key decision guidance for the user:**
- **C-Corp vs LLC:** C-Corp for VC fundraising, multiple stock classes, going public. LLC for simpler businesses, pass-through taxation, flexible profit distribution.
- **Delaware vs Nevada:** Delaware for investor expectations, Court of Chancery, VC-standard docs. Nevada for no franchise tax, lower annual costs, privacy.
- **Delaware C-Corp warning:** Franchise tax can be very high with many authorized shares — always use the Assumed Par Value Capital Method (see delaware-corp.md).

### Step 3: Generate Documents

Read each template from `assets/templates/` and replace all `{{VARIABLES}}` with config values. Templates are in Markdown — convert to .docx for final output.

**Documents generated (C-Corp):**
1. **Articles of Incorporation** — filed with Secretary of State
2. **Bylaws** — internal governance rules
3. **Action of Incorporator** — appoints initial board
4. **Organizational Resolutions** — board adopts bylaws, elects officers, authorizes stock
5. **Stock Ledger** — records all share ownership + voting power summary
6. **Filing Checklist** — step-by-step guide with links to each document

**Documents generated (LLC):**
1. **Articles of Organization** — filed with Secretary of State (template: `llc-01-articles-of-organization.md`)
2. **Operating Agreement** — governance, economics, member rights (template: `llc-02-operating-agreement.md`)
3. **Membership Ledger** — records ownership and transfers (template: `llc-03-membership-ledger.md`)
4. **Filing Checklist** — step-by-step guide (template: `llc-04-filing-checklist.md`)

**Delaware C-Corp uses different template for Articles:**
- Use `de-01-certificate-of-incorporation.md` instead of `01-articles-of-incorporation.md`
- Delaware calls it "Certificate of Incorporation" not "Articles"
- Includes exculpation clause (DGCL §102(b)(7)) and blank check preferred authorization
- All other C-Corp documents (Bylaws, Action, Resolutions, Stock Ledger, Checklist) are the same with state-specific adjustments

### Step 4: Format + Deliver

- All text: Times New Roman, black, 12pt headers, 11pt body
- Tables: bordered, alternating row shading, dark blue headers
- Highlight in yellow any fields that still need manual input
- Upload to Google Drive or save as local .docx files
- Link each document from the Filing Checklist

### Step 5: Walk Through Next Steps

After generating docs, brief the user on filing sequence:
1. File Articles with Secretary of State (online if available)
2. Sign Action of Incorporator (after filing confirmed)
3. Hold organizational meeting / sign resolutions
4. Issue stock / record in ledger
5. File Initial List of Officers (if required by state, within deadline)
6. Obtain EIN from IRS
7. Open bank account

## Important Notes

- These are standard formation documents, not legal advice
- Complex structures (convertible notes, vesting schedules, multiple preferred series) should involve a lawyer
- State-specific requirements vary — always check the state reference file
- Annual maintenance requirements differ by state — included in checklist
- **Delaware franchise tax** can be very expensive — see `references/delaware-corp.md` for the Assumed Par Value method
- **LLC operating agreements** are highly customizable — the template covers standard provisions but complex arrangements (waterfall distributions, vesting, drag-along rights) need legal review
