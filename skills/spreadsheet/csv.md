# CSV Handling — Spreadsheet Skill

## Reading

```python
import pandas as pd

df = pd.read_csv('file.csv',
    encoding='utf-8',
    sep=',',               # or ';' for European
    parse_dates=['date'],
    nrows=1000             # limit for preview
)
```

## Writing

```python
df.to_csv('output.csv', index=False, encoding='utf-8')
```

## Common Operations

```python
# Filter
filtered = df[df['amount'] > 100]
filtered = df[df['category'].isin(['food', 'transport'])]

# Aggregate
summary = df.groupby('category')['amount'].agg(['sum', 'mean', 'count'])

# Join
merged = pd.merge(df1, df2, on='id', how='left')

# Detect issues
df.isnull().sum()      # Nulls per column
df[df.duplicated()]    # Duplicate rows
```

## Large Files

```python
# Chunked processing
for chunk in pd.read_csv('large.csv', chunksize=10000):
    process(chunk)
```

## Traps

- **Encoding** — Default UTF-8; check for BOM (`utf-8-sig`)
- **Delimiter** — European CSVs often use `;`
- **Decimal** — US: `.`, Europe: `,` — affects number parsing
- **Newlines in cells** — Quote all fields when writing
- **Large context** — Never load >10MB into LLM; summarize first
