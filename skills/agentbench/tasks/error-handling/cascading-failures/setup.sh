#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="$1"

cd "$WORKSPACE"
git init -q
git config user.email "bench@agentbench.local"
git config user.name "AgentBench"

# ── data/input.csv (100 rows, ~10 with empty amounts) ────────────────────────
mkdir -p data

python3 - << 'PYGEN'
import csv
import random

random.seed(42)

first_names = [
    "Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Hank",
    "Irene", "Jack", "Karen", "Leo", "Mona", "Nick", "Olivia", "Paul",
    "Quinn", "Rita", "Steve", "Tina", "Uma", "Victor", "Wendy", "Xander",
    "Yolanda", "Zach"
]
last_names = [
    "Johnson", "Smith", "White", "Brown", "Davis", "Miller", "Wilson",
    "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "Harris", "Martin",
    "Garcia", "Clark", "Lewis", "Walker", "Hall", "Allen", "Young", "King",
    "Wright", "Lopez", "Hill", "Scott"
]
categories = ["Electronics", "Books", "Clothing", "Food", "Sports", "Home", "Garden", "Toys"]

# Rows (1-indexed) that should have empty amounts
empty_amount_rows = {8, 17, 25, 34, 42, 51, 63, 72, 85, 94}

rows = []
for i in range(1, 101):
    first = first_names[i % len(first_names)]
    last = last_names[i % len(last_names)]
    name = f"{first} {last}"

    if i in empty_amount_rows:
        amount = ""
    else:
        amount = f"{random.uniform(10, 500):.2f}"

    category = categories[i % len(categories)]
    day = (i % 28) + 1
    month = ((i - 1) // 28) % 12 + 1
    date = f"2025-{month:02d}-{day:02d}"

    rows.append({
        "id": str(i),
        "name": name,
        "amount": amount,
        "category": category,
        "date": date
    })

with open("data/input.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "amount", "category", "date"])
    writer.writeheader()
    writer.writerows(rows)
PYGEN

# ── ingest.py ─────────────────────────────────────────────────────────────────
cat > ingest.py << 'EOF'
"""Read CSV input and yield rows as dictionaries."""
import csv

def ingest(filepath):
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row
EOF

# ── validate.py ───────────────────────────────────────────────────────────────
cat > validate.py << 'EOF'
"""Validate data rows."""

def validate_row(row):
    """Validate a single row. Returns validated row with typed fields."""
    return {
        'id': int(row['id']),
        'name': row['name'].strip(),
        'amount': float(row['amount']),  # BUG: crashes on empty/None values
        'category': row['category'].strip(),
        'date': row['date'].strip()
    }
EOF

# ── transform.py ──────────────────────────────────────────────────────────────
cat > transform.py << 'EOF'
"""Transform and enrich data rows."""
from validate import validate_row

def transform_row(row):
    """Validate and transform a single row."""
    try:
        validated = validate_row(row)
    except (ValueError, TypeError):
        # Silently drop rows that fail validation
        return None

    # Add computed fields
    validated['amount_category'] = (
        'high' if validated['amount'] > 200
        else 'medium' if validated['amount'] > 50
        else 'low'
    )
    return validated

def transform_all(rows):
    """Transform all rows, silently skipping failures."""
    results = []
    for row in rows:
        transformed = transform_row(row)
        if transformed is not None:
            results.append(transformed)
    return results
EOF

# ── export.py ─────────────────────────────────────────────────────────────────
cat > export.py << 'EOF'
"""Export processed data to CSV."""
import csv

def export(data, filepath):
    if not data:
        return
    fieldnames = data[0].keys()
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Exported {len(data)} records to {filepath}")
EOF

# ── pipeline.py ───────────────────────────────────────────────────────────────
cat > pipeline.py << 'EOF'
"""Main pipeline: ingest -> transform -> export."""
from ingest import ingest
from transform import transform_all
from export import export

def run():
    print("Starting pipeline...")
    rows = list(ingest('data/input.csv'))
    print(f"Ingested {len(rows)} records")

    transformed = transform_all(rows)
    print(f"Transformed {len(transformed)} records")

    export(transformed, 'output.csv')
    print("Pipeline complete.")

if __name__ == '__main__':
    run()
EOF

# ── Initial commit ────────────────────────────────────────────────────────────
git add -A
git commit -q -m "initial: add data pipeline with CSV processing"
