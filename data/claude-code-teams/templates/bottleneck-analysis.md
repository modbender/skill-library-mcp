# Bottleneck Analysis Template

## When to Use This Pattern

✅ **Use when:**
- Performance issue spans multiple systems or layers
- Root cause could be in database, network, application, or frontend
- Need cross-domain expertise to diagnose
- Want parallel investigation across the stack

❌ **Don't use when:**
- Bottleneck is obvious (e.g., single slow query identified)
- Issue is isolated to one layer (use single-domain investigation)
- Profiling tools already pinpoint the issue
- Simple load test reveals the problem

## Team Structure

**Lead:** Coordinator who synthesizes findings across domains
**Teammates:** 3-4 domain specialists
- **Database Analyst:** Query performance, connection pools, indexes
- **Network Analyst:** Latency, throughput, packet loss
- **Application Analyst:** CPU, memory, algorithm efficiency
- **Frontend Analyst (optional):** Render performance, bundle size, API calls

## File/Directory Boundaries

Each analyst produces separate output:

```
bottleneck-analysis-[date]/
  database-analysis.md       # Database analyst's findings
  network-analysis.md        # Network analyst's findings
  application-analysis.md    # Application analyst's findings
  frontend-analysis.md       # Frontend analyst's findings (optional)
  synthesis-report.md        # Lead's cross-domain synthesis
  remediation-plan.md        # Prioritized action plan
```

## Spawn Prompt (Copy-Paste Ready)

```markdown
I need to investigate a performance bottleneck: [ISSUE - e.g., "Dashboard load time increased from 1.5s to 8s"]

**Symptoms:**
- [SYMPTOM 1 - e.g., "Dashboard load time p99 = 8s (was 1.5s)"]
- [SYMPTOM 2 - e.g., "Affects all users (not isolated to subset)"]
- [SYMPTOM 3 - e.g., "Started 3 days ago (Feb 13)"]

**Context:**
- [SCALE - e.g., "500 users, ~2000 dashboard loads/day"]
- [RECENT CHANGES - e.g., "Added 3 new widgets on Feb 12"]
- [ENVIRONMENT - e.g., "Production (AWS us-east-1)"]

**Tools/access available:**
- Database: [e.g., "PostgreSQL slow query log, pgbadger, connection pool stats"]
- Network: [e.g., "CloudWatch metrics, traceroute, curl timing"]
- Application: [e.g., "APM traces (Datadog), CPU/memory graphs"]
- Frontend: [e.g., "Chrome DevTools, Lighthouse reports"]

Spawn 4 domain specialists using Sonnet (tactical investigation):

1. **Database Analyst**
   - Name: db-analyst
   - Focus: Database layer performance
   - Output: database-analysis.md
   - Investigation tasks:
     * Check slow query log (queries >1s)
     * Analyze connection pool utilization
     * Review query execution plans (EXPLAIN ANALYZE)
     * Check for missing indexes
     * Identify lock contention or deadlocks
     * Test query performance in isolation

2. **Network Analyst**
   - Name: network-analyst
   - Focus: Network layer performance
   - Output: network-analysis.md
   - Investigation tasks:
     * Measure API endpoint latency (server TTFB)
     * Check for packet loss or retransmissions
     * Analyze CDN performance (if applicable)
     * Review CloudWatch network metrics
     * Test connectivity from different regions
     * Identify any throttling or rate limiting

3. **Application Analyst**
   - Name: app-analyst
   - Focus: Application layer performance
   - Output: application-analysis.md
   - Investigation tasks:
     * Profile CPU/memory usage during dashboard load
     * Analyze APM traces (identify slow operations)
     * Review new widget code (Feb 12 change)
     * Check for N+1 queries or inefficient loops
     * Identify synchronous operations blocking response
     * Test with widgets disabled (isolate issue)

4. **Frontend Analyst**
   - Name: frontend-analyst
   - Focus: Frontend layer performance
   - Output: frontend-analysis.md
   - Investigation tasks:
     * Run Lighthouse audit (performance score)
     * Check bundle size (before/after Feb 12)
     * Profile render performance (React DevTools)
     * Identify unnecessary re-renders
     * Measure API call waterfall (sequential vs parallel)
     * Test with network throttling (3G simulation)

**Coordination rules:**
- Use delegate mode: I coordinate, specialists investigate
- Each specialist works independently (parallel investigation)
- Specialists should report:
  * Findings (what's slow, by how much)
  * Root cause hypothesis (if identifiable)
  * Recommendation (how to fix)
  * Confidence level (High/Medium/Low)
- Wait for all specialists to complete before synthesis

**After all teammates finish:**
1. Read all domain analysis reports
2. Identify primary bottleneck (which layer is the main culprit?)
3. Identify secondary bottlenecks (contributing factors)
4. Synthesize into remediation-plan.md with:
   - Root cause(s) prioritized by impact
   - Quick wins (can fix in <1 day)
   - Long-term improvements (architectural changes)
   - Expected performance improvement for each fix
```

## Expected Outcomes

### Domain Analysis Reports

**database-analysis.md:**
```markdown
# Database Layer Analysis

## Findings

### Slow Queries Detected
- Query: `SELECT * FROM widgets WHERE dashboard_id = ? ORDER BY position`
  - Execution time: 4.2s (was 0.05s before Feb 12)
  - Executions: 3-5 per dashboard load
  - **Impact: 12-20s total per dashboard load**

### Root Cause
- New widgets added Feb 12 increased widget count from 5 → 20 per dashboard
- Missing index on `(dashboard_id, position)` causes full table scan
- Table now has 500K rows (was 50K before Feb 12)

### Execution Plan Analysis
```sql
EXPLAIN ANALYZE SELECT * FROM widgets WHERE dashboard_id = 'abc';
---
Seq Scan on widgets (cost=0.00..12500.00 rows=20 width=1024) (actual time=4200.123)
  Filter: (dashboard_id = 'abc')
  Rows Removed by Filter: 499980
```

**Problem:** Sequential scan of 500K rows to find 20 matching rows.

### Connection Pool
- Utilization: 40% (normal)
- No connection exhaustion issues

## Recommendation

**Quick Win (fix in <1 hour):**
```sql
CREATE INDEX idx_widgets_dashboard_position 
ON widgets(dashboard_id, position);
```

**Expected improvement:** 4.2s → 0.05s per query = 12-20s saved per dashboard load

**Confidence:** HIGH (index will eliminate full table scan)

## Additional Observations
- No lock contention detected
- No other slow queries (this is the only bottleneck in DB layer)
```

**network-analysis.md:**
```markdown
# Network Layer Analysis

## Findings

### API Endpoint Latency
- `/api/dashboard/{id}` TTFB: 6.5s (was 1.2s)
- Server processing time matches APM data (see Application Analysis)
- Network latency itself is normal (50-80ms)

### No Network Issues Detected
- No packet loss
- No throttling or rate limiting
- CDN performance normal (CSS/JS assets load fast)

## Root Cause
Network layer is NOT the bottleneck. High TTFB is caused by slow server processing (see Application Analysis).

## Recommendation
No network-layer fixes needed. Focus on application and database layers.

**Confidence:** HIGH (network metrics are all normal)
```

**application-analysis.md:**
```markdown
# Application Layer Analysis

## Findings

### APM Trace Analysis
Dashboard load trace breakdown:
- Database queries: 18s (83% of total time)
  - `getWidgets()` called 3 times: 4.2s × 3 = 12.6s
  - Other queries: 5.4s
- Widget rendering: 1.2s (5% of total time)
- Other operations: 2.8s (12% of total time)

### Root Cause
Application is making redundant database calls:
1. Initial load: `getWidgets(dashboardId)` → 4.2s
2. Widget A initialization: `getWidgets(dashboardId)` again → 4.2s
3. Widget B initialization: `getWidgets(dashboardId)` again → 4.2s

**Problem:** No caching between widget initializations. Each widget fetches ALL widgets independently.

### Code Review (Feb 12 change)
```javascript
// Before Feb 12:
const widgets = await getWidgets(dashboardId);
widgets.forEach(w => initializeWidget(w));

// After Feb 12 (PROBLEMATIC):
widgetComponents.forEach(async (WidgetComponent) => {
  const widgets = await getWidgets(dashboardId);  // REDUNDANT CALL
  const widget = widgets.find(w => w.type === WidgetComponent.type);
  initializeWidget(widget);
});
```

## Recommendation

**Quick Win (fix in <2 hours):**
```javascript
// Fetch widgets once, pass to components
const widgets = await getWidgets(dashboardId);
widgetComponents.forEach((WidgetComponent) => {
  const widget = widgets.find(w => w.type === WidgetComponent.type);
  initializeWidget(widget);
});
```

**Expected improvement:** Eliminate 2 redundant calls = 8.4s saved

**Combined with database index:** 18s → 0.15s (total database time)

**Confidence:** HIGH (APM traces show clear redundancy)
```

**frontend-analysis.md:**
```markdown
# Frontend Layer Analysis

## Findings

### Lighthouse Audit
- Performance score: 45/100 (was 85/100)
- Time to Interactive (TTI): 9.2s (was 2.1s)
- Main thread blocking: 8.5s (server wait time)

### Bundle Size
- Before Feb 12: 450 KB (gzipped)
- After Feb 12: 520 KB (gzipped)
- **Increase:** 70 KB (new widget code)

### Render Performance
- React render time: 180ms (acceptable)
- No unnecessary re-renders detected
- No large component trees

### API Call Waterfall
- 1 initial call to `/api/dashboard/{id}`: 8.5s (BLOCKING)
- Then 3 parallel calls for widget data: 200ms each (fast)

## Root Cause
Frontend is blocked waiting for slow API response (8.5s). The delay is server-side, not client-side.

Bundle size increase (70 KB) adds ~100ms load time, but this is minor compared to 8s server delay.

## Recommendation

**Primary:** Fix server-side performance (see Application + Database analyses)

**Secondary (nice-to-have):**
- Code-split widget bundles (reduce initial bundle by ~50 KB)
- Add loading skeleton during server wait (improve perceived performance)

**Expected improvement:** Server fix → 8.5s → 0.5s response time

**Confidence:** HIGH (frontend is waiting on server)
```

### Synthesis Report

**synthesis-report.md:**
```markdown
# Bottleneck Analysis Synthesis

## Primary Bottleneck: Database Layer (83% of load time)

**Root cause:**
Missing index on `widgets(dashboard_id, position)` causes 4.2s sequential scan per query.

**Impact:** 12-20s per dashboard load (query executed 3-5 times)

---

## Secondary Bottleneck: Application Layer (Redundant Calls)

**Root cause:**
Feb 12 code change introduced redundant `getWidgets()` calls (1 per widget instead of 1 per dashboard).

**Impact:** Multiplies database query cost by 3x

---

## Contributing Factors

**Frontend bundle size:** +70 KB adds ~100ms (minor compared to server delay)

**Network layer:** No issues detected (normal latency)

---

## Overall Impact Breakdown

| Layer | Time | % of Total | Issue |
|-------|------|------------|-------|
| Database | 18s | 83% | Slow queries (missing index) |
| Application | 1.2s | 5% | Redundant calls |
| Frontend | 0.5s | 2% | Render time (acceptable) |
| Network | 0.08s | <1% | Normal latency |
| Other | 2.2s | 10% | Misc operations |

**Total:** 21.98s (p99 dashboard load time)
```

### Remediation Plan

**remediation-plan.md:**
```markdown
# Remediation Plan

## Quick Wins (Fix Today)

### 1. Add Database Index (1 hour)
```sql
CREATE INDEX idx_widgets_dashboard_position 
ON widgets(dashboard_id, position);
```

**Expected improvement:** 4.2s → 0.05s per query
**Total impact:** 12-20s → 0.15-0.25s

### 2. Eliminate Redundant Calls (2 hours)
Refactor widget initialization to fetch data once, pass to components.

**Expected improvement:** Reduce queries from 3 → 1
**Total impact:** With index: 0.15s total database time

---

## Expected Performance After Quick Wins

| Metric | Before | After Quick Wins | Improvement |
|--------|--------|------------------|-------------|
| p99 load time | 8s | 1.5s | 81% faster |
| Database time | 18s | 0.15s | 99% faster |
| Total time | 22s | 3.5s | 84% faster |

---

## Long-Term Improvements (Next Sprint)

### 3. Cache Widget Data (1 day)
Implement Redis cache for widget data (TTL: 5 minutes).

**Expected improvement:** 0.15s → 0.01s (cache hit)
**Impact:** Additional 0.14s saved on cache hits

### 4. Code-Split Widget Bundles (2 days)
Split new widget code into separate chunks.

**Expected improvement:** Reduce initial bundle by 50 KB = ~70ms
**Impact:** Minor, but improves perceived performance

### 5. Add Loading Skeleton (1 day)
Show loading skeleton during data fetch.

**Expected improvement:** No performance gain, but better UX

---

## Implementation Order

1. **Database index** (30 min to implement, 10 min to deploy)
2. **Verify improvement** (run load test, check dashboard p99)
3. **Refactor redundant calls** (2 hours)
4. **Verify final improvement** (run load test again)
5. **Long-term improvements** (schedule for next sprint)

---

## Success Metrics

**Target:** p99 load time < 2s (back to Feb 12 baseline of 1.5s)

**After quick wins:** Expected 1.5s (meets target)

**After long-term improvements:** Expected 1.2s (20% better than baseline)

---

## Rollback Plan

If index causes issues:
```sql
DROP INDEX idx_widgets_dashboard_position;
```

If refactor causes bugs:
- Revert commit (deploy previous version)
- Emergency fix tested in staging first
```

## Timing

**Sequential investigation:** ~90-120 minutes (20-30 min per domain)
**Parallel investigation:** ~30-40 minutes (all domains simultaneously)

**Speedup:** ~3x faster

## Cost Estimate

**Team:** 1 Opus lead + 4 Sonnet specialists
**Duration:** ~35 minutes
**Estimated cost:** $22-30

## Success Metrics

✅ **Successful if:**
- All specialists complete within 40 minutes
- Primary bottleneck clearly identified (with evidence)
- Remediation plan includes quick wins (fixable today)
- Expected improvements are quantified (not just "should be faster")
- Cross-domain synthesis reveals full picture

❌ **Red flags:**
- Multiple "primary" bottlenecks (suggests lack of prioritization)
- Vague recommendations ("optimize database" without specifics)
- No quantified expected improvement
- Specialists contradict each other without resolution

## Variations

### Three-Specialist Variant (Budget-Conscious)
Combine network + application into single analyst:
- Database Analyst
- Network + Application Analyst
- Frontend Analyst

**Cost savings:** ~25% less, but slightly slower

### Five-Specialist Deep Dive
Add:
- **Caching Analyst:** Redis, CDN, browser cache
- Use for complex distributed systems

## Follow-Up Actions

After remediation:
1. Implement quick wins (same day)
2. Verify improvement with load test
3. Schedule long-term improvements (next sprint)
4. Update monitoring alerts (p99 < 2s threshold)
5. Document learnings in runbook
