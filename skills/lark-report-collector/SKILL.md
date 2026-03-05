---
name: lark-report-collector
description: "Collect weekly reports from Lark Reports (oa.larksuite.com), summarize into Lark Docs, and notify. Use when: (1) collecting weekly reports from specific teams/templates, (2) checking who hasn't submitted reports, (3) generating report summaries as Lark documents. Requires browser automation (Reports is a SPA, API not available on international Lark)."
---

# Lark Report Collector

Collect weekly report data from Lark Reports, summarize into Lark Docs, and send notifications.

## When to Use

- "Collect this week's/last week's reports for Photo/Bloom/H&F"
- "Who hasn't submitted their weekly report?"
- "Summarize weekly reports into a Lark doc"

## Hard Rules (battle-tested)

1. **Reports is a SPA** — curl/web_fetch returns nothing. Must use `browser` (profile=openclaw)
2. **Pagination is reversed** — Next = older weeks, Previous = newer weeks
3. **Always snapshot to confirm week title after pagination** (most common error: collecting wrong week)
4. **One page may show multiple weeks** — data is sorted by time, a single page can span 2-3 weeks
5. **block_type mapping** — 12=bullet, 13=ordered (NOT 9/10! Those are heading7/heading8)
6. **Never restart gateway inside a sub-agent** (kills itself)
7. **Sub-agents need exact URLs and steps** — don't let them explore on their own

## Complete Workflow

### Step 1: Navigate to Reports

```
browser action=navigate profile=openclaw targetUrl="https://oa.larksuite.com/report/record/entry"
```

Prerequisites: openclaw browser must have active Lark login session.

### Step 2: Select Report Template

Snapshot and click the target template menuitem in the left sidebar "Received by me".

### Step 3: Navigate to Target Week

Page defaults to latest data. Week title format: `"Feb 2 ~ Feb 8 Submitted: 18"`

**Pagination (critical):**
- **Next** button = older weeks ⬅️
- **Previous** button = newer weeks ➡️
- Page display: "2/25" (page 2 of 25), page 1 is newest

⚠️ **Snapshot and confirm the date in the title after every page turn!**

### Step 4: Extract Submitted Members Data

- Same page may show multiple weeks — only extract rows belonging to target week
- Paginate through all rows for the target week
- **Append to local file after each extraction** (prevents data loss)

### Step 5: Get Unsubmitted List

"Not submitted: N" button has no snapshot ref. Click via JS evaluate:

```javascript
(() => {
  const btns = [...document.querySelectorAll('button')].filter(
    b => /Not submitted.*\d/.test(b.innerText)
  );
  if(btns.length) { btns[0].click(); return 'clicked'; }
  return 'not found';
})()
```

Dialog shows: unsubmitted count + names + departments.

### Step 6: Create Lark Doc

Create document via Lark Open API (see `lark-api` skill for auth).

**block_type reference (verified):**

| block_type | Type | JSON field |
|-----------|------|-----------|
| 2 | Text | `"text"` |
| 3 | Heading 1 | `"heading1"` |
| 4 | Heading 2 | `"heading2"` |
| 5 | Heading 3 | `"heading3"` |
| 12 | Bullet list ✅ | `"bullet"` |
| 13 | Ordered list ✅ | `"ordered"` |
| 22 | Divider | `"divider"` |

**❌ 9=heading7, 10=heading8. NOT lists!**

### Step 7: Send Notification

Send message via Lark API with doc link.

## Lessons Learned (6 real attempts)

| # | Result | Root Cause | Lesson |
|---|--------|-----------|---------|
| 1 | ❌ Self-killed | Sub-agent ran `gateway restart` | Never restart gateway in sub-agent |
| 2 | ⚠️ Wrong week | Collected Feb 10-14 instead of Feb 3-7 | Always confirm week title after pagination |
| 3 | ❌ 200K tokens burned | Tried `curl` on SPA | Reports is SPA, browser only |
| 4 | ❌ 200K tokens burned | Sub-agent explored on its own | Give exact URLs and steps |
| 5 | ✅ Success | Precise instructions + correct block_types | Template is key |

## Known Limitations

- Lark Report Open API unavailable on international version (returns 404) — browser only
- Browser login session may expire — re-login needed
- Export button (Excel) untested — potential alternative
