# Deployment Verification Guide

**Core Problem:** Agents build features but forget to wire them into production.

**Real Example (2026-02-02):**
- Built: `dynamic_trader.py` with news verification
- Built: Improved `notify.py` with URLs and scoring  
- **Forgot:** Hourly cron still using old output format
- **Result:** Users got incomplete reports

---

## Why This Happens

**Agent mindset:**
```
Task: "Build feature X"
→ Code written ✅
→ "Done" ❌ (Wrong!)
```

**Should be:**
```
Goal: "Users receive benefit X"
→ Build feature
→ Test production flow
→ Find integration gaps
→ Fix them
→ Verify user receives benefit
→ "Done" ✅
```

---

## The Gap: Code vs Production

**What agents often miss:**

1. **Entry points** - How does code actually run?
   - Cron jobs
   - APIs/webhooks
   - Manual commands
   - Background workers

2. **Data flow** - Where does output go?
   - Files
   - Databases
   - Message queues
   - User-facing channels

3. **Format assumptions** - What does consumer expect?
   - JSON vs plain text
   - Field names/structure
   - Required vs optional fields

---

## Mechanical Enforcement

**Don't rely on agent memory. Make it mechanical.**

### 1. Deployment Check Script

Template: `scripts/create-deployment-check.sh`

Creates `.deployment-check.sh` that:
- ✅ Runs actual production flow
- ✅ Verifies output exists
- ✅ Checks output format
- ✅ Tests all integration points
- ❌ Blocks if any test fails

### 2. Pre-Commit Hook

Runs deployment check before allowing commit:
```bash
# Project files changed?
→ Run .deployment-check.sh
→ All pass? Allow commit
→ Any fail? Block ❌
```

### 3. Deployment Checklist

Template: `DEPLOYMENT-CHECKLIST.md`

Forces agent to think through:
- What are the entry points?
- Where does output go?
- What format is expected?
- How will I verify end-to-end?

---

## Implementation Steps

### For a New Project

```bash
cd your-project/
bash /path/to/agent-guardrails/scripts/create-deployment-check.sh .
```

This creates:
- `.deployment-check.sh` (customize with your tests)
- `DEPLOYMENT-CHECKLIST.md` (document your flow)
- `.git-hooks/pre-commit-deployment` (install to enforce)

### For Existing Project

1. **Identify integration points:**
   - Where does your code get called?
   - What consumes your output?

2. **Create tests:**
   ```bash
   # Test: Does main flow work?
   bash scripts/generate_report.sh
   
   # Test: Output has required fields?
   grep -q "Required Field" /tmp/output.txt
   
   # Test: User actually receives it?
   # (manual check or automated)
   ```

3. **Add to .deployment-check.sh:**
   ```bash
   echo "Test 1: Report generation..."
   if bash scripts/generate_report.sh > /dev/null 2>&1; then
       echo "  ✅ Generated"
   else
       echo "  ❌ Failed"
       FAILED=1
   fi
   ```

4. **Install git hook:**
   ```bash
   cp .git-hooks/pre-commit-deployment .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit
   ```

---

## Test Coverage

### Minimum (Must Have)

- ✅ **Main flow runs** (no crashes)
- ✅ **Output exists** (file/DB/message created)
- ✅ **Output format valid** (parseable, has required fields)

### Recommended (Should Have)

- ✅ **All entry points tested** (cron, API, manual)
- ✅ **Edge cases handled** (empty, errors, timeouts)
- ✅ **User-facing output verified** (what they actually see)

### Advanced (Nice to Have)

- ✅ **Integration tests** (end-to-end with real services)
- ✅ **Performance checks** (not too slow)
- ✅ **Monitoring alerts** (catch issues in production)

---

## Common Pitfalls

### 1. "I tested the function"
❌ **Wrong:**
```python
def generate_report():
    return "Report"

# Tested: ✅ Returns "Report"
```

✅ **Right:**
```bash
# Test the FULL FLOW:
bash scripts/hourly_cron.sh
# → Calls generate_report()
# → Saves to /tmp/report.txt
# → Sends via message tool
# → User receives message

# Verify: User got "Report" in their chat
```

### 2. "It works when I run it manually"
❌ **Wrong:**
```bash
# Agent runs: python3 script.py
# Works! ✅

# But cron runs: /usr/bin/python3 script.py
# Different environment, missing deps ❌
```

✅ **Right:**
```bash
# Test the ACTUAL cron command:
/usr/bin/python3 /full/path/script.py

# Or better: run the cron job manually
bash /path/to/cron_wrapper.sh
```

### 3. "I updated the code"
❌ **Wrong:**
```bash
# Updated: notify.py
# But cron still calls: old_notify.py
# Users get old output ❌
```

✅ **Right:**
```bash
# Check what cron ACTUALLY calls:
crontab -l | grep notify

# Update ALL entry points:
# - Cron jobs
# - API routes
# - Manual commands
# - Documentation
```

---

## Integration with Agent Workflow

### Update AGENTS.md

Add to your project's `AGENTS.md`:

```markdown
### Deployment Verification (Mandatory)

**Before marking feature "done":**
```bash
bash .deployment-check.sh
```

**Git hook:** Auto-runs on commit. Blocks if fails.

**Rule:** Feature ≠ done until user receives benefit from production flow.
```

### Agent Instruction

```markdown
## Completing Features

When you finish a feature:

1. ✅ Code written
2. ✅ **Run .deployment-check.sh** ← Mandatory
3. ✅ **Fix any issues found**
4. ✅ **Re-verify**
5. ✅ **Update DEPLOYMENT-CHECKLIST.md** with any new lessons

Only then say "Done."
```

---

## Example: Kalshi Hourly Reports

### Problem

Built new notify.py with scoring/URLs, but forgot to update cron.

### Solution

**Created .deployment-check.sh:**
```bash
# Test 1: Cron generates report
bash kalshi/send_hourly_scan.sh > /dev/null 2>&1
if [ -f /tmp/kalshi_hourly_scan_dm.txt ]; then
    echo "  ✅ Report generated"
fi

# Test 2: Report has URLs
if grep -q "https://kalshi.com/" /tmp/kalshi_hourly_scan_dm.txt; then
    echo "  ✅ URLs present"
fi

# Test 3: Report has scoring
if grep -q "Score:" /tmp/kalshi_hourly_scan_dm.txt; then
    echo "  ✅ Scoring present"
fi
```

**Installed git hook:**
```bash
# Runs .deployment-check.sh on every commit
# Blocks if report missing URLs/scoring
```

**Result:**
- Can't commit without verification passing
- Catches integration gaps before they reach users

---

## Maintenance

### When to Update

Update `.deployment-check.sh` when:
- Adding new features
- Changing output format
- Adding new entry points
- Integrating new services

### Record Lessons

In `DEPLOYMENT-CHECKLIST.md`:
```markdown
## Lessons Learned

### 2026-02-02: Incomplete Hourly Reports

**Symptom:** Users got reports missing URLs

**Root cause:** Updated notify.py but cron still used old format

**Fix:** Verified cron output matches new format

**Prevention:** Added "check cron output" to .deployment-check.sh
```

---

## Summary

**Problem:** Agents build features but don't verify production integration

**Solution:** Mechanical enforcement via deployment checks + git hooks

**Key Principle:** A feature isn't done until users receive the benefit

**Reliability:** Code hooks (100%) > Prompt rules (60-70%) > Markdown (40-50%)

**Remember:** If it's not mechanically enforced, it will be forgotten.
