# GitHub via TapAuth

## Available Scopes

| Scope | Access |
|-------|--------|
| `repo` | Full repository access (read/write code, issues, PRs) |
| `repo:status` | Commit statuses |
| `public_repo` | Public repositories only |
| `read:user` | Read user profile |
| `user:email` | Read user email addresses |
| `read:org` | Read org membership |
| `gist` | Create and read gists |
| `notifications` | Read notifications |
| `workflow` | GitHub Actions workflows |
| `write:packages` | Publish packages |
| `delete_repo` | Delete repositories (use with extreme caution) |

## Example: Read a User's Repos

```bash
# 1. Get a token with repo scope
./scripts/tapauth.sh github "repo,read:user" "Repo Browser"

# 2. Use the token
curl -H "Authorization: Bearer <token>" \
  https://api.github.com/user/repos
```

## Example: Create an Issue

```bash
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/OWNER/REPO/issues \
  -d '{"title": "Bug report", "body": "Description here"}'
```

## Gotchas

- **Token type:** GitHub returns a user OAuth token (`gho_...`). It acts on behalf of the user.
- **Rate limits:** 5,000 requests/hour for authenticated requests. Check `X-RateLimit-Remaining` header.
- **Scope reduction:** Users can approve with fewer scopes than requested. Always check the `scope` field in the token response.
- **Fine-grained tokens:** TapAuth uses classic OAuth tokens, not fine-grained PATs. Scope semantics follow GitHub's classic OAuth model.
- **Expiry:** GitHub OAuth tokens don't expire unless the user revokes them or the OAuth app is suspended.

## Recommended Minimum Scopes

| Use Case | Scopes |
|----------|--------|
| Read repos | `public_repo` or `repo` |
| Manage issues/PRs | `repo` |
| Read profile only | `read:user` |
| CI/CD actions | `repo`, `workflow` |
