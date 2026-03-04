# Skill Registry URLs

## ClawHub

**Base URL:** `https://clawhub.com`

### Endpoints

- **Search API:** `https://clawhub.com/api/skills/search?q=<query>&limit=<n>`
- **Skill Detail:** `https://clawhub.com/api/skills/<skill-name>`
- **Skill Manifest:** `https://clawhub.com/api/skills/<skill-name>/manifest`
- **Raw SKILL.md:** Varies by repo (check skill metadata for source URL)

### CLI Commands

```bash
# Search
clawhub search "<query>" --limit <n>

# Get skill info
clawhub install <skill-name> --dry-run

# List installed
clawhub list
```

## GitHub

**Base URL:** `https://github.com`

### Search Patterns

- **Code Search:** `https://github.com/search?q=SKILL.md+openclaw&type=code`
- **Repo Search:** `https://github.com/search?q=openclaw-skill+in:name&type=repositories`

### Raw File URLs

```
https://raw.githubusercontent.com/<owner>/<repo>/<branch>/SKILL.md
https://raw.githubusercontent.com/<owner>/<repo>/<branch>/scripts/<script>.py
https://raw.githubusercontent.com/<owner>/<repo>/<branch>/references/<file>.md
```

### GitHub CLI

```bash
# Search repos
gh search repos --language=markdown "openclaw skill"

# Search code
gh search code "SKILL.md" --language=markdown

# View repo
gh repo view <owner>/<repo>
```

## Awesome Lists

- **Awesome OpenClaw:** `https://raw.githubusercontent.com/openclaw/awesome-openclaw/main/README.md`
- **Community Skills:** Check ClawHub search for community-curated lists

## Known Skill Repositories

| Repository | Type | Notes |
|------------|------|-------|
| `openclaw/openclaw` | Core | Official OpenClaw skills |
| `clawhub/registry` | Registry | ClawHub public skills |
| Community repos | Various | Search via ClawHub |

## Rate Limits

- **ClawHub:** No documented limits (be reasonable)
- **GitHub API:** 60 requests/hour unauthenticated, 5000/hour with token
- **Raw GitHub:** Higher limits but don't abuse

## Authentication

- **ClawHub:** Not required for read/search
- **GitHub:** Token optional for public repos (use `gh auth login` for higher limits)
