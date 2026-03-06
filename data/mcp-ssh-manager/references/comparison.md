# Comparing Historical Data

This document describes how to compare SSH operation results over time using the workdir structure.

## Comparison Use Cases

| Use Case | What to Compare | Why |
|----------|-----------------|-----|
| **Trend analysis** | Disk usage over weeks | Detect gradual capacity issues |
| **Problem diagnosis** | Before/after system state | Identify what changed |
| **Performance tuning** | CPU/memory under load | Measure impact of changes |
| **Security audit** | Service configurations | Detect unauthorized changes |

## Comparison Methods

### 1. Simple Diff

```bash
# Compare disk usage
diff ~/.ssh-workdir/{hostname}/2026-02-01-system-check/output/df-h.txt \
     ~/.ssh-workdir/{hostname}/2026-02-07-system-check/output/df-h.txt
```

### 2. Side-by-Side Comparison

```bash
# Use diff -y for side-by-side
diff -y ~/.ssh-workdir/{hostname}/2026-02-01-system-check/output/df-h.txt \
       ~/.ssh-workdir/{hostname}/2026-02-07-system-check/output/df-h.txt
```

### 3. Structured Comparison (JSON)

Compare structured data like `status.json`:

```bash
# Extract specific fields
cat ~/.ssh-workdir/{hostname}/2026-02-01-system-check/status.json | jq '.disk'
cat ~/.ssh-workdir/{hostname}/2026-02-07-system-check/status.json | jq '.disk'
```

### 4. Custom Comparison Script

```bash
#!/bin/bash
# compare-status.sh - Compare two status snapshots

OLD_DIR="$1"
NEW_DIR="$2"

echo "=== Disk Comparison ==="
diff "$OLD_DIR/output/df-h.txt" "$NEW_DIR/output/df-h.txt" || true

echo "=== Memory Comparison ==="
diff "$OLD_DIR/output/memory.txt" "$NEW_DIR/output/memory.txt" || true

echo "=== Summary Comparison ==="
diff "$OLD_DIR/summary.md" "$NEW_DIR/summary.md" || true
```

## Comparison Workflows

### Daily System Check Comparison

```bash
# Compare today vs yesterday
bash scripts/compare-status.sh \
  ~/.ssh-workdir/{hostname}/2026-02-06-system-check \
  ~/.ssh-workdir/{hostname}/2026-02-07-system-check
```

Expected output:
```
=== Disk Comparison ===
< /dev/sda1      70%      14G      4.3G
---
> /dev/sda1      75%      15G      3.7G

=== Summary Comparison ===
< - Disk: 70% (4.3GB free)
> - Disk: 75% (3.7GB free)
```

### Weekly Trend Analysis

```bash
# Collect all disk usage from weekly checks
cat > /tmp/disk-trend.txt << 'EOF'
2026-02-01: 65%
2026-02-02: 68%
2026-02-03: 70%
2026-02-04: 72%
2026-02-05: 75%
2026-02-06: 78%
2026-02-07: 80%
EOF

# Analyze trend
cat /tmp/disk-trend.txt
# At this rate, disk will be full in ~2 weeks
```

### Before/After Deployment Comparison

```bash
# Before deployment
mkdir -p ~/.ssh-workdir/{hostname}/2026-02-07-before-deploy/output
ssh_execute server="{hostname}" command="df -h" > ~/.ssh-workdir/{hostname}/2026-02-07-before-deploy/output/df-h.txt
ssh_execute server="{hostname}" command="free -h" > ~/.ssh-workdir/{hostname}/2026-02-07-before-deploy/output/memory.txt

# Deploy...

# After deployment
mkdir -p ~/.ssh-workdir/{hostname}/2026-02-07-after-deploy/output
ssh_execute server="{hostname}" command="df -h" > ~/.ssh-workdir/{hostname}/2026-02-07-after-deploy/output/df-h.txt
ssh_execute server="{hostname}" command="free -h" > ~/.ssh-workdir/{hostname}/2026-02-07-after-deploy/output/memory.txt

# Compare
bash scripts/compare-status.sh \
  ~/.ssh-workdir/{hostname}/2026-02-07-before-deploy \
  ~/.ssh-workdir/{hostname}/2026-02-07-after-deploy
```

### Service Change Detection

```bash
# Before
mkdir -p ~/.ssh-workdir/{hostname}/2026-02-07-before-change/output
ssh_execute server="{hostname}" command="systemctl list-units --type=service --state=running" > \
  ~/.ssh-workdir/{hostname}/2026-02-07-before-change/output/services.txt

# After
mkdir -p ~/.ssh-workdir/{hostname}/2026-02-07-after-change/output
ssh_execute server="{hostname}" command="systemctl list-units --type=service --state=running" > \
  ~/.ssh-workdir/{hostname}/2026-02-07-after-change/output/services.txt

# Find differences
comm -13 <(sort ~/.ssh-workdir/{hostname}/2026-02-07-before-change/output/services.txt) \
       <(sort ~/.ssh-workdir/{hostname}/2026-02-07-after-change/output/services.txt)
```

## Comparison Commands Reference

### Basic Diff

```bash
diff <file1> <file2>
```

### Side-by-Side

```bash
diff -y <file1> <file2>
diff --width=150 -y <file1> <file2>
```

### Unified Format

```bash
diff -u <file1> <file2>
```

### Ignore Whitespace

```bash
diff -w <file1> <file2>
diff -b <file1> <file2>
```

### Binary Files

```bash
cmp <file1> <file2>
```

### JSON Comparison

```bash
# Extract and compare specific fields
diff <(jq -S '.disk' old.json) <(jq -S '.disk' new.json)
diff <(jq '.services | keys' old.json) <(jq '.services | keys' new.json)
```

## Comparison Report Template

Create a comparison report:

```markdown
# Comparison Report: {hostname}

## Compared Period
- Before: {date1}
- After: {date2}
- Duration: {N} days

## Metrics Compared

### Disk Usage
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| /dev/sda1 | 70% | 75% | +5% |
| /home | 45% | 48% | +3% |

### Memory
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Used | 8GB | 9GB | +1GB |
| Available | 8GB | 7GB | -1GB |

### Services
| Service | Before | After | Status |
|---------|--------|-------|--------|
| nginx | Running | Running | ✓ |
| docker | Running | Running | ✓ |
| postgres | Running | Stopped | ⚠️ |

## Key Findings

1. Disk usage increased by 5%
2. Memory usage increased by 1GB
3. PostgreSQL service stopped - investigate

## Recommendations

1. Clean up disk space
2. Check PostgreSQL service
3. Monitor memory usage
```

## Automated Comparison Tools

### compare-snapshots.sh

```bash
#!/bin/bash
# compare-snapshots.sh - Compare two snapshots and generate report

OLD="$1"
NEW="$2"

if [ -z "$OLD" ] || [ -z "$NEW" ]; then
    echo "Usage: $0 <old-snapshot-dir> <new-snapshot-dir>"
    exit 1
fi

cat << EOF
# Comparison Report
Generated: $(date)

## Snapshots Compared
- Before: $OLD
- After: $NEW

## Disk Usage
EOF

if [ -f "$OLD/output/df-h.txt" ] && [ -f "$NEW/output/df-h.txt" ]; then
    diff -u "$OLD/output/df-h.txt" "$NEW/output/df-h.txt" || true
else
    echo "Disk comparison: files not found"
fi

cat << EOF

## Memory Usage
EOF

if [ -f "$OLD/output/memory.txt" ] && [ -f "$NEW/output/memory.txt" ]; then
    diff -u "$OLD/output/memory.txt" "$NEW/output/memory.txt" || true
else
    echo "Memory comparison: files not found"
fi

cat << EOF

## Summary
EOF

if [ -f "$OLD/summary.md" ] && [ -f "$NEW/summary.md" ]; then
    echo "=== Previous Summary ==="
    cat "$OLD/summary.md"
    echo ""
    echo "=== Current Summary ==="
    cat "$NEW/summary.md"
else
    echo "Summary comparison: files not found"
fi
```

## Best Practices for Comparison

1. **Use consistent naming**: Always use `YYYY-MM-DD-{topic}` format
2. **Save structured data**: Use `status.json` for machine-readable comparisons
3. **Document context**: Add notes about why you're comparing
4. **Automate comparisons**: Use scripts for regular comparisons
5. **Track trends**: Keep historical data for trend analysis
6. **Share findings**: Export comparison reports for team review
