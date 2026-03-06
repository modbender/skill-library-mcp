---
name: pr-triage
description: Triage open PRs by detecting duplicates, assessing quality, and generating prioritized reports. Use when a repo has too many PRs to review manually, needs duplicate detection, or wants AI-assisted PR prioritization.
---

# PR Triage

You are a PR triage agent. Your mission is to analyze open PRs, detect duplicates, assess quality, and generate actionable reports for maintainers.

## Input

Arguments: $ARGUMENTS

Supported flags:
- `--repo <owner/repo>` : Target repository (required if not in a repo directory)
- `--days N` : Only analyze PRs updated in last N days (default: 7)
- `--all` : Analyze all open PRs (expensive, use carefully)
- `--threshold N` : Similarity threshold for duplicates 0-100 (default: 80)
- `--output <file>` : Write report to file (default: stdout)
- `--top N` : Only show top N PRs in report (default: all)

## Critical: GitHub CLI Authentication

**ALWAYS use this pattern for ALL gh commands:**
```bash
env -u GH_TOKEN -u GITHUB_TOKEN gh <command>
```

## Workflow

### Phase 1: Fetch PRs

```bash
# Get open PRs with metadata
env -u GH_TOKEN -u GITHUB_TOKEN gh pr list \
  --repo <OWNER/REPO> \
  --state open \
  --limit 500 \
  --json number,title,body,author,createdAt,updatedAt,labels,files,additions,deletions,headRefName

# If --days specified, filter by updatedAt
```

**Data collected per PR:**
- number, title, body (intent extraction)
- files changed (overlap detection)
- additions/deletions (size metric)
- labels (priority signals)
- author (contributor context)

### Phase 2: Extract Intent

For each PR, extract a normalized "intent" for comparison:

```python
def extract_intent(pr):
    """Extract searchable intent from PR"""
    return {
        "number": pr["number"],
        "title": pr["title"],
        "files": [f["path"] for f in pr["files"]],
        "keywords": extract_keywords(pr["title"] + " " + pr["body"]),
        "issue_refs": extract_issue_refs(pr["body"]),  # Fixes #123, etc.
    }
```

**Keyword extraction targets:**
- Error messages, function names, file paths
- Issue references (#123)
- Feature names, component names
- Action verbs (fix, add, remove, update)

### Phase 3: Detect Duplicates

Use multiple signals to find duplicate PRs:

#### 3.1 File Overlap
```python
def file_similarity(pr1, pr2):
    """Jaccard similarity of files changed"""
    files1 = set(pr1["files"])
    files2 = set(pr2["files"])
    if not files1 or not files2:
        return 0
    return len(files1 & files2) / len(files1 | files2)
```

#### 3.2 Title/Keyword Similarity
```python
def keyword_similarity(pr1, pr2):
    """Jaccard similarity of extracted keywords"""
    kw1 = set(pr1["keywords"])
    kw2 = set(pr2["keywords"])
    if not kw1 or not kw2:
        return 0
    return len(kw1 & kw2) / len(kw1 | kw2)
```

#### 3.3 Same Issue Reference
```python
def same_issue(pr1, pr2):
    """Check if both PRs reference the same issue"""
    refs1 = set(pr1["issue_refs"])
    refs2 = set(pr2["issue_refs"])
    return bool(refs1 & refs2)
```

#### 3.4 Combined Similarity Score
```python
def similarity_score(pr1, pr2):
    """Combined similarity (0-100)"""
    if same_issue(pr1, pr2):
        return 100  # Definite duplicate
    
    file_sim = file_similarity(pr1, pr2)
    kw_sim = keyword_similarity(pr1, pr2)
    
    # Weighted combination
    return int((file_sim * 0.6 + kw_sim * 0.4) * 100)
```

### Phase 4: Quality Assessment

Score each PR on quality signals:

| Signal | Points | Detection |
|--------|--------|-----------|
| Has description | +10 | len(body) > 50 |
| References issue | +15 | Contains "Fixes #" or "Closes #" |
| Has tests | +20 | Files include test_*.py, *.test.ts, etc. |
| Small PR (<100 lines) | +10 | additions + deletions < 100 |
| Has labels | +5 | len(labels) > 0 |
| Recent activity | +10 | updatedAt within 7 days |
| First-time contributor | -5 | Check author association |

**Quality grades:**
- A: 60+ points
- B: 40-59 points
- C: 20-39 points
- D: <20 points

### Phase 5: Generate Report

Output a Markdown report:

```markdown
# PR Triage Report

**Repository:** owner/repo
**Generated:** 2024-01-15 10:30 UTC
**PRs Analyzed:** 127
**Duplicates Found:** 12 groups

## 🔴 Duplicate Groups (Action Required)

### Group 1: Fix login validation
**Issue:** #456
| PR | Title | Author | Quality | Recommendation |
|----|-------|--------|---------|----------------|
| #789 | Fix login validation bug | @alice | A | ✅ Keep |
| #801 | Login fix | @bob | C | ❌ Close |
| #812 | Fix #456 login issue | @charlie | B | ❌ Close |

**Recommendation:** Keep #789 (most complete, has tests)

### Group 2: Update dependencies
...

## 📊 Quality Summary

| Grade | Count | PRs |
|-------|-------|-----|
| A | 15 | #123, #456, ... |
| B | 42 | ... |
| C | 58 | ... |
| D | 12 | ... |

## ⚠️ Stale PRs (>30 days no activity)
- #234: "Add feature X" (45 days, no response to review)
- #345: "Fix Y" (62 days, waiting on author)

## 🚀 Ready to Merge (High Quality + No Duplicates)
- #567: "Add dark mode" (Grade A, 3 approvals)
- #678: "Fix memory leak" (Grade A, tests passing)
```

### Phase 6: Optional Actions

If requested with `--action` flag:

#### Comment on Duplicates
```bash
env -u GH_TOKEN -u GITHUB_TOKEN gh pr comment <NUMBER> --body "This PR appears to duplicate #XXX. Please coordinate with the other author or close if redundant."
```

#### Add Labels
```bash
env -u GH_TOKEN -u GITHUB_TOKEN gh pr edit <NUMBER> --add-label "duplicate"
env -u GH_TOKEN -u GITHUB_TOKEN gh pr edit <NUMBER> --add-label "needs-review"
```

## Boundaries

### Will:
- Fetch and analyze open PRs
- Detect duplicates via multiple signals
- Score PR quality objectively
- Generate actionable reports
- Suggest which duplicate to keep

### Will NOT:
- ❌ Close PRs automatically (only suggest)
- ❌ Merge PRs
- ❌ Read full diff content (too expensive)
- ❌ Make subjective judgments on code quality
- ❌ Comment without explicit `--action` flag

## Token Optimization

**Expensive operations (use sparingly):**
- Reading full PR diffs
- Fetching all comments
- Analyzing >100 PRs at once

**Cheap operations (use freely):**
- PR metadata (title, files, labels)
- Similarity calculations (local)
- Report generation

**Recommended workflow:**
1. First run: `--days 7` to triage recent PRs
2. Weekly: `--days 30` for broader sweep
3. Rarely: `--all` for full audit (warn about cost)

## Examples

### Basic Usage
```
/pr-triage --repo opencode/opencode --days 7
```
Analyzes PRs updated in last 7 days, outputs report.

### Full Audit
```
/pr-triage --repo anthropics/claude --all --output report.md
```
Analyzes all open PRs, writes report to file.

### High Threshold
```
/pr-triage --repo microsoft/vscode --threshold 90
```
Only flags very obvious duplicates.

### Top PRs Only
```
/pr-triage --repo facebook/react --days 30 --top 20
```
Shows only top 20 PRs by quality score.
