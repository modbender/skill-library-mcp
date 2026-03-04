# Security Notes

## What This Repo Contains

This repo contains **templates and setup scripts** — generic, placeholder-based, safe to share publicly.

No real credentials, IDs, or personal data should ever be committed here.

---

## What Should NOT Be Public

After you install and personalize this system, the following should live in a **private repo** (or local-only):

### Your Operational Config
- `openclaw.json` — contains model keys, agent configs, gateway settings
- `cron/jobs.json` — reveals your automation schedule and cron prompts
- `agents/observer/AGENT_PROMPT.md` + `daily-prompt.md` — your security detection playbook. An attacker who reads this knows exactly what you're watching for — and what you're not.

### Your Memory + Research
- `memory/` — personal context, decisions, people, commitments
- `research/` — your notes, bookmarks, analysis
- `memory/audits/` — security audit findings = a map of every weakness found

### Your Identity Files (After Personalization)
- `SOUL.md` — your agent's actual behavioral rules (post-personalization)
- `AGENTS.md` — your operational protocol (post-personalization, with real IDs/channels)
- `USER.md` — personal information about you

### Your Integration Scripts
- Any script with hardcoded paths, API keys, or account identifiers

---

## The Rule

**Templates = public. Your instance = private.**

The templates in this repo are starting points. Once you fill them in with real data, they belong in a private repo or local git only.

---

## Recommended Setup

1. Use this public repo to install the skill
2. Create a **private GitHub** (separate account recommended for OPSEC) for your personalized instance
3. Push your workspace to the private repo: `git remote add private https://github.com/YOUR_PRIVATE_ACCOUNT/YOUR_REPO.git`
4. Never push `openclaw.json`, credentials, or memory to the public repo

The `setup/lock-identity.sh` script handles file-system permissions. A private git remote handles version control for your personalized instance.
