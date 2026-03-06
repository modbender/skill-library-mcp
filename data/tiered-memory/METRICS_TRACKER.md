# Memory Metrics Tracker

Python script for tracking memory system health over time.

## Location

`/home/bowen/clawd/skills/tiered-memory/scripts/metrics_tracker.py`

## Features

### 1. Record Metrics (`--record`)

Appends current memory statistics to a JSONL file for historical tracking.

**Usage:**
```bash
python3 metrics_tracker.py --record
```

**Output:**
```
✓ Recorded metrics at 2026-02-09 14:20:44
```

**Data Format (JSONL):**
```json
{"timestamp": 1770607244, "hot_bytes": 3847, "warm_count": 18, "warm_bytes": 5006, "tree_nodes": 20, "evicted": 0, "cold_count": 0}
```

**Storage:**
- File: `memory/memory-metrics.jsonl`
- Format: One JSON line per check
- Fields:
  - `timestamp` - Unix timestamp
  - `hot_bytes` - Hot memory size in bytes
  - `warm_count` - Number of warm entries
  - `warm_bytes` - Warm memory size in bytes
  - `tree_nodes` - Number of tree nodes
  - `evicted` - Total evicted entries (placeholder)
  - `cold_count` - Cold storage entries (placeholder)

---

### 2. Health Report (`--report`)

Displays current memory system health with visual progress bars.

**Usage:**
```bash
python3 metrics_tracker.py --report
```

**Output:**
```
=== Memory Health Report (2026-02-09) ===

Hot:  3.8KB / 5.0KB (75%)  ███████░░░
Warm: 4.9KB / 50KB  (10%)   ░░░░░░░░░░
Tree: 20/50 nodes
Cold: 0 entries

Warm entry count: 18
Score range: N/A
Last consolidation: 1h ago
```

**Features:**
- Visual progress bars (10-segment)
- Human-readable byte formatting (B/KB/MB)
- Current capacity usage percentages
- Entry counts and node statistics

---

### 3. Trend Analysis (`--trend`)

Shows 7-day trend of memory usage with daily averages.

**Usage:**
```bash
python3 metrics_tracker.py --trend
```

**Output:**
```
=== Memory Trend (last 7 days, 42 samples) ===

Date         Hot        Warm            Tree       Cold      
------------------------------------------------------------
2026-02-03   3.2KB      12 entries      18 nodes   0
2026-02-04   3.5KB      14 entries      19 nodes   0
2026-02-05   3.6KB      15 entries      19 nodes   0
2026-02-06   3.7KB      16 entries      20 nodes   0
2026-02-07   3.8KB      17 entries      20 nodes   0
2026-02-08   3.8KB      18 entries      20 nodes   0
2026-02-09   3.8KB      18 entries      20 nodes   0

Trends:
  Hot:  +614B
  Warm: +6 entries
  Tree: +2 nodes
```

**Features:**
- Groups metrics by day
- Calculates daily averages
- Shows growth/decline trends
- Analyzes last 7 days of data

---

## Integration with memory_cli.py

The tracker calls `memory_cli.py stats` to get current memory statistics:

```bash
python3 memory_cli.py stats
```

Returns JSON with hot/warm/tree stats which the tracker parses and records.

---

## Automation

Add to cron for automatic tracking:

```bash
# Record metrics every hour
0 * * * * cd /home/bowen/clawd && python3 skills/tiered-memory/scripts/metrics_tracker.py --record

# Daily health report at 9 AM
0 9 * * * cd /home/bowen/clawd && python3 skills/tiered-memory/scripts/metrics_tracker.py --report
```

Or use OpenClaw's heartbeat system to check periodically.

---

## Implementation Details

**No External Dependencies:**
- Pure Python 3 stdlib
- Uses subprocess to call memory_cli.py
- JSON for data serialization
- Datetime for timestamp handling

**File Structure:**
- JSONL format for easy append and line-by-line parsing
- Each entry is self-contained
- Can be processed by standard Unix tools (grep, awk, jq)

**Error Handling:**
- Returns exit code 0 on success, 1 on failure
- Prints errors to stderr
- Validates memory_cli.py output

---

## Example Workflow

```bash
# Record metrics now
python3 metrics_tracker.py --record

# Check current health
python3 metrics_tracker.py --report

# View trends after a week
python3 metrics_tracker.py --trend
```

---

## Files

**Created:**
- `skills/tiered-memory/scripts/metrics_tracker.py` - Main script
- `memory/memory-metrics.jsonl` - Time-series data storage

**Used:**
- `skills/tiered-memory/scripts/memory_cli.py` - Stats source

**Commit:**
- `030b462` - Add memory metrics tracking script
