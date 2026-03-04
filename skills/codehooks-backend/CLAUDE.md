# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

This is an OpenClaw skill package (`codehooks-openclaw-skill`) — not a runnable application. It provides `SKILL.md` (the skill definition for OpenClaw agents) and `examples/` (ready-to-use code templates). There is no build system, test suite, or package.json — the repo is documentation and example code that teaches OpenClaw agents how to use the Codehooks serverless platform.

## Repository Structure

- `SKILL.md` — The OpenClaw skill definition file. This is the core artifact. It follows the OpenClaw skill format with YAML frontmatter (`name`, `description`, `metadata`) and markdown body containing instructions, CLI commands, and code examples.
- `README.md` — User-facing documentation for the skill package.
- `examples/` — JavaScript code templates using `codehooks-js`:
  - `webhook-handler.js` — Stripe webhook with signature verification via `webhook-verify`
  - `daily-job.js` — Cron-scheduled job (`app.job()`)
  - `queue-worker.js` — Async queue processing (`app.worker()` + `conn.enqueue()`)
  - `workflow-automation.js` — Multi-step autonomous workflow (`app.createWorkflow()`)

## Key Concepts

**Codehooks-js patterns** — All examples follow the same structure:
1. Import `app` (and `Datastore`) from `codehooks-js`
2. Register handlers (routes, jobs, workers, workflows)
3. Export `app.init()` as default

**Auth bypass for webhooks** — External webhook endpoints need `app.auth('/path', (req, res, next) => next())` to skip JWT authentication.

**SKILL.md frontmatter** — The `metadata` field uses nested JSON: `{ "openclaw": { "emoji": "...", "requires": { "bins": [...], "env": [...] } } }`. The `requires.bins` lists CLI tools (`coho`) and `requires.env` lists required environment variables (`CODEHOOKS_ADMIN_TOKEN`).

## Editing Guidelines

When modifying `SKILL.md`, keep code examples self-contained and deployable — agents copy-paste them directly. The `coho prompt` command provides the full codehooks-js API reference, so `SKILL.md` only needs common patterns, not exhaustive API docs.

When adding examples, follow the existing pattern: single-file, ES module imports, export `app.init()`, and include comments explaining the "why" (e.g., auth bypass).
