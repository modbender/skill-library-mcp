# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

This is an **OpenClaw skill** — a prompt-based package that teaches AI agents (like Claude in OpenClaw/ShellBot) how to use the Freepik API. There is no application code, build system, or tests. The entire skill is defined in three files:

- **`SKILL.md`** — The main skill definition. Contains the frontmatter metadata (name, version, allowed-tools, env requirements) and all API usage instructions, curl examples, and model selection guidance. This is what the AI agent reads at runtime.
- **`_meta.json`** — ClawHub registry metadata (slug, version, publishedAt, icon URL).
- **`models-reference.md`** — Complete catalog of all Freepik API models and endpoints with parameters. Supplementary reference linked from SKILL.md.

## Architecture

The skill works by injecting `SKILL.md` into an OpenClaw agent's context when the user invokes `/freepik` or asks about image/video generation. The agent then uses `curl` to call the Freepik REST API directly — there is no SDK or wrapper code.

**Key pattern:** Most Freepik AI endpoints are async (queue-based):
1. `POST` submits a task → returns `task_id`
2. `GET` polls every 3s until `status: "COMPLETED"`
3. Result contains a temporary CDN URL

Exceptions: Remove Background and AI Image Classifier are synchronous.

**Security constraints** (defined in `SKILL.md` frontmatter `allowed-tools`):
- Only `curl *api.freepik.com*` is permitted — no downloads from arbitrary domains
- Only `jq` for JSON parsing and `mkdir -p ~/.freepik/*` for session directories
- No `base64` encoding, no `curl` to non-Freepik domains

## How to Make Changes

- **Adding/updating a model:** Edit `SKILL.md` to add the endpoint, parameters, and examples. Update the model table in `models-reference.md` as well.
- **Changing skill metadata:** Edit the frontmatter block at the top of `SKILL.md` (between `---` markers). The `allowed-tools` field controls which Bash commands the agent can execute.
- **Bumping version:** Update `version` in both `SKILL.md` frontmatter and `_meta.json`. Tag the release (`git tag v1.0.x`).
- **Publishing:** `clawhub publish` from the repo root (requires ClawHub credentials).

## Environment

Requires `FREEPIK_API_KEY` environment variable. Get one from https://www.freepik.com/developers/dashboard/api-key

## Conventions

- Model endpoint tables use `$1` as the model selector argument (maps to the skill's argument system: `$0` = command, `$1` = model/operation, `$ARGUMENTS` = all args).
- curl examples must always target `api.freepik.com` — this is enforced by the `allowed-tools` whitelist and is a security requirement.
- Result URLs should be presented to users directly, not downloaded via curl (they are temporary signed CDN links).
