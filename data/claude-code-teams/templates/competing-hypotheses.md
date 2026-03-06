# Competing Hypotheses Template

## When to Use This Pattern

✅ **Use when:**
- Debugging a complex issue with multiple plausible causes
- Root cause is unclear after initial investigation
- Issue spans multiple systems/layers
- Want to avoid confirmation bias (testing only one theory)

❌ **Don't use when:**
- Root cause is obvious (single clear culprit)
- Issue is easily reproducible in isolation
- Only one hypothesis is plausible
- Budget is tight (parallel investigation multiplies cost)

## Team Structure

**Lead:** Coordinator who synthesizes findings and facilitates debate
**Teammates:** 2-3 investigators, each assigned a different hypothesis

Typical hypotheses:
- **Database Issues:** Connection pool exhaustion, slow queries, lock contention
- **Application Issues:** Memory leak, CPU spike, infinite loop
- **Infrastructure Issues:** Network latency, disk I/O, resource limits
- **External Dependencies:** Third-party API issues, message queue backlog

## File/Directory Boundaries

Each investigator produces separate output:

```
hypothesis-A-investigation.md    # Database investigator's findings
hypothesis-B-investigation.md    # Application investigator's findings
hypothesis-C-investigation.md    # Infrastructure investigator's findings
debate-transcript.md             # Lead's synthesis + debate
root-cause-conclusion.md         # Final diagnosis + remediation plan
```

## Spawn Prompt (Copy-Paste Ready)

```markdown
I need to debug a complex issue with multiple plausible causes: [DESCRIBE ISSUE - e.g., "API latency spiked from 200ms to 5s starting at 14:00 UTC"]

**Symptoms:**
- [SYMPTOM 1 - e.g., "p99 latency increased 25x"]
- [SYMPTOM 2 - e.g., "Error rate unchanged (still <0.1%)"]
- [SYMPTOM 3 - e.g., "Only affects /search endpoint"]

**Context:**
- [RECENT CHANGES - e.g., "Deployed new search ranking algorithm at 13:45 UTC"]
- [SCALE - e.g., "Traffic volume normal (~1000 req/s)"]
- [ENVIRONMENT - e.g., "Production (AWS us-east-1)"]

Spawn 3 investigators using Sonnet (tactical investigation):

1. **Hypothesis A: Database Performance**
   - Name: db-investigator
   - Theory: Slow queries or connection pool exhaustion
   - Output: hypothesis-A-investigation.md
   - Investigation tasks:
     * Check slow query logs (queries >1s)
     * Monitor connection pool utilization
     * Review recent schema changes or missing indexes
     * Check for lock contention or deadlocks
     * Test query performance in isolation

2. **Hypothesis B: Application Logic**
   - Name: app-investigator
   - Theory: Inefficient algorithm or memory leak in new code
   - Output: hypothesis-B-investigation.md
   - Investigation tasks:
     * Profile CPU/memory usage during high latency
     * Review new search ranking algorithm for O(n²) patterns
     * Check for synchronous external API calls in request path
     * Test algorithm performance with production data volume
     * Look for caching misses or cache invalidation issues

3. **Hypothesis C: Infrastructure/Network**
   - Name: infra-investigator
   - Theory: Network latency, resource limits, or external dependency issue
   - Output: hypothesis-C-investigation.md
   - Investigation tasks:
     * Check network latency to database/external APIs
     * Monitor CPU/memory/disk I/O on application servers
     * Review AWS CloudWatch for throttling or limits
     * Test connectivity to external search index service
     * Check for DNS resolution delays

**Coordination rules:**
- Use delegate mode: I coordinate, teammates investigate (I don't implement fixes yet)
- Each investigator works independently (parallel investigation)
- Investigators should report:
  * Confidence level (High / Medium / Low that this is the root cause)
  * Evidence found (logs, metrics, traces)
  * Recommendation (if this hypothesis is correct, what's the fix?)
  * Tests performed
- Wait for all 3 investigators to complete before debate

**After all teammates finish:**
1. Read all 3 investigation reports
2. Facilitate debate: each investigator presents evidence
3. Synthesize into root-cause-conclusion.md with:
   - Root cause (based on strongest evidence)
   - Contributing factors (if multiple causes)
   - Remediation plan (immediate + long-term)
   - Confidence level in diagnosis
4. If no clear winner, recommend additional targeted investigation
```

## Expected Outcomes

### Individual Investigation Reports

**hypothesis-A-investigation.md (Database):**
```markdown
# Hypothesis A: Database Performance Issue

## Confidence Level: MEDIUM

## Evidence Found
- ✅ Slow query log shows 15 queries >2s (normally <5)
- ✅ Connection pool utilization 85% (normally 40-50%)
- ❌ No missing indexes detected
- ❌ No lock contention in logs

## Key Finding
New search algorithm generates complex JOIN with 4 tables. Query plan shows full table scan on `search_terms` table (2M rows).

## Test Results
- Isolated query execution: 3.2s avg
- With proposed index on `search_terms.term`: 0.15s avg

## Recommendation
**If this is root cause:**
1. Add index: `CREATE INDEX idx_search_terms ON search_terms(term, document_id)`
2. Rewrite query to use index hint
3. Monitor query performance after deployment

**Confidence reasoning:**
- Timing matches (slow queries started at 13:45)
- Impact magnitude matches (3s query → 5s p99 latency)
- But: Only 15 slow queries vs 1000 req/s suggests other factors involved
```

**hypothesis-B-investigation.md (Application):**
```markdown
# Hypothesis B: Application Logic Issue

## Confidence Level: HIGH

## Evidence Found
- ✅ CPU spike on application servers (30% → 90%)
- ✅ New ranking algorithm has O(n²) sorting step
- ✅ Profiling shows 80% time in `rankResults()` function
- ✅ Algorithm complexity scales with result set size

## Key Finding
New ranking algorithm sorts results twice:
1. Initial sort by relevance score: O(n log n)
2. Re-sort by custom ranking (nested loop comparing all pairs): O(n²)

With 500-1000 results per search, this causes massive CPU spike.

## Test Results
- Old algorithm: 10ms avg for 1000 results
- New algorithm: 4200ms avg for 1000 results
- New algorithm with single-sort optimization: 15ms avg

## Recommendation
**If this is root cause:**
1. IMMEDIATE: Roll back to old algorithm
2. SHORT-TERM: Fix O(n²) nested loop → single-pass sort
3. LONG-TERM: Add performance tests for algorithm changes

**Confidence reasoning:**
- Timing matches exactly (deployed at 13:45)
- Impact magnitude matches (4s algorithm → 5s p99 latency)
- CPU spike correlates perfectly with latency spike
- O(n²) complexity explains why only high-traffic endpoint affected
```

**hypothesis-C-investigation.md (Infrastructure):**
```markdown
# Hypothesis C: Infrastructure/Network Issue

## Confidence Level: LOW

## Evidence Found
- ❌ Network latency to database normal (2-3ms)
- ❌ No AWS throttling or service limits hit
- ✅ CPU utilization high (see Hypothesis B)
- ❌ External API latency normal (<50ms)

## Key Finding
No infrastructure issues detected. High CPU usage found, but likely caused by application logic (see Hypothesis B).

## Test Results
- Network connectivity: All green
- DNS resolution: Normal (<10ms)
- Disk I/O: Normal utilization

## Recommendation
**Confidence reasoning:**
- No evidence of infrastructure issues
- All metrics within normal ranges except CPU (which points to app logic)
- Recommend ruling out this hypothesis
```

### Debate and Conclusion

**root-cause-conclusion.md:**
```markdown
# Root Cause Analysis: API Latency Spike

## Conclusion: Hypothesis B (Application Logic) - HIGH CONFIDENCE

### Root Cause
New search ranking algorithm contains O(n²) nested loop that sorts results twice. With 500-1000 results per search, this causes 4+ second CPU-bound processing time.

### Evidence
1. CPU spike correlates perfectly with deployment time (13:45)
2. Profiling shows 80% time in `rankResults()` function
3. Algorithm complexity confirmed in code review
4. Test with optimized algorithm reduces latency from 4200ms → 15ms

### Contributing Factors
- Database queries slightly slower (3s vs 0.5s normally) due to complex JOIN
- Connection pool utilization elevated but not exhausted
- **Assessment:** Database issue is secondary symptom, not root cause

### Remediation Plan

**Immediate (next 30 min):**
1. Roll back to previous ranking algorithm
2. Verify latency returns to normal (<200ms p99)

**Short-term (next sprint):**
1. Fix O(n²) nested loop → single-pass sort with custom comparator
2. Add unit test: `rankResults()` must complete in <100ms for 1000 items
3. Add performance regression test to CI pipeline

**Long-term (next quarter):**
1. Establish performance budgets for critical paths
2. Require performance testing for algorithm changes
3. Add profiling to staging environment

## Confidence Level: 95%

### Why high confidence:
- Timing matches exactly
- Impact magnitude matches
- Code review confirms O(n²) complexity
- Test with fix eliminates issue

### Remaining uncertainty:
- Database issue may resurface after app fix (monitor closely)
```

## Timing

**Sequential investigation:** ~60-90 minutes (20-30 min per hypothesis)
**Parallel investigation:** ~25-35 minutes (all hypotheses simultaneously)

**Speedup:** ~2-3x faster

## Cost Estimate

**Team:** 1 Opus lead + 3 Sonnet investigators
**Duration:** ~30 minutes
**Estimated cost:** $18-25

## Variations

### Two-Hypothesis Variant
If only 2 plausible causes, spawn 2 investigators instead of 3.

### Four-Hypothesis Deep Dive
For very complex issues, add:
- **External Dependencies:** Third-party APIs, message queues
- **Data Issues:** Corrupt data, unexpected input patterns

## Success Metrics

✅ **Successful if:**
- All investigators complete within 35 minutes
- Evidence is concrete (logs, metrics, traces, not speculation)
- Confidence levels are realistic (not all "HIGH")
- Debate leads to clear conclusion
- Remediation plan is actionable

❌ **Red flags:**
- All hypotheses rated "HIGH" confidence (suggests lack of evidence evaluation)
- Vague findings without concrete evidence
- Lead concluding before debate
- No remediation plan

## Follow-Up Actions

After root cause identified:
1. Execute remediation plan (immediate fix)
2. Verify issue resolved (monitor latency returns to normal)
3. Create tickets for short-term and long-term improvements
4. Update runbook with learnings
5. Post-mortem to prevent recurrence
