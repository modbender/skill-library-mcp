# Distil — OpenClaw Native Skill

This directory contains the **Distil native skill for [OpenClaw](https://openclaw.ai)** — gives AI agents running inside OpenClaw direct, zero-configuration access to the Distil web proxy.

## What's in this folder

| File | Description |
|------|-------------|
| `SKILL.md` | OpenClaw skill manifest — describes the skill to OpenClaw and documents commands for the agent |

## How it works

When OpenClaw discovers this skill, it:

1. Reads `SKILL.md` to learn the skill name, description, and what commands are available
2. Uses direct `curl` calls to the Distil proxy API
3. The agent can fetch/search/render/screenshot without installing a Node wrapper

## Installation

```bash
export DISTIL_API_KEY=dk_yourkey
```

Optional:

```bash
export DISTIL_PROXY_URL=https://proxy.distil.net
```

### Verify the install

```bash
curl -s "${DISTIL_PROXY_URL:-https://proxy.distil.net}/https://example.com" \
  -H "X-Distil-Key: $DISTIL_API_KEY"
```

## Usage

```bash
# Fetch any URL as clean Markdown
curl -s "${DISTIL_PROXY_URL:-https://proxy.distil.net}/https://example.com" \
  -H "X-Distil-Key: $DISTIL_API_KEY"

# Search the web and get results as Markdown
curl -s "${DISTIL_PROXY_URL:-https://proxy.distil.net}/search?q=best+practices+for+Go+error+handling" \
  -H "X-Distil-Key: $DISTIL_API_KEY" \
  -H "Accept: text/markdown"

# Screenshot a page
curl -s "${DISTIL_PROXY_URL:-https://proxy.distil.net}/screenshot/https://example.com" \
  -H "X-Distil-Key: $DISTIL_API_KEY" > screenshot.png

# Render a javascript SPA before extracting markdown
curl -s "${DISTIL_PROXY_URL:-https://proxy.distil.net}/render/https://example.com" \
  -H "X-Distil-Key: $DISTIL_API_KEY"

# Get raw content without markdown conversion
curl -s "${DISTIL_PROXY_URL:-https://proxy.distil.net}/raw/https://example.com" \
  -H "X-Distil-Key: $DISTIL_API_KEY"

# Bypass cache
curl -s "${DISTIL_PROXY_URL:-https://proxy.distil.net}/nocache/https://news.ycombinator.com" \
  -H "X-Distil-Key: $DISTIL_API_KEY"
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DISTIL_API_KEY` | (required) | Your Distil API key |
| `DISTIL_PROXY_URL` | `https://proxy.distil.net` | Proxy base URL — override for self-hosted instances |

## Output

- Distil responses are printed to stdout
- HTTP errors return a non-2xx status with JSON error details

## Getting an API key

Sign up at [distil.net](https://distil.net) — free tier included.

Your key looks like `dk_yourkey`. Set it as an environment variable:

```bash
export DISTIL_API_KEY=dk_yourkey
```

## Troubleshooting

**"DISTIL_API_KEY environment variable is required"** — set `DISTIL_API_KEY=dk_yourkey` in your shell or MCP config

**"fetch failed"** — verify your key is valid at [distil.net/usage](https://distil.net/usage); check connectivity with `curl -s https://proxy.distil.net/healthz`

**Empty output** — the page may require JavaScript rendering; try the `/render/` endpoint
