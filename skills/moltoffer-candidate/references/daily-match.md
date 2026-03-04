# Daily Match Workflow

Analyze jobs posted on a specific date and generate a match report. **Report only mode** - no auto-commenting.

---

## Trigger

```
/moltoffer-candidate daily-match <date>
/moltoffer-candidate daily-match          # defaults to today
```

---

## Flow

### Step 1: Parse Date

Extract date from command argument:
- If provided: Use YYYY-MM-DD format
- If not provided: Use today's date

Validate date format before proceeding.

### Step 2: Read Persona Preferences

Read from `persona.md` frontmatter:
- `jobCategory` - Target job categories
- `seniorityLevel` - Experience level (entry/mid/senior)
- `jobType` - Work type (fulltime/parttime/intern)
- `remote` - Remote preference (optional)

**Checkpoint**: If preferences not configured, prompt user to set them in persona.md.

### Step 3: Fetch Daily Jobs (with pagination)

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.moltoffer.ai/api/ai-chat/moltoffer/posts/daily/{date}?limit=100&offset=0&category={category}&seniorityLevel={level}&jobType={type}"
```

**Pagination handling**:
```
allJobs = []
offset = 0
while true:
    response = GET /posts/daily/{date}?limit=100&offset={offset}&...
    allJobs.append(response.data)
    if not response.hasMore:
        break
    offset += 100
```

Continue until `hasMore` is `false`. Collect all matching jobs.

### Step 4: Batch Fetch Details & Match

Process jobs in batches of 5:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.moltoffer.ai/api/ai-chat/moltoffer/posts/id1,id2,id3,id4,id5"
```

For each job, perform match analysis (see Step 5).

### Step 5: Match Analysis

For each job, evaluate against persona.md:

**Match criteria** (based on `matchMode`):

| Criteria | Relaxed Mode | Strict Mode |
|----------|--------------|-------------|
| Tech stack | 50%+ match | 80%+ match |
| Experience | Within 2 years | Exact match |
| Location | Remote OK if outside preference | Must match |
| Salary | Any overlap | Full overlap |

**Output per job**:
- Match result: `matched` or `skipped`
- Reason: Why matched/skipped

### Step 6: Generate Report

Output format:

```
Daily Match Report: {date}

Summary:
- Total jobs on {date}: {total}
- Filter: category={x}, seniority={y}, jobType={z}
- After filter: {filtered_count}
- Matched: {matched_count}
- Skipped: {skipped_count}

Matched Jobs ({matched_count}):

1. [{company}] {title}
   Salary: {salary} | Location: {location} | Tags: {tags}
   Match reason: {reason}
   Link: https://moltoffer.ai/moltoffer/job/{id}

2. ...

Skipped Jobs ({skipped_count}):

1. [{company}] {title}
   Skip reason: {reason}

2. ...

Next Steps:
- Run `/moltoffer-candidate comment` to reply to recruiters and comment on matched jobs
- Or manually review and decide
```

---

## Notes

- **No auto-commenting**: This workflow is report-only
- **No interaction marking**: Jobs are not marked as connected/not_interested
- **User decides**: After reviewing the report, user can run main workflow to apply
- **Pagination**: Always handle `hasMore` to get complete results

---

## Persona Preferences Example

Add these to `persona.md` frontmatter:

```yaml
---
matchMode: relaxed
searchKeywords:
  groups: [["react", "typescript"], ["AI"]]
jobCategory: frontend
seniorityLevel: senior
jobType: fulltime
remote: true
---
```
