# RLM Extraction Cache System

Builds structured JSON cache from RLM state for kirk-content-pipeline Step 3 (writing).

**New in v2:** Auto-generates full attribution map with tags, key_metrics, and source_context!

---

## Problem This Solves

**Before:** Writer relies on memory when writing → context label errors
**After:** Writer loads structured cache → writes from verified data with labels

**What auto-generates:**
- ✅ Source tags from PDF filenames ("GFHK - Memory.pdf" → tag: "GFHK")
- ✅ Topics with primary_source, key_metrics, source_context
- ✅ Extraction entries with full context labels (product_type, time_period, units, scope)

---

## Quick Start

### Single PDF (rlm-repl)

```bash
cd ~/.claude/skills/kirk-content-pipeline/scripts

# Auto-extracts from default rlm-repl state location
python3 build_extraction_cache.py \
    --output /path/to/draft-assets/rlm-extraction-cache.json
```

### Multiple PDFs (rlm-repl-multi)

```bash
cd ~/.claude/skills/kirk-content-pipeline/scripts

# Use --multi flag to load from rlm-repl-multi state
python3 build_extraction_cache.py \
    --multi \
    --output /path/to/draft-assets/rlm-extraction-cache.json
```

### With Manual Cross-Doc Synthesis Descriptions

```bash
# Add optional synthesis descriptions for cross-doc insights
python3 build_extraction_cache.py \
    --multi \
    --output /path/to/draft-assets/rlm-extraction-cache.json \
    --synthesis /path/to/cross-doc-synthesis.json
```

**Synthesis format** (optional, for complex multi-source threads):
```json
{
  "dual_squeeze_thesis": {
    "description": "Memory shortage (1Q26) + ABF substrate shortage (2H26) = compounding AI server bottleneck",
    "components": [
      {"topic": "Memory Pricing", "source": "gfhk_memory", "timeframe": "1Q26"},
      {"topic": "Abf Shortage", "source": "goldman_abf", "timeframe": "2H26-2028"}
    ]
  }
}
```

---

## Workflow Integration

### Step 1b: RLM Extraction (create state.pkl)

**Single PDF:**
```bash
cd ~/.claude/skills/rlm-repl/scripts

# Extract from PDF
python3 rlm_repl.py init "/path/to/pdf.pdf" --extract-images

# Run targeted grep queries
python3 rlm_repl.py exec -c "
results = grep('369|408|BOM|HGX|GB300', max_matches=20, window=500)
print(results)
"
```

**Multiple PDFs (cross-doc):**
```bash
cd ~/.claude/skills/rlm-repl-multi/scripts

# Initialize both PDFs
python3 rlm_repl.py init "/path/to/gfhk.pdf" --name gfhk --extract-images
python3 rlm_repl.py init "/path/to/goldman.pdf" --name goldman --extract-images

# Run grep across both
python3 rlm_repl.py exec -c "
results = grep_all('BOM|shortage|substrate', max_matches_per_context=20)
print(results)
"
```

### Step 1b.5: Build Cache (NEW STEP)

```bash
cd ~/.claude/skills/kirk-content-pipeline/scripts

# Build cache from RLM state
python3 build_extraction_cache.py \
    --output /Users/dydo/Documents/agent/ksvc-intern/content-pipeline/draft/2026-02-05-topic-assets/rlm-extraction-cache.json

# Check what was extracted
cat ../draft/2026-02-05-topic-assets/rlm-extraction-cache.json | jq '.extractions | length'
```

### Step 3: Write (load cache)

**In conversation when writing:**
```
Load cache: draft/2026-02-05-topic-assets/rlm-extraction-cache.json

For each claim:
1. Find entry in cache by metric/value
2. Use cache's product_type (not memory)
3. Use cache's time_period (not guessing)
4. Use cache's source_id for attribution
```

**Example:**
```python
cache = load_json('rlm-extraction-cache.json')

# Find entry for BOM data
entry = cache.find(values={'before': '369', 'after': '408'})

# Write using cache labels
write(f"""
{entry.product_type} BOM ({entry.time_period}):
${entry.values.before}k → ${entry.values.after}k
""")

# Result: "HGX B300 8-GPU server BOM (3Q25 → 1Q26E): $369k → $408k"
# Not: "GB300 rack BOM: $369k → $408k" (wrong product type)
```

---

## Cache Format

### Full Structure (Auto-Generated)

```json
{
  "cache_version": "1.0",
  "generated_at": "2026-02-05T10:30:00",
  "sources": [
    {
      "source_id": "gfhk_memory",
      "pdf_path": "/Users/Shared/ksvc/pdfs/20260204/GFHK - Memory price impact.pdf",
      "pdf_name": "GFHK - Memory price impact.pdf",
      "tag": "GFHK",
      "chars_extracted": 13199
    },
    {
      "source_id": "goldman_abf",
      "pdf_path": "/Users/Shared/ksvc/pdfs/20260204/Goldman ABF shortage.pdf",
      "pdf_name": "Goldman Sachs ABF shortage report.pdf",
      "tag": "Goldman Sachs",
      "chars_extracted": 25000
    }
  ],
  "extractions": [
    {
      "entry_id": "gfhk_memory_001",
      "source_id": "gfhk_memory",
      "metric": "Total BOM",
      "product_type": "HGX B300 8-GPU server",
      "time_period": "3Q25 → 1Q26E",
      "figure_ref": "Figure 2",
      "units": "$k",
      "scope": "per server",
      "values": {
        "before": "369",
        "after": "408",
        "change": "39",
        "change_pct": "10.6"
      },
      "context_snippet": "...Figure 2: HGX B300 8-GPU server BOM Analysis...3Q25 ASP...369...1Q26E ASP...408...",
      "char_position": 4359
    }
  ],
  "source_attribution_map": {
    "topics": {
      "Gfhk Memory": {
        "primary_source": "gfhk_memory",
        "tag": "GFHK",
        "key_metrics": ["HBM3e ASP", "DDR5-6400 (128GB)", "NVMe SSD (3.84TB)", "Total BOM"],
        "source_context": "Figures: Figure 2; Time periods: 3Q25 → 1Q26E",
        "notes": "4 extractions from this source"
      },
      "Goldman Abf": {
        "primary_source": "goldman_abf",
        "tag": "Goldman Sachs",
        "key_metrics": ["ABF shortage ratio", "Kinsus PT", "NYPCB PT", "Unimicron PT"],
        "source_context": "Time periods: 2H26, 2027, 2028",
        "notes": "5 extractions from this source"
      }
    },
    "cross_doc_synthesis": {
      "dual_squeeze_thesis": {
        "description": "Memory shortage (1Q26) + ABF substrate shortage (2H26) = compounding AI server bottleneck",
        "components": [
          {"topic": "Gfhk Memory", "source": "gfhk_memory", "timeframe": "1Q26"},
          {"topic": "Goldman Abf", "source": "goldman_abf", "timeframe": "2H26-2028"}
        ]
      }
    }
  }
}
```

---

## Manual Cache Building (Recommended for Precision)

For maximum control, manually structure your cache from grep results:

```python
# After running targeted grep queries, structure results manually
import json

cache = {
    "cache_version": "1.0",
    "generated_at": "2026-02-05T10:30:00",
    "sources": [
        {
            "source_id": "gfhk_memory",
            "pdf_path": "/Users/Shared/ksvc/pdfs/20260204/GFHK - Memory price impact.pdf",
            "pdf_name": "GFHK - Memory price impact.pdf"
        }
    ],
    "extractions": [
        {
            "entry_id": "mem_001",
            "source_id": "gfhk_memory",
            "metric": "Total BOM",
            "product_type": "HGX B300 8-GPU server",  # From Figure 2 title
            "time_period": "3Q25 → 1Q26E",            # From table headers
            "figure_ref": "Figure 2",                  # From grep context
            "units": "dollars per server",             # Inferred from context
            "scope": "single HGX B300 8-GPU server",   # Not 1GW datacenter
            "values": {
                "before": "$369k",
                "after": "$408k",
                "change": "+$39k",
                "change_pct": "+10.6%"
            },
            "source_quote": "3Q25 ASP: Total BOM ($k) 369, 1Q26E ASP: Total BOM ($k) 408",
            "verification": "RLM grep 'Figure 2' + visual inspection"
        }
    ]
}

# Save
with open('draft/2026-02-05-topic-assets/rlm-extraction-cache.json', 'w') as f:
    json.dump(cache, f, indent=2)
```

---

## Verification

**Check cache quality:**
```bash
# Count extractions
jq '.extractions | length' cache.json

# List all product types extracted
jq '.extractions[].product_type' cache.json | sort | uniq

# List all time periods
jq '.extractions[].time_period' cache.json | sort | uniq

# Find entries missing labels
jq '.extractions[] | select(.product_type == null or .time_period == null)' cache.json
```

**Red flags:**
- `product_type: null` → context labels not extracted
- `time_period: null` → missing temporal context
- Many entries with same `char_position` → duplicate extractions

---

## Integration with Source Attribution Map

**Build attribution map during Step 1c:**

```json
{
  "topics": {
    "memory_pricing": {
      "primary_source": "gfhk_memory",
      "tag": "GFHK"
    },
    "abf_shortage": {
      "primary_source": "goldman_abf",
      "tag": "Goldman"
    }
  }
}
```

**Use when writing:**
```python
# Load both cache and attribution map
cache = load_json('rlm-extraction-cache.json')
attr_map = cache.get('source_attribution_map', {})

# Get topic attribution
topic = "memory_pricing"
source_tag = attr_map['topics'][topic]['tag']  # "GFHK"

# Write with attribution
write(f"{source_tag}'s BOM breakdown shows: ...")
# → "GFHK's BOM breakdown shows: ..."
# Not: "Goldman's BOM breakdown" (wrong attribution)
```

---

## Troubleshooting

### "No RLM state found"

**Cause:** Haven't run RLM yet, or state.pkl in wrong location

**Fix:**
```bash
# Check if state.pkl exists
ls -la ~/.claude/skills/rlm-repl/scripts/.claude/rlm_state/state.pkl

# If not, run RLM first:
cd ~/.claude/skills/rlm-repl/scripts
python3 rlm_repl.py init "/path/to/pdf.pdf"
```

### "Empty extractions list"

**Cause:** Auto-extraction regex didn't find patterns

**Fix:** Use manual cache building with your grep results (see above)

### "Product type is null"

**Cause:** Context window didn't capture product label

**Fix:** Use wider grep window (500+ chars) or manually add labels

---

## Advanced: Custom Context Extractors

**Add custom patterns for your domain:**

```python
# Edit build_extraction_cache.py

def extract_context_labels(text: str, window_start: int) -> Dict:
    # Add custom patterns
    custom_patterns = {
        'wafer_capacity': r'(\d+k?\s*WPM)',  # "135k WPM"
        'fab_name': r'(Fab\s+[A-Z0-9]+)',    # "Fab 3"
        'process_node': r'(\d+nm)',           # "7nm"
    }

    # Extract using custom patterns
    ...
```

---

## Next Steps

1. **Test the script:**
   ```bash
   # Run on current thread
   python3 build_extraction_cache.py \
       --output test-cache.json
   ```

2. **Integrate into workflow:**
   - Add Step 1b.5 (build cache) to kirk-content-pipeline skill
   - Add cache loading to Step 3 (writing)
   - Update Step 4b (audit) to verify against cache

3. **Make it mandatory:**
   - Step 3 should ERROR if trying to write number not in cache
   - Enforce: "All claims must reference cache entry"
