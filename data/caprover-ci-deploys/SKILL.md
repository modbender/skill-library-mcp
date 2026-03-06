---
name: caprover-deploy
description: Deploy apps to CapRover and set up GitHub Actions CI/CD workflows for new or existing projects. Use when the user says things like "deploy X", "trigger a deploy of X", "deploy branch Y to Z", "set up CI/CD for this project", "configure CapRover deploy workflow", "add deploy workflow to my repo", or asks about deployment status. Supports GitHub workflow triggers, CapRover webhook triggers, and direct CLI deploys. Also helps scaffold .github/workflows/deploy.yml, captain-definition, and GitHub secrets for any new project.
---

# CapRover Deploy

## Overview

This skill enables deploying apps to CapRover just by asking. It supports two primary strategies:
1. **GitHub workflow_dispatch** — triggers an existing CI/CD workflow (build + deploy)
2. **CapRover App Token / Webhook** — directly triggers a CapRover build/deploy

## Configuration

All credentials live in a `config.json` file in the skill directory (gitignored).

### config.json Format

```json
{
  "caprover": {
    "url": "https://captain.example.com",
    "password": "YOUR_MASTER_PASSWORD"
  },
  "github": {
    "token": "ghp_YOUR_GITHUB_PAT",
    "owner": "your-github-username"
  },
  "apps": {
    "myapp": {
      "caprover_app_name": "myapp",
      "github_repo": "your-username/myapp",
      "github_workflow": "deploy.yml",
      "default_branch": "main",
      "caprover_app_token": "OPTIONAL_PER_APP_TOKEN",
      "caprover_webhook_url": "OPTIONAL_WEBHOOK_URL_FROM_CAPROVER_DASHBOARD"
    }
  }
}
```

### What each credential does

| Credential | Where to get it | Purpose |
|---|---|---|
| `caprover.url` | Your CapRover server | Base URL for API calls |
| `caprover.password` | CapRover dashboard | Master password for API auth |
| `github.token` | GitHub → Settings → Developer Settings → PAT | For triggering workflow_dispatch |
| `apps.*.caprover_app_token` | App → Deployment tab → Enable App Token | Per-app deploy without master password |
| `apps.*.caprover_webhook_url` | App → Deployment tab → Webhook URL | Trigger rebuild from configured git repo |
| `apps.*.github_workflow` | `.github/workflows/` filename | Which workflow to trigger |

## Deploy Decision Flow

When user says "deploy X" (optionally "to branch Y"):

```
1. Read config.json
2. Look up app by name (fuzzy match)
3. Choose strategy:
   a. If github.token + github_repo + github_workflow → use GitHub workflow_dispatch
   b. Else if caprover_webhook_url → POST to webhook URL
   c. Else if caprover_app_token → use caprover CLI
   d. Ask user for missing config
4. Execute and report result
```

## Strategy 1: GitHub Workflow Dispatch (Recommended)

```bash
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/OWNER/REPO/actions/workflows/deploy.yml/dispatches \
  -d '{"ref":"main"}'
```

Check run status:
```bash
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/OWNER/REPO/actions/runs?per_page=1
```

## Strategy 2: CapRover Webhook Trigger

```bash
curl -X POST "WEBHOOK_URL_FROM_CONFIG"
```

The webhook URL is found in: CapRover Dashboard → Apps → [App Name] → Deployment Tab → Webhook URL

## Strategy 3: CapRover App Token (CLI Deploy)

```bash
caprover deploy \
  --caproverUrl https://captain.example.com \
  --appToken "APP_TOKEN" \
  --appName "myapp" \
  --imageName "ghcr.io/owner/myapp:latest"
```

## Conversational Triggers

| User says | Action |
|---|---|
| "deploy myapp" | Deploy default branch via best available strategy |
| "deploy myapp to main" | Deploy main branch |
| "deploy branch feat/ui to myapp" | GitHub dispatch with ref=feat/ui |
| "trigger a deploy of myapp" | Same as deploy |
| "check deploy status of myapp" | Fetch latest GitHub Actions run status |
| "what apps can I deploy?" | List apps from config.json |

## Setting Up a New Project for CapRover Deploy

### Step 1: Choose the right workflow template

| Scenario | Template |
|---|---|
| Has Dockerfile, push image to ghcr.io | `assets/templates/deploy-image.yml` |
| Node build step + tar deploy | `assets/templates/deploy-tar.yml` |
| Staging + production environments | `assets/templates/deploy-multi-env.yml` |

### Step 2: Create workflow file in the project

```bash
mkdir -p PROJECT/.github/workflows
cp assets/templates/deploy-image.yml PROJECT/.github/workflows/deploy.yml
# Replace __APP_NAME__ with actual CapRover app name
sed -i 's/__APP_NAME__/myapp/g' PROJECT/.github/workflows/deploy.yml
```

### Step 3: Add captain-definition (if needed for tar-based deploy)

```bash
cp assets/templates/captain-definition.json PROJECT/captain-definition
```

### Step 4: Configure GitHub Secrets

Add these in GitHub → Repo → Settings → Secrets and variables → Actions:

| Secret name | Value |
|---|---|
| `CAPROVER_HOST` | CapRover URL, e.g. `https://captain.example.com` |
| `CAPROVER_APP_TOKEN` | From CapRover App → Deployment → Enable App Token |

For multi-env:
- `CAPROVER_APP_PROD`, `CAPROVER_APP_TOKEN_PROD`
- `CAPROVER_APP_STAGING`, `CAPROVER_APP_TOKEN_STAGING`

### Step 5: Commit and push

```bash
cd PROJECT
git add .github/workflows/deploy.yml captain-definition
git commit -m "ci: add CapRover deploy workflow"
git push
```

## Notes

- The `caprover` CLI may not be installed: `npm install -g caprover`
- For private repos, the GitHub token needs `repo` + `workflow` scopes
- Always confirm the deploy was triggered (check API response or GitHub Actions UI)
- See `assets/templates/` for workflow templates
