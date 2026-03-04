# PR Template

Use this template when creating PRs via the GitHub API.

## Title Format
```
<type>: <short description>
```
Types: `feat`, `fix`, `chore`, `refactor`, `docs`, `style`, `test`

## Body Template

```markdown
## What
<1-2 sentence summary of what this PR does>

## Why
<Link to MC task or brief context on why this change is needed>

## Changes
- <bullet list of key changes, grouped by file/area>

## Testing
- <How was this tested? Manual steps, commands run, etc.>

## Notes
- <Any decisions made, trade-offs, or things the reviewer should know>
- <Dependencies or follow-up work needed>
```

## Example API Call

```bash
curl -s -X POST "https://api.github.com/repos/${OWNER}/${REPO}/pulls" \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "feat: Add toast notifications for user feedback",
    "body": "## What\nAdds sonner toast notifications across the app.\n\n## Why\nUsers had no feedback when saving settings or creating resources.\n\n## Changes\n- Added sonner dependency\n- Global Toaster in root layout\n- Success/error toasts on all CRUD operations\n\n## Testing\n- Tested create/update/delete flows for agents, tasks, triggers\n- Verified toasts auto-dismiss after 3s",
    "head": "task/abc123",
    "base": "main"
  }'
```
