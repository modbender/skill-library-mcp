# Job Costing Report (Agent-Assisted)

## Overview
The agent navigates to a project's Job Costing Budget in Buildertrend, extracts estimated vs actual vs projected costs per cost code, calculates variance, and delivers a formatted summary to the user on messaging platform. Highlights over-budget items and optionally saves the report to Google Drive.

## Trigger
- the user says "how's the budget on [project]?" or "job costing report for [project]"
- the user says "are we over budget on anything?"
- Weekly/monthly budget review cycle
- Before creating an invoice (to verify profitability)
- Before a client meeting (to review financials)

---

## Step 1: Identify Project
**Action:** Confirm which project to report on

**Message to the user:**
```
📊 Job Costing Report — which project?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Project Alpha | `primary` | `bt_jc_project_1` |
| 🏗️ Project Alpha | `primary` | `bt_jc_project_1` |
| 🏗️ Project Beta | `primary` | `bt_jc_project_2` |
| 🏗️ Project Beta | `primary` | `bt_jc_project_2` |
| 🏗️ Project Epsilon | `primary` | `bt_jc_project_3` |
| 🏗️ Project Gamma | `primary` | `bt_jc_project_4` |
| 🏗️ Project Eta | `primary` | `bt_jc_project_5` |
| 📊 All Projects Summary | `primary` | `bt_jc_project_all` |
| ❌ Cancel | `danger` | `bt_jc_cancel` |

---

## Step 2: Extract Budget Data via Browser Relay
**Action:** Navigate to Job Costing Budget and scrape all data

### Browser Relay Execution
1. Ensure correct job is selected in BT left sidebar
2. Navigate to `/app/JobCostingBudget`
3. Snapshot → read the full page

### Data to Extract

**Profitability Summary (top section):**
| Field | Location |
|---|---|
| Revised Client Price | Profitability summary bar |
| Projected Total Costs | Profitability summary bar |
| Projected Profit | Profitability summary bar |
| Projected Margin % | Profitability summary bar |
| Amount Invoiced | Profitability summary bar |
| Remaining to Invoice | Profitability summary bar |

**Per Cost Code (table rows):**
| Field | Column Header |
|---|---|
| Cost Code | "Cost codes" column |
| Original Budget | "Original budget costs" column |
| Revised Budget | "Revised budget costs" column |
| Pending Costs | "Pending costs" column |
| Committed Costs | "Committed costs" column |
| Actual Costs | "Actual costs" column |
| Builder Variance | "Builder variance" column |
| Complete | "Complete" checkbox column |
| Projected Costs | "Projected costs" column |
| Cost to Complete | "Cost to complete" column |
| Revised vs Projected | "Revised vs projected" column |

4. **Expand all categories** if collapsed (click "Expand all" button)
5. Parse each row — cost codes are nested under category headers
6. Capture unbudgeted items (actual costs with $0 original budget)
7. Snapshot each section if table is long

---

## Step 3: Calculate Variance & Format Report
**Action:** Process extracted data and generate report

### Calculations Per Cost Code:
```
Variance ($) = Actual Costs - Revised Budget
Variance (%) = (Actual Costs - Revised Budget) / Revised Budget × 100
Status = 
  - "✅ Under" if Actual < Revised
  - "⚠️ At Risk" if Actual > 80% of Revised but < Revised
  - "🔴 OVER" if Actual > Revised
  - "⬜ No Spend" if Actual = 0
  - "🆕 Unbudgeted" if Original Budget = 0 and Actual > 0
```

### Report Format:

**Message to the user:**
```
📊 JOB COSTING REPORT
🏗️ [Project Name]
📅 As of [date]

━━━ PROFITABILITY SUMMARY ━━━
💰 Contract: $[revised_client_price]
📊 Projected Costs: $[projected_costs]
📈 Projected Profit: $[projected_profit] ([margin]%)
📤 Invoiced: $[invoiced] ([pct]%)
📥 Remaining: $[remaining_to_invoice]

━━━ BUDGET STATUS ━━━
```

Then present cost codes grouped by category:

```
📁 01 - GENERAL CONDITIONS
| Code | Description | Budget | Actual | Projected | Variance | Status |
|------|-------------|--------|--------|-----------|----------|--------|
| 01.00 | General Conditions | $5,000 | $3,200 | $5,000 | -$1,800 | ✅ Under |
| 01.02 | Carpentry Labor | $4,200 | $4,200 | $4,200 | $0 | ✅ On Budget |
| 01.01 | Site Materials | $0 | $209 | $209 | +$209 | 🆕 Unbudgeted |

📁 05 - CARPENTRY / FRAMING
| Code | Description | Budget | Actual | Projected | Variance | Status |
|------|-------------|--------|--------|-----------|----------|--------|
| 05.05 | Non-Structural | $20,000 | $22,500 | $22,500 | +$2,500 | 🔴 OVER |

...

━━━ OVER-BUDGET ITEMS (Action Required) ━━━
🔴 05.05 Non-Structural Framing: $2,500 OVER ($22,500 vs $20,000 budget)
🔴 14.00 Painting: $400 OVER ($5,400 vs $5,000 budget)
🆕 01.01 Site Materials: $209 unbudgeted spend
🆕 34.30 Street Signs: $1 unbudgeted spend

━━━ TOTALS ━━━
Original Budget: $[original_total]
Revised Budget: $[revised_total]
Actual Costs: $[actual_total]
Projected Costs: $[projected_total]
Total Variance: $[total_variance] ([over_under])
```

---

## Step 4: Deliver Report
**Action:** Send the report and offer follow-up actions

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 💾 Save to Google Drive | `primary` | `bt_jc_save_drive` |
| 📊 Export as Spreadsheet | `primary` | `bt_jc_export_xlsx` |
| 🔍 Drill into [worst code] | `primary` | `bt_jc_drill_[code]` |
| 📋 Compare to last month | `primary` | `bt_jc_compare` |
| 🔄 Refresh data | `primary` | `bt_jc_refresh` |
| 👍 Thanks, that's all | `success` | `bt_jc_done` |

### If "Save to Google Drive":
- Format as markdown or Excel
- Save to project folder: `Projects/[Project]/Other Documents/`
- Filename: `Job-Costing-Report_YYYY-MM-DD.md` or `.xlsx`

### If "Export as Spreadsheet":
- Use XLSX skill to create a formatted Excel workbook
- Columns: Cost Code, Description, Original Budget, Revised Budget, Committed, Actual, Projected, Variance $, Variance %, Status
- Color code: Red rows for over-budget, green for under, yellow for at risk
- Save and send via messaging

### If "Drill into [code]":
Navigate to that cost code in BT → click for detail → extract:
- Related Bills (amounts, vendors, dates)
- Related POs (amounts, vendors, status)
- Time Clock entries (hours, rates)
- Change Order impacts

**Message:**
```
🔍 Detail: [cost code] — [name]

📦 Purchase Orders:
| PO # | Vendor | Amount | Status |
|------|--------|--------|--------|
| PO-001 | ABC Plumbing | $8,500 | Approved |

🧾 Bills:
| Bill # | Vendor | Amount | Date | Status |
|--------|--------|--------|------|--------|
| B-001 | ABC Plumbing | $4,250 | Jan 15 | Paid |
| B-002 | ABC Plumbing | $4,250 | Feb 1 | Open |

⏱️ Time Clock: $0 (no labor entries)
```

---

## Step 5: All-Projects Summary (if requested)
When the user wants a cross-project overview:

1. Navigate to `/app/JobCostingBudget` for each active project
2. Extract profitability summary from each
3. Compile into a dashboard:

```
📊 ALL PROJECTS — Financial Dashboard
📅 As of [date]

| Project | Contract | Projected Cost | Profit | Margin | Invoiced | Status |
|---------|----------|---------------|--------|--------|----------|--------|
| Project Alpha | $350K | $280K | $70K | 20% | $175K (50%) | ✅ Healthy |
| Project Alpha | $800K | $720K | $80K | 10% | $500K (63%) | ⚠️ Watch |
| Project B | $500K | $420K | $80K | 16% | $250K (50%) | ✅ Healthy |
| Project Gamma | $350K | $280K | $70K | 20% | $150K (43%) | ✅ Healthy |
| ... |

💰 Total Portfolio: $[total_contract]
📈 Projected Total Profit: $[total_profit]
📤 Total Invoiced: $[total_invoiced]
📥 Total Outstanding: $[total_remaining]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🔍 Drill into [worst project] | `primary` | `bt_jc_drill_project_[code]` |
| 💾 Save dashboard to Drive | `primary` | `bt_jc_save_dashboard` |
| 📊 Full detail per project | `primary` | `bt_jc_full_all` |

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| No estimate sent to budget | Report: "No budget data — estimate hasn't been sent to budget yet" |
| Budget table too large to parse | Extract in sections (by category), snapshot each |
| Numbers don't add up | Report discrepancy, suggest: "Check BT settings — Cash vs Accrual may affect totals" |
| Browser relay disconnected | Stop, ask the user to re-enable the extension |
| Job not found in BT | Verify job name/selection in sidebar |
| QB costs not showing | Check: "Include costs entered in QuickBooks in budget" setting |

---

## Budget Concepts Quick Reference

| Term | Definition | Formula |
|---|---|---|
| Original Budget | From signed proposal (estimate → send to budget) | = Estimate builder cost |
| Revised Budget | Original + Selections + Change Orders | = Original + approved COs + selections |
| Committed | Approved POs + Variance POs + unapproved Time | Sum of all commitments |
| Actual (Accrual) | Open/paid Bills + Variance Bills + approved Time + QB costs | Sum of all recorded costs |
| Actual (Cash) | Paid Bills + Variance Bills + approved Time + QB costs | Cash-basis costs only |
| Projected | Greatest of: Revised, Committed, or Actual | = MAX(Revised, Committed, Actual) |
| Cost to Complete | How much more will be spent | = Projected − Actual |
| Revised vs Projected | Over/under budget | = Projected − Revised |
| Builder Variance | Builder-covered costs (not client variances) | Cost overruns absorbed by the company |
| Complete | Flag that resets Projected = Actual | Mark when cost code is fully done |

### Profitability Status Thresholds
| Status | Condition | Action |
|---|---|---|
| ✅ Healthy | Margin > 15% | No action needed |
| ⚠️ Tight | Margin 5-15% | Monitor closely |
| 🔴 Risk | Margin < 5% | Review all costs, find savings |
| 💀 Loss | Margin < 0% | Immediate attention — stop the bleeding |

---

## Report Schedule (Suggested)
| Frequency | Report Type | Best For |
|---|---|---|
| Weekly | Single project detail | Active projects with high spend |
| Bi-weekly | All projects summary | Portfolio overview |
| Monthly | Full detail + Drive export | Client meetings, partner reviews |
| On-demand | Drill-down per code | Cost overrun investigation |
