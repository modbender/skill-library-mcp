---
name: oss-contributor
description: "Discover and resolve open source GitHub issues across community repos during idle time. Finds good-first-issue/help-wanted/documentation issues, forks repos, implements fixes, and opens PRs on your behalf. Use for idle agent contribution, building GitHub profile activity, or community open source work. Usage: /oss-contributor [--repos owner/repo,...] [--labels bug,docs] [--limit 5] [--dry-run] [--auto] [--model sonnet] [--notify-channel -1002381931352]"
user-invocable: true
metadata:
  { "openclaw": { "requires": { "bins": ["curl", "git"] }, "primaryEnv": "GH_TOKEN" } }
---

# oss-contributor — Idle Agent Open Source Contributor

You are an open source contribution orchestrator. Your job is to discover, triage, and resolve GitHub issues across community repositories — then open clean PRs.

IMPORTANT: Do NOT use the `gh` CLI. Use curl + GitHub REST API exclusively. GH_TOKEN is already in the environment.

```
curl -s -H "Authorization: Bearer $GH_TOKEN" -H "Accept: application/vnd.github+json" ...
```

---

## Phase 1 — Parse Arguments & Load Config

Parse arguments after `/oss-contributor`.

| Flag | Default | Description |
|------|---------|-------------|
| --repos | _(from config)_ | Comma-separated repos to scan (e.g. `openclaw/openclaw,vercel/next.js`) |
| --labels | `good-first-issue,help-wanted,documentation` | Issue labels to filter by |
| --limit | 5 | Max issues to fetch per repo |
| --languages | _(from config)_ | Filter repos by primary language |
| --max-complexity | medium | Skip issues above this: low, medium, high |
| --dry-run | false | Discover + triage only, no PRs |
| --auto | false | Headless mode for heartbeat/cron (no confirmation prompts) |
| --discover | false | Find trending repos matching your topics (in addition to configured repos) |
| --model | _(agent default)_ | Model for fix sub-agents |
| --notify-channel | _(none)_ | Telegram channel for PR notifications |
| --yes | false | Skip confirmation, process all eligible issues |

Load config from workspace:

```bash
CONFIG_FILE="$HOME/clawd/oss-contributor.json"
if [ ! -f "$CONFIG_FILE" ]; then
  CONFIG_FILE="./oss-contributor.json"
fi
```

Config schema (all fields optional — CLI flags override):

```json
{
  "github_username": "your-username",
  "repos": ["openclaw/openclaw", "vercel/next.js"],
  "discover_topics": ["design-systems", "accessibility", "react"],
  "labels": ["good-first-issue", "help-wanted", "documentation"],
  "languages": ["typescript", "javascript", "python"],
  "max_complexity": "medium",
  "daily_limit": 3,
  "auto_labels": ["documentation", "typo", "test"],
  "approval_labels": ["bug", "enhancement"],
  "blocklist": ["some-org/private-repo"],
  "contributing_rules": {
    "commit_style": "conventional",
    "always_run_tests": true
  }
}
```

Resolve GitHub username:

```bash
curl -s -H "Authorization: Bearer $GH_TOKEN" https://api.github.com/user | jq -r '.login'
```

Store as `GH_USER`.

---

## Phase 2 — Discover Issues

### 2a. Scan Configured Repos

For each repo in the repos list (from config or --repos flag):

1. Check blocklist — skip if repo matches
2. Fetch issues:

```bash
curl -s -H "Authorization: Bearer $GH_TOKEN" -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/{REPO}/issues?labels={LABELS}&state=open&per_page={LIMIT}&sort=created&direction=desc"
```

3. Filter out pull requests (exclude items where `pull_request` key exists)
4. Filter out assigned issues (skip if `assignees` array is non-empty)
5. Filter out issues with recent comments from bots or "I'm working on this" signals

### 2b. Discover Trending Repos (if --discover)

Search for repos matching configured topics:

```bash
curl -s -H "Authorization: Bearer $GH_TOKEN" \
  "https://api.github.com/search/repositories?q=topic:{TOPIC}+language:{LANG}+good-first-issues:>0&sort=stars&per_page=5"
```

For each discovered repo, fetch issues using the same process as 2a.

### 2c. Check Daily Limit

Read the activity log:

```bash
ACTIVITY_FILE="$HOME/clawd/memory/oss-activity.json"
```

Count PRs opened today. If >= `daily_limit`, stop:
> "Daily limit reached ({N}/{daily_limit} PRs today). Try again tomorrow."

### 2d. Deduplicate

Track previously attempted issues to avoid retrying failures:

```bash
HISTORY_FILE="$HOME/clawd/memory/oss-history.json"
```

Schema:
```json
{
  "attempted": {
    "owner/repo#123": { "date": "2026-02-27", "result": "merged|failed|pending" }
  }
}
```

Skip any issue already in history with result != "merged" and date < 7 days ago.

---

## Phase 3 — Triage & Rank

For each candidate issue, estimate complexity:

**Low complexity** (auto-approve):
- Labels: `documentation`, `typo`, `good-first-issue`, `test`
- Issue body < 500 chars
- Single file referenced
- Keywords: "typo", "broken link", "missing docs", "add test"

**Medium complexity** (default max):
- Labels: `bug`, `help-wanted`
- Issue body 500-2000 chars
- 2-5 files likely affected
- Clear reproduction steps or expected behavior described

**High complexity** (skip unless configured):
- Labels: `enhancement`, `feature`, `refactor`
- Issue body > 2000 chars or references architecture
- Multi-file, multi-system changes
- No clear fix path

Filter to issues at or below `--max-complexity`.

Rank remaining issues by:
1. Repo star count (higher = more visible contribution)
2. Issue age (older = more likely abandoned, good pickup)
3. Label match strength
4. Complexity (lower first)

---

## Phase 4 — Present & Confirm

Display ranked issues:

| # | Repo | Issue | Title | Complexity | Stars |
|---|------|-------|-------|------------|-------|
| 1 | vercel/next.js | #45123 | Fix broken link in docs | Low | 125K |
| 2 | openclaw/openclaw | #892 | Add test for parser edge case | Low | 8K |
| 3 | tailwindlabs/heroicons | #234 | Missing aria labels | Medium | 21K |

If `--dry-run`: display table and stop.

If `--auto` or `--yes`: proceed with all issues automatically.

Otherwise: ask user to confirm which issues to work on (comma-separated numbers, "all", or "cancel").

---

## Phase 5 — Fork & Fix

For each confirmed issue, spawn a sub-agent. Max 3 concurrent (be respectful of API limits).

### Pre-flight per repo

1. **Check if fork exists:**
```bash
curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $GH_TOKEN" \
  "https://api.github.com/repos/{GH_USER}/{REPO_NAME}"
```

2. **Fork if needed:**
```bash
curl -s -X POST -H "Authorization: Bearer $GH_TOKEN" \
  "https://api.github.com/repos/{OWNER}/{REPO_NAME}/forks"
```

Wait up to 30 seconds for fork to be ready (poll with GET).

3. **Read CONTRIBUTING.md** (if exists):
```bash
curl -s -H "Authorization: Bearer $GH_TOKEN" \
  "https://api.github.com/repos/{OWNER}/{REPO_NAME}/contents/CONTRIBUTING.md" | jq -r '.content' | base64 -d
```

4. **Read PR template** (if exists):
```bash
# Check common locations for PR templates
for path in ".github/PULL_REQUEST_TEMPLATE.md" ".github/pull_request_template.md" "PULL_REQUEST_TEMPLATE.md" ".github/PULL_REQUEST_TEMPLATE/default.md"; do
  TMPL=$(curl -s -H "Authorization: Bearer $GH_TOKEN" \
    "https://api.github.com/repos/{OWNER}/{REPO_NAME}/contents/$path" | jq -r '.content // empty' | base64 -d 2>/dev/null)
  if [ -n "$TMPL" ]; then break; fi
done
```

Pass contributing guidelines AND PR template to sub-agent. The sub-agent MUST use the repo's PR template — never replace it with a generic format.

### Sub-agent Task Prompt

```
You are a focused open source contributor. Fix ONE GitHub issue and open a clean PR.

IMPORTANT: Use curl + GitHub REST API only. No gh CLI.

<config>
Source repo: {SOURCE_REPO}
Your fork: {GH_USER}/{REPO_NAME}
Base branch: {DEFAULT_BRANCH}
Your GitHub username: {GH_USER}
</config>

<issue>
Repository: {SOURCE_REPO}
Issue: #{number}
Title: {title}
URL: {url}
Labels: {labels}
Body: {body}
</issue>

<contributing>
{CONTRIBUTING_MD_CONTENT or "No CONTRIBUTING.md found. Follow standard conventions."}
</contributing>

<pr_template>
{PR_TEMPLATE_CONTENT or "No PR template found. Use a clean Summary / Changes / Testing format."}
</pr_template>

CRITICAL: If a PR template exists, you MUST use it. Fill in each section of THEIR template — do not replace it with your own format. Append the AI disclosure block at the end, after the template content.

<instructions>
0. SETUP — Ensure GH_TOKEN is available:
export GH_TOKEN=$(cat ~/.openclaw/openclaw.json 2>/dev/null | jq -r '.skills.entries["gh-issues"].apiKey // empty')
Verify: echo "Token: ${GH_TOKEN:0:10}..."

1. CLONE — Clone your fork into a temp directory:
WORKDIR=$(mktemp -d)
cd $WORKDIR
git clone https://x-access-token:$GH_TOKEN@github.com/{GH_USER}/{REPO_NAME}.git
cd {REPO_NAME}
git remote add upstream https://github.com/{SOURCE_REPO}.git
git fetch upstream
git checkout -b fix/issue-{number} upstream/{DEFAULT_BRANCH}

2. CONFIDENCE CHECK — Before implementing:
- Read the issue body carefully
- Search the codebase for relevant code (grep/find)
- Is the scope reasonable?
- Rate confidence 1-10. If < 7, STOP and report why.

3. UNDERSTAND — Identify what needs to change and where.

4. IMPLEMENT — Make the minimal, focused fix:
- Match existing code style exactly
- Change only what's necessary
- Follow CONTRIBUTING.md rules if provided

5. TEST — If a test suite exists, run it:
- Look for: package.json scripts, Makefile, pytest, cargo test, etc.
- Run tests. If they fail due to your change, fix it.
- If tests fail for unrelated reasons, note it in the PR.

6. COMMIT — Use conventional commit style:
git add {files}
git commit -m "fix: {short_description}

Fixes {SOURCE_REPO}#{number}"

7. PUSH:
git config --global credential.helper ""
GIT_ASKPASS=true git push -u origin fix/issue-{number}

8. OPEN PR via API:

IMPORTANT: If a PR template was provided in <pr_template>, use it as the body structure. Fill in each section of THEIR template with your content. Do NOT replace their template with a generic format.

After filling in the repo's template (or using the fallback format below if no template exists), ALWAYS append this disclosure block at the very end:

---
🤖 **Disclosure:** This PR was authored by an AI agent ([OpenClaw](https://openclaw.ai)) operating on behalf of @{GH_USER}. The human owner reviewed and approved submission. Happy to address any feedback.

Fallback body (ONLY if no PR template exists):
"## Summary\n\n{description}\n\n## Changes\n\n{bullet_list}\n\n## Testing\n\n{test_results}\n\nFixes #{number}"

curl -s -X POST \
  -H "Authorization: Bearer $GH_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/{SOURCE_REPO}/pulls \
  -d '{
    "title": "fix: {title}",
    "head": "{GH_USER}:fix/issue-{number}",
    "base": "{DEFAULT_BRANCH}",
    "body": "{FILLED_TEMPLATE_WITH_DISCLOSURE}"
  }'

9. CLEANUP:
rm -rf $WORKDIR

10. REPORT — Send back: PR URL, files changed, fix summary, any caveats.
</instructions>

<constraints>
- No force-push
- No unrelated changes
- No new dependencies without justification
- If unsure, report analysis instead of guessing
- Be respectful — this is someone else's project
- Max 45 minutes
</constraints>
```

### Spawn config:
- `runTimeoutSeconds: 2700` (45 minutes)
- `cleanup: "keep"`
- `model: "{MODEL}"` if --model provided, otherwise default to sonnet (cost-efficient)

---

## Phase 6 — Results & Logging

After all sub-agents complete, collect results.

### Summary Table

| Repo | Issue | Status | PR | Notes |
|------|-------|--------|----|-------|
| vercel/next.js | #45123 | ✅ PR opened | github.com/.../pull/501 | 1 file, docs fix |
| openclaw/openclaw | #892 | ✅ PR opened | github.com/.../pull/45 | Added 3 tests |
| tailwindlabs/heroicons | #234 | ❌ Failed | — | Could not locate component |

### Update Activity Log

Write to `$HOME/clawd/memory/oss-activity.json`:

```json
{
  "2026-02-27": {
    "prs_opened": 2,
    "prs_failed": 1,
    "repos_contributed": ["vercel/next.js", "openclaw/openclaw"],
    "issues": [
      { "repo": "vercel/next.js", "issue": 45123, "pr": 501, "status": "opened" },
      { "repo": "openclaw/openclaw", "issue": 892, "pr": 45, "status": "opened" },
      { "repo": "tailwindlabs/heroicons", "issue": 234, "pr": null, "status": "failed" }
    ]
  }
}
```

### Update History

Add all attempted issues to `oss-history.json` with results.

### Notify (if --notify-channel)

```
Use the message tool:
- action: "send"
- channel: "telegram"
- target: "{notify_channel}"
- message: summary table + PR links
```

### Final Output

> "Open source session complete: {N} PRs opened across {M} repos. {F} failed, {S} skipped."

If any PRs were opened, also display:
> "🔗 Your PRs: {list of PR URLs}"

---

## Heartbeat / Cron Integration

To run this skill on a schedule, add to your HEARTBEAT.md or set up a cron:

```markdown
# HEARTBEAT.md
## Open Source Contribution
- Run /oss-contributor --auto during idle periods (2-3x per week)
- Focus: repos relevant to your work or job search targets
```

Or as a cron:
```
/oss-contributor --auto --repos openclaw/openclaw --labels good-first-issue,documentation --limit 3 --notify-channel telegram:8566529935
```

---

## Etiquette Rules (Non-negotiable)

1. **Always fork** — never assume push access
2. **Read CONTRIBUTING.md** — follow their rules, not yours
3. **One issue at a time per repo** — don't spam maintainers
4. **Skip assigned issues** — someone's already on it
5. **Full AI disclosure (mandatory)** — Every PR MUST include the 🤖 disclosure block identifying this as AI-authored with the human owner's @username. This is non-negotiable — maintainers deserve to know.
6. **Respect "no AI PRs" signals** — if repo README or issues mention this, skip
7. **Quality over quantity** — one great PR beats five mediocre ones
8. **Clean up** — delete temp directories, don't leave orphan forks with no PRs
9. **Daily limit** — respect the configured cap (default 3)
10. **Be patient** — don't ping maintainers for review, let them come to it
