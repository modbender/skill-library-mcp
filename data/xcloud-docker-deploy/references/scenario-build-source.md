# Scenario: Build-from-Source Apps

## Detection

This scenario applies when `docker-compose.yml` contains a `build:` directive:

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    image: my-app:latest   # local tag — not a public registry
```

## Solution Overview

1. Set up GitHub Actions to build the image and push to GHCR on every push to `main`
2. Replace `build:` with `image: ghcr.io/OWNER/REPO:latest` in the compose
3. xCloud pulls the pre-built image automatically on each deploy

## Step 1 — Modify docker-compose.yml

Remove the `build:` block, replace `image:` with the GHCR reference:

```yaml
# BEFORE
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    image: my-app:latest

# AFTER
services:
  app:
    image: ghcr.io/OWNER/REPO:latest
    # build: removed
```

Replace `OWNER` with the GitHub username/org, `REPO` with the repository name.

## Step 2 — Generate GitHub Actions Workflow

Use the template at `assets/github-actions-build.yml`. Replace placeholders:
- `IMAGE_NAME` — repository name (lowercase, e.g., `vidify-app`)
- `REGISTRY` — `ghcr.io`

The workflow:
- Triggers on push to `main`
- Builds the Docker image from `Dockerfile`
- Tags as `ghcr.io/OWNER/REPO:latest` and `ghcr.io/OWNER/REPO:sha-XXXXXX`
- Pushes to GHCR using `GITHUB_TOKEN` (no extra secrets needed for public repos)

Save to `.github/workflows/docker-build.yml`.

## Step 3 — Make GHCR Image Public

After first push:
1. Go to `github.com/OWNER/REPO` → Packages
2. Find the package → Settings → Change visibility to **Public**

Or configure in `docker-build.yml` using `packages: write` permission (already in template).

## Step 4 — xCloud Webhook for Auto-Deploy

After GHCR push, trigger xCloud to redeploy. Add this step to the GitHub Actions workflow:

```yaml
- name: Trigger xCloud deploy
  run: |
    curl -X POST "${{ secrets.XCLOUD_DEPLOY_WEBHOOK }}" \
      -H "Content-Type: application/json"
```

Get the webhook URL from xCloud site settings → Git Deploy → Webhook URL.
Add it as a GitHub secret `XCLOUD_DEPLOY_WEBHOOK`.

## Step 5 — .env.example

Extract all `${VAR_NAME}` references from the compose and generate a `.env.example`:

```bash
# Auto-extract env vars from docker-compose.yml
grep -oP '\$\{\K[^}]+' docker-compose.yml | sort -u | sed 's/^/# /; s/$/=/' > .env.example
```

## Multiple Services with build:

If multiple services have `build:` directives, each needs its own image and GitHub Actions job:

```yaml
jobs:
  build-app:
    # builds ghcr.io/owner/repo-app:latest
  build-worker:
    # builds ghcr.io/owner/repo-worker:latest
```

Or use a matrix strategy (see template).
