# OpenClaw GitHub Skill

A skill that lets your AI assistant query and manage GitHub repositories.

## Features

- 📋 **List Repos** — View your repositories with filters
- 📊 **Get Repo Details** — Stars, forks, language, last updated
- 🔄 **Check CI Status** — Monitor CI/CD pipelines
- 📝 **Create Issues** — Open issues from conversation
- 📁 **Create Repos** — Create new repositories
- 🔍 **Search Repos** — Find repos by name/query
- 📊 **Recent Activity** — View recent commits

## Prerequisites

- OpenClaw gateway running
- Node.js 18+
- GitHub account with a Personal Access Token (PAT)

## Setup

### 1. Generate a GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: `openclaw-github-skill`
4. Scopes (permissions):
   - `repo` — Full control of private repositories
   - `public_repo` — Limited access to public repositories only
   - `read:user` — Read user profile data (optional)
5. Copy the token

### 2. Configure Credentials

**Option A: Environment Variables (Recommended for local use)**

Set before starting OpenClaw:

```bash
export GITHUB_TOKEN="ghp_your_token_here"
export GITHUB_USERNAME="your_github_username"
```

**Option B: OpenClaw Config**

Add to `~/.openclaw/openclaw.json`:

```json
{
  "github": {
    "token": "ghp_your_token_here",
    "username": "your_username"
  }
}
```

### 3. Restart OpenClaw

```bash
openclaw gateway restart
```

## Usage

```
You: List my Python repositories
Bot: [lists your Python repositories]

You: Check CI status on my-project
Bot: [shows CI/CD status]

You: Create an issue in my-project about the login bug
Bot: [creates the issue and returns the link]

You: What's the recent activity on my-project?
Bot: [shows recent commits]

You: Search my repos for "trading"
Bot: [shows matching repositories]
```

## Directory Structure

```
openclaw-github-skill/
├── SKILL.md       # Skill documentation for OpenClaw
├── README.md      # This file
├── index.js       # Skill implementation
└── package.json   # NPM package metadata
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `list_repos` | List repositories (filter by type, language, sort) |
| `get_repo` | Get detailed repo info (stars, forks, etc.) |
| `check_ci_status` | CI/CD status |
| `create_issue` | Create a new issue |
| `create_repo` | Create a new repository |
| `search_repos` | Search your repositories |
| `get_recent_activity` | View recent commits |

## Security

⚠️ **IMPORTANT: Protect Your GitHub Token!**

**Do:**
- ✅ Use environment variables or OpenClaw config
- ✅ Use minimal required scopes (`repo` or `public_repo`)
- ✅ Rotate tokens if compromised

**Don't:**
- ❌ Commit tokens to git
- ❌ Share tokens in code or public repos
- ❌ Store tokens in unprotected files

**Best Practices:**
- For local development: Environment variables are acceptable
- For shared machines: Use OpenClaw config or a secrets manager
- For production: Use your platform's credential store

## Rate Limits

- **Unauthenticated requests:** 60/hour
- **Authenticated requests:** 5,000/hour

The skill automatically uses your credentials for authentication.

## Requirements

- OpenClaw 2024+
- Node.js 18+
- GitHub Personal Access Token with appropriate scopes

## Contributing

Contributions welcome! To contribute:

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Acknowledgments

Built for the OpenClaw ecosystem.
