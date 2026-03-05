# GitHub API Cheatsheet (Repo chat ops)

## Shared curl flags
```bash
BASE="https://api.github.com"
OWNER="<owner>"
REPO="<repo>"
AUTH=(-H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github+json")
```

## Repo metadata
```bash
curl "${BASE}/repos/${OWNER}/${REPO}" "${AUTH[@]}"
```
Useful fields: `default_branch`, `archived`, `open_issues_count`, `pushed_at`.

## Commits (activity summaries)
```bash
SINCE="2025-12-01T00:00:00Z"
UNTIL="2025-12-08T00:00:00Z"
curl "${BASE}/repos/${OWNER}/${REPO}/commits?since=${SINCE}&until=${UNTIL}" "${AUTH[@]}" > /tmp/commits.json
```
- Use `jq '.[].commit.author | {name, email, date}'` for quick timelines.
- Add `author=username` to focus on one contributor.
- Paginate with `?per_page=100&page=2` for long ranges.

## Issues & PRs
List everything changed recently:
```bash
curl "${BASE}/repos/${OWNER}/${REPO}/issues?state=all&since=${SINCE}&per_page=100" "${AUTH[@]}" > /tmp/issues.json
```
- Presence of `pull_request` key marks PRs.
- Filter just issues: `jq '.[] | select(.pull_request | not)'`.

## Create an issue
```bash
cat <<'JSON' > /tmp/new-issue.json
{
  "title": "Investigate payment webhook timeouts",
  "body": "Summary...",
  "labels": ["bug", "priority:high"],
  "assignees": ["octocat"]
}
JSON
curl -X POST "${BASE}/repos/${OWNER}/${REPO}/issues" \
     "${AUTH[@]}" \
     -H "Content-Type: application/json" \
     --data @/tmp/new-issue.json
```
Capture the returned `html_url` to share with the user.

## Update an issue
```bash
ISSUE=42
curl -X PATCH "${BASE}/repos/${OWNER}/${REPO}/issues/${ISSUE}" \
     "${AUTH[@]}" \
     -H "Content-Type: application/json" \
     -d '{"state": "closed", "assignees": ["octocat"]}'
```

## Comment on an issue / PR
```bash
curl -X POST "${BASE}/repos/${OWNER}/${REPO}/issues/${ISSUE}/comments" \
     "${AUTH[@]}" \
     -H "Content-Type: application/json" \
     -d '{"body": "Follow-up note"}'
```

## Browse repo contents (no clone)
List files in a directory:
```bash
PATH="src"
curl "${BASE}/repos/${OWNER}/${REPO}/contents/${PATH}?ref=main" "${AUTH[@]}"
```
Fetch raw file contents:
```bash
FILE="src/app.py"
curl -H "Accept: application/vnd.github.raw" \
     "${BASE}/repos/${OWNER}/${REPO}/contents/${FILE}?ref=main" \
     "${AUTH[@]}" > /tmp/app.py
```
Whole-tree snapshot (limit 20k entries):
```bash
curl "${BASE}/repos/${OWNER}/${REPO}/git/trees/$(git rev-parse HEAD)?recursive=1" "${AUTH[@]}"
```

## Per-commit diff summaries
```bash
SHA="a251e65"
curl "${BASE}/repos/${OWNER}/${REPO}/commits/${SHA}" "${AUTH[@]}" > /tmp/commit.json
```
`files[]` contains filename, additions, deletions, and patch; use it to describe what actually changed.

## Tips
- 408 WhatsApp disconnects are unrelated to GitHub; just re-ask for tokens if the chat reconnects.
- When summarizing activity, convert timestamps to Africa/Lagos: `date -j -f "%Y-%m-%dT%H:%M:%SZ" ...` on macOS or use Python.
- Always `unset GITHUB_TOKEN` after finishing: `unset GITHUB_TOKEN && history -d $((HISTCMD-1))` if needed.
