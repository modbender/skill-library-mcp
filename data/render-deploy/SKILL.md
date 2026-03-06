---
name: Render Deploy
slug: render-deploy
version: 1.0.0
homepage: https://clawic.com/skills/render-deploy
description: Deploy applications on Render with codebase analysis, render.yaml Blueprint generation, MCP direct provisioning, and post-deploy verification.
changelog: Added end-to-end Render deployment guidance with method selection, runtime checks, and practical troubleshooting flows.
metadata: {"clawdbot":{"emoji":"🚀","requires":{"bins":["git","render"],"env":["RENDER_API_KEY"],"config":["~/render-deploy/"]},"primaryEnv":"RENDER_API_KEY","install":[{"id":"brew","kind":"brew","formula":"render","bins":["render"],"label":"Install Render CLI (Homebrew)"}],"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines.
If local memory is needed, ask for consent before creating `~/render-deploy/`.

## When to Use

Use this skill when the user wants to deploy, publish, or host an application on Render and needs reliable deployment execution instead of generic advice. Activate for render.yaml Blueprint generation, MCP direct service creation, runtime configuration checks, and post-deploy triage.

## Architecture

Memory lives in `~/render-deploy/`. See `memory-template.md` for setup.

```text
~/render-deploy/
|- memory.md                  # Stable preferences and integration choices
|- deployment-notes.md        # Project-level deployment decisions
|- env-inventory.md           # Required env vars and source of truth
`- incident-log.md            # Deploy failures and resolved fixes
```

## Quick Reference

Load only the minimum file needed for the current request.

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Codebase detection and commands | `codebase-analysis.md` |
| Blueprint workflow and render.yaml rules | `blueprint-workflow.md` |
| Authentication and MCP execution mapping | `direct-creation.md` |
| Startup and healthcheck troubleshooting | `troubleshooting.md` |

## Authentication Model

Before any provisioning command, confirm one of these is active:
- `RENDER_API_KEY` is exported in the shell, or
- Render CLI is authenticated (`render whoami -o json`)

For git-backed flows, require `git` and a valid remote URL. Do not attempt opaque credential discovery or unrelated environment inspection.

## Core Rules

### 1. Classify the Deployment Path First
Before proposing commands, decide which path applies:
- Git-backed deploy (Blueprint or Direct Creation)
- Prebuilt Docker image deploy via Dashboard/API

If the repository has no remote, stop and ask the user to push a remote or switch to dashboard image deploy.

### 2. Choose Method by Complexity, Not Preference
Default decision:
- Direct Creation when it is one simple service and no extra infra
- Blueprint when there are multiple services, datastores, cron, workers, or reproducibility requirements

If uncertainty remains, ask one clarifying question and continue.

### 3. Verify Prerequisites Before Any Deploy Action
Run checks in this order:
- `git remote -v` for source availability
- MCP availability (`list_services()`)
- CLI fallback readiness (`render --version`, `render whoami -o json`)
- Active workspace context (MCP or CLI)
- Authentication presence (`RENDER_API_KEY` or authenticated CLI session)

Do not proceed to deployment steps when prerequisites are missing.

### 4. Treat `render.yaml` as Executable Infrastructure
When using Blueprint:
- Declare all required env vars
- Mark user-provided secrets with `sync: false`
- Prefer `plan: free` unless user requests another plan
- Match service type and runtime to the actual app behavior

After creating the file, validate before push.

### 5. Require Push Before Deeplink Handoff
Before sharing a Render Blueprint deeplink, confirm `render.yaml` is committed and pushed to the remote branch. If not pushed, the Dashboard flow will fail to discover the configuration.

### 6. Verify the Deployment and Close With Evidence
After deployment:
- Confirm latest deploy status is live
- Check health endpoint response
- Review recent error logs
- Validate required env vars and port binding (`0.0.0.0:$PORT`)

If failures exist, run one-fix-at-a-time triage from `troubleshooting.md`.

## Common Traps

- Starting deploy without a git remote -> Blueprint and MCP git-backed flows fail immediately.
- Picking Direct Creation for multi-service systems -> Missing workers/datastores and fragmented setup.
- Forgetting `sync: false` on secrets -> Broken deploys or accidental secret exposure in config.
- Using localhost binding instead of `0.0.0.0:$PORT` -> Health checks fail even when process is running.
- Redeploying repeatedly without root-cause fix -> Noisy failures and delayed resolution.

## External Endpoints

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| https://dashboard.render.com | Repository URL, service config, env key names | Blueprint apply flow and dashboard provisioning |
| https://mcp.render.com | Service creation/config requests and workspace-scoped metadata | MCP direct provisioning |
| https://api.render.com | Deployment metadata, logs, service status (via CLI/API) | Validation and operational checks |

No other endpoints should be used unless the user requests an explicit integration.

## Security & Privacy

**Data that leaves your machine:**
- Repository URL and deployment metadata sent to Render services.
- Environment variable names and provided values when the user explicitly sets them.

**Data that stays local:**
- Preferences and deployment history in `~/render-deploy/` if the user accepts memory.
- Local codebase inspection outputs and interim analysis notes.

**This skill does NOT:**
- Read unrelated credentials outside the deployment context.
- Scrape credentials from shell history, dotfiles, or unrelated config paths.
- Send project files to undeclared third-party endpoints.
- Run destructive infrastructure changes without explicit confirmation.

## Trust

By using this skill, deployment metadata and selected configuration are sent to Render services. Only use it if you trust Render with this operational data.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `deploy` - General deployment planning and release execution.
- `devops` - CI/CD, infrastructure workflows, and ops coordination.
- `docker` - Container packaging and runtime configuration.
- `ci-cd` - Pipeline automation and release validation stages.
- `nodejs` - Runtime-specific app configuration and startup tuning.

## Feedback

- If useful: `clawhub star render-deploy`
- Stay updated: `clawhub sync`
