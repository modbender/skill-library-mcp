#!/usr/bin/env python3
"""Merge review JSON arrays from sub-agent outputs into the main skills.json catalog."""

import json
import sys
import re
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).parent.parent
CATALOG_PATH = PROJECT_DIR / "data" / "skills.json"

def extract_json_array(text):
    """Extract a JSON array from text that may contain other content."""
    # Try to find JSON array in the text
    # Look for the outermost [ ... ]
    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == '[' and start is None:
            start = i
            depth = 1
        elif ch == '[' and start is not None:
            depth += 1
        elif ch == ']' and start is not None:
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i+1])
                except json.JSONDecodeError:
                    start = None
    return None

def merge_reviews(review_files):
    """Merge reviews from multiple files into the catalog."""
    # Load existing catalog
    with open(CATALOG_PATH) as f:
        catalog = json.load(f)
    
    existing = {s['name'] for s in catalog['skills']}
    new_skills = []
    
    for filepath in review_files:
        print(f"Processing {filepath}...")
        with open(filepath) as f:
            text = f.read()
        
        reviews = extract_json_array(text)
        if reviews is None:
            print(f"  WARNING: Could not extract JSON array from {filepath}")
            continue
        
        for review in reviews:
            name = review.get('name', '')
            if name and name not in existing:
                new_skills.append(review)
                existing.add(name)
                print(f"  + {name} ({review.get('trustScore', '?')})")
            elif name in existing:
                print(f"  ~ {name} (already exists, skipping)")
    
    catalog['skills'].extend(new_skills)
    catalog['totalReviewed'] = len(catalog['skills'])
    catalog['lastUpdated'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    with open(CATALOG_PATH, 'w') as f:
        json.dump(catalog, f, indent=2)
    
    print(f"\nDone. Catalog now has {len(catalog['skills'])} skills (+{len(new_skills)} new).")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 merge-reviews.py <review-file1> [review-file2] ...")
        sys.exit(1)
    merge_reviews(sys.argv[1:])
