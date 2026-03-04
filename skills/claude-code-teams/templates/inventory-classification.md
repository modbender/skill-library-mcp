# Inventory Classification Template

## When to Use This Pattern

✅ **Use when:**
- Processing many independent items (files, records, components)
- Each item requires similar analysis or transformation
- No dependencies between items (true data-parallel work)
- Want linear speedup (3 agents = 3x faster)

**Examples:**
- Classify 300 components by complexity (simple/medium/complex)
- Migrate 500 legacy files to new format
- Add TypeScript types to 200 JavaScript files
- Audit 150 API endpoints for security issues
- Refactor 100 test files to new testing library

❌ **Don't use when:**
- Items have dependencies (file A imports file B)
- Work requires coordination (shared state)
- Items are heterogeneous (each needs different approach)
- Total work is small (<30 items) - overhead > benefit

## Team Structure

**Lead:** Coordinator who divides work and aggregates results
**Teammates:** N workers (typically 3-6), each processing a subset of items

**Team sizing:**
- **3 workers:** Good balance (300 items = 100 per worker)
- **6 workers:** For urgent work (300 items = 50 per worker)
- **>6 workers:** Diminishing returns (coordination overhead)

## File/Directory Boundaries

**Critical:** Each worker owns distinct items (no overlap).

```
inventory-work-[date]/
  items-manifest.md          # Lead creates: full list of items
  assignments.md             # Lead creates: which worker gets which items
  worker-1-results.md        # Worker 1's processed items
  worker-2-results.md        # Worker 2's processed items
  worker-3-results.md        # Worker 3's processed items
  aggregated-results.md      # Lead's synthesis
  summary-report.md          # Lead's summary statistics
```

## Spawn Prompt (Copy-Paste Ready)

```markdown
I need to classify/process [NUMBER] items: [DESCRIPTION - e.g., "300 React components by complexity"]

**Task:** [WHAT TO DO - e.g., "Classify each component as Simple, Medium, or Complex based on criteria"]

**Classification criteria:**
- [CRITERION 1 - e.g., "Simple: <50 LOC, no state, pure presentation"]
- [CRITERION 2 - e.g., "Medium: 50-200 LOC, local state, some logic"]
- [CRITERION 3 - e.g., "Complex: >200 LOC, global state, business logic"]

**Items to process:**
[PROVIDE LIST OR DIRECTORY - e.g., "All .tsx files in src/components/"]

**Expected output format:**
```
| Component | LOC | Complexity | Reason |
|-----------|-----|------------|--------|
| Button.tsx | 35 | Simple | Pure presentation, no state |
| UserProfile.tsx | 180 | Medium | Local state, API calls |
| Dashboard.tsx | 450 | Complex | Redux, 5 API calls, business logic |
```

---

First, I will create the items manifest and divide work. Wait for my signal before teammates start processing.

---

**[AFTER CREATING MANIFEST AND ASSIGNMENTS]**

Items are divided in `assignments.md`. Now spawn 3 workers using Sonnet:

1. **Worker 1**
   - Name: classifier-1
   - Items: [RANGE - e.g., "Items 1-100 (see assignments.md)"]
   - Output: worker-1-results.md
   - Tasks:
     * Process assigned items in order
     * For each item: analyze, classify, document reason
     * Output in specified format (table)
     * Report completion when done

2. **Worker 2**
   - Name: classifier-2
   - Items: [RANGE - e.g., "Items 101-200 (see assignments.md)"]
   - Output: worker-2-results.md
   - Tasks:
     * Process assigned items in order
     * For each item: analyze, classify, document reason
     * Output in specified format (table)
     * Report completion when done

3. **Worker 3**
   - Name: classifier-3
   - Items: [RANGE - e.g., "Items 201-300 (see assignments.md)"]
   - Output: worker-3-results.md
   - Tasks:
     * Process assigned items in order
     * For each item: analyze, classify, document reason
     * Output in specified format (table)
     * Report completion when done

**Coordination rules:**
- Use delegate mode: I coordinate, workers process
- Workers operate independently (no communication between workers)
- Each worker owns distinct items (no overlap)
- Workers should NOT read other workers' results (prevents confusion)
- Wait for all workers to complete before aggregation

**After all workers finish:**
1. Read all worker result files
2. Aggregate into single results file
3. Generate summary statistics:
   - Total items processed
   - Breakdown by classification (Simple: 45%, Medium: 40%, Complex: 15%)
   - Any anomalies or patterns
4. Verify no items missed (count should match manifest)
```

## Expected Outcomes

### Items Manifest (Lead creates)

**items-manifest.md:**
```markdown
# Component Classification - Items Manifest

**Total items:** 300 components
**Location:** src/components/
**Generated:** 2026-02-16

## Full List

1. src/components/Button.tsx
2. src/components/Input.tsx
3. src/components/UserProfile.tsx
...
300. src/components/Dashboard.tsx
```

### Assignments (Lead creates)

**assignments.md:**
```markdown
# Work Assignments

## Worker 1 (classifier-1)
**Items 1-100:**
1. src/components/Button.tsx
2. src/components/Input.tsx
...
100. src/components/FormField.tsx

## Worker 2 (classifier-2)
**Items 101-200:**
101. src/components/Modal.tsx
102. src/components/Dropdown.tsx
...
200. src/components/Sidebar.tsx

## Worker 3 (classifier-3)
**Items 201-300:**
201. src/components/Header.tsx
202. src/components/Footer.tsx
...
300. src/components/Dashboard.tsx
```

### Worker Results

**worker-1-results.md:**
```markdown
# Worker 1 Results (Items 1-100)

| Item | Component | LOC | Complexity | Reason |
|------|-----------|-----|------------|--------|
| 1 | Button.tsx | 35 | Simple | Pure presentation, no state, just props |
| 2 | Input.tsx | 42 | Simple | Controlled input, minimal logic |
| 3 | UserProfile.tsx | 180 | Medium | useEffect, API call, local state |
| 4 | FormField.tsx | 88 | Medium | Validation logic, error handling |
...
| 100 | Pagination.tsx | 120 | Medium | State management, click handlers |

**Summary:**
- Total processed: 100
- Simple: 45
- Medium: 48
- Complex: 7
```

**worker-2-results.md:**
```markdown
# Worker 2 Results (Items 101-200)

| Item | Component | LOC | Complexity | Reason |
|------|-----------|-----|------------|--------|
| 101 | Modal.tsx | 95 | Medium | Portal, useEffect, escape key handler |
| 102 | Dropdown.tsx | 68 | Medium | Click outside detection, state |
...
| 200 | Sidebar.tsx | 155 | Medium | Navigation state, responsive logic |

**Summary:**
- Total processed: 100
- Simple: 38
- Medium: 52
- Complex: 10
```

**worker-3-results.md:**
```markdown
# Worker 3 Results (Items 201-300)

| Item | Component | LOC | Complexity | Reason |
|------|-----------|-----|------------|--------|
| 201 | Header.tsx | 210 | Complex | Auth logic, notifications, Redux |
| 202 | Footer.tsx | 45 | Simple | Pure presentation |
...
| 300 | Dashboard.tsx | 520 | Complex | 5 API calls, Redux, charts, filters |

**Summary:**
- Total processed: 100
- Simple: 40
- Medium: 45
- Complex: 15
```

### Aggregated Results

**aggregated-results.md:**
```markdown
# Component Classification - Aggregated Results

**Total components:** 300
**Processed by:** 3 workers (classifier-1, classifier-2, classifier-3)
**Date:** 2026-02-16

## All Components (Sorted by Complexity)

### Complex (38 components, 12.7%)
| Component | LOC | Worker | Reason |
|-----------|-----|--------|--------|
| Dashboard.tsx | 520 | 3 | 5 API calls, Redux, charts, filters |
| AdminPanel.tsx | 480 | 3 | User management, permissions, 3 APIs |
| Analytics.tsx | 445 | 2 | Data viz, 4 API calls, complex state |
...

### Medium (145 components, 48.3%)
| Component | LOC | Worker | Reason |
|-----------|-----|--------|--------|
| Sidebar.tsx | 155 | 2 | Navigation state, responsive logic |
| Modal.tsx | 95 | 2 | Portal, useEffect, escape key handler |
...

### Simple (117 components, 39%)
| Component | LOC | Worker | Reason |
|-----------|-----|--------|--------|
| Footer.tsx | 45 | 3 | Pure presentation |
| Input.tsx | 42 | 1 | Controlled input, minimal logic |
| Button.tsx | 35 | 1 | Pure presentation, no state |
...

## Verification
✅ Total items processed: 300 (matches manifest)
✅ No duplicates detected
✅ No items missed
```

### Summary Report

**summary-report.md:**
```markdown
# Component Classification - Summary Report

## Executive Summary

Classified 300 React components across the codebase in 35 minutes using 3-worker parallel processing.

## Results Breakdown

| Complexity | Count | % of Total | Avg LOC |
|------------|-------|------------|---------|
| Simple | 117 | 39% | 48 |
| Medium | 145 | 48% | 125 |
| Complex | 38 | 13% | 380 |
| **Total** | **300** | **100%** | **142** |

## Key Insights

### 1. Complexity Distribution
- **39% Simple:** Good foundation of reusable components
- **48% Medium:** Majority are feature components with moderate logic
- **13% Complex:** Small set of high-complexity components

### 2. Complexity Drivers
Most common reasons for "Complex" classification:
1. Multiple API calls (5+ calls): 18 components
2. Redux/global state: 15 components
3. Business logic (>200 LOC): 12 components
4. Data visualization: 8 components

### 3. Refactoring Opportunities
**High-priority candidates for simplification:**
- Dashboard.tsx (520 LOC) → Split into 3-4 smaller components
- AdminPanel.tsx (480 LOC) → Extract permission logic to hook
- Analytics.tsx (445 LOC) → Move chart configs to separate files

**Estimated impact:** Reduce complex components from 38 → 25 (35% reduction)

## Recommendations

### 1. Immediate (This Sprint)
- Refactor top 3 complex components (Dashboard, AdminPanel, Analytics)
- Extract common patterns into hooks

### 2. Short-term (Next Month)
- Establish complexity budget: max 250 LOC per component
- Add Lint rule: flag components >250 LOC for review
- Create component templates for common patterns

### 3. Long-term (Next Quarter)
- Reduce complex components to <10% of total
- Increase simple components to >50% of total
- Build component library from simple components

## Performance Metrics

**Processing speed:**
- Sequential (1 worker): Est. 120 minutes (300 components × 24s avg)
- Parallel (3 workers): Actual 35 minutes
- **Speedup:** 3.4x faster

**Cost:**
- Team: 1 Opus lead + 3 Sonnet workers
- Duration: 35 minutes
- Estimated cost: $20-28

## Next Steps

1. Share report with team
2. Create tickets for top 3 refactoring candidates
3. Schedule component complexity review (monthly)
4. Update component guidelines with complexity budget
```

## Timing

**Sequential processing:** ~120 minutes (300 items × 24s avg)
**Parallel processing (3 workers):** ~35 minutes (100 items × 24s avg per worker)

**Speedup:** 3-3.5x faster (near-linear scaling)

## Cost Estimate

**Team:** 1 Opus lead + 3 Sonnet workers
**Duration:** ~35 minutes
**Estimated cost:** $20-28

## Success Metrics

✅ **Successful if:**
- All workers complete within similar time (±10% variance)
- Total items processed matches manifest (no items missed)
- No duplicate processing (each item processed exactly once)
- Results are consistent (same criteria applied)
- Near-linear speedup (3 workers ≈ 3x faster)

❌ **Red flags:**
- One worker finishes in 10 min, another in 60 min (uneven distribution)
- Missing items or duplicates
- Inconsistent criteria application (one worker more strict)
- Workers editing each other's files (boundary violation)

## Variations

### Two-Worker Variant (Budget-Conscious)
- 300 items → 150 per worker
- Slower (50 min vs 35 min) but cheaper

### Six-Worker Variant (Urgent)
- 300 items → 50 per worker
- Faster (20 min vs 35 min) but more expensive
- Only use for urgent deadlines

### Heterogeneous Items Variant
If items require different approaches:
- Lead pre-classifies items into categories
- Assign each worker a category (not a range)
- Example: Worker 1 gets "data components", Worker 2 gets "form components"

## Common Pitfalls

### Uneven Distribution
**Problem:** Items 1-100 are simpler than items 201-300 → Worker 1 finishes early

**Solution:**
- Shuffle items before assigning (random distribution)
- Or: Interleave assignments (Worker 1 gets items 1, 4, 7... Worker 2 gets items 2, 5, 8...)

### Inconsistent Criteria
**Problem:** Workers apply classification criteria differently

**Solution:**
- Provide 3-5 reference examples in spawn prompt
- Example: "Button.tsx is Simple because <50 LOC, no state"

### Dependencies Between Items
**Problem:** File A imports File B, but different workers process them

**Solution:**
- Use different pattern (not inventory classification)
- Or: Pre-analyze dependencies, assign related files to same worker

## Follow-Up Actions

After aggregation:
1. Review summary report with team
2. Create tickets for high-priority refactoring
3. Update coding standards (complexity budgets)
4. Schedule follow-up audit (3 months)
5. Track metrics (% complex components over time)
