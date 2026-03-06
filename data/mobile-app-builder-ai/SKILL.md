---
name: launchpulse
version: 1.1.1
description: Build full-stack web and mobile apps from a text description. Creates projects, plans features, and starts Quick Start builds for background execution.
homepage: https://launchpulse.ai
license: MIT
user-invocable: true
metadata: {"openclaw":{"homepage":"https://launchpulse.ai","requires":{"bins":["node"]},"author":"LaunchPulse","categories":["development","deployment"]}}
---

# LaunchPulse (Web + Mobile App Generator)

Build production-ready web apps and Expo mobile apps from a text description. LaunchPulse plans features, starts Quick Start in the background, and returns project/session context immediately.

**What it does:**
1. Creates a new project (web or Expo mobile)
2. Plans MVP features using AI and auto-approves them
3. Starts Quick Start (single-pass background build)
4. Returns immediately with project id/session id so progress can be monitored
5. Iterates on existing projects with change requests
6. Supports production ops: deployments, app store publish, domains, database, storage, env/payment setup

If feature planning is temporarily unavailable, the skill falls back to a single MVP feature so Quick Start never stalls.

## Authentication

The first time you run the skill, it automatically starts a device-login flow:
1. OpenClaw prints a sign-in link
2. You open it, sign in with Google on launchpulse.ai, and confirm
3. OpenClaw receives a personal access token (PAT) and stores it locally

Token storage path: `${OPENCLAW_STATE_DIR:-~/.openclaw}/launchpulse/auth.json`

Advanced alternatives:
- `LAUNCHPULSE_PAT` / `--pat <token>`: provide a PAT directly
- `LAUNCHPULSE_API_KEY` / `--api-key <token>`: alias for PAT-style API key auth
- `LAUNCHPULSE_ACCESS_TOKEN` / `--access-token <jwt>`: provide a Supabase JWT (advanced)

## Billing

LaunchPulse uses a token-based billing system. Every AI operation (feature planning, building, iterating) consumes tokens.

**Plans:**
| Plan | Price | Tokens/month | Best for |
|------|-------|-------------|----------|
| Free | $0 | 10,000 (~2-5 features) | Trying it out |
| Starter | $19/mo | 200,000 (~50-100 features) | Individual builders |
| Builder | $49/mo | 500,000 (~125-250 features) | Serious app builders |

**Token addon packs** (one-time, never expire):
- 50K tokens: $5
- 100K tokens: $9
- 500K tokens: $39 (22% off)
- 1M tokens: $69 (31% off)

**What happens when you run out:**
- Before Quick Start/iterate starts, the skill checks your balance and blocks with a clear message if exhausted
- If tokens run out during a build, the backend will stop progress and report billing context in status APIs
- Run `/launchpulse status` to check your balance anytime
- Run `/launchpulse upgrade` to purchase more tokens or upgrade your plan

## How to use

**Login** (optional, happens automatically on first use):
- `/launchpulse login`

**Logout** (clears stored token):
- `/launchpulse logout`

**Check balance:**
- `/launchpulse status`

**Upgrade plan or buy tokens:**
- `/launchpulse upgrade` (shows all options)
- `/launchpulse upgrade --tier STARTER` (subscribe to Starter)
- `/launchpulse upgrade --tier BUILDER --billing-period annual` (annual Builder)
- `/launchpulse upgrade --tokens 0` (buy 50K token pack)

**Quick Start a web app:**
- `/launchpulse web "Create a landing page for a dog walking business"`

**Quick Start a mobile app (Expo):**
- `/launchpulse mobile "Create an Expo app for habit tracking"`

**Iterate on an existing project:**
- `/launchpulse iterate <projectId> "Add a contact form to the homepage"`

**Production operations:**
- `/launchpulse projects`
- `/launchpulse project-status <projectId>`
- `/launchpulse deploy <projectId> --target cloud-run --wait`
- `/launchpulse deploy-status <projectId> <deploymentId>`
- `/launchpulse store-publish <projectId> --payload-file ./store-publish.json --wait`
- `/launchpulse store-status <projectId> [--publish-id <id>]`
- `/launchpulse store-2fa <projectId> <publishId> <code>`
- `/launchpulse domains search "mybrand"`
- `/launchpulse domains check mybrand.com`
- `/launchpulse domains add <projectId> mybrand.com`
- `/launchpulse domains provision <projectId> mybrand.com my-fly-app`
- `/launchpulse db info <projectId>`
- `/launchpulse db table <projectId> users`
- `/launchpulse db query <projectId> "select * from users limit 10"`
- `/launchpulse storage init`
- `/launchpulse storage upload <projectId> --payload-file ./upload.json`
- `/launchpulse env-files list <projectId>`
- `/launchpulse env-files save <projectId> --file-path vitereact/.env --vars-file ./vars.json`
- `/launchpulse payments inject-env <projectId> --project-type vitereact`
- `/launchpulse payments setup <projectId> --project-type expo --stripe-publishable-key pk_test_... --revenuecat-ios-key appl_... --revenuecat-secret-key sk_...`

If the user says "iterate it" without an id, use the most recent `projectId` from the current chat/session.

### What the assistant should do internally

Run the script from the OpenClaw workspace root:

- `cd ~/.openclaw/workspace`
- `node skills/launchpulse/scripts/launchpulse.cjs login`
- `node skills/launchpulse/scripts/launchpulse.cjs status`
- `node skills/launchpulse/scripts/launchpulse.cjs upgrade --tier STARTER`
- `node skills/launchpulse/scripts/launchpulse.cjs web "<description>"`
- `node skills/launchpulse/scripts/launchpulse.cjs mobile "<description>"`
- `node skills/launchpulse/scripts/launchpulse.cjs iterate <projectId> "<change request>"`
- `node skills/launchpulse/scripts/launchpulse.cjs projects`
- `node skills/launchpulse/scripts/launchpulse.cjs project-status <projectId>`
- `node skills/launchpulse/scripts/launchpulse.cjs deploy <projectId> --target cloud-run --wait`
- `node skills/launchpulse/scripts/launchpulse.cjs store-publish <projectId> --payload-file ./store-publish.json --wait`
- `node skills/launchpulse/scripts/launchpulse.cjs domains search "<query>"`
- `node skills/launchpulse/scripts/launchpulse.cjs db info <projectId>`
- `node skills/launchpulse/scripts/launchpulse.cjs payments setup <projectId> --project-type vitereact --vars-file ./vars.json`

Useful options:
- `--api-base <url>`: override API base (for local/dev backend)
- `--name <slug>`: preferred project id
- `--pat <token>` / `--access-token <jwt>`: advanced auth overrides
- `--no-plan`: skip AI planner and use MVP fallback feature directly
- `--timeout-min <n>`: timeout in minutes for long-running commands (iterate/deploy/store wait)
- `--chat-id <id>`: (iterate) use a specific project chat
- `--provider <id>` / `--model <id>`: (iterate) override AI provider/model
- `--target <cloud-run|fly>`: (deploy) deployment target
- `--wait`: poll until terminal status (deploy/store publish)
- `--payload-file <path>`: JSON payload for complex commands
- `--project-type <vitereact|expo>`: payment/env injection mode
- `--vars-file <path>` / `--file-path <path>`: env-files save/payment setup

### User updates (required)

When running this skill for users in Telegram/OpenClaw, keep updates short and frequent:
- Send a milestone update after each major step: auth, project creation, planning/fallback, quick-start kickoff.
- When script returns `status: "quick_start_started"`, always send an explicit completion update immediately with `projectId`, `sessionId`, and guidance to monitor via `project-status`.
- If stuck or degraded (planner failure, quick-start start failure), say exactly what happened and what is still usable.
- If `status: "token_limit_exceeded"`, tell the user their tokens are used up and share the upgrade URL from the output.

## Output

The script prints a final JSON object to stdout including:
- `ok`: boolean success flag
- `status`: operation-specific status (`quick_start_started`, `success`, `failed`, `token_limit_exceeded`, deploy/store/domain/db/payment states)
- `projectId`, `mode`, `sessionId`
- `preview`: URLs (frontendUrl, backendUrl, expoGoUrl)
- `features`: counts snapshot (total, selected, completed)
- `billing`: (when applicable) tier, upgradeUrl, buyTokensUrl

**Exit codes:** 0=success, 1=error, 2=paused, 3=timeout, 4=failed, 5=billing/token limit

## Backend selection

Default API: `https://api.launchpulse.ai/api`

Override for local dev:
- `LAUNCHPULSE_API_BASE_URL=http://localhost:667/api`
- or `--api-base http://localhost:667/api`

## Changelog

### 1.1.1
- Switched `web` and `mobile` flow to Quick Start only
- Removed auto-mode loop polling/continue behavior from create flow
- `web`/`mobile` now return immediately with `status: "quick_start_started"`

### 1.1.0
- Added production commands: projects, project-status, deploy/deploy-status
- Added store publish support (start/status/2FA/wait)
- Added domains command suite (search/check/map/provision/status/dns/checkout/register/verification)
- Added database command suite (info/table/query)
- Added storage command suite (init/upload/save-assets)
- Added env-files and payment setup commands (inject env + Stripe/RevenueCat env save)
- Hardened upgrade failure exit behavior (non-zero on checkout fallback failure)

### 1.0.0
- Initial ClawHub release
- Device auth flow (Google sign-in)
- Web and mobile (Expo) project creation
- AI-powered feature planning with fallback
- Auto-build with live polling
- Project iteration support
- Token balance checking and billing integration
- `status` command to check plan and usage
- `upgrade` command with direct Stripe checkout links
