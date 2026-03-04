---
name: Pandas
slug: pandas
version: 1.0.1
homepage: https://clawic.com/skills/pandas
description: Analyze, transform, and clean DataFrames with efficient patterns for filtering, grouping, merging, and pivoting.
metadata: {"clawdbot":{"emoji":"🐼","requires":{"bins":["python3"]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, create `~/pandas/` and read `setup.md` for initialization. User preferences are stored in `~/pandas/memory.md` — users can view or edit this file anytime.

## When to Use

User needs to work with tabular data in Python. Agent handles DataFrame operations, data cleaning, aggregations, merges, pivots, and exports.

## Architecture

Memory lives in `~/pandas/`. See `memory-template.md` for structure.

```
~/pandas/
├── memory.md     # User preferences and common patterns
└── snippets/     # Saved code patterns (optional)
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |

## Core Rules

### 1. Use Vectorized Operations
- NEVER iterate with `for` loops over DataFrame rows
- Use `.apply()` only when vectorized alternatives don't exist
- Prefer `df['col'].str.method()` over `apply(lambda x: x.method())`

### 2. Chain Methods for Readability
```python
# Good: method chaining
result = (df
    .query('age > 30')
    .groupby('city')
    .agg({'salary': 'mean'})
    .reset_index())

# Bad: intermediate variables everywhere
filtered = df[df['age'] > 30]
grouped = filtered.groupby('city')
result = grouped.agg({'salary': 'mean'}).reset_index()
```

### 3. Handle Missing Data Explicitly
- Always check `df.isna().sum()` before analysis
- Choose strategy: `dropna()`, `fillna()`, or interpolation
- Document WHY missing values exist before removing them

### 4. Use Categorical for Repeated Strings
```python
# Memory savings for columns with few unique values
df['status'] = df['status'].astype('category')
df['country'] = df['country'].astype('category')
```

### 5. Merge with Validation
```python
# Always specify how and validate
result = pd.merge(
    df1, df2,
    on='id',
    how='left',
    validate='m:1'  # Many-to-one: catch unexpected duplicates
)
```

### 6. Prefer query() for Complex Filters
```python
# Readable
df.query('age > 30 and city == "NYC" and salary < 100000')

# Hard to read
df[(df['age'] > 30) & (df['city'] == 'NYC') & (df['salary'] < 100000)]
```

### 7. Set Index When Appropriate
```python
# Faster lookups, cleaner merges
df = df.set_index('user_id')
user_data = df.loc[12345]  # O(1) lookup
```

## Common Traps

- **SettingWithCopyWarning** → Use `.loc[]` for assignment: `df.loc[mask, 'col'] = value`
- **Slow loops** → Replace `iterrows()` with vectorized ops or `apply()`
- **Memory explosion** → Use `dtype` in `read_csv()`: `pd.read_csv(f, dtype={'id': 'int32'})`
- **Silent data loss** → Check shape before/after merge: `print(f"Before: {len(df1)}, After: {len(result)}")`
- **Index confusion** → Use `reset_index()` after `groupby()` to get clean DataFrame
- **Chained indexing** → `df['a']['b']` fails silently; use `df.loc[:, ['a', 'b']]`

## Security & Privacy

**Data storage:**
- User preferences stored in `~/pandas/memory.md`
- All DataFrame operations run locally
- No data is sent externally

**This skill does NOT:**
- Upload data to any service
- Access files outside `~/pandas/` and the working directory
- Modify source data files without explicit instruction

**User control:**
- View stored preferences: `cat ~/pandas/memory.md`
- Clear all data: `rm -rf ~/pandas/`

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `data-analysis` — general data analysis patterns
- `csv` — CSV file handling
- `sql` — database queries
- `excel-xlsx` — Excel file operations

## Feedback

- If useful: `clawhub star pandas`
- Stay updated: `clawhub sync`
