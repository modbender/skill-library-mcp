#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="$1"

cd "$WORKSPACE"
git init -q
git config user.email "bench@agentbench.local"
git config user.name "AgentBench"

# ── import.py ────────────────────────────────────────────────────────────────
cat > import.py << 'EOF'
"""Import JSON data files into SQLite database."""
import json
import sqlite3
import os
import glob

def import_data(data_dir, db_path='records.db'):
    """Import all JSON files from data_dir into SQLite."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY,
            name TEXT,
            value REAL,
            category TEXT,
            source_file TEXT
        )
    ''')

    json_files = sorted(glob.glob(os.path.join(data_dir, '*.json')))
    print(f"Found {len(json_files)} JSON files to import")

    # BUG: Single try/except around everything — one bad file kills the whole import
    try:
        for filepath in json_files:
            filename = os.path.basename(filepath)
            print(f"Importing {filename}...")

            with open(filepath, 'r') as f:
                data = json.load(f)

            for record in data['records']:
                cursor.execute(
                    'INSERT INTO records (name, value, category, source_file) VALUES (?, ?, ?, ?)',
                    (record['name'], record['value'], record['category'], filename)
                )

        conn.commit()
        print("Import complete!")
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    import_data('data')
EOF

# ── data directory ───────────────────────────────────────────────────────────
mkdir -p data

# ── file_001.json — valid ────────────────────────────────────────────────────
cat > data/file_001.json << 'EOF'
{
  "records": [
    {"name": "Item A1", "value": 42.50, "category": "Electronics"},
    {"name": "Item A2", "value": 18.75, "category": "Books"},
    {"name": "Item A3", "value": 125.00, "category": "Electronics"},
    {"name": "Item A4", "value": 9.99, "category": "Books"},
    {"name": "Item A5", "value": 67.30, "category": "Clothing"}
  ]
}
EOF

# ── file_002.json — valid ────────────────────────────────────────────────────
cat > data/file_002.json << 'EOF'
{
  "records": [
    {"name": "Item B1", "value": 34.99, "category": "Kitchen"},
    {"name": "Item B2", "value": 245.00, "category": "Electronics"},
    {"name": "Item B3", "value": 12.50, "category": "Books"},
    {"name": "Item B4", "value": 89.95, "category": "Sports"},
    {"name": "Item B5", "value": 55.00, "category": "Kitchen"},
    {"name": "Item B6", "value": 7.25, "category": "Garden"}
  ]
}
EOF

# ── file_003.json — valid ────────────────────────────────────────────────────
cat > data/file_003.json << 'EOF'
{
  "records": [
    {"name": "Item C1", "value": 199.99, "category": "Electronics"},
    {"name": "Item C2", "value": 14.50, "category": "Books"},
    {"name": "Item C3", "value": 39.99, "category": "Clothing"},
    {"name": "Item C4", "value": 72.00, "category": "Sports"},
    {"name": "Item C5", "value": 28.75, "category": "Garden"},
    {"name": "Item C6", "value": 155.00, "category": "Electronics"},
    {"name": "Item C7", "value": 8.99, "category": "Books"}
  ]
}
EOF

# ── file_004.json — valid ────────────────────────────────────────────────────
cat > data/file_004.json << 'EOF'
{
  "records": [
    {"name": "Item D1", "value": 450.00, "category": "Electronics"},
    {"name": "Item D2", "value": 22.99, "category": "Kitchen"},
    {"name": "Item D3", "value": 15.00, "category": "Books"},
    {"name": "Item D4", "value": 63.50, "category": "Clothing"},
    {"name": "Item D5", "value": 110.00, "category": "Sports"}
  ]
}
EOF

# ── file_005.json — valid ────────────────────────────────────────────────────
cat > data/file_005.json << 'EOF'
{
  "records": [
    {"name": "Item E1", "value": 33.00, "category": "Garden"},
    {"name": "Item E2", "value": 79.95, "category": "Kitchen"},
    {"name": "Item E3", "value": 19.99, "category": "Books"},
    {"name": "Item E4", "value": 299.00, "category": "Electronics"},
    {"name": "Item E5", "value": 45.50, "category": "Clothing"},
    {"name": "Item E6", "value": 12.00, "category": "Garden"},
    {"name": "Item E7", "value": 88.75, "category": "Sports"},
    {"name": "Item E8", "value": 6.99, "category": "Books"}
  ]
}
EOF

# ── file_006.json — valid ────────────────────────────────────────────────────
cat > data/file_006.json << 'EOF'
{
  "records": [
    {"name": "Item F1", "value": 175.00, "category": "Electronics"},
    {"name": "Item F2", "value": 27.50, "category": "Kitchen"},
    {"name": "Item F3", "value": 41.99, "category": "Clothing"},
    {"name": "Item F4", "value": 95.00, "category": "Sports"},
    {"name": "Item F5", "value": 16.75, "category": "Garden"}
  ]
}
EOF

# ── file_007.json — valid ────────────────────────────────────────────────────
cat > data/file_007.json << 'EOF'
{
  "records": [
    {"name": "Item G1", "value": 59.99, "category": "Kitchen"},
    {"name": "Item G2", "value": 135.00, "category": "Electronics"},
    {"name": "Item G3", "value": 23.50, "category": "Books"},
    {"name": "Item G4", "value": 48.00, "category": "Clothing"},
    {"name": "Item G5", "value": 82.25, "category": "Sports"},
    {"name": "Item G6", "value": 11.99, "category": "Garden"}
  ]
}
EOF

# ── file_008.json — TRUNCATED (invalid JSON, cuts off mid-object) ────────────
cat > data/file_008.json << 'EOF'
{
  "records": [
    {"name": "Item H1", "value": 55.00, "category": "Sports"},
    {"name": "Item H2", "value": 33.25, "cate
EOF

# ── file_009.json — ENCODING ERROR (contains invalid UTF-8 byte \xff) ────────
printf '{\n  "records": [\n    {"name": "Item I1\xff", "value": 29.99, "category": "Garden"}\n  ]\n}' > data/file_009.json

# ── file_010.json — WRONG SCHEMA (uses "items" instead of "records") ─────────
cat > data/file_010.json << 'EOF'
{
  "items": [
    {"name": "Item J1", "value": 88.00, "category": "Tools"},
    {"name": "Item J2", "value": 15.50, "category": "Kitchen"}
  ]
}
EOF

# ── Initial commit ───────────────────────────────────────────────────────────
git add -A
git commit -q -m "initial: add data import script with JSON files"
