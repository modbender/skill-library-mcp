# Spreadsheet Engineering — AfrexAI

> Build bulletproof spreadsheets: financial models, dashboards, data systems, and automation. Platform-agnostic methodology for Google Sheets, Excel, and LibreOffice.

## Quick Health Check

Score your spreadsheet /16:

| Signal | Healthy | Sick |
|---|---|---|
| Named ranges for all key inputs | ✅ Uses named ranges | ❌ Raw cell references everywhere |
| Inputs separated from calculations | ✅ Clear input section | ❌ Hardcoded values in formulas |
| No circular references | ✅ Clean dependency chain | ❌ Iterative calculation warnings |
| Documentation/comments exist | ✅ README sheet + cell notes | ❌ "What does this formula do?" |
| Error handling in formulas | ✅ IFERROR/IFNA wrapping | ❌ #REF! #N/A scattered everywhere |
| Consistent formatting | ✅ Style guide followed | ❌ Random fonts, colors, sizes |
| Version history/backup | ✅ Named versions + changelog | ❌ "Final_v3_REAL_final.xlsx" |
| Data validation on inputs | ✅ Dropdowns + range constraints | ❌ Free-text in structured fields |

**Score:** 0-4 🔴 rebuild | 5-8 🟡 refactor | 9-12 🟢 optimize | 13-16 🔵 production-grade

---

## Phase 1: Architecture & Planning

### Spreadsheet Strategy Brief

```yaml
spreadsheet_brief:
  name: "[Descriptive Name]"
  purpose: "[What decision does this support?]"
  owner: "[Who maintains this]"
  audience: "[Who uses this — technical level]"
  update_frequency: "[Real-time / Daily / Weekly / Monthly / Ad-hoc]"
  data_sources:
    - source: "[Where data comes from]"
      method: "[Manual / Import / API / IMPORTRANGE / Power Query]"
      refresh: "[How often]"
  outputs:
    - "[Dashboard / Report / Export / Decision support]"
  complexity_tier: "[Simple / Standard / Complex / Enterprise]"
  platform: "[Google Sheets / Excel / Both]"
  kill_criteria:
    - "If >50 users need simultaneous editing → move to database"
    - "If >100K rows → move to database or BI tool"
    - "If requires audit trail → move to proper system"
```

### Complexity Tier Guide

| Tier | Rows | Sheets | Users | Formulas | Example |
|---|---|---|---|---|---|
| Simple | <1K | 1-3 | 1-3 | Basic | Budget tracker, checklist |
| Standard | 1K-10K | 3-8 | 3-10 | Intermediate | Financial model, project tracker |
| Complex | 10K-50K | 8-15 | 10-30 | Advanced | Multi-dept dashboard, CRM |
| Enterprise | 50K+ | 15+ | 30+ | Expert | Data warehouse substitute (🚩 migrate) |

### When NOT to Use a Spreadsheet

| Scenario | Better Tool |
|---|---|
| >100K rows of data | Database (PostgreSQL, SQLite) |
| >10 concurrent editors | Web app or Airtable |
| Complex relational data (3+ entity types) | Database + app |
| Needs audit trail / compliance | Purpose-built system |
| Real-time data processing | ETL pipeline + BI tool |
| Version-controlled code logic | Actual code (Python, JS) |

**Rule:** Spreadsheets are prototyping tools that become production systems by accident. Know when to graduate.

---

## Phase 2: Sheet Architecture

### Recommended Structure

```
📊 Workbook
├── 📋 README          — Purpose, instructions, changelog
├── 📊 Dashboard       — Charts, KPIs, summary (output only)
├── ⚙️ Config          — Settings, parameters, dropdowns
├── 📥 Data_Input      — Raw data entry or imports
├── 🔧 Calculations    — All formulas and transformations
├── 📈 Analysis        — Pivot tables, scenarios, what-if
├── 📤 Output          — Formatted reports for export/print
└── 🗄️ Reference       — Lookup tables, constants, mappings
```

### 7 Architecture Rules

1. **One direction of flow** — Data flows left→right or top→bottom. Never circular.
2. **Inputs separate from calculations** — NEVER hardcode numbers in formulas. Use named ranges.
3. **One fact in one place** — If a value is used in 3 places, define it once and reference it.
4. **Color code by purpose** — Blue = input, Black = formula, Green = linked from other sheet, Red = warning.
5. **Freeze panes on every data sheet** — Header row and label columns always visible.
6. **Protect formula cells** — Lock everything except input cells. Prevent accidental overwrites.
7. **README sheet is mandatory** — Every workbook starts with purpose, instructions, and changelog.

### Naming Conventions

```
Sheets:    PascalCase — Dashboard, Raw_Data, Config
Named Ranges: SCREAMING_SNAKE — TAX_RATE, START_DATE, REVENUE_TARGET
Tabs:      Prefix with emoji or number for sort order — 01_Dashboard, 02_Config
Files:     YYYY-MM-DD_Description_vX.xlsx
```

### Color Coding Standard

| Color | Meaning | When to Use |
|---|---|---|
| 🔵 Light blue background | User input cell | Editable fields |
| ⬛ Black text | Formula/calculated | Auto-populated cells |
| 🟢 Green text | Linked from other sheet | Cross-sheet references |
| 🔴 Red text/background | Warning/error | Validation failures, negative values |
| 🟡 Yellow background | Assumption | Key assumptions that drive the model |
| ⬜ Grey background | Reference/locked | Constants, lookup tables |

---

## Phase 3: Formula Engineering

### Formula Complexity Levels

| Level | Techniques | Example |
|---|---|---|
| L1 Basic | SUM, AVERAGE, COUNT, IF, CONCATENATE | `=SUM(B2:B100)` |
| L2 Intermediate | VLOOKUP/XLOOKUP, SUMIFS, INDEX/MATCH, TEXT | `=XLOOKUP(A2,Ref!A:A,Ref!B:B)` |
| L3 Advanced | ARRAYFORMULA, QUERY, INDIRECT, nested IFs | `=QUERY(Data!A:F,"SELECT A,SUM(F) GROUP BY A")` |
| L4 Expert | LAMBDA, MAP/REDUCE, LET, dynamic arrays, MAKEARRAY | `=LET(data,A2:A100,filtered,FILTER(data,data>0),SORT(filtered))` |

### Essential Formula Patterns

#### Lookup — Always Prefer XLOOKUP/INDEX-MATCH Over VLOOKUP

```
❌ VLOOKUP (fragile — breaks when columns inserted):
=VLOOKUP(A2, Data!A:D, 4, FALSE)

✅ XLOOKUP (Excel 365 / Google Sheets):
=XLOOKUP(A2, Data!A:A, Data!D:D, "Not Found")

✅ INDEX/MATCH (universal — works everywhere):
=INDEX(Data!D:D, MATCH(A2, Data!A:A, 0))
```

#### Multi-Criteria Lookup

```
=XLOOKUP(1, (Data!A:A=B2)*(Data!B:B=C2), Data!D:D, "Not Found")

Or INDEX/MATCH array (Ctrl+Shift+Enter in older Excel):
=INDEX(Data!D:D, MATCH(1, (Data!A:A=B2)*(Data!B:B=C2), 0))
```

#### Conditional Aggregation

```
Single condition:
=SUMIF(Category, "Sales", Amount)

Multiple conditions:
=SUMIFS(Amount, Category, "Sales", Region, "US", Date, ">="&DATE(2025,1,1))

Count with conditions:
=COUNTIFS(Status, "Active", Score, ">80")

Average with conditions:
=AVERAGEIFS(Score, Department, "Engineering", Status, "Active")
```

#### Date Calculations

```
Working days between dates:
=NETWORKDAYS(Start, End, Holidays)

Add working days:
=WORKDAY(Start, 10, Holidays)

Month-end date:
=EOMONTH(A2, 0)

Quarter from date:
=ROUNDUP(MONTH(A2)/3, 0)

Fiscal year (Apr-Mar):
=IF(MONTH(A2)>=4, YEAR(A2), YEAR(A2)-1)
```

#### Text Manipulation

```
Extract domain from email:
=MID(A2, FIND("@",A2)+1, LEN(A2))

Proper case with exceptions:
=PROPER(SUBSTITUTE(LOWER(A2)," llc"," LLC"))

Clean messy data:
=TRIM(CLEAN(SUBSTITUTE(A2, CHAR(160), " ")))
```

#### Dynamic Arrays (Excel 365 / Google Sheets)

```
FILTER:
=FILTER(Data, Data[Status]="Active", Data[Amount]>1000)

SORT:
=SORT(FILTER(Data, Data[Region]="US"), 3, -1)

UNIQUE:
=UNIQUE(Data[Category])

SEQUENCE:
=SEQUENCE(12, 1, DATE(2025,1,1), 30)  — 12 monthly dates
```

#### Google Sheets QUERY (Power Feature)

```
Basic aggregation:
=QUERY(Data!A:F, "SELECT A, SUM(F) WHERE B='Active' GROUP BY A ORDER BY SUM(F) DESC LABEL SUM(F) 'Total Revenue'")

Date filtering:
=QUERY(Data!A:F, "SELECT A, B, F WHERE C >= date '"&TEXT(B1,"yyyy-MM-dd")&"' ORDER BY F DESC LIMIT 10")

Pivot-style:
=QUERY(Data!A:F, "SELECT A, SUM(F) GROUP BY A PIVOT B")
```

#### LET for Readable Complex Formulas

```
=LET(
  revenue, SUMIFS(Sales!D:D, Sales!A:A, A2),
  costs, SUMIFS(Costs!D:D, Costs!A:A, A2),
  margin, (revenue - costs) / revenue,
  IF(revenue=0, "No Data",
    IF(margin > 0.3, "✅ Healthy",
      IF(margin > 0.1, "⚠️ Watch", "🔴 Critical")))
)
```

#### LAMBDA (Custom Functions)

```
Named LAMBDA (define in Name Manager / named ranges):
FISCAL_QUARTER = LAMBDA(date, "FY"&IF(MONTH(date)>=4,YEAR(date),YEAR(date)-1)&" Q"&ROUNDUP(MOD(MONTH(date)+8,12)/3,0))

MAP with LAMBDA:
=MAP(A2:A100, LAMBDA(x, PROPER(TRIM(x))))
```

### 10 Formula Rules

1. **NEVER hardcode values** — Use named ranges or a Config sheet
2. **Wrap external lookups in IFERROR** — `=IFERROR(XLOOKUP(...), "Not Found")`
3. **Use LET for formulas >100 chars** — Readable, debuggable, faster
4. **Prefer XLOOKUP over VLOOKUP** — More flexible, no column counting
5. **One formula per cell** — Don't nest 5+ functions. Break into helper columns.
6. **Comment complex formulas** — Use cell notes or a documentation column
7. **Test with edge cases** — Empty cells, zeros, dates before 1900, text in number fields
8. **Avoid INDIRECT for performance** — It's volatile (recalculates every time)
9. **Use structured references in tables** — `=SUM(Table1[Amount])` not `=SUM(D:D)`
10. **Keep formulas auditable** — Someone else (or future you) must understand them

---

## Phase 4: Data Validation & Quality

### Input Validation Checklist

| Data Type | Validation | Implementation |
|---|---|---|
| Date | Date range | Data validation: between START and END |
| Currency | Number ≥ 0 | Data validation: decimal ≥ 0, format $#,##0.00 |
| Percentage | 0-100 or 0-1 | Data validation: decimal between 0 and 1 |
| Category | Dropdown list | Data validation: list from Reference sheet |
| Email | Contains @ | Custom: `=ISNUMBER(FIND("@",A2))` |
| Phone | Length check | Custom: `=AND(LEN(A2)>=10, LEN(A2)<=15)` |
| Required field | Not blank | Custom: `=LEN(TRIM(A2))>0` |
| ID/Code | Unique + format | Custom: `=AND(COUNTIF(A:A,A2)=1, LEN(A2)=8)` |

### Data Cleaning Pipeline

```
Step 1: Remove whitespace
=TRIM(CLEAN(A2))

Step 2: Standardize case
=PROPER(A2) or =UPPER(A2)

Step 3: Remove duplicates
Use Remove Duplicates tool or UNIQUE()

Step 4: Fix dates
=DATEVALUE(TEXT(A2,"YYYY-MM-DD"))

Step 5: Validate
=IF(AND(A2>0, A2<1000000, ISNUMBER(A2)), "✅", "❌ Check")
```

### Conditional Formatting Rules (Priority Order)

1. 🔴 **Errors** — Any cell with #REF!, #N/A, #VALUE! → Red background
2. 🟡 **Warnings** — Values outside expected range → Yellow background
3. 🟢 **Positive** — On-target metrics → Green text
4. 📊 **Data bars** — Numeric ranges → Proportional bars
5. 🎯 **Icons** — Status indicators → Traffic light icon sets

---

## Phase 5: Financial Modeling

### Model Architecture

```
📊 Financial Model
├── 📋 Cover          — Model name, version, date, author
├── ⚙️ Assumptions    — ALL inputs here (blue cells), scenarios
├── 📊 Revenue        — Revenue build-up by product/segment
├── 📊 COGS           — Cost of goods/services
├── 📊 OpEx           — Operating expenses by category
├── 📊 P&L            — Income statement (auto-calculated)
├── 📊 Balance_Sheet  — Assets, liabilities, equity
├── 📊 Cash_Flow      — Operating, investing, financing
├── 📈 DCF            — Discounted cash flow valuation
├── 📈 Scenarios      — Bull/Base/Bear cases
├── 📊 KPIs           — Key metrics dashboard
└── 📊 Charts         — Visualizations
```

### Revenue Model Patterns

```yaml
saas_revenue:
  mrr_start: "=PREVIOUS_MONTH_MRR"
  new_mrr: "=NEW_CUSTOMERS * ARPU"
  expansion_mrr: "=EXISTING * EXPANSION_RATE / 12"
  contraction_mrr: "=EXISTING * CONTRACTION_RATE / 12"
  churn_mrr: "=EXISTING * CHURN_RATE / 12"
  mrr_end: "=MRR_START + NEW + EXPANSION - CONTRACTION - CHURN"
  arr: "=MRR_END * 12"

unit_economics:
  cac: "=TOTAL_SALES_MARKETING / NEW_CUSTOMERS"
  ltv: "=ARPU / MONTHLY_CHURN_RATE"
  ltv_cac_ratio: "=LTV / CAC  # Target: >3.0"
  cac_payback_months: "=CAC / ARPU  # Target: <12"
```

### Scenario Analysis Template

```
=SWITCH(SCENARIO_SELECTOR,
  "Bull", Assumptions!B2 * 1.3,
  "Base", Assumptions!B2,
  "Bear", Assumptions!B2 * 0.7,
  Assumptions!B2)

Or with CHOOSE:
=CHOOSE(SCENARIO_INDEX, BEAR_VALUE, BASE_VALUE, BULL_VALUE)
```

### Sensitivity Analysis (Data Table)

```
Two-variable data table:
- Row input: Growth Rate (10%, 15%, 20%, 25%, 30%)
- Column input: Churn Rate (2%, 3%, 5%, 7%, 10%)
- Output cell: NPV or IRR
- Select range → Data → What-If Analysis → Data Table
```

### Common Financial Formulas

```
NPV: =NPV(DISCOUNT_RATE, CF1:CF10) + INITIAL_INVESTMENT
IRR: =IRR(CF_RANGE, guess)
XIRR: =XIRR(CF_VALUES, CF_DATES)  — irregular cash flows
PMT: =PMT(RATE/12, NPER*12, -PV)  — loan payment
Compound growth: =FV * (1 + RATE)^YEARS
CAGR: =(END_VALUE/START_VALUE)^(1/YEARS) - 1
Break-even units: =FIXED_COSTS / (PRICE - VARIABLE_COST)
```

---

## Phase 6: Dashboard Design

### Dashboard Layout

```
┌─────────────────────────────────────────────────┐
│  📊 Dashboard Title              Period: [Dropdown] │
│  Last Updated: [Auto]            Filter: [Dropdown] │
├──────────┬──────────┬──────────┬──────────────────┤
│  KPI 1   │  KPI 2   │  KPI 3   │  KPI 4           │
│  $1.2M   │  45%     │  128     │  $47             │
│  ▲ 12%   │  ▼ -3%   │  ▲ 8%   │  ● Flat          │
├──────────┴──────────┴──────────┴──────────────────┤
│                                                     │
│  [Primary Chart — Revenue Trend]                   │
│                                                     │
├─────────────────────┬───────────────────────────────┤
│  [Secondary Chart]  │  [Table / Top Items]          │
│  [Category Split]   │  [Ranked List]                │
└─────────────────────┴───────────────────────────────┘
```

### KPI Card Formula Pattern

```
Current value:  =SUMIFS(Data!E:E, Data!A:A, ">="&PERIOD_START, Data!A:A, "<="&PERIOD_END)
Previous value: =SUMIFS(Data!E:E, Data!A:A, ">="&PREV_START, Data!A:A, "<="&PREV_END)
Change %:       =(CURRENT - PREVIOUS) / ABS(PREVIOUS)
Indicator:      =IF(CHANGE>0.05, "▲", IF(CHANGE<-0.05, "▼", "●"))
Display:        =INDICATOR & " " & TEXT(ABS(CHANGE), "0.0%")
```

### Chart Selection Guide

| Data Pattern | Best Chart | Avoid |
|---|---|---|
| Trend over time | Line chart | Pie chart |
| Part of whole | Stacked bar or donut | 3D pie |
| Comparison | Horizontal bar | Radar chart |
| Distribution | Histogram | Line chart |
| Relationship | Scatter plot | Bar chart |
| KPI vs target | Bullet chart or gauge | Complex chart |
| Geographic | Heat map or filled map | Bar chart |

### 7 Chart Rules

1. **Title = Insight**, not description. "Revenue grew 23% in Q3" not "Q3 Revenue Chart"
2. **Start Y-axis at zero** for bar charts. Line charts can truncate with clear labeling.
3. **Max 5-7 data series** per chart. Use "Other" category for the rest.
4. **Remove chartjunk** — No 3D effects, gradient fills, excessive gridlines.
5. **Use consistent colors** — Same category = same color across all charts.
6. **Label directly** on chart where possible. Minimize legend lookups.
7. **Sort meaningfully** — By value (largest→smallest) or chronologically. Never alphabetically unless it's the only logical order.

### Interactive Dashboard Controls

```
Filter by dropdown:
1. Config sheet: Data validation dropdown for Region, Period, Category
2. Dashboard formulas use dropdown value:
   =SUMIFS(Data!E:E, Data!C:C, CONFIG_REGION, Data!A:A, ">="&CONFIG_START)

Sparklines (in-cell mini charts):
=SPARKLINE(B2:M2, {"charttype","line"; "color","#2563eb"; "linewidth",2})
```

---

## Phase 7: Data Import & Integration

### Import Method Selection

| Source | Method | Refresh |
|---|---|---|
| CSV/Excel file | Manual import / Power Query | Manual |
| Google Sheets (other) | IMPORTRANGE | Auto (varies) |
| Web page table | IMPORTHTML / Power Query | Auto / manual |
| API / JSON | IMPORTDATA / Apps Script / Power Query | Scheduled |
| Database | Power Query / ODBC | Scheduled |
| Another sheet (same workbook) | Direct reference | Real-time |

### Google Sheets Import Functions

```
From another spreadsheet:
=IMPORTRANGE("spreadsheet_url", "Sheet1!A1:D100")

From web page (table):
=IMPORTHTML("url", "table", 1)

From CSV:
=IMPORTDATA("csv_url")

From XML/RSS:
=IMPORTXML("url", "//item/title")
```

### Excel Power Query Patterns

```
1. Data → Get Data → From [Source]
2. Transform in Power Query Editor
3. Close & Load (to table or connection only)

Essential transforms:
- Remove columns → Right-click header → Remove
- Filter rows → Click filter arrow
- Split column → Transform → Split Column
- Unpivot → Select ID columns → Unpivot Other Columns
- Merge queries → Home → Merge (= VLOOKUP but better)
- Append queries → Home → Append (= UNION)
```

### IMPORTRANGE Best Practices

```
Rules:
1. Authorize on first use (one-time popup)
2. Use named ranges in source spreadsheet
3. Wrap in IFERROR for graceful failures
4. Minimize imported range — don't import entire sheets
5. Cache results if auto-refresh causes slowness

Pattern:
=IFERROR(
  IMPORTRANGE(SOURCE_URL, "Data!A1:D"&SOURCE_ROW_COUNT),
  "⚠️ Connection failed — check source spreadsheet access"
)
```

---

## Phase 8: Automation & Scripts

### Google Apps Script Essentials

```javascript
// Auto-populate timestamp on edit
function onEdit(e) {
  const sheet = e.source.getActiveSheet();
  if (sheet.getName() === "Data" && e.range.getColumn() >= 2) {
    sheet.getRange(e.range.getRow(), 1).setValue(new Date());
  }
}

// Email report on schedule (set up trigger)
function sendWeeklyReport() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const dashboard = ss.getSheetByName("Dashboard");
  const kpi1 = dashboard.getRange("B2").getDisplayValue();
  const kpi2 = dashboard.getRange("C2").getDisplayValue();
  
  MailApp.sendEmail({
    to: "team@company.com",
    subject: `Weekly Report — ${Utilities.formatDate(new Date(), "GMT", "MMM dd")}`,
    htmlBody: `<h2>Weekly KPIs</h2><p>Revenue: ${kpi1}</p><p>Growth: ${kpi2}</p>`
  });
}

// Auto-archive rows older than 90 days
function archiveOldRows() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const data = ss.getSheetByName("Data");
  const archive = ss.getSheetByName("Archive");
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - 90);
  
  const rows = data.getDataRange().getValues();
  for (let i = rows.length - 1; i >= 1; i--) {
    if (rows[i][0] < cutoff) {
      archive.appendRow(rows[i]);
      data.deleteRow(i + 1);
    }
  }
}
```

### Excel VBA Essentials

```vba
' Auto-format new entries
Private Sub Worksheet_Change(ByVal Target As Range)
    If Not Intersect(Target, Range("A:A")) Is Nothing Then
        Application.EnableEvents = False
        Target.Offset(0, 5).Value = Now
        Application.EnableEvents = True
    End If
End Sub

' Refresh all Power Query connections
Sub RefreshAllData()
    ThisWorkbook.RefreshAll
    MsgBox "All data refreshed at " & Now
End Sub
```

### Automation Decision Guide

| Task | Google Sheets | Excel |
|---|---|---|
| On-edit timestamp | Apps Script onEdit | VBA Worksheet_Change |
| Scheduled email | Apps Script + trigger | Power Automate |
| Data refresh | Apps Script + trigger | Power Query + schedule |
| PDF export | Apps Script | VBA + SaveAs |
| Cross-system sync | Apps Script + API | Power Automate / VBA |
| Custom functions | Apps Script CUSTOM_FUNCTION | VBA UDF or LAMBDA |

---

## Phase 9: Performance Optimization

### Performance Killers (Ranked)

| Issue | Impact | Fix |
|---|---|---|
| INDIRECT/OFFSET (volatile) | 🔴 Critical | Replace with INDEX/XLOOKUP |
| Whole-column references (A:A) | 🔴 Critical | Use bounded ranges (A2:A1000) |
| ARRAYFORMULA on huge ranges | 🟡 High | Limit range or use QUERY |
| Excessive conditional formatting | 🟡 High | Reduce rules, use bounded ranges |
| Too many IMPORTRANGE | 🟡 High | Consolidate, cache locally |
| Unused sheets with formulas | 🟢 Medium | Delete or clear unused sheets |
| Complex nested IFs | 🟢 Medium | Replace with SWITCH/IFS/XLOOKUP |
| Heavy formatting (images, shapes) | 🟢 Medium | Minimize decorative elements |

### Google Sheets Performance Rules

1. Keep workbook under 5M cells (ideal: <500K)
2. Limit IMPORTRANGE to <10 per workbook
3. Use QUERY instead of multiple SUMIFS when possible
4. Put ARRAYFORMULA results on a dedicated calc sheet
5. Avoid NOW()/TODAY() in frequently-recalculated areas

### Excel Performance Rules

1. Use tables (Ctrl+T) for structured data — better performance than raw ranges
2. Power Query > formulas for data transformation
3. XLOOKUP > VLOOKUP > INDEX/MATCH for speed
4. Turn off auto-calculation during bulk edits: `Application.Calculation = xlManual`
5. Use Power Pivot for >100K rows instead of formulas

---

## Phase 10: Collaboration & Governance

### Access Control Strategy

| Role | Permissions | Implementation |
|---|---|---|
| Owner | Full control | Original creator |
| Editor | Edit data, not structure | Share with edit, protect structure sheets |
| Analyst | Edit inputs, view outputs | Protect all except input cells |
| Viewer | View only | Share as viewer |
| Commenter | View + comment | Share as commenter |

### Sheet Protection Pattern

```
1. Protect entire workbook structure (prevent sheet add/delete/rename)
2. Protect each sheet
3. UNLOCK only input cells (blue-coded)
4. Set password for admin overrides
5. Document which cells are editable in README
```

### Version Control

```
Naming: YYYY-MM-DD_ModelName_vX.Y
  X = major change (new section, restructure)
  Y = minor change (formula fix, data update)

Changelog (on README sheet):
| Date | Version | Author | Change |
|------|---------|--------|--------|
| 2025-03-15 | 2.1 | Jane | Added Q2 actuals |
| 2025-03-01 | 2.0 | John | Restructured revenue model |
```

### Collaboration Rules

1. **Never edit someone else's model without telling them**
2. **Use named versions** before major changes (Google Sheets: File → Version history → Name current version)
3. **Comment on cells** — don't explain in chat, explain in the sheet
4. **One editor at a time** for complex formula areas — use "editing" flag cell
5. **Weekly review** — Check for broken references, stale data, unused sheets

---

## Phase 11: Common Templates

### Budget Tracker Template

```
Columns: Month | Category | Subcategory | Budgeted | Actual | Variance | % Variance
KPIs: Total Budget | Total Spent | Remaining | Burn Rate | Projected Year-End
Charts: Budget vs Actual (bar), Spend by Category (donut), Monthly Trend (line)
Formulas:
  Variance: =Actual - Budgeted
  % Variance: =IF(Budgeted=0, "", (Actual-Budgeted)/ABS(Budgeted))
  Burn Rate: =SUMIFS(Actual, Month, "<="&TODAY()) / (MONTH(TODAY()) * Total_Budget / 12)
```

### Project Tracker Template

```
Columns: Task | Owner | Status | Priority | Start | Due | Days Left | % Complete | Notes
Status: 🔴 Blocked | 🟡 In Progress | 🟢 Complete | ⚪ Not Started
Formulas:
  Days Left: =IF(Status="🟢 Complete", "✅", MAX(0, Due-TODAY()))
  Overdue flag: =IF(AND(Status<>"🟢 Complete", Due<TODAY()), "⚠️ OVERDUE", "")
  Completion %: =COUNTIF(Status, "🟢 Complete") / COUNTA(Status)
Dashboard: Gantt-style with conditional formatting date bars
```

### Sales Pipeline Template

```
Columns: Deal | Company | Stage | Amount | Probability | Weighted | Owner | Close Date | Days in Stage | Next Action
Stages: Prospect (10%) | Qualified (25%) | Proposal (50%) | Negotiation (75%) | Closed Won (100%) | Lost (0%)
Formulas:
  Weighted: =Amount * Probability
  Pipeline: =SUMIFS(Weighted, Stage, "<>"&"Lost", Stage, "<>"&"Closed Won")
  Velocity: =AVERAGE(Days_to_Close_for_Won_Deals)
Dashboard: Pipeline by stage (funnel), Forecast vs quota, Win rate trend
```

### OKR Tracker Template

```
Columns: Objective | Key Result | Metric | Start | Current | Target | Score | Status
Score: =MIN(1, (Current - Start) / (Target - Start))
Status: =IF(Score>=0.7, "🟢", IF(Score>=0.4, "🟡", "🔴"))
Overall: =AVERAGE(Score) across all KRs per Objective
```

---

## Phase 12: Quality & Maintenance

### Spreadsheet Quality Rubric (0-100)

| Dimension | Weight | Scoring |
|---|---|---|
| Architecture | 15% | Clear sheet structure, data flow direction, README |
| Formula Quality | 20% | Named ranges, error handling, no hardcoding |
| Data Validation | 15% | Input constraints, dropdowns, type checking |
| Visual Design | 10% | Consistent formatting, color coding, readability |
| Documentation | 15% | Cell notes, README, changelog, instructions |
| Performance | 10% | No volatile functions, bounded ranges, fast recalc |
| Error Handling | 10% | IFERROR wrappers, validation checks, no broken refs |
| Maintainability | 5% | Protected structure, clear ownership, versioned |

### Monthly Maintenance Checklist

- [ ] Check for #REF! and #N/A errors across all sheets
- [ ] Verify data source connections are refreshing
- [ ] Review and update assumptions (Config sheet)
- [ ] Remove unused sheets and named ranges
- [ ] Check file size — if growing, archive old data
- [ ] Test all dropdowns and validation rules
- [ ] Update README with any changes made
- [ ] Create named version snapshot

### 10 Spreadsheet Killers

| Mistake | Impact | Fix |
|---|---|---|
| Hardcoded numbers in formulas | Can't audit or update | Named ranges + Config sheet |
| No error handling | #N/A cascades break everything | IFERROR on all lookups |
| Whole-column references | Slow, crashes on large data | Bounded ranges |
| Circular references | Unpredictable results | Redesign calculation flow |
| No documentation | "What does this formula do?" | README + cell notes |
| No data validation | Garbage in = garbage out | Dropdowns + constraints |
| One mega-sheet | Unmaintainable, slow | Split by function |
| No backup/versions | One mistake = lost work | Named versions + exports |
| Copy-paste instead of formulas | Stale data, inconsistencies | Use references/IMPORTRANGE |
| Manual processes that should be automated | Error-prone, time-wasting | Scripts or scheduled refreshes |

---

## Edge Cases

### Migrating Excel ↔ Google Sheets

- **XLOOKUP** works in both (Excel 365 + Google Sheets)
- **QUERY** is Google Sheets only — replace with Power Query in Excel
- **ARRAYFORMULA** is Google Sheets — Excel uses Ctrl+Shift+Enter or dynamic arrays
- **Apps Script** → no Excel equivalent. Use VBA or Power Automate.
- **Power Query / Power Pivot** → no Google Sheets equivalent. Use QUERY or BigQuery connector.
- Test all formulas after migration. Named ranges may break.

### Multi-Currency Spreadsheets

```
=Amount * XLOOKUP(Currency, FX_Rates!A:A, FX_Rates!B:B)
Or with GOOGLEFINANCE:
=Amount * GOOGLEFINANCE("CURRENCY:GBPUSD")
```

### Large Dataset Workarounds (>100K rows)

1. Split data across multiple sheets by time period
2. Use pivot tables / QUERY instead of row-level formulas
3. Import summarized data, not raw transactions
4. Consider BigQuery + Connected Sheets (Google) or Power Pivot (Excel)
5. If you need >500K rows, graduate to a database

---

## Natural Language Commands

When working with spreadsheets, you can ask:
- "Audit this spreadsheet for quality issues"
- "Design a financial model for [business type]"
- "Create a dashboard layout for [metrics]"
- "Write the formulas for [calculation]"
- "Optimize this spreadsheet for performance"
- "Build a data validation system for [input type]"
- "Create an Apps Script to [automate task]"
- "Design a template for [use case]"
- "Review this formula and suggest improvements"
- "Help me migrate this from Excel to Google Sheets"
- "Set up a scenario analysis for [model]"
- "Build a KPI tracker for [department]"

---

## ⚡ Level Up — AfrexAI Context Packs

This skill covers spreadsheet engineering methodology. For **industry-specific financial models, dashboards, and templates**:

- 💰 [**SaaS Context Pack**](https://afrexai-cto.github.io/context-packs/) — MRR/ARR models, SaaS metrics dashboards, cohort analysis templates
- 🏦 [**Fintech Context Pack**](https://afrexai-cto.github.io/context-packs/) — Financial modeling, risk calculators, compliance trackers
- 🏭 [**Manufacturing Context Pack**](https://afrexai-cto.github.io/context-packs/) — Production trackers, inventory models, cost analysis
- 🏗️ [**Construction Context Pack**](https://afrexai-cto.github.io/context-packs/) — Project budgets, bid calculators, resource planning

**$47 per pack** — Complete AI agent context for your industry.

Browse all packs: [**AfrexAI Storefront →**](https://afrexai-cto.github.io/context-packs/)

---

## 🔗 More Free Skills by AfrexAI

- [afrexai-data-storytelling](https://clawhub.com/afrexai-cto/afrexai-data-storytelling) — Data visualization & dashboard design methodology
- [afrexai-personal-finance](https://clawhub.com/afrexai-cto/afrexai-personal-finance) — Complete personal finance operating system
- [afrexai-product-analytics](https://clawhub.com/afrexai-cto/afrexai-product-analytics) — Product metrics & analytics engineering
- [afrexai-fpa-engine](https://clawhub.com/afrexai-cto/afrexai-fpa-engine) — Financial planning & analysis
- [afrexai-automation-strategy](https://clawhub.com/afrexai-cto/afrexai-automation-strategy) — Workflow automation methodology

---

*Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — AI agents that compound capital and code.*
