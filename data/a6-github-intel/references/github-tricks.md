# GitHub URL Tricks & API Shortcuts

## Raw File Access (No Token Needed)

```
# Raw file content (any branch)
https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}

# Raw file via API
https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}

# Raw from specific commit
https://raw.githubusercontent.com/{owner}/{repo}/{commit_sha}/{path}

# Download entire repo as zip
https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip
https://github.com/{owner}/{repo}/archive/refs/tags/{tag}.tar.gz

# Download single file via codeload
https://codeload.github.com/{owner}/{repo}/tar.gz/refs/heads/{branch}
```

## API Endpoints (No Token — 60 req/hr)

```bash
# Repo metadata
curl https://api.github.com/repos/{owner}/{repo}

# File tree (recursive)
curl "https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"

# README content
curl -H "Accept: application/vnd.github.raw" https://api.github.com/repos/{owner}/{repo}/readme

# Language breakdown
curl https://api.github.com/repos/{owner}/{repo}/languages

# Recent commits
curl https://api.github.com/repos/{owner}/{repo}/commits?per_page=10

# Tags/releases
curl https://api.github.com/repos/{owner}/{repo}/tags
curl https://api.github.com/repos/{owner}/{repo}/releases/latest

# Contributors
curl https://api.github.com/repos/{owner}/{repo}/contributors

# File content (base64 encoded)
curl https://api.github.com/repos/{owner}/{repo}/contents/{path}

# Search code in repo (needs token for private, works for public)
curl "https://api.github.com/search/code?q=filename:Dockerfile+repo:{owner}/{repo}"

# Repo topics
curl -H "Accept: application/vnd.github.mercy-preview+json" https://api.github.com/repos/{owner}/{repo}/topics
```

## GitHub Search Tricks (Web & API)

```
# Find repos by topic/language
https://github.com/search?q=language:python+topic:ai&type=repositories

# Search code across all of GitHub
https://github.com/search?q=GOOGLE_AI_API_KEY+language:python&type=code

# Find files by name
https://github.com/search?q=filename:docker-compose.yml+repo:{owner}/{repo}&type=code

# Advanced: stars, forks, pushed date
https://github.com/search?q=stars:>1000+language:rust+pushed:>2025-01-01&type=repositories

# API search
curl "https://api.github.com/search/repositories?q=stars:>10000+language:python&sort=stars&per_page=10"
```

## URL Navigation Hacks

```
# Compare branches/tags
https://github.com/{owner}/{repo}/compare/{base}...{head}

# Blame a file
https://github.com/{owner}/{repo}/blame/{branch}/{path}

# File history
https://github.com/{owner}/{repo}/commits/{branch}/{path}

# View file at specific commit
https://github.com/{owner}/{repo}/blob/{commit_sha}/{path}

# Permalink to line range
https://github.com/{owner}/{repo}/blob/{branch}/{path}#L10-L20

# View rendered markdown
https://github.com/{owner}/{repo}/blob/{branch}/docs/guide.md

# Network/fork graph
https://github.com/{owner}/{repo}/network

# Dependency graph
https://github.com/{owner}/{repo}/network/dependencies

# .patch and .diff for any commit/PR
https://github.com/{owner}/{repo}/commit/{sha}.patch
https://github.com/{owner}/{repo}/pull/{number}.diff
```

## Shortcut URLs

```
# User's repos (sorted by stars)
https://github.com/{user}?tab=repositories&sort=stargazers

# Organization members
https://github.com/orgs/{org}/people

# Repo traffic (owner only)
https://github.com/{owner}/{repo}/graphs/traffic

# GitHub1s (VS Code in browser, third-party)
https://github1s.com/{owner}/{repo}

# Gitpod (instant dev environment, third-party)
https://gitpod.io/#https://github.com/{owner}/{repo}
```

## Rate Limits

| Method | Limit |
|--------|-------|
| Unauthenticated | 60 requests/hour |
| With token | 5,000 requests/hour |
| GitHub App | 5,000+ requests/hour |
| Search API | 10 requests/min (unauth), 30/min (auth) |

## Tips

- **Add `.json` to any GitHub page URL** — doesn't work, but the API equivalent usually does
- **raw.githubusercontent.com** is CDN-cached and fast, no rate limit concerns
- **Use `If-None-Match` header** with ETags to avoid burning rate limit on unchanged data
- **GitHub's tree API with `recursive=1`** returns the entire repo structure in one call
- **`/contents/` endpoint** returns base64-encoded file content + metadata in one call
- **For large files**, use the Git Blobs API: `GET /repos/{owner}/{repo}/git/blobs/{sha}`
