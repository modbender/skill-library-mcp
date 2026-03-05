# Cost Code Configuration & Management (Agent-Assisted)

## Overview
Cost Codes are the foundation of ALL financial features in Buildertrend — every estimate, bid, bill, PO, invoice, selection, change order, and budget line depends on them. This playbook covers creating, organizing, importing, mapping to QBO, and managing {{company_name}}'s 200+ cost code structure across 43 categories.

## Trigger
- the user says "set up cost codes", "add new cost code", "check cost code mapping"
- New job setup requires cost code review
- QBO reconciliation reveals unmapped codes
- bookkeeper agent flags missing cost code → QBO account mapping
- New trade category needed for a project

---

## Step 1: Navigate to Cost Codes Settings
**Action:** Open Cost Code configuration

```
browser → navigate to https://buildertrend.net/app/Settings/CostCodes
browser → snapshot → verify Cost Codes settings page loaded
```

**URL:** `/app/Settings/CostCodes`
**Tabs:** Cost Codes | Variances
**Actions:** New, Import, Inactive toggle, More button

---

## Step 2: Understand {{company_name}}'s Cost Code Structure

### Architecture
```
00 - BILLABLE (parent)
  └── Category (e.g., "01 - GENERAL CONDITIONS")
       └── Cost Code (e.g., "01.01 - Site material Purchases")

00 - NON-BILLABLE (parent)
  └── Cost Code (e.g., "00-01 - Insurance")

00 - TIME TRACKING (parent)
  └── Cost Code (e.g., "00.10 - Time Tracking Cost code")

Buildertrend Default (parent)
  └── Buildertrend Flat Rate (default placeholder)
```

### {{company_name}}'s Complete Category Structure (43 BILLABLE Categories)

| # | Category | Codes | Range |
|---|---|---|---|
| 01 | GENERAL CONDITIONS | 8 | 01.00 – 01.50 |
| 02 | GENERAL REQUIREMENTS | 11 | 02.00 – 02.45 |
| 03 | SUPERSTRUCTURE | 5 | 03.00 – 03.50 |
| 04 | EXCAVATION FOUNDATION | 10 | 04.00 – 04.40 |
| 05 | CARPENTRY / FRAMING | 4 | 05.00 – 05.05 |
| 06 | ROOFING | 4 | 06.00 – 06.25 |
| 07 | PLUMBING | 8 | 07.00 – 07.40 |
| 08 | ELECTRICAL | 5 | 08.00 – 08.20 |
| 09 | HVAC | 8 | 09.00 – 09.70 |
| 10 | INSULATION & DRYWALL | 7 | 10.00 – 10.31 |
| 11 | GLAZING | 5 | 11.00 – 11.15 |
| 12 | CARPENTRY / MILLWORK | 8 | 12.00 – 12.70 |
| 13 | WINDOWS & DOORS | 6 | 13.00 – 13.35 |
| 14 | PAINTING AND COATING | 4 | 14.00 – 14.25 |
| 15 | FLOORING & TILE | 5 | 15.00 – 15.30 |
| 16 | APPLIANCES | 3 | 16.00 – 16.20 |
| 17 | BRICK & MASONRY | 5 | 17.00 – 17.15 |
| 18 | EXTERIOR WORKS | 7 | 18.00 – 18.60 |
| 19 | CLEANING | 2 | 19.00 – 19.10 |
| 20 | DEMOLITION | 3 | 20.10 – 20.30 |
| 21 | METAL FABRICATIONS | 6 | 21-20 – 21.60 |
| 22 | CEILINGS | 3 | 22.10 – 22.30 |
| 23 | WALL FINISHES | 3 | 23.05 – 23.50 |
| 24 | SOLAR PANELS | 1 | 24.00 |
| 25 | FIRE PROTECTION | 4 | 25.10 – 25.25 |
| 26 | AUDIO VISUAL / SECURITY | 7 | 26.00 – 26.70 |
| 27 | FIRE ALARM | 3 | 27.00 – 27.20 |
| 28 | COUNTERTOPS | 5 | 28.00 – 28.40 |
| 29 | UTILITIES | 7 | 29.00 – 29.60 |
| 30 | EXTERIOR FAQADES | 6 | 30.00 – 30.50 |
| 31 | ELEVATOR | 3 | 31.00 – 31.20 |
| 32 | SCAFFOLDING / SHEDS | 6 | 32.00 – 32.40 |
| 33 | WINDOW TREATMENTS | 2 | 33.00 – 33.10 |
| 34 | SIGNAGE | 5 | 34.00 – 34.40 |
| 35 | STRUCTURAL STEEL | 4 | 35.00 – 35.20 |
| 36 | HAZARDOUS MATERIALS | 2 | 36.00 – 36.10 |
| 37 | PROJECT SPECIFIC INSURANCE | 1 | 37.00 |
| 38 | CURTAINS | 2 | 38.10 – 38.20 |
| 39 | RENTAL EQUIPMENT | 1 | 39.00 |
| 40 | FIRE PROOFING | 3 | 40.00 – 40.20 |
| 41 | MATERIALS | 4 | 41.10 – 41.50 |

### NON-BILLABLE Codes (9)
| Code | Name |
|---|---|
| 00-01 | Insurance |
| 00.02 | Auto Insurance |
| 00.03 | Workers Comp |
| 00.04 | Disability Insurance |
| 00.05 | Tickets and Violations |
| 00.06 | Technology Expenses |
| 00.07 | Material Purchases |
| 00.08 | General Administrative |
| 00.09 | Auto Expenses |

### TIME TRACKING Codes (2)
| Code | Name |
|---|---|
| 00.10 | Time Tracking Cost code |
| 00.20 | Driver |

**Total: 200+ cost codes across 43 BILLABLE categories + 9 NON-BILLABLE + 2 TIME TRACKING + 1 default**

---

## Step 3: Create a New Cost Category

### When to Create a Category
- New trade/discipline not covered by existing 43 categories
- Organization needs new grouping level

### Steps
```
browser → snapshot → navigate to Cost Codes settings
browser → snapshot → click "New" button
browser → snapshot → select "New Category"
browser → snapshot → fill Category Name (use format: "XX - CATEGORY NAME")
browser → snapshot → set numbering/ordering
browser → snapshot → click "Save"
browser → snapshot → verify category created
```

**Naming Convention:** `[2-digit number] - [UPPERCASE NAME]`
- Keep numbers sequential with existing categories
- Use leading zeros for single digits

---

## Step 4: Create a New Cost Code

### Within an Existing Category
```
browser → snapshot → expand the target category
browser → snapshot → click "+" or "Add Cost Code" within category
browser → snapshot → fill fields:
```

| Field | Type | Required | Notes |
|---|---|---|---|
| Code Number | Text | **Yes** | Format: `XX.XX` (e.g., `01.51`) |
| Name | Text | **Yes** | Descriptive name |
| Cost Type | Dropdown | No | Material, Labor, Sub, Equipment, Other |
| Time Clock Labor Code | Checkbox | No | Enable for Time Clock use |
| Description | Text | No | Internal reference |

```
browser → snapshot → click "Save"
browser → snapshot → verify code created under correct category
```

### Cost Type Definitions
| Type | Description | Budget Impact |
|---|---|---|
| Material | Physical materials purchased | Material costs column |
| Labor | Employee labor hours | Labor costs column |
| Subcontractor | Sub/vendor contracted work | Subcontractor costs column |
| Equipment | Equipment rental/purchase | Equipment costs column |
| Other | Miscellaneous costs | Other costs column |
| None | Not specified | General costs |

**Note:** Cost Type filtering only available for jobs created after June 12, 2024.

---

## Step 5: Import Cost Codes

### Import from Excel
```
browser → snapshot → click "Import" button
browser → snapshot → download Excel template
(fill in template with cost codes, categories, types)
browser → snapshot → click "Browse" → select filled template
browser → snapshot → map columns to BT fields
browser → snapshot → review imported codes
browser → snapshot → click "Import"
browser → snapshot → verify all codes imported
```

### Import from QBO (Accounting Integration)
```
browser → navigate to https://buildertrend.net/app/Settings/Settings/Accounting
browser → snapshot → find cost code mapping section
browser → snapshot → click "Import from QuickBooks"
browser → snapshot → map QBO Products & Services → BT Cost Codes
browser → snapshot → create new codes or select existing matches
browser → snapshot → save mapping
```

### Import from BT Recommended List
```
browser → snapshot → click "Import" → select "Buildertrend Recommended"
browser → snapshot → review recommended codes
browser → snapshot → select codes to import
browser → snapshot → click "Import"
```

---

## Step 6: Map Cost Codes to QBO Accounts

### Why Mapping Matters
- Cost Codes in BT ≠ Chart of Accounts in QBO
- BT Cost Codes map to QBO **Products & Services (Items)**
- Proper mapping ensures bills, invoices, and time entries sync correctly

### Mapping Process
```
browser → navigate to https://buildertrend.net/app/Settings/Settings/Accounting
browser → snapshot → find "Manage links" or cost code mapping section
browser → snapshot → for each BT cost code, select matching QBO Product/Service
browser → snapshot → save mapping
```

**Mapping Strategy for {{company_name}}:**
| BT Cost Code | → | QBO Product/Service |
|---|---|---|
| 01.01 Site material Purchases | → | Site Materials (COGS) |
| 05.05 Non-Structural Framing | → | Carpentry (COGS) |
| 08.00 Electrical | → | Electrical (COGS) |
| 14.00 Painting | → | Painting (COGS) |
| 00-01 Insurance (NON-BILL) | → | Insurance Expense |

**⚠️ Important:** When creating bills in BT with "Send to QuickBooks" checked, the cost code mapping determines which QBO account the expense hits.

---

## Step 7: Set Default Cost Codes per Vendor

### Smart Defaults
When creating bills/POs, BT can suggest cost codes based on the assigned vendor:
- Home Depot → 41.10 Materials - General
- Electrical supply → 08.00 Electrical
- Plumbing supply → 07.00 Plumbing
- See `receipt-to-bill.md` for full vendor → cost code mapping

### Setting Defaults
Default cost codes are suggested based on:
1. Vendor's previous bill history (BT learns from patterns)
2. Cost Catalog items (pre-configured in Catalog settings)
3. Manual suggestion logic in agent playbooks

---

## Step 8: Deactivate/Delete Cost Codes

### Deactivate (Recommended)
- Keeps code for historical reporting
- Removes from new job dropdowns
- Use when code is no longer needed but has been used in financial features

```
browser → snapshot → find the cost code to deactivate
browser → snapshot → click edit/options on the code
browser → snapshot → toggle "Active" to off / click "Deactivate"
browser → snapshot → verify code moved to Inactive list
```

### Delete (Only if Never Used)
- **Only possible** if the code has never been used in any feature
- If used anywhere → deactivate instead
- Deletion is permanent

### View Inactive Codes
```
browser → snapshot → toggle "Show Inactive" / "Inactive" filter
browser → snapshot → review deactivated codes
```

---

## Step 9: Budget Allocation per Cost Code per Job
**Action:** Assign budget amounts to cost codes within a job's estimate

This happens during the **Estimate** phase (see `run-estimates.md`):
1. Build Estimate with line items per cost code
2. Set unit costs and quantities
3. "Send to Budget" → creates Job Costing Budget
4. Each cost code gets an Original Budget amount
5. Revised Budget updates with approved COs and Selections

```
browser → navigate to https://buildertrend.net/app/Estimate
(for specific job)
browser → snapshot → review line items by cost code
browser → snapshot → verify budget amounts per code
```

---

## Step 10: Variance Codes
**Action:** Manage variance codes for unexpected costs

**Variance Codes Tab:** `/app/Settings/CostCodes` → Variances tab

| Variance Type | Purpose |
|---|---|
| Customer Variance | Client-initiated changes (shows in Revised Client Price) |
| Builder Variance | Builder-covered costs (doesn't affect client price) |
| Custom Variance | Other variance categories |

**Key Variance Code:** "72 – Client Change Order" = client-initiated variance, flows to budget correctly.

```
browser → snapshot → click "Variances" tab
browser → snapshot → review existing variance codes
browser → snapshot → click "New" to create if needed
browser → snapshot → set Name, mark as Customer/Builder variance
browser → snapshot → save
```

---

## Features That Use Cost Codes
| Feature | How Cost Codes Are Used |
|---|---|
| Estimates | Line items assigned to cost codes |
| Bids | Bid packages linked to cost codes |
| Purchase Orders | PO line items assigned to cost codes |
| Bills | Bill line items assigned to cost codes |
| Change Orders | CO line items assigned to cost codes |
| Invoices | Invoice line items by cost code |
| Selections | Allowances linked to cost codes |
| Time Clock | Labor entries assigned to time tracking codes |
| Job Costing Budget | Budget organized by cost code |
| Deposits | Deposit allocations by cost code |
| QBO Sync | Cost codes map to QBO Products & Services |

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| Cost code already exists | Check for duplicate — may need different code number |
| Cannot delete used code | Deactivate instead — code has transaction history |
| QBO mapping missing | Navigate to Accounting Settings → map the code |
| Code not appearing in dropdown | Check if deactivated, check job assignment |
| Flat Rate default on receipts | Receipt not assigned a code — needs manual assignment |
| "Buildertrend Flat Rate" on bill | Replace with proper cost code before QB sync |

---

## Best Practices (from BT Help Center)

1. **Keep it Simple** — clear purpose, used on most jobs (5-10 or hundreds depending on needs)
2. **Track Labor/Materials Separately** — decide level of detail needed for job costing
3. **Numbering System** — organize numerically with leading zeros (e.g., 001, 01.01)
4. **Gather Team Input** — estimating, accounting, bidding, invoicing teams should agree
5. **Avoid Excessive Codes** — use Titles & Descriptions for specificity, not new codes
6. **Limit Sub-Codes** — add complexity without reporting benefits
7. **Avoid Duplicates** — no similar codes with different numbers
8. **Establish Before Financial Features** — ⚠️ CRITICAL: set up codes before creating any estimates, bills, POs
9. **Build Cost Catalog After** — create frequently used cost items linked to codes

---

## Company-Specific Notes
- **200+ codes** already established across 43 BILLABLE categories
- **QBO Connected:** QuickBooks Online Plus, company "{{company_name}}"
- **Tax Rate:** {{tax_jurisdiction}} {{tax_rate}}% (adjust to your local rates)
- **Settings URL:** `/app/Settings/CostCodes`
- **Catalog URL:** `/app/Settings/CostCatalogSettings?viewType=1`
- Most common codes: 01.00-01.50 (General), 05.00-05.05 (Carpentry), 08.00 (Electrical), 14.00 (Painting)
- Non-billable codes (00-01 through 00.09) for overhead/admin expenses
