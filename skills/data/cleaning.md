# Cleaning & Transformation

## Missing Data

### Detection
- Count nulls per column — `df.isnull().sum()`
- Calculate missing percentage
- Check for patterns — MCAR, MAR, MNAR
- Look for implicit nulls (empty strings, "N/A", -999, 0 where inappropriate)

### Strategies
| Pattern | Strategy | When |
|---------|----------|------|
| Random missing | Drop rows | <5% missing, large dataset |
| Random missing | Mean/median impute | Numeric, no strong skew |
| Non-random | Flag + model | Important feature, can't drop |
| Entire column missing | Drop column | >50% missing, not critical |
| Time series gap | Interpolate | Regular intervals, smooth data |

**Never impute without documenting** — create a `_was_imputed` flag column.

## Duplicates

### Detection
- Exact duplicates: all columns match
- Fuzzy duplicates: key columns match (ID, email, name)
- Near-duplicates: slight variations (whitespace, case, typos)

### Resolution
```
1. Identify duplicate key (what makes a row unique?)
2. For exact: keep first, log dropped
3. For fuzzy: define matching rules
4. For near: clean first, then dedupe
5. Document dropped count and reason
```

## Type Conversion

### Common Issues
- **Dates as strings** — parse explicitly with format
- **Numbers as strings** — handle thousand separators, currency symbols
- **Booleans as integers** — 0/1 vs true/false
- **Categories as strings** — convert to categorical for efficiency
- **Mixed types in column** — coerce or split into columns

### Safe Conversion Pattern
```python
# Don't: df['date'] = pd.to_datetime(df['date'])
# Do: handle errors explicitly
df['date'] = pd.to_datetime(df['date'], errors='coerce')
invalid_count = df['date'].isna().sum()
# Log: "X rows had unparseable dates"
```

## Normalization

### Text
- Trim whitespace
- Normalize case (lower for comparison, title for display)
- Remove/replace special characters
- Normalize Unicode (NFD/NFC)
- Handle encoding issues

### Numeric
- Standard scaling: (x - mean) / std
- Min-max scaling: (x - min) / (max - min)
- Log transform: for skewed distributions
- Binning: continuous to categorical

### Dates
- Standardize timezone (UTC for storage, local for display)
- Consistent format (ISO 8601)
- Extract components if needed (year, month, day_of_week)

## Joins & Merges

### Pre-Join Checks
- Key uniqueness — one-to-one vs one-to-many vs many-to-many
- Key data types — must match exactly
- Key nulls — decide how to handle before join
- Expected row count after join

### Post-Join Validation
```
Before: left=1000, right=500
After: result=1200
Check: expected many-to-many? Or data issue?
```

## Transformation Documentation

Every transformation should log:
- Source column(s)
- Operation applied
- Parameters used
- Rows affected
- Before/after sample
