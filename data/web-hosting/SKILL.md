---
name: hosting
description: Meta-skill for zero-friction deployment of local web projects to production URLs by orchestrating github-api, vercel/netlify, domain-dns-ops, and api-gateway. Use when users want to make a local site live with SSL, CI/CD, and optional custom domain wiring.
homepage: https://clawhub.ai
user-invocable: true
disable-model-invocation: false
metadata: {"openclaw":{"emoji":"🚀","requires":{"bins":["git","node","npm","npx"],"env":["MATON_API_KEY"],"config":[]},"note":"Requires local installation of github-api, vercel or netlify, and optionally domain-dns-ops/api-gateway for custom infra or DNS operations."}}
---

# Purpose

Take a local codebase or static site and publish it to a production URL with minimal DevOps friction.

Primary outcomes:
1. repository created and synced,
2. deployment triggered,
3. live URL verified,
4. custom-domain path documented when requested.

This is an orchestration skill. It does not guarantee uptime/SLA by itself.

# Required Installed Skills

Core:
- `github-api` (inspected latest: `1.0.3`)
- One deploy path:
  - `vercel` (inspected latest: `1.0.1`), or
  - `netlify` (inspected latest: `1.0.0`)

Optional:
- `domain-dns-ops` (inspected latest: `1.0.0`, environment-specific)
- `api-gateway` (inspected latest: `1.0.29`)

Install/update:

```bash
npx -y clawhub@latest install github-api
npx -y clawhub@latest install vercel
npx -y clawhub@latest install netlify
npx -y clawhub@latest install domain-dns-ops
npx -y clawhub@latest install api-gateway
npx -y clawhub@latest update --all
```

Verify:

```bash
npx -y clawhub@latest list
```

Important name mapping:
- If user says `/netlifly`, map it to `/netlify`.

# Required Credentials

Mandatory:
- `MATON_API_KEY` (required for `github-api`, and for `api-gateway` routes)

Provider/CLI auth (at least one deploy path):
- Vercel path: logged in `vercel login` or `VERCEL_TOKEN`
- Netlify path: logged in `netlify login` or `NETLIFY_AUTH_TOKEN`

Optional (custom infra through api-gateway):
- active app-specific OAuth connection in Maton control plane (`ctrl.maton.ai`)

Preflight:

```bash
echo "$MATON_API_KEY" | wc -c
echo "$VERCEL_TOKEN$NETLIFY_AUTH_TOKEN" | wc -c
```

Mandatory behavior:
- Never fail silently on missing keys/tokens.
- Always return `MissingAPIKeys` (or missing auth) with blocked stages.
- Continue with non-blocked stages and mark output as `Partial` when needed.

# Inputs the LM Must Collect First

- `project_path`
- `repo_name`
- `repo_visibility` (`private` or `public`)
- `deploy_target` (`vercel` or `netlify`)
- `framework_hint` (optional)
- `custom_domain` (optional)
- `domain_provider` (optional; Cloudflare/Namecheap/etc.)
- `infra_mode` (`frontend-static`, `fullstack-managed`, `vps-server`)

Do not run deployment before deploy target and visibility are explicit.

# Tool Responsibilities

## github-api

Use for repository bootstrap and remote sync setup:
- create repository (user/org),
- configure visibility,
- store remote URL metadata for subsequent push/deploy linkage.

Operational constraints from inspected skill:
- requires `MATON_API_KEY`
- uses Maton-managed OAuth connections
- missing/invalid key leads to auth errors

## vercel

Use for managed frontend/fullstack deploy path:
- link project,
- trigger deploy (`vercel` / `vercel --prod`),
- inspect deployment and domain status,
- manage domain attachments when needed.

## netlify

Use as alternative managed deploy path:
- site create/link/init,
- CI/CD setup from GitHub,
- manual or prod deploy,
- environment variable and domain/dns capabilities.

## domain-dns-ops

Use only when environment matches its assumptions.

Important limitation from inspected skill:
- this skill is documented as environment-specific ("for Peter", source of truth in `~/Projects/manager`).
- if that source context does not exist, do not assume it is portable.

## api-gateway

Use for optional infra/API-managed operations when connected apps exist.

Operational constraints from inspected skill:
- requires `MATON_API_KEY`
- requires active app-specific connection per target service
- `400` indicates missing app connection
- `401` indicates missing/invalid Maton key

Capability disclosure:
- inspected list clearly includes Netlify and many SaaS apps.
- DigitalOcean/AWS are not explicitly listed as native app names in the inspected `api-gateway` skill index.
- treat VPS/server provisioning via gateway as conditional, not guaranteed.

# Canonical Causal Signal Chain

1. `Code Audit`
- scan project root for framework markers:
  - `package.json`, `next.config.*`, `vite.config.*`, `index.html`, `dist/`, `build/`
- classify project type (`Next.js`, `Vite`, static HTML, other)
- determine default build and publish path

2. `Git Inception`
- initialize git if needed,
- create remote repository via `github-api`,
- set origin, commit, and push branch.

3. `Infrastructure Gate`
- present hosting recommendation based on project type:
  - Vercel/Netlify for frontend-managed deploy,
  - custom infra path only if supported connections exist.

Required gate format:
- `InfraGateStatus`: `available` or `blocked`
- `Reason`: missing auth / missing connection / unsupported provider
- `Action`: exact next step

If user asks about provider signup/offers:
- provide neutral official onboarding links only.

4. `Deployment Trigger`
- Vercel path: run `vercel link` (if needed), then deploy (`vercel --prod`).
- Netlify path: create/link/init and deploy (`netlify deploy --prod`).

5. `Status Monitoring`
- poll deploy status/logs until final state:
  - `Ready`/success -> proceed,
  - failure -> return build error summary + remediation actions.

6. `Domain Wiring`
- if custom domain requested:
  - attach domain in provider (Vercel/Netlify),
  - output required DNS records,
  - verify DNS propagation and HTTPS readiness.

7. `Output`
- return live URL,
- return domain instructions,
- return CI/CD update path (future pushes redeploy automatically).

# Output Contract

Always return:

- `ProjectDetection`
  - detected framework
  - build/publish assumptions

- `RepoStatus`
  - repository URL
  - default branch
  - push status

- `InfraGateStatus`
  - provider selected
  - gate status
  - blockers and actions

- `DeploymentStatus`
  - live URL
  - deploy ID/reference
  - final state (`ready` or `failed`)

- `CustomDomainPlan`
  - required DNS records
  - where to set them
  - verification checklist

- `NextActions`
  - exact command/portal steps if anything remains manual

# Quality Gates

Before final output, verify:
- framework detection based on actual files (not guesswork)
- remote repo exists and push path is valid
- deployment URL resolves and status is successful
- custom domain records are explicit and provider-correct
- all missing credentials/connections are disclosed

If any gate fails, return `Needs Revision` with concrete missing dependencies or errors.

# Failure Handling

- Missing `MATON_API_KEY`: return `MissingAPIKeys`, skip github-api/api-gateway stages.
- Missing Vercel/Netlify auth: return missing auth state and provide exact login/token setup steps.
- Git push rejected: keep deployment blocked, return upstream remote/auth error and retry commands.
- Deploy build failed: return build log summary and required fixes.
- Missing domain control: return live platform URL and park custom-domain steps as pending.
- Unsupported VPS provider path in gateway: disclose limitation and provide managed-hosting fallback.

# Guardrails

- Never claim deployment success without a reachable URL.
- Never claim custom domain is active before DNS + HTTPS checks pass.
- Never hide provider limitations or auth blockers.
- Keep recommendations bounded to inspected, available integrations.
