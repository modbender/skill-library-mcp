# SociClaw

[![CI](https://github.com/sociclaw/sociclaw/actions/workflows/ci.yml/badge.svg)](https://github.com/sociclaw/sociclaw/actions/workflows/ci.yml)

SociClaw is an OpenClaw skill that helps teams produce X/Twitter content automatically:

- discovers trending topics
- plans posts
- generates text + optional images
- syncs to Trello/Notion
- supports local/managed updates for running bots

**Website:** https://sociclaw.com

---

## What this repo contains

- `sociclaw/` — Python skill (core code + CLI)
- `sociclaw/templates/`, `sociclaw/fixtures/`, `sociclaw/tests/` — assets and tests

---

## Install (2 minutes)

```bash
git clone https://github.com/sociclaw/sociclaw.git ~/.openclaw/skills/sociclaw
cd ~/.openclaw/skills/sociclaw
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Then start your OpenClaw runtime and run `/sociclaw`.

For quick local tests:

```bash
python -m pytest -q
```

---

## OpenClaw setup (quick)

### 1) Quick start (text-only, no envs required)

1. Run:

```bash
/sociclaw
/sociclaw setup
```

This stores local config in `.sociclaw/` and gets you planning/generating posts right away.

### 2) Optional: enable images + credits

To generate images (and allow `/sociclaw pay` topups), set:

- `SOCICLAW_IMAGE_API_BASE_URL` (Image API base domain)
- Either:
  - `SOCICLAW_PROVISION_URL` (recommended, auto-provision per user), or
  - `SOCICLAW_IMAGE_API_KEY` (single-account mode)

Example `openclaw.json` env config:

```json
{
  "skills": {
    "entries": {
      "sociclaw": {
        "env": {
          "SOCICLAW_IMAGE_API_BASE_URL": "https://<your-image-api-domain>",
          "SOCICLAW_PROVISION_URL": "https://api.sociclaw.com/api/sociclaw/provision"
        }
      }
    }
  }
```

You will be guided through:
- provider/user id
- niche and posting frequency
- content language
- brand logo (for image generation)
- optional integrations (Trello / Notion)

### 3) Start using commands

```bash
/sociclaw setup
/sociclaw plan
/sociclaw generate
/sociclaw pay
/sociclaw paid <tx-hash>
/sociclaw status
/sociclaw reset
```

---

## Main CLI commands (optional for dev/test)

```bash
# Provision image account (via your secure API gateway)
python -m sociclaw.scripts.cli provision-image-gateway --provider telegram --provider-user-id 123

# Create/update plan
python -m sociclaw.scripts.cli plan --sync-trello --with-image

# Generate due posts and sync
python -m sociclaw.scripts.cli generate --with-image --sync-trello

# Credits topup
python -m sociclaw.scripts.cli topup-start --provider telegram --provider-user-id 123 --amount-usd 5
python -m sociclaw.scripts.cli topup-claim --provider telegram --provider-user-id 123 --tx-hash 0x...
```

---

## Environments and secrets

### Required (by feature)

- Images + credits:
  - `SOCICLAW_IMAGE_API_BASE_URL`
  - `SOCICLAW_IMAGE_MODEL` (optional, default `nano-banana`)
  - `SOCICLAW_IMAGE_URL` / `brand_logo_url` (required for img2img models like `nano-banana`)
- Auto-provisioning (recommended):
  - `SOCICLAW_PROVISION_URL`
  - `SOCICLAW_INTERNAL_TOKEN` (optional; only if your gateway requires it)
- Single-account mode (no provisioning):
  - `SOCICLAW_IMAGE_API_KEY`

### Server-only (gateway, never on user hosts)

- Your gateway will hold privileged secrets server-side (never paste into chat, never set them on user VPS/mac mini).

### Optional (feature-by-feature)

- `XAI_API_KEY` (trend research)
- `TRELLO_API_KEY`, `TRELLO_TOKEN`, `TRELLO_BOARD_ID`
- `NOTION_API_KEY`, `NOTION_DATABASE_ID`
- `SOCICLAW_ALLOW_IMAGE_URL_INPUT` (`true|false`, default false)
- `SOCICLAW_ALLOWED_IMAGE_URL_HOSTS` (comma-separated allowlist for remote logo URL fallback when enabled)
- `SOCICLAW_ALLOWED_IMAGE_INPUT_DIRS` (comma-separated allowed paths for local logo/image files, default `.sociclaw,.tmp`)
- `SOCICLAW_ALLOW_ABSOLUTE_IMAGE_INPUT_DIRS` (`true|false`, default false)

> Never paste secrets in chat. Configure secrets via environment variables on trusted hosts only.

---

## Data and behavior defaults (important)

- Default plan is starter-friendly: **14 days × 1 post/day**.
- If no logo is configured, `nano-banana` generation is skipped automatically.
- Planning starts from the current date and clamps past dates.
- Trello sync keeps board columns focused on the active window (past months are not recreated).
- A local persistent memory DB (`.sociclaw/memory.db`) tracks generated posts and improves topic variety across sessions.

---

## Update and maintenance

```bash
python -m sociclaw.scripts.cli self-update
```

This build prints **manual update steps** (it does not run `git pull` or `pip install` automatically for security).

---

## Troubleshooting (fast)

- **Provision fails with 500/secret error**: check gateway envs and deploy logs.
- **Image says model needs input image**: use `nano-banana` + valid logo URL/path in setup.
- **Plan/user seems stale**: run `/sociclaw reset --yes` and setup again.

---

## Helpful docs

- `SKILL.md` (skill contract)
- `requirements.txt` (dependencies)

