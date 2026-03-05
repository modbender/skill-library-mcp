# glab api - Advanced API Access

> ⚠️ **Security Warning**: This command provides unrestricted GitLab API access with your authenticated token. A compromised or overly-permissive token can delete projects, modify settings, expose secrets, and perform other destructive operations.

## Token Scope Recommendations

| Scope | Access Level | Use Case |
|-------|--------------|----------|
| `read_api` | Read-only | Viewing projects, issues, MRs |
| `api` | Full read/write | Creating/updating/deleting resources |
| `sudo` | Admin actions | Only for admin tasks (avoid if possible) |

**Best practice:** Use `read_api` scope tokens for read-only operations. Only use `api` scope when write operations are required.

## Basic Usage

```bash
# GET request
glab api projects/:id/merge_requests

# With pagination (use query params, NOT flags)
glab api "projects/:id/merge_requests?per_page=100&state=opened"

# Auto-fetch all pages
glab api --paginate "projects/:id/jobs?per_page=100"
```

## POST/PUT/DELETE Requests

```bash
# POST with data
glab api --method POST projects/:id/issues \
  --field title="Bug" \
  --field description="Details"

# PUT (update)
glab api --method PUT projects/:id/issues/123 \
  --field state_event="close"

# DELETE
glab api --method DELETE projects/:id/issues/123
```

## Common Patterns

### List Unresolved MR Comments

```bash
glab api "projects/:id/merge_requests/{mr}/discussions?per_page=100" | \
  jq '[.[] | select(.notes[0].resolvable == true and .notes[0].resolved == false) | \
  {id: .notes[0].id, body: .notes[0].body[0:100], path: .notes[0].position.new_path}]'
```

### Reply to Discussion Threads

`glab mr note` creates standalone comments. To reply within a thread:

```bash
# 1. Find the discussion_id containing the note
glab api "projects/:id/merge_requests/{mr}/discussions" | \
  jq '.[] | select(.notes[].id == {note_id}) | .id'

# 2. Post reply to the discussion thread
glab api --method POST \
  "projects/:id/merge_requests/{mr}/discussions/{discussion_id}/notes" \
  --field body="Your reply"
```

### Get Pipeline Jobs

```bash
glab api --paginate "projects/:id/pipelines/{pipeline_id}/jobs?per_page=100"
```

### Trigger Pipeline

```bash
glab api --method POST projects/:id/pipeline \
  --field ref="main"
```

## Safety Patterns

1. **Dry-run first**: Use GET to verify before POST/PUT/DELETE
2. **Limit scope**: Use project-level tokens instead of personal tokens when possible
3. **Audit trail**: GitLab logs API calls - review activity periodically
4. **Rate limiting**: GitLab has API rate limits; use `--paginate` for large datasets

## Error Handling

```bash
# Check response status
glab api projects/:id/merge_requests 2>&1 | head -1

# Handle errors in scripts
if ! glab api projects/:id >/dev/null 2>&1; then
  echo "API call failed"
  exit 1
fi
```

## API Documentation

- [GitLab REST API](https://docs.gitlab.com/ee/api/)
- [glab api docs](https://docs.gitlab.com/editor_extensions/gitlab_cli/)
