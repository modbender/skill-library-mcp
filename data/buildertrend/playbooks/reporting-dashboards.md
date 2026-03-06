# Reports & Dashboards

## Overview
Navigate Buildertrend's reporting module to pull financial summaries, project performance data, and cross-job analytics. Export reports, schedule automatic delivery, and monitor {{company_name}}'s key KPIs — all from `/app/Reporting`.

## Trigger
- "Run a report", "show me the numbers", "cash flow report"
- "Budget vs actual for [project]", "how's profitability?"
- Weekly/monthly financial review prep
- "Send me the [report type]", "export job costing"
- Scheduled automatic report delivery check

---

## Step 1: Identify Report Type
**Action:** Ask the user which report or suggest based on context

**Message to the user:**
```
📊 Which report do you need?
```

**Inline buttons — Financial Reports:**
| Button | Style | callback_data |
|---|---|---|
| 💰 Cash Flow | `primary` | `bt_report_cashflow` |
| 📈 Profitability | `primary` | `bt_report_profitability` |
| 📊 Budgeted vs Projected | `primary` | `bt_report_budgetvsproj` |
| 🧾 Invoicing | `primary` | `bt_report_invoicing` |
| 🏗️ Work in Progress (WIP) | `primary` | `bt_report_wip` |

**Inline buttons — Project Management Reports:**
| Button | Style | callback_data |
|---|---|---|
| 📅 Schedule % Complete | `primary` | `bt_report_schedule` |
| 📋 CO Profit | `primary` | `bt_report_coprofit` |
| ⏱️ Hours by Job | `primary` | `bt_report_hoursjob` |
| ⏱️ Hours by User | `primary` | `bt_report_hoursuser` |
| 📝 Daily Log Count | `primary` | `bt_report_dailylogs` |
| 📏 Baseline vs Actual | `primary` | `bt_report_baseline` |

**Inline buttons — Sales Reports:**
| Button | Style | callback_data |
|---|---|---|
| 🏷️ Lead Activities by Salesperson | `primary` | `bt_report_leadact` |
| 📊 Lead Count by Salesperson | `primary` | `bt_report_leadcount` |
| 🔍 Lead Status by Source | `primary` | `bt_report_leadsource` |

**Inline buttons — Other:**
| Button | Style | callback_data |
|---|---|---|
| 📋 Job Costing Budget (per job) | `primary` | `bt_report_jobcosting` |
| 🏠 Job Price Summary | `primary` | `bt_report_jobprice` |

---

## Step 2: Navigate to Report
**Action:** Browser Relay → open the selected report

### Report URL Map
| Report | URL |
|---|---|
| Cash Flow | `/app/Reporting/CashflowReport` |
| Profitability | `/app/Reporting/ProfitabilityReport` |
| Budgeted vs Projected | `/app/Reporting/BudgetedVsProjected` |
| Invoicing | `/app/Reporting/InvoicingReport` |
| Work in Progress | `/app/Reporting/WIPReport` |
| Schedule % Complete | `/app/Reporting/SchedulePercentCompleteByJob/` |
| CO Profit | `/Reporting/ReportDetails.aspx?reportType=21&reportFilter=133` |
| Hours by Job | `/app/Reporting/HoursByJobReport` |
| Hours by User | `/Reporting/ReportDetails.aspx?reportType=12&reportFilter=110` |
| Daily Log Count | `/Reporting/ReportDetails.aspx?reportType=2&reportFilter=109` |
| Baseline vs Actual | `/Reporting/ReportDetails.aspx?reportType=15&reportFilter=120` |
| Lead Activities | `/Reporting/ReportDetails.aspx?reportType=5&reportFilter=106` |
| Lead Count | `/Reporting/ReportDetails.aspx?reportType=6&reportFilter=104` |
| Lead Status by Source | `/Reporting/ReportDetails.aspx?reportType=7&reportFilter=108` |
| Job Costing Budget | `/app/JobCostingBudget` (job-scoped) |
| Job Price Summary | `/app/JobFinancials` (job-scoped) |

### Browser Relay Execution
1. Navigate to `https://buildertrend.net{report_url}`
2. Snapshot → confirm report page loaded
3. Wait for data to render (charts/tables may load async)
4. If job-scoped report → ensure correct job is selected in left sidebar

---

## Step 3: Apply Filters
**Action:** Customize report parameters based on the user's request

**Common filter options (vary by report):**
| Filter | Type | Options |
|---|---|---|
| Date Range | Date pickers | Custom, This Month, Last Month, This Quarter, This Year, Last Year |
| Jobs | Multi-select | All jobs or specific selection |
| Status | Multi-select | Open, Closed, Presale, Warranty |
| Job Group | Multi-select | Custom groups defined in BT |
| Job Type | Multi-select | Project types |
| Cost Codes | Multi-select | From {{company_name}}'s 200+ cost codes |
| Users | Multi-select | Internal team members |

### Browser Relay Steps
1. Click filter panel (right side or top bar)
2. Set date range → select start/end dates
3. Select jobs (all or specific)
4. Apply additional filters as needed
5. Click "Apply filter" button
6. Snapshot → verify filtered results

---

## Step 4: Read & Summarize Report Data
**Action:** Extract key metrics from the rendered report and present to the user

**For Financial Reports, extract:**
- Total revenue / projected revenue
- Total costs / projected costs
- Profit / projected profit
- Margin %
- Over/under-billed amounts (WIP)
- Cash flow in vs out

**For Job Costing, extract:**
- Original budget vs revised budget
- Committed costs vs actual costs
- Projected cost to complete
- Variance per cost code category
- Profit margin %

**Present to the user:**
```
📊 [Report Name] — [Date Range]

[Key metrics in clean format]

💡 Observations:
- [Notable trend or issue #1]
- [Notable trend or issue #2]
```

---

## Step 5: Export Report
**Action:** Export report in requested format

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📄 Export PDF | `primary` | `bt_report_export_pdf` |
| 📊 Export Excel | `primary` | `bt_report_export_excel` |
| 📋 Export CSV | `primary` | `bt_report_export_csv` |
| ✅ No export needed | `success` | `bt_report_done` |

### Browser Relay Steps
1. Click Export button (usually top-right of report)
2. Select format (PDF / Excel / CSV)
3. Wait for download to complete
4. Confirm export: "📄 Report exported as [format]"

---

## Step 6: Schedule Automatic Delivery (Optional)
**Action:** Set up recurring report email delivery

**Note:** Report scheduling is available on select reports. Navigate to report → look for "Schedule" or "Email" option.

### Browser Relay Steps
1. Open desired report
2. Click Schedule/Email option (if available)
3. Set frequency (daily, weekly, monthly)
4. Set recipients (email addresses)
5. Set delivery day/time
6. Save schedule

---

## Company-Specific Key Reports for the user

### Weekly Financial Review Package
| Report | What to Check | Why |
|---|---|---|
| Cash Flow | Inflows vs outflows next 30/60/90 days | Predict cash gaps, plan draws |
| Profitability | Margin by job, flagged risk jobs | Catch budget blowouts early |
| Budgeted vs Projected | Variance per job/cost code | Identify overruns before they grow |
| Invoicing | Outstanding invoices, aging | AR aging — who owes what |
| WIP | Over/under-billed status | Revenue recognition accuracy |

### Monthly Close Reports
| Report | Purpose |
|---|---|
| Job Costing Budget (all jobs) | Full cost audit per project |
| CO Profit | Change order profitability check |
| Hours by Job | Labor cost allocation verification |
| Lead Count by Salesperson | Sales pipeline health |

### Quick KPI Dashboard (Manual)
Build from Job Price Summary (`/app/JobFinancials`):
- **Total active project value** — sum of all contract prices
- **Total billed to date** — sum of invoiced amounts
- **Total collected** — payments received
- **AR aging** — outstanding balances by age
- **Sub payment status** — bills pending vs paid

---

## Smart Suggestions

| Context | Suggestion |
|---|---|
| the user says "how's the budget?" | Run Budgeted vs Projected for all open jobs |
| the user says "cash flow" | Run Cash Flow report, 90-day window |
| Before client meeting | Run Profitability + Invoicing for that job |
| Monthly close | Run WIP + Invoicing + Job Costing |
| the user asks about a specific sub | Run Bills list filtered by that vendor |
| Payroll time | Run Hours by Job + Hours by User for pay period |

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| Report shows "No data" | Check date range and job filters — may be too restrictive |
| Report takes too long to load | Wait additional 10s, re-snapshot. If still loading, suggest narrower filter |
| Export fails | Retry once. If persistent, screenshot error and report |
| Browser relay disconnected | Stop, ask the user to re-enable extension |
| Report not available for plan | Notify the user — may require plan upgrade or BT Business Insights add-on |

---

## Batch Mode
When the user asks for a "full financial review" or "weekly report package":

1. Run Cash Flow report → extract summary
2. Run Profitability report → extract summary
3. Run Budgeted vs Projected → extract summary
4. Run Invoicing report → extract summary
5. Compile all summaries into one messaging platform message
6. Offer export: "Want me to export all 4 as PDFs?"

**Progress tracking:**
```
📊 Running weekly report package...
✅ Cash Flow — done
✅ Profitability — done
⏳ Budgeted vs Projected — running...
⬜ Invoicing — pending
```

---

## URL Patterns
| Page | URL |
|---|---|
| Reports Hub | `/app/Reporting` |
| Cash Flow | `/app/Reporting/CashflowReport` |
| Profitability | `/app/Reporting/ProfitabilityReport` |
| Budgeted vs Projected | `/app/Reporting/BudgetedVsProjected` |
| Invoicing | `/app/Reporting/InvoicingReport` |
| WIP | `/app/Reporting/WIPReport` |
| Schedule % Complete | `/app/Reporting/SchedulePercentCompleteByJob/` |
| Hours by Job | `/app/Reporting/HoursByJobReport` |
| Job Costing Budget | `/app/JobCostingBudget` |
| Job Price Summary | `/app/JobFinancials` |
