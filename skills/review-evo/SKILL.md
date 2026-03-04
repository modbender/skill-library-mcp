---
name: review-evo
description: Self-improving code reviewer that learns your codebase over time. Analyzes git history, spots patterns, identifies risk — and gets smarter every run.
homepage: https://github.com/8co/review-evo
metadata: {"clawdbot":{"emoji":"🔍","requires":{"bins":["git"]}}}
---

# ReviewEvo

A self-improving code reviewer. It analyzes your git history, identifies risk hotspots, learns your team's conventions, and builds a persistent knowledge base that sharpens every review.

**No external services. No API keys. No dependencies.** It uses git and the agent's built-in tools — nothing else.

**Follow these steps in order.** Complete each step fully before moving to the next.

## Prerequisites

Verify git is available:

- Run `git --version` and confirm output

The user must be inside a git repository with at least 20 commits of history. Run `git rev-list --count HEAD` to confirm. If fewer than 20 commits, warn the user that analysis will be limited but can still proceed.

## Step 1 — Detect Project and Load Prior Learnings

Check if this project has been reviewed before:

```
ls .review-evo/learnings.md 2>/dev/null
```

**If the file exists:** Read `.review-evo/learnings.md` in full. This contains findings from prior runs. Reference these throughout the review — confirm resolved issues, track recurring patterns, and build on previous analysis. Tell the user: "I found learnings from a previous review. I'll build on those."

**If the file does not exist:** This is a first run. Tell the user you'll create the knowledge base after analysis.

Then detect the project setup by checking for these files in the repo root:

- `tsconfig.json` → TypeScript
- `package.json` → Node.js (read `scripts` for build/test/lint commands)
- `requirements.txt` or `pyproject.toml` → Python
- `go.mod` → Go
- `Cargo.toml` → Rust
- `pom.xml` or `build.gradle` → Java

Report what you found and confirm with the user.

## Step 2 — Analyze Git History

Run each of these commands and capture the output. Do not summarize prematurely — collect all data before drawing conclusions.

**Recent activity (last 50 commits):**
```
git log --oneline -50
```

**Contributor breakdown:**
```
git log --since="6 months ago" --format="%an" | sort | uniq -c | sort -rn
```

**High-churn files (most frequently modified):**
```
git log --since="3 months ago" --diff-filter=M --name-only --pretty=format: | sort | uniq -c | sort -rn | head -25
```

**Large recent diffs (potential complexity bombs):**
```
git log --since="1 month ago" --pretty=format:"%h %s" --shortstat | head -60
```

**Files with the most authors (knowledge-spread risk):**
```
git log --since="6 months ago" --pretty=format:"%an" --name-only | awk '/^$/{next} !author{author=$0;next} {files[author][$0]++; allfiles[$0]++} END{for(f in allfiles) {n=0; for(a in files) if(f in files[a]) n++; if(n>1) print n,f}}' | sort -rn | head -15
```

If the awk command fails on the platform, fall back to:
```
git log --since="6 months ago" --format="%an" --name-only | head -200
```
and manually count distinct authors per file from the output.

## Step 3 — Build Review Profile

Using the data from Step 2, analyze and report on each of these dimensions:

### Churn Hotspots
Files modified more than 5 times in 3 months are hotspots. For each one:
- Read the file
- Assess complexity (function count, nesting depth, line count)
- Flag if it lacks corresponding test coverage (look for matching `*.test.*`, `*.spec.*`, or `test_*` files)

### Convention Patterns
From the recent commits and file contents, identify:
- Naming conventions (camelCase, snake_case, kebab-case for files)
- Import patterns (relative vs absolute, barrel files)
- Error handling patterns (try/catch, Result types, error callbacks)
- Comment density and style

### Risk Indicators
Flag any of these:
- Files over 400 lines with no tests
- Functions over 50 lines
- TODOs or FIXMEs older than 30 days (check `git log -1 --format=%cr` on lines containing them)
- Dependencies with known issues (check lock file age)
- Single-author files in critical paths (bus factor risk)

### Strengths
Also identify what the codebase does well:
- Consistent patterns
- Good test coverage areas
- Clean separation of concerns
- Recent improvements visible in git history

## Step 4 — Deliver the Review

Ask the user what they want reviewed:

> What would you like me to focus on?
> **(a)** Full codebase health report
> **(b)** A specific branch or PR diff (provide branch name)
> **(c)** Current working changes (`git diff`)
> **(d)** A specific file or directory

### For option (a) — Full Health Report
Compile all findings from Step 3 into a structured report with sections: Hotspots, Risks, Conventions, Strengths, and Recommendations. Rank findings by severity (critical, warning, info).

### For option (b) — Branch/PR Review
Run `git diff main...{branch}` (or the appropriate target branch). Analyze the diff through the lens of the patterns found in Step 3. Flag deviations from conventions, new risk introductions, and missing test coverage for changed code.

### For option (c) — Working Changes
Run `git diff` and `git diff --cached`. Apply the same analysis as option (b).

### For option (d) — Targeted Review
Read the specified files. Analyze against the patterns and conventions discovered. Provide focused, actionable feedback.

For all options, structure each finding as:
- **What:** The specific issue or observation
- **Where:** File and line range
- **Why it matters:** Impact on maintainability, reliability, or security
- **Suggestion:** Concrete fix or improvement

## Step 5 — Store Learnings

After delivering the review, persist findings for future runs.

Create the directory if it doesn't exist:
```
mkdir -p .review-evo
```

Write (or append to) `.review-evo/learnings.md` with the following structure:

```markdown
## Review — {YYYY-MM-DD}

### Project Profile
- Language: {detected}
- Key patterns: {conventions found}
- Active contributors: {count}

### Hotspots
{list of high-churn files with context}

### Recurring Patterns
{patterns that appeared in this and prior reviews}

### Resolved
{items from prior reviews that are no longer flagged}

### Open Risks
{current findings ranked by severity}
```

If the file already exists, append the new review section. Do not overwrite prior entries — the history is the value.

Tell the user: "Learnings saved. Next time I review this project, I'll build on these findings."

Also recommend adding `.review-evo/` to the project's `.gitignore` if it's not already there — these are local analysis artifacts, not source code.

## Troubleshooting

- **"Not a git repository"** — Run the skill from inside a git repo, or provide the path to one.
- **awk command fails** — Some platforms have limited awk. The skill includes fallback commands for each analysis step.
- **Very large repos (10K+ commits)** — The `--since` flags keep queries bounded. If commands are still slow, narrow the date range.
- **Monorepo** — Ask the user which subdirectory to focus on and scope all git commands with `-- {path}`.
