# DeShell — OpenClaw Native Skill

This directory contains the **DeShell native skill for [OpenClaw](https://openclaw.ai)** — a minimal bash-based command that gives AI agents running inside OpenClaw direct, zero-configuration access to the DeShell web proxy.

## What's in this folder

| File | Description |
|------|-------------|
| `SKILL.md` | OpenClaw skill manifest — describes the skill to OpenClaw and documents commands for the agent |

## How it works

When OpenClaw discovers this skill, it:

1. Reads `SKILL.md` to learn the skill name, description, and what commands are available
2. **Currently, you must manually install the `@deshell/mcp` npm package** (see Installation section below). Future versions of OpenClaw may auto-install based on the skill metadata.
3. The agent can then call `deshell fetch <URL>` or `deshell search <query>` directly from shell commands

The `deshell` script resolves your API key from the `DESHELL_API_KEY` env var, constructs the correct proxy URL, and fires a `curl` request — returning clean Markdown to stdout.

## Installation

### Via NPM

```bash
npm install -g @deshell/mcp
```

**Security Note:** Before installing, verify the package provenance:
- Check the package details: `npm view @deshell/mcp`
- Visit the package page: https://www.npmjs.com/package/@deshell/mcp
- Ensure you're installing from the official source

Set the `DESHELL_API_KEY` environment variable

### Verify the install

```bash
deshell fetch https://example.com
```

You should get clean Markdown back. If you see an error about a missing API key, check your Keychain entry.

## Usage

```bash
# Fetch any URL as clean Markdown
deshell fetch https://example.com

# Search the web and get results as Markdown
deshell search "best practices for Go error handling"

# Multi-word queries work naturally — no quoting needed
deshell search top 10 AI companies 2025

# Force a fresh fetch (bypass cache)
DESHELL_EXTRA_HEADERS="-H X-DeShell-No-Cache:true" deshell fetch https://news.ycombinator.com

# Limit response size (saves tokens on very long pages)
DESHELL_EXTRA_HEADERS="-H X-DeShell-Max-Tokens:2000" deshell fetch https://long-article.example.com
```

## Configuration

All configuration is via environment variables. Defaults work for most users.

| Variable | Default | Description |
|----------|---------|-------------|
| `DESHELL_API_KEY` | (none) | Your DeShell API key |
| `DESHELL_PROXY_URL` | `https://proxy.deshell.ai/` | Proxy base URL — override for self-hosted instances |
| `DESHELL_EXTRA_HEADERS` | (none) | Extra `curl -H` flags passed to every request |

## Output

- **`deshell fetch`** — page content as clean Markdown on stdout, HTTP errors on stderr
- **`deshell search`** — search results (titles, URLs, descriptions) as Markdown on stdout
- **Exit codes** — `0` on success, `1` on any error (missing key, HTTP failure, bad usage)

## Getting an API key

Sign up at [deshell.ai](https://deshell.ai) — free tier includes 500 requests/month.

Your key looks like `dk_yourkey`. Store it in an environment variable.

```bash
export DESHELL_API_KEY=dk_yourkey
```

## Troubleshooting

**"No API key found"** — set your environment variable `DESHELL_API_KEY=dk_yourkey`

**"fetch failed"** — check `curl -v https://proxy.deshell.ai/` to confirm connectivity; verify your key is valid at [deshell.ai/usage](https://deshell.ai/usage)

**Empty output** — the page may require JavaScript rendering.
