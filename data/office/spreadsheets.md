# Spreadsheets Deep Dive

## Formula Patterns

### Lookup Values
```
=VLOOKUP(lookup_value, table_range, column_index, FALSE)
=XLOOKUP(lookup_value, lookup_array, return_array)  [Excel 365+]
=INDEX(return_range, MATCH(lookup_value, lookup_range, 0))
```

### Conditional Calculations
```
=SUMIF(range, criteria, sum_range)
=SUMIFS(sum_range, criteria_range1, criteria1, criteria_range2, criteria2)
=COUNTIF(range, criteria)
=AVERAGEIF(range, criteria, average_range)
```

### Text Manipulation
```
=CONCATENATE(A1, " ", B1)  or  =A1 & " " & B1
=LEFT(text, num_chars)
=RIGHT(text, num_chars)
=TRIM(text)  -- removes extra spaces
=PROPER(text)  -- Title Case
```

### Date Functions
```
=TODAY()
=YEAR(date) / MONTH(date) / DAY(date)
=DATEDIF(start_date, end_date, "Y")  -- years between dates
=WORKDAY(start_date, num_days)  -- excludes weekends
```

---

## Pivot Tables

**When to use:** Summarizing large datasets by categories.

**Setup:**
1. Select data (including headers)
2. Insert → Pivot Table
3. Drag fields:
   - Rows = categories to group by
   - Columns = secondary grouping
   - Values = what to calculate (Sum, Count, Average)

**Refresh:** Right-click pivot → Refresh (data source changed)

**Calculated fields:** Add custom calculations within pivot.

---

## Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| #N/A | VLOOKUP can't find value | Check spelling, spaces, data type |
| #REF! | Referenced cell deleted | Update formula references |
| #VALUE! | Wrong data type | Check if text vs number |
| #DIV/0! | Dividing by zero | Add IF to check denominator |
| ##### | Column too narrow | Widen column |

---

## Data Cleaning

**Remove duplicates:** Data → Remove Duplicates
**Text to columns:** Data → Text to Columns (split by delimiter)
**Find & Replace:** Ctrl+H, use wildcards (* for any characters)
**Trim spaces:** `=TRIM(A1)` then paste values

---

## Keyboard Shortcuts (Excel)

| Action | Windows | Mac |
|--------|---------|-----|
| New row/column | Ctrl++ | Cmd++ |
| Delete row/column | Ctrl+- | Cmd+- |
| Fill down | Ctrl+D | Cmd+D |
| Absolute reference | F4 | Cmd+T |
| Go to formula cell | Ctrl+[ | Cmd+[ |
| Select to end | Ctrl+Shift+End | Cmd+Shift+End |
